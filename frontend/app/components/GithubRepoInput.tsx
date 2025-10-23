// frontend/components/GithubRepoInput.tsx
"use client";
import React, { useState } from "react";
import { submitGitRepo, FinalReview } from "../../lib/api";
import JobStatusLoader from "./JobStatusLoader";
import StatusBadge from "./StatusBadge";
import ReviewResult from "./ReviewResult";

export default function GithubRepoInput() {
  const [url, setUrl] = useState("");
  const [jobId, setJobId] = useState<string | null>(null);
  const [final, setFinal] = useState<FinalReview | null>(null);
  const [showLoader, setShowLoader] = useState(false);

  const submit = async () => {
    if (!url.trim()) return alert("Enter a GitHub repo URL");
    setShowLoader(true);
    try {
      const job = await submitGitRepo(url);
      setJobId(job.job_id);
    } catch (err) {
      console.error(err);
      setShowLoader(false);
    }
  };

  return (
    <div className="card">
      <h2 className="text-lg font-semibold">GitHub Repository</h2>
      <input value={url} onChange={(e) => setUrl(e.target.value)} placeholder="Input github repo url..." className="repo-input" />
      <div className="mt-4 flex items-center gap-3">
        <button onClick={submit} className="review-btn">Analyze Repo</button>
        {final && <StatusBadge status={final.status} />}
      </div>

      {showLoader && jobId && (
        <JobStatusLoader
          jobId={jobId}
          onComplete={(res) => {
            setFinal(res);
            setShowLoader(false);
          }}
          onCancel={() => setShowLoader(false)}
        />
      )}

      {final && final.status === "completed" && (
        <ReviewResult final={final} />
      )}

      {final && final.status === "failed" && <div className="mt-4 text-red-600">Failed: {final.error}</div>}
    </div>
  );
}
