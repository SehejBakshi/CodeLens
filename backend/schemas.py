from pydantic import BaseModel
from typing import List

class CodeInput(BaseModel):
    code: str
    filename: str = None
    repo: str = None

class ArchitectureMetric(BaseModel):
    name: str
    dot_diagram: str

class SecurityFinding(BaseModel):
    issue: str
    #line: int
    severity: str

class ReviewOutput(BaseModel):
    final_feedback: str
    architecture: List[ArchitectureMetric]
    security_findings: List[SecurityFinding]