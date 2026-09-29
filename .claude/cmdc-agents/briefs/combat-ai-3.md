# Lane brief — `combat-ai-3` · the combat-AI program, taken over from a drained lane

**Program**: `combat-ai` (anchor `tasks/combat-ai-anchor.md`; plan `tasks/combat-ai-plan.md`; todo
`tasks/combat-ai-todo.md`; ledger `tasks/combat-ai-ledger.jsonl`; map `docs/architecture/combat-ai-map.md`).
**Session id**: `combat-ai-3`. **Branch**: `cmdc/combat-ai-3`, cut from `features/mega-merge`.

## Why this lane exists (and why not `combat-ai-2`)

`combat-ai-2` did real work — its last merge (`65cf80ee`, reviewed `ebfd12ac`) carried CAI3.1 slice 4, the
CAI2.6 evidence/cross-reference commits and the `CAI-guard-2` fix (the two CI-tier guard reds that were this
program's own files: `CoreIntentPolicy.cs:76-77` bare literals and the `DecisionAllocationTests.cs:400`
population pin) — but it is now **drained**: each `continue` makes it start, spend `input 587 / output 3`
tokens, and exit with `exitCodes [0,0,0]`. It cannot carry the program's remaining rows.

⚠ **Do not touch `.claude/worktrees/cmdc-combat-ai-2` or its branch.** You work in your own worktree.

## The program's remaining work (40 open checklist lines in `tasks/combat-ai-todo.md`)

Take them in the todo's own order, worst-first, reading each row's own Acceptance/Verify lines. The
headline rows (verify their current state before assuming):

- `CAI-guard-1`'s re-pin rides **`tvb58`** (executor ruling: Guard files are a protected path) — **not
  yours**, do not touch `gk-core/tests/FusionRpg.Guard.Tests/**`.
- The siege-suite and `combat-ai.v1.json` / `siege.v2.json` rows whose acceptance lines still stand
  (`AiScoring` in exactly one place; the DESIGN-GATE row; goldens unmoved except CAI1.5/CAI1.11's named
  ones; `audit-overflow.py --targets A3` and `audit-magic-numbers.py --summary` gaining no
  `Actions/Ai/` row).
- Rows whose *executor half* sits outside the fence: the parity test / projection / dominance run, and the
  injector half (a denied path). Route those as rows in the owning program's todo rather than reaching for
  them.

## Hard edges

- **H1 — golden re-bless order.** Battle goldens are unmoved and unblessed unless a row names the move; if a
  golden moves, one cause per commit and the fragment records the cause.
- **H7 — a publish switches its readers in the same commit** (`combat-ai.v1.json`, `siege.v2.json`).
- **Never widen a guard's allowlist to make a test pass, and never add a `knownRed` entry** — those
  registrations belong to `test-verification-boundary`.
- **Injector builds need both env vars** or the bridge compiles against the wrong interop:
  `$env:FUSIONRPG_ML_GAMEDIR = "H:\Games\PVZ-Fusion-3.9_MelonLoader"` and
  `$env:FUSIONRPG_GAME_PROFILE = "pvzrh-3.9"`, then
  `dotnet build gk-fusion/src/FusionRpg.Injector.MelonLoader/FusionRpg.Injector.MelonLoader.csproj -c Release`.
- **The Core test project was split** (lane `tvb58`, merged): `gk-core/tests/FusionRpg.Core.Tests/**` is now several
  per-area projects (`gk-core/tests/FusionRpg.Core.Balance.Tests/**`, `...Core.Aura.Tests`, `...Core.ClassSystem.Tests`,
  `...Core.CapPolicyTests.Tests`, …). Put a test where its subject lives, and check the project you add it to
  is wired in `FusionRpg.slnx` + `.github/workflows/ci.yml` (`CiWiringGuardTests` enforces that).
- **Findings route out; code stays in.** A finding outside your fence becomes a row in the OWNING program's
  todo in the same commit as the fragment that reports it.

## Verification

Put the printed numbers in each fragment:

- `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Ai"` (the program's main suite) —
  and the per-area project when the row's file moved there.
- `dotnet test gk-core/tests/FusionRpg.Guard.Tests` — reds here are load-fragile or other programs'; name them
  rather than fixing them (`CAI-guard-1` is `tvb58`'s).
- `pwsh -NoProfile -File scripts/guard-actor-hub.ps1` when a change touches stat composition.
- `python gk-core/scripts/anchor-ledger.py tasks/combat-ai-ledger.jsonl check` after every ledger line.
- `.\scripts\verify-change.ps1 -Paths <your real changed paths> -Session combat-ai-3` — run it yourself;
  read the **numbers printed**, never the exit code alone (TVB-F3).

## Evidence contract (binding)

One fragment per task at `tasks/evidence-fragments/<task-id>.md` with
`| Criterion | Command | Result | Artifact |`, the exact commands, the numbers printed, the committed
artefact, an explicit **Not proved** list, and every finding routed to its owning row in the same commit.
