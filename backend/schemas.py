from pydantic import BaseModel, model_validator
from typing import List, Optional

class CodeInput(BaseModel):
    code: Optional[str] = None
    filename: Optional[str] = None
    repo: Optional[str] = None

    @model_validator(mode="before")
    def code_or_file_must_exist(cls, values):
        code = values.get("code")
        filename = values.get("filename")

        if not code and not filename:
            raise ValueError("Either code or filename must be provided")
        return values

class ArchitectureMetric(BaseModel):
    name: str
    dot_diagram: str

class SecurityFinding(BaseModel):
    issue: str
    line: int
    severity: str

class ReviewOutput(BaseModel):
    final_feedback: str
    architecture: List[ArchitectureMetric]
    security_findings: List[SecurityFinding]

class FinalReview(BaseModel):
    job_id: str
    status: str # "pending", "completed", "failed"
    result: Optional[ReviewOutput] = None
    error: Optional[str] = None

class Job(BaseModel):
    job_id: str
    status: str
    code: Optional[str] = None
    filename: Optional[str] = None
    repo: Optional[str] = None
    result: Optional[ReviewOutput] = None
    error: Optional[str] = None