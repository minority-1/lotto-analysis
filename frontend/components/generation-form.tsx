"use client";

import { useActionState } from "react";
import { useFormStatus } from "react-dom";

import { generateAction, type GenerationState } from "@/app/generate/actions";
import { LottoBall } from "@/components/lotto-ball";
import { restoredValue, type SubmittedValues } from "@/lib/form-state";
import type { GenerationResponse } from "@/lib/types";

const initialState: GenerationState = { result: null, error: null, values: {}, submission: 0 };

export function GenerationForm() {
  const [state, action] = useActionState(generateAction, initialState);
  return <>
    <form className="generator-form" action={action} key={state.submission}>
      <div className="generator-intro"><div><span className="eyebrow">BASIC SETTINGS</span><h2>생성 조건</h2></div><p>포함·제외 번호는 쉼표나 공백으로 구분하세요.</p></div>
      <div className="generator-grid">
        <Field label="생성 전략"><select name="strategy" defaultValue={restoredValue(state.values, "strategy", "uniform")}><option value="uniform">균등 무작위</option><option value="frequency">과거 빈도 가중</option></select></Field>
        <Field label="빈도 기준"><select name="weight_recent" defaultValue={restoredValue(state.values, "weight_recent", "0")}><option value="0">전체 회차</option><option value="50">최근 50회</option><option value="100">최근 100회</option><option value="200">최근 200회</option><option value="500">최근 500회</option></select><small>빈도 가중 전략에서만 적용</small></Field>
        <Field label="생성 개수"><input name="count" type="number" min="1" max="50" defaultValue={restoredValue(state.values, "count", "5")} required /></Field>
        <Field label="재현 seed"><input name="seed" type="number" defaultValue={restoredValue(state.values, "seed", "")} placeholder="비우면 매번 변경" /></Field>
        <Field label="반드시 포함"><input name="required_numbers" defaultValue={restoredValue(state.values, "required_numbers", "")} placeholder="예: 7, 20" /></Field>
        <Field label="제외"><input name="excluded_numbers" defaultValue={restoredValue(state.values, "excluded_numbers", "")} placeholder="예: 1, 2, 3" /></Field>
      </div>
      <details className="advanced-conditions"><summary>고급 조건 설정</summary><div className="condition-grid">
        <RangeFields title="홀수 개수" prefix="odd" minimum={0} maximum={6} values={state.values} />
        <RangeFields title="낮은 번호 개수 (1~22)" prefix="low" minimum={0} maximum={6} values={state.values} />
        <RangeFields title="번호 합계" prefix="sum" minimum={21} maximum={255} values={state.values} />
        <RangeFields title="소수 개수" prefix="prime" minimum={0} maximum={6} values={state.values} />
        <RangeFields title="AC 값" prefix="ac" minimum={0} maximum={10} values={state.values} />
        <Field label="최대 연속 번호쌍"><input name="maximum_consecutive_pairs" type="number" min="0" max="5" defaultValue={restoredValue(state.values, "maximum_consecutive_pairs", "5")} /></Field>
        <Field label="과거 조합 최대 중복"><input name="maximum_historical_overlap" type="number" min="0" max="6" defaultValue={restoredValue(state.values, "maximum_historical_overlap", "4")} /></Field>
        <Field label="생성 결과끼리 최대 중복"><input name="maximum_result_overlap" type="number" min="0" max="6" defaultValue={restoredValue(state.values, "maximum_result_overlap", "4")} /></Field>
        <Field label="최대 시도 횟수"><input name="maximum_attempts" type="number" min="1" max="100000" defaultValue={restoredValue(state.values, "maximum_attempts", "10000")} /></Field>
        <label className="checkbox-field"><input name="exclude_exact_historical" type="checkbox" defaultChecked={state.submission === 0 || state.values.exclude_exact_historical === "on"} /><span>과거 당첨 조합과 완전히 같은 결과 제외</span></label>
      </div></details>
      <p className="generator-warning">조건이 서로 충돌하거나 지나치게 좁으면 요청 개수보다 적게 생성될 수 있습니다.</p>
      <SubmitButton />
    </form>
    {state.error && <div className="generation-error"><strong>생성 조건을 확인해 주세요.</strong><p>{state.error}</p></div>}
    {state.result && <GenerationResult result={state.result} />}
  </>;
}

