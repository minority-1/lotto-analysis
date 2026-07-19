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

export type ValueFrequency = { value: number; count: number; rate: number };

export type PatternAnalysis = {
  total_draws: number;
  start_draw: number;
  end_draw: number;
  ac_distribution: ValueFrequency[];
  gap_distribution: ValueFrequency[];
  prime_count_distribution: ValueFrequency[];
  composite_count_distribution: ValueFrequency[];
  square_count_distribution: ValueFrequency[];
  sum_band_distribution: Array<{ minimum: number; maximum: number; count: number; draw_rate: number }>;
  last_digit_sum_minimum: number;
  last_digit_sum_maximum: number;
  last_digit_sum_mean: number;
};

type CombinationFrequency = { numbers: number[]; count: number; draw_rate: number };

export type RelationshipAnalysis = {
  total_draws: number;
  start_draw: number;
  end_draw: number;
  pairs: CombinationFrequency[];
  triples: CombinationFrequency[];
  anchor_number: number | null;
  anchor_appearance_count: number;
  companions: Array<{ number: number; count: number; conditional_rate: number }>;
  distances: Array<{ distance: number; count: number; observation_rate: number }>;
  adjacent_pair_count: number;
  adjacent_draw_count: number;
  adjacent_draw_rate: number;
  same_last_digit_pair_count: number;
  same_last_digit_draw_count: number;
  same_last_digit_draw_rate: number;
  consecutive_groups: CombinationFrequency[];
  lag_overlaps: Array<{ lag: number; compared_draws: number; overlap_distribution: number[]; average_overlap: number }>;
  bonus_followups: Array<{ lag: number; eligible_draws: number; main_appearances: number; appearance_rate: number }>;
};

export type MatrixCell = {
  row: number;
  column: number;
  number: number | null;
  count: number;
  draw_rate: number;
};

export type MatrixAnalysis = {
  total_draws: number;
  start_draw: number;
  end_draw: number;
  cells: MatrixCell[];
  row_totals: number[];
  column_totals: number[];
  average_distinct_rows: number;
  average_distinct_columns: number;
  diagonals: Array<{ name: string; numbers: number[]; total_appearances: number; draw_count: number; draw_rate: number }>;
};

export type MatrixComparison = {
  baseline_start_draw: number;
  baseline_end_draw: number;
  comparison_start_draw: number;
  comparison_end_draw: number;
  baseline_total_draws: number;
  comparison_total_draws: number;
  cells: Array<{ row: number; column: number; number: number | null; baseline_count: number; comparison_count: number; baseline_rate: number; comparison_rate: number; rate_difference: number }>;
};
