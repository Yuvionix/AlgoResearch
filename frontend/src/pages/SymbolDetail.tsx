import { Link, useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import { getSymbolDetail } from "../api/client";
import Page from "./_Page";

export default function SymbolDetail() {
  const { symbol = "Symbol" } = useParams();
  const [detail, setDetail] = useState<any>(null);
  const [error, setError] = useState("");
  useEffect(() => { getSymbolDetail(symbol).then(setDetail).catch(() => setError("Unable to load symbol analysis.")); }, [symbol]);
  return <Page kicker="Symbol detail" title={symbol} lede="Review the price series, indicators, and screening evidence for one instrument.">{error && <div className="error">{error}</div>}<div className="grid grid-2"><div className="card"><h3>Latest signal</h3><div className="metric">{detail?.recent_crossover ? "Golden crossover" : "No recent crossover"}</div><p className="sub">Quality score: {detail?.data_quality?.score ?? "—"}/100</p></div><div className="card"><h3>Indicators</h3><p>EMA 20: {detail?.ema20?.toFixed?.(2) || "—"}</p><p>EMA 50: {detail?.ema50?.toFixed?.(2) || "—"}</p><p>Data source: {detail?.data_source || "—"}</p></div></div><p style={{ marginTop: 20 }}><Link to="/app/scanner">Back to screening</Link></p></Page>;
}