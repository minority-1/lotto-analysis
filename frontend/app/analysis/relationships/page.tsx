import { AnalysisNav } from "@/components/analysis-nav";
import { LottoBall } from "@/components/lotto-ball";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";
import { getRelationshipAnalysis } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function RelationshipPage({ searchParams }: { searchParams: Promise<{ recent?: string; number?: string }> }) {
  const query = await searchParams;
  const result = await getRelationshipAnalysis(query.recent ?? "100", query.number ?? "7");
  return <main>
    <SiteHeader active="analysis" />
    <section className="page-hero analysis-hero"><div className="eyebrow">NUMBER RELATIONSHIPS</div><h1>번호 관계</h1><p>과거 회차에서 함께 나온 번호와 회차 사이의 중복 관계를 살펴봅니다.</p></section>
    <section className="content analysis-page">
      <AnalysisNav active="relationships" />
      <form className="single-range-form relationship-form" action="/analysis/relationships">
        <label><span>분석 범위</span><select name="recent" defaultValue={query.recent ?? "100"}><option value="50">최근 50회</option><option value="100">최근 100회</option><option value="200">최근 200회</option><option value="500">최근 500회</option><option value="0">전체 회차</option></select></label>
        <label><span>기준 번호</span><select name="number" defaultValue={query.number ?? "7"}>{Array.from({ length: 45 }, (_, index) => <option key={index + 1} value={index + 1}>{index + 1}번</option>)}</select></label>
        <button type="submit">분석</button>
      </form>
      {result.data ? <RelationshipResult data={result.data} /> : <AnalysisError message={result.error} />}
    </section><SiteFooter />
  </main>;
}

function RelationshipResult({ data }: { data: NonNullable<Awaited<ReturnType<typeof getRelationshipAnalysis>>["data"]> }) {
  const companions = data.companions.slice(0, 10);
  return <>
    <div className="analysis-summary relationship-summary">
      <article><span>분석 범위</span><strong>{data.start_draw}–{data.end_draw}회</strong><small>{data.total_draws}개 회차</small></article>
      <article><span>기준 번호</span><strong>{data.anchor_number ?? "–"}번</strong><small>{data.anchor_appearance_count}회 출현</small></article>
      <article><span>±1 번호 포함</span><strong>{(data.adjacent_draw_rate * 100).toFixed(1)}%</strong><small>{data.adjacent_draw_count}개 회차</small></article>
      <article className="accent"><span>같은 끝수 포함</span><strong>{(data.same_last_digit_draw_rate * 100).toFixed(1)}%</strong><small>{data.same_last_digit_draw_count}개 회차</small></article>
    </div>
    <div className="relationship-layout">
      <section className="relationship-card"><h2>{data.anchor_number}번 동반 출현 상위</h2>{companions.map((item) => <div className="companion-row" key={item.number}><LottoBall number={item.number} small /><i><b style={{ width: `${item.conditional_rate * 100}%` }} /></i><strong>{item.count}회</strong><small>{(item.conditional_rate * 100).toFixed(1)}%</small></div>)}</section>
      <CombinationList title="번호쌍 상위 10" items={data.pairs.slice(0, 10)} />
      <CombinationList title="3개 조합 상위 10" items={data.triples.slice(0, 10)} />
      <section className="relationship-card"><h2>직전 회차와 평균 중복</h2>{data.lag_overlaps.map((item) => <div className="metric-line" key={item.lag}><span>{item.lag}회 전</span><strong>{item.average_overlap.toFixed(2)}개</strong><small>{item.compared_draws}회 비교</small></div>)}</section>
      <section className="relationship-card"><h2>보너스 번호 후속 출현</h2>{data.bonus_followups.map((item) => <div className="metric-line" key={item.lag}><span>{item.lag}회 뒤</span><strong>{(item.appearance_rate * 100).toFixed(1)}%</strong><small>{item.main_appearances}/{item.eligible_draws}회</small></div>)}</section>
      <section className="relationship-card"><h2>번호 간 거리 상위</h2>{[...data.distances].sort((a, b) => b.count - a.count).slice(0, 8).map((item) => <div className="metric-line" key={item.distance}><span>거리 {item.distance}</span><strong>{item.count}회</strong><small>{(item.observation_rate * 100).toFixed(1)}%</small></div>)}</section>
    </div>
    <p className="analysis-disclaimer">동반 출현과 회차 간 중복은 과거 관계의 빈도를 설명하며 번호 추천 점수나 조건부 당첨 확률이 아닙니다.</p>
  </>;
}

function CombinationList({ title, items }: { title: string; items: Array<{ numbers: number[]; count: number; draw_rate: number }> }) { return <section className="relationship-card"><h2>{title}</h2>{items.map((item) => <div className="combination-row" key={item.numbers.join("-")}><div>{item.numbers.map((number) => <LottoBall key={number} number={number} small />)}</div><strong>{item.count}회</strong><small>{(item.draw_rate * 100).toFixed(1)}%</small></div>)}</section>; }
function AnalysisError({ message }: { message: string | null }) { return <div className="analysis-error"><p className="eyebrow">RANGE CHECK REQUIRED</p><h2>관계 분석 범위를 확인해 주세요.</h2><p>{message ?? "FastAPI 연결 상태를 확인해 주세요."}</p></div>; }