function Field({ label, children }: { label: string; children: React.ReactNode }) { return <label className="generator-field"><span>{label}</span>{children}</label>; }

function RangeFields({ title, prefix, minimum, maximum, values }: { title: string; prefix: string; minimum: number; maximum: number; values: SubmittedValues }) {
  return <fieldset><legend>{title}</legend><label><span>최소</span><input name={`${prefix}_minimum`} type="number" min={minimum} max={maximum} defaultValue={restoredValue(values, `${prefix}_minimum`, String(minimum))} /></label><label><span>최대</span><input name={`${prefix}_maximum`} type="number" min={minimum} max={maximum} defaultValue={restoredValue(values, `${prefix}_maximum`, String(maximum))} /></label></fieldset>;
}

function SubmitButton() { const { pending } = useFormStatus(); return <button className="generate-button" type="submit" disabled={pending}>{pending ? "조건을 확인하고 생성 중…" : "후보 조합 생성"}</button>; }

function GenerationResult({ result }: { result: GenerationResponse }) {
  return <section className="generation-result">
    <div className="generator-intro"><div><span className="eyebrow">GENERATED CANDIDATES</span><h2>생성 결과</h2></div><p>{result.complete ? `${result.combinations.length}개 생성 완료` : `${result.requested_count}개 중 ${result.combinations.length}개 생성`}</p></div>
    <div className="generation-meta"><span>전략 <strong>{strategyName(result.strategy)}</strong></span><span>시도 <strong>{result.attempts.toLocaleString()}회</strong></span><span>seed <strong>{result.seed ?? "자동"}</strong></span>{result.strategy_details.map(([key, value]) => <span key={key}>{detailName(key)} <strong>{value}</strong></span>)}</div>
    {!result.complete && <p className="partial-message">{result.message ?? "조건을 완화한 뒤 다시 실행해 주세요."}</p>}
    <div className="generated-list">{result.combinations.map((combination, index) => <article key={`${combination.numbers.join("-")}-${index}`}><span className="candidate-index">#{String(index + 1).padStart(2, "0")}</span><div className="draw-numbers">{combination.numbers.map((number) => <LottoBall key={number} number={number} />)}</div><dl><div><dt>합계</dt><dd>{combination.number_sum}</dd></div><div><dt>홀짝</dt><dd>{combination.odd_count}:{combination.even_count}</dd></div><div><dt>저고</dt><dd>{combination.low_count}:{combination.high_count}</dd></div><div><dt>소수</dt><dd>{combination.prime_count}</dd></div><div><dt>AC</dt><dd>{combination.ac_value}</dd></div><div><dt>과거 최대 중복</dt><dd>{combination.maximum_historical_overlap}</dd></div></dl></article>)}</div>
    {result.rejection_counts.length > 0 && <details className="rejection-details"><summary>조건별 제외 횟수</summary><div>{result.rejection_counts.map(([reason, count]) => <span key={reason}>{reason} <strong>{count.toLocaleString()}</strong></span>)}</div></details>}
    <p className="analysis-disclaimer">이 결과는 입력 조건을 만족하는 무작위 후보입니다. 추천 순위, 예측 결과 또는 실제 당첨 확률의 향상을 의미하지 않습니다.</p>
  </section>;
}

function strategyName(strategy: string) { return strategy === "uniform" || strategy === "uniform_random" ? "균등 무작위" : strategy === "frequency_weighted" ? "과거 빈도 가중" : strategy; }
function detailName(key: string) { return key === "source_draws" ? "빈도 원본 회차" : key === "smoothing" ? "평활값" : key === "cap_multiplier" ? "가중치 상한" : key; }
