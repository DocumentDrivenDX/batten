import {invoke, login, session, type Actor, type Call, type Outcome, type RequestRecord} from './api';

function element<T extends HTMLElement>(selector: string): T {
  const value = document.querySelector<T>(selector);
  if (!value) throw new Error('Missing app control: ' + selector);
  return value;
}

const actorSelect = element<HTMLSelectElement>('#actor');
const requests = element<HTMLUListElement>('#requests');
const detail = element<HTMLElement>('#detail');
const notice = element<HTMLElement>('#notice');
const observe = element<HTMLButtonElement>('#observe');
const submit = element<HTMLButtonElement>('#submit');
const refresh = element<HTMLButtonElement>('#refresh');
let actor: Actor | null = null;
let records: RequestRecord[] = [];
let selected: RequestRecord | null = null;
let pending: Call | null = null;
let epoch = 0;
let busy = false;
let needsRefresh = false;

function message(text: string, error = false): void {
  notice.textContent = text;
  notice.dataset.error = String(error);
  notice.hidden = false;
}

function statusLabel(state: string): string {
  return ({pending: 'Pending review', approved: 'Approved', rejected: 'Rejected'} as Record<string,string>)[state] || state;
}

function person(id: string): string {
  return ({alex: 'Alex', blake: 'Blake', casey: 'Casey'} as Record<string,string>)[id] || id;
}

function savePending(call: Call | null): void {
  pending = call;
  if (actor) {
    const key = 'batten.approval.pending.' + actor.id;
    if (call) localStorage.setItem(key, JSON.stringify(call));
    else localStorage.removeItem(key);
  }
  observe.hidden = !pending;
  submit.disabled = !actor || busy || !!pending;
}

function badge(state: string): HTMLSpanElement {
  const value = document.createElement('span');
  value.className = 'badge ' + state;
  value.textContent = statusLabel(state);
  return value;
}

function row(record: RequestRecord): HTMLLIElement {
  const item = document.createElement('li');
  const button = document.createElement('button');
  button.type = 'button';
  button.setAttribute('aria-pressed', String(record.id === selected?.id));
  const title = document.createElement('strong');
  title.textContent = record.title;
  const meta = document.createElement('span');
  meta.className = 'row-meta';
  const owner = document.createElement('span');
  owner.textContent = person(record.owner);
  meta.append(badge(record.state), owner);
  button.append(title, meta);
  button.addEventListener('click', () => {selected = record; render(); detail.focus();});
  item.append(button);
  return item;
}

function info(label: string, text: string, list: HTMLDListElement): void {
  const term = document.createElement('dt');
  term.textContent = label;
  const description = document.createElement('dd');
  description.textContent = text;
  list.append(term, description);
}

function action(label: string, operation: string, inputs: Record<string,string>, className = ''): HTMLButtonElement {
  const button = document.createElement('button');
  button.type = 'button';
  button.textContent = label;
  button.className = className;
  button.disabled = busy || !!pending || needsRefresh;
  button.addEventListener('click', () => void mutate({operation, inputs, key: crypto.randomUUID()}));
  return button;
}

function editable(record: RequestRecord): void {
  const label = document.createElement('label');
  label.htmlFor = 'edit-title'; label.textContent = 'Update the pending summary';
  const input = document.createElement('textarea');
  input.id = 'edit-title'; input.value = record.title; input.maxLength = 240;
  const button = document.createElement('button');
  button.textContent = 'Save changes'; button.type = 'button';
  button.disabled = busy || !!pending || needsRefresh;
  button.addEventListener('click', () => {
    if (!input.value.trim()) {message('Add a request summary first.', true); input.focus(); return;}
    void mutate({operation: 'edit', inputs: {id: record.id, title: input.value.trim(), revision: record.revision}, key: crypto.randomUUID()});
  });
  const controls = document.createElement('div'); controls.className = 'actions'; controls.append(button);
  detail.append(label, input, controls);
}

function renderDetail(): void {
  detail.replaceChildren();
  if (!selected) {
    const text = document.createElement('p'); text.className = 'detail-placeholder';
    text.textContent = 'Select a request to inspect its current record.'; detail.append(text); return;
  }
  const record = selected;
  const heading = document.createElement('h3'); heading.textContent = record.title;
  const list = document.createElement('dl');
  info('Requested by', person(record.owner), list);
  info('Current decision', statusLabel(record.state), list);
  if (record.decided_by) info('Decided by', person(record.decided_by), list);
  info('Revision', record.revision.slice(0, 12), list);
  detail.append(badge(record.state), heading, list);
  if (record.state !== 'pending') return;
  if (record.owner === actor?.id) {editable(record); return;}
  if (!actor?.can_review) return;
  const hint = document.createElement('p'); hint.textContent = 'Your decision applies to the revision shown. If the request changes, inspect it again.';
  const controls = document.createElement('div'); controls.className = 'actions';
  controls.append(action('Approve request', 'decide', {id: record.id, revision: record.revision, decision: 'approved'}), action('Reject request', 'decide', {id: record.id, revision: record.revision, decision: 'rejected'}, 'reject'));
  detail.append(hint, controls);
}

