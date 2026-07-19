import Link from "next/link";

import { AnalysisNav } from "@/components/analysis-nav";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";
import { getSimilarityAnalysis } from "@/lib/api";
import type { DrawSimilarity } from "@/lib/types";

export const dynamic = "force-dynamic";

export default async function SimilarityPage({ searchParams }: { searchParams: Promise<{ recent?: string }> }) {
  const query = await searchParams;
  const result = await getSimilarityAnalysis(query.recent ?? "100");
  return <main>
    <SiteHeader active="analysis" />
    <section className="page-hero analysis-hero"><div className="eyebrow">HISTORICAL SIMILARITY</div><h1>조합 유사도</h1><p>선택한 과거 회차 안에서 서로 다른 당첨 조합이 몇 개의 번호를 공유했는지 살펴봅니다.</p></section>
    <section className="content analysis-page">
      <AnalysisNav active="similarity" />
      <form className="single-range-form gap-form" action="/analysis/similarity"><label><span>분석 범위</span><select name="recent" defaultValue={query.recent ?? "100"}><option value="50">최근 50회</option><option value="100">최근 100회</option><option value="200">최근 200회</option><option value="500">최근 500회</option></select></label><button type="submit">분석</button></form>
      {result.data ? <SimilarityResult data={result.data} /> : <AnalysisError message={result.error} />}
    </section><SiteFooter />
  </main>;
}

function SimilarityResult({ data }: { data: NonNullable<Awaited<ReturnType<typeof getSimilarityAnalysis>>["data"]> }) {
  const mostCommonOverlap = data.overlap_distribution.reduce((best, count, overlap, values) => count > values[best] ? overlap : best, 0);
  const highOverlapPairs = data.overlap_distribution.slice(3).reduce((sum, count) => sum + count, 0);
  const maximumOverlap = Math.max(...data.draws.map((draw) => draw.maximum_overlap), 0);
  const recentDraws = [...data.draws].reverse().slice(0, 20);
  const maximumDistribution = Math.max(...data.overlap_distribution, 1);
  return <>
    <div className="analysis-summary similarity-summary">
      <article><span>분석 범위</span><strong>{data.start_draw}–{data.end_draw}회</strong><small>{data.total_draws}개 회차</small></article>
      <article><span>조합쌍 비교</span><strong>{data.pair_comparisons.toLocaleString()}쌍</strong><small>순서 없는 서로 다른 회차쌍</small></article>
      <article><span>가장 흔한 중복</span><strong>{mostCommonOverlap}개</strong><small>{data.overlap_distribution[mostCommonOverlap].toLocaleString()}쌍</small></article>
      <article className="accent"><span>최대 중복</span><strong>{maximumOverlap}개</strong><small>3개 이상 중복 {highOverlapPairs.toLocaleString()}쌍</small></article>
    </div>
    <div className="similarity-layout">
      <section className="similarity-distribution"><div className="section-heading compact"><div><span>OVERLAP DISTRIBUTION</span><h2>공통 번호 개수 분포</h2></div></div>
        {data.overlap_distribution.map((count, overlap) => <div className="overlap-row" key={overlap}><span>{overlap}개 중복</span><i><b style={{ width: `${count / maximumDistribution * 100}%` }} /></i><strong>{count.toLocaleString()}쌍</strong><small>{data.pair_comparisons ? (count / data.pair_comparisons * 100).toFixed(2) : "0.00"}%</small></div>)}
      </section>
      <section className="similarity-draws"><div className="section-heading compact"><div><span>RECENT DRAWS</span><h2>최근 회차별 최대 유사 기록</h2></div><p>최근 20개 회차</p></div>
        <div className="similarity-table">{recentDraws.map((draw) => <SimilarityRow key={draw.draw_number} draw={draw} />)}</div>
      </section>
    </div>
    <p className="analysis-disclaimer">조합 유사도는 과거 당첨 조합끼리 공유한 번호를 설명합니다. 과거 조합과 유사하거나 다른 정도가 미래 당첨 가능성을 높인다는 의미는 아닙니다.</p>
  </>;
}

function SimilarityRow({ draw }: { draw: DrawSimilarity }) {
  return <article><Link href={`/draws/${draw.draw_number}`}><strong>{draw.draw_number}회</strong></Link><div><span>최대 {draw.maximum_overlap}개</span><small>Jaccard {draw.maximum_jaccard?.toFixed(3) ?? "–"}</small></div><div className="similar-draw-links">{draw.most_similar_draws.slice(0, 4).map((number) => <Link href={`/draws/${number}`} key={number}>{number}회</Link>)}</div><small>3개 이상 {draw.overlap_3_count + draw.overlap_4_count + draw.overlap_5_count + draw.overlap_6_count}쌍</small></article>;
}

function AnalysisError({ message }: { message: string | null }) { return <div className="analysis-error"><p className="eyebrow">RANGE CHECK REQUIRED</p><h2>유사도 분석 범위를 확인해 주세요.</h2><p>{message ?? "FastAPI 연결 상태를 확인해 주세요."}</p></div>; }
