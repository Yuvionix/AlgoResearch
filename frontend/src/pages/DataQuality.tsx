import { useState } from "react";
import { validateCsv } from "../api/client";
import Page from "./_Page";

export default function DataQuality() {
  const [file, setFile] = useState<File | null>(null); const [report, setReport] = useState<any>(null); const [error, setError] = useState("");
  async function validate() { if (!file) { setError("Choose an OHLC CSV first."); return; } setError(""); try { setReport(await validateCsv(file)); } catch (requestError: any) { setError(requestError.response?.data?.message || "Unable to validate the uploaded CSV."); } }
  return <Page kicker="Data quality" title="Validate the inputs" lede="Check OHLC files before they influence a classification, screen, or backtest."><div className="card"><div className="row"><label className="field">OHLC file<input type="file" accept=".csv" onChange={(event) => setFile(event.target.files?.[0] || null)} /></label><button className="btn" onClick={validate}>Validate file</button></div></div>{error && <div className="error" style={{ marginTop: 12 }}>{error}</div>}<div className={report?.passed ? "callout" : "warnbox"} style={{ marginTop: 16 }}><strong>{report ? `${report.passed ? "Passed" : "Review required"} · Score ${report.score}/100` : "No file selected."}</strong><p>{report ? `${report.row_count} rows from ${report.start} to ${report.end}.` : "Validation checks required columns, dates, numeric values, and OHLC relationships."}</p></div></Page>;
}