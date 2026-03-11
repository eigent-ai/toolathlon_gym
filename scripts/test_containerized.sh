#!/bin/bash
# Smoke tests for run_containerized.sh infrastructure.
#
# Tests (no full task execution required):
#   1. docker CLI is available
#   2. toolathlon_net network exists
#   3. toolathlon_pg is running and healthy
#   4. Image exists and venv / local_servers are in place
#   5. Container can reach postgres over the named network
#   6. Sequential lock prevents concurrent runs
#
# Usage:
#   bash scripts/test_containerized.sh [image]

set -euo pipefail

IMAGE="${1:-toolathlon-pack:latest}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
PASS=0
FAIL=0

pass() { echo "  [PASS] $*"; PASS=$(( PASS + 1 )); }
fail() { echo "  [FAIL] $*" >&2; FAIL=$(( FAIL + 1 )); }

section() { echo; echo "=== $* ==="; }

# Run a command inside a disposable container and remove it afterwards.
# Usage: run_in_temp_container <name_suffix> <command...>
run_in_temp_container() {
    local suffix="$1"; shift
    local name="toolathlon-test-${suffix}-$$"
    docker run --rm \
        --name "$name" \
        --network toolathlon_net \
        -e PGHOST=toolathlon_pg \
        -e PGPORT=5432 \
        -e PGUSER=eigent \
        -e PGPASSWORD=camel \
        -e PGDATABASE=toolathlon_gym \
        -e LOCAL_SERVERS_PATH=/opt/local_servers \
        -e PYTHON_BIN=/opt/venv/bin/python3 \
        "$IMAGE" \
        "$@"
}

# ---------------------------------------------------------------------------
# Test 1: docker CLI
# ---------------------------------------------------------------------------
section "Test 1: docker CLI"
if command -v docker >/dev/null 2>&1; then
    pass "docker is available ($(docker --version))"
else
    fail "docker not found in PATH"
fi

# ---------------------------------------------------------------------------
# Test 2: toolathlon_net network
# ---------------------------------------------------------------------------
section "Test 2: toolathlon_net network"
if docker network inspect toolathlon_net >/dev/null 2>&1; then
    pass "toolathlon_net network exists"
else
    fail "toolathlon_net not found — run: docker compose up -d postgres"
fi

# ---------------------------------------------------------------------------
# Test 3: postgres health
# ---------------------------------------------------------------------------
section "Test 3: postgres health"
pg_status="$(docker inspect --format '{{.State.Health.Status}}' toolathlon_pg 2>/dev/null || echo "missing")"
if [[ "$pg_status" == "healthy" ]]; then
    pass "toolathlon_pg is healthy"
else
    fail "toolathlon_pg status: $pg_status — run: docker compose up -d postgres"
fi

# ---------------------------------------------------------------------------
# Test 4: image and key paths
# ---------------------------------------------------------------------------
section "Test 4: image and key paths inside container"
if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
    fail "Image '$IMAGE' not found — run: docker build -t $IMAGE ."
else
    pass "Image '$IMAGE' exists"

    # Check /opt/venv
    if run_in_temp_container "venv" test -f /opt/venv/bin/python3 >/dev/null 2>&1; then
        pass "/opt/venv/bin/python3 exists"
    else
        fail "/opt/venv/bin/python3 not found in image"
    fi

    # Check /opt/local_servers
    if run_in_temp_container "servers" test -d /opt/local_servers >/dev/null 2>&1; then
        pass "/opt/local_servers directory exists"
    else
        fail "/opt/local_servers not found in image"
    fi

    # Check main.py is present
    if run_in_temp_container "main" test -f /workspace/main.py >/dev/null 2>&1; then
        pass "/workspace/main.py exists in image"
    else
        fail "/workspace/main.py not found in image"
    fi

    # Check tasks directory
    task_count="$(run_in_temp_container "tasks" bash -c 'ls /workspace/tasks/finalpool | wc -l' 2>/dev/null || echo 0)"
    if (( task_count > 0 )); then
        pass "/workspace/tasks/finalpool contains $task_count tasks"
    else
        fail "/workspace/tasks/finalpool is empty or missing"
    fi
fi

# ---------------------------------------------------------------------------
# Test 5: container → postgres connectivity
# ---------------------------------------------------------------------------
section "Test 5: postgres connectivity from container"
if (( FAIL == 0 )) || docker image inspect "$IMAGE" >/dev/null 2>&1; then
    pg_result="$(run_in_temp_container "pgconn" \
        bash -c 'PGPASSWORD=camel psql -h toolathlon_pg -U postgres -d toolathlon -tAc "SELECT 1"' \
        2>/dev/null || echo "error")"
    if [[ "$pg_result" == "1" ]]; then
        pass "Container can reach toolathlon_pg and query the database"
    else
        fail "Container cannot reach toolathlon_pg (result: $pg_result)"
    fi
fi

# ---------------------------------------------------------------------------
# Test 6: sequential lock
# ---------------------------------------------------------------------------
section "Test 6: sequential lock"
DUMPS_DIR="$PROJECT_ROOT/dumps"
LOCK_FILE="$DUMPS_DIR/.run.lock"
LOCK_DIR="$DUMPS_DIR/.run.lock.d"
mkdir -p "$DUMPS_DIR"
# Clean up any leftover lock state from a previous failed run
rm -f "$LOCK_FILE"; rmdir "$LOCK_DIR" 2>/dev/null || true

if command -v flock >/dev/null 2>&1; then
    # Linux path: flock-based lock
    (
        exec 9>"$LOCK_FILE"
        flock 9
        sleep 2
    ) &
    HOLDER_PID=$!
    sleep 0.3

    if ( exec 9>"$LOCK_FILE"; flock --nonblock 9 ) 2>/dev/null; then
        fail "flock: non-blocking lock succeeded while holder is running"
    else
        pass "flock: non-blocking lock blocked while lock is held"
    fi

    wait $HOLDER_PID 2>/dev/null || true

    if ( exec 9>"$LOCK_FILE"; flock --nonblock 9 ) 2>/dev/null; then
        pass "flock: lock acquirable after holder exits"
    else
        fail "flock: lock still blocked after holder exited"
    fi
else
    # macOS fallback: mkdir-based lock
    mkdir "$LOCK_DIR"

    if mkdir "$LOCK_DIR" 2>/dev/null; then
        fail "mkdir lock: second mkdir succeeded (should have failed)"
        rmdir "$LOCK_DIR" 2>/dev/null || true
    else
        pass "mkdir lock: second mkdir correctly blocked"
    fi

    rmdir "$LOCK_DIR"

    if mkdir "$LOCK_DIR" 2>/dev/null; then
        pass "mkdir lock: acquirable after release"
        rmdir "$LOCK_DIR"
    else
        fail "mkdir lock: still blocked after release"
    fi
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo
echo "=============================="
echo "  PASS: $PASS"
echo "  FAIL: $FAIL"
echo "=============================="

(( FAIL == 0 ))   # exit 0 on all pass, non-zero otherwise
