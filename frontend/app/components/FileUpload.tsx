"use client";
import React, { useState, useRef } from "react";
import { uploadFile, FinalReview } from "../../lib/api";
import JobStatusLoader from "./JobStatusLoader";
import StatusBadge from "./StatusBadge";

export default function FileUpload() {
  const [file, setFile] = useState<File | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [final, setFinal] = useState<FinalReview | null>(null);
  const [showLoader, setShowLoader] = useState(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const handleChooseFile = () => {
    fileInputRef.current?.click();
  };

  const submit = async () => {
    if (!file) return alert("Choose a file first");
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
    <div>
      <h2 className="text-lg font-semibold">Upload File / Zip</h2>

      {/* Choose File */}
      <div className="w-full mb-5 upload-file-body">
        <label className="flex flex-col items-center justify-center py-9 w-full border border-gray-300 border-dashed border-rounded rounded-2xl cursor-pointer bg-gray-50" style={{borderRadius: 15 + "px"}}>
          <div className="mb-3 flex items-center justify-center upload-file">
            <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 40 40" fill="none">
              <g id="Upload 02">
                <path id="icon" d="M16.296 25.3935L19.9997 21.6667L23.7034 25.3935M19.9997 35V21.759M10.7404 27.3611H9.855C6.253 27.3611 3.33301 24.4411 3.33301 20.8391C3.33301 17.2371 6.253 14.3171 9.855 14.3171V14.3171C10.344 14.3171 10.736 13.9195 10.7816 13.4326C11.2243 8.70174 15.1824 5 19.9997 5C25.1134 5 29.2589 9.1714 29.2589 14.3171H30.1444C33.7463 14.3171 36.6663 17.2371 36.6663 20.8391C36.6663 24.4411 33.7463 27.3611 30.1444 27.3611H29.2589" stroke="#4F46E5" strokeWidth="1.6" strokeLinecap="round" />
              </g>
            </svg>
          </div>
          <h4 className="text-center text-gray-900 text-sm font-medium leading-snug">Drop your file here or</h4>
          <div className="mt-4 flex items-center gap-3">
            <div>
              <button
                onClick={handleChooseFile}
                className="choose-btn"
              >
                {file ? "Change File" : "Choose File"}
              </button>
              <input
                ref={fileInputRef}
                type="file"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                className="hidden"
              />
            </div>
            <div style={{marginBottom: 7 + "%" }}>
              {file && (
                <span className="text-sm text-gray-500 truncate max-w-xs uploaded-file">
                  {file.name}
                </span>
              )}
            </div>
          </div>
        </label>
      </div> 

      {/* Upload Button */}
      <div className="mt-4 flex items-center gap-3">
        <button onClick={submit} className="review-btn">
          Upload & Review
        </button>
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
          <pre className="mt-2 p-3 rounded bg-gray-50 text-sm overflow-x-auto">
            {final?.result[0]?.review?.final_feedback}
          </pre>
        </div>
      )}
      {final && final.status === "failed" && (
        <div className="mt-4 text-red-600">Failed: {final.error}</div>
      )}
    </div>
  );
}
