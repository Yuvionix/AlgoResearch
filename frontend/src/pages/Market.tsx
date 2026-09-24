import { useState } from "react";
import { classifyMarket } from "../api/client";
import Page from "./_Page";

export default function Market() {
  const [symbol, setSymbol] = useState("NIFTY");
  const [period, setPeriod] = useState("1y");
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function analyze() {
    setLoading(true);
    setError("");
    try {
      setResult(await classifyMarket({ instrument: symbol, source: "local", period, lookback: 5 }));
    } catch (requestError: any) {
      setError(requestError.response?.data?.message || "Unable to complete market classification.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Page kicker="Market analysis" title="Describe the market first" lede="Select a symbol and period to classify recent OHLC structure.">
      <div className="card"><div className="row"><label className="field">Symbol<input value={symbol} onChange={(event) => setSymbol(event.target.value.toUpperCase())} /></label><label className="field">Period<select value={period} onChange={(event) => setPeriod(event.target.value)}><option value="1mo">1 month</option><option value="6mo">6 months</option><option value="1y">1 year</option><option value="5y">5 years</option></select></label><button className="btn" onClick={analyze} disabled={loading}>{loading ? "Analyzing..." : "Analyze"}</button></div></div>
      {error && <div className="error" style={{ marginTop: 12 }}>{error}</div>}
      <div className="grid grid-2" style={{ marginTop: 16 }}><div className="card"><h3>Classification</h3><div className="metric">{result?.result?.classification || "Awaiting data"}</div><p className="sub">{result?.result?.confidence ? `Confidence: ${result.result.confidence}` : "Run an analysis to see direction and confidence."}</p></div><div className="card"><h3>Evidence</h3><p>{result?.result?.why?.join(" ") || "Recent OHLC observations and indicator evidence will appear here."}</p><p className="sub">Source: {result?.result?.data_source || "local historical fixtures"}</p></div></div>
    </Page>
  );
}