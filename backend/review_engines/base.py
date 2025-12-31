from abc import ABC, abstractmethod
from pathlib import Path
from dotenv import load_dotenv
import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from personalization import PersonalizationStore
from schemas import ReviewOutput

env_path = Path('.', '.env')
load_dotenv(env_path)
HUGGINGFACE_TOKEN = os.environ.get("HUGGINGFACE_TOKEN")
HF_CACHE_DIR = (
    os.environ.get("HF_HOME")
    or os.environ.get("TRANSFORMERS_CACHE")
    or os.path.expanduser("~/.cache/huggingface")
)

class BaseReviewEngine(ABC):
    """
    Base class for all language reviews
    1. Loads/PreLoads model
    2. Caches pipeline
    3. Automatic GPU/CPU and HF Cache handling
    """

    _pipe = None
    _model_name = None
    _device = None

    def __init__(self, model_name: str, use_gpu: bool = True):
        self.model_name = model_name
        self.device = 0 if (use_gpu and torch.cuda.is_available()) else -1
        print(f"[BaseReviewEngine] Using {'GPU' if self.device == 0 else 'CPU'}")
        self.personal = PersonalizationStore("personal.db")
        # self.pipe = self._load_llm()
        self.pipe = self.preload_llm(model_name, self.device)


    @classmethod
    def preload_llm(cls, model_name: str, device: int = -1, hf_token: str|None = None):
        """
        Loads and caches hf model
        """
        if (
            cls._pipe is not None
            and cls._model_name == model_name
            and cls._device == device
        ):
            return cls._pipe

    # def _load_llm(self):
        os.environ.setdefault("HF_HOME", HF_CACHE_DIR)
        if hf_token:
            os.environ["HUGGINGFACE_TOKEN"] = hf_token

        print(f"[BaseReviewEngine] Loading model: {model_name}")

        tokenizer = AutoTokenizer.from_pretrained(
            model_name, trust_remote_code=True, token=HUGGINGFACE_TOKEN
        )
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if device == 0 else torch.float32,
            low_cpu_mem_usage=True,
            trust_remote_code=True,
            token=HUGGINGFACE_TOKEN
        )
        
        pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, device=device)
        if getattr(pipe, "tokenizer", None) and getattr(pipe.tokenizer, "pad_token", None) is None:
            pipe.tokenizer.pad_token = pipe.tokenizer.eos_token

        cls._pipe = pipe
        cls._model_name = model_name
        cls._device = device
        
        print(f"[BaseReviewEngine] Model {model_name} ready on device {device}")
        return cls._pipe

    def run_llm(self, prompt: str, max_new_tokens: int = 128) -> str:
        out = self.pipe(prompt, max_new_tokens=max_new_tokens, do_sample=False)
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
    def review(self, code: str, filename: str = None) -> ReviewOutput:
        ...