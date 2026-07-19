import { LottoBall } from "@/components/lotto-ball";
import { AnalysisNav } from "@/components/analysis-nav";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";
import { getBasicAnalysis } from "@/lib/api";

export const dynamic = "force-dynamic";

type AnalysisPageProps = {
  searchParams: Promise<{
    mode?: string;
    recent?: string;
    start_draw?: string;
    end_draw?: string;
    start_date?: string;
    end_date?: string;
  }>;
};

export default async function AnalysisPage({ searchParams }: AnalysisPageProps) {
  const query = await searchParams;
  const result = await getBasicAnalysis(query);

  return (
    <main>
      <SiteHeader active="analysis" />
      <section className="page-hero analysis-hero">
        <div className="eyebrow">DESCRIPTIVE STATISTICS</div>
        <h1>기본 통계</h1>
        <p>과거 회차의 출현 횟수와 조합 특성을 선택한 범위 안에서 살펴봅니다.</p>
      </section>

      <section className="content analysis-page">
        <AnalysisNav active="basic" />
        <RangeControls query={query} />
        {result.data ? <AnalysisResult data={result.data} /> : <AnalysisError message={result.error} />}
      </section>
      <SiteFooter />
    </main>
  );
}

type RangeQuery = Awaited<AnalysisPageProps["searchParams"]>;

function RangeControls({ query }: { query: RangeQuery }) {
  const mode = query.mode ?? "recent";
  return (
    <div className="range-panel">
      <form className="range-form" action="/analysis">
        <input type="hidden" name="mode" value="recent" />
        <label><span>최근 범위</span>
          <select name="recent" defaultValue={mode === "recent" ? query.recent ?? "100" : "100"}>
            <option value="50">최근 50회</option>
            <option value="100">최근 100회</option>
            <option value="200">최근 200회</option>
            <option value="500">최근 500회</option>
            <option value="0">전체 회차</option>
          </select>
        </label>
        <button type="submit">적용</button>
      </form>

      <form className="range-form" action="/analysis">
        <input type="hidden" name="mode" value="draw" />
        <label><span>시작 회차</span><input type="number" name="start_draw" min="1" required defaultValue={query.start_draw ?? ""} /></label>
        <label><span>끝 회차</span><input type="number" name="end_draw" min="1" required defaultValue={query.end_draw ?? ""} /></label>
        <button type="submit">회차 분석</button>
      </form>

      <form className="range-form" action="/analysis">
        <input type="hidden" name="mode" value="date" />
        <label><span>시작 날짜</span><input type="date" name="start_date" required defaultValue={query.start_date ?? ""} /></label>
        <label><span>끝 날짜</span><input type="date" name="end_date" required defaultValue={query.end_date ?? ""} /></label>
        <button type="submit">날짜 분석</button>
      </form>
    </div>
  );
}

function AnalysisResult({ data }: { data: NonNullable<Awaited<ReturnType<typeof getBasicAnalysis>>["data"]> }) {
  const ranked = [...data.number_statistics].sort(
    (left, right) => right.main_count - left.main_count || left.number - right.number,
  );
  const maximumCount = ranked[0]?.main_count ?? 1;

  return (
    <>
      <div className="analysis-summary">
        <article><span>분석 범위</span><strong>{data.start_draw}–{data.end_draw}회</strong><small>{data.total_draws}개 회차</small></article>
        <article><span>번호 합계 평균</span><strong>{data.summary.sum_mean.toFixed(1)}</strong><small>중앙값 {data.summary.sum_median.toFixed(1)}</small></article>
        <article><span>번호 합계 범위</span><strong>{data.summary.sum_min}–{data.summary.sum_max}</strong><small>표준편차 {data.summary.sum_standard_deviation.toFixed(1)}</small></article>
        <article className="accent"><span>연속번호 포함</span><strong>{(data.summary.consecutive_draw_rate * 100).toFixed(1)}%</strong><small>선택 범위 기준</small></article>
      </div>

      <div className="analysis-layout">
        <section>
          <div className="section-heading compact"><div><span>TOP 10</span><h2>출현 횟수 상위</h2></div></div>
          <div className="ranking-chart">
            {ranked.slice(0, 10).map((item, index) => (
              <div className="ranking-row" key={item.number}>
                <span className="rank">{String(index + 1).padStart(2, "0")}</span>
                <LottoBall number={item.number} small />
                <div className="ranking-bar"><i style={{ width: `${item.main_count / maximumCount * 100}%` }} /></div>
                <strong>{item.main_count}회</strong>
                <small>{(item.main_rate * 100).toFixed(1)}%</small>
              </div>
            ))}
          </div>
        </section>

        <section>
          <div className="section-heading compact"><div><span>ALL NUMBERS</span><h2>번호별 상세</h2></div></div>
          <div className="number-stat-grid">
            {data.number_statistics.map((item) => (
              <article key={item.number}>
                <LottoBall number={item.number} small />
                <div><strong>{item.main_count}회</strong><span>보너스 {item.bonus_count}회</span></div>
                <div className="absence"><strong>{item.absence_draws}</strong><span>현재 미출현</span></div>
              </article>
            ))}
          </div>
        </section>
      </div>
      <p className="analysis-disclaimer">출현 빈도와 미출현 회차는 선택한 과거 범위를 설명하는 값이며, 다음 당첨번호나 번호별 미래 확률을 의미하지 않습니다.</p>
    </>
  );
}

function AnalysisError({ message }: { message: string | null }) {
  return (
    <div className="analysis-error">
      <p className="eyebrow">RANGE CHECK REQUIRED</p>
      <h2>분석 범위를 확인해 주세요.</h2>
      <p>{message ?? "FastAPI 연결 상태를 확인한 뒤 다시 시도해 주세요."}</p>
    </div>
  );
}
