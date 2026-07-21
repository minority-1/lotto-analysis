import { expect, test } from "@playwright/test";

test("대시보드에서 최신 데이터와 주요 메뉴를 확인한다", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("heading", { name: /숫자를 예측하지 않고/ })).toBeVisible();
  await expect(page.getByText("1232", { exact: true })).toBeVisible();
  for (const menu of ["대시보드", "회차", "분석", "번호 생성", "백테스트"]) {
    await expect(page.getByRole("link", { name: menu, exact: true })).toBeVisible();
  }
});

test("회차 상세를 표시하고 없는 회차는 404 화면으로 안내한다", async ({ page }) => {
  await page.goto("/draws/1232");
  await expect(page.getByText("1등 당첨자")).toBeVisible();
  await expect(page.getByRole("link", { name: "전체 회차" })).toBeVisible();

  await page.goto("/draws/9999");
  await expect(page.getByRole("heading", { name: "해당 회차를 찾을 수 없습니다." })).toBeVisible();
});

test("기본 통계 범위와 번호별 결과를 표시한다", async ({ page }) => {
  await page.goto("/analysis");

  await expect(page.getByRole("heading", { name: "기본 통계", exact: true })).toBeVisible();
  await expect(page.getByText("1133–1232회")).toBeVisible();
  await expect(page.getByRole("heading", { name: "번호별 상세" })).toBeVisible();
});

test("번호 생성 후 결과와 제출한 입력값을 유지한다", async ({ page }) => {
  await page.goto("/generate");
  await page.getByLabel("생성 개수").fill("1");
  await page.getByLabel("재현 seed").fill("42");
  await page.getByLabel("반드시 포함").fill("20");
  await page.getByLabel("제외", { exact: true }).fill("21");
  await page.getByRole("button", { name: "후보 조합 생성" }).click();

  await expect(page.getByRole("heading", { name: "생성 결과" })).toBeVisible();
  await expect(page.getByLabel("재현 seed")).toHaveValue("42");
  await expect(page.getByLabel("반드시 포함")).toHaveValue("20");
  await expect(page.getByLabel("제외", { exact: true })).toHaveValue("21");
});
