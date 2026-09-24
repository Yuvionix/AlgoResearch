export default function Why() {
  return (
    <div className="page">
      <p className="kicker">Why this platform?</p>
      <h1>Four concrete research problems</h1>
      <p className="lede">
        The product is designed for quantitative researchers and systematic traders,
        not as a retail trading app.
      </p>

      <div className="card" style={{ marginBottom: 16 }}>
        <h2>Problem 1 — Manual screening</h2>
        <p>Manually reviewing a large stock universe for the same technical setup is repetitive and inconsistent.</p>
        <p><strong>Solution:</strong> Automated EMA 20/50 crossover screening with structure and fundamental filters.</p>
      </div>
      <div className="card" style={{ marginBottom: 16 }}>
        <h2>Problem 2 — Fragmented research</h2>
        <p>Market analysis, screening, and strategy evaluation often occur in separate workflows.</p>
        <p><strong>Solution:</strong> A unified research workspace that can run classification, screening, and backtest review in one recorded session.</p>
      </div>
      <div className="card" style={{ marginBottom: 16 }}>
        <h2>Problem 3 — Poor reproducibility</h2>
        <p>Decisions are hard to reconstruct if parameters, timestamps, and data sources are not stored.</p>
        <p><strong>Solution:</strong> Research Runs with run IDs, parameters, data-source tracking, and exportable summaries.</p>
      </div>
      <div className="card">
        <h2>Problem 4 — Strategy evaluation without portfolio context</h2>
        <p>Evaluating strategies one at a time can hide portfolio-level P&amp;L and drawdown behaviour.</p>
        <p><strong>Solution:</strong> Portfolio-level analytics and a comparison view that presents metrics without declaring a “best” strategy.</p>
      </div>
    </div>
  );
}
