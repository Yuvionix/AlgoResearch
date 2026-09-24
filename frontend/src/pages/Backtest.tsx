import { useState } from "react";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { analyzeTrades } from "../api/client";
import Page from "./_Page";

export default function Backtest() {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  async function run() {
    if (!file) { setError("Choose a trade CSV first."); return; }
    setLoading(true); setError("");
    try { setResult(await analyzeTrades(file, 100000)); } catch (requestError: any) { setError(requestError.response?.data?.message || "Unable to analyze the uploaded trades."); } finally { setLoading(false); }
  }
  return <Page kicker="Backtest analytics" title="Evaluate a strategy in context" lede="Upload or select historical trades, then inspect portfolio-level performance and risk."><div className="card"><div className="row"><label className="field">Trade file<input type="file" accept=".csv" onChange={(event) => setFile(event.target.files?.[0] || null)} /></label><label className="field">Initial capital<input type="number" defaultValue="100000" /></label><button className="btn" onClick={run} disabled={loading}>{loading ? "Running..." : "Run backtest"}</button></div></div>{error && <div className="error" style={{ marginTop: 12 }}>{error}</div>}<div className="grid grid-4" style={{ marginTop: 16 }}><div className="card"><h3>Net P&amp;L</h3><div className="metric">{result?.total_pnl ?? "—"}</div></div><div className="card"><h3>Max drawdown</h3><div className="metric">{result?.max_drawdown ?? "—"}</div></div><div className="card"><h3>Trades</h3><div className="metric">{result?.trade_count ?? "—"}</div></div><div className="card"><h3>Return</h3><div className="metric">{result?.return_on_capital_pct ? `${result.return_on_capital_pct.toFixed(2)}%` : "—"}</div></div></div>{result?.equity_curve && <div className="card chart-card"><h2>Equity curve</h2><div className="chart-box"><ResponsiveContainer width="100%" height="100%"><LineChart data={result.equity_curve}><XAxis dataKey="date" hide /><YAxis width={72} tickFormatter={(value) => `${Math.round(value / 1000)}k`} /><Tooltip formatter={(value) => [Number(value).toFixed(2), "Equity"]} /><Line type="monotone" dataKey="equity" stroke="var(--accent)" strokeWidth={2} dot={false} /></LineChart></ResponsiveContainer></div></div>}</Page>;
}