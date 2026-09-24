import Page from "./_Page";

export default function Workspace() {
  return <Page kicker="Workspace" title="Set up a research session" lede="Keep the inputs and conventions for a piece of analysis together."><div className="grid grid-2"><div className="card"><h2>Data source</h2><label className="field">Provider<select defaultValue="Local CSV"><option>Local CSV</option><option>Yahoo Finance</option></select></label><p className="sub" style={{ marginTop: 10 }}>Local fixtures are useful for repeatable research and validation.</p></div><div className="card"><h2>Session notes</h2><label className="field">Notes<textarea rows={4} placeholder="Record the research question and assumptions." /></label></div></div></Page>;
}