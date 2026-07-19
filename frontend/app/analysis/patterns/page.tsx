import { AnalysisNav } from "@/components/analysis-nav";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";
import { getPatternAnalysis } from "@/lib/api";
import type { ValueFrequency } from "@/lib/types";

export const dynamic = "force-dynamic";

export default async function PatternPage({ searchParams }: { searchParams: Promise<{ recent?: string }> }) {
  const query = await searchParams;
  const result = await getPatternAnalysis(query.recent ?? "100");
  return <main>
    <SiteHeader active="analysis" />
    <section className="page-hero analysis-hero"><div className="eyebrow">COMBINATION PATTERNS</div><h1>조합 패턴</h1><p>과거 당첨 조합의 수학적 형태와 분포를 선택한 범위에서 요약합니다.</p></section>
    <section className="content analysis-page">
      <AnalysisNav active="patterns" />
      <RangeForm recent={query.recent ?? "100"} action="/analysis/patterns" />
      {result.data ? <PatternResult data={result.data} /> : <AnalysisError message={result.error} />}
    </section>
    <SiteFooter />
  </main>;
}

function RangeForm({ recent, action }: { recent: string; action: string }) {
  return <form className="single-range-form gap-form" action={action}><label><span>분석 범위</span><select name="recent" defaultValue={recent}>
    <option value="50">최근 50회</option><option value="100">최근 100회</option><option value="200">최근 200회</option><option value="500">최근 500회</option><option value="0">전체 회차</option>
  </select></label><button type="submit">분석</button></form>;
}

function PatternResult({ data }: { data: NonNullable<Awaited<ReturnType<typeof getPatternAnalysis>>["data"]> }) {
  return <>
    <div className="analysis-summary pattern-summary">
      <article><span>분석 범위</span><strong>{data.start_draw}–{data.end_draw}회</strong><small>{data.total_draws}개 회차</small></article>
      <article><span>끝수 합계 평균</span><strong>{data.last_digit_sum_mean.toFixed(1)}</strong><small>범위 {data.last_digit_sum_minimum}–{data.last_digit_sum_maximum}</small></article>
      <article><span>대표 AC 값</span><strong>{mostCommon(data.ac_distribution)?.value ?? "–"}</strong><small>최다 출현 기준</small></article>
      <article className="accent"><span>대표 합계 구간</span><strong>{mostCommonBand(data.sum_band_distribution)}</strong><small>최다 출현 기준</small></article>
    </div>
    <div className="pattern-layout">
      <Distribution title="AC 값 분포" items={data.ac_distribution} />
      <Distribution title="소수 개수 분포" items={data.prime_count_distribution} />
      <Distribution title="합성수 개수 분포" items={data.composite_count_distribution} />
      <Distribution title="제곱수 개수 분포" items={data.square_count_distribution} />
      <Distribution title="인접 간격 분포" items={data.gap_distribution} limit={12} />
      <section className="distribution-card"><h2>번호 합계 구간</h2>{data.sum_band_distribution.map((item) => <div className="distribution-row" key={item.minimum}><span>{item.minimum}–{item.maximum}</span><i><b style={{ width: `${item.draw_rate * 100}%` }} /></i><strong>{item.count}회</strong><small>{(item.draw_rate * 100).toFixed(1)}%</small></div>)}</section>
    </div>
    <p className="analysis-disclaimer">조합 패턴 분포는 과거 당첨 조합의 형태를 설명하며 특정 패턴의 미래 당첨 가능성을 의미하지 않습니다.</p>
  </>;
}

function Distribution({ title, items, limit }: { title: string; items: ValueFrequency[]; limit?: number }) {
  const visible = limit ? items.slice(0, limit) : items;
  const maximum = Math.max(...visible.map((item) => item.count), 1);
  return <section className="distribution-card"><h2>{title}</h2>{visible.map((item) => <div className="distribution-row" key={item.value}><span>{item.value}</span><i><b style={{ width: `${item.count / maximum * 100}%` }} /></i><strong>{item.count}회</strong><small>{(item.rate * 100).toFixed(1)}%</small></div>)}</section>;
}

function mostCommon(items: ValueFrequency[]) { return [...items].sort((a, b) => b.count - a.count || a.value - b.value)[0]; }
function mostCommonBand(items: Array<{ minimum: number; maximum: number; count: number }>) { const item = [...items].sort((a, b) => b.count - a.count)[0]; return item ? `${item.minimum}–${item.maximum}` : "–"; }
function AnalysisError({ message }: { message: string | null }) { return <div className="analysis-error"><p className="eyebrow">RANGE CHECK REQUIRED</p><h2>패턴 분석 범위를 확인해 주세요.</h2><p>{message ?? "FastAPI 연결 상태를 확인해 주세요."}</p></div>; }
