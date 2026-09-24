import Page from "./_Page";

export default function DataQuality() {
  return <Page kicker="Data quality" title="Validate the inputs" lede="Check OHLC files before they influence a classification, screen, or backtest."><div className="card"><div className="row"><label className="field">OHLC file<input type="file" accept=".csv" /></label><button className="btn">Validate file</button></div></div><div className="warnbox" style={{ marginTop: 16 }}><strong>No file selected.</strong><p>Validation checks required columns, dates, numeric values, and OHLC relationships.</p></div></Page>;
}