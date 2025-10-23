// frontend/components/FileInput.tsx
"use client";
import React, { useState } from "react";
import { uploadFile, FinalReview } from "../../lib/api";
import JobStatusLoader from "./JobStatusLoader";
import StatusBadge from "./StatusBadge";

export default function FileUpload() {
  const [file, setFile] = useState<File | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [final, setFinal] = useState<FinalReview | null>(null);
  const [showLoader, setShowLoader] = useState(false);

  const submit = async () => {
    if (!file) return alert("Choose a file");
    setShowLoader(true);
    try {
      const job = await uploadFile(file);
      setJobId(job.job_id);
    } catch (err) {
      console.error(err);
      setShowLoader(false);
    }
  };

  return (
    <div className="card">
      <h2 className="text-lg font-semibold">Upload File / Zip</h2>
      <div className="mt-4">
        <input type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} className="block" />
      </div>

      <div className="mt-4 flex items-center gap-3">
        <button onClick={submit} className="review-btn">Upload & Review</button>
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
        <div className="mt-4">
          <h3 className="font-semibold">Feedback</h3>
          <pre className="mt-2 p-3 rounded bg-gray-50 text-sm overflow-x-auto">{final?.result[0]?.review?.final_feedback}</pre>
        </div>
      )}
      {final && final.status === "failed" && <div className="mt-4 text-red-600">Failed: {final.error}</div>}
    </div>
  );
}
