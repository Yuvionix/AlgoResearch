import { Link } from "react-router-dom";
import Page from "./_Page";

export default function Scanner() {
  return (
    <Page kicker="Stock screening" title="Find technical candidates" lede="Screen the configured universe for EMA 20/50 crossover structures.">
      <div className="card"><div className="row"><label className="field">Universe<select defaultValue="NIFTY 50"><option>NIFTY 50</option><option>Custom upload</option></select></label><label className="field">As of date<input type="date" /></label><button className="btn">Run screen</button></div></div>
      <div className="table-wrap" style={{ marginTop: 16 }}><table><thead><tr><th>Symbol</th><th>Signal</th><th>Price</th><th>Observed</th></tr></thead><tbody><tr><td><Link to="/app/scanner/INFY">INFY</Link></td><td><span className="badge bull">Candidate</span></td><td>—</td><td>Run a screen to populate</td></tr></tbody></table></div>
    </Page>
  );
}