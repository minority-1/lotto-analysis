import { createServer } from "node:http";

const portFlag = process.argv.indexOf("--port");
const port = Number(portFlag >= 0 ? process.argv[portFlag + 1] : 18000);

function draw(drawNumber = 1232) {
  return {
    draw_number: drawNumber,
    draw_date: "2026-07-18",
    numbers: [3, 11, 20, 27, 34, 42],
    bonus_number: 7,
    first_prize_winners: 12,
    first_prize_amount: 2_100_000_000,
    total_sales_amount: 115_000_000_000,
    collected_at: "2026-07-19T00:00:00+09:00",
  };
}

const latestDraw = draw();
const numberStatistics = Array.from({ length: 45 }, (_, index) => ({
  number: index + 1,
  main_count: 20 - (index % 10),
  main_rate: (20 - (index % 10)) / 100,
  bonus_count: index % 4,
  last_draw_number: 1232 - (index % 8),
  last_draw_date: "2026-07-18",
  absence_draws: index % 8,
}));
const basicAnalysis = {
  total_draws: 100,
  start_draw: 1133,
  end_draw: 1232,
  number_statistics: numberStatistics,
  summary: {
    sum_min: 82,
    sum_max: 214,
    sum_mean: 138.5,
    sum_median: 137,
    sum_standard_deviation: 26.4,
    consecutive_draw_count: 49,
    consecutive_draw_rate: 0.49,
  },
};

function json(response, status, body) {
  response.writeHead(status, {
    "Content-Type": "application/json; charset=utf-8",
    "Access-Control-Allow-Origin": "*",
  });
  response.end(JSON.stringify(body));
}

function generationResponse(body) {
  const required = body.required_numbers?.[0] ?? 3;
  const available = [3, 11, 20, 27, 34, 42].filter(
    (number) => number !== required && !body.excluded_numbers?.includes(number),
  );
  const numbers = [required, ...available, 45]
    .filter((number, index, values) => values.indexOf(number) === index)
    .slice(0, 6)
    .sort((left, right) => left - right);
  return {
    strategy: "uniform_random",
    strategy_details: [],
    requested_count: body.count,
    combinations: [{
      numbers,
      odd_count: numbers.filter((number) => number % 2 === 1).length,
      even_count: numbers.filter((number) => number % 2 === 0).length,
      low_count: numbers.filter((number) => number <= 22).length,
      high_count: numbers.filter((number) => number > 22).length,
      number_sum: numbers.reduce((total, number) => total + number, 0),
      prime_count: 2,
      ac_value: 5,
      consecutive_pair_count: 0,
      maximum_historical_overlap: 2,
    }],
    attempts: 1,
    maximum_attempts: body.maximum_attempts,
    rejection_counts: [],
    seed: body.seed,
    complete: body.count === 1,
    message: body.count === 1 ? null : "테스트 응답은 한 조합만 반환합니다.",
  };
}

createServer((request, response) => {
  const url = new URL(request.url ?? "/", `http://127.0.0.1:${port}`);
  if (request.method === "GET" && url.pathname === "/api/health") {
    return json(response, 200, { status: "ok" });
  }
  if (request.method === "GET" && url.pathname === "/api/dashboard") {
    return json(response, 200, { total_draws: 1232, first_draw_number: 1, latest_draw: latestDraw, missing_draw_numbers: [] });
  }
  if (request.method === "GET" && url.pathname === "/api/draws") {
    return json(response, 200, Array.from({ length: 8 }, (_, index) => draw(1232 - index)));
  }
  if (request.method === "GET" && url.pathname === "/api/analysis/basic") {
    return json(response, 200, basicAnalysis);
  }
  if (request.method === "GET" && url.pathname === "/api/draws/latest") {
    return json(response, 200, latestDraw);
  }
  if (request.method === "GET" && url.pathname === "/api/draws/1232") {
    return json(response, 200, latestDraw);
  }
  if (request.method === "GET" && url.pathname.startsWith("/api/draws/")) {
    return json(response, 404, { detail: "Draw not found" });
  }
  if (request.method === "POST" && url.pathname === "/api/combinations/generate") {
    let payload = "";
    request.on("data", (chunk) => { payload += chunk; });
    request.on("end", () => json(response, 200, generationResponse(JSON.parse(payload))));
    return;
  }
  return json(response, 404, { detail: "Mock route not found" });
}).listen(port, "127.0.0.1");
