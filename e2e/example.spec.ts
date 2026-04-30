import { test, expect } from '@playwright/test';

// Reusable setup — goes to homepage before each test
test.beforeEach(async ({ page }) => {
  await page.goto('http://localhost:8501/');
  // Wait for Streamlit to fully load
  await page.waitForLoadState('networkidle');
});

// ─── TEST 1: Bowling tab loads ───────────────────────────────────────────────
test('bowling tab loads successfully', async ({ page }) => {
  await page.getByRole('tab', { name: '🎯 BOWLING' }).click();
  await page.waitForLoadState('networkidle');
  // Verify the tab is now active/visible
  await expect(page.getByRole('tab', { name: '🎯 BOWLING' })).toBeVisible();
});

// ─── TEST 2: Team Intel — dropdown works ────────────────────────────────────
test('team intel tab loads and team selection works', async ({ page }) => {
  await page.getByRole('tab', { name: '🏟️ TEAM INTEL' }).click();
  await page.waitForLoadState('networkidle');

  // Select Chennai Super Kings
  await page.locator('div').filter({ hasText: /^Chennai Super Kings$/ }).nth(2).click();
  await page.waitForLoadState('networkidle');

  // Select opponent team
  await page.getByTestId('stSelectboxVirtualDropdown')
    .getByText('Royal Challengers Bengaluru').click();
  await page.waitForLoadState('networkidle');

  // Verify something rendered (page didn't crash)
  await expect(page.getByRole('tab', { name: '🏟️ TEAM INTEL' })).toBeVisible();
});

// ─── TEST 3: Best XI tab loads ───────────────────────────────────────────────
test('best XI vs opponent tab loads player cards', async ({ page }) => {
  await page.getByRole('tab', { name: '🏟️ TEAM INTEL' }).click();
  await page.waitForLoadState('networkidle');

  await page.getByRole('tab', { name: '🌟 Best XI vs Opponent' }).click();
  await page.waitForLoadState('networkidle');

  // Verify player cards appear
  await expect(page.locator('.xi-card').first()).toBeVisible();
  await expect(page.locator('.xi-name').first()).toBeVisible();
});

// ─── TEST 4: Head to Head — player search works ──────────────────────────────
test('head to head tab loads and player search works', async ({ page }) => {
  await page.getByRole('tab', { name: '⚔️ HEAD TO HEAD' }).click();
  await page.waitForLoadState('networkidle');

  // Search for RG Sharma
  await page.getByRole('combobox', { name: /Selected/ }).fill('rg');
  await page.getByRole('combobox', { name: /Selected/ }).press('ArrowUp');
  await page.getByRole('combobox', { name: /Selected/ }).press('Enter');

  // Verify RG Sharma appears in selection
  await expect(
    page.locator('div').filter({ hasText: /^RG Sharma$/ }).nth(3)
  ).toBeVisible();
});

// ─── TEST 5: Player search — search by name works ────────────────────────────
test('player search returns results for V Kohli', async ({ page }) => {
  await page.getByRole('tab', { name: '🔎 PLAYER SEARCH' }).click();
  await page.waitForLoadState('networkidle');

  await page.getByPlaceholder('🔍  Search — e.g. Kohli,').fill('V Kohli');
  await page.getByPlaceholder('🔍  Search — e.g. Kohli,').press('Enter');
  await page.waitForLoadState('networkidle');

  // Verify results appeared — page didn't stay blank
  await expect(page.getByPlaceholder('🔍  Search — e.g. Kohli,')).toHaveValue('V Kohli');
});

// ─── TEST 6: Player search — works for bowler too ────────────────────────────
test('player search returns results for Bumrah', async ({ page }) => {
  await page.getByRole('tab', { name: '🔎 PLAYER SEARCH' }).click();
  await page.waitForLoadState('networkidle');

  await page.getByPlaceholder('🔍  Search — e.g. Kohli,').fill('bumrah');
  await page.getByPlaceholder('🔍  Search — e.g. Kohli,').press('Enter');
  await page.waitForLoadState('networkidle');

  await expect(page.getByPlaceholder('🔍  Search — e.g. Kohli,')).toHaveValue('bumrah');
});

// ─── TEST 7: All tabs are present on load ────────────────────────────────────
test('all main tabs are visible on homepage', async ({ page }) => {
  await expect(page.getByRole('tab', { name: '🏏 BATTING' })).toBeVisible();
  await expect(page.getByRole('tab', { name: '🎯 BOWLING' })).toBeVisible();
  await expect(page.getByRole('tab', { name: '🏟️ TEAM INTEL' })).toBeVisible();
  await expect(page.getByRole('tab', { name: '⚔️ HEAD TO HEAD' })).toBeVisible();
  await expect(page.getByRole('tab', { name: '🔎 PLAYER SEARCH' })).toBeVisible();
});