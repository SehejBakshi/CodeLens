import React from "react";

type Status = "pending" | "completed" | "failed";

export default function StatusBadge({ status }: { status: Status }) {
  const base = "status-badge";
  if (status === "completed") 
    return <span className={base} style={{ background:"#dcfce7", color:"#166534", marginLeft: 1 + "%" }}>Review Completed!</span>;
  return <span className={base} style={{ background:"#fee2e2", color:"#991b1b", marginLeft: 1 + "%" }}>Review Failed! Please try again!</span>;
}
