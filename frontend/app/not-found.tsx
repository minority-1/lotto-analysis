import Link from "next/link";
import { SiteHeader } from "@/components/site-header";

export default function NotFound() {
  return (
    <main>
      <SiteHeader active="draws" />
      <section className="offline-inline">
        <p className="eyebrow">DRAW NOT FOUND</p>
        <h1>해당 회차를 찾을 수 없습니다.</h1>
        <p>저장된 회차 번호인지 확인해 주세요.</p>
        <Link className="primary-link" href="/draws">회차 목록으로</Link>
      </section>
    </main>
  );
}
