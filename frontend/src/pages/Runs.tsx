import Page from "./_Page";

export default function Runs() {
  return <Page kicker="Research runs" title="A record of your analyses" lede="Saved runs make parameters, timestamps, and data sources inspectable later."><div className="table-wrap"><table><thead><tr><th>Run ID</th><th>Type</th><th>Timestamp</th><th>Source</th></tr></thead><tbody><tr><td colSpan={4}>No research runs recorded yet.</td></tr></tbody></table></div></Page>;
}