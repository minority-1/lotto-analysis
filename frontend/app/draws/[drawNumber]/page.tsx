import Link from "next/link";
import { notFound } from "next/navigation";
import { DrawNumbers } from "@/components/draw-numbers";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";
import { getDrawDetail } from "@/lib/api";

export const dynamic = "force-dynamic";

const won = new Intl.NumberFormat("ko-KR");

type DrawDetailPageProps = {
  params: Promise<{ drawNumber: string }>;
};

export default async function DrawDetailPage({ params }: DrawDetailPageProps) {
  const drawNumber = Number((await params).drawNumber);
  if (!Number.isInteger(drawNumber) || drawNumber < 1) {
    notFound();
  }

  const result = await getDrawDetail(drawNumber);
  if (!result) {
    notFound();
  }
  const { draw, latestDrawNumber } = result;

  return (
    <main>
      <SiteHeader active="draws" />
      <section className="draw-detail-hero">
        <div className="eyebrow">DRAW RESULT · {draw.draw_date}</div>
        <div className="detail-title"><strong>{draw.draw_number}</strong><span>회</span></div>
        <DrawNumbers numbers={draw.numbers} bonus={draw.bonus_number} />
      </section>

      <section className="content detail-content">
        <div className="detail-grid">
          <article><span>1등 당첨자</span><strong>{won.format(draw.first_prize_winners)}명</strong></article>
          <article><span>1인당 당첨금</span><strong>{won.format(draw.first_prize_amount)}원</strong></article>
          <article><span>총 판매금액</span><strong>{won.format(draw.total_sales_amount)}원</strong></article>
        </div>

        <div className="detail-note">
          <span>ABOUT THIS DATA</span>
          <p>공식 결과에서 수집하고 검증한 과거 회차 정보입니다. 이 기록과 통계는 미래 번호를 예측하거나 당첨 가능성을 높인다는 의미가 아닙니다.</p>
        </div>

        <nav className="draw-navigation" aria-label="인접 회차 이동">
          {draw.draw_number > 1 ? <Link href={`/draws/${draw.draw_number - 1}`}>← {draw.draw_number - 1}회</Link> : <span />}
          <Link className="back-to-list" href="/draws">전체 회차</Link>
          {draw.draw_number < latestDrawNumber ? (
            <Link href={`/draws/${draw.draw_number + 1}`}>{draw.draw_number + 1}회 →</Link>
          ) : <span />}
        </nav>
      </section>
      <SiteFooter />
    </main>
  );
}
