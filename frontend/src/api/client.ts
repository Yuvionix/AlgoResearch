import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:5001/api",
  timeout: 120000,
});

export async function getDashboard() {
  return (await api.get("/dashboard")).data;
}

export async function classifyMarket(payload: {
  instrument: string;
  source: string;
  period: string;
  lookback: number;
}) {
  return (await api.post("/market/classify", payload)).data;
}

export async function runScanner(payload: { source: string; lookback_days: number }) {
  return (await api.post("/scanner/run", payload)).data;
}

export async function analyzeTrades(file: File, initialCapital: number) {
  const form = new FormData();
  form.append("file", file);
  form.append("initial_capital", String(initialCapital));
  return (await api.post("/backtest/analyze-csv", form)).data;
}

export async function validateCsv(file: File) {
  const form = new FormData();
  form.append("file", file);
  return (await api.post("/data-quality/validate-csv", form)).data;
}

export async function getRuns() {
  return (await api.get("/research-runs")).data;
}

export async function getAuthState() {
  return (await api.get("/auth/me")).data;
}

export async function login(username: string, password: string) {
  return (await api.post("/auth/login", { username, password })).data;
}

export async function compareRuns(datasets: string[]) {
  return (await api.post("/backtest/compare", { datasets })).data;
}

export async function getSymbolDetail(symbol: string) {
  return (await api.get(`/scanner/symbol/${encodeURIComponent(symbol)}`, { params: { source: "local" } })).data;
}

export async function executeWorkspace() {
  return (await api.post("/workspace/execute", {
    instrument: "NIFTY",
    source: "local",
    lookback: 5,
    include_scan: false,
    include_backtest: true,
    backtest_dataset: "sample",
  })).data;
}

export type ResearchRun = {
  run_id: string;
  timestamp: string;
  instrument?: string | null;
  universe?: string | null;
  analysis_type: string;
  parameters: Record<string, unknown>;
  data_period: Record<string, unknown>;
  data_source: string;
  result_summary: Record<string, unknown>;
  details?: Record<string, unknown>;
};
