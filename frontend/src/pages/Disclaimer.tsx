import Page from "./_Page";

export default function Disclaimer() {
  return (
    <Page kicker="Important context" title="Research software, not financial advice" lede="AlgoResearch is an educational and analytical workspace for historical market data.">
      <div className="warnbox"><strong>Use with care.</strong><p>Historical results are not guarantees of future performance. The application does not execute orders, connect to a broker, or recommend securities.</p></div>
      <div className="card" style={{ marginTop: 16 }}><h2>Data limitations</h2><p>Market data may contain missing values, corporate actions, stale observations, or other errors. Validate inputs and review assumptions before relying on an analysis.</p></div>
    </Page>
  );
}