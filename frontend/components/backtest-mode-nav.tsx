import Link from "next/link";

export function BacktestModeNav({ active }: { active: "single" | "experiment" }) {
  return <nav className="backtest-mode-nav" aria-label="백테스트 화면">
    <Link className={active === "single" ? "active" : ""} href="/backtests">단일 전략 실행</Link>
    <Link className={active === "experiment" ? "active" : ""} href="/backtests/experiment">반복 전략 비교</Link>
  </nav>;
}
