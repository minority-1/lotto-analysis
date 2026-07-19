import { AnalysisNav } from "@/components/analysis-nav";
import { LottoBall } from "@/components/lotto-ball";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";
import { getPeriodComparison } from "@/lib/api";

export const dynamic = "force-dynamic";

type ComparePageProps = {
  searchParams: Promise<{ recent?: string; against_all?: string }>;
};

export default async function ComparePage({ searchParams }: ComparePageProps) {
  const query = await searchParams;
  const result = await getPeriodComparison(query.recent ?? "50", query.against_all === "true");

  return (
    <main>
      <SiteHeader active="analysis" />
      <section className="page-hero analysis-hero">
        <div className="eyebrow">PERIOD COMPARISON</div>
        <h1>기간 비교</h1>
        <p>서로 다른 과거 기간의 번호별 회차당 출현률과 순위를 비교합니다.</p>
      </section>
      <section className="content analysis-page">
        <AnalysisNav active="compare" />
        <form className="single-range-form" action="/analysis/compare">
          <label><span>최근 비교 기간</span><select name="recent" defaultValue={query.recent ?? "50"}>
            <option value="20">최근 20회</option><option value="30">최근 30회</option>
            <option value="50">최근 50회</option><option value="100">최근 100회</option>
            <option value="200">최근 200회</option>
          </select></label>
          <label><span>기준 기간</span><select name="against_all" defaultValue={query.against_all ?? "false"}>
            <option value="false">직전 동일 기간</option><option value="true">전체 회차</option>
          </select></label>
          <button type="submit">비교</button>
        </form>
        {result.data ? <ComparisonResult data={result.data} /> : <AnalysisError message={result.error} />}
      </section>
      <SiteFooter />
    </main>
  );
}

function ComparisonResult({ data }: { data: NonNullable<Awaited<ReturnType<typeof getPeriodComparison>>["data"]> }) {
  const ordered = [...data.numbers].sort((a, b) => Math.abs(b.rate_difference) - Math.abs(a.rate_difference));
  const maximum = Math.max(...ordered.map((item) => Math.abs(item.rate_difference)), 0.01);
  return <>
    <div className="period-summary">
      <article><span>기준 기간</span><strong>{data.baseline_start_draw}–{data.baseline_end_draw}회</strong><small>{data.baseline_total_draws}개 회차</small></article>
      <article><span>비교 기간</span><strong>{data.comparison_start_draw}–{data.comparison_end_draw}회</strong><small>{data.comparison_total_draws}개 회차</small></article>
    </div>
    <div className="section-heading compact"><div><span>RATE DIFFERENCE</span><h2>출현률 차이</h2></div><p>차이 절댓값 순</p></div>
    <div className="comparison-table">
      {ordered.map((item) => <div className="comparison-row" key={item.number}>
        <LottoBall number={item.number} small />
        <div className="comparison-values"><span>기준 {(item.baseline_rate * 100).toFixed(1)}%</span><span>비교 {(item.comparison_rate * 100).toFixed(1)}%</span></div>
        <div className={`difference-bar ${item.rate_difference < 0 ? "negative" : ""}`}><i style={{ width: `${Math.abs(item.rate_difference) / maximum * 100}%` }} /></div>
        <strong className={item.rate_difference < 0 ? "negative-text" : "positive-text"}>{item.rate_difference > 0 ? "+" : ""}{(item.rate_difference * 100).toFixed(1)}%p</strong>
        <small>순위 {item.rank_change > 0 ? "+" : ""}{item.rank_change}</small>
      </div>)}
    </div>
    <p className="analysis-disclaimer">출현률 차이와 순위 변화는 두 과거 기간의 기술적 비교이며 이후 기간의 추세나 당첨 가능성을 의미하지 않습니다.</p>
  </>;
}

function AnalysisError({ message }: { message: string | null }) {
  return <div className="analysis-error"><p className="eyebrow">RANGE CHECK REQUIRED</p><h2>비교 범위를 확인해 주세요.</h2><p>{message ?? "FastAPI 연결 상태를 확인해 주세요."}</p></div>;
}
