const { defineConfig, devices } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests/browser',
  timeout: 30000,
  expect: { timeout: 8000 },
  fullyParallel: false,
  reporter: process.env.CI ? [['list'], ['html', { open: 'never' }]] : [['list']],
  use: {
    baseURL: 'http://127.0.0.1:5001',
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
    url: 'http://127.0.0.1:5001/login',
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
    env: {
      ...process.env,
      PORT: '5001',
      HOST: '127.0.0.1',
      AUTH_ENABLED: 'true',
      LEON_PASSWORD: 'playwright-pass',
      SECRET_KEY: 'playwright-secret-key',
      DATA_DIR: 'data_browser_test',
      BACKUP_DIR: 'backup_browser_test',
      LEON_TERMINAL_ACTIVITY: '0',
      LEON_STARTUP_VERBOSE: '0',
      LEON_TERMINAL_LOG_LEVEL: 'CRITICAL',
    },
  },
});
