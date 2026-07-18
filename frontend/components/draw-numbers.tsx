import { LottoBall } from "@/components/lotto-ball";

type DrawNumbersProps = {
  numbers: number[];
  bonus?: number;
  small?: boolean;
};

export function DrawNumbers({ numbers, bonus, small = false }: DrawNumbersProps) {
  return (
    <div className="draw-numbers" aria-label={`당첨번호 ${numbers.join(", ")}`}>
      {numbers.map((number) => (
        <LottoBall key={number} number={number} small={small} />
      ))}
      {bonus !== undefined && (
        <>
          <span className="plus">+</span>
          <LottoBall number={bonus} small={small} />
        </>
      )}
    </div>
  );
}
