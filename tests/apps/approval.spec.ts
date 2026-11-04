import {randomUUID} from 'node:crypto';
import {test, expect, login, api, loseResponse, type Outcome} from './fixtures.js';
import type {Page} from '@playwright/test';

test('approval desk native browser journey', async ({app, browser}) => {
  // @covers US-101-AC1 @covers US-101-AC2 @covers US-101-AC3 @covers US-101-AC4 @covers US-101-AC5
  let [alex, blake, casey] = await Promise.all(['alex', 'blake', 'casey'].map(actor => login(browser, app.url, actor)));
  await expect(alex.locator('#empty')).toBeVisible();
  for (const [action, predicate] of [
    [async () => {await alex.locator('#title').fill('Fabricated equipment request'); await alex.locator('#submit').click();}, () => expect(alex.locator('#requests strong')).toHaveText('Fabricated equipment request')],
    [() => blake.locator('#refresh').click(), () => expect(blake.getByRole('button', {name: 'Approve request'})).toBeVisible()],
    [async () => {await alex.locator('#edit-title').fill('Fabricated revised equipment request'); await alex.getByRole('button', {name: 'Save changes'}).click();}, () => expect(alex.locator('#requests strong')).toHaveText('Fabricated revised equipment request')],
    [() => blake.getByRole('button', {name: 'Approve request'}).click(), () => expect(blake.locator('#notice')).toContainText('changed')],
    [() => blake.locator('#refresh').click(), () => expect(blake.getByRole('button', {name: 'Approve request'})).toBeEnabled()],
    [() => blake.getByRole('button', {name: 'Approve request'}).click(), () => expect(blake.locator('#detail')).toContainText('Approved')],
  ]) {await action(); await predicate();}
  const final = (await api(blake, 'list', {})).result!;
  expect(final.rows.map(row => [row.owner, row.state, row.decided_by, row.title])).toEqual([['alex', 'approved', 'blake', 'Fabricated revised equipment request']]);
  expect((await api(casey, 'get', {id: final.rows[0].id})).result).toEqual({rows: [], cursor: null});
  await alex.locator('#title').fill('Fabricated response loss');
  await alex.route('**/apps/approval-desk/api/operations/submit', loseResponse);
  await alex.locator('#submit').click();
  await expect(alex.locator('#notice')).toContainText('response was lost');
  await alex.unroute('**/apps/approval-desk/api/operations/submit', loseResponse);
  await alex.locator('#observe').click();
  await expect(alex.locator('#requests strong')).toHaveCount(2);
  await expect(alex.locator('#observe')).toBeHidden();
  expect((await api(casey, 'list', {})).result).toEqual({rows: [], cursor: null});
  expect((await api(blake, 'submit', {title: 'Fabricated reviewer request'}, randomUUID())).status).toBe('succeeded');
  const reviewer = (await api(blake, 'list', {})).result!.rows.find(row => row.owner === 'blake')!;
  const refusals: [Page, string, Record<string, string>, string][] = [
    [blake, 'decide', {id: reviewer.id, revision: reviewer.revision, decision: 'approved'}, 'precondition_failed'],
    [alex, 'decide', {id: final.rows[0].id, revision: final.rows[0].revision, decision: 'approved'}, 'denied'],
    [alex, 'unknown', {}, 'denied'],
    [alex, 'submit', {title: 'Fabricated impersonation', actor: 'blake'}, 'invalid'],
  ];
  for (const [page, operation, inputs, expected] of refusals) expect((await api(page, operation, inputs, randomUUID())).status).toBe(expected);
  await app.stop();
  const cli = JSON.parse(await app.command('call', '--actor', 'blake', '--operation', 'list')) as Outcome;
  expect([cli.status, cli.result!.rows.length, cli.result!.rows.find(row => row.owner === 'blake')!.state]).toEqual(['succeeded', 3, 'pending']);
  await app.start();
  expect((await api(alex, 'list', {})).status).toBe('denied');
  [alex, blake] = await Promise.all(['alex', 'blake'].map(actor => login(browser, app.url, actor)));
  await app.revokeReviewer();
  const own = (await api(blake, 'list', {})).result!;
  expect(own.rows.length > 0 && own.rows.every(row => row.owner === 'blake')).toBe(true);
  const pending = (await api(alex, 'list', {})).result!.rows.find(row => row.state === 'pending')!;
  expect((await api(blake, 'decide', {id: pending.id, revision: pending.revision, decision: 'approved'}, randomUUID())).status).toBe('precondition_failed');
  expect((await api(alex, 'get', {id: pending.id})).result!.rows[0].state).toBe('pending');
  await app.stop();
  const originalHead = app.setHead('0'.repeat(64));
  try {await expect(app.start()).rejects.toThrow('installation-reference-mismatch');} finally {app.setHead(originalHead);}
  await app.start();
  const captures = app.capture('audit.jsonl') + app.capture('spans.jsonl');
  const spans = app.capture('spans.jsonl').trim().split('\n').map(line => JSON.parse(line) as {name: string; span_id: string; parent_id: string; trace_id: string});
  expect(['Fabricated', 'postgresql://', 'SELECT '].every(value => !captures.includes(value))).toBe(true);
  expect(spans.some(span => span.name === 'database') && spans.some(span => span.name === 'operation') && spans.filter(span => span.name === 'database').every(span => spans.some(parent => ['operation', 'startup'].includes(parent.name) && parent.span_id === span.parent_id && parent.trace_id === span.trace_id))).toBe(true);
});

test('registry lists visual apps and brand returns home', async ({app, browser}, testInfo) => {
  // @covers US-101-AC6
  const page = await browser.newPage();
  await page.goto(app.url);
  const card = page.getByRole('link', {name: 'Open Approval desk', exact: true});
  await expect(card).toContainText('independent decision');
  expect(await card.locator('img').evaluate(image => (image as HTMLImageElement).complete && (image as HTMLImageElement).naturalWidth > 0)).toBe(true);
  await card.click();
  await expect(page).toHaveURL(app.url + '/apps/approval-desk/');
  await page.locator('#actor').selectOption('alex');
  await expect(page.locator('#submit')).toBeEnabled();
  expect([...new Set((await page.context().cookies()).filter(cookie => cookie.name === 'batten_local').map(cookie => cookie.path))]).toEqual(['/apps/approval-desk/api']);
  await page.getByRole('link', {name: 'Batten application registry'}).click();
  await expect(page).toHaveURL(app.url + '/');
  await expect(page.getByRole('heading', {name: 'Applications', exact: true})).toBeVisible();
  expect(await Promise.all(['/apps/unregistered/', '/api/session'].map(async path => (await page.request.get(app.url + path)).status()))).toEqual([404, 404]);
  for (const [width, height] of [[1365, 900], [390, 844]]) {
    await page.setViewportSize({width, height});
    await page.goto(app.url);
    await expect(page.getByRole('heading', {name: 'Applications', exact: true})).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    await expect(page.getByRole('link', {name: 'Open Approval desk', exact: true})).toBeVisible();
    await page.screenshot({path: testInfo.outputPath(`registry-${width}.png`), fullPage: true});
  }
  await page.close();
});
