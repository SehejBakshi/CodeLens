import os
import asyncio
import shutil
import tempfile
from uuid import uuid4
from db import ReviewDB
from typing import Dict, List
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from schemas import FileReview, ReviewRequest, FinalReview
from models.job_status import JobStatus
from prepare_files import prepare_files
from review_engines.base import BaseReviewEngine
from review_engines.python_engine import PythonReviewEngine
from core.logging_config import logger

cors_origins = [os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")]

app = FastAPI(title="CodeLens - Code Review Engine")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Engine registry
engines: Dict[str, BaseReviewEngine] = {
    "py": PythonReviewEngine(use_gpu=True),
    # "cs": CSharpReviewEngine(use_gpu=True),  # Future extension
}

db = ReviewDB("reviews.db")
executor = ThreadPoolExecutor(max_workers=4)
jobs: Dict[str, FinalReview] = {}

def get_engine(filename: str) -> BaseReviewEngine:
    """Return the correct engine based on file extension. Defaults to Python."""
    if not filename:
        return engines["py"]
    ext = os.path.splitext(filename)[1].lstrip('.').lower()
    return engines.get(ext, engines["py"])

async def process_file(file_review: FileReview, repo: str = None) -> FileReview:
    try:
        logger.info(f"Processing file: {file_review.filename}")

        """Process a single FileReview object and store result in DB."""
        loop = asyncio.get_running_loop()
        engine = get_engine(file_review.filename)

        logger.info("Analyzing code and generating feedback...")
        result = await loop.run_in_executor(executor, engine.review, file_review.code, file_review.filename)

        db.insert_review(
            repo=repo or "local",
            filepath=file_review.filename or "<stdin>",
            review_text=result.final_feedback
        )

        file_review.review = result  # attach ReviewOutput
        return file_review
    
    except Exception as e:
        logger.exception(f"Exception while processing file for filename:'{file_review.filename}'.\n {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_job(job_id: str, files: List[FileReview], repo: str = None):
    """Process multiple files for a job concurrently."""
    job = jobs[job_id]
    try:
        processed_files = []
        for file_review in files:
            processed_files.append(await process_file(file_review, repo))
        job.status = JobStatus.COMPLETED
        job.result = processed_files
        job.error = None
        logger.info(f"Completed job processing for job_id: '{job_id}'")
    except Exception as e:
        job.status = JobStatus.FAILED
        job.result = None
        job.error = str(e)
        logger.exception(f"Exception while processing job_id: '{job_id}'.\n {e}")
    finally:
        db.update_job(job)
        logger.info(f"Updating job for job_id: '{job_id}' with final status={job.status}")

async def schedule_job(files, repo: str, code: str="", filename: str=None):
    try:
        job_id = str(uuid4())
        job = FinalReview(job_id=job_id, status=JobStatus.PENDING, result=None, error=None)
        jobs[job_id] = job

        # store initial job in DB
        db.insert_job(job=job, code=code or "", filename=filename, repo=repo)
        logger.info(f"Creating new job for job_id='{job_id}'")

        asyncio.create_task(process_job(job_id, files, repo))
        return job
    
    except Exception as e:
        logger.exception(f"Error creating or scheduling job: {e}")
        raise HTTPException(status_code=500, detail="Internal job creation error")

# --- API Endpoints ---
@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/review")
async def review_code(input: ReviewRequest):
    logger.info("Starting ReviewEngine")
    files = prepare_files(input)

    if not files:
        logger.exception("Error: No valid code files found to review.")
        raise HTTPException(status_code=400, detail="No valid code files found to review")

    # schedule job for completion
    return await schedule_job(
        files=files, 
        repo=input.repo or "local",
        code=input.code or "",
        filename=input.filename
    )

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        logger.info("Starting ReviewEngine")
        tmp_dir = tempfile.mkdtemp()
        file_path = os.path.join(tmp_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        repo = "upload"

        review_request = ReviewRequest(uploaded_file_path=file_path, filename = file.filename, repo=repo)
        files = prepare_files(review_request)

        if not files:
            logger.exception("Error: No valid code files found to review (Unsupported or empty file)")
            raise HTTPException(status_code=400, detail="Unsupported or empty file")
        
        return await schedule_job(
            files=files,
            repo=repo,
            code=files[0].code or "",
            filename=file.filename
        )
    except Exception as e:
        logger.exception(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status/{job_id}", response_model=FinalReview)
async def check_status(job_id: str):
    try:
        logger.info(f"Checking status for job_id: '{job_id}'")
        
        job = jobs.get(job_id)
        if job:
            return job

        job_from_db = db.get_job(job_id)
        
        if not job_from_db:
            logger.exception("Error. job not found")
            raise HTTPException(status_code=404, detail="Job not found")

        if job_from_db.status == JobStatus.PENDING:
            # reconstruct ReviewRequest to prepare files again
            files = prepare_files(ReviewRequest(
                code=job_from_db.code,
                filename=job_from_db.filename,
                repo=job_from_db.repo
            ))

            job = await schedule_job(
                files=files,
                repo=job_from_db.repo,
                code=job_from_db.code,
                filename=job_from_db.filename
            )
            return job

        return job_from_db
    
    except Exception as e:
        logger.exception("Error while checking status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/repo-summary")
def repo_summary(repo: str = None):
    try:
        summary = db.summarize_repo(repo or "local")
        return {"repo": repo, "summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
