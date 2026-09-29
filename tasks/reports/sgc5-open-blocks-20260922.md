# sgc-5 — the measured open set, and where the brief and the todo disagree

**Lane:** `sgc-5` (session `species-gear-chain-5`, worktree `cmdc-sgc-5`, base `74b5312b5681`)
**Measured:** this worktree at `74b5312b5`, 2026-09-22.

## 1. The brief's count does not reproduce; the todo's own block rule does

The brief says *"28 open task blocks … start with the T49 family"*. Neither half holds at this tip.

The classification is the reconciliation's own (`tasks/reports/backlog-reconciliation-20260921.md` §1, S1
"heading task + block rule"), re-run here: heading marker → body closure phrase → column-0 `- [ ]` → `- [x]`.

```
$ python - <<'PY'   # heading marker | body closure phrase | column-0 boxes | prose-only, per the §1 method
blocks=66  open (heading without ✅/⭐/🔶/DONE/CLOSED/BUILT/SHIPPED and no closure phrase) = 3
  T37  item-upgrade-tree a — heading names an OWNER RULING → not this lane's to close
  T55  verification-boundaries — the seedsmith boundary; the registry (`scripts/**`) is outside this fence
  T60  the upgrade launders wear and resets potential — prose-only open; TAKEN AND CLOSED by this lane
PY
```

- **`T49` is closed, and was closed before this lane started.** Lane sgc-4 completed the instrument the brief
  asks for (`cb42970a6` "feat(t49): complete the balance pass's instrument -- downgrade risk and craft wear",
  plus its re-confirmation notes) and the todo's T49 row carries the ⛔ **ERRATUM REQUESTED** for the briefed
  `v3/v2/v2` publishes (`deployment-hierarchy` is at v5, so a v3 publish is a rollback). The brief's "start
  here" points at finished work.
- **The `- [ ]` lines inside ✅ blocks are the contract clause the file's own header declares** (`:16-17`),
  so a line count overstates by ~240; the block count is the work count. See `RECON-F6` in the todo.
- **T59/T57/T58/T28/T30/T33/T34*/T40–T46** are done or filed elsewhere (T59's three remaining dark domains
  belong to the achievements / actions / movement programs, whose todos are outside this fence).

**Lane decision:** the brief's stale count is recorded here rather than acted on; the work taken is the
todo's measured open set, in todo order.

## 2. T60 — closed (potential half)

`CraftWearSource.PotentialMaxFor` (T61 half A) removed the only blocker T60 named, so the potential half was
implementable in-fence. Implemented, tested at both layers, spec Open question 3 marked decided, row closed.
Evidence: `tasks/reports/T60-evidence.md`.

## 3. Findings for other programs (the owning todos are outside this lane's fence)

- **DATA-TEST-SUBSTRATE — the full `FusionRpg.Data.Tests` project is load-flaky and its failures move.**
  Three consecutive full runs at the same tree: **1851/1 failed**, **1850/2 failed**, **1852/0 failed**. The
  failures are `CreatureSpeciesImportCliTests.A_stale_committed_file_refuses_the_whole_import_and_writes_nothing`
  (passes alone in 9.3 s) and, in the second run only, `EmpireLevelTests.The_backfill_produces_what_live_play_credited`.
  The failing SET moves between runs and neither test touches the files this lane changed. **Not proved:**
  the cause — no diagnosis beyond "load-dependent, non-deterministic". The substrate program owns the test
  substrate and changed the memory/disk rule on 2026-09-22, so it owns the disposition.
