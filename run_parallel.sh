#!/bin/bash
# Fully parallel benchmark: every task gets its own PostgreSQL + agent container.
# Concurrency is controlled by a semaphore (max N tasks running at once).
#
# Usage:
#   ./run_fully_parallel.sh <max_concurrent> [task1 task2 ...]
#   ./run_fully_parallel.sh 10                          # all tasks, 10 at a time
#   ./run_fully_parallel.sh 5 task-a task-b task-c      # specific tasks
#
# Environment variables:
#   MODEL / PROVIDER / MAX_STEPS / IMAGE / GEMINI_API_KEY / MODEL_API_KEY
#   MODEL_PLATFORM / MODEL_API_URL

set -uo pipefail
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

# ─── Arguments ────────────────────────────────────────────────────────────────
MAX_CONCURRENT="${1:?Usage: $0 <max_concurrent> [task1] [task2] ...}"
shift

if [ $# -gt 0 ]; then
    TASKS=("$@")
else
    TASKS=()
    while IFS= read -r t; do TASKS+=("$t"); done < <(ls tasks/finalpool/)
fi

# ─── Config ───────────────────────────────────────────────────────────────────
MODEL="${MODEL:-gemini-3-flash-preview}"
PROVIDER="${PROVIDER:-gemini}"
MAX_STEPS="${MAX_STEPS:-100}"
IMAGE="${IMAGE:-toolathlon_pack-toolathlon:latest}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_DIR="benchmark_logs/fully_parallel_${TIMESTAMP}"
DOCKER=$(which docker 2>/dev/null || echo "/usr/local/bin/docker")

mkdir -p "$LOG_DIR"

echo "============================================="
echo "Fully Parallel Benchmark"
echo "  Max concurrent: $MAX_CONCURRENT"
echo "  Total tasks:    ${#TASKS[@]}"
echo "  Model:          $PROVIDER/$MODEL"
echo "  Max steps:      $MAX_STEPS"
echo "  Image:          $IMAGE"
echo "  Log dir:        $LOG_DIR"
echo "============================================="

# ─── Verify image exists ─────────────────────────────────────────────────────
if ! $DOCKER run --rm "$IMAGE" true >/dev/null 2>&1; then
    echo "[error] Image '$IMAGE' not found or cannot run. Build it first."
    exit 1
fi

# ─── Semaphore via a FIFO ────────────────────────────────────────────────────
FIFO="$LOG_DIR/.semaphore"
mkfifo "$FIFO"
exec 3<>"$FIFO"
rm -f "$FIFO"

# Fill the semaphore with N tokens
for ((i = 0; i < MAX_CONCURRENT; i++)); do
    echo >&3
done

# ─── Summary file ────────────────────────────────────────────────────────────
SUMMARY="$LOG_DIR/summary.csv"
echo "task,status,eval_pass,duration_s" > "$SUMMARY"
SUMMARY_LOCK="$LOG_DIR/.summary.lock"

append_summary() {
    # Atomic append using a lock directory (works on both Linux and macOS)
    while ! mkdir "$SUMMARY_LOCK" 2>/dev/null; do sleep 0.1; done
    echo "$1" >> "$SUMMARY"
    rmdir "$SUMMARY_LOCK"
}

# ─── Track all containers for cleanup ────────────────────────────────────────
CONTAINER_LIST="$LOG_DIR/.containers"
touch "$CONTAINER_LIST"
CONTAINER_LIST_LOCK="$LOG_DIR/.containers.lock"

register_container() {
    while ! mkdir "$CONTAINER_LIST_LOCK" 2>/dev/null; do sleep 0.1; done
    echo "$1" >> "$CONTAINER_LIST"
    rmdir "$CONTAINER_LIST_LOCK"
}

cleanup_all() {
    echo ""
    echo "Cleaning up all containers..."
    if [ -f "$CONTAINER_LIST" ]; then
        while IFS= read -r c; do
            $DOCKER rm -f "$c" >/dev/null 2>&1 || true
        done < "$CONTAINER_LIST"
    fi
    # Close the semaphore fd
    exec 3>&- 2>/dev/null || true
    echo "Cleanup done."
}
trap cleanup_all EXIT

# ─── Export helpers for subshells ─────────────────────────────────────────────
export MODEL PROVIDER MAX_STEPS IMAGE DOCKER LOG_DIR SUMMARY SUMMARY_LOCK CONTAINER_LIST CONTAINER_LIST_LOCK
export GEMINI_API_KEY="${GEMINI_API_KEY:-}"
export MODEL_API_KEY="${MODEL_API_KEY:-}"
export MODEL_PLATFORM="${MODEL_PLATFORM:-}"
export MODEL_API_URL="${MODEL_API_URL:-}"
export MODEL_PROVIDER="${MODEL_PROVIDER:-}"
export -f append_summary register_container

# ─── Run a single task with full isolation ────────────────────────────────────
run_one_task() {
    local TASK="$1"
    local TASK_HASH=$(echo "$TASK" | md5 -q 2>/dev/null || echo "$TASK" | md5sum 2>/dev/null | cut -c1-8 || echo "$RANDOM")
    local TASK_ID="$$-${TASK_HASH:0:8}"
    local PG_CONTAINER="pg-${TASK_ID}"
    local AGENT_CONTAINER="agent-${TASK_ID}"
    local TASK_LOG="$LOG_DIR/${TASK}.log"
    local NET_NAME="net-${TASK_ID}"

    local START_TS=$(date +%s)
    echo "[$(date +%H:%M:%S)] START  $TASK"

    # Create an isolated Docker network for this task
    $DOCKER network create "$NET_NAME" >> "$TASK_LOG" 2>&1 || true
    register_container "$PG_CONTAINER"
    register_container "$AGENT_CONTAINER"

    # --- Start PostgreSQL ---
    $DOCKER run -d \
        --name "$PG_CONTAINER" \
        --network "$NET_NAME" \
        -e POSTGRES_DB=toolathlon_gym \
        -e POSTGRES_USER=eigent \
        -e POSTGRES_PASSWORD=camel \
        -v "$(pwd)/db/init.sql.gz:/docker-entrypoint-initdb.d/init.sql.gz:ro" \
        --health-cmd="pg_isready -U eigent -d toolathlon_gym" \
        --health-interval=3s --health-retries=20 \
        postgres:15 >> "$TASK_LOG" 2>&1

    # Wait for postgres to be healthy
    local RETRIES=60 READY=false
    while [ $RETRIES -gt 0 ]; do
        local ST=$($DOCKER inspect --format '{{.State.Health.Status}}' "$PG_CONTAINER" 2>/dev/null || echo "missing")
        if [ "$ST" = "healthy" ]; then READY=true; break; fi
        sleep 2
        RETRIES=$((RETRIES - 1))
    done

    if [ "$READY" != "true" ]; then
        echo "[$(date +%H:%M:%S)] FAIL   $TASK (postgres not healthy)" | tee -a "$TASK_LOG"
        local END_TS=$(date +%s)
        append_summary "${TASK},pg_fail,null,$((END_TS - START_TS))"
        $DOCKER rm -f "$PG_CONTAINER" >> "$TASK_LOG" 2>&1 || true
        $DOCKER network rm "$NET_NAME" >> "$TASK_LOG" 2>&1 || true
        return 1
    fi

    # Fix sent_log foreign key
    $DOCKER run --rm --network "$NET_NAME" \
        -e PGHOST="$PG_CONTAINER" -e PGPORT=5432 \
        -e PGDATABASE=toolathlon_gym -e PGUSER=eigent -e PGPASSWORD=camel \
        "$IMAGE" /opt/venv/bin/python3 -c "
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
" >> "$TASK_LOG" 2>&1 || true

    # --- Start agent container ---
    local ENV_ARGS=()
    [ -n "$GEMINI_API_KEY" ]  && ENV_ARGS+=("-e" "GEMINI_API_KEY=$GEMINI_API_KEY")
    [ -n "$MODEL_API_KEY" ]   && ENV_ARGS+=("-e" "MODEL_API_KEY=$MODEL_API_KEY")
    [ -n "$MODEL_PLATFORM" ]  && ENV_ARGS+=("-e" "MODEL_PLATFORM=$MODEL_PLATFORM")
    [ -n "$MODEL_API_URL" ]   && ENV_ARGS+=("-e" "MODEL_API_URL=$MODEL_API_URL")
    [ -n "$MODEL_PROVIDER" ]  && ENV_ARGS+=("-e" "MODEL_PROVIDER=$MODEL_PROVIDER")

    $DOCKER run -d \
        --name "$AGENT_CONTAINER" \
        --network "$NET_NAME" \
        -e PGHOST="$PG_CONTAINER" \
        -e PG_HOST="$PG_CONTAINER" \
        -e PGPORT=5432 \
        -e PGUSER=eigent \
        -e PGPASSWORD=camel \
        -e PGDATABASE=toolathlon_gym \
        -e LOCAL_SERVERS_PATH=/opt/local_servers \
        -e PYTHON_BIN=/opt/venv/bin/python3 \
        -e MODEL_PROVIDER="$PROVIDER" \
        "${ENV_ARGS[@]}" \
        -v "$(pwd):/workspace" \
        -w /workspace \
        "$IMAGE" sleep 7200 >> "$TASK_LOG" 2>&1

    sleep 1

    # --- Run the task ---
    $DOCKER exec \
        "$AGENT_CONTAINER" \
        /opt/venv/bin/python3 -u /workspace/main.py \
            --provider "$PROVIDER" \
            --model_name "$MODEL" \
            --task_dir "$TASK" \
            --max_steps "$MAX_STEPS" \
        >> "$TASK_LOG" 2>&1 || true

    local END_TS=$(date +%s)
    local DURATION=$((END_TS - START_TS))

    # --- Parse results ---
    local STATUS="unknown" EVAL_PASS="null"
    if grep -q "Status: success" "$TASK_LOG" 2>/dev/null; then
        STATUS="success"
    elif grep -q "Status: failed" "$TASK_LOG" 2>/dev/null; then
        STATUS="failed"
    fi

    if [ "$STATUS" = "success" ]; then
        if grep -q "Pass:.*True" "$TASK_LOG" 2>/dev/null; then
            EVAL_PASS="True"
        elif grep -q "Pass:.*False" "$TASK_LOG" 2>/dev/null; then
            EVAL_PASS="False"
        fi
    fi

    append_summary "${TASK},${STATUS},${EVAL_PASS},${DURATION}"

    # --- Determine result label ---
    local RESULT="AGENT_FAIL"
    if [ "$EVAL_PASS" = "True" ]; then
        RESULT="PASS"
    elif [ "$STATUS" = "success" ]; then
        RESULT="EVAL_FAIL"
    fi

    echo "[$(date +%H:%M:%S)] DONE   $TASK -> $RESULT (${DURATION}s)"

    # --- Cleanup this task's containers and network ---
    $DOCKER rm -f "$AGENT_CONTAINER" >> "$TASK_LOG" 2>&1 || true
    $DOCKER rm -f "$PG_CONTAINER" >> "$TASK_LOG" 2>&1 || true
    $DOCKER network rm "$NET_NAME" >> "$TASK_LOG" 2>&1 || true
}

export -f run_one_task

# ─── Launch all tasks with semaphore-controlled concurrency ───────────────────
PIDS=()
for TASK in "${TASKS[@]}"; do
    # Acquire semaphore token (blocks if all N slots are in use)
    read -u 3

    (
        run_one_task "$TASK"
        # Release semaphore token
        echo >&3
    ) &
    PIDS+=($!)
done

# ─── Wait for all tasks ──────────────────────────────────────────────────────
echo ""
echo "All ${#TASKS[@]} tasks launched (max $MAX_CONCURRENT concurrent). Waiting..."
echo ""

FAILED=0
for pid in "${PIDS[@]}"; do
    wait "$pid" || FAILED=$((FAILED + 1))
done

# ─── Report ──────────────────────────────────────────────────────────────────
echo ""
echo "============================================="
echo "RESULTS"
echo "============================================="

python3 - "$SUMMARY" << 'PYEOF'
import sys, csv

summary_file = sys.argv[1]
pass_count = eval_fail = agent_fail = other = 0
total_duration = 0
results = []

with open(summary_file) as f:
    reader = csv.DictReader(f)
    for row in reader:
        task = row["task"]
        status = row["status"]
        eval_pass = row["eval_pass"]
        duration = int(row["duration_s"])
        total_duration += duration

        if eval_pass == "True":
            label = "PASS"
            pass_count += 1
        elif status == "success":
            label = "EVAL_FAIL"
            eval_fail += 1
        elif status == "pg_fail":
            label = "PG_FAIL"
            other += 1
        else:
            label = "AGENT_FAIL"
            agent_fail += 1
        results.append((task, label, duration))

# Print individual results
for task, label, dur in sorted(results):
    print(f"  {task:<55s} {label:<12s} ({dur}s)")

total = pass_count + eval_fail + agent_fail + other
print()
if total > 0:
    print(f"  PASS:       {pass_count:4d}  ({100*pass_count/total:.1f}%)")
    print(f"  EVAL_FAIL:  {eval_fail:4d}  ({100*eval_fail/total:.1f}%)")
    print(f"  AGENT_FAIL: {agent_fail:4d}  ({100*agent_fail/total:.1f}%)")
    if other:
        print(f"  OTHER_FAIL: {other:4d}  ({100*other/total:.1f}%)")
    print(f"  TOTAL:      {total:4d}")
    print(f"  Wall time sum: {total_duration}s")
else:
    print("  No results.")
PYEOF

echo ""
echo "Summary CSV: $SUMMARY"
echo "Task logs:   $LOG_DIR/<task>.log"
echo "Done."
