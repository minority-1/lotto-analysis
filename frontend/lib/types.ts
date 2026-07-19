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
    sum_standard_deviation: number;
    consecutive_draw_count: number;
    consecutive_draw_rate: number;
  };
};

export type PeriodComparison = {
  baseline_label: string; comparison_label: string;
  baseline_start_draw: number; baseline_end_draw: number;
  comparison_start_draw: number; comparison_end_draw: number;
  baseline_total_draws: number; comparison_total_draws: number;
  numbers: Array<{ number: number; baseline_count: number; comparison_count: number; baseline_rate: number; comparison_rate: number; rate_difference: number; baseline_rank: number; comparison_rank: number; rank_change: number }>;
};

export type GapAnalysis = {
  total_draws: number; start_draw: number; end_draw: number;
  numbers: Array<{ number: number; appearance_draws: number[]; gaps: number[]; mean_gap: number | null; median_gap: number | null; minimum_gap: number | null; maximum_gap: number | null; latest_gap: number | null; current_absence: number; gap_standard_deviation: number | null }>;
};
