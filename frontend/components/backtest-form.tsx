"use client";

import Link from "next/link";
import { useActionState } from "react";
import { useFormStatus } from "react-dom";

import { runBacktestAction, type BacktestState } from "@/app/backtests/actions";
import { LottoBall } from "@/components/lotto-ball";
import type { BacktestResponse } from "@/lib/types";

const initialState: BacktestState = { result: null, error: null };

export function BacktestForm() {
  const [state, action] = useActionState(runBacktestAction, initialState);
  return <>
    <form className="backtest-form" action={action}>
      <div className="generator-intro"><div><span className="eyebrow">RUN SETTINGS</span><h2>실행 조건</h2></div><p>기본 작업량: 20회 × 5조합 = 100조합</p></div>
      <div className="backtest-form-grid">
        <label><span>전략</span><select name="strategy" defaultValue="uniform"><option value="uniform">균등 무작위</option><option value="frequency">과거 빈도 가중</option></select></label>
        <label><span>빈도 기준</span><select name="weight_recent" defaultValue="0"><option value="0">각 목표 이전 전체</option><option value="20">각 목표 이전 최근 20회</option><option value="50">각 목표 이전 최근 50회</option><option value="100">각 목표 이전 최근 100회</option></select><small>빈도 가중 전략에서만 적용</small></label>
        <label><span>목표 회차 수</span><input name="target_count" type="number" min="1" max="100" defaultValue="20" required /></label>
        <label><span>회차당 조합 수</span><input name="combinations_per_target" type="number" min="1" max="50" defaultValue="5" required /></label>
        <label><span>기본 seed</span><input name="base_seed" type="number" defaultValue="42" required /></label>
        <label><span>회차당 최대 시도</span><input name="maximum_attempts" type="number" min="1" max="10000" defaultValue="10000" required /></label>
      </div>
      <p className="generator-warning">목표 회차 수 × 회차당 조합 수는 최대 5,000이며 실행 중에는 결과가 나올 때까지 기다려 주세요.</p>
      <BacktestButton />
    </form>
    {state.error && <div className="generation-error"><strong>백테스트 조건을 확인해 주세요.</strong><p>{state.error}</p></div>}
    {state.result && <BacktestResult result={state.result} />}
  </>;
}

function BacktestButton() { const { pending } = useFormStatus(); return <button className="generate-button" type="submit" disabled={pending}>{pending ? "과거 회차를 순서대로 검증 중…" : "백테스트 실행"}</button>; }

function BacktestResult({ result }: { result: BacktestResponse }) {
  const average = weightedAverage(result.main_match_distribution);
  const averageBest = weightedAverage(result.best_match_distribution);
  const leakageSafe = result.targets.every((target) => target.training_end_draw < target.target_draw_number);
  return <section className="backtest-result">
    <div className="generator-intro"><div><span className="eyebrow">BACKTEST RESULT</span><h2>실행 결과</h2></div><p>{result.complete_targets}/{result.target_count}개 목표 완료</p></div>
    <div className="analysis-summary backtest-summary">
      <article><span>생성 조합</span><strong>{result.total_generated_combinations.toLocaleString()}개</strong><small>{result.target_count}회 × {result.combinations_per_target}조합</small></article>
      <article><span>조합당 평균 일치</span><strong>{average.toFixed(3)}개</strong><small>전체 생성 조합 기준</small></article>
      <article><span>목표별 평균 최고</span><strong>{averageBest.toFixed(3)}개</strong><small>목표마다 최고 조합 기준</small></article>
      <article className="accent"><span>미래 데이터 차단</span><strong>{leakageSafe ? "확인" : "오류"}</strong><small>모든 학습 종료 &lt; 목표 회차</small></article>
    </div>
    <div className="backtest-distributions">
      <Distribution title="전체 조합 일치 분포" subtitle={`${result.total_generated_combinations.toLocaleString()}개 조합 기준`} values={result.main_match_distribution} />
      <Distribution title="목표별 최고 일치 분포" subtitle={`${result.target_count}개 목표 기준`} values={result.best_match_distribution} />
    </div>
    <div className="section-heading compact target-heading"><div><span>TARGET DETAILS</span><h2>목표 회차별 결과</h2></div><p>최신 목표부터 표시</p></div>
    <div className="backtest-targets">{[...result.targets].reverse().map((target) => <article key={target.target_draw_number}>
      <div className="target-title"><Link href={`/draws/${target.target_draw_number}`}><strong>{target.target_draw_number}회</strong></Link><span>최고 {target.best_main_match}개 일치</span></div>
      <div className="draw-numbers">{target.actual_numbers.map((number) => <LottoBall key={number} number={number} small />)}<span className="plus">+</span><LottoBall number={target.actual_bonus_number} small /></div>
      <dl><div><dt>학습 범위</dt><dd>{target.training_start_draw}–{target.training_end_draw}회</dd></div><div><dt>학습 회차</dt><dd>{target.training_draws}개</dd></div><div><dt>생성</dt><dd>{target.generated_combinations}/{target.requested_combinations}</dd></div><div><dt>seed</dt><dd>{target.seed}</dd></div></dl>
    </article>)}</div>
    <p className="analysis-disclaimer">백테스트는 과거 조건에서 생성 전략의 결과를 기술적으로 확인합니다. 과거 일치 수는 전략의 미래 성과나 실제 당첨 확률을 보장하지 않습니다.</p>
  </section>;
}

function Distribution({ title, subtitle, values }: { title: string; subtitle: string; values: number[] }) { const maximum = Math.max(...values, 1); return <section className="backtest-distribution"><h3>{title}</h3><p>{subtitle}</p>{values.map((count, matches) => <div key={matches}><span>{matches}개 일치</span><i><b style={{ width: `${count / maximum * 100}%` }} /></i><strong>{count.toLocaleString()}</strong></div>)}</section>; }
function weightedAverage(values: number[]) { const total = values.reduce((sum, count) => sum + count, 0); return total ? values.reduce((sum, count, value) => sum + count * value, 0) / total : 0; }
