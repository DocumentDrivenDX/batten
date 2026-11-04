import {defineConfig} from '@playwright/test';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';

const sources = ['playwright.config.ts', 'tests/apps/approval.spec.ts', 'tests/apps/fixtures.ts', 'tests/apps/host.ts', 'tests/apps/native_probe.py', 'package.json', 'bun.lock', 'uv.lock', '.cache/approval-cohort.json'];

export default defineConfig({
  testDir: './tests/apps',
  metadata: {sourceHashes: Object.fromEntries(sources.map(path => [path, createHash('sha256').update(readFileSync(path)).digest('hex')]))},
  testMatch: '**/*.spec.ts',
  fullyParallel: false,
  workers: 1,
  retries: 0,
  timeout: 600_000,
  reporter: [['list'], ['json', {outputFile: '.cache/browser-results.json'}]],
  outputDir: '.cache/browser-test-artifacts',
  use: {browserName: 'chromium', headless: true},
});
