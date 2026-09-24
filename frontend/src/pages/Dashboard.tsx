import { Link } from "react-router-dom";
import { useEffect, useState } from "react";
import { getDashboard } from "../api/client";
import Page from "./_Page";

export default function Dashboard() {
  const [summary, setSummary] = useState<any>(null);
  useEffect(() => { getDashboard().then(setSummary).catch(() => undefined); }, []);
  return (
    <Page kicker="Workspace overview" title="Research dashboard" lede="A starting point for moving from market context to a documented result.">
      <div className="grid grid-4">
        <div className="card"><h3>Market state</h3><div className="metric">Ready</div><p className="sub">Choose an instrument to classify.</p></div>
        <div className="card"><h3>Screening universe</h3><div className="metric">NIFTY</div><p className="sub">EMA crossover candidates.</p></div>
        <div className="card"><h3>Backtest status</h3><div className="metric">Idle</div><p className="sub">No run currently active.</p></div>
        <div className="card"><h3>Research runs</h3><div className="metric">{summary?.research_run_count ?? 0}</div><p className="sub">Saved in this session.</p></div>
      </div>
      <div className="callout" style={{ marginTop: 20 }}><strong>Suggested next step</strong><p><Link to="/app/market">Start with market analysis</Link> to establish context before screening or backtesting.</p></div>
    </Page>
  );
}