function render(): void {
  requests.replaceChildren(...records.map(row));
  element('#empty').hidden = records.length > 0;
  element('#count').textContent = actor ? `${records.length} requests in this view` : 'Choose an identity to begin.';
  submit.disabled = !actor || busy || !!pending;
  refresh.disabled = !actor || busy;
  observe.hidden = !pending;
  renderDetail();
}

async function load(): Promise<void> {
  const current = epoch;
  requests.setAttribute('aria-busy', 'true');
  try {
    const outcome = await invoke({operation: 'list', inputs: {}});
    if (current !== epoch) return;
    if (outcome.status !== 'succeeded') {message('This view is unavailable or your access has changed.', true); records = []; selected = null;}
    else {
      records = outcome.result?.rows || [];
      selected = records.find(record => record.id === selected?.id) || records[0] || null;
    }
    needsRefresh = false; render();
  } catch {if (current === epoch) message('The host is unavailable. Your records have not been changed.', true);}
  finally {if (current === epoch) requests.setAttribute('aria-busy', 'false');}
}

function explain(outcome: Outcome): void {
  if (outcome.status === 'precondition_failed') message('This request changed or cannot be decided by this identity. Refresh and inspect the current record.', true);
  else if (outcome.status === 'denied') message('Your current identity cannot perform this action.', true);
  else if (outcome.status === 'uncertain') message('The outcome is not confirmed. Check the original outcome before doing anything again.', true);
  else if (outcome.status === 'invalid') message('Check the supplied values. No valid change was accepted.', true);
  else message('The operation is unavailable. Keep the original outcome identity for recovery.', true);
}

function refused(outcome: Outcome): void {
  if (['denied','invalid','precondition_failed'].includes(outcome.status)) savePending(null);
  needsRefresh = outcome.status === 'precondition_failed';
  explain(outcome);
}

function canMutate(): boolean {
  return actor !== null && !busy;
}

async function mutate(call: Call, phase = 'invoke'): Promise<void> {
  if (!canMutate()) return;
  const current = epoch; busy = true; savePending(call); render();
  try {
    const outcome = await invoke(call, phase);
    if (current !== epoch) return;
    if (outcome.status === 'succeeded') {
      savePending(null); message(phase === 'observe' ? 'The original outcome is confirmed.' : 'The current record has been saved.');
      if (call.operation === 'submit') element<HTMLTextAreaElement>('#title').value = '';
      await load();
    } else {
      refused(outcome);
    }
  } catch {if (current === epoch) message('The response was lost. Check the original outcome; do not submit a new command.', true);}
  finally {if (current === epoch) {busy = false; render();}}
}

function restorePending(): void {
  if (!actor) return;
  const stored = localStorage.getItem('batten.approval.pending.' + actor.id);
  if (!stored) return;
  try {
    const value = JSON.parse(stored);
    if (!['submit', 'edit', 'decide'].includes(value.operation) || typeof value.key !== 'string' || !value.inputs || typeof value.inputs !== 'object') throw new Error('Invalid recovery identity');
    savePending(value);
    message('An earlier operation needs its original outcome checked.', true);
  } catch {message('The saved recovery record is unreadable. Inspect records before making another change.', true); needsRefresh = true;}
}

async function chooseActor(): Promise<void> {
  const current = ++epoch;
  busy = false; actor = null; records = []; selected = null; pending = null; needsRefresh = false;
  actorSelect.disabled = true; notice.hidden = true; render();
  try {
    await login(actorSelect.value);
    const value = await session();
    if (current !== epoch) return;
    actor = value; restorePending();
    if (actor) await load();
  } catch {if (current === epoch) message('This local identity is unavailable.', true);}
  finally {if (current === epoch) {actorSelect.disabled = false; render();}}
}

async function boot(): Promise<void> {
  const current = epoch;
  try {
    const value = await session();
    if (current !== epoch) return;
    actor = value;
    if (actor) {actorSelect.value = actor.id; restorePending(); await load();}
    render();
  } catch {if (current === epoch) message('Start the local host to use this app.', true);}
  finally {if (current === epoch) actorSelect.disabled = false;}
}

actorSelect.addEventListener('change', () => void chooseActor());
refresh.addEventListener('click', () => void load());
observe.addEventListener('click', () => {if (pending) void mutate(pending, 'observe');});
element<HTMLFormElement>('#submit-form').addEventListener('submit', event => {
  event.preventDefault();
  const title = element<HTMLTextAreaElement>('#title');
  if (!title.value.trim()) {title.focus(); return;}
  void mutate({operation: 'submit', inputs: {title: title.value.trim()}, key: crypto.randomUUID()});
});
void boot();
