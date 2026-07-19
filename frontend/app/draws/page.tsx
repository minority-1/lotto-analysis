import Link from "next/link";
import { DrawNumbers } from "@/components/draw-numbers";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";
import { getDrawPage } from "@/lib/api";

export const dynamic = "force-dynamic";

const PAGE_SIZE = 20;

type DrawListPageProps = {
  searchParams: Promise<{ page?: string }>;
};

function parsePage(value: string | undefined): number {
  const page = Number(value ?? "1");
  return Number.isInteger(page) && page > 0 ? page : 1;
}

export default async function DrawListPage({ searchParams }: DrawListPageProps) {
  const requestedPage = parsePage((await searchParams).page);
  const result = await getDrawPage(requestedPage, PAGE_SIZE);

  if (!result) {
    return <DrawListOffline />;
  }

  const { draws, page, totalPages, total } = result;

  return (
    <main>
      <SiteHeader active="draws" />
      <section className="page-hero">
        <div className="eyebrow">DRAW ARCHIVE</div>
        <h1>회차 기록</h1>
        <p>1회부터 최신 회차까지 저장된 공식 당첨 결과를 확인합니다.</p>
      </section>

      <section className="content archive-page">
        <div className="archive-summary">
          <div><span>전체 기록</span><strong>{total.toLocaleString("ko-KR")}회</strong></div>
          <div><span>현재 페이지</span><strong>{page} / {totalPages}</strong></div>
        </div>

        <div className="archive-table">
          {draws.map((draw) => (
            <Link className="archive-row" href={`/draws/${draw.draw_number}`} key={draw.draw_number}>
              <div className="archive-number"><strong>{draw.draw_number}</strong><span>회</span></div>
              <time>{draw.draw_date}</time>
              <DrawNumbers numbers={draw.numbers} bonus={draw.bonus_number} small />
              <span className="row-arrow" aria-hidden="true">→</span>
            </Link>
          ))}
        </div>

        <nav className="pagination" aria-label="회차 페이지 이동">
          {page > 1 ? <Link href={`/draws?page=${page - 1}`}>← 최신 방향</Link> : <span />}
          <span>{page} / {totalPages}</span>
          {page < totalPages ? <Link href={`/draws?page=${page + 1}`}>과거 방향 →</Link> : <span />}
        </nav>
      </section>
      <SiteFooter />
    </main>
  );
}

function DrawListOffline() {
  return (
    <main>
      <SiteHeader active="draws" />
      <section className="offline-inline">
        <p className="eyebrow">API CONNECTION REQUIRED</p>
        <h1>회차 기록을 불러오지 못했습니다.</h1>
        <p>FastAPI 실행 상태를 확인한 뒤 새로고침해 주세요.</p>
      </section>
    </main>
  );
}
