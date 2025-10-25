import sqlite3
import json
from typing import Optional
from schemas import FinalReview, Job, ReviewOutput

class ReviewDB:
    def __init__(self, db_path="reviews.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.execute("""CREATE TABLE IF NOT EXISTS reviews (
            repo TEXT,
            filepath TEXT,
            review_text TEXT
        )""")
        self.conn.execute("""CREATE TABLE IF NOT EXISTS jobs (
            job_id TEXT PRIMARY KEY,
            status TEXT,
            code TEXT,
            filename TEXT,
            repo TEXT,
            result TEXT,
            error TEXT
        )""")
        self.conn.commit()

    def insert_review(self, repo: str, filepath: str, review_text: str):
        self.conn.execute("INSERT INTO reviews (repo, filepath, review_text) VALUES (?,?,?)",
                          (repo, filepath, review_text))
        self.conn.commit()

    def summarize_repo(self, repo: str):
        cursor = self.conn.execute("SELECT review_text FROM reviews WHERE repo=?", (repo,))
        texts = [r[0] for r in cursor.fetchall()]
        summary = ' '.join(texts)[:1000]
        return {"repo": repo, "short_summary": summary}

    def insert_job(self, job: FinalReview, code: Optional[str], filename: Optional[str], repo: Optional[str]):
        result_str = json.dumps(job.result.dict()) if job.result else None
        self.conn.execute(
            "INSERT INTO jobs (job_id, status, code, filename, repo, result, error) VALUES (?,?,?,?,?,?,?)",
            (job.job_id, job.status, code, filename, repo, result_str, job.error)
        )
        self.conn.commit()

    def update_job(self, job: FinalReview):
        result_str = json.dumps(job.result[0].review.dict()) if job.result else None
        self.conn.execute(
            "UPDATE jobs SET status=?, result=?, error=? WHERE job_id=?",
            (job.status, result_str, job.error, job.job_id)
        )
        self.conn.commit()

    def get_job(self, job_id: str) -> Optional[FinalReview]:
        cursor = self.conn.execute(
            "SELECT job_id, status, code, filename, repo, result, error FROM jobs WHERE job_id=?",
            (job_id,)
        )
        row = cursor.fetchone()
        if not row:
            return None

        result_obj = None
        if row[5]:
            try:
                result_obj = ReviewOutput.model_validate(json.loads(row[5]))
            except:
                result_obj = None

        return Job(
            job_id=row[0],
            status=row[1],
            code=row[2],
            filename=row[3],
            repo=row[4],
            result=result_obj,
            error=row[6]
        )