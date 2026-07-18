import { DrawNumbers } from "@/components/draw-numbers";
import { LottoBall } from "@/components/lotto-ball";
import { getDashboardData } from "@/lib/api";

export const dynamic = "force-dynamic";

const won = new Intl.NumberFormat("ko-KR");

async function loadDashboard() {
  try {
    return await getDashboardData();
  } catch {
    return null;
  }
}

export default async function Home() {
  const data = await loadDashboard();
  if (!data) {
    return <OfflineState />;
  }

    const { dashboard, draws, analysis } = data;
    const latest = dashboard.latest_draw;
    const hotNumbers = [...analysis.number_statistics]
      .sort((left, right) => right.main_count - left.main_count || left.number - right.number)
      .slice(0, 8);

    return (
      <main>
        <header className="topbar">
          <a className="brand" href="#top" aria-label="Lotto Lab 홈">
            <span className="brand-mark">L</span>
            <span>LOTTO LAB</span>
          </a>
          <nav aria-label="주요 메뉴">
            <a className="active" href="#overview">대시보드</a>
            <a href="#draws">회차</a>
            <a href="#frequency">분석</a>
          </nav>
          <span className="status"><i /> API 연결됨</span>
        </header>

        <section className="hero" id="top">
          <div className="eyebrow">KOREAN LOTTO 6/45 · DATA ARCHIVE</div>
          <h1>숫자를 예측하지 않고,<br /><em>기록을 선명하게.</em></h1>
          <p>과거 당첨 데이터를 정직한 통계로 살펴보는 개인 분석실입니다.</p>
        </section>

        <section className="content" id="overview">
          <div className="section-heading">
            <div><span>OVERVIEW</span><h2>데이터 현황</h2></div>
            <p>마지막 업데이트 기준</p>
          </div>

          <div className="overview-grid">
            <article className="latest-card">
              <div className="card-label">LATEST DRAW</div>
              {latest ? (
                <>
                  <div className="latest-title">
                    <div><strong>{latest.draw_number}</strong><span>회</span></div>
                    <time>{latest.draw_date}</time>
                  </div>
                  <DrawNumbers numbers={latest.numbers} bonus={latest.bonus_number} />
                  <div className="prize-row">
                    <span>1등 당첨</span>
                    <strong>{latest.first_prize_winners}명</strong>
                    <span>1인당</span>
                    <strong>{won.format(latest.first_prize_amount)}원</strong>
                  </div>
                </>
              ) : <p>저장된 회차가 없습니다.</p>}
            </article>

            <div className="metric-stack">
              <article className="metric-card"><span>수집 완료</span><strong>{won.format(dashboard.total_draws)}</strong><small>개 회차</small></article>
              <article className="metric-card"><span>누락 회차</span><strong>{dashboard.missing_draw_numbers.length}</strong><small>개</small></article>
              <article className="metric-card accent"><span>분석 범위</span><strong>{analysis.total_draws}</strong><small>최근 회차</small></article>
            </div>
          </div>
        </section>

        <section className="content split-section">
          <article id="draws">
            <div className="section-heading compact"><div><span>ARCHIVE</span><h2>최근 회차 기록</h2></div></div>
            <div className="draw-list">
              {draws.map((draw) => (
                <div className="draw-row" key={draw.draw_number}>
                  <div className="draw-meta"><strong>{draw.draw_number}회</strong><time>{draw.draw_date}</time></div>
                  <DrawNumbers numbers={draw.numbers} bonus={draw.bonus_number} small />
                </div>
              ))}
            </div>
          </article>

          <article id="frequency">
            <div className="section-heading compact"><div><span>RECENT 100</span><h2>출현 빈도 상위</h2></div></div>
            <div className="frequency-card">
              {hotNumbers.map((item, index) => (
                <div className="frequency-row" key={item.number}>
                  <span className="rank">{String(index + 1).padStart(2, "0")}</span>
                  <LottoBall number={item.number} small />
                  <div className="bar-track"><i style={{ width: `${item.main_rate * 100}%` }} /></div>
                  <strong>{item.main_count}회</strong>
                </div>
              ))}
              <p className="notice">과거 출현 횟수는 미래 당첨 확률을 의미하지 않습니다.</p>
            </div>
          </article>
        </section>

        <footer>LOTTO LAB <span>·</span> DATA, NOT PREDICTION <span>·</span> {new Date().getFullYear()}</footer>
      </main>
    );
}

function OfflineState() {
  return (
    <main className="offline-page">
      <div className="offline-card">
        <span className="brand-mark">L</span>
        <p className="eyebrow">API CONNECTION REQUIRED</p>
        <h1>분석 서버를 기다리고 있어요.</h1>
        <p>FastAPI를 8000번 포트에서 실행한 뒤 이 페이지를 새로고침해 주세요.</p>
        <code>uvicorn lotto_analysis.api.main:app --reload</code>
      </div>
    </main>
  );
}
