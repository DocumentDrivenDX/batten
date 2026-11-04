import {spawn, execFile, type ChildProcess} from 'node:child_process';
import {promisify} from 'node:util';
import {mkdtempSync, readFileSync, writeFileSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {resolve, join, dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createServer} from 'node:net';
import {createInterface} from 'node:readline';

const execute = promisify(execFile);
const root = resolve(dirname(fileURLToPath(import.meta.url)), '../..');

export class AppHost {
  private process: ChildProcess | null = null;
  readonly data: string;
  readonly config: string;
  readonly python = join(root, '.cache/approval-runtime/bin/python');
  constructor(readonly workspace: string, readonly url: string, port: number) {
    this.data = join(workspace, 'data');
    this.config = join(workspace, 'local.toml');
    writeFileSync(this.config, readFileSync(join(root, 'examples/approval-desk/local.toml'), 'utf8').replace('port = 8820', `port = ${port}`));
  }
  static async create(): Promise<AppHost> {
    const listener = createServer();
    await new Promise<void>(done => listener.listen(0, '127.0.0.1', done));
    const address = listener.address();
    if (!address || typeof address === 'string') throw new Error('missing allocated port');
    const port = address.port;
    await new Promise<void>(done => listener.close(() => done()));
    const app = new AppHost(mkdtempSync(join(tmpdir(), 'batten-browser-')), `http://127.0.0.1:${port}`, port);
    await app.command('init');
    await app.start();
    return app;
  }
  async command(command: string, ...args: string[]): Promise<string> {
    const result = await execute(this.python, ['-I', '-m', 'approval_desk.cli', command, '--data', this.data, '--config', this.config, ...args], {cwd: this.workspace, encoding: 'utf8', timeout: 300_000, maxBuffer: 1024 * 1024});
    return result.stdout;
  }
  async start(): Promise<void> {
    const child = spawn(this.python, ['-I', '-m', 'approval_desk.cli', 'serve', '--data', this.data, '--config', this.config], {cwd: this.workspace, stdio: ['ignore', 'pipe', 'pipe']});
    this.process = child;
    await new Promise<void>((done, reject) => {
      const logs: string[] = [];
      const lines = createInterface({input: child.stdout!});
      const finish = (error?: Error): void => {
        clearTimeout(timer);
        lines.close();
        child.off('exit', exited);
        if (error) reject(error); else done();
      };
      const exited = (): void => finish(new Error(logs.join('\n')));
      const timer = setTimeout(() => {child.kill('SIGKILL'); finish(new Error(`host readiness timeout: ${logs.join('\n')}`));}, 90_000);
      child.stderr!.on('data', chunk => logs.push(String(chunk)));
      child.once('exit', exited);
      child.once('error', finish);
      lines.on('line', line => {
        logs.push(line);
        if (line.startsWith('{') && JSON.parse(line).ready) finish();
      });
    });
  }
  async stop(): Promise<void> {
    const child = this.process;
    if (!child || child.exitCode !== null || child.signalCode !== null) return;
    await new Promise<void>((done, reject) => {
      const timer = setTimeout(() => {child.kill('SIGKILL'); reject(new Error('host stop timeout'));}, 45_000);
      child.once('exit', () => {clearTimeout(timer); done();});
      child.kill('SIGINT');
    });
    this.process = null;
  }
  async revokeReviewer(): Promise<void> {
    await execute(join(root, '.venv/bin/python'), [join(root, 'tests/apps/native_probe.py'), this.data], {encoding: 'utf8', timeout: 90_000});
  }
  setHead(digest: string): string {
    const path = join(this.data, 'deployment.json');
    const metadata = JSON.parse(readFileSync(path, 'utf8'));
    const previous = metadata.reference.headDigest as string;
    metadata.reference.headDigest = digest;
    writeFileSync(path, JSON.stringify(metadata));
    return previous;
  }
  capture(name: string): string {return readFileSync(join(this.data, name), 'utf8');}
}
