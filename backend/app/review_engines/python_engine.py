from app.review_engines.base import BaseReviewEngine
from app.analyzer import analyze_code
from app.security import scan_code
from app.schemas import ReviewOutput, ArchitectureMetric, SecurityFinding

class PythonReviewEngine(BaseReviewEngine):
    def __init__(self):
        super().__init__()

    def review(self, code: str, filename: str|None = None) -> ReviewOutput:
        arch = analyze_code(code, filename)
        sec = scan_code(code, filename)

        prompt = self.build_prompt(code, language="Python")
        feedback = self.run_llm(prompt)

        return ReviewOutput(
            final_feedback=feedback,
            architecture=[ArchitectureMetric(**(a.dict() if hasattr(a, "dict") else a)) for a in arch],
            security_findings=[SecurityFinding(**(s.dict() if hasattr(s, "dict") else s)) for s in sec]
        )