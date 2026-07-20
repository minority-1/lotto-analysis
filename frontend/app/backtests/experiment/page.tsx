import { BacktestExperimentForm } from "@/components/backtest-experiment-form";
import { BacktestModeNav } from "@/components/backtest-mode-nav";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";

export default function BacktestExperimentPage() {
  return <main>
    <SiteHeader active="backtests" />
    <section className="page-hero backtest-hero"><div className="eyebrow">REPEATED STRATEGY EXPERIMENT</div><h1>반복 전략 비교</h1><p>동일한 목표 회차·조합 수·seed로 세 가지 생성 전략을 반복해 과거 결과를 비교합니다.</p></section>
    <section className="content backtest-page"><BacktestModeNav active="experiment" /><BacktestExperimentForm /></section>
    <SiteFooter />
  </main>;
}
