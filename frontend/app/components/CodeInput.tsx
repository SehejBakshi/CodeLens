"use client";
import React, { useState } from "react";
import Editor from "@monaco-editor/react";
import { submitRawCode } from "../..//lib/api";
import JobStatusLoader from "./JobStatusLoader";
import ReviewResult from "./ReviewResult";

export default function CodeInput() {
  const [code, setCode] = useState<string>("def add(a,b):\n  return a+b\n");
  const [jobId, setJobId] = useState<string | null>(null);
  const [final, setFinal] = useState<any | null>(null);
  const [showLoader, setShowLoader] = useState(false);
  const [snackbar, setSnackbar] = useState<{ text: string; type: "success" | "error" | "info" } | null>(null);

  const submit = async () => {
    setShowLoader(true);
    try {
      const res = await submitRawCode(code, "snippet.py");
      setJobId(res.job_id || null);
      setSnackbar({ text: "Submitted for review...", type: "info" });
      setTimeout(() => setSnackbar(null), 3000);
    } catch (err) {
      console.error(err);
      setShowLoader(false);
      setSnackbar({ text: "Failed to submit code", type: "error" });
      setTimeout(() => setSnackbar(null), 3000);
    }
  };

  return (
    <div>
      <div className="editor-container">
        <Editor
          height="320px"
          defaultLanguage="python"
          value={code}
          onChange={(v) => setCode(v || "")}
          theme="vs-dark"
          options={{
            smoothScrolling: true
          }}
        />
      </div>

      <div className="mt-6 flex items-center gap-3 review-button">
        <button
          onClick={submit}
          className="review-btn"
        >
          Review Code
        </button>
      </div>

      {showLoader && jobId && (
        <JobStatusLoader
          jobId={jobId}
          onComplete={(res) => {
            setFinal(res);
            setShowLoader(false);
            setSnackbar({
              text: res.status === "completed" ? "Review completed!" : "Review failed.",
              type: res.status === "completed" ? "success" : "error",
            });
            setTimeout(() => setSnackbar(null), 4000);
          }}
          onCancel={() => setShowLoader(false)}
        />
      )}

      {final?.status === "completed" && (
        <ReviewResult final={final}/>
      )}

      {/* Snackbar */}
      {snackbar && (
        <div className={`snackbar snackbar-${snackbar.type}`}>
          {snackbar.text}
        </div>
      )}
    </div>
  );
}
