import torch
import os
from abc import ABC, abstractmethod
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from app.personalization import PersonalizationStore
from app.schemas import ReviewOutput
from app.config import LLMConfig

HUGGINGFACE_TOKEN = os.environ.get("HUGGINGFACE_TOKEN")

class BaseReviewEngine(ABC):
    """
    Base class for all language reviews
    1. Loads/PreLoads model
    2. Caches pipeline
    3. Automatic GPU/CPU and HF Cache handling
    """

    _pipe = None
    _config: LLMConfig | None = None
    _personal = None

    # ----------------- Global Initialization -----------------
    @classmethod
    def initialize_global(cls, config: LLMConfig):
        if cls._pipe is not None:
            return

        device = 0 if (torch.cuda.is_available()) else -1
        print(f"[BaseReviewEngine] Loading {config.model_name} on {'GPU' if device == 0 else 'CPU'}")

        tokenizer = AutoTokenizer.from_pretrained(
            config.model_name, 
            trust_remote_code=True, 
            token=HUGGINGFACE_TOKEN
        )

        model = AutoModelForCausalLM.from_pretrained(
            config.model_name,
            torch_dtype=torch.float16 if device == 0 else torch.float32,
            low_cpu_mem_usage=True,
            trust_remote_code=True,
            token=HUGGINGFACE_TOKEN
        )
        
        cls._pipe = pipeline(
            "text-generation", 
            model=model, 
            tokenizer=tokenizer, 
            device=device
        )

        if getattr(cls._pipe, "tokenizer", None) and getattr(cls._pipe.tokenizer, "pad_token", None) is None:
            cls._pipe.tokenizer.pad_token = cls._pipe.tokenizer.eos_token

        cls._config = config
        cls._personal = PersonalizationStore("personal.db")

        print("[BaseReviewEngine] Model initialized successfully")

    def __init__(self):
        if self.__class__._pipe is None:
            raise RuntimeError (
                "Model not initialized. Call BaseReviewEngine.initialize_global() at startup."
            )
        
        self.pipe = self.__class__._pipe
        self.personal = self.__class__._personal
        self.config = self.__class__._config

    def run_llm(self, prompt: str) -> str:
        out = self.pipe(prompt, max_new_tokens=self.config.max_new_tokens, do_sample=False)
        text = out[0]["generated_text"] or out[0].get("text") or ""
        return text.split("Feedback:")[-1].strip()

    def build_prompt(self, code: str, language: str = "Python") -> str:
        examples = self.personal.get_examples(code, k=3)
        prompt = f"You are a senior {language} software engineer. Provide concise, actionable review feedback."
        for ex_code, ex_feedback in examples:
            prompt += f"\nExample Code:\n{ex_code}\nExample Feedback:\n{ex_feedback}\n"
        prompt += f"\nReview this code:\n{code}\nFeedback:\n"
        return prompt

    @abstractmethod
    def review(self, code: str, filename: str | None = None) -> ReviewOutput:
        ...