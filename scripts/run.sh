#!/bin/bash
# Run a task using CAMEL ChatAgent + local MCP servers (PostgreSQL-backed)
#
# Usage:
#   cd Toolathlon_Pack
#   bash scripts/run.sh howtocook-meal-plan-gcal
#   bash scripts/run.sh <task_name> [max_steps]
#
# Environment variables for model selection (set before running):
#   MODEL_PLATFORM=openai_compatible   (or: anthropic, openai, gemini, deepseek)
#   MODEL_NAME=claude-3-5-sonnet-20241022
#   MODEL_API_KEY=your-api-key
#   MODEL_API_URL=https://aihubmix.com/v1   (for openai_compatible)
#
# Quick examples:
#   # Via aihubmix (OpenAI-compatible endpoint):
#   MODEL_PLATFORM=openai_compatible MODEL_NAME=claude-3-5-sonnet-20241022 \
#     MODEL_API_KEY=sk-xxx MODEL_API_URL=https://aihubmix.com/v1 \
#     bash scripts/run.sh howtocook-meal-plan-gcal
#
#   # Via native Anthropic:
#   MODEL_PLATFORM=anthropic MODEL_NAME=claude-3-5-haiku-20241022 \
#     MODEL_API_KEY=sk-ant-xxx \
#     bash scripts/run.sh howtocook-meal-plan-gcal

TASK="${1:-howtocook-meal-plan-gcal}"
MAX_STEPS="${2:-100}"

echo "=============================================="
echo "  Task:     $TASK"
echo "  Model:    ${MODEL_NAME:-gemini-2.5-flash} (${MODEL_PLATFORM:-openai_compatible})"
echo "  Steps:    $MAX_STEPS"
echo "=============================================="

python3 main.py \
    --task_dir "$TASK" \
    --max_steps "$MAX_STEPS" \
    --debug
