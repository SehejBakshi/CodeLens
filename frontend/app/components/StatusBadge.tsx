import React from "react";

type Status = "pending" | "completed" | "failed";

export default function StatusBadge({ status }: { status: Status }) {
  const base = "status-badge";
  if (status === "pending") return <span className={base} style={{ background:"#fff3bf", color:"#92400e" }}>Pending</span>;
  if (status === "completed") return <span className={base} style={{ background:"#dcfce7", color:"#166534" }}>Completed</span>;
  return <span className={base} style={{ background:"#fee2e2", color:"#991b1b" }}>Failed</span>;
}
