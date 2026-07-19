import Link from "next/link";

type SiteHeaderProps = {
  active: "dashboard" | "draws" | "analysis";
};

export function SiteHeader({ active }: SiteHeaderProps) {
  return (
    <header className="topbar">
      <Link className="brand" href="/" aria-label="Lotto Lab 홈">
        <span className="brand-mark">L</span>
        <span>LOTTO LAB</span>
      </Link>
      <nav aria-label="주요 메뉴">
        <Link className={active === "dashboard" ? "active" : ""} href="/">
          대시보드
        </Link>
        <Link className={active === "draws" ? "active" : ""} href="/draws">
          회차
        </Link>
        <Link className={active === "analysis" ? "active" : ""} href="/#frequency">
          분석
        </Link>
      </nav>
      <span className="status"><i /> API 연결됨</span>
    </header>
  );
}
