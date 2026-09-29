# SSH1.6 — `host-gate` f: harden the craft path's role ceiling

Task: tasks/strain-splice-host-todo.md SSH1.6 · spec: docs/architecture/strain-splice-host/spec-host-gate.md §5

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `BaseTypeSocketMaxCorpus.Load` runs `SocketGeometry.ValidateEntry` per row; a corrupt row returns `null`, the workbench refuses with `socket.base-type-socket-max-unavailable` | `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~BaseTypeSocketMaxCorpus"` | exit=0 :: 3 passed, incl. `A_base_row_above_its_role_ceiling_is_refused_at_load` | `WorkbenchEndpoints.cs`, `BaseTypeSocketMaxCorpusTests.cs` |
| No new rule id, no role branch, no `TryAdd` overload | read the diff | confirmed: reuses `SocketRules.EntryExceedsRoleCeiling` via the existing `SocketGeometry.ValidateEntry`; the loop is generic over `role`; `byId[id] = socketMax` unchanged | `WorkbenchEndpoints.cs` |
| `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~ItemWorkbenchEndpoints"` | same | exit=0 :: 59 passed | — |
| Full Server.Tests (production wiring change — `Program.cs`'s own boot path) | `dotnet test gk-core/tests/FusionRpg.Server.Tests -c Release` | exit=0 :: 656/656 | — |
| Audits | `audit-overflow.py`/`audit-magic-numbers.py --targets <3 files>` | both clean | — |

## The fix

`BaseTypeSocketMaxCorpus.Load` previously read only `id`/`socketMax` off each JSON row and trusted
`socketMax` unconditionally — the corpus validator (`gk-forge/tools/ItemSeedValidator/Checks/SocketMaxCheck.cs`)
already refuses a role-ceiling violation at AUTHORING time, but nothing stopped a hand-edited or
corrupted row from reaching the runtime lookup regardless. `Load` now also reads `role`, parses it, and
calls the SAME `SocketGeometry.ValidateEntry(role, socketMax, tuning)` the corpus validator's own rule
is built on; a row that fails (bad role string, or `socketMax` above that role's ceiling) is dropped
from the dictionary — the lookup then returns `null` for that id exactly as it already does for an id
the corpus never carried, and the workbench's existing `socket.base-type-socket-max-unavailable`
refusal (unchanged, `ItemWorkbench.cs:979`) covers it. `Load` gained one new parameter, `SocketTuning
tuning` — its one production call site (`Program.cs`) already had a `socketTuning` instance in scope
from earlier boot wiring, so the change is a one-line addition there.

## No downstream break, proven at scale

The full, real 740-entry shipped base-type corpus loads through this exact path at Server boot
(`Program.cs`'s own workbench wiring) and the FULL Server.Tests suite — 656 tests, everything that
exercises the workbench, item cards, or sockets — stays green: the real corpus has no row that violates
its own role's ceiling today, so this hardening changes nothing observable for real content, only for a
corrupt one.

## Status

Both SSH1.6 acceptance criteria met. Ledger marked done; todo checkbox ticked. **This closes Wave 1
(host-gate) — Checkpoint 1's own four boxes are now all backed by a passing test.**
