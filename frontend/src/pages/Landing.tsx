import { Link } from "react-router-dom";

export default function Landing() {
  return (
    <div className="page">
      <p className="kicker">AlgoResearch</p>
      <div className="hero">
        <h1>From Market Analysis to Strategy Evaluation.</h1>
        <p className="lede">
          An integrated research platform for systematic market analysis, technical
          screening, and backtest analytics.
        </p>
      </div>

      <div className="callout" style={{ margin: "28px 0" }}>
        <strong>What real problem does this solve?</strong>
        <p style={{ margin: "8px 0 0" }}>
          It reduces fragmentation and repetitive manual work in systematic trading
          research by providing a unified workflow for market analysis, technical
          screening, strategy evaluation, and risk analytics.
        </p>
      </div>

      <h2>Fragmented research workflow</h2>
      <p>
        Direction analysis, technical screening, signal validation, backtest
        interpretation, and risk review often live in separate notebooks, spreadsheets,
        and vendor tools. That makes research slower, harder to reproduce, and easy to
        mis-compare.
      </p>

      <h2>Our solution</h2>
      <div className="flow" style={{ margin: "16px 0 28px" }}>
        <span>Market analysis</span>→<span>Signal screening</span>→
        <span>Strategy evaluation</span>→<span>Risk analysis</span>→
        <span>Research report</span>
      </div>

      <div className="grid grid-3">
        <div className="card">
          <h3>Market direction</h3>
          <p>Rule-based classification of recent OHLC structure, with the reasons attached.</p>
        </div>
        <div className="card">
          <h3>NIFTY screening</h3>
          <p>EMA 20/50 golden-crossover pipeline that emits research candidates, not buy calls.</p>
        </div>
        <div className="card">
          <h3>Backtest analytics</h3>
          <p>Portfolio P&amp;L, drawdown, and comparison on documented or uploaded research data.</p>
        </div>
      </div>

      <p style={{ marginTop: 32 }}>
        Built from my experience as an Algorithmic Trading Intern at Bithub Finance
        Private Limited — then extended into a reproducible research workspace.
      </p>
      <p>
        <Link to="/app" className="btn" style={{ display: "inline-block" }}>
          Open the research workspace
        </Link>
      </p>
      <p className="footer-note">
        Historical data only. This application does not execute orders, connect to a
        broker, or provide investment advice.
      </p>
    </div>
  );
}
