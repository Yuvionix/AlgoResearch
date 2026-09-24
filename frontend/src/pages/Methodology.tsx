import Page from "./_Page";

export default function Methodology() {
  return (
    <Page kicker="Research method" title="Evidence before interpretation" lede="Every workflow keeps its inputs, rules, and limitations visible so results can be reproduced.">
      <div className="grid grid-2">
        <section className="card"><h2>Classify</h2><p>Use recent OHLC structure and documented rules to describe market direction without pretending to predict it.</p></section>
        <section className="card"><h2>Screen</h2><p>Apply EMA crossover and universe filters consistently, then inspect candidates before any evaluation.</p></section>
        <section className="card"><h2>Evaluate</h2><p>Review portfolio P&amp;L, drawdown, and trade-level outcomes over a stated historical period.</p></section>
        <section className="card"><h2>Record</h2><p>Store timestamps, parameters, data sources, and summaries as research runs for later comparison.</p></section>
      </div>
    </Page>
  );
}