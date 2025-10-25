"use client";
import React, { useState } from "react";
import Editor from "@monaco-editor/react";
import { submitRawCode } from "../..//lib/api";
import JobStatusLoader from "./JobStatusLoader";
import ReviewResult from "./ReviewResult";
import StatusBadge from "./StatusBadge";
import { Language, Languages, StarterCodes } from "../../utils/StarterCodes";

export default function CodeInput() {
  const [language, setLanguage] = useState<Language>("python");
  const [code, setCode] = useState(StarterCodes[language]);
  const [jobId, setJobId] = useState<string | null>(null);
  const [final, setFinal] = useState<any | null>(null);
  const [showLoader, setShowLoader] = useState(false);
  const [snackbar, setSnackbar] = useState<{ text: string; type: "success" | "error" | "info" } | null>(null);

  const handleLanguageChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newLang = e.target.value as Language;
    setLanguage(newLang);
    setCode(StarterCodes[newLang]); 
  };

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
        {/* Language Selection */}
        <select
          value={language}
          onChange={handleLanguageChange}
          className="block
            w-full
            px-4
            py-2
            pr-10
            border
            border-gray-600
            rounded-lg
            bg-gray-900
            text-gray-100
            focus:outline-none
            focus:ring-2
            focus:ring-blue-500
            focus:border-blue-500
            cursor-pointer
            hover:border-blue-400 
            choose-btn"
            style={{margin: 1 + "%", width: 'auto'}}
          >
            {Languages.map((lang) => (
            <option key={lang.value} value={lang.value}>
              {lang.label}
            </option>
          ))}
        </select>

        <Editor
          height="320px"
          language={language}
          value={code}
          onChange={(v) => setCode(v || "")}
          theme="vs-dark"
          options={{
            smoothScrolling: true,
            automaticLayout: true,
            suggestOnTriggerCharacters: true,
            wordBasedSuggestions: 'allDocuments',
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
        {final && <StatusBadge status={final.status} />}
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
