import { FinalReview } from "../../lib/api";
import ArchitectureDiagram from "./ArchitectureDiagram";

interface Props {
  final: FinalReview
}

export default function ReviewResult({final}: Props) {
    const severityColor = (sev: string) => {
    switch ((sev || "").toUpperCase()) {
      case "HIGH":
        return "#f87171"; // red-400
      case "MEDIUM":
        return "#fbbf24"; // yellow-400
      default:
        return "#34d399"; // green-400
    }
  };
  
    return (
        <div className="result card mt-4">
            <div>
            <h3 className="font-semibold">Feedback</h3>
            <pre style={{marginLeft: 1 + "%"}}
                className="ml-2 pl-6 break-words whitespace-pre-wrap"
            >
                {final.result[0]?.review?.final_feedback}
            </pre>
            </div>

            <div className="mt-4">
            <h3 className="font-semibold">Security Findings</h3>

            {final.result[0]?.review?.security_findings ? (
                <ol className="list-decimal list-outside m-0 pl-6 space-y-2">
                {final.result[0]?.review?.security_findings.map(
                    (item: any, index: any) => (
                    <li
                        key={index}
                        className="font-semibold text-gray-100 break-words whitespace-pre-wrap m-0"
                    >
                        {item.issue}
                        <br />
                        Line: {item.line} | Severity:{" "}
                        <span style={{ color: severityColor(item.severity) }}>
                        {item.severity}
                        </span>
                    </li>
                    )
                )}
                </ol>
            ) : (
                <p>No issues found</p>
            )}
            </div>

            <div>
            <ArchitectureDiagram architecture={final?.result[0]?.review?.architecture[0]?.dot_diagram} />
            </div>
        </div>
    )
}