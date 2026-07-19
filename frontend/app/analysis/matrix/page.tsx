import { AnalysisNav } from "@/components/analysis-nav";
import { MatrixModeNav } from "@/components/matrix-mode-nav";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";
import { getMatrixAnalysis } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function MatrixPage({ searchParams }: { searchParams: Promise<{ recent?: string }> }) {
  const query = await searchParams;
  const result = await getMatrixAnalysis(query.recent ?? "100");
  return <main>
    <SiteHeader active="analysis" />
    <section className="page-hero analysis-hero"><div className="eyebrow">NUMBER MATRIX</div><h1>번호 행렬</h1><p>1부터 45까지의 번호를 7×7 위치에 놓고 과거 출현 분포를 확인합니다.</p></section>
    <section className="content analysis-page">
      <AnalysisNav active="matrix" /><MatrixModeNav active="frequency" />
      <RangeForm recent={query.recent ?? "100"} action="/analysis/matrix" />
      {result.data ? <MatrixResult data={result.data} /> : <AnalysisError message={result.error} />}
    </section><SiteFooter />
  </main>;
}

function MatrixResult({ data }: { data: NonNullable<Awaited<ReturnType<typeof getMatrixAnalysis>>["data"]> }) {
  const maximum = Math.max(...data.cells.map((cell) => cell.count), 1);
  return <>
    <div className="analysis-summary matrix-summary">
      <article><span>분석 범위</span><strong>{data.start_draw}–{data.end_draw}회</strong><small>{data.total_draws}개 회차</small></article>
      <article><span>평균 사용 행</span><strong>{data.average_distinct_rows.toFixed(2)}</strong><small>회차당 서로 다른 행</small></article>
      <article><span>평균 사용 열</span><strong>{data.average_distinct_columns.toFixed(2)}</strong><small>회차당 서로 다른 열</small></article>
      <article className="accent"><span>전체 번호 출현</span><strong>{data.total_draws * 6}회</strong><small>보너스 제외</small></article>
    </div>
    <section className="matrix-section"><div className="section-heading compact"><div><span>7 × 7 GRID</span><h2>번호별 출현 횟수</h2></div><p>진한 색일수록 선택 범위에서 많이 출현</p></div>
      <div className="matrix-scroll"><div className="number-matrix">{data.cells.map((cell) => cell.number === null ? <div className="matrix-cell empty" key={`${cell.row}-${cell.column}`} /> : <article className="matrix-cell" key={cell.number} style={{ backgroundColor: `rgba(25, 92, 70, ${0.08 + cell.count / maximum * 0.72})` }}><strong>{cell.number}</strong><span>{cell.count}회</span><small>{(cell.draw_rate * 100).toFixed(1)}%</small></article>)}</div></div>
    </section>
    <div className="matrix-detail-grid">
      <Totals title="행별 합계" values={data.row_totals} />
      <Totals title="열별 합계" values={data.column_totals} />
      <section className="relationship-card matrix-diagonals"><h2>대각선 요약</h2>{data.diagonals.map((item) => <div className="metric-line" key={item.name}><span>{diagonalName(item.name)} · {item.numbers.join(", ")}</span><strong>{item.draw_count}회</strong><small>{(item.draw_rate * 100).toFixed(1)}%</small></div>)}</section>
    </div>
    <p className="analysis-disclaimer">행렬의 위치와 색상은 선택한 과거 범위의 출현 분포를 설명하며 번호의 우선순위나 미래 출현 가능성을 뜻하지 않습니다.</p>
  </>;
}

function RangeForm({ recent, action }: { recent: string; action: string }) { return <form className="single-range-form gap-form" action={action}><label><span>분석 범위</span><select name="recent" defaultValue={recent}><option value="50">최근 50회</option><option value="100">최근 100회</option><option value="200">최근 200회</option><option value="500">최근 500회</option><option value="0">전체 회차</option></select></label><button type="submit">분석</button></form>; }
function Totals({ title, values }: { title: string; values: number[] }) { return <section className="relationship-card"><h2>{title}</h2><div className="total-strip">{values.map((value, index) => <div key={index}><span>{index + 1}</span><strong>{value}</strong></div>)}</div></section>; }
function diagonalName(name: string) { return name === "main" ? "주대각선" : name === "anti" ? "역대각선" : name; }
function AnalysisError({ message }: { message: string | null }) { return <div className="analysis-error"><p className="eyebrow">RANGE CHECK REQUIRED</p><h2>행렬 분석 범위를 확인해 주세요.</h2><p>{message ?? "FastAPI 연결 상태를 확인해 주세요."}</p></div>; }
