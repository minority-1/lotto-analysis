"use server";

import { generateCombinations } from "@/lib/api";
import { submittedValues, type SubmittedValues } from "@/lib/form-state";
import type { GenerationRequest, GenerationResponse } from "@/lib/types";

export type GenerationState = { result: GenerationResponse | null; error: string | null; values: SubmittedValues; submission: number };

export async function generateAction(previous: GenerationState, formData: FormData): Promise<GenerationState> {
  const values = submittedValues(formData);
  try {
    const request: GenerationRequest = {
      strategy: formData.get("strategy") === "frequency" ? "frequency" : "uniform",
      weight_recent: integer(formData, "weight_recent", 0),
      count: integer(formData, "count", 5),
      required_numbers: numberList(formData, "required_numbers"),
      excluded_numbers: numberList(formData, "excluded_numbers"),
      odd_minimum: integer(formData, "odd_minimum", 0),
      odd_maximum: integer(formData, "odd_maximum", 6),
      low_minimum: integer(formData, "low_minimum", 0),
      low_maximum: integer(formData, "low_maximum", 6),
      sum_minimum: integer(formData, "sum_minimum", 21),
      sum_maximum: integer(formData, "sum_maximum", 255),
      prime_minimum: integer(formData, "prime_minimum", 0),
      prime_maximum: integer(formData, "prime_maximum", 6),
      ac_minimum: integer(formData, "ac_minimum", 0),
      ac_maximum: integer(formData, "ac_maximum", 10),
      maximum_consecutive_pairs: integer(formData, "maximum_consecutive_pairs", 5),
      exclude_exact_historical: formData.get("exclude_exact_historical") === "on",
      maximum_historical_overlap: integer(formData, "maximum_historical_overlap", 4),
      maximum_result_overlap: integer(formData, "maximum_result_overlap", 4),
      maximum_attempts: integer(formData, "maximum_attempts", 10000),
      seed: optionalInteger(formData, "seed"),
    };
    return { result: await generateCombinations(request), error: null, values, submission: previous.submission + 1 };
  } catch (error) {
    return { result: null, error: error instanceof Error ? error.message : "번호 생성 요청에 실패했습니다.", values, submission: previous.submission + 1 };
  }
}

function integer(formData: FormData, name: string, fallback: number): number {
  const value = String(formData.get(name) ?? "").trim();
  return value === "" ? fallback : Number.parseInt(value, 10);
}

function optionalInteger(formData: FormData, name: string): number | null {
  const value = String(formData.get(name) ?? "").trim();
  return value === "" ? null : Number.parseInt(value, 10);
}

function numberList(formData: FormData, name: string): number[] {
  const value = String(formData.get(name) ?? "").trim();
  if (!value) return [];
  const numbers = value.split(/[\s,]+/).filter(Boolean).map(Number);
  if (numbers.some((number) => !Number.isInteger(number) || number < 1 || number > 45)) throw new Error(`${name === "required_numbers" ? "포함" : "제외"} 번호는 1~45의 정수로 입력해 주세요.`);
  return [...new Set(numbers)].sort((a, b) => a - b);
}
