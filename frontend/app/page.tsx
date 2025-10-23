"use client";
import React, { useState } from "react";
import CodeInput from "./components/CodeInput";
import FileUpload from "./components/FileUpload";
import GithubRepoInput from "./components/GithubRepoInput";

const TABS = [
  { id: "code", label: "Code Editor" },
  { id: "file", label: "Upload File / Zip" },
  { id: "repo", label: "GitHub Repo" },
];

export default function HomePage() {
  const [tab, setTab] = useState<string>("code");

  return (
    <main className="min-h-screen p-8">
      <div className="max-w-6xl mx-auto">
        <header className="app-header mb-6">
          <h1 className="title">CodeLens — AI Code Review</h1>
          <h4 className="by-line">Smart reviews. Cleaner code. Faster ship.</h4>
          <p className="kicker mt-1">
            Paste, upload, or connect a repo — get AI insights.
          </p>
        </header>

        <div className="card">
          {/* Centered Tabs */}
          <div className="flex justify-center mb-6">
            <nav className="tabs">
              {TABS.map((t) => (
                <button
                  key={t.id}
                  onClick={() => setTab(t.id)}
                  className={`tab-btn ${tab === t.id ? "tab-active" : ""}`}
                >
                  {t.label}
                </button>
              ))}
            </nav>
          </div>

          <div className="px-4 pb-4">
            {tab === "code" && <CodeInput />}
            {tab === "file" && <FileUpload />}
            {tab === "repo" && <GithubRepoInput />}
          </div>
        </div>
      </div>
    </main>
  );
}
