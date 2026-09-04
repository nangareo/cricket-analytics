import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright config — https://playwright.dev/docs/test-configuration
 *
 * `webServer` boots the Streamlit dashboard automatically, so `npx playwright
 * test` works from a clean checkout without starting anything by hand. An
 * already-running dashboard on :8501 is reused locally.
 */
const PORT = 8501;
const BASE_URL = `http://localhost:${PORT}`;

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  // One Streamlit process serves every session, and each worker's page load
  // triggers a full script rerun. Five at once occasionally starved a tab of
  // its render budget; three keeps the suite deterministic and costs ~5s.
  workers: process.env.CI ? 1 : 3,
  reporter: 'html',

  /* Streamlit reruns the whole script on every interaction, so give it room. */
  timeout: 90_000,
  expect: { timeout: 20_000 },

  use: {
    baseURL: BASE_URL,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  webServer: {
    command:
      '.venv/bin/streamlit run dashboard/app.py ' +
      `--server.port=${PORT} --server.address=0.0.0.0 --server.headless=true`,
    url: `${BASE_URL}/_stcore/health`,
    reuseExistingServer: !process.env.CI,
    timeout: 180_000,
    stdout: 'pipe',
    stderr: 'pipe',
  },
});
