from pydantic import BaseModel, Field, model_validator
from typing import List, Optional, Dict

class ReviewRequest(BaseModel):
    code: Optional[str] = Field(None, description="Raw source code string")
    filename: Optional[str] = Field(None, description="Local file path")
    uploaded_file_path: Optional[str] = Field(None, description="Path to uploaded file or zip")
    git_url: Optional[str] = Field(None, description="GitHub repository URL")
    repo: Optional[str] = Field(None, description="Logical repo identifier for context")

    @model_validator(mode="before")
    def at_least_one_source(cls, values):
        if not any([values.get("code"), values.get("filename"), values.get("uploaded_file_path"), values.get("git_url")]):
            raise ValueError("Provide at least one code source: raw code, file, uploaded file, or GitHub URL")
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

class FileReview(BaseModel):
    filename: Optional[str] = Field(None, description="Name/path of the file")
    code: str = Field(..., description="Source code of the file")
    review: Optional[ReviewOutput] = Field(None, description="Review output for the file")

class FinalReview(BaseModel):
    job_id: str
    status: str  # "pending", "completed", "failed"
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