from review_engines.base import BaseReviewEngine
from analyzer import analyze_code
from security import scan_code
from schemas import ReviewOutput, ArchitectureMetric, SecurityFinding

DEFAULT_MODEL = "refactai/Refact-1_6B-fim"

class PythonReviewEngine(BaseReviewEngine):
    def __init__(self, model_name: str = DEFAULT_MODEL, use_gpu: bool = True):
        super().__init__(model_name=model_name, use_gpu=use_gpu)

    def review(self, code: str, filename: str = None) -> ReviewOutput:
        arch = analyze_code(code, filename)
        sec = scan_code(code, filename)

        prompt = self.build_prompt(code, language="Python")
        feedback = self.run_llm(prompt)

        return ReviewOutput(
            final_feedback=feedback,
            architecture=[ArchitectureMetric(**(a.dict() if hasattr(a, "dict") else a)) for a in arch],
            security_findings=[SecurityFinding(**(s.dict() if hasattr(s, "dict") else s)) for s in sec]
        )