import { AnalysisNav } from "@/components/analysis-nav";
import { MatrixModeNav } from "@/components/matrix-mode-nav";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";
import { getMatrixComparison } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function MatrixComparePage({ searchParams }: { searchParams: Promise<{ recent?: string }> }) {
  const query = await searchParams;
  const result = await getMatrixComparison(query.recent ?? "50");
  return <main>
    <SiteHeader active="analysis" />
    <section className="page-hero analysis-hero"><div className="eyebrow">MATRIX COMPARISON</div><h1>기간 차이 행렬</h1><p>최근 기간과 바로 앞의 동일 길이 기간을 번호 위치별 출현률로 비교합니다.</p></section>
    <section className="content analysis-page">
      <AnalysisNav active="matrix" /><MatrixModeNav active="compare" />
      <form className="single-range-form gap-form" action="/analysis/matrix/compare"><label><span>비교 기간</span><select name="recent" defaultValue={query.recent ?? "50"}><option value="20">최근 20회</option><option value="30">최근 30회</option><option value="50">최근 50회</option><option value="100">최근 100회</option><option value="200">최근 200회</option></select></label><button type="submit">비교</button></form>
      {result.data ? <ComparisonResult data={result.data} /> : <AnalysisError message={result.error} />}
    </section><SiteFooter />
  </main>;
}

function ComparisonResult({ data }: { data: NonNullable<Awaited<ReturnType<typeof getMatrixComparison>>["data"]> }) {
  const maximum = Math.max(...data.cells.map((cell) => Math.abs(cell.rate_difference)), 0.01);
  return <>
    <div className="period-summary"><article><span>기준 기간</span><strong>{data.baseline_start_draw}–{data.baseline_end_draw}회</strong><small>{data.baseline_total_draws}개 회차</small></article><article><span>비교 기간</span><strong>{data.comparison_start_draw}–{data.comparison_end_draw}회</strong><small>{data.comparison_total_draws}개 회차</small></article></div>
    <section className="matrix-section"><div className="section-heading compact"><div><span>RATE DIFFERENCE</span><h2>회차당 출현률 차이</h2></div><p>초록 증가 · 붉은색 감소</p></div>
      <div className="matrix-scroll"><div className="number-matrix">{data.cells.map((cell) => cell.number === null ? <div className="matrix-cell empty" key={`${cell.row}-${cell.column}`} /> : <article className={`matrix-cell comparison ${cell.rate_difference < 0 ? "down" : "up"}`} key={cell.number} style={{ ["--strength" as string]: `${0.1 + Math.abs(cell.rate_difference) / maximum * 0.75}` }}><strong>{cell.number}</strong><span>{cell.rate_difference > 0 ? "+" : ""}{(cell.rate_difference * 100).toFixed(1)}%p</span><small>{cell.baseline_count} → {cell.comparison_count}회</small></article>)}</div></div>
    </section>
    <p className="analysis-disclaimer">출현률 차이는 두 과거 기간을 동일한 회차 수로 비교한 값이며 이후 기간의 상승·하락 추세를 예측하지 않습니다.</p>
  </>;
}

function AnalysisError({ message }: { message: string | null }) { return <div className="analysis-error"><p className="eyebrow">RANGE CHECK REQUIRED</p><h2>행렬 비교 범위를 확인해 주세요.</h2><p>{message ?? "FastAPI 연결 상태를 확인해 주세요."}</p></div>; }
