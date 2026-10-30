'use strict';

const root = document.documentElement;
const themeButton = document.querySelector('.theme-toggle');
const preferredDark = window.matchMedia('(prefers-color-scheme: dark)');
let themeChoice = null;
try { themeChoice = localStorage.getItem('batten-site-theme'); } catch { /* Storage is optional. */ }
function setTheme(theme) {
  root.dataset.theme = theme;
  if (themeButton) {
    themeButton.setAttribute('aria-label', `Switch to ${theme === 'dark' ? 'light' : 'dark'} theme`);
    themeButton.setAttribute('aria-pressed', String(theme === 'dark'));
  }
}
setTheme(themeChoice || (preferredDark.matches ? 'dark' : 'light'));
themeButton?.addEventListener('click', () => {
  themeChoice = root.dataset.theme === 'dark' ? 'light' : 'dark';
  setTheme(themeChoice);
  try { localStorage.setItem('batten-site-theme', themeChoice); } catch { /* The view still works. */ }
});
preferredDark.addEventListener('change', event => {
  if (!themeChoice) setTheme(event.matches ? 'dark' : 'light');
});

const menuButton = document.querySelector('.menu-toggle');
const navigation = document.querySelector('#site-nav');
function closeMenu() {
  navigation?.classList.remove('open');
  menuButton?.setAttribute('aria-expanded', 'false');
}
menuButton?.addEventListener('click', () => {
  const open = menuButton.getAttribute('aria-expanded') !== 'true';
  menuButton.setAttribute('aria-expanded', String(open));
  navigation?.classList.toggle('open', open);
});
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && menuButton?.getAttribute('aria-expanded') === 'true') {
    closeMenu();
    menuButton.focus();
  }
});
navigation?.querySelectorAll('a').forEach(link => link.addEventListener('click', closeMenu));

const moduleNames = { tables: 'UMF + Weft', agents: 'Tether', ontology: 'Arras', ui: 'ux-builder', sagas: 'UMF sagas' };
const hostDescriptions = {
  local: ['LOCAL HOST', 'Develop with explicit local resources.', 'Fabricated identity · owned resources'],
  standalone: ['STANDALONE HOST', 'Own the service lifecycle.', 'Operator identity · explicit resources'],
  embedded: ['EMBEDDED HOST', 'Connect through the public host API.', 'Host identity · owned or borrowed services']
};
const selectedModules = new Set(['tables', 'agents', 'ui']);
let selectedHost = 'local';
const placement = document.querySelector('#placement');
function renderComposition() {
  const chips = document.querySelector('#capability-chips');
  if (!chips || !placement) return;
  chips.replaceChildren();
  const core = document.createElement('span');
  core.className = 'capability-chip core';
  core.textContent = 'Batten core';
  chips.append(core);
  Object.keys(moduleNames).filter(key => selectedModules.has(key)).forEach(key => {
    const chip = document.createElement('span');
    chip.className = 'capability-chip';
    chip.textContent = moduleNames[key];
    chips.append(chip);
  });
  const host = hostDescriptions[selectedHost];
  document.querySelector('#host-label').textContent = host[0];
  document.querySelector('#host-description').textContent = host[1];
  document.querySelector('#ownership-description').textContent = host[2];
  const placementName = placement.options[placement.selectedIndex].text.toLowerCase();
  const capabilities = selectedModules.size === 0 ? 'Core-only illustration' : `${selectedModules.size} optional ${selectedModules.size === 1 ? 'capability' : 'capabilities'} selected`;
  document.querySelector('#composition-summary').textContent = `${capabilities} · ${selectedHost} host · ${placementName}.`;
  const notes = ['Architecture illustration only; this does not run or assess an application.'];
  if (placement.value === 'remote-worker') notes.push('Remote workers require separately qualified transport and recovery.');
  if (selectedModules.has('sagas')) notes.push('Saga execution requires an exact qualified UMF executor.');
  if (!selectedModules.has('ui')) notes.push('Headless applications omit UI dependencies.');
  document.querySelector('#explorer-note').textContent = notes.join(' ');
}
document.querySelectorAll('[data-module]').forEach(button => {
  button.addEventListener('click', () => {
    const key = button.dataset.module;
    if (selectedModules.has(key)) selectedModules.delete(key);
    else selectedModules.add(key);
    button.setAttribute('aria-pressed', String(selectedModules.has(key)));
    renderComposition();
  });
});
document.querySelectorAll('[data-host]').forEach(button => {
  button.addEventListener('click', () => {
    selectedHost = button.dataset.host;
    document.querySelectorAll('[data-host]').forEach(item => item.setAttribute('aria-pressed', String(item === button)));
    renderComposition();
  });
});
placement?.addEventListener('change', renderComposition);
renderComposition();
