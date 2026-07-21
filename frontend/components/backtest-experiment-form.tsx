"use client";

import { useActionState } from "react";
import { useFormStatus } from "react-dom";

import { runExperimentAction, type ExperimentState } from "@/app/backtests/experiment/actions";
import { restoredValue } from "@/lib/form-state";
import type { BacktestExperimentResponse, BacktestExperimentSummary } from "@/lib/types";

const initialState: ExperimentState = { result: null, error: null, values: {}, submission: 0 };

export function BacktestExperimentForm() {
  const [state, action] = useActionState(runExperimentAction, initialState);
  return <>
    <form className="backtest-form" action={action} key={state.submission}>
      <div className="generator-intro"><div><span className="eyebrow">EXPERIMENT GRID</span><h2>비교 조건</h2></div><p>균등 · 전체 빈도 · 최근 빈도 전략을 모두 실행합니다.</p></div>
      <div className="experiment-form-grid">
        <label><span>목표 회차 수</span><input name="target_count" type="number" min="1" max="100" defaultValue={restoredValue(state.values, "target_count", "20")} required /></label>
        <label><span>회차당 조합 수 목록</span><input name="combination_counts" defaultValue={restoredValue(state.values, "combination_counts", "1, 5, 10")} required /><small>1~50, 중복 없이 최대 4개</small></label>
        <label><span>seed 목록</span><input name="seeds" defaultValue={restoredValue(state.values, "seeds", "41, 42, 43")} required /><small>중복 없이 최대 10개</small></label>
        <label><span>최근 빈도 학습 범위</span><select name="frequency_recent" defaultValue={restoredValue(state.values, "frequency_recent", "50")}><option value="20">최근 20회</option><option value="50">최근 50회</option><option value="100">최근 100회</option><option value="200">최근 200회</option></select></label>
        <label><span>회차당 최대 시도</span><input name="maximum_attempts" type="number" min="1" max="10000" defaultValue={restoredValue(state.values, "maximum_attempts", "10000")} required /></label>
      </div>
      <p className="generator-warning">예상 조합 작업량은 목표 수 × 조합 수 합계 × seed 수 × 3개 전략이며 최대 100,000입니다.</p>
      <ExperimentButton />
    </form>
    {state.error && <div className="generation-error"><strong>반복 비교 조건을 확인해 주세요.</strong><p>{state.error}</p></div>}
    {state.result && <ExperimentResult result={state.result} />}
  </>;
}

function ExperimentButton() { const { pending } = useFormStatus(); return <button className="generate-button" type="submit" disabled={pending}>{pending ? "동일 조건으로 세 전략을 반복 실행 중…" : "반복 전략 비교 실행"}</button>; }

function ExperimentResult({ result }: { result: BacktestExperimentResponse }) {
  const totalRuns = result.summaries.reduce((sum, item) => sum + item.run_count, 0);
  const completeRuns = result.summaries.reduce((sum, item) => sum + item.complete_runs, 0);
  const totalGenerated = result.summaries.reduce((sum, item) => sum + item.total_generated_combinations, 0);
  return <section className="backtest-result experiment-result">
    <div className="generator-intro"><div><span className="eyebrow">EXPERIMENT RESULT</span><h2>전략 비교 결과</h2></div><p>{completeRuns}/{totalRuns}개 실행 완료</p></div>
    <div className="analysis-summary experiment-summary"><article><span>목표 회차</span><strong>{result.target_count}회</strong><small>각 실행 공통</small></article><article><span>seed</span><strong>{result.seeds.length}개</strong><small>{result.seeds.join(", ")}</small></article><article><span>전체 생성 조합</span><strong>{totalGenerated.toLocaleString()}개</strong><small>모든 전략·실행 합계</small></article><article className="accent"><span>최근 빈도 범위</span><strong>{result.frequency_recent}회</strong><small>최근 빈도 전략에만 적용</small></article></div>
    {result.combination_counts.map((count) => <ComparisonGroup key={count} count={count} summaries={result.summaries.filter((item) => item.combinations_per_target === count)} />)}
    <p className="analysis-disclaimer">전략 비교는 같은 조합 수 행끼리만 해석해야 합니다. 조합을 더 많이 생성하면 목표별 최고 일치 수가 구조적으로 커질 수 있으며, 과거 평균은 미래 성과나 당첨 확률을 의미하지 않습니다.</p>
  </section>;
}

function ComparisonGroup({ count, summaries }: { count: number; summaries: BacktestExperimentSummary[] }) {
  const maximumBest = Math.max(...summaries.map((item) => item.average_best_match), 0.01);
  return <section className="experiment-group"><div className="section-heading compact"><div><span>SAME COMBINATION COUNT</span><h2>회차당 {count}조합 비교</h2></div><p>같은 목표·seed 조건</p></div>
    <div className="experiment-table"><div className="experiment-table-head"><span>전략</span><span>평균 일치</span><span>평균 최고</span><span>완료</span><span>생성 조합</span></div>{summaries.map((item) => <article key={item.strategy_label}><div><strong>{strategyName(item.strategy_label)}</strong><small>{item.weight_recent ? `목표 이전 최근 ${item.weight_recent}회` : item.strategy_label === "uniform" ? "동일 확률" : "목표 이전 전체"}</small></div><span>{item.average_main_match.toFixed(3)}</span><div className="best-average"><i><b style={{ width: `${item.average_best_match / maximumBest * 100}%` }} /></i><strong>{item.average_best_match.toFixed(3)}</strong></div><span>{item.complete_runs}/{item.run_count}</span><span>{item.total_generated_combinations.toLocaleString()}</span><details><summary>분포 보기</summary><div className="experiment-distributions"><MiniDistribution title="전체 조합" values={item.main_match_distribution} /><MiniDistribution title="목표별 최고" values={item.best_match_distribution} /></div></details></article>)}</div>
  </section>;
}

function MiniDistribution({ title, values }: { title: string; values: number[] }) { return <div><strong>{title}</strong><p>{values.map((count, matches) => `${matches}개 ${count}`).join(" · ")}</p></div>; }
function strategyName(label: string) { return label === "uniform" ? "균등 무작위" : label === "frequency_all" ? "전체 빈도 가중" : label.startsWith("frequency_recent_") ? `최근 ${label.split("_").at(-1)}회 빈도 가중` : label; }
