import { BacktestForm } from "@/components/backtest-form";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";

export default function BacktestsPage() {
  return <main>
    <SiteHeader active="backtests" />
    <section className="page-hero backtest-hero"><div className="eyebrow">LEAKAGE-SAFE BACKTEST</div><h1>전략 백테스트</h1><p>각 목표 회차보다 이전 데이터만 학습에 사용해 번호 생성 전략의 과거 결과를 확인합니다.</p></section>
    <section className="content backtest-page"><BacktestForm /></section>
    <SiteFooter />
  </main>;
}
