import sqlite3
from typing import List

class ReviewDB:
    def __init__(self, db_path="reviews.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.execute("""CREATE TABLE IF NOT EXISTS reviews (
        repo TEXT, filepath TEXT, review_text TEXT
        )""")

    def insert_review(self, repo: str, filepath: str, review_text: str):
        self.conn.execute("INSERT INTO reviews (repo, filepath, review_text) VALUES (?,?,?)",
        (repo, filepath, review_text))
        self.conn.commit()

    def summarize_repo(self, repo: str):
        cursor = self.conn.execute("SELECT review_text FROM reviews WHERE repo=?", (repo,))
        texts = [r[0] for r in cursor.fetchall()]
        # simple truncate for demo
        summary = ' '.join(texts)[:1000]
        return {"repo": repo, "short_summary": summary}