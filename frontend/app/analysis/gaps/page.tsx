import { AnalysisNav } from "@/components/analysis-nav";
import { LottoBall } from "@/components/lotto-ball";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";
import { getGapAnalysis } from "@/lib/api";

export const dynamic = "force-dynamic";

type GapPageProps = { searchParams: Promise<{ recent?: string }> };

export default async function GapPage({ searchParams }: GapPageProps) {
  const query = await searchParams;
  const result = await getGapAnalysis(query.recent ?? "100");
  return <main>
    <SiteHeader active="analysis" />
    <section className="page-hero analysis-hero"><div className="eyebrow">APPEARANCE GAPS</div><h1>출현 간격</h1><p>선택한 과거 범위에서 번호별 출현 사이의 회차 간격을 요약합니다.</p></section>
    <section className="content analysis-page">
      <AnalysisNav active="gaps" />
      <form className="single-range-form gap-form" action="/analysis/gaps">
        <label><span>분석 범위</span><select name="recent" defaultValue={query.recent ?? "100"}>
          <option value="50">최근 50회</option><option value="100">최근 100회</option>
          <option value="200">최근 200회</option><option value="500">최근 500회</option><option value="0">전체 회차</option>
        </select></label><button type="submit">분석</button>
      </form>
      {result.data ? <GapResult data={result.data} /> : <AnalysisError message={result.error} />}
    </section><SiteFooter />
  </main>;
}

function GapResult({ data }: { data: NonNullable<Awaited<ReturnType<typeof getGapAnalysis>>["data"]> }) {
  const ordered = [...data.numbers].sort((a, b) => b.current_absence - a.current_absence || a.number - b.number);
  return <>
    <div className="period-summary gap-summary"><article><span>분석 범위</span><strong>{data.start_draw}–{data.end_draw}회</strong><small>{data.total_draws}개 회차</small></article></div>
    <div className="section-heading compact"><div><span>ALL NUMBERS</span><h2>번호별 간격 상세</h2></div><p>현재 미출현 회차 내림차순</p></div>
    <div className="gap-grid">{ordered.map((item) => <article key={item.number}>
      <LottoBall number={item.number} small />
      <div><span>현재 미출현</span><strong>{item.current_absence}회</strong></div>
      <div><span>평균 간격</span><strong>{item.mean_gap?.toFixed(1) ?? "–"}</strong></div>
      <div><span>최근 간격</span><strong>{item.latest_gap ?? "–"}</strong></div>
      <small>범위 {item.minimum_gap ?? "–"}–{item.maximum_gap ?? "–"}</small>
    </article>)}</div>
    <p className="analysis-disclaimer">현재 미출현 회차와 평균 간격은 과거 기록의 위치를 설명하며 다음 출현 시점을 예측하지 않습니다.</p>
  </>;
}

function AnalysisError({ message }: { message: string | null }) {
  return <div className="analysis-error"><p className="eyebrow">RANGE CHECK REQUIRED</p><h2>간격 분석 범위를 확인해 주세요.</h2><p>{message ?? "FastAPI 연결 상태를 확인해 주세요."}</p></div>;
}
