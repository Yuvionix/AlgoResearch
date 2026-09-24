import Page from "./_Page";

export default function Market() {
  return (
    <Page kicker="Market analysis" title="Describe the market first" lede="Select a symbol and period to classify recent OHLC structure.">
      <div className="card"><div className="row"><label className="field">Symbol<input defaultValue="NIFTY" /></label><label className="field">Period<select defaultValue="1 year"><option>1 month</option><option>6 months</option><option>1 year</option><option>5 years</option></select></label><button className="btn">Analyze</button></div></div>
      <div className="grid grid-2" style={{ marginTop: 16 }}><div className="card"><h3>Classification</h3><div className="metric">Awaiting data</div><p className="sub">Run an analysis to see direction and confidence.</p></div><div className="card"><h3>Evidence</h3><p>Recent OHLC observations and indicator values will appear here with their data source.</p></div></div>
    </Page>
  );
}