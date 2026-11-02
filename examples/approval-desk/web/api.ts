export type Actor = {id: string; name: string; can_review: boolean};
export type RequestRecord = {id: string; owner: string; title: string; state: string; revision: string; decided_by: string};
export type Call = {operation: string; inputs: Record<string, string>; key?: string};
export type Outcome = {status: string; invocation?: string; result?: {rows?: RequestRecord[]; cursor?: string | null; recovered?: boolean}; code?: string};

export async function session(): Promise<Actor | null> {
  const response = await fetch('./api/session', {cache: 'no-store'});
  if (!response.ok) throw new Error('Session unavailable.');
  return (await response.json()).actor;
}

export async function login(actor: string): Promise<void> {
  const response = await fetch('./api/local-session', {method: 'POST', headers: {'content-type': 'application/json'}, body: JSON.stringify({actor})});
  if (!response.ok) throw new Error('This local identity is unavailable.');
}

export async function invoke(call: Call, phase = 'invoke'): Promise<Outcome> {
  const response = await fetch('./api/operations/' + encodeURIComponent(call.operation), {
    method: 'POST', headers: {'content-type': 'application/json'},
    body: JSON.stringify({inputs: call.inputs, ...(call.key ? {key: call.key} : {}), phase}),
  });
  const outcome: Outcome = await response.json();
  if (!outcome.status) throw new Error('The host did not return a usable outcome.');
  return outcome;
}
