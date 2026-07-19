import { GenerationForm } from "@/components/generation-form";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";

export default function GeneratePage() {
  return <main>
    <SiteHeader active="generate" />
    <section className="page-hero generate-hero"><div className="eyebrow">CONDITION-BASED GENERATOR</div><h1>번호 조합 생성</h1><p>선택한 조건을 만족하는 무작위 후보 조합을 제한된 시도 안에서 생성합니다.</p></section>
    <section className="content generate-page"><GenerationForm /></section>
    <SiteFooter />
  </main>;
}
