# SSH5.13 — the R11 helm-host re-run under `sockets.v2` (owner-authorized)

The re-run the owner authorized. Run with no `tools/seedsmith/.env` in this worktree (gitignored, not
copied), so the machine-local values were passed explicitly: endpoint `http://localhost:1234/v1/chat/completions`,
model `google/gemma-4-26b-a4b-qat` (identical to the main checkout's `.env` and to `llm_caller`'s built-in
default), `--authored-utc 1970-01-01T00:00:00Z` (the corpus's deterministic stamp), `--retry-label r11-helm`.

## The run

| Step | Command | Result |
|---|---|---|
| strain, R11 pass | `PYTHONPATH=gk-forge/tools/seedsmith python -m seedsmith items generate --kind combination --shape strain --write --retry-blocked --retry-label r11-helm --allow-production-tree --model google/gemma-4-26b-a4b-qat` | planned **5**, persisted **2**, escalated 0, blocked **3** |
| splice, R11 pass | same with `--shape splice` | planned **2**, persisted **1**, escalated 0, blocked **1** |
| strain, second `--retry-blocked` pass (re-print + another authoring pass) | same as row 1 | planned **4**, persisted 0, escalated **1**, blocked **3** |
| splice, second `--retry-blocked` pass | same as row 2 | planned **1**, persisted **1**, blocked 0 |

`head-guard` was **offered by derivation** in every pass — `hostRoles` printed
`armament-primary, armament-secondary, core-guard, footing, girdle, head-guard, infusion, manipulator,
mantle, retinue, ward-array`, `geometricCombosPerActor: 11`, no code or schema change (the R11 pre-flight
`deps_mod.roles_without_a_base` passed, which is what the SSH5.12 re-stamp unblocked).

## Acceptance

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `Coverage/HostRoleDiversity` printed across weapon / chest / helm / other (a reading) | `cd gk-forge/tools/seedsmith; PYTHONPATH=. python -m seedsmith check ../../data/seed/items --adapter items --gate --metric Coverage/HostRoleDiversity` | exit 0, **23 note**. strain 32 entries: core-guard 19/32 (**593‰**), armament-primary 11/32 (**343‰**), none 2/32 (62‰), **head-guard 0/32 (0‰)**, manipulator 0. splice 66 entries: core-guard 36/66 (**545‰**), armament-primary 29/66 (**439‰**), **manipulator 1/66 (15‰)**, **head-guard 0/66 (0‰)** | `gk-data/packs/fusion/data/seed/items/combinations/combination-still-blocked.json` |
| the still-blocked report re-printed; every cell `entry` or listed by id (R13) | `python -c "…"` over the two partition files + the report | **32 + 66 entries + 4 reported = 102 cells, 0 unaccounted** (grid = 36 strain + 66 splice) | same |
| the four reported cells by id | (above) | `strain/composure-balance` blocked, `strain/ferocity-defense` blocked, `strain/might-balance` blocked, `strain/ferocity-balance` **escalated** — each carries its own reason and `survivedReruns` ending `r11-helm` | same |
| the shipped corpus is still valid after the move | `dotnet run --project gk-forge/tools/ItemSeedValidator` | **PASS — 3960 entries / 1013 files / 2589 warnings**, 0 errors | `gk-data/packs/fusion/data/seed/items/combinations/{strains,splices}.json` |
| `the_shipped_corpus_has_no_refusal` (SSH3.3/SSH4.4) still green | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~CombinationCorpus"` | **6 passed / 0 failed** | — |
| seedsmith suites touched by the guard work | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py gk-forge/tools/seedsmith/tests/test_combogen.py gk-forge/tools/seedsmith/tests/test_item_name_repair.py gk-forge/tools/seedsmith/tests/test_combination_repair_ledger.py -q` | **117 passed** | — |
| validator-project tests | `dotnet test gk-forge/tests/FusionRpg.ItemSeedValidator.Tests` | **97 passed / 0 failed** | `gk-forge/tools/ItemSeedValidator/Program.cs` |
| corpus health, full gate | `cd gk-forge/tools/seedsmith; PYTHONPATH=. python -m seedsmith check ../../data/seed/items --adapter items --gate` | exit **1** — **57 gap / 598 note / 153 not_measured** (counts identical to SSH5.12's reading; the exit is the 30 gating `Linkage/SetCompletability` GAPs on `gk-data/packs/fusion/data/seed/items/sets/**`, untouched here) | — |
| 21-guard CI tier | `pwsh -NoProfile -File scripts/run-guards.ps1 -Tier ci` | **18 gating green / 3 red** (`doc-citations`, `magic-numbers`, `population-pin`) — the same three as at the base `5f51d6fcd492` | — |
| doc citations, strict | `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict` | exit 1: 1681 docs / 24920 citations, **21 HIGH, 0 under `strain-splice-host/`** | — |

## Two defects the run exposed, and what landed with it

1. **The authoring graph never validated the naming contract.** The R11 pass persisted
   `combo.strain-ferocity-balance` = `Bastion of Ferocity` beside the shipped splice `Ferocity Bastion`
   — a token-set collision only the C# validator saw, after the write. Fixed on the production path:
   `answer_reuses_a_shipped_idea` in `workflow/graphs/item_combination.py`, armed by
   `name_repair.shipped_name_keys()` in `_cmd_items_combination_write` (`report/cli.py`), keyed by the
   **authoritative** normalizer (new `ItemSeedValidator --normalize-names`, consumed by
   `name_repair.validator_keys`) — never a Python re-implementation. `repair-names` got the same
   authority (`validate_answers(..., key_of=…)`) and now names the keeper in words, not only by id
   (`keeper_name`): with the id alone, five attempts produced nothing but the keeper's idea reversed.
2. **R13's report dropped `escalated` cells.** An escalated cell has no entry and no `blocked` row, so a
   report filtering on `blocked` alone loses it — exactly what happened to `ferocity-balance`. The
   report now carries every non-entry terminal state with its own `outcome`. The **grammar**
   half of defect 1 (a fusion like `Ironstead` / `Ironheart` that does not decompose) is **not**
   guarded yet — filed as row `SSH5.13-P1` in `tasks/strain-splice-host-todo.md`.

## NOT proved / open

- **The helm was offered but never chosen**: `head-guard` reads 0‰ in both shapes, which is the spec's own
  stated consequence (authored cells are never re-run) — the reading R13's ruling needs, not a defect.
- **`verify-change.ps1` could not run to completion on the corpus paths**: all four
  `gk-data/packs/fusion/data/seed/items/combinations/*.json` have **no owner row** in `gk-core/scripts/verification-boundaries.v1.json`
  (`VERIFICATION BOUNDARY MISSING`), and `scripts/**` is outside this lane's fence — filed as
  `TVB-F14` in `tasks/test-verification-boundary-todo.md`, with the manager to place the row. On the
  mapped code/test paths the run stopped inside the `seedsmith-fallback` pytest check (whole project:
  **4193 passed / 23 failed / 3 skipped**; the 23 are actions/creatures/themes/preflight/population-pin
  failures unrelated to this change — five are registry `KNOWN RED SR-25` — so its `itemseedvalidator`
  check never executed and that boundary was run directly instead: 97/0 + validator PASS).
  `guard-test-substrate` on that run: OK.
- **`gen-items-gate.ps1` (the `gen-items-gate-seam`) exits 1**: "item seed corpus has reachability gaps" —
  the same pre-existing gating `Linkage/SetCompletability` GAPs on `sets/**`.
- The `SSH5.12` fragment recorded the full gate as `exit 0`; re-measured here it is **exit 1** (same
  57/598/153 counts). Counts are the evidence; the earlier exit code was a misreading.
- The seedsmith project run dirtied `gk-data/packs/fusion/data/seed/creatures/_registry/themes.v2.json` (test pollution:
  `test_themes_v2.py::test_publish_is_idempotent` writes the production file with CRLF). Restored to HEAD;
  already filed with its cause and remedy in `tasks/seedsmith-generated-seed-repair-todo.md:123-133`.
- No live-game evidence (CC8's live half stays deferred).
