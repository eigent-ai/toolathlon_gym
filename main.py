"""Toolathlon Pack – main entry point."""
import asyncio, argparse, os
from utils.general.helper import read_json, print_color
from utils.data_structures.task_config import TaskConfig
from utils.task_runner.runner import TaskRunner
from utils.evaluation.evaluator import TaskEvaluator


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--eval_config", default="scripts/eval_config.json")
    parser.add_argument("--task_dir", default="wc-coupon-campaign-gcal-gform")
    parser.add_argument("--model_name", default=None)
    parser.add_argument("--provider",   default=None)
    parser.add_argument("--max_steps",  type=int, default=None)
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--cn_mode", action="store_true")
    args = parser.parse_args()

    cfg = read_json(args.eval_config)
    model_name, provider, max_steps, dump_path = TaskRunner.load_configs(cfg)

    if args.model_name: model_name = args.model_name
    if args.provider:   provider   = args.provider
    if args.max_steps:  max_steps  = args.max_steps
    if os.environ.get("MODEL_NAME"):     model_name = os.environ["MODEL_NAME"]
    if os.environ.get("MODEL_PROVIDER"): provider   = os.environ["MODEL_PROVIDER"]

    # global_task_config drives log_file / agent_workspace path via dump_path
    global_task_config = {"dump_path": dump_path,
                          "max_steps_under_single_turn_mode": max_steps}

    task_config = TaskConfig.build(
        args.task_dir,
        agent_short_name=f"{provider}/{model_name}",
        global_task_config=global_task_config,
        single_turn_mode=True,
        cn_mode=args.cn_mode,
    )

    print_color(f"====== {args.task_dir} | {provider}/{model_name} | steps={max_steps} ======", "yellow")
    print_color(f"workspace : {task_config.agent_workspace}", "cyan")
    print_color(f"log       : {task_config.log_file}", "cyan")

    # Enable CAMEL model logging — writes each LLM request+response to camel_logs/
    os.environ["CAMEL_MODEL_LOG_ENABLED"] = "true"
    os.environ["CAMEL_LOG_DIR"] = os.path.join(task_config.task_root, "camel_logs")

    status = await TaskRunner.run_single_task(
        task_config=task_config,
        model_name=model_name,
        provider=provider,
        max_steps=max_steps,
        debug=args.debug,
    )
    print_color(f"\n====== Status: {status.value} ======", "yellow")

    print_color("\n====== Evaluating ======", "yellow")
    eval_res = await TaskEvaluator.evaluate_from_log_file(task_config.log_file)
    print(f"Pass:    {eval_res.get('pass', False)}")
    print(f"Details: {eval_res.get('details', 'N/A')}")
    return 0 if eval_res.get("pass", False) else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
