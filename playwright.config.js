const { defineConfig, devices } = require('@playwright/test');

const port = process.env.PLAYWRIGHT_PORT || process.env.PORT || '5001';
const browserDataDir = process.env.PLAYWRIGHT_DATA_DIR || `data_browser_test_${port}`;
const browserBackupDir = process.env.PLAYWRIGHT_BACKUP_DIR || `backup_browser_test_${port}`;

module.exports = defineConfig({
  testDir: './tests/browser',
  timeout: 30000,
  expect: { timeout: 8000 },
  fullyParallel: false,
  reporter: process.env.CI ? [['list'], ['html', { open: 'never' }]] : [['list']],
  use: {
    baseURL: `http://127.0.0.1:${port}`,
    trace: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: {
    command: 'python app.py',
    url: `http://127.0.0.1:${port}/login`,
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
    env: {
      ...process.env,
      PORT: port,
      HOST: '127.0.0.1',
      AUTH_ENABLED: 'true',
      LEON_PASSWORD: 'playwright-pass',
      SECRET_KEY: 'playwright-secret-key',
      DATA_DIR: browserDataDir,
      BACKUP_DIR: browserBackupDir,
      LEON_TERMINAL_ACTIVITY: '0',
      LEON_STARTUP_VERBOSE: '0',
      LEON_TERMINAL_LOG_LEVEL: 'CRITICAL',
    },
  },
});
