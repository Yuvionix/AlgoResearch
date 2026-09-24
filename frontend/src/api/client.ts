import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:5001/api",
  timeout: 120000,
});

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
