declare const graphql: (document: TemplateStringsArray) => unknown;
graphql`query CommandListQuery($first: Int!, $after: String) {
  tasks(first: $first, after: $after) {
    edges { cursor node { id title assignee { id displayName } } }
    pageInfo { endCursor hasNextPage hasPreviousPage }
  }
}`;
graphql`query CommandNodeQuery($id: ID!) {
  node(id: $id) { id ... on Task { title assignee { id displayName } } }
}`;
graphql`mutation CommandCompleteMutation($input: CompleteTaskInput!) {
  completeTask(input: $input) {
    __typename
    ... on CommandApplied { invocationKey durability receipt affectedIds }
    ... on CommandRejected { invocationKey code }
    ... on CommandUnknown { invocationKey }
  }
}`;
graphql`query CommandObserveQuery($input: ObserveCompleteTaskInput!) {
  observeCompleteTask(input: $input) {
    __typename
    ... on CommandRecovered { invocationKey durability receipt }
    ... on CommandNotObserved { invocationKey }
  }
}`;
