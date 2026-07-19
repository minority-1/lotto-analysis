import type { BasicAnalysis, Dashboard, DrawPage, LottoDraw } from "@/lib/types";

const API_BASE_URL =
  process.env.LOTTO_API_BASE_URL ?? "http://127.0.0.1:8000/api";

async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    cache: "no-store",
    headers: { Accept: "application/json" },
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null) as { detail?: string } | null;
    throw new Error(body?.detail ?? `API request failed with status ${response.status}`);
  }
  return response.json() as Promise<T>;
}

type BasicAnalysisQuery = {
  mode?: string;
  recent?: string;
  start_draw?: string;
  end_draw?: string;
  start_date?: string;
  end_date?: string;
};

export async function getBasicAnalysis(query: BasicAnalysisQuery): Promise<{
  data: BasicAnalysis | null;
  error: string | null;
}> {
  const mode = query.mode ?? "recent";
  let path: string;
  if (mode === "draw") {
    const parameters = new URLSearchParams({
      start_draw: query.start_draw ?? "",
      end_draw: query.end_draw ?? "",
    });
    path = `/analysis/basic/range?${parameters}`;
  } else if (mode === "date") {
    const parameters = new URLSearchParams({
      start_date: query.start_date ?? "",
      end_date: query.end_date ?? "",
    });
    path = `/analysis/basic/range?${parameters}`;
  } else {
    const recent = query.recent ?? "100";
    path = `/analysis/basic?recent=${encodeURIComponent(recent)}`;
  }

  try {
    return { data: await apiGet<BasicAnalysis>(path), error: null };
  } catch (error) {
    return {
      data: null,
      error: error instanceof Error ? error.message : null,
    };
  }
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

export async function getDrawPage(page: number, pageSize: number): Promise<{
  draws: LottoDraw[];
  page: number;
  total: number;
  totalPages: number;
} | null> {
  try {
    const dashboard = await apiGet<Dashboard>("/dashboard");
    const totalPages = Math.max(1, Math.ceil(dashboard.total_draws / pageSize));
    const normalizedPage = Math.min(page, totalPages);
    if (dashboard.total_draws === 0) {
      return { draws: [], page: 1, total: 0, totalPages: 1 };
    }
    const remaining = dashboard.total_draws - (normalizedPage - 1) * pageSize;
    const limit = Math.min(pageSize, remaining);
    const offset = Math.max(dashboard.total_draws - normalizedPage * pageSize, 0);
    const response = await apiGet<DrawPage>(`/draws/page?limit=${limit}&offset=${offset}`);
    return {
      draws: [...response.items].reverse(),
      page: normalizedPage,
      total: response.total,
      totalPages,
    };
  } catch {
    return null;
  }
}

export async function getDrawDetail(drawNumber: number): Promise<{
  draw: LottoDraw;
  latestDrawNumber: number;
} | null> {
  try {
    const [draw, latest] = await Promise.all([
      apiGet<LottoDraw>(`/draws/${drawNumber}`),
      apiGet<LottoDraw>("/draws/latest"),
    ]);
    return { draw, latestDrawNumber: latest.draw_number };
  } catch {
    return null;
  }
}
