import Link from "next/link";

type AnalysisNavProps = {
  active: "basic" | "compare" | "gaps";
};

export function AnalysisNav({ active }: AnalysisNavProps) {
  return (
    <nav className="analysis-nav" aria-label="분석 화면">
      <Link className={active === "basic" ? "active" : ""} href="/analysis">기본 통계</Link>
      <Link className={active === "compare" ? "active" : ""} href="/analysis/compare">기간 비교</Link>
      <Link className={active === "gaps" ? "active" : ""} href="/analysis/gaps">출현 간격</Link>
    </nav>
  );
}
