import { createOperationDescriptor, Environment, Network, RecordSource, Store } from "relay-runtime";
import type { ConcreteRequest } from "relay-runtime";
import list from "./__generated__/CommandListQuery.graphql";
import refetch from "./__generated__/CommandNodeQuery.graphql";
import complete from "./__generated__/CommandCompleteMutation.graphql";
import observe from "./__generated__/CommandObserveQuery.graphql";
import type { CommandListQuery } from "./__generated__/CommandListQuery.graphql";
import type { CommandNodeQuery } from "./__generated__/CommandNodeQuery.graphql";
import type { CommandCompleteMutation } from "./__generated__/CommandCompleteMutation.graphql";
import type { CommandObserveQuery } from "./__generated__/CommandObserveQuery.graphql";

function createEnvironment() {
  return new Environment({
    network: Network.create(async (params, variables) => {
      const api = document.querySelector('meta[name="lintel-api"]')?.getAttribute("content");
      if (!api || !params.text) throw new Error("missing build identity");
      const result = await fetch("/api/graphql", {
        method: "POST",
        headers: {"Content-Type":"application/json", "x-lintel-api":api},
        body: JSON.stringify({query: params.text, operationName: params.name, variables}),
      });
      const payload = await result.json();
      if (!result.ok || payload.errors) throw new Error(JSON.stringify(payload));
      return payload;
    }),
    store: new Store(new RecordSource()),
  });
}
let environment = createEnvironment();
function execute<Q extends {variables: object; response: unknown}>(
  operation: ConcreteRequest, variables: Q["variables"],
): Promise<Q["response"]> {
  const descriptor = createOperationDescriptor(operation, variables);
  const request = operation.params.operationKind === "mutation"
    ? environment.executeMutation({ operation: descriptor })
    : environment.execute({ operation: descriptor });
  return new Promise((resolve, reject) => {
    request.subscribe({next: payload => resolve(payload.data as Q["response"]), error: reject});
  });
}

const client = {
  login: async (actor: string) => {
    const response = await fetch("/api/local-session", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({actor}),
    });
    if (!response.ok) throw new Error("login refused");
    environment = createEnvironment();
  },
  list: (variables: CommandListQuery["variables"]) =>
    execute<CommandListQuery>(list, variables),
  refetch: (variables: CommandNodeQuery["variables"]) =>
    execute<CommandNodeQuery>(refetch, variables),
  complete: (variables: CommandCompleteMutation["variables"]) =>
    execute<CommandCompleteMutation>(complete, variables),
  observe: (variables: CommandObserveQuery["variables"]) =>
    execute<CommandObserveQuery>(observe, variables),
};
Object.assign(window, {client});
