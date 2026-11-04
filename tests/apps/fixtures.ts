import {test as base, type Browser, type Page, type Route} from '@playwright/test';
import {AppHost} from './host.js';

export const test = base.extend<object, {app: AppHost}>({
  app: [async ({}, use) => {
    const app = await AppHost.create();
    try {await use(app);} finally {await app.stop();}
  }, {scope: 'worker', timeout: 300_000}],
});
export {expect} from '@playwright/test';

export interface RequestRow {
  id: string; owner: string; state: string; decided_by: string | null;
  title: string; revision: string;
}
export interface Outcome {
  http: number; status: string; result?: {rows: RequestRow[]; cursor: string | null};
}
export async function login(browser: Browser, url: string, actor: string): Promise<Page> {
  const page = await browser.newPage();
  await page.goto(url);
  await page.getByRole('link', {name: 'Open Approval desk', exact: true}).click();
  await page.locator('#actor').selectOption(actor);
  await page.locator('#actor:enabled').waitFor();
  await page.locator('#refresh:enabled').waitFor();
  return page;
}
export async function api(page: Page, operation: string, inputs: Record<string, string>, key?: string): Promise<Outcome> {
  return await page.evaluate(async ({operation, inputs, key}) => {
    const response = await fetch('./api/operations/' + operation, {method: 'POST', headers: {'content-type': 'application/json'}, body: JSON.stringify({inputs, ...(key ? {key} : {})})});
    return {http: response.status, ...await response.json()};
  }, {operation, inputs, key});
}
export async function loseResponse(route: Route): Promise<void> {
  await route.fetch();
  await route.abort('failed');
}
