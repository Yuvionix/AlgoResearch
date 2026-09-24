import { Link, useParams } from "react-router-dom";
import Page from "./_Page";

export default function SymbolDetail() {
  const { symbol = "Symbol" } = useParams();
  return <Page kicker="Symbol detail" title={symbol} lede="Review the price series, indicators, and screening evidence for one instrument."><div className="grid grid-2"><div className="card"><h3>Latest signal</h3><div className="metric">No analysis</div><p className="sub">Load market data from the scanner or market workflow.</p></div><div className="card"><h3>Indicators</h3><p>EMA 20: —</p><p>EMA 50: —</p><p>Data source: —</p></div></div><p style={{ marginTop: 20 }}><Link to="/app/scanner">Back to screening</Link></p></Page>;
}