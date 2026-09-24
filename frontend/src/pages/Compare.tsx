import Page from "./_Page";

export default function Compare() {
  return <Page kicker="Compare datasets" title="Put research results side by side" lede="Compare documented runs without collapsing the assumptions behind each result."><div className="card"><div className="row"><label className="field">First run<select defaultValue="Select a run"><option>Select a run</option></select></label><label className="field">Second run<select defaultValue="Select a run"><option>Select a run</option></select></label><button className="btn">Compare</button></div></div><div className="callout" style={{ marginTop: 16 }}>Select two saved research runs to compare their metrics, periods, and data sources.</div></Page>;
}