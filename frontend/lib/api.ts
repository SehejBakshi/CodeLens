import axios from "axios";

export const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type JobStatus = "pending" | "completed" | "failed";

export interface FinalReview {
  job_id: string;
  status: JobStatus;
  result?: any;
  error?: string;
}

/** Submit raw code */
export const submitRawCode = async (code: string, filename?: string): Promise<FinalReview> => {
  const res = await axios.post<FinalReview>(`${API_BASE}/review`, { code, filename });
  return res.data;
};

/** Submit GitHub repo url */
export const submitGitRepo = async (git_url: string, repo?: string): Promise<FinalReview> => {
  const res = await axios.post<FinalReview>(`${API_BASE}/review`, { git_url, repo });
  return res.data;
};

/** Upload single file (form-data) */
export const uploadFile = async (file: File): Promise<FinalReview> => {
  const fd = new FormData();
  fd.append("file", file);
  const res = await axios.post<FinalReview>(`${API_BASE}/upload`, fd, {
    headers: { "Content-Type": "multipart/form-data" }
  });
  return res.data;
};

/** Polling helper: calls /status/{jobId} until completed or failed */
export const pollJobStatus = async (
  jobId: string,
  intervalMs = 2000,
  onUpdate?: (status: FinalReview) => void
): Promise<FinalReview> => {
  return new Promise((resolve, reject) => {
    const tick = async () => {
      try {
        const r = await axios.get<FinalReview>(`${API_BASE}/status/${jobId}`);
        const data = r.data;
        if (onUpdate) onUpdate(data);
        if (data.status === "completed" || data.status === "failed") {
          resolve(data);
        } else {
          setTimeout(tick, intervalMs);
        }
      } catch (err) {
        reject(err);
      }
    };
    tick();
  });
};

/** Health check */
if (typeof window !== "undefined") {
  const pingBackend = async () => {
    await axios.get(`${API_BASE}/health`);
  }

  pingBackend();
  setInterval(pingBackend, 10*60*1000); // ping every 10 min
};