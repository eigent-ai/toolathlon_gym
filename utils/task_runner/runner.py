"""TaskRunner: entry point for running a single task."""
from utils.roles.task_agent import TaskAgent, TaskStatus
from utils.data_structures.task_config import TaskConfig
from utils.api_model.model_provider import build_model
from utils.general.helper import print_color
from pprint import pprint


class TaskRunner:
    @staticmethod
    async def run_single_task(
        task_config: TaskConfig,
        model_name: str,
        provider: str,
        max_steps: int = 100,
        debug: bool = False,
    ) -> TaskStatus:
        model = build_model(model_name, provider)

        if debug:
            print_color("=== Task config ===", "magenta")
            pprint(task_config)

        agent = TaskAgent(
            task_config=task_config,
            model=model,
            max_steps=max_steps,
            debug=debug,
        )
        return await agent.run()

    @staticmethod
    def load_configs(eval_config_dict: dict):
        """Parse eval_config.json into (model_name, provider, max_steps, dump_path)."""
        agent_cfg = eval_config_dict.get("agent", {})
        model_name = agent_cfg.get("model_name", "gpt-4o-mini")
        provider   = agent_cfg.get("provider", "openai")
        max_steps  = eval_config_dict.get("global_task_config", {}).get(
            "max_steps_under_single_turn_mode", 100)
        dump_path  = eval_config_dict.get("dump_path", "./dumps/")
        return model_name, provider, max_steps, dump_path
