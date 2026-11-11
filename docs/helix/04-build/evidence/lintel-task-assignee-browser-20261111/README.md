# Task-board assignee expansion and command recovery

The admitted Batten endpoint ran Lintel prepared API /5 on PostgreSQL 18.6.
Relay 21.0.1 compiled four TypeScript operations from the admitted SDL.
Strict TypeScript checking passed and Relay Runtime 21.0.1 executed the
operations in Chromium 153.0.8010.12.

The first page returned a Task with its visible Person assignee. The second
page returned two tasks and used one relationship batch. The assignee hidden
by PostgreSQL row policy was null and the visible assignee was returned. Node
refetch preserved both Task and assignee identities. The client received a
typed confirmation refusal before the approved mutation. The test dropped the
successful HTTP response, then the observation query returned the same
committed receipt. Refetch showed the update and the other principal could
observe neither the receipt nor the Task. One approved mutation ran and all
21 leases were returned.

Batten joins the selected relationship to its verified native binding. It
reads authorized parents and authorized targets through the generated key
batch executor in the same request snapshot. Target keys are used internally
and only the selected authorized target fields are returned. The verified
database fixture has a required foreign key. It exercises policy-hidden
assignees but does not qualify physically unassigned tasks or optional
foreign keys. This is local source composition evidence.

[Receipt](receipt.json) · [Prepared API](prepared-api.json) ·
[UMF fixture](fixture.umf.json) · [Relay source](relay-source/)

The retained runner files document the exact verification. To replay in a
scratch directory, copy the three Python text files as `browser_check.py`,
`board_fixture.py` and `build_check.py`. Copy Lintel's S-02 native
`fixture.py` alongside them. Point `board_fixture.py` at the retained
`fixture-inputs` directory, copy `relay-source` to `client`, and create
`client/src/__generated__` and `assets`. Link `client/node_modules` to the
Batten build dependencies. Run with the matching UMF Build and PostgreSQL
runtime cohort and the local Batten, Lintel and UMF source packages on the
Python path. The runner stops its disposable PostgreSQL cluster on exit.
