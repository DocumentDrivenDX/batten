import {readFileSync} from 'node:fs';
import {relative} from 'node:path';
import {parseSync} from 'oxc-parser';

const configuration = new Set(['extend', 'describe', 'use', 'setTimeout', 'slow', 'info', 'step', 'beforeAll', 'afterAll', 'beforeEach', 'afterEach']);
const forbidden = new Set(['skip', 'only', 'fixme']);
function callPath(node) {
  if (!node) return '';
  if (node.type === 'Identifier') return node.name;
  if (node.type === 'MemberExpression') return `${callPath(node.object)}.${node.property.name ?? node.property.value}`;
  if (node.type === 'CallExpression') return callPath(node.callee);
  return '';
}
function bindingFor(node, bindings) {
  const path = callPath(node);
  return [...bindings].find(name => path === name || path.startsWith(name + '.')) ?? '';
}
function bindImport(binding, source, tests, assertions) {
  const imported = binding.imported?.name;
  if (['test', 'it'].includes(imported)) tests.add(binding.local.name);
  if (['expect', 'assert'].includes(imported) || source.startsWith('node:assert')) assertions.add(binding.local.name);
  const framework = ['@playwright/test', 'node:test', 'bun:test'].includes(source);
  if (framework && binding.type === 'ImportDefaultSpecifier') tests.add(binding.local.name);
  if (framework && binding.type === 'ImportNamespaceSpecifier') {
    for (const name of ['test', 'it']) tests.add(`${binding.local.name}.${name}`);
    assertions.add(`${binding.local.name}.expect`);
  }
}
function children(node) {
  return Object.values(node).flatMap(value => Array.isArray(value) ? value : [value]).filter(value => value && typeof value === 'object' && typeof value.type === 'string');
}
function isFunction(node) {return /Function(Expression|Declaration)$/.test(node.type) || node.type === 'ArrowFunctionExpression';}
function ownsAssertion(node, assertions) {
  return children(node).some(child => {
    if (isFunction(child)) return false;
    if (child.type === 'CallExpression' && bindingFor(child.callee, assertions)) return true;
    return ownsAssertion(child, assertions);
  });
}
function registration(node, tests, parent) {
  if (node.type !== 'CallExpression') return false;
  if (parent?.callee === node) return false;
  const binding = bindingFor(node.callee, tests);
  if (!binding) return false;
  const modifiers = callPath(node.callee).slice(binding.length).split('.');
  if (modifiers.some(name => forbidden.has(name))) throw new Error('disabled/focused test registration');
  return !modifiers.some(name => configuration.has(name));
}
function hiddenTest(node, canonical, assertions) {
  if (canonical || !isFunction(node)) return false;
  if (node.id?.name?.startsWith('test_')) return true;
  return ownsAssertion(node.body ?? node, assertions);
}
function bindAliases(node, tests, assertions) {
  if (node.type === 'VariableDeclarator' && node.id.type === 'Identifier') {
    if (bindingFor(node.init, tests)) tests.add(node.id.name);
    if (bindingFor(node.init, assertions)) assertions.add(node.id.name);
  }
  for (const child of children(node)) bindAliases(child, tests, assertions);
}
function inspect(path) {
  const source = readFileSync(path, 'utf8');
  const parsed = parseSync(path, source, {sourceType: 'module'});
  if (parsed.errors.length) throw new Error(`${path}: browser source parse failed: ${JSON.stringify(parsed.errors)}`);
  if (parsed.comments.some(comment => /(oxlint|eslint)-disable|@ts-ignore|@ts-nocheck/.test(comment.value))) throw new Error(`${path}: rule suppression`);
  const tests = new Set(['test', 'it']);
  const assertions = new Set(['expect', 'assert']);
  for (const node of parsed.program.body.filter(node => node.type === 'ImportDeclaration')) {
    for (const binding of node.specifiers) bindImport(binding, node.source.value, tests, assertions);
  }
  bindAliases(parsed.program, tests, assertions);
  const registrations = [];
  const hidden = [];
  function visit(node, canonical = false, parent = null) {
    const registered = registration(node, tests, parent);
    if (registered) registrations.push({file: relative(process.cwd(), path), line: source.slice(0, node.start).split('\n').length});
    if (hiddenTest(node, canonical, assertions)) hidden.push({file: relative(process.cwd(), path), name: node.id?.name ?? '<assertion helper>'});
    for (const child of children(node)) visit(child, canonical || registered, node);
  }
  visit(parsed.program);
  return {count: registrations.length + hidden.length, registrations, hidden};
}
const results = process.argv.slice(2).map(inspect);
process.stdout.write(JSON.stringify({count: results.reduce((sum, result) => sum + result.count, 0), registrations: results.flatMap(result => result.registrations), hidden: results.flatMap(result => result.hidden)}) + '\n');
