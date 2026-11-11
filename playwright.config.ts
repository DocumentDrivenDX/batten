import {defineConfig} from '@playwright/test';

export default defineConfig({
  testDir: './tests/apps',
  testMatch: '**/*.spec.ts',
  fullyParallel: false,
  workers: 1,
  retries: 0,
  timeout: 600_000,
  reporter: [['list'], ['json', {outputFile: '.cache/browser-results.json'}]],
  outputDir: '.cache/browser-test-artifacts',
  use: {browserName: 'chromium', headless: true},
});
