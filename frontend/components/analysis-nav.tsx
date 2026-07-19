import Link from "next/link";

type AnalysisNavProps = {
  active: "basic" | "compare" | "gaps" | "patterns" | "relationships" | "matrix" | "similarity";
};

export function AnalysisNav({ active }: AnalysisNavProps) {
  return (
    <nav className="analysis-nav" aria-label="분석 화면">
      <Link className={active === "basic" ? "active" : ""} href="/analysis">기본 통계</Link>
      <Link className={active === "compare" ? "active" : ""} href="/analysis/compare">기간 비교</Link>
      <Link className={active === "gaps" ? "active" : ""} href="/analysis/gaps">출현 간격</Link>
      <Link className={active === "patterns" ? "active" : ""} href="/analysis/patterns">조합 패턴</Link>
      <Link className={active === "relationships" ? "active" : ""} href="/analysis/relationships">번호 관계</Link>
      <Link className={active === "matrix" ? "active" : ""} href="/analysis/matrix">번호 행렬</Link>
      <Link className={active === "similarity" ? "active" : ""} href="/analysis/similarity">조합 유사도</Link>
    </nav>
  );
}
