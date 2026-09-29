# Lane brief — `sgc-2` · T27: the set-planning system

**Program**: `species-gear-chain` (anchor `tasks/species-gear-chain-anchor.md`; todo
`tasks/species-gear-chain-todo.md`; ledger `tasks/species-gear-chain-ledger.jsonl`).
**Session id**: `sgc-2`. **Branch**: `cmdc/sgc-2`, cut from `features/mega-merge`.

## Why this lane exists

Task **T27** was `BLOCKED, owner ruling needed`. The owner ruled on **2026-09-21**: **build the
set-planning system** — do not drop `setClass`. The 2026-09-10 topology classes are the target, not a
dead design: their role-count shapes get authored into a real system, and the shipped sets are brought
onto it. `speciesId` is already built and proven; `setClass` is the half that was missing.

## Read before you write (binding — the design gate)

`docs/DESIGN-GATE.md` §1 for every subsystem you touch, then the documents its rows name, **in this
session**: `docs/architecture/species-gear-chain/spec-set-species-binding.md` (this task's spec — read
its Boundaries, its Ask list and its acceptance), `docs/architecture/item/ssot-sets.md`,
`docs/architecture/item/spec-set-charm-gen.md`, `docs/architecture/decisions.md`'s 2026-09-10
**Set topology classes** row, `docs/architecture/species-craft-ideal.md` (the design this came from),
and `PRINCIPLES.md`. Code beats docs; docs beat comments.

## Deliverable

The `setClass` / set-planning half of T27, in the spec's own terms:

1. **`S1` — spec revision first.** `spec-set-species-binding.md` still records `setClass` as an
   unanswered ask-first decision (`gk-forge/tools/seedsmith/seedsmith/adapters/items/setgen/seedfile.py:355-356`
   says exactly that in code). Revision it to the owner's ruling: the topology classes are adopted,
   their member-role counts and thresholds become versioned set-planning data, and the shipped sets are
   re-planned deterministically onto them. Answer the spec's own Ask at
   `docs/architecture/species-gear-chain/spec-set-species-binding.md:246` (the `build.*` / `theme.*`
   sets) from the class design rather than from convenience. **Commit S1 before you start S2.**
   Report the spec's resulting task list to the manager — rows are added by the manager, not invented
   by the lane.
2. **`S2` — the topology classes as data.** Versioned set-planning data (a new `gk-core/data/tuning/*.v1.json`
   or the registry the spec names), the loader, and a validator. No magnitude or threshold in code.
3. **`S3` — forward emission.** `set-charm-gen` emits `setClass` for newly generated entries, through
   the data from S2.
4. **`S4` — the shipped corpus, deterministically.** Every shipped set entry carries `speciesId` (a real
   id or an explicit absent) and `setClass`. **Never hand-edit generated seed data**: fix the generator,
   regenerate, commit the diff.

## Hard constraints

- **No magic numbers on the balance surface** — thresholds and role counts live in versioned tuning
  data (`gk-core/data/tuning/<domain>.v{n}.json`), published via `gk-core/tools/tuning/publish.py`, never in code.
- **Generated seed data is never hand-edited** — change the generator and regenerate.
- **H7**: a publish switches its readers in the same commit.
- **No hard progression ceilings**; an absolute bound is derived and throws, never clamps.
- `decisions.md` locks what it names; an architecture change that locks behaviour needs a decision
  first. If the spec and the code disagree, the code is the evidence and the spec is the defect to fix.

## Fence (`--allow`)

`gk-forge/tools/seedsmith/**`, `gk-data/packs/fusion/data/seed/items/**`, `gk-core/data/tuning/**`, `gk-data/packs/fusion/data/generated/**`,
`docs/architecture/species-gear-chain/**`, `docs/architecture/item/**`, `tests/**`, `tasks/**`.
Nothing under `src/**` — if the work appears to need it, **stop** and route the finding to the owning
program's todo instead of editing it.

## Verification

> **Runner note:** the runner takes the *first code span of each bullet in this section* as a
> verification command and runs it **verbatim** — a placeholder like `<every changed path>` is never
> substituted, so it is run as written and fails with a shell error. Each bullet below is therefore a
> real, substitution-free command; run the full `verify-change.ps1` yourself with your real changed
> paths and report the **numbers printed**, never the exit code alone (TVB-F3).

Run these and put their real output in the fragment:

- `$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests -q` — compare against the
  pre-existing failure baseline before you blame your change (some seedsmith tests fail on a clean HEAD).
- `dotnet run --project gk-forge/tools/ItemSeedValidator` — the corpus gate; must be green.
Boundary check -- run it yourself with your real changed paths (the runner cannot substitute a
placeholder, so this is deliberately not one of the bullets above), then report the numbers printed:

```powershell
./scripts/verify-change.ps1 -Paths <paths you changed> -Session sgc-2
```
- `python gk-core/scripts/anchor-ledger.py tasks/species-gear-chain-ledger.jsonl check` — must exit 0 after each
  ledger line you add.
- The spec's own acceptance lines for S1; each of S2–S4 carries its own focused command in the fragment.

## Evidence contract (binding)

One fragment per task at `tasks/evidence-fragments/<task-id>.md` with a table
`| Criterion | Command | Result | Artifact |`, the exact commands, the numbers printed, the committed
artifact, and an explicit **Not proved** list. Findings about files outside this fence go to the owning
program's todo as a row — a finding with no owning row is not delivered.

## Queue

`S1` spec revision → `S2` topology data → `S3` forward emission → `S4` corpus. One task = one commit.
