type LottoBallProps = {
  number: number;
  small?: boolean;
};

function colorClass(number: number): string {
  if (number <= 10) return "ball-yellow";
  if (number <= 20) return "ball-blue";
  if (number <= 30) return "ball-red";
  if (number <= 40) return "ball-gray";
  return "ball-green";
}

export function LottoBall({ number, small = false }: LottoBallProps) {
  return (
    <span className={`lotto-ball ${colorClass(number)} ${small ? "small" : ""}`}>
      {number}
    </span>
  );
}
