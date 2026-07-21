"use server";

import { runBacktestExperiment } from "@/lib/api";
import { submittedValues, type SubmittedValues } from "@/lib/form-state";
import type { BacktestExperimentRequest, BacktestExperimentResponse } from "@/lib/types";

export type ExperimentState = { result: BacktestExperimentResponse | null; error: string | null; values: SubmittedValues; submission: number };

export async function runExperimentAction(previous: ExperimentState, formData: FormData): Promise<ExperimentState> {
  const values = submittedValues(formData);
  try {
    const request: BacktestExperimentRequest = {
      target_count: integer(formData, "target_count", 20),
      combination_counts: integerList(formData, "combination_counts", 1, 50, 4),
      seeds: integerList(formData, "seeds", null, null, 10),
      frequency_recent: integer(formData, "frequency_recent", 50),
      maximum_attempts: integer(formData, "maximum_attempts", 10000),
    };
    return { result: await runBacktestExperiment(request), error: null, values, submission: previous.submission + 1 };
  } catch (error) {
    return { result: null, error: error instanceof Error ? error.message : "반복 비교 요청에 실패했습니다.", values, submission: previous.submission + 1 };
  }
}

function integer(formData: FormData, name: string, fallback: number): number { const value = String(formData.get(name) ?? "").trim(); return value === "" ? fallback : Number.parseInt(value, 10); }

function integerList(formData: FormData, name: string, minimum: number | null, maximum: number | null, limit: number): number[] {
  const values = String(formData.get(name) ?? "").split(/[\s,]+/).filter(Boolean).map(Number);
  if (!values.length || values.some((value) => !Number.isInteger(value) || (minimum !== null && value < minimum) || (maximum !== null && value > maximum))) throw new Error(`${name === "seeds" ? "seed" : "조합 수"} 목록을 확인해 주세요.`);
  if (values.length > limit) throw new Error(`${name === "seeds" ? "seed" : "조합 수"}는 최대 ${limit}개까지 입력할 수 있습니다.`);
  if (new Set(values).size !== values.length) throw new Error(`${name === "seeds" ? "seed" : "조합 수"}는 중복 없이 입력해 주세요.`);
  return values;
}
