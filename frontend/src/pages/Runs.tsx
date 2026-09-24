import { useEffect, useState } from "react";
import { getRuns } from "../api/client";
import Page from "./_Page";

export default function Runs() {
  const [runs, setRuns] = useState<any[]>([]); const [error, setError] = useState("");
  useEffect(() => { getRuns().then((data) => setRuns(data.runs || [])).catch(() => setError("Unable to load research runs.")); }, []);
  return <Page kicker="Research runs" title="A record of your analyses" lede="Saved runs make parameters, timestamps, and data sources inspectable later.">{error && <div className="error">{error}</div>}<div className="table-wrap"><table><thead><tr><th>Run ID</th><th>Type</th><th>Timestamp</th><th>Source</th></tr></thead><tbody>{runs.length ? runs.map((run) => <tr key={run.run_id}><td>{run.run_id}</td><td>{run.analysis_type}</td><td>{new Date(run.timestamp).toLocaleString()}</td><td>{run.data_source}</td></tr>) : <tr><td colSpan={4}>No research runs recorded yet.</td></tr>}</tbody></table></div></Page>;
}