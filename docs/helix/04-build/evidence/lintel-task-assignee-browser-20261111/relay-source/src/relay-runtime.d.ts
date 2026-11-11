declare module "relay-runtime" {
  export interface ConcreteRequest {
    params: { name: string; text: string | null; operationKind: string };
  }
  export interface OperationDescriptor {}
  export interface NetworkLayer {}
  interface RecordSource {}
  interface Store {}
  export const RecordSource: { new(): RecordSource };
  export const Store: { new(source: RecordSource): Store };
  export const Network: {
    create(fetch: (params: ConcreteRequest["params"], variables: object) => Promise<object>): NetworkLayer;
  };
  export class Environment {
    constructor(config: { network: NetworkLayer; store: Store });
    execute(config: { operation: OperationDescriptor }): Observable;
    executeMutation(config: { operation: OperationDescriptor }): Observable;
  }
  export function createOperationDescriptor(
    operation: ConcreteRequest, variables: object,
  ): OperationDescriptor;
  interface Observable {
    subscribe(observer: {
      next(payload: { data?: unknown; errors?: unknown }): void;
      error(error: unknown): void;
    }): void;
  }
}
