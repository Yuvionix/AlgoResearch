import { useState } from "react";
import { executeWorkspace } from "../api/client";
import Page from "./_Page";

export default function Workspace() {
  const [result, setResult] = useState<any>(null); const [loading, setLoading] = useState(false); const [error, setError] = useState("");
  async function execute() { setLoading(true); setError(""); try { setResult(await executeWorkspace()); } catch (requestError: any) { setError(requestError.response?.data?.message || "Unable to execute the workspace workflow."); } finally { setLoading(false); } }
  return <Page kicker="Workspace" title="Run a complete research session" lede="Execute market context and sample backtest analytics together, then save the run for later review."><div className="grid grid-2"><div className="card"><h2>Offline demo session</h2><p>Uses the included NIFTY history and sample trade data, so the workflow is reproducible without API keys or network access.</p><button className="btn" onClick={execute} disabled={loading}>{loading ? "Running workflow..." : "Run workspace"}</button></div><div className="card"><h2>Latest result</h2><div className="metric">{result?.market?.result?.classification || "Ready"}</div><p className="sub">{result?.research_run?.run_id ? `Saved as ${result.research_run.run_id}` : "No workflow run yet."}</p><p>{result?.backtest ? `Sample P&L: ${result.backtest.total_pnl}` : "The result will include classification and backtest metrics."}</p></div></div>{error && <div className="error" style={{ marginTop: 12 }}>{error}</div>}</Page>;
}