"use client";
import React, { useEffect, useState } from "react";
import { pollJobStatus, FinalReview } from "../../lib/api";

interface Props {
  jobId: string;
  onComplete?: (final: FinalReview) => void;
  onCancel?: () => void;
  intervalMs?: number;
}

export default function JobStatusLoader({ jobId, onComplete, onCancel, intervalMs = 2000 }: Props) {
  const [status, setStatus] = useState<FinalReview | null>(null);
  const [dots, setDots] = useState(0);

  useEffect(() => {
    let anim: NodeJS.Timeout;
    setDots(0);

    const startPolling = async () => {
      try {
        const final = await pollJobStatus(jobId, intervalMs, (s) => setStatus(s));
        setStatus(final);
        if (onComplete) onComplete(final);
      } catch (err) {
        setStatus({ job_id: jobId, status: "failed", error: String(err) });
        if (onComplete) onComplete({ job_id: jobId, status: "failed", error: String(err) });
      }
    };

    startPolling();
    anim = setInterval(() => setDots((d) => (d + 1) % 4), 500);
    return () => clearInterval(anim);
  }, [jobId, intervalMs, onComplete]);

  return (
    <div className="loader-overlay" role="dialog" aria-modal="true">
      <div className="loader-card">
        <div className="flex items-start gap-4">
          <div className="spinner" aria-hidden />
          <div className="flex-1">
            <h3 className="text-lg font-semibold">
              {status?.status === "completed" ? "Review completed" : status?.status === "failed" ? "Review failed" : "Analyzing code"}
            </h3>
            <p className="kicker mt-1">Job ID: <span className="font-mono text-xs">{jobId}</span></p>

            <div className="mt-3">
              {status?.status === "pending" || !status ? (
                <>
                  <p className="small">Working on your review{Array.from({length:dots}).map((_,i)=>".")}</p>
                  <p className="small mt-1">This can take a few seconds to a minute depending on model & repo size.</p>
                </>
              ) : status.status === "completed" ? (
                <>
                  <p className="small">Final feedback ready — summary below.</p>
                  <div className="mt-3 grid grid-cols-3 gap-3">
                    <div className="p-2 bg-gray-50 rounded text-sm">
                      <div className="small">Feedback</div>
                      <div className="font-medium mt-1 truncate">{(status.result[0]?.review?.final_feedback || "").slice(0,160)}</div>
                    </div>
                    <div className="p-2 bg-gray-50 rounded text-sm">
                      <div className="small">Architecture</div>
                      <div className="font-medium mt-1">{(status.result[0]?.review?.architecture || []).length} item(s)</div>
                    </div>
                    <div className="p-2 bg-gray-50 rounded text-sm">
                      <div className="small">Security</div>
                      <div className="font-medium mt-1">{(status.result[0]?.review?.security_findings || []).length} finding(s)</div>
                    </div>
                  </div>
                  <div className="mt-4 flex justify-end gap-2">
                    <button onClick={() => onCancel && onCancel()} className="px-3 py-1.5 rounded bg-gray-100 text-sm">Close</button>
                    <button onClick={() => onComplete && status && onComplete(status)} className="px-3 py-1.5 rounded bg-indigo-600 text-white">View review</button>
                  </div>
                </>
              ) : (
                <div>
                  <div className="text-red-600 font-semibold">Error</div>
                  <div className="small mt-1">{status?.error}</div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}