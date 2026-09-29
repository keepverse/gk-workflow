# Lane brief — `combat-ai-2` · the combat-AI program, wave 1 tail into wave 2

**Program**: `combat-ai` (anchor `tasks/combat-ai-anchor.md`; plan `tasks/combat-ai-plan.md`; todo
`tasks/combat-ai-todo.md`; ledger `tasks/combat-ai-ledger.jsonl`; map `docs/architecture/combat-ai-map.md`).
**Session id**: `combat-ai-20260920`. **Branch**: `cmdc/combat-ai-2`, cut from `features/mega-merge`.

## Why this lane exists

The program's first lane ran three slices and is terminal-partial. Its work is merged
(`b19c9460` CAI1.11, `c3bb0ba2` CAI1.12 Core half, `98e20e10` CAI1.13, `d936830d` CAI1.14 slice 2,
`9fcfbba6` CAI1.12 injector half via `cai-sink`), but **three wave-1 rows are still open** and wave 2
has not started. This lane finishes the tail in the todo's own order and then takes wave 2.

## Your slice, in this order

1. **CAI1.12 — `resolvable-here`: the per-place executor allowlist.** Core half (`c3bb0ba2`) and the
   injector half (`9fcfbba6`) are landed. Read the row (`tasks/combat-ai-todo.md`, search `CAI1.12`)
   and its fragments (`tasks/evidence-fragments/CAI1.12*.md`) before you write anything: the row
   still carries the lawn half and an erratum asking for the acceptance line that forbids a tuning
   file naming an opcode (`No_file_under_data_tuning_names_an_opcode`). Close what is genuinely
   outstanding; if the row is already complete in code, say so with file:line evidence and close it
   as an erratum rather than inventing work.
2. **CAI1.14 — `decision-perf`.** Sites 1 and 2 are landed (`CostLedger.RowsFor` zero-alloc;
   `CandidateScorer.TopThreeInto` + `CostLedger.TryPay` scratch-buffer reuse). The row is `L`: read
   it for the remaining allocation sites and the O(n²) cap, and take them one commit each. The
   channel-id interning half was filed to `tasks/derived-stats-todo.md` — leave it there.
3. **CAI1.15 — propagate the program into the index documents (PARTIAL).** Two edits remain and both
   are in your fence: `docs/DESIGN-GATE.md:56` and `docs/architecture/combat-ai-ideal.md:129`. Read
   `docs/architecture/combat-ai-ideal.md` for what the design gate row must name, then make those two
   edits the row describes — nothing more.
4. **Then wave 2 in todo order**: CAI2.1 `replay-identity` A, CAI2.2 B, CAI2.3 `action-schedule-twin`,
   CAI2.4/2.5 `decision-inspector`. One row = one commit = one fragment; stop at the segment boundary.

## Read before you write (binding — the design gate)

`docs/DESIGN-GATE.md` §1 for every subsystem you touch, then the documents its rows name, **in this
session**: `docs/architecture/combat-ai-ideal.md`, `docs/architecture/combat-ai/**` for the module the
row names, `docs/architecture/decisions.md` for the locks the program cites, and `PRINCIPLES.md`.
Code beats docs; docs beat comments.

## Hard edges you must respect

- **H1 — golden re-bless order.** Battle goldens are unmoved and unblessed unless a row names the move.
  If a golden moves, one cause per commit, and the fragment records the cause.
- **H7 — a publish switches its readers in the same commit.** `combat-ai.v1.json` / `siege.v2.json`
  and their readers move together.
- **CAI-guard-1 is NOT yours.** The pinned `BattleEffects.cs` baseline in
  `gk-core/tests/FusionRpg.Guard.Tests/PlantSideStatusGuardTests.cs` was re-pinned by an executor ruling that
  routed the re-pin to `tvb58`. Do not touch that pin; if your work moves it again, say so in the
  fragment and open a row.
- **Never widen a guard's allowlist to make a test pass**, and never add a `knownRed` entry — those
  registrations belong to the `test-verification-boundary` program.
- **Injector builds need both env vars** or the 3.8.1 bridge compiles against 3.9 interop:
  `$env:FUSIONRPG_ML_GAMEDIR = "H:\Games\PVZ-Fusion-3.9_MelonLoader"` and
  `$env:FUSIONRPG_GAME_PROFILE = "pvzrh-3.9"`, then
  `dotnet build gk-fusion/src/FusionRpg.Injector.MelonLoader/FusionRpg.Injector.MelonLoader.csproj -c Release`.
- **Findings route out, code stays in.** A finding outside your fence becomes a row in the OWNING
  program's todo in the same commit as the fragment that reports it; you never edit another program's
  files to fix it.

## Verification

> **Runner note:** the runner takes the *first code span of each bullet in this section* as a
> verification command and runs it **verbatim** — a placeholder like `<every changed path>` is never
> substituted, so it is run as written and fails with a shell error. Each bullet below is therefore a
> real, substitution-free command; run the full `verify-change.ps1` yourself with your real changed
> paths and report the **numbers printed**, never the exit code alone (TVB-F3).

Run these and put their real output in the fragment:

Boundary check -- run it yourself with your real changed paths (the runner cannot substitute a
placeholder, so this is deliberately not one of the bullets above), then report the numbers printed:

```powershell
./scripts/verify-change.ps1 -Paths <paths you changed> -Session combat-ai-20260920
```
  path-owned boundary. Never the full suite: that belongs to CC8 or this program's final checkpoint.
- `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Battle"` and, when the row
  touches scoring, `--filter "FullyQualifiedName~Ai"` — report the numbers printed, not a summary.
- `dotnet test gk-core/tests/FusionRpg.Guard.Tests` — 4 tests are red at HEAD for known, registered reasons
  owned by other programs; name them as pre-existing instead of fixing them.
- `pwsh -NoProfile -File scripts/guard-actor-hub.ps1` when you touch anything that composes actor
  stats; `python gk-core/scripts/anchor-ledger.py tasks/combat-ai-ledger.jsonl check` after every ledger line
  (must exit 0).
- The row's own Verify line — each row carries one, and it is the acceptance you are held to.

## Evidence contract (binding)

One task = one commit. Each task writes `tasks/evidence-fragments/<task-id>.md` with a
`| Criterion | Command | Result | Artifact |` table whose Result column carries the printed numbers,
an explicit **NOT proved** list, and any finding routed to its owning todo. Append one ledger line
through the script (`anchor-ledger.py … note` — keep notes under 280 characters). Report the tip SHA
and the list of paths you changed when you stop. Never claim a check you did not run; a check you
could not run is reported as not run, with the reason.
