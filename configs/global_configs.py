# Configure your API key for the model provider you want to use.
class _Cfg(dict):
    def __getattr__(self, k): return self.get(k, "")
    def __setattr__(self, k, v): self[k] = v

global_configs = _Cfg(
    aihubmix_key="",
    openrouter_key="",
    qwen_official_key="",
    deepseek_official_key="",
    anthropic_official_key="",
    openai_official_key="",
    google_official_key="",
)
