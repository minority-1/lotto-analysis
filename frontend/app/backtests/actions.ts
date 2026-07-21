"use server";

import { runBacktest } from "@/lib/api";
import { submittedValues, type SubmittedValues } from "@/lib/form-state";
import type { BacktestRequest, BacktestResponse } from "@/lib/types";

export type BacktestState = { result: BacktestResponse | null; error: string | null; values: SubmittedValues; submission: number };

export async function runBacktestAction(previous: BacktestState, formData: FormData): Promise<BacktestState> {
  const values = submittedValues(formData);
  const request: BacktestRequest = {
    strategy: formData.get("strategy") === "frequency" ? "frequency" : "uniform",
    target_count: integer(formData, "target_count", 20),
    combinations_per_target: integer(formData, "combinations_per_target", 5),
    base_seed: integer(formData, "base_seed", 42),
    weight_recent: integer(formData, "weight_recent", 0),
    maximum_attempts: integer(formData, "maximum_attempts", 10000),
  };
  try {
    return { result: await runBacktest(request), error: null, values, submission: previous.submission + 1 };
  } catch (error) {
    return { result: null, error: error instanceof Error ? error.message : "백테스트 요청에 실패했습니다.", values, submission: previous.submission + 1 };
  }
}

function integer(formData: FormData, name: string, fallback: number): number {
  const value = String(formData.get(name) ?? "").trim();
  return value === "" ? fallback : Number.parseInt(value, 10);
}
