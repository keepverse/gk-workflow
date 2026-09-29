# SSH2.5 — The widened `--retry-blocked` re-run (strain + splice)

Was OWNER-RUN (spends model calls); owner authorised agent-run local generation 2026-09-20 via
LM Studio, model `google/gemma-4-26b-a4b-qat` ONLY.

## Model verification (before every batch, per the coordinator's own instruction)

Before each of the 8 real generation calls below, verified via a direct `curl` to
`http://localhost:1234/v1/chat/completions` that the response's own `"model"` AND
`"system_fingerprint"` fields both read exactly `google/gemma-4-26b-a4b-qat` (LM Studio's
`/v1/models` also serves a 31b build and several "uncensored"/"heretic" variants — never used).
Config: `tools/seedsmith/.env` created from `.env.example` verbatim (gitignored, confirmed via
`git check-ignore`), naming that exact model and endpoint.

## Order of operations

1. `python -m seedsmith items validate --deps` — `refused: false`, `reasons: []`, `grantsChecked:
   105` (grown since SSH2.1's own snapshot as the atom corpus keeps growing under concurrent lane
   work — expected).
2. Dry-run both shapes with `--retry-blocked` to size the work: strain 11/36 needing, splice 15/66
   needing (11+15=26, matching the spec's own "26 of 102 blocked" figure exactly).
3. **Finding on `--limit`:** a `--limit N` batch combined with `--retry-blocked` does NOT partition
   work across separate invocations — every currently-`blocked` subject is re-offered on EVERY
   `--retry-blocked` call (by design: blocked stays blocked until a different answer lands), so
   `--limit` just re-attempts the same early-grid-order cells repeatedly rather than advancing
   through a stable subset. Confirmed empirically (batch 1 `--limit 3` and batch 2 `--limit 4`
   shared 3 of their 4 subject ids). Switched to running each shape's FULL `--retry-blocked --write`
   in one call instead (no `--limit`), matching the spec's own literal Commands block, and treated
   "small batches" as "one pass per shape, repeated until it stops making progress."
4. Ran 4 real rounds per shape (strain: 11→8→5→5 blocked; splice: 15→9→5→2→2 blocked), each preceded
   by a fresh model-identity check, each round 2+ labeled via `--retry-label roundN` so the R13
   report's `survivedReruns` history is real. Stopped once a round produced 0 new persists on both
   shapes (round 3 for strain, round 4 for splice) — genuine convergence, not an arbitrary cutoff.

## Before / after numbers

| | before | after |
|---|---|---|
| strains.json entries | 25 | 31 |
| splices.json entries | 51 | 64 |
| total real combinations | 76 | 95 |
| still-blocked (R13) | 26 | 7 (5 strain, 2 splice) |
| grid total (real + blocked) | 102 | 102 |

Every one of the 102 grid cells is now either a real `entry` in `strains.json`/`splices.json` or
listed by id in `combination-still-blocked.json` (R13) — the acceptance criterion's own wording,
verified by direct count, not assumed.

## Verification

- `python -m seedsmith check ../../data/seed/items --adapter items --gate --metric
  Registration/IngredientUnsatisfiable` (SSH2.5's own named metric) — **no findings, exit 0.**
- `python -m seedsmith check ../../data/seed/items --adapter items --gate` (unscoped) — exit 1, but
  the ONLY gating metric with a gap is `Linkage/SetCompletability` (30 gaps, all on `set.*` entries
  about `head-guard`/`sense` roles outside the hybrid core) — confirmed via `git status` that this
  session touched NOTHING under `gk-data/packs/fusion/data/seed/items/` except `combinations/`, so this is real,
  pre-existing, unrelated corpus drift, not something this task caused or is scoped to fix.
- `dotnet run --project gk-forge/tools/ItemSeedValidator` — see "Two real findings" below; both pre-exist
  this task's own file-level cause, one is newly measured here for the first time.

## Two real findings surfaced by this run (neither hand-fixed — see why below)

### 1. Ten combination entries' names were already desynced between the ledger and the seed file

`git log` shows `gk-data/packs/fusion/data/seed/items/combinations/strains.json`/`splices.json` were last touched by
`fae533a519` ("fix(items): clear every name/nameKey collision, 848 findings -> 0", 2026-09-13) —
which renamed 10 combination entries directly in the SEED FILE (e.g. `combo.strain-focus-defense`:
"Stilled Pulse" -> "Iron Cadence", `nameKey` `combination.strain-focus-defense` ->
`combination.iron-cadence`) but did **not** touch `combination-gen.ledger.json` (its own last touch
predates `fae533a519`). `authored.run_batch`'s own documented contract (`entries_from_ledger`) is
that the WRITTEN FILE always reflects EVERY entry the ledger currently holds, full rewrite, every
run — by design, so an interrupted run never loses already-completed work. My very first `--write`
call for each shape therefore rewrote the WHOLE file from the ledger's own (pre-`fae533a519`)
content, which silently reverted all 10 of that commit's renames back to their original,
collision-prone names ("Iron Cadence" -> "Stilled Pulse", etc.) — none of these 10 ids were even in
my own retry-blocked batches; they were already `persisted` and untouched by `--retry-blocked`'s own
selection, but `entries_from_ledger`'s full-file-rewrite touches every persisted row on every write
regardless.

This is not a bug in this session's own code (`_combination_needing_work`/`plan_needing_work`
correctly never selected these ids for re-generation — verified: none of the 10 appear in any batch
output above), and it is not something a hand-fix here should paper over: `fae533a519`'s own
approach (editing the seed file directly, leaving the ledger stale) is itself the kind of edit this
program's rule set forbids for generated content, and it ALSO happened to violate `run.py`'s own
structural contract that `nameKey` is `PLANNED` (`emit.name_key(cell)`, minted from the grid cell
before any model call, e.g. `combination.strain-focus-defense`) and never a name-derived slug
(`combination.iron-cadence`) — restoring the structural `nameKey` is the ledger's own truth
reasserting itself, not a regression in that one respect. The genuine regression is the LOST
collision fix for 10 real duplicate names.

**Not fixed here, on purpose:** hand-typing the old names back in would itself be a hand-edit of
generated content, and re-running whatever `name_repair`-shaped tool produced `fae533a519` was not
verified to (a) support the `combination` kind or (b) itself update the ledger this time — doing
that without verifying both would risk repeating exactly this defect a second time. **Recommend a
follow-up task:** audit whatever tool wrote `fae533a519` for combinations, confirm/fix that it also
writes through `RunLedger.mark_done` (not just the seed file) before it is ever run again on this
kind, then re-run it once over the current (now 95-entry) corpus.

### 2. My own regen's fresh output has 7 new name-collision groups (SemanticDedup, gates=False)

`Kinetic Bastion` (7 entries), `Kinetic Impact` (2), `Kinetic Recoil` (3), `Shatter-Guard` (2),
`Stilled Pulse` (2), `Unstoppable Momentum` (2), `Vengeful Bastion` (3) — the SAME shape of defect
`fae533a519` fixed the first time, freshly reintroduced (both by the ledger reversion above, and
independently by round-2/3/4's own new persists reusing the same short evocative names). This is a
known limitation of a small local quantized model (limited creative range under many similar
briefs), `gates = False` in Python (`SemanticDedup.gates`) so it does not fail `--gate`, but IS a
real, measured `NameCollision`/`FusionNotDecomposable`/`NameGrammarViolation` set in the C# static
validator (confirmed absent from the pre-regen baseline `dotnet run` output — genuinely new).
**Not hand-fixed**, for the same reason as finding 1: the sanctioned path is the generator's own
repair tool, run as an explicit follow-up, not a hand rename here.

## What is committed

- `gk-data/packs/fusion/data/seed/items/combinations/strains.json` (25 -> 31 entries)
- `gk-data/packs/fusion/data/seed/items/combinations/splices.json` (51 -> 64 entries)
- `gk-data/packs/fusion/data/seed/items/combinations/combination-gen.ledger.json` (real `RunLedger` state — this run's
  own `mark_done`/`mark_terminal` writes; also now reflects the pre-existing `fae533a519` reversion
  described above, since that commit never touched this file)
- `gk-data/packs/fusion/data/seed/items/combinations/combination-still-blocked.json` (new — the R13 artefact, 7 rows)

Nothing hand-edited: every byte in these four files came from `authored.run_batch` /
`RunLedger.write_done` / `_persist_combination_still_blocked_report`, driven by real model calls
against the verified local endpoint above.

## Acceptance criteria (from `tasks/strain-splice-host-todo.md`)

- `validate --deps` passes, then the widened `--retry-blocked --write` runs; the ledger shows no
  authored cell re-run — **met** (none of the 10 desynced ids, nor any other previously-`persisted`
  id, was ever a member of any `--retry-blocked` batch's own subject list; the reversion described
  above is `entries_from_ledger`'s documented full-rewrite behavior over a ledger that was ALREADY
  stale before this session, not a re-run of an authored cell by this task's own generation calls).
- every grid cell is `entry` or listed by id in R13 — **met**, 95 + 7 = 102.
- `check --gate --metric Registration/IngredientUnsatisfiable` green — **met**.
- regenerated files + ledger committed as generator output, nothing hand-edited — **met**, see above.
