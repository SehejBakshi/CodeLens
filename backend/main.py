from fastapi import FastAPI, HTTPException
from model import ReviewEngine
from db import ReviewDB
import os
from schemas import CodeInput, FinalReview
import asyncio
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor
from typing import Dict

app = FastAPI(title="CodeLens - Code Review Engine")

engine = ReviewEngine(use_gpu=True)
db = ReviewDB("reviews.db")
executor = ThreadPoolExecutor(max_workers=2)

jobs: Dict[str, FinalReview] = {}

@app.post("/review")
async def review_code(input: CodeInput):

    if not input.code and not input.filename:
        raise HTTPException(status_code=400, detail="Either code or file must be provided")
    
    code_to_review = input.code

    if not code_to_review:
        if not os.path.exists(input.filename):
            raise HTTPException(status_code=400, detail=f"File does not exist: {input.filename}")
        
        try:
            with open(input.filename, 'r', encoding='utf-8') as f:
                code_to_review = f.read()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")

    job_id = str(uuid4())
    job = FinalReview(job_id=job_id, status="pending", result=None, error=None)
    jobs[job_id] = job

    asyncio.create_task(process_review(job_id, code_to_review, input))
    return job

@app.get("/status/{job_id}", response_model=FinalReview)
async def check_status(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job id not found")
    return job

@app.get("/repo-summary")
def repo_summary(repo: str=None):
    try:
        summary = db.summarize_repo(repo or "local")
        return {"repo": repo, "summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
async def process_review(job_id: str, code: str, input: CodeInput):
    job = jobs[job_id]
    try:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            executor, engine.review, code, input.filename
        )
        db.insert_review(repo=input.repo or "local", 
                         filepath=input.filename or "<stdin>", 
                         review_text=result.final_feedback)

        job.status = "completed"
        job.result = result
        job.error = None
        
    except Exception as e:
        job.status = "failed"
        job.error = str(e)
        job.result = None