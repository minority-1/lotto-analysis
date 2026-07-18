export type LottoDraw = {
  draw_number: number;
  draw_date: string;
  numbers: [number, number, number, number, number, number];
  bonus_number: number;
  first_prize_winners: number;
  first_prize_amount: number;
  total_sales_amount: number;
  collected_at: string | null;
};

export type Dashboard = {
  total_draws: number;
  first_draw_number: number | null;
  latest_draw: LottoDraw | null;
  missing_draw_numbers: number[];
};

export type DrawPage = {
  items: LottoDraw[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
};

export type NumberStatistic = {
  number: number;
  main_count: number;
  main_rate: number;
  bonus_count: number;
  last_draw_number: number | null;
  last_draw_date: string | null;
  absence_draws: number;
};

export type BasicAnalysis = {
  total_draws: number;
  start_draw: number;
  end_draw: number;
  number_statistics: NumberStatistic[];
  summary: {
    sum_min: number;
    sum_max: number;
    sum_mean: number;
    sum_median: number;
    consecutive_draw_rate: number;
  };
};
