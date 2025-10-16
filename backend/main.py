from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from model import ReviewEngine
from db import ReviewDB
from fastapi.responses import JSONResponse
from schemas import ReviewOutput

app = FastAPI(title="CodeLens - Code Review Engine")

class CodeInput(BaseModel):
    code: str
    filename: str = None
    repo: str = None

engine = ReviewEngine(use_gpu=True)
db = ReviewDB("reviews.db")

@app.post("/review", response_model=ReviewOutput)
async def review_code(input: CodeInput):
    try:
        result = engine.review(input.code, filename=input.filename)
        db.insert_review(repo=input.repo or "local", filepath=input.filename or "<stdin>", review_text=result.final_feedback)
        return {
            "feedback": result.final_feedback,
            "architecture": [a.dict() for a in result.architecture],
            "security_findings": [s.dict() for s in result.security_findings],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/repo-summary")
def repo_summary(repo: str=None):
    try:
        summary = db.summarize_repo(repo or "local")
        return {"repo": repo, "summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))