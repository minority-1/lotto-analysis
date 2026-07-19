import Link from "next/link";

export function MatrixModeNav({ active }: { active: "frequency" | "compare" }) {
  return <nav className="matrix-mode-nav" aria-label="번호 행렬 보기">
    <Link className={active === "frequency" ? "active" : ""} href="/analysis/matrix">출현 행렬</Link>
    <Link className={active === "compare" ? "active" : ""} href="/analysis/matrix/compare">기간 차이 행렬</Link>
  </nav>;
}
