import os
from pathlib import Path

from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers.pipelines import pipeline, TextGenerationPipeline
import torch
from personalization import PersonalizationStore
from analyzer import analyze_code
from security import scan_code
from  dotenv import load_dotenv

env_path = Path('.', '.env')
load_dotenv()

HUGGINGFACE_TOKEN = os.environ.get("HUGGINGFACE_TOKEN")

class ReviewEngine:
    def __init__(self, use_gpu=True):
        self.device = 0 if (use_gpu and torch.cuda.is_available()) else -1
        print(f"Using device: {'GPU' if self.device == 0 else 'CPU'}")
        self.pipe = self.load_llm()
        self.personal = PersonalizationStore("personal.db")

    def load_llm(self, use_gpu=True):
        model_name = "refactai/Refact-1_6B-fim"
        tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True, token=HUGGINGFACE_TOKEN)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if self.device == 0 else torch.float32,
            low_cpu_mem_usage=True,
            trust_remote_code=True, token=HUGGINGFACE_TOKEN
        )
        pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, device=self.device)
        pipe.tokenizer.pad_token = pipe.tokenizer.eos_token
        return pipe

    def build_prompt(self, code):
        examples = self.personal.get_examples(code, k=3)
        prompt = "You are a senior software engineer. Provide concise, actionable review feedback."
        for ex_code, ex_feedback in examples:
            prompt += f"\nExample Code:\n{ex_code}\nExample Feedback:\n{ex_feedback}\n"
        prompt += f"\nReview this code:\n{code}\nFeedback:\n"
        return prompt

    def run_llm(self, prompt):
        out = self.pipe(prompt, max_new_tokens=512, do_sample=False)
        text = out[0]["generated_text"]
        return text.split("Feedback:")[-1].strip()

    def review(self, code, filename=None):
        arch = analyze_code(code, filename)
        sec = scan_code(code, filename)
        prompt = self.build_prompt(code)
        feedback = self.run_llm(prompt)

        class ReviewResult:
            pass

        r = ReviewResult()
        r.final_feedback = feedback
        r.architecture = arch
        r.security_findings = sec
        return r
