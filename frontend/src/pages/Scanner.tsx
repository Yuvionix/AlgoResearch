import { Link } from "react-router-dom";
import { useState } from "react";
import { runScanner } from "../api/client";
import Page from "./_Page";

export default function Scanner() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function scan() {
    setLoading(true);
    setError("");
    try {
      setData(await runScanner({ source: "local", lookback_days: 15 }));
    } catch (requestError: any) {
      setError(requestError.response?.data?.message || "Unable to complete the scan.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Page kicker="Stock screening" title="Find technical candidates" lede="Screen the configured universe for EMA 20/50 crossover structures.">
      <div className="card"><div className="row"><label className="field">Universe<select defaultValue="NIFTY 50"><option>NIFTY 50</option></select></label><label className="field">Lookback days<input type="number" defaultValue="15" min="1" max="365" /></label><button className="btn" onClick={scan} disabled={loading}>{loading ? "Scanning..." : "Run screen"}</button></div></div>
      {error && <div className="error" style={{ marginTop: 12 }}>{error}</div>}
      <div className="table-wrap" style={{ marginTop: 16 }}><table><thead><tr><th>Symbol</th><th>Signal</th><th>Price</th><th>Quality</th></tr></thead><tbody>{data?.candidates?.length ? data.candidates.map((candidate: any) => <tr key={candidate.symbol}><td><Link to={`/app/scanner/${candidate.symbol}`}>{candidate.symbol}</Link></td><td><span className={`badge ${candidate.research_status?.label === "Passed Screening Criteria" ? "bull" : "side"}`}>{candidate.research_status?.label}</span></td><td>{candidate.price?.toFixed?.(2) || "—"}</td><td>{candidate.data_quality_score}/100</td></tr>) : <tr><td colSpan={4}>{data ? "No candidates returned." : "Run a screen to populate results."}</td></tr>}</tbody></table></div>
    </Page>
  );
}