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

class BaseReviewEngine(ABC):
    def __init__(self, model_name: str, use_gpu: bool = True):
        self.device = 0 if (use_gpu and torch.cuda.is_available()) else -1
        print(f"Using device: {'GPU' if self.device == 0 else 'CPU'}")
        self.model_name = model_name
        self.personal = PersonalizationStore("personal.db")
        self.pipe = self._load_llm()

    def _load_llm(self):
        tokenizer = AutoTokenizer.from_pretrained(
            self.model_name, trust_remote_code=True, token=HUGGINGFACE_TOKEN
        )
        model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16 if self.device == 0 else torch.float32,
            low_cpu_mem_usage=True,
            trust_remote_code=True,
            token=HUGGINGFACE_TOKEN
        )
        pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, device=self.device)
        if getattr(pipe, "tokenizer", None) and getattr(pipe.tokenizer, "pad_token", None) is None:
            pipe.tokenizer.pad_token = pipe.tokenizer.eos_token
        return pipe

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