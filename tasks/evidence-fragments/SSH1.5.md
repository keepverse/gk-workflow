# SSH1.5 — `host-gate` e: ruling 3 plus the R11 derivation, on both ports

Task: tasks/strain-splice-host-todo.md SSH1.5 · spec: docs/architecture/strain-splice-host/spec-host-gate.md §4 row 3

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `no_socket_path_branches_on_head_guard`: source scan of `gk-core/src/FusionRpg.Core/Items/Sockets/**` and the workbench finds no `HeadGuard`/`head-guard` outside the role table | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~SocketGeometry"` | exit=0 :: 26 passed | `SocketGeometryTests.cs` |
| `a_role_hosts_a_word_iff_its_ceiling_reaches_the_ingredient_count`: fixture `head-guard` 3 -> 4 moves the helm, no code change | same | passed (C#); `test_a_role_hosts_a_word_iff_its_ceiling_reaches_the_ingredient_count` passed (Python) | `SocketGeometryTests.cs`, `test_strain_splice_gen.py` |
| `a_helm_host_is_admitted_by_the_one_matcher_at_four_sockets`: capacity 4 -> `CanEverHold` true; capacity 3 -> false | same | passed | `SocketGeometryTests.cs` |
| `$env:PYTHONPATH="gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py -q` | same | exit=0 :: 56 passed | — |
| Audits | `audit-overflow.py`/`audit-magic-numbers.py --targets <file>` | clean | — |
| `guard-population-pin.py --summary` | same | 0/0/0 (still clean after these edits) | — |

## Ruling 3, proven as an absence and a derivation

`SocketGeometry.RolesThatCanHostAStrain` and Python's `ComboTuning.host_roles()` were ALREADY fully
derived (`ceiling >= ingredientCount`, no hardcoded role) — confirmed by reading both before writing
anything, and `HeadGuard`/`head-guard` appears nowhere in `gk-core/src/FusionRpg.Core/Items/Sockets/**` or the
workbench today. What was missing was the ENFORCEMENT: a source-scan regression guard (so a future
edit cannot special-case the helm), and a property test proving the rule is genuinely dynamic rather
than coincidentally matching today's shipped list. The property test moves ONLY `head-guard`'s own
ceiling in a fixture (3 -> 4, R11's real upcoming change) and shows the helm crossing in and out of
`RolesThatCanHostAStrain`/`host_roles()` with **no code change between the two `Parse`/`load()`
calls** — the C# and Python halves of the identical claim, both against the real shipped
`sockets.v1.json` mutated by string/dict replacement, matching this file's own established fixture
style (`A_ceiling_above_the_structural_maximum_throws_rather_than_clamping` and siblings).

`A_helm_host_is_admitted_by_the_one_matcher_at_four_sockets` is `ComboMatcher.CanEverHold`'s own
capacity-vs-role check (SSH1.3), read against a `HeadGuard`-role host: capacity 4 admits a
4-`MinSockets` recipe, capacity 3 does not — the same matcher SSH1.1 unified, now proven for the
specific role R11 will widen.

## Verification-boundary gap (same one named in SSH1.4)

`test_strain_splice_gen.py` still has no owner mapping in `gk-core/scripts/verification-boundaries.v1.json` --
`verify-change.ps1` refuses it outright, unchanged from SSH1.4's own finding. Verified directly via
`pytest` (56/56, above); `verify-change.ps1` run for the C# file it can resolve.

## Status

All SSH1.5 acceptance criteria met. Ledger marked done; todo checkbox ticked.
