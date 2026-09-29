# T55 — the seedsmith boundary: cwd fixed, six red rows cleared, nine routed

**Row:** `tasks/species-gear-chain-todo.md` T55 · **Lane:** `sgc-5` · Row stays **OPEN**: boxes 1b (glob
fallback), 3 (`knownRed` rows) and 5 live in `gk-core/scripts/verification-boundaries.v1.json`, outside this fence.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Boxes 1+2 — both paths resolve a boundary, not throw | `pwsh -NoProfile -Command "& './scripts/verify-change.ps1' -Paths @('gk-core/data/tuning/set-topology.v1.json','gk-data/packs/fusion/data/seed/items/sets/abyssswordstar.json') -Session species-gear-chain-5 -PlanOnly"` | **EXIT 0** — `tuning-set-topology (module)`; `seed-items-corpus (module)` + `seed-items-validator-seam (seam)` | plan printed |
| Box 2 follow-on — item corpus valid? | `pwsh -NoProfile -File scripts/checks/gen-item-seed-validator.ps1` | **FAIL — 498 errors / 35 partitions** (T37's owed exemption; its patch also touches `gk-forge/tools/ItemSeedValidator/**`, denied here) | `tasks/evidence-fragments/T37-validator-successor-edge-exemption.patch` |
| Box 4 — the boundary's cwd is portable | `cd gk-forge/tools/seedsmith && python -m pytest tests/test_audit_doc_citations.py -q` | **BEFORE 1 failed** (`0 not greater than 0`) → **AFTER 23 passed**; repo root **23 passed**; boundary's own invocation exits **0** | `gk-forge/tools/seedsmith/tests/test_audit_doc_citations.py` |
| Box 3 — the pre-existing failures | `python -m pytest <the 12 files T55 names> -q -rf --tb=no` | **14 failed / 310 passed → 9 failed / 315 passed / 0 skipped** (three passes; 6 rows fixed) | this fragment |
| Box 5 — outcome attributable to the diff | `pwsh -NoProfile -Command "& './scripts/verify-change.ps1' -Paths @('gk-forge/tools/seedsmith/tests/test_audit_doc_citations.py') -Session species-gear-chain-5"` | **EXIT 1** on `FusionRpg.Guard.Tests` only (2 × `verification-boundary script timed out`) — both pass 2/2 in isolation and the suite was 591/591 earlier on this tree (load flake); the pytest check never ran | — |

**Cleared (6), one line each; the cause is in the commit that fixed it.** 1. `RealTreeTests` now chdir's to
`REPO_ROOT` (the checker shells out to `git ls-files` against the PROCESS cwd; the boundary runs from
`gk-forge/tools/seedsmith`, which has no `docs/`) — the pattern `DocCitationFixture.scan` already used. 2. **Real
defect:** `run_seam_cli` parsed from the FIRST `{` on stdout while its comment promised the LAST top-level
value (the host's `[save-identity] … report: {` sits at char 64 → `Extra data: line 2 column 1 (char 639)`).
3. `test_channel_weight_backfill` pinned `version == 5`; v6 moved it while `missing == {}` holds at
v5/v6/latest (0 each). 4. `test_tree_plan_emit` pinned `channelFamily == 55`; SE1.5 (`325191c05`) published
**54**, so the axis now asserts it MIRRORS the injected catalog. 5. `test_nodegen_vocab` pinned three per-tag
counts; the tag-axis repair (`e1d9103ee`) took `utility` 19 → 17, so it now asserts the closed tag vocabulary,
≥1 tag per family, the generators' own exclusivity rule and both branches non-empty. 6. `test_affix_authoring`
hand-listed 5 slot-eligible families; four more `atom.aura-*` families ship all six variants (derived set
5 → 9), so the five are a subset assertion and the derivation contract stays in its sibling test.

**Routed — 9 genuine reds (filed SGC5-F1/F2/F3 in the todo; every owner is out of this fence).** Six are
**SGC5-F1**: `.gitignore:113` ignores `/data/seed/actions/_candidates/`, empty in every fresh checkout
(measured 0 files), so `test_general_propose.py::RealWorkedExampleTests` ×5 raise
`FileNotFoundError: …/general/round-1.json` and `test_usage_stats.py` reports `acceptedCount == 0`. Two are
**SGC5-F2** (one cause — `gk-data/packs/fusion/data/seed/actions/authored-basics.json`'s `act.attack` names the removed
`atom.fx-overlay-damage`), in `test_cli.py` and `test_corpus_loader.py`. One is **SGC5-F3**: the committed
dump is self-inconsistent, and it is DATA — the C# `--verify` and the Python mirror report the identical
hash pair (`declared cc322647…, disk 6181dc2d…`), so the mirror has not drifted.

**Whole suite, four chunks (none wrapped in `timeout`, each under ~16 min).** `tests/adapters` +
`tests/pipeline` + `tests/workflow` **586 passed / 0 failed**; `test_[a-c]*` 10 failed / 863 passed;
`test_[d-l]*` 8 failed / 1272 passed; `test_[m-z]*` 2 failed / 1612 passed / 1 skipped. **Corrected total 14
failed**, of which **5 are the five REGISTERED `knownRed` rows** (`test_actions_description_completeness.py`
×5) — leaving the 9 above. Per-file re-runs, not arithmetic, give the corrected figures: the 9-file
skip-bearing group → **6 failed / 126 passed / 0 skipped**, the combogen + item_name_repair + fusion group →
**78 passed / 0 skipped**.

⚠️ **MEASUREMENT HAZARD — do not wrap these runs in the local `timeout`.** That wrapper replaces the child's
`PATH` with a 10-entry list (measured: plain `python -c` → 95 entries including `C:\Program Files\dotnet\`;
`timeout 60 python -c` → 10, no dotnet), so any bare-name tool launch fails `FileNotFoundError [WinError 2]`
or skips. Six rows first recorded as red here — `test_combogen` ×3, `test_item_name_repair` ×3 — were that
artifact. Fix #2's proof is therefore stated from the no-wrapper run: the seam genuinely launches.