- **T55's remaining halves stay open, owner: the verification-boundary registry (`scripts/**`, outside this
  fence), plus one manager-plane patch.** ⭐ Measured 2026-09-22 by this lane: both boxes' MAPPING half is met
  — `-Paths gk-core/data/tuning/set-topology.v1.json,gk-data/packs/fusion/data/seed/items/sets/abyssswordstar.json -PlanOnly` plans
  `tuning-set-topology (module)`, `seed-items-corpus (module)` and `seed-items-validator-seam (seam)`, no
  `VERIFICATION BOUNDARY MISSING`. The missing `gk-core/data/tuning/*.v*.json` glob fallback and the `knownRed`
  disposition of the pre-existing seedsmith failures are still the registry owner's (nothing in the registry
  lives in this lane's fence). ⛔ **The item corpus still fails: 498 errors / 35 partitions** — T37's owed
  exemption, whose patch touches `gk-forge/tools/ItemSeedValidator/**` (outside this fence) plus a test file inside it,
  so it must be applied WHOLE by the manager, never in halves.
  Box 4 (cwd portability) is FIXED by this lane, and SIX failures were cleared in three passes — see
  `tasks/reports/T55-evidence.md`: the 12-file subset T55 names went **14 failed / 310 passed** →
  **9 failed / 314 passed**, and the cwd-only `RealTreeTests` failure (invisible from the repo root) is gone
  (23 passed from `gk-forge/tools/seedsmith` and from the repo root). Each cleared row has its measured cause:
  `run_seam_cli` took the FIRST `{` on stdout (`Extra data: line 2 column 1 (char 639)` at the payload's own
  start); a `version == 5` tuning pin (v6 published); a `channelFamily == 55` pin (SE1.5 published 54); three
  per-tag count pins (`utility` 19 → 17 after the tag-axis exclusivity repair); and a hand-listed 5-family
  slot-eligibility set that grew to 9. The 9 remaining are three filed causes, all out of fence: **SGC5-F1**
  (six rows need the gitignored `data/seed/actions/_candidates/`), **SGC5-F2** (the generated actions corpus
  names the removed `atom.fx-overlay-damage`), **SGC5-F3** (the committed creature dump is self-inconsistent —
  the C# `--verify` and the Python mirror report the identical hash pair, so the DATA is stale, not the mirror).

## 4. T37 — the recorded blocker, re-read at this tip (the orchestrator's request)

**Verdict: still genuinely external, but the recorded dependency is the wrong one.** Both blobs below are
measurements taken in this session; the row's own text now carries them.

- **WAS: "rule 4's runtime wire is blocked on E9's per-atom power."** ⛔ **That link is done.** E9
  `power-vector` is BUILT (`tasks/effect-atom-todo.md:126`: `PowerVector`/`PowerMath`/`CostFunction`/
  `PowerTables`/`ActorPowerCache`, `RpgStore.Power.cs`, E8 registry v3, plus the `power_json` backfill — which
  writes **`effect_atom.power_json`**, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Power.cs:295`).
- **IS: item `P7.3`/`P7.4` (module 24 `equipment-activation`), unchecked rows in another program's todo.**
  The spec's own chain is *per-atom power (E9) → a profile can be resolved and persisted → the shared
  equip-time enforcement → this verb passes the successor's profile*, and items 2–3 are module 24's. Measured:
  `grep -rn "requirement_profile" gk-core/src/FusionRpg.Data/` → **0 hits** (nothing holds a persisted profile);
  `RequirementProfileResolver` has **no production caller** outside its own file; the only consumer is
  `ItemUpgradePolicy.Decide`, which takes a **caller-supplied** `RequirementProfile?`
  (`gk-core/src/FusionRpg.Core/Items/Mutation/ItemUpgradePolicy.cs:43`, evaluated `:175`). `tasks/item-todo.md:9883+`
  is another active session's file, and its preamble says module 24 "remains genuinely unbuilt".
  Building that second persistence + enforcement mechanism inside this lane is the duplicate-source defect this
  module has already caught three times, so it is NOT done here.
- **Blocker A, unchanged and a DENIED PATH for this lane:** `gk-forge/tools/ItemSeedValidator/**` flags all 498 authored
  edges `SameStageReference` — re-measured: `pwsh -NoProfile -File
  scripts/checks/gen-item-seed-validator.ps1` → **FAIL, 498 errors across 35 partitions**. The ready patch
  touches a denied file **and** a test file inside this fence, so it must be applied WHOLE on the manager plane.
- **One item in T37's own "still open" list has landed**, so it is no longer owed: the real-corpus endpoint
  proof (`A_realCorpusArmourBaseTypeUpgradesToItsAuthoredSuccessor`, `~ItemUpgradeEndpointTests` **15 passed**).

## 5. The block-count question, measured (2026-09-23)

The manager's figure was "38 open task blocks / 265 open rows". Neither reproduces at this tip, and the gap is
a definition, so all six readings are printed here — the file's own rule is the first row.

```
$ python - <<'PY'   # on tasks/species-gear-chain-todo.md at this tip
task blocks (#### headings)                                   66
  open by the reconciliation's §1 rule (heading marker -> closure phrase -> boxes)      2   T37, T55
  blocks with >=1 unchecked box                                                        40
  blocks whose heading lacks a positive marker                                         20
column-0 unchecked rows                                                              285   (was 283 before this lane filed SGC5-F1/F2)
PY
```

So **38 ≈ 40** (blocks carrying at least one unchecked box) and **265 is a line reading that has since moved**
(283 at this lane's start, 285 now). The file's own header clause (`:16-17`) says a ticked task's boxes are
"the original contract" — which is why 40 box-bearing blocks collapse to 2 genuinely open ones, and why this
lane measured before acting rather than working 38 blocks. **Enough said on the metric; the work rows are
T37 (blocked, §4) and T55 (in-fence half done, §3).**

**The exact decomposition, one step further (same run) — the manager's 38 is the CLOSED set.**

```
40 blocks carry >=1 unticked box
  37 of them are marked ✅ in the heading  (manager-closed)
     -> 36 of those 37 name a commit SHA and/or an evidence/report file in their own body
        (the only one that names neither is T56:2908, whose body records the manager's own
         application and the validator's PASS reading)
   3 are unmarked: T37 (blocked, external), T55 (this lane; boxes 1b/3/5 out of fence), T57 (one
     verify box fence-blocked, the rest landed)
40 - 2 (T37, T55) = 38
```

So a count of **38** reads the 37 ✅-marked blocks (plus one of the three unmarked) as open, when the file
itself declares every one of them closed and 36/37 carry their own proof pointer. That is RECON-F6's exact
class — a box counter cannot see the closure markers or the contract clause — and it is why this lane's
answer to "38 open blocks" is two blocked rows, not thirty-eight tasks. **If the manager intends a different
closure rule than the file's own markers, that is a file-level decision (re-mark, or re-open with a reason),
and it should be made once rather than re-derived per lane.**

## 6. The whole seedsmith suite, measured — and an instrument hazard that faked six failures

**The measurement (four chunks, none wrapped in the local `timeout`, each under ~16 min).**

| chunk | result |
|---|---|
| `gk-forge/tools/seedsmith/tests/adapters` + `pipeline` + `workflow` | **586 passed / 0 failed** |
| `tools/seedsmith/tests/test_[a-c]*.py` | 10 failed / 863 passed |
| `tools/seedsmith/tests/test_[d-l]*.py` | 8 failed / 1272 passed |
| `tools/seedsmith/tests/test_[m-z]*.py` | 2 failed / 1612 passed / 1 skipped |

**Corrected total: 14 failed, and 5 of them are the five REGISTERED `knownRed` rows**
(`test_actions_description_completeness.py::RealCommittedCorpusCleanPassTests` ×5 — the registry carries them
and AGENTS.md names the file), so **9 genuine reds** remain: 6 × SGC5-F1, 2 × SGC5-F2, 1 × SGC5-F3. This is
the program-wide figure T55 has been owed since sgc-4's last full reading (17), and it is smaller than that
reading because this lane fixed six rows.

⛔ **HAZARD FOR EVERY LANE ON THIS MACHINE — the local `timeout` wrapper silently breaks tool-launching
tests.** `timeout 60 python -c "import os; print(len(os.environ['PATH'].split(os.pathsep)))"` prints **10**
entries (no `C:\Program Files\dotnet\`), while the same probe without the wrapper prints **95**. So any test
that launches a bare-name tool under a `timeout`-wrapped pytest run fails `FileNotFoundError [WinError 2]`
(or silently **skips**, if it has its own guard). Measured cost here: six rows (`test_combogen` ×3,
`test_item_name_repair` ×3) were recorded red and are **78 passed / 0 skipped** without the wrapper, and one
row (`test_fusion_recipe::test_real_corpus_end_to_end`) *skipped the very seam the lane's fix was about* — so
its proof had to be re-run without the wrapper. Both figures in this report are the corrected ones; the
divergence is named rather than quietly fixed, because a lane that wraps its verification in `timeout` gets a
false red list.
