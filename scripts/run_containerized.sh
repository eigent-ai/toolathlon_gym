#!/bin/bash
# Run a single task in an ephemeral container with per-task filesystem isolation.
#
# Isolation strategy (aligned with Toolathlon):
#   - Each task runs inside a fresh Docker container that is destroyed on exit.
#   - The container has its own filesystem and MCP server processes.
#   - Postgres (toolathlon_pg) is shared across tasks; tasks must run sequentially
#     because preprocess resets shared schema state.
#   - A lock file (./dumps/.run.lock) enforces sequential execution.
#
# Prerequisites:
#   1. Build the image:    docker build -t toolathlon-pack:latest .
#   2. Start postgres:     docker compose up -d postgres
#
# Usage:
#   bash scripts/run_containerized.sh <task_name> [max_steps] [image]
#
# Model configuration (environment variables):
#   MODEL_PROVIDER   Provider key used by main.py: aihubmix | openai | anthropic |
#                    gemini | deepseek | openai_compatible  (overrides eval_config.json)
#   MODEL_NAME       Model name, e.g. gpt-4o, claude-3-5-sonnet-20241022
#   MODEL_API_KEY    API key for the selected provider
#   MODEL_API_URL    Base URL (required for openai_compatible / aihubmix)
#
# Examples:
#   # Native OpenAI:
#   MODEL_PROVIDER=openai MODEL_NAME=gpt-4o \
#     MODEL_API_KEY=sk-proj-xxx \
#     bash scripts/run_containerized.sh wc-coupon-campaign-gcal-gform
#
#   # Via aihubmix (OpenAI-compatible endpoint):
#   MODEL_PROVIDER=aihubmix MODEL_NAME=claude-3-5-sonnet-20241022 \
#     MODEL_API_KEY=sk-xxx \
#     bash scripts/run_containerized.sh howtocook-meal-plan-gcal
#
#   # Native Anthropic:
#   MODEL_PROVIDER=anthropic MODEL_NAME=claude-3-5-haiku-20241022 \
#     MODEL_API_KEY=sk-ant-xxx \
#     bash scripts/run_containerized.sh howtocook-meal-plan-gcal 50

set -euo pipefail

# ---------------------------------------------------------------------------
# Arguments
# ---------------------------------------------------------------------------
TASK="${1:?Usage: $0 <task_name> [max_steps] [image]}"
MAX_STEPS="${2:-100}"
IMAGE="${3:-toolathlon-pack:latest}"

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TASK_SOURCE="$PROJECT_ROOT/tasks/finalpool/$TASK"
DUMPS_DIR="$PROJECT_ROOT/dumps"
LOCK_FILE="$DUMPS_DIR/.run.lock"

# ---------------------------------------------------------------------------
# Validate task directory exists in the image source tree
# ---------------------------------------------------------------------------
if [[ ! -d "$TASK_SOURCE" ]]; then
    echo "[error] Task directory not found: $TASK_SOURCE" >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Container naming
# ---------------------------------------------------------------------------
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
SAFE_TASK="$(echo "$TASK" | tr '/' '-')"
CONTAINER_NAME="toolathlon-${SAFE_TASK}-${TIMESTAMP}"

# Output on the host: dumps/<task>/<timestamp>/
# Mounted into the container as /workspace/dumps so that eval_config's
# dump_path="./dumps/" resolves to /workspace/dumps/ inside the container.
OUTPUT_DIR="$DUMPS_DIR/$TASK/$TIMESTAMP"
mkdir -p "$OUTPUT_DIR" "$DUMPS_DIR"

# ---------------------------------------------------------------------------
# Logging helpers
# ---------------------------------------------------------------------------
log()  { echo "[$(date +%H:%M:%S)] $*"; }
warn() { echo "[$(date +%H:%M:%S)] [warn] $*" >&2; }
die()  { echo "[$(date +%H:%M:%S)] [error] $*" >&2; exit 1; }

# ---------------------------------------------------------------------------
# Cleanup: stop and remove the ephemeral container on any exit
# ---------------------------------------------------------------------------
cleanup() {
    log "Cleaning up container $CONTAINER_NAME ..."
    docker stop  "$CONTAINER_NAME" >/dev/null 2>&1 || true
    docker rm    "$CONTAINER_NAME" >/dev/null 2>&1 || true
    log "Container removed."
}
trap cleanup EXIT

# ---------------------------------------------------------------------------
# Prerequisites check
# ---------------------------------------------------------------------------
check_prerequisites() {
    command -v docker >/dev/null 2>&1 || die "docker not found in PATH"

    # Verify the image exists locally
    if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
        die "Image '$IMAGE' not found. Build it first: docker build -t $IMAGE ."
    fi

    # Verify toolathlon_net network exists (created by docker compose up -d postgres)
    if ! docker network inspect toolathlon_net >/dev/null 2>&1; then
        die "Network 'toolathlon_net' not found. Run: docker compose up -d postgres"
    fi

    # Verify postgres container is running and healthy
    local pg_status
    pg_status="$(docker inspect --format '{{.State.Health.Status}}' toolathlon_pg 2>/dev/null || echo "missing")"
    if [[ "$pg_status" != "healthy" ]]; then
        die "toolathlon_pg is not healthy (status: $pg_status). Run: docker compose up -d postgres"
    fi
}

