import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Lotto Lab | 로또 데이터 분석",
  description: "한국 로또 6/45 과거 데이터의 예측 중립적 통계 분석",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}
