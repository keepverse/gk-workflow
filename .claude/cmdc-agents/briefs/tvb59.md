# Lane brief — `tvb59` · test-verification-boundary, the analyzer and registry half

**Program**: `test-verification-boundary` (anchor `tasks/test-verification-boundary-anchor.md`; todo
`tasks/test-verification-boundary-todo.md`; ledger `tasks/test-verification-boundary-ledger.jsonl`).
**Session id**: `test-verification-boundary-2`. **Branch**: `cmdc/tvb59`, cut from `features/mega-merge`.

## Why a second lane in this program, and how it avoids colliding with `tvb58`

`tvb58` owns the **test-project split chain** (`TVB5.7`, `TVB5.8.k`, `TVB5.9`): each increment creates a
per-area test project under `tests/**` and wires it into `FusionRpg.slnx` and `.github/workflows/ci.yml`.
That chain must stay single-writer, so **your fence excludes `tests/**`, `FusionRpg.slnx` and
`.github/workflows/**`** — you never touch the split.

Your half is the **analyzer, the verification registry and the docs**:

- **`TVB4.7`** — map `gk-data/packs/fusion/data/seed/**`; switch the seam on; doc paragraph (spec `seam-coverage` S2 row 4).
- **`TVB6.1`** — Analyzer `--production-map`.
- **`TVB6.2`** — K1: per-area Core production owners derived from the production map.
- **`TVB6.3`** — K2: re-key the existing focused `core.*` boundaries.
- **`TVB6.4`** — K3: orphan `core.*` traits + the ideal line.
- **`TVB6.5`** — reading: `Core/Stats` + `Core/Effects` production paths still plan `core-fallback`.

Also yours, and the reason this lane is worth the 8th slot: **`TVB-F13`'s Guard-suite re-measure** is already
done by `tvb58` (1 failed / 579 passed / 580 at the merged head), so do not re-run it; but the **`doc-citations`
guard red** currently standing at the head is *not* yours either (routed to trade-network, npc-story-events and
world-stage) — leave those rows alone.

## Hard edges

- **The registry is append-mostly and shared.** `gk-core/scripts/verification-boundaries.v1.json` is edited by other
  programs too (owner rows for new tuning/generated files). Keep your changes additive and ordered; if a
  merge conflicts, resolve by **union**, never by dropping another program's row.
- **`gk-core/data/tuning/**`, `gk-data/packs/fusion/data/generated/**` and `gk-core/tests/fixtures/**` are `EnforcedRoots`**: every file under them
  must resolve to an owner row, and `gk-core/scripts/guard-verification-boundaries.py` fails otherwise. When you map
  `gk-data/packs/fusion/data/seed/**` (TVB4.7) say explicitly in the fragment which paths are enforced today and which are not —
  do not widen enforcement silently.
- **A guardrail validates the CONTRACT and closed enums, never a population count or generated text**
  (`docs/architecture/validation-ssot.md`). If a change seems to need "assert N rows exist", it is the wrong
  change.
- **Never widen a guard's allowlist to make a test pass, and never add a `knownRed` entry** — registrations
  are this program's *deliberate* decisions and need their own row, not a drive-by edit.
- `gk-core/tests/FusionRpg.Guard.Tests/**` is a **protected** path; `tvb58` holds `--allow-protected` for it. If a
  guard needs editing, say so in the fragment and route it rather than reaching for it.
- **Findings route out**; code stays in.

## Verification

Put the printed numbers in each fragment:

- `python gk-core/scripts/guard-verification-boundaries.py` (must print OK) and, when the registry
  changes, `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~VerificationBoundary|FullyQualifiedName~EnforcementRegistry"` — both are load-fragile, so re-run a red alone before believing it.
- `python gk-core/scripts/anchor-ledger.py tasks/test-verification-boundary-ledger.jsonl check` after every ledger line.
- `.\scripts\verify-change.ps1 -Paths <your real changed paths> -Session test-verification-boundary-2` — run
  it yourself and read the **numbers printed**, never the exit code alone (TVB-F3).

## Evidence contract (binding)

One fragment per task at `tasks/evidence-fragments/<task-id>.md` with
`| Criterion | Command | Result | Artifact |`, the exact commands, the numbers printed, the committed
artefact, an explicit **Not proved** list, and every finding routed to its owning row in the same commit.