# ---------------------------------------------------------------------------
# Sequential lock: only one task runs at a time (shared postgres constraint)
#
# Uses flock(1) on Linux; falls back to a mkdir-based atomic lock on macOS
# (where flock is not available by default).
# ---------------------------------------------------------------------------
LOCK_DIR="$DUMPS_DIR/.run.lock.d"

acquire_lock() {
    if command -v flock >/dev/null 2>&1; then
        # Linux: flock on a file descriptor
        exec 9>"$LOCK_FILE"
        if ! flock --nonblock 9 2>/dev/null; then
            warn "Another task is already running (lock: $LOCK_FILE)."
            warn "Waiting for it to finish before starting $TASK ..."
            flock 9
        fi
    else
        # macOS fallback: mkdir is atomic on POSIX filesystems
        while ! mkdir "$LOCK_DIR" 2>/dev/null; do
            warn "Another task is already running (lock: $LOCK_DIR)."
            warn "Waiting 3s before retrying ..."
            sleep 3
        done
        # Release the mkdir lock on exit (in addition to the container cleanup)
        trap 'rmdir "$LOCK_DIR" 2>/dev/null || true; cleanup' EXIT
    fi
    log "Lock acquired."
}

# ---------------------------------------------------------------------------
# Start the ephemeral container
# ---------------------------------------------------------------------------
start_container() {
    log "Starting container $CONTAINER_NAME ..."

    # Collect model-related env vars that are set on the host.
    # MODEL_PROVIDER overrides the provider key in main.py (aihubmix, openai, anthropic …).
    # MODEL_PLATFORM overrides the CAMEL platform inside model_provider.py (finer-grained).
    local env_args=()
    for var in MODEL_PROVIDER MODEL_PLATFORM MODEL_NAME MODEL_API_KEY MODEL_API_URL; do
        [[ -n "${!var:-}" ]] && env_args+=("-e" "${var}=${!var}")
    done

    docker run -d \
        --name "$CONTAINER_NAME" \
        --network toolathlon_net \
        -e PGHOST=toolathlon_pg \
        -e PG_HOST=toolathlon_pg \
        -e PGPORT=5432 \
        -e PGUSER=eigent \
        -e PGPASSWORD=camel \
        -e PGDATABASE=toolathlon_gym \
        -e LOCAL_SERVERS_PATH=/opt/local_servers \
        -e PYTHON_BIN=/opt/venv/bin/python3 \
        "${env_args[@]}" \
        -v "$OUTPUT_DIR:/workspace/dumps" \
        -w /workspace \
        "$IMAGE" \
        sleep 3600 \
        >/dev/null

    log "Container started."
}

# ---------------------------------------------------------------------------
# Wait until the container is responsive
# ---------------------------------------------------------------------------
wait_for_container() {
    local max_wait=30
    local count=0
    log "Waiting for container to be ready ..."
    while (( count < max_wait )); do
        if docker exec "$CONTAINER_NAME" true >/dev/null 2>&1; then
            log "Container is ready."
            return 0
        fi
        (( count++ ))
        sleep 1
    done
    die "Container did not become ready within ${max_wait}s"
}

# ---------------------------------------------------------------------------
# Run the task inside the container
# ---------------------------------------------------------------------------
run_task() {
    log "Running task: $TASK (max_steps=$MAX_STEPS) ..."
    log "Output directory: $OUTPUT_DIR"

    # Fix sent_log foreign key (init.sql.gz lacks ON DELETE CASCADE)
    docker exec "$CONTAINER_NAME" \
        /opt/venv/bin/python3 -c "
import psycopg2, os
conn = psycopg2.connect(host=os.environ['PGHOST'], database=os.environ['PGDATABASE'],
                        user=os.environ['PGUSER'], password=os.environ['PGPASSWORD'])
conn.autocommit = True
cur = conn.cursor()
try:
    cur.execute('ALTER TABLE email.sent_log DROP CONSTRAINT sent_log_message_id_fkey')
    cur.execute('ALTER TABLE email.sent_log ADD CONSTRAINT sent_log_message_id_fkey FOREIGN KEY (message_id) REFERENCES email.messages(id) ON DELETE CASCADE')
except: pass
conn.close()
" 2>/dev/null || true

    # main.py picks up MODEL_* env vars automatically; the eval_config inside
    # the image supplies all other defaults (model, provider, dump_path).
    docker exec "$CONTAINER_NAME" \
        /opt/venv/bin/python3 main.py \
            --task_dir  "$TASK" \
            --max_steps "$MAX_STEPS" \
            --debug \
        2>&1 | tee "$OUTPUT_DIR/run.log"
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
log "=============================================="
log "  Task:      $TASK"
log "  Max steps: $MAX_STEPS"
log "  Image:     $IMAGE"
log "  Model:     ${MODEL_NAME:-<from eval_config>} (${MODEL_PROVIDER:-<from eval_config>})"
log "  Output:    $OUTPUT_DIR"
log "=============================================="

check_prerequisites
acquire_lock
start_container
wait_for_container
run_task

log "Done. Results written to: $OUTPUT_DIR"
