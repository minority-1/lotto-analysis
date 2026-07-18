import type { BasicAnalysis, Dashboard, LottoDraw } from "@/lib/types";

const API_BASE_URL =
  process.env.LOTTO_API_BASE_URL ?? "http://127.0.0.1:8000/api";

async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    cache: "no-store",
    headers: { Accept: "application/json" },
  });

  if (!response.ok) {
    throw new Error(`API request failed with status ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export async function getDashboardData(): Promise<{
  dashboard: Dashboard;
  draws: LottoDraw[];
  analysis: BasicAnalysis;
}> {
  const [dashboard, draws, analysis] = await Promise.all([
    apiGet<Dashboard>("/dashboard"),
    apiGet<LottoDraw[]>("/draws?recent=8"),
    apiGet<BasicAnalysis>("/analysis/basic?recent=100"),
  ]);
  return { dashboard, draws, analysis };
}
