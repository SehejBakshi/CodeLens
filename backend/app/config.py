import os

class LLMConfig:
    def __init__(self, model_name: str, max_new_tokens: int):
        self.model_name = model_name
        self.max_new_tokens = max_new_tokens

def load_llm_config(require_explicit: bool = False) -> LLMConfig:
    model_name = os.environ.get("BASE_MODEL_NAME")
    max_tokens = os.environ.get("MAX_NEW_TOKENS")

    if require_explicit:
        if not model_name:
            raise RuntimeError("BASE_MODEL_NAME must be set")
        if not max_tokens:
            raise RuntimeError("MAX_NEW_TOKENS must be set")
        
    return LLMConfig(
        model_name=model_name or "refactai/Refact-1_6B-fim",
        max_new_tokens=int(max_tokens or 128)
    )