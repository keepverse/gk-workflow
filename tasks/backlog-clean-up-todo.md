# Todo: `backlog-clean-up`

**Plan:** [backlog-clean-up-plan.md](backlog-clean-up-plan.md) ·
**Map:** [../docs/architecture/backlog-clean-up-map.md](../docs/architecture/backlog-clean-up-map.md) ·
**Evidence:** [../docs/research/backlog-clean-up/](../docs/research/backlog-clean-up/README.md) (lane
files A–G; "lane X" below means `lane-X-*.md`).

**Status:** approved 2026-09-20 (owner). Tasks may start in plan order. Prefix `BCU`. A cross-program reference is written `<prefix><id>`.

Documents-only verification (used where a task says "docs"):
`python gk-core/scripts/audit-program-pipeline.py` · `python scripts/audit-doc-citations.py`.

---

## Wave 0 — independent foundations

- [x] **BCU0.1 — `lawn-signal-ownership`: record the `PUT /api/players/current` split** — closed
  2026-09-20 (`backlog-clean-up-build-20260920`). `lawn-playable-map.md` (new "Signal ownership" section)
  and `lawn-playable/spec-actor-liveness-refresh.md` (new "Signal ownership" section + `Player` row +
  rule 4) now state `SP6.6` owns the `PUT /api/players/current` notice and that `actor-liveness-refresh`
  extends it with `Ladder`/`CommanderAllocation`/`UniqueAllocation`/`Equip`/`Tree` plus a reserved
  `empireId` field, never a second `Player`-kind channel. Stale `DefaultEnabled = false` / 26.7–37%
  framing corrected in both `lawn-playable-map.md` and `lawn-tuning-profile-map.md` (verified live:
  `LawnBasicAttackFeature.cs:56` reads `DefaultEnabled = true`). The cross-program note to lane B below
  already stated this shape from the design phase; left as is. combat-ai's wave 4 (`lawn-cost-authority`
  et al.) is unblocked.
  - Files: `docs/architecture/lawn-playable-map.md`, `docs/architecture/lawn-tuning-profile-map.md`, `docs/architecture/lawn-playable/spec-actor-liveness-refresh.md`.
- [x] **BCU0.2 — audit v2 B1: blockquote status banners** — closed 2026-09-20
  (`backlog-clean-up-build-20260920`). `status_of()` now also reads a first-10-line blockquote
  banner (`BANNER_RE`) against the one `CLOSED_STATUSES` tuple both regexes share (also used by
  `git_last_touched`'s existing `CLOSED_RE`). `rel()`/`git_last_touched()`/`collect()`/`referencing()`/
  `audit()` threaded a `repo: Path` parameter (default the real repo) so fixture-tree tests can point
  the module at a `tmp_path` tree without touching the real one; `main()` gained a hidden `--root` for
  the same reason. `gk-core/tests/tools/test_audit_program_pipeline.py` (new) covers the banner case, the
  plain-Status-line case staying open, and a v1-regression smoke test (`map-plan-missing`) — 3/3,
  run twice for determinism (0.15s, 0.11s).
  - Verify: `python -m pytest gk-core/tests/tools/test_audit_program_pipeline.py -q` (3 passed x2).
    `verify-change.ps1` refuses with "VERIFICATION BOUNDARY MISSING" — a pre-existing gap (v1 was
    never mapped either); deferred below, registry is fenced by 5 active lanes.
  - Files: `gk-core/scripts/audit-program-pipeline.py`, `gk-core/tests/tools/test_audit_program_pipeline.py`.
- [x] **BCU0.3 — audit v2 B2: `todo-header-vs-boxes` + session/ledger suppression** — closed
  2026-09-20 (`backlog-clean-up-build-20260920`), landed in the same commit as BCU0.4/BCU0.5. Reason:
  the spec's own B2 acceptance text ("the same fixture plus a merged session record… yields no
  `stalled-todo` row") requires the B4 kind to exist to be checkable at all, so B2/B3/B4 could not be
  independently verified across separate commits without either duplicating the whole test harness
  three times or leaving an intermediate commit's test suite unable to collect. `header_claims_complete()`
  scans a todo's first 15 lines for a completion phrase, guarded by a negation check (found live: the
  naive form fired on "No task is done until its verification command is green" — a per-task rule, not
  a whole-todo claim) and by the paperwork-reconcile rule-4 banner ("closed by the header above") once
  that fix lands. `merged_session_names()`/`ledger_done_ids()` (new) read `tasks/sessions/*.json`
  (status=merged) and `tasks/*-ledger.jsonl` for B4's suppression.
  - Files: `gk-core/scripts/audit-program-pipeline.py`, `gk-core/tests/tools/test_audit_program_pipeline.py`.
- [x] **BCU0.4 — audit v2 B3: `absorbed-no-pointer` (advisory)** — closed 2026-09-20, same commit as
  BCU0.3/BCU0.5. `ADVISORY_KINDS = ("absorbed-no-pointer", "stalled-todo")`; excluded from
  `--fail-on-open` unless `--strict`. A live false positive found while building this (a bare word like
  `budget` matching unrelated prose next to an unrelated checked box, 290 rows on the real repo) is
  fixed by requiring either a hyphenated compound module id as a whole word (this repo's real absorbed
  ids: `corpse-cache`, `cache-decay-void`, …) or an explicit backtick citation — real-repo count dropped
  290 → 84 (a reading, not asserted in the test; the test asserts the *behaviour*: generic-word fixture
  yields zero rows).
  - Files: same.
- [x] **BCU0.5 — audit v2 B4: `stalled-todo` + `--stale-days` + `--strict`** — closed 2026-09-20, same
  commit. One `git_history()` pass (`git log --format=%x01%cs%x02%s --name-only`) replaces v1's
  file-dates-only `git_last_touched`, giving both per-path dates (`resolve_touched`, v1's own
  fallback logic unchanged) and (date, subject) per commit for a program-name match — no per-program
  subprocess. `--stale-days` (default 7) and `--strict` are new CLI flags. `test_stale_days_threshold_...`
  proves the threshold moves the verdict; `test_stalled_todo_suppressed_by_{merged_session,ledger_done_ids}`
  prove the two suppression paths independently.
  - Verify (BCU0.3/0.4/0.5 combined): `python -m pytest gk-core/tests/tools/test_audit_program_pipeline.py -q`
    — 15/15, run twice (2.13s, 18.56s — the second run's slowdown is this shared machine's concurrent
    load across other active worktrees, not flakiness: both runs reported 15 passed, 0 failed).
    `verify-change.ps1` refuses (VERIFICATION BOUNDARY MISSING, same pre-existing gap noted at BCU0.2).
  - Files: same.

## Wave 1 — `paperwork-reconcile` (documents only; one writer; re-read `tasks/sessions/*.json` before each batch)

Each batch follows spec rules 1–7: evidence on every tick, a pointer on every close, and a fenced file
goes to the deferred list below. Each batch is one commit.

- [x] **BCU1.1 — P1 tools/infra todos** — closed 2026-09-20 (`backlog-clean-up-build-20260920`).
  Added a "closed by the header above" banner (rule 4) to `rift-gate-todo.md`, `onboarding-rift-todo.md`,
  `debug-mcp-todo.md`, `game-control-todo.md`; re-pointed `live-probe-screenshot-todo.md`'s worktree
  links to the merged in-tree paths + banner; ticked `data-test-substrate-todo.md` Checkpoints 1/2/6/7
  with evidence (D1 covers the "owner reviews" residue); ticked `phaser-kernel-todo.md:43`,
  `overlay-switch-todo.md:123`, `world-map-runtime-gaps-todo.md:47`, and drop-tables' 4 leftover
  verify/manual-check boxes. `audit-doc-citations.py --strict` on each touched file: 0 HIGH introduced
  by this batch (pre-existing HIGH findings on rift-gate/world-map-runtime-gaps are far from the edited
  lines, confirmed via `git diff`). `pipeline-audit-v2 --only todo-header-vs-boxes` no longer lists any
  of the four banner-only files.
  - Files: the 9 files named above.
- [x] **BCU1.2 — P2 story-scene / achievement-title / commander-surface** — closed 2026-09-20
  (`backlog-clean-up-build-20260920`). `story-scene-todo.md`: banner for T1–T26 (pointer to the
  HANDOFF section + PR #7 `f384b3809`); F1's stale "active session" fence corrected — the session
  (`verification-boundaries-20260913-6f31`) merged 2026-09-17, and the row now points at
  `test-verification-boundary` (convergence lane D, read-only here) as the real owner, in both the
  "What absorption did NOT include" table and the Follow-ups table. `achievement-title-todo.md`:
  banner for T1–T7a pointing at the existing "Checkpoint: Complete" evidence (Data 47/Core 22/Server 9).
  `commander-surface-todo.md:253`: split the compound line — Playwright half ticked, live-deploy-smoke
  half stays open/owner-only. `audit-doc-citations.py --strict` per file: 0 HIGH introduced (confirmed
  via `git diff` hunks vs each file's pre-existing HIGH lines).
  - Files: `tasks/story-scene-todo.md`, `tasks/achievement-title-todo.md`, `tasks/commander-surface-todo.md`.
- [x] **BCU1.3 — P3 status lines** — closed 2026-09-20 (`backlog-clean-up-build-20260920`). Fixed:
  `aura-skill-map.md:21` (program finished 2026-08-30, pointer to `aura-skill-ideal.md`'s own
  2026-09-18 self-correction), `drop-tables-map.md:3` (plan complete 2026-09-07), `world-map-program.md:3`
  (contradicted its own line 42), `world-map-todo.md:4` (superseded by `world-map-runtime`), and the 4
  trailed actor-sheet specs (`spec-derived-stats-tab.md`, `spec-gear-tab.md`,
  `spec-locked-preview-tabs.md`, `spec-progression-tab.md`) — each TRAIL-banner spec's bottom Status
  line now matches its own top banner instead of reading "pending owner review." `spec-aura-content.md:303`
  deferred — fenced by `cmdc/lane-d` (solid-enforcement) at batch time; re-check after merging
  `features/mega-merge` (lane D reported complete). `audit-doc-citations.py --strict`: 0 HIGH introduced.
  - Files: the 7 files named above.
- [x] **BCU1.4 — P4 `backlog-clear-todo.md`** — closed 2026-09-20 (`backlog-clean-up-build-20260920`).
  Retired the git-hands-off rule (pointer to `docs/contributing/agent-git.md`); Checkpoint 1's
  misattribution bullet ticked (fixed `aura-skill-todo.md`'s 3 stale `effect-atom E20-E25` references
  → `aura-binding-producer`, and `commander-surface-map.md:146`'s matching naming drift); Phase 3's
  B27 ticked with the `battle-timeline-todo.md` live-probe pointer (Checkpoint 2's 3 dependent boxes
  follow); Phase 6 (loam) marked SUPERSEDED/OBSOLETE with a pointer to `loam-todo.md` and
  `spec-world-warden.md`; Phase 7's E1/E2/E3 all ticked with pointers into `combat-unification-todo.md`
  (Checkpoint 4 follows); Phase 8's stale "spec-first, no specs" premise corrected, B19 ticked, B20-23
  annotated PARTIAL with their real blockers named; Phase 9's housekeeping line ticked; Phase 10's
  placeholder + the `spec-planner.md` §7 follow-up (already self-corrected 2026-08-31) ticked, Checkpoint
  5 updated. Did **not** rewrite the plan header to "superseded by backlog-clean-up" — this program
  routes/points at backlog-clear's real work, it does not absorb or replace the program itself; noted as
  a correction to my own brief's phrasing. `audit-doc-citations.py --strict`: 0 HIGH introduced (confirmed
  via `git diff` hunks vs each file's pre-existing HIGH lines).
  - Files: `tasks/backlog-clear-todo.md`, `tasks/aura-skill-todo.md`, `docs/architecture/commander-surface-map.md`.
- [x] **BCU1.5 — P5 absorbed audits** — closed 2026-09-20 (`backlog-clean-up-build-20260920`).
  `battle-derived-wire-todo.md`: Tasks 0,1,8,10-13,16 (+ Checkpoint 4) ticked/annotated BUILT with
  `solid-remediation` pointers; Tasks 2,3,14,15 annotated PARTIAL/mixed with the real remaining scope
  named and routed to `battle-wire-remainder-todo.md` (BCU2.7) rather than re-attempted; Task 7 (W9
  delve) marked SUPERSEDED/moot; Tasks 4,5 (SR-14) and 9,17,18 left as genuinely open (already
  correct). `combat-math-dedup-todo.md`: Tasks 1,2,3,4,6 ticked/annotated BUILT with pointers
  (+ Checkpoints 1,2); Task 5 narrowed (part a reuse, part b open); Tasks 7,8 annotated with numbering
  traps flagged (matched by content, never D-number, per this batch's own rule); Task 15 (D17, live
  bug) pointed at `infra-remainders` BCU8.1 rather than duplicated; the "not a duplication finding"
  (bare clamps) pointed at BCU8.2. Both plan headers corrected (`battle-derived-wire-plan.md`,
  `combat-math-dedup-plan.md`). Both audit docs' tables updated with landing-commit pointers
  (`battle-derived-wire-audit-2026-09-16.md` §7 W1/W2/W5/W9-siege/W10/W12; `combat-math-dedup-audit-2026-09-16.md`
  §2 D1-D5) — the `combat-math-dedup-audit` file was deferred at BCU1.3's batch time (fenced by
  `cmdc/lane-d`) and became free after the mega-merge merge. `audit-doc-citations.py --strict`: 0 HIGH
  across all 6 touched files.
  - Files: `tasks/battle-derived-wire-todo.md`, `tasks/battle-derived-wire-plan.md`,
    `tasks/combat-math-dedup-todo.md`, `tasks/combat-math-dedup-plan.md`,
    `docs/research/battle-derived-wire-audit-2026-09-16.md`,
    `docs/research/combat-math-dedup-audit-2026-09-16.md`.
- [x] **BCU1.6 — P6 creatures/species** — closed 2026-09-20 (`backlog-clean-up-build-20260920`).
  `creature-progression-todo.md`: D0.1, D1.1, D2.1 ticked with pointers; D1.2 **verified live**
  (read `SpeciesAllocationSource.cs:99-136` directly, not just its consumer) then ticked.
  `creature-seed-todo.md`: Task 13 ticked (pointer to lane-c ledger `be3ac8a6`); GAP-1/2/3/5 ticked
  (each fix was already inline, boxes just never matched). `species-build-todo.md`: T4.6's "not the
  lawn" bullet ticked; G2's 2 boxes ticked after verifying live `KnownMissingPlanSpecies =
  Array.Empty<string>()`. `creature-corpus-self-heal-todo.md` Checkpoint C: ran
  `python -m seedsmith creatures run status --json` live (idle — transient state since overwritten by
  later runs), ticked against the durable C2/C3/D1 written record instead. `creature-lawn-deploy-todo.md:34`:
  ticked (self-declared obsolete). `creature-standalone-todo.md` F2.3: did **not** tick (the real test
  still doesn't exist) — corrected the stale "F2.4 doesn't exist yet" framing and routed the actual
  test-writing to `creature-remainders` BCU4.4 (code work, out of this docs-only batch's scope).
  `audit-doc-citations.py --strict` per file: 0 HIGH introduced (line-level diff inspection, not just
  hunk-range, confirms every pre-existing HIGH citation is an unmodified context line in my edits).
  - Files: `tasks/creature-progression-todo.md`, `tasks/creature-seed-todo.md`,
    `tasks/species-build-todo.md`, `tasks/creature-corpus-self-heal-todo.md`,
    `tasks/creature-lawn-deploy-todo.md`, `tasks/creature-standalone-todo.md`.
- [x] **BCU1.7 — P7 misc absorbed/obsolete** — closed 2026-09-20 (`backlog-clean-up-build-20260920`).
  `actor-hub-enforcement-todo.md:34` and `derived-cook-todo.md:61` ticked with pointers;
  derived-cook's D6 float ticket annotated against the 2026-09-15 numeric-types ruling.
  `verification-boundaries-todo.md`'s Follow-on adoption slices marked SUPERSEDED by
  `test-verification-boundary`. `action-distribution-gaps-todo.md`'s duplicate T4.1-T4.4 block (+
  Checkpoint M) merged per rule 3, pointing at the real ticked rows. `item-todo.md`: Phase 7's module
  23 (P7.1/P7.2/Checkpoint 7A) marked SUPERSEDED with pointers to `species-gear-chain` T35/T36; D39
  corrected from "deferred" to OBSOLETE (`AtomKindRegistry.cs:345-355` permanently refuses it).
  `empire-development-plan.md`: stale "none of deployment-hierarchy's modules are built" overview
  sentence corrected; the 3-way duplicate relic ask (plan prose, plan 4B.3, todo 4B.3, todo
  open-decision) consolidated to the two 4B.3 rows per rule 3. `loam-todo.md` Checkpoint 11 marked
  SUPERSEDED/OBSOLETE in place (L47-L49 additionally OBSOLETE via `spec-world-warden.md` Q3).
  `passive-tree-repair-todo.md:588-591`: gate premise re-verified live (`git merge-base --is-ancestor`
  confirms both the branch merge and the `BattleStatComposer` fusion landed) and corrected from
  "still unmerged" to "stale, likely clear now," routing the actual P11 build to `infra-remainders`
  BCU8.8. `gui-lego-todo.md` Queue reconciled against `menu-refactor-queue.md` (P1 Done + pointer,
  P1b added as its own row, P4 split into Aptitudes-done + the real remainder, P4·Notices added).
  `audit-doc-citations.py --strict` per file: 0 HIGH introduced, confirmed via `git diff` hunk ranges
  against every pre-existing HIGH line in each of the 10 files.
  - Files: `tasks/actor-hub-enforcement-todo.md`, `tasks/derived-cook-todo.md`,
    `tasks/verification-boundaries-todo.md`, `tasks/action-distribution-gaps-todo.md`,
    `tasks/item-todo.md`, `tasks/empire-development-plan.md`, `tasks/empire-development-todo.md`,
    `tasks/loam-todo.md`, `tasks/passive-tree-repair-todo.md`, `tasks/gui-lego-todo.md`.
- [x] **BCU1.8 — P8 duplicates** — closed 2026-09-20 (`backlog-clean-up-build-20260920`). L-N26↔Task
  17: both ticked per D3 ruling (kill→soul gap closed — both known root causes fixed, every
  reconciliation since found zero gaps). Task 22↔`spec-summon-pool-integrity.md`: cross-linked, not
  ticked (still genuinely unbuilt), routed to `lawn-plan.md`'s `summon-pool-integrity` module (BCU2.4).
  Proof 5↔L-N2: cross-linked to `lawn-tuning-profile`'s `lawn-scale-live-proof` (BCU2.4), not ticked
  (still genuinely unbuilt). W16↔class-system P9.0: cross-linked in both `class-system-todo.md` and
  `battle-derived-wire-audit-2026-09-16.md`, merged write-up routed to `infra-remainders` BCU8.9.
  `audit-doc-citations.py --strict` per file: 0 HIGH introduced (confirmed via `git diff` hunk ranges).
  - Files: `tasks/live-probe-todo.md`, `tasks/lawn-combat-wire-todo.md`, `tasks/class-system-todo.md`,
    `docs/research/battle-derived-wire-audit-2026-09-16.md`.
- [x] **BCU1.9 — Deferred-fix list reconciled** — closed 2026-09-20 (`backlog-clean-up-build-20260920`).
  Re-checked the one remaining deferred item: `gk-core/scripts/verification-boundaries.v1.json` is still
  contested (`git diff HEAD...cmdc/lane-b` and `HEAD...worktree-agent-a7caaafc906532c18` both still
  name it; `HEAD...cmdc/lane-c`/`HEAD...cmdc/lane-d` cleared since BCU0.2's snapshot) — stays deferred,
  owned by `test-verification-boundary`. **Found and fixed a real self-inflicted gap while
  reconciling:** `story-scene-todo.md` and `achievement-title-todo.md`'s BCU1.2/BCU1.1 banners used
  paraphrased wording ("closed by the HANDOFF section…", "closed by the … Checkpoint: Complete
  section…") instead of the spec's own mandated literal phrase ("**All boxes below are closed by the
  header above**") — `pipeline-audit-v2`'s `RECONCILED_BANNER_RE` only matches the literal phrase, so
  both files still tripped `todo-header-vs-boxes` after their own paperwork fix landed. Reworded both
  to the exact mandated phrase; `pipeline-audit-v2 --only todo-header-vs-boxes` now lists neither.
  - Files: `tasks/story-scene-todo.md`, `tasks/achievement-title-todo.md`.

### Checkpoint CB1
- [x] Every batch has a commit hash, with evidence on every tick. — BCU1.1 `abf663ae`, BCU1.2
  `5b8125a8`, BCU1.3 `ea1c077a`+`92d6d0c6`, BCU1.4 `0ac0af2d`, BCU1.5 `663755cd`, BCU1.6 `cc4e6271`,
  BCU1.7 `fa29ef1a`, BCU1.8 `30e6efe5`, BCU1.9 (this commit).
- [x] `python gk-core/scripts/audit-program-pipeline.py --only todo-header-vs-boxes` lists no batch file
  (needs BCU0.3) — verified: none of rift-gate/onboarding-rift/debug-mcp/game-control/achievement-title/story-scene
  appear.
- [x] Three random pointers per batch opened and confirmed. — spot-checked live during each batch
  (e.g. `SpeciesAllocationSource.cs:99-136` for BCU1.6, `git merge-base --is-ancestor` for BCU1.7,
  `python -m seedsmith creatures run status` for BCU1.6) rather than only paraphrased from the lane
  reports.

## Wave 2 — owner packet and orphan plans

- [x] **BCU2.1 — Write `docs/research/backlog-clean-up/owner-decision-packet.md`** — closed 2026-09-20
  (`backlog-clean-up-build-20260920`). Part 1 records D1-D5 for the trail. Part 2 lists 10 remaining
  K3 rows (rider-default-on scale-gate framing, base-defense force-size/CONCEAL/Fortress, empire relic
  weight/upkeep value, battle UI for B20/B21, GG1 reframe, item's ~15-20 ask-first rows, war-feedback
  promotion, seedsmith `bond` name tie) each with a stated default. A reconciliation section maps
  every lane's OWNER-ONLY row to one of 5 buckets (closed by D1-4, reclassified K1→agent-run, a named
  K2 run, a genuine still-open K4, or one of the 10 K3 rows) — a coverage assertion per
  `validation-ssot.md`, not a population pin. `audit-doc-citations.py --strict`: 0 HIGH.
  - Files: the packet.
- [x] **BCU2.2 — Apply the owner's answers** — closed 2026-09-20 (`backlog-clean-up-build-20260920`).
  D3 applied at BCU1.8 (Task 17 + L-N26 closed with a pointer). D1's agent-review route applied at
  BCU1.1 (`data-test-substrate-todo.md`'s 4 checkpoints) and now at `backlog-clear-todo.md`'s WM1
  owner-playtest bullets (Phase 4) — the K4 precedent test passes (`world-map-todo.md:510` is the
  in-repo precedent), so it is released to agent review rather than left silent; the live 10-turn
  session itself is not run in this docs-only pass. D2 (lawn combat loop stays on) is already reflected
  in `lawn-playable-map.md`/`LawnBasicAttackFeature.cs` (BCU0.1) and `lawn-combat-ai-ideal.md`. D4's
  four corpus runs are recorded as BCU2.10-2.13, blocked on an owner charter (see those tasks).
  `audit-doc-citations.py --strict`: 0 HIGH introduced.
  - Files: `tasks/backlog-clear-todo.md`.
- [x] **BCU2.3 — Write the two missing lawn specs** — **already done** ahead of this task, discovered
  2026-09-20 while starting it: both files exist, committed `ebf188a23` ("Spec the combat-ai program:
  20 module specs plus 3 cross-program specs"), each headed "Authored by: backlog-clean-up **BCU2.3**"
  — the combat-ai spec session wrote them as its own cross-program prerequisites ahead of this program
  reaching this task. Verified both pass the DESIGN-GATE §5 checklist (present at each file's own
  bottom section, with honest `[~]` gaps named rather than hidden); `spec-zombie-power-source.md` is
  narrowed to wiring over `ZombossCommanderAllocation`, per the map's ruling 1. The one real gap this
  task closed: `lawn-tuning-profile-map.md:13-14` still said "Still unwritten: `lawn-combat-baseline`,
  `zombie-power-source`" — corrected with links, closing this program's own `map-plan-missing`-adjacent
  staleness. `audit-doc-citations.py --strict`: 0 HIGH.
  - Files: `docs/architecture/lawn-tuning-profile-map.md` (the two spec files needed no edit).
- [x] **BCU2.4 — `tasks/lawn-plan.md` / `-todo.md` (prefix `LW`)** — closed 2026-09-20
  (`backlog-clean-up-build-20260920`). Wrote both files: 16 tasks (LW1.1–LW4.2) over 4 waves, one plan
  over `lawn-playable` + `lawn-tuning-profile`. Already-shipped pointers recorded (`DefaultEnabled`,
  `hub-snapshot-cache`/`rider-hit-cost` SUPERSEDED, the attack-write removal, the two BCU2.3 specs,
  `SP6.6` split). `lawn-perf-budget.v1` is LW1.1, first in wave 1. Edges E1/E2 (extends `SP6.6`, never
  a second `Player`-kind channel) and H7 (both tunables land with their readers) are named in the
  plan's own "Architecture decisions" and "Hard edges" sections. Both maps updated in this commit to
  name the plan — `python gk-core/scripts/audit-program-pipeline.py --only map-plan-missing` no longer lists
  `lawn-playable`/`lawn-tuning-profile` (a first attempt still listed them because the map text quoted
  the literal old promised filenames even while saying they were never written — the audit's regex
  matches any `tasks/*-plan.md` mention; reworded to describe them without the literal path).
  `audit-doc-citations.py --strict`: 0 HIGH across all 4 touched files.
  - Files: `tasks/lawn-plan.md`, `tasks/lawn-todo.md`, `docs/architecture/lawn-playable-map.md`,
    `docs/architecture/lawn-tuning-profile-map.md`.
- [x] **BCU2.5 — `tasks/deployment-hierarchy-plan.md` / `-todo.md` (prefix `DH`)** — closed 2026-09-20
  (`backlog-clean-up-build-20260920`). Wrote both files: 9 tasks (DH1.1–DH3.3) over 3 waves. Modules
  3–6 and module 7's §1/§2/§5-workbench/§6 slice recorded as already-shipped pointers (commits from
  `empire-development` and `species-gear-chain`), never tasks. Planned: `deploy-carry`'s real wiring
  (DH1.1–1.3), `injury-tiers` in full (DH2.1–2.3), and module 7's remainder — §3 battle wear (no
  blocker, DH3.1), D4 field touch-up (blocked on `party-dungeon`'s `PackGrid`, named as such, DH3.2),
  D6 commander-pouch parity (DH3.3). Map updated to name the plan in this commit;
  `map-plan-missing`/`spec-no-plan` both clean for `deployment-hierarchy`. `audit-doc-citations.py
  --strict`: 0 HIGH across all 3 touched files.
  - Files: `tasks/deployment-hierarchy-plan.md`, `tasks/deployment-hierarchy-todo.md`,
    `docs/architecture/deployment-hierarchy-map.md`.
- [x] **BCU2.6 — `tasks/effect-pipeline-plan.md` / `-todo.md` (prefix `EPL`)** — closed 2026-09-20
  (`backlog-clean-up-build-20260920`). **Verified each of the 12 modules against code first (trap 1)
  and found the first drift-audit pass wrong**: 10 of 12 modules (`affix-schema` through `dev-reforge`)
  are already built, planned all along inside `tasks/seed-to-concrete-todo.md` under their `ep N`
  ids (T3.1-T3.6, T5.1, T5.2, T5.7, T6.1, T6.2, T7.1, T7.2, all `[x]`) — the map's own line 28 already
  named that plan; the pipeline audit missed it because the plan isn't a literally-named
  `tasks/effect-pipeline-*.md` file. The real gap is exactly modules 11-12 (`affix-power-class`,
  `affix-channel-weights`), added by owner decision 2026-09-03 after `seed-to-concrete-todo.md` was
  substantially written and never folded in. Wrote a 6-task plan (EPL1.1-EPL2.3) for just those two;
  EPL1.3 (the 98-family classification) is flagged as its own K2 model-calling task needing an owner
  charter, not started here. `passive-tree-repair`'s own P10.1-P10.3 dispositions confirm it correctly
  filed these two modules here rather than building them, and its P10.3 tree-consumption follow-up
  stays that program's own future task (gated on a pick-quality measurement it names itself), not
  built by this plan. Map updated in this commit; `spec-no-plan` clean for `effect-pipeline`.
  `audit-doc-citations.py --strict`: 0 HIGH across all 3 files.
  - Files: `tasks/effect-pipeline-plan.md`, `tasks/effect-pipeline-todo.md`,
    `docs/architecture/effect-pipeline-map.md`.
- [x] **BCU2.7 — `tasks/battle-wire-remainder-plan.md` / `-todo.md` (prefix `BWR`)** — done 2026-09-20.
  15 tasks (`BWR1.1`-`BWR3.2`) over 3 waves covering the true remainder of `battle-derived-wire`
  (W3, W4 decision, W8, W13 narrowed, W14/W15, W17) and `combat-math-dedup` (D6-D9, D11/D12,
  D13-D16/D18/D19, D20/D21) after `paperwork-reconcile` P5 (BCU1.5) closed 11 rows. H1 named
  explicitly for BWR1.1 (W3) and BWR1.6 (W17) — both may move battle goldens; the change and the
  re-bless land in the same commit. No single capability map owns this pair (it draws from two
  closed todos + two audits, not one map) so no map pointer was edited.
  `audit-doc-citations.py --strict`: 0 HIGH across both files. Fixed a self-inflicted
  `todo-header-vs-boxes` false positive found live: the header's own "closed"/"done" wording
  (describing the *source* todos as retired, not this file's own boxes) tripped
  `audit-program-pipeline.py`'s header-completion heuristic — reworded without touching the shared
  tool, same class as the `map-plan-missing` literal-string trap hit twice earlier in this program.
  - Files: `tasks/battle-wire-remainder-plan.md`, `tasks/battle-wire-remainder-todo.md`.
- [x] **BCU2.8 — Independent agent review of the four plans** — done 2026-09-20. Fresh-context review
  (`code-reviewer` agent), reading each plan against its cited map/audit/todo and re-verifying key
  claims against live code. 3 PASS, 1 FAIL, fixed same session:
  - **lawn (LW): PASS** — traceable to `lawn-playable-map.md`/`lawn-tuning-profile-map.md` P1-P5a/M1-M5;
    no `combat-ai` overlap (`combat-ai-todo.md:530-531,647,665-666` reads `lawn-perf-budget.v1` as a
    share, authors nothing).
  - **deployment-hierarchy (DH): FAIL, fixed** — DH3.2's "blocked on `party-dungeon`'s `PackGrid`,
    itself unbuilt" was stale/false: `PackGrid` shipped (`party-dungeon-todo.md` D3.18-D3.23 all `[x]`;
    `gk-core/src/FusionRpg.Core/Delve/Pack/PackGrid.cs` exists on disk), and the map self-contradicted (line 50
    called it shipped, line 201 called it unbuilt). Corrected in this commit: `deployment-hierarchy-map.md`,
    `-plan.md`, `-todo.md` all now name the real remaining gap (`ICarriedSupplyCheck` has zero
    implementations, no caller wires a `PackGrid` instance through the resolver) and DH3.2 moved from
    blocked to buildable-now. `audit-doc-citations.py --strict`: 0 HIGH across all three files.
  - **effect-pipeline (EPL): PASS** — all 10 `ep N` closures independently verified `[x]` in
    `seed-to-concrete-todo.md`; EPL1.3 honestly flagged as its own K2/owner-charter task.
  - **battle-wire-remainder (BWR): PASS** — every task traced to its source todo's own P5
    status-update pointer; `BattleHubCompose.cs:92` independently confirmed still `ResolveDerived`
    (W17/BWR1.6 real); H1 named explicitly for BWR1.1/BWR1.6; no re-opened closed rows.
  - Files: `docs/architecture/deployment-hierarchy-map.md`, `tasks/deployment-hierarchy-plan.md`,
    `tasks/deployment-hierarchy-todo.md`.

- [x] **BCU2.9 — `combat-ai`: `/spec` the shared core** — done 2026-09-20. Map `docs/architecture/combat-ai-map.md` (APPROVED by independent review), 20 module specs under `docs/architecture/combat-ai/`, plus 3 cross-program specs (`creature-lawn-deploy/spec-unique-deploy-cap.md`, `lawn-tuning-profile/spec-lawn-combat-baseline.md`, `spec-zombie-power-source.md`). Two independent reviews + a fixer pass: `docs/research/combat-ai/REVIEW-A.md`, `REVIEW-B.md`. **Next:** `tasks/combat-ai-plan.md` / `-todo.md`.
- [x] **BCU2.9a — Write the `combat-ai` plan pair** — done 2026-09-20. [tasks/combat-ai-plan.md](combat-ai-plan.md) / [tasks/combat-ai-todo.md](combat-ai-todo.md), prefix `CAI`, 38 tasks over 5 waves, one task per spec with every spec covered (the plan's "Coverage" table maps all 20 modules). The lawn tunables landed in `data/tuning/combat-ai.v{n}.json` rather than a separate `lawn-combat-ai.v1.json` — the program has one tuning domain with a lawn section, per `spec-profile-schema.md`. `lawn.ai.decide` is `PerfSection` 26 and its budget **share** stays the lawn plan's `lawn-perf-budget.v1` (BCU2.4); the 300-zombie AI-on/off A/B is CAI5.1. Three cross-spec contradictions were found and resolved in the plan's "Corrections" section (PerfSection index collision, `AiTriggerBlock` field count, `lawn-held-actions`' stale dependency header).
- [x] **BCU2.10 — Corpus run: action-distribution-gaps B0 → B1 (then top-up rounds per its todo)** · L-run · deps: **T4.5 preflight (met; re-run GREEN 2026-09-23 in this lane) + a manager-run detached job** (T4.6's own text: *"NOT STARTED: a corpus-scale model run (~23–28 h) is a manager-run detached job, not a lane job"*); spend gate released 2026-09-21; authorized by D4; runbook in `tasks/action-distribution-gaps-todo.md` T4.5+
  - **Lane `cmdc/bcu8-4` close-out (2026-09-23) — this row is a manager-run detached job and is IN FLIGHT; it is not a lane job, and its outputs (`gk-data/packs/fusion/data/seed/actions/**`) sit outside this lane's fence.** Sources: `tasks/run-board-20260920.md:1560` ("launched as a manager-run detached job … resumed round-1") and `2004b5a42` on `features/mega-merge` ("`BCU2.10` running (action round-1, resumed)"). The lane-reachable half — the BEFORE reading the row's "thinCell shortfall **delta**" needs — is delivered: `PYTHONPATH=gk-forge/tools/seedsmith python tasks/reports/bcu2-10-readings.py --out tasks/reports/bcu2-10-readings.json` → accepted size **181** (`corpusHash 9c8ff5b7…`), thinCell shortfall **20,384** (48 of 48 cells thin), `quotaDrift` **clean**, verdict `pass`, targets 5,387; the same command after the run yields the delta. It runs the coverage tool's `--dry-run` path and writes nothing under `data/`.
  - **Top-up half read at `53ce6ef60` (T4.7–T4.10's baseline): the committed round-2 report is a different corpus generation and must not be used as one.** `python tasks/reports/bcu2-10-readings.py --round 2 --out tasks/reports/bcu2-10-readings-round-2.json` → a fresh round-2 dry-run reads **181 accepted** (`corpusHash 9c8ff5b7…`, tuning **3**, thinCell shortfall **20,384**, 48 thin cells, verdict `pass`), while the committed `gk-data/packs/fusion/data/seed/actions/_reports/coverage-round-2.json` reads **24 accepted** (`corpusHash 0f8c6c83…`, tuning **2**, shortfall **639** over 45 cells, 237 entries, verdict **`not-clean`**) — so its 639 is not comparable to the current 20,384. The first top-up round must be planned from the *current* round-1 report and the round-2 report regenerated by the run (a `gk-data/packs/fusion/data/seed/actions/**` write — the manager's); using the on-disk one silently compares two corpora. Same staleness class as ADG-F1, which this program has already paid for once. Also stated there: a fresh round-2 reading equal to round 1's is *not* "round 2 changed nothing" — the targets derive from the same corpus, so the two must agree until a top-up writes rows. Details: `tasks/reports/bcu2-10-closeout.md`.
  - **Finding filed (row stays open):** `710390b56`'s own body says "Readings recorded … in `tasks/reports/BCU2.10-round-1.json`", but that file carries only `job`/`report`/`topLevelKeys`, and the commit changed exactly two files — `_generated/characteristic-pool.json` (one `action-rungs.v1.json` → `v4.json` string) and the artefact. No `_rounds/round-1/**` or `_reports/coverage-round-1.json` moved (last writes 2026-09-16 `094ca0286` / 2026-09-19 `e6324de18`, both before the 2026-09-21 replan `c52697a4a`), and `generate_usage_stats --write` (`generate_usage_stats.py:75-77`) produces `_reports/_usage-{date}.json`, absent from every branch's history. Evidence, `file:line` and the full reading table: `tasks/reports/bcu2-10-closeout.md`.
  - **CLOSED 2026-09-23 by measurement (manager).** Detached job finished VERDICT JOB END (report_exit=0, commit_exit=0); merged as a401abbe5; boundary guard OK. Report now carries readings: acceptedSize 181, thinCell shortfall 20384 across 48 cells, quotaDrift clean (evaluated, verdict pass). The thin-cell gap is the top-up rounds' work per this row's own text, not a blocker.
- [ ] **BCU2.11 — Corpus run: item-seedgen full run (~904 species / 36 sets / ~904 charms)** · L-run · deps: **a generator fix for the near-duplicate / `EmptyPartition` defect** (ISG-gap-2's 2026-09-22 correction by measurement: the corpus adds **747 near-duplicates [STALE — measured 558; see the 2026-09-26 correction] [STALE — measured 558; see the 2026-09-26 correction] [STALE — measured 558; see the 2026-09-26 correction] [STALE — measured 558; see the 2026-09-26 correction] [STALE — measured 558; see the 2026-09-26 correction] [STALE — measured 558; see the 2026-09-26 correction] [STALE — measured 558; see the 2026-09-26 correction] [STALE — measured 558; see the 2026-09-26 correction]** and fills **none** of the 911 gaps — revert `ea2aeb756`), **not an owner charter** (spend released 2026-09-21, and `Linkage/SetCompletability` measures *no findings* at HEAD); authorized by D4; per `tasks/item-seedgen-todo.md`
  - **Lane `cmdc/bcu8-4` reading (2026-09-23): the board line gates this row on a criterion that measures CLEAN at HEAD.** `tasks/run-board-20260920.md:1563` names its `SetCompletability` GAPs; `cd gk-forge/tools/seedsmith && PYTHONPATH=. python -m seedsmith check ../../data/seed/items --adapter items --metric Linkage/SetCompletability` → `no findings`, exit 0 (ISG-gap-1's 30 → 0 fix already landed; that row's erratum request stands). **The real gate is the one ISG-gap-2 corrected by measurement (2026-09-22):** the BCU2.11 corpus does **not** fill the 911 `Coverage/EmptyPartition` gaps and adds **747 near-duplicates** — `ea2aeb756` reverted it (956 files, −130,881). Closing that means fixing the generator (`gk-forge/tools/seedsmith/**`), then re-running; both outside this lane's fence. Ask: re-route the row on the near-duplicate/EmptyPartition defect, not on `SetCompletability`.
  - **The residue is now mapped (the ISG-gap-2 acceptance's own alternative: "the residue is enumerated partition-by-partition with a reason per partition").** `PYTHONPATH=. python -m seedsmith check ../../data/seed/items --adapter items --metric Coverage/EmptyPartition --json ../../tasks/reports/ISG-gap-2-residue.json` → **911**, all named in that JSON with their metric evidence, grouped with a reason per group in `tasks/reports/bcu2-11-residue-map.md`: **904 of the 911 are `sets/species/<id>`** (one per roster species, allocated by `KindCatalog.cs` + `naming.v1.json` via the snapshot at `adapters/items/registries.py:14`), 1 `sets/might-offense`, 1 `attributes`, 2 base-type frames, 3 display-template slots. The open question the map hands to `item-seedgen`: whether a species-scoped set is intended at all — if it is, the generator owes 904 *distinct* sets and the 747 near-duplicates are the defect [STALE — measured 558; see the 2026-09-26 correction] [STALE — measured 558; see the 2026-09-26 correction] [STALE — measured 558; see the 2026-09-26 correction] [STALE — measured 558; see the 2026-09-26 correction] [STALE — measured 558; see the 2026-09-26 correction] [STALE — measured 558; see the 2026-09-26 correction] [STALE — measured 558; see the 2026-09-26 correction] [STALE — measured 558; see the 2026-09-26 correction]; if it is not, the allocation rule is over-allocating. It is model-free and writes nothing under `data/`.
  - **Root cause of that residue, read at `file:line` (same lane): it is mostly a partition-KEY mismatch, not 911 unfilled slots.** `gk-forge/tools/ItemSeedValidator/Registries/NamespaceAllocation.cs:261` allocates `sets/species/<raw speciesId>` (underscores kept: `sets/species/elephantzombie_a`) while the corpus emits `sets/<hyphenated slug>` from the set's own id (`gk-forge/tools/seedsmith/seedsmith/adapters/items/setgen/authored.py:99-100`: `set.elephantzombie-a-001` → `sets/elephantzombie-a`). Measured on the same corpus (`PYTHONPATH=gk-forge/tools/seedsmith python tasks/reports/bcu2-11-partition-key-map.py --out tasks/reports/ISG-gap-2-per-partition.json`): of the 904 allocated species slots, **844 have a same-species set entry under the other spelling** (`counterpartPartition` in the per-partition JSON, one `reason` per partition × 911), **60 have none**, plus `sets/might-offense`, `attributes`, 2 base-type frames and 3 display-template slots — residue **67** if the allocation key is corrected, with zero slug collisions after folding case/`-`/`_`. That also explains the reverted run's **747 `SemanticDedup/NearDuplicate` [STALE — measured 558; see the 2026-09-26 correction] [STALE — measured 558; see the 2026-09-26 correction] [STALE — measured 558; see the 2026-09-26 correction] [STALE — measured 558; see the 2026-09-26 correction] [STALE — measured 558; see the 2026-09-26 correction] [STALE — measured 558; see the 2026-09-26 correction] [STALE — measured 558; see the 2026-09-26 correction] [STALE — measured 558; see the 2026-09-26 correction]** findings: a fill aimed at `sets/species/<id>` re-writes the same sets under a second key. The fix is a contract call between two files outside this lane's fence (`gk-forge/tools/ItemSeedValidator/**`, `gk-forge/tools/seedsmith/**`) — **not** a fill, and the owner must say which spelling is canonical. Evidence: `tasks/reports/bcu2-11-residue-map.md` (its correction section) + `tasks/reports/ISG-gap-2-per-partition.json`.
  - **Manager reading (2026-09-23 ~12:45) -- the run completed, its base went stale, and it is being REGENERATED.** (1) The job finished cleanly: log `.pi/tasks/session-67372-67372/b3bd00488.output` (`FINISHED=2026-09-23T12:19:48`, `fill_exit=0`), report `tasks/reports/BCU2.11-full-run.json`, 56 files written. (2) **Measured, the same check on both trees** (`python -m seedsmith check gk-data/packs/fusion/data/seed/items --adapter items`, PYTHONPATH set in each): integration head **931 gap** / 612 note vs the job tree **770 gap** / 10527 note -- the run closed **161 gap findings**. (3) **Its base was 1 ahead / 1160 behind**, so merging it conflicted in **53 files** under `gk-data/packs/fusion/data/seed/items/**`; both sides are generator OUTPUT, so that is resolved by **regenerating on the current head, never by hand-editing rows** (the runner script's own header already names this hazard). (4) Regeneration in flight: worktree `.claude/worktrees/corpus-bcu211b` (branch `corpus/bcu211b`, based on the integration head `f0661fc13`), job `b72965106`, log `D:\tmp\bcu211b-run.log`. Branch `corpus/bcu211` keeps commit `6fc3d2b21` as the reference reading. (5) The job's own in-script check reported `check_exit=1` with a detail saying a batch written outside the tree cannot move the metric -- a launcher path bug, recorded here rather than read as a corpus failure. **The row stays open** until the regenerated output lands with its own report, and then ticks on the new measured reading (the runner now takes `-Worktree`, commit `170c31b5f`).    - **Manager erratum (2026-09-26) — the 770 is a stale-base reading, and applying this run to the current head is a REGRESSION, not the -161 the commit subject claims.** Measured on this tree, same command both sides (`PYTHONPATH=gk-forge/tools/seedsmith python -m seedsmith check gk-data/packs/fusion/data/seed/items --adapter items`): integration head before the attempt **931 gap / 612 note / 153 not_measured**. The resolved merge of `corpus/bcu211` gives **1672 gap / 10533 note / 153 not_measured** — **+741 gaps, not -161**, and the note count rises 17x. The merge was **aborted** and the tree restored to 931/612/153 exactly, so nothing from this attempt is on the branch.
      - **Why the conflict resolution was not the cause.** 52 add/add files under `gk-data/packs/fusion/data/seed/items/**`; 19 verified as strict supersets (every keyed row on this side present and identical), 4 are run ledgers / a blocked-combination record, and **29 carry the same item ids with different content**. On those 29 the difference is exactly one field: this side's rows carry `successorOf`, the run's do not. That is not a merge decision but a missing post-pass — `successor_edges.py:10` states the field is applied additively from the authored registry, and the run emitted the pre-pass rows. Re-running the sanctioned tool (`python -m seedsmith.adapters.items.basetypegen.successor_edges --dry-run` → `--write`) restamped **398** rows and restored the field, recorded in `_meta.amendments`. So the resolution was generator-mediated, and the metric still went to 1672: the regression is in the run's content, not in the merge.
      - **Provenance cannot adjudicate the 29.** Every `_meta` key is byte-identical on both sides — `promptVersion`, `contractVersion`, `model`, `registryVersions` and even `authoredUtc`. These are not two generations of the file; they are the same generation with different content, so "the newer run wins" has no evidence behind it and hand-picking rows is forbidden.
      - **This confirms and quantifies the 2026-09-23 reading above** (stale base 1 ahead / 1160 behind, 53 conflicting files, regenerate rather than hand-merge). The new number is what that reading predicted would happen if the stale output were merged anyway.
      - **State of the in-flight regeneration, so it is not mistaken for progress:** worktree `.claude/worktrees/corpus-bcu211b` (branch `corpus/bcu211b`) is based on **`f0661fc13`, itself ~1160 commits behind this head**, holds **73 UNCOMMITTED** entries, has **0** commits not on this head, and its run log `D:\tmp\cu211b-run.log` is **absent**. Nothing about it is reviewable or landable. The report on head, `tasks/reports/BCU2.11-full-run.json`, was itself generated at head `ac0fd77c` on branch `corpus/bcu211` — a third, older head.
      - **Still an owner decision, unchanged and now load-bearing:** the root cause above is a partition-KEY mismatch (`gk-forge/tools/ItemSeedValidator/Registries/NamespaceAllocation.cs:261` allocates `sets/species/<raw speciesId>` with underscores; the corpus emits `sets/<hyphenated slug>` from the set's own id). 844 of 904 allocated slots have a same-species set under the other spelling. **Which spelling is canonical is a contract call the owner must make**, and until it is made a re-run reproduces the same near-duplicates rather than filling the gaps.
    - **Manager correction (2026-09-26, after the partition-key audit) — the 747 does NOT reproduce, and the "904 distinct sets" premise is WRONG. Measured 558.** The 747 figure, and the framing built on it, came from the reverted stale-base run and was carried forward unverified through this block and into the manager's own question to the owner. The audit measured **558** `SemanticDedup/NearDuplicate` and proved the figure is not stable: `dedup.py:85` returns a `frozenset` whose iteration order makes the reported *pair set* non-deterministic (the pair set was byte-identical over three runs; 20 notes moved). Quote 558, and treat the count as a reading rather than a constant.
      - **The premise "the generator owes 904 *distinct* sets" is overturned.** `setgen/emit.py:70-72` reserves sequence `900-999` *in every partition* for later use, and `_merged_partition_rows` appends to a committed partition file — so a species-scoped set partition is a **namespace holding many sets**, not one set per species. The generator owes 904 **partitions**, of which **844 were already occupied**. The 904-sets reading is what made the fill look like a near-duplicate generator in the first place.
      - **Which side was wrong: the allocation, and specifically the extra path segment — not the spelling.** The raw underscored `speciesId` is canonical (`setgen/emit.py:41-54`: underscored names "remain the authoritative `speciesId` in the theme registry", hyphenated only "at the item boundary"), and the 844 shipped entries agree — 65 carry `_`, **0** carry `-`. `naming.v1.json:367` declares **one** partition key, `"partitionKey": "themeId"`, a single component; `sets` was the only kind allocating two path depths for one declared key, and `grep` finds `sets/species` in exactly two places — the line that wrote it and the 904 snapshot rows it produced. No test, no spec. `NamespaceAllocation.cs` now names the partition by the id template's slot.
      - **Result, reproduced by the manager on the merged head with `PYTHONPATH=gk-forge/tools/seedsmith python -m seedsmith check gk-data/packs/fusion/data/seed/items --adapter items`:** baseline **931 gap / 612 note / 153 not_measured** → **87 gap / 612 note / 153 not_measured**. `Coverage/EmptyPartition` 911 → **67**, and the 67 are the genuinely empty ones. Every other metric **+0**; the near-duplicate pair set unchanged (558, 0 gained, 0 lost). The 60 "new" gaps are those same 60 empty species partitions, relabelled rather than filled.
      - The 60 that had no counterpart under either spelling are the real residue, and they are the next thing to fill. Report: `tasks/reports/partition-key-audit-20260926.md`.

  - **CORRECTION 2026-09-27 (manager, leftover walk): the corpus accounting in the reports to the owner
    was wrong in both directions, and this row's decision is sharper for it.** Measured against
    `features/mega-merge`:
    - **`corpus/bcu211b` has 0 unmerged commits** - fully integrated. Its
      `gk-data/packs/fusion/data/seed/items/_runs/materials-gen.ledger.json` is **byte-equivalent to integration's** (79
      distinct lines, 0 differences either way). The "24,440 unlanded lines in materials-gen" figure
      reported to the owner as gating BCU2.11 **does not belong to this branch**.
    - **`corpus/bcu212` also has 0 unmerged commits.** Its unlanded content is **706 untracked generated
      files** under `gk-data/packs/fusion/data/seed/passive-tree` (352 `species/`, 351 `nodes/`, 3 `_runs/`) - not 47,508
      lines in a ledger. `tree-language.ledger.json` is not at that path on any branch; the real file is
      `gk-data/packs/fusion/data/seed/passive-tree/_runs/tree-language.ledger.json`, 386,586 lines, and it **is** at
      integration.
    - **The real unlanded materials corpus is `corpus/bcu211`'s `6fc3d2b21`**: 56 files, every one
      present at integration *by name*, and **all 56 DIVERGENT by line set**, with
      `materials-gen.ledger.json` at **+24,404 / -0** - a strict superset of integration's. That is the
      figure that was real, attributed to the wrong branch. The commit had **no ref but its own
      worktree's branch**, so a rescue ref `rescue/corpus-bcu211-itemseedgen-run` was created before
      anything touched it; this row already names the commit and its 56-file run, so the work is tracked
      rather than forgotten.
    - **The owner decision is unchanged in substance and sharper in shape.** It was never "authorize two
      model runs against 24k and 47k unlanded lines". It is the **partition-key decision this row
      already names as load-bearing** (`gk-forge/tools/ItemSeedValidator/Registries/NamespaceAllocation.cs:261`
      and the extra path segment), plus whether to land the one regeneration that now exists on the
      rescue ref. Neither branch is waiting on a commit.

- [ ] **BCU2.12 — Corpus run: passive-tree J9 / J10 / J13** · L-run · deps: **J9-B1(b)'s named repair** (PT-J9-F1: re-ask the colliding node / supersede its ledger row — the refusal is *reported* today, not repaired) **+ J13's target restatement to `tree-language/3`** (PT-J9-F2); spend released 2026-09-21; authorized by D4; per `tasks/passive-tree-todo.md`
  - **Lane `cmdc/bcu8-4` reading (2026-09-23): manager-run job in flight.** `tasks/run-board-20260920.md:1562` (`[133/904]`, log fresh) and `2004b5a42` (`[134/904]`); its corpus is `gk-data/packs/fusion/data/generated/passive-tree/**` + `gk-data/packs/fusion/data/seed/passive-tree/**`, outside this lane's fence. The merged artefact `tasks/reports/BCU2.12-full-run.json` reads 0 species complete against 904, 12 started-but-incomplete, 4 nodes without the codex supplement — i.e. the run's own acceptance is unmet and still running. **The J10 census reading is recorded, model-free:** `PYTHONPATH=gk-forge/tools/seedsmith python -m seedsmith check --family PassiveTree` → **3030 note, 543 gap, 1 not_measured** — 389 `NameCollision` (`388/1679 nodes (231‰) share a name`), 83 `QuotaDrift`, 67 `SpeciesUniqueness`, 4 single corpus-level findings — over **42 trees / 1,679 nodes**. Per-finding lines: `tasks/reports/bcu2-12-census.txt`; the reading, its provenance and the ledger-vs-corpus gap (2,200 ledger rows vs 42 trees on disk): `tasks/reports/bcu2-12-census.md`. Re-run the same command after the run for the delta.
  - **Root-cause read of the 388 `NameCollision` nodes (same lane, model-free, `file:line`): the gate exists and the ledger says it did not hold.** The contract is `nodegen/run.py:162-249` (gate 21, closed 2026-09-11) seeded corpus-wide at `:1031-1047` from the whole ledger, and the species path reaches it (`species/generate_tree.py:192`). Measured in that ledger (2,249 accepted subjects): **303 names are recorded by more than one subject**; `Kinetic Recirculation` was accepted **12 times across 7 trees, five inside `BigGatling`** (ledger indices 2161-2177) — and ledger order is append order, so `might`'s copy at index 203 predates every later accept, i.e. the name was already in `taken_names`. Narrowed to two mechanisms, both outside this lane's fence: (1) a re-gate that compares `nameKey` instead of `name` (`run.py:1114-1118`), or (2) the codex/finalize write, which references the primitives **zero** times (`grep` over `adapters/trees/species/**` + `_j9_batch_run.py` = 0 hits) while `_j9_batch_run.py:138`'s `finalize_codex` re-draws the vote and writes the species record. The separating experiment is one controlled re-generation (a model call — the owner's). Also: no test pins the tree path's gate (the primitives appear only in base-types/dungeon/uniques/quality-gate tests), which is the contract-with-no-guard shape `validation-ssot.md` names. Details: `tasks/reports/bcu2-12-namecollision-finding.md`.
  - **The NameCollision mechanism, narrowed again by model-free probes (`python tasks/reports/bcu2-12-namegate-probe.py`) — the two earlier candidates are both EXCLUDED.** The real gate refuses a duplicate name (`build_response_gate(..., taken_names=["Kinetic Recirculation"])` over a draft with that name returns *"field 'name' … is already used by another commander effect"*; an unrelated taken name passes as the control), so it is not a `nameKey`-vs-`name` re-gate; and the codex/finalize stage only ever produces `codexSummary` sentences (`species/generate_codex.py`, `_j9_batch_run.py:100-137`), never node names, so it cannot be the writer. What remains is the suffixing path: `_derive_unique_name_key` (`nodegen/run.py:703-724`, called at `:909`) derives the persisted `nameKey` from the accepted **name** and can always make the *key* unique — *"collision-free by construction"*, but about **keys only** — so a duplicate name that gets past the gate is silently key-suffixed, which is exactly the ledger fingerprint (12 identical names at keys `-2`, `-4`, … `-13`). The record-time closure (`run.py:1141-1179`) already turns a **same-batch** name race into an `unresolved` outcome, so a *persisted* duplicate needs either a pre-2026-09-11 accept (three of the twelve sit in `might`/`vigor`/`precision`, files dated 2026-09-07) or a **cross-invocation** ordering the per-invocation live sets cannot see (the species-side holders, files dated 2026-09-21, and `BigGatling`, which has no file at all). Settling that last case needs one controlled species run against the shared ledger — a model call, `gk-forge/tools/seedsmith/**`. Probe JSON: `tasks/reports/bcu2-12-namegate-probe.json`; details: `tasks/reports/bcu2-12-namegate-mechanism.md`.
  - **J13's own Verify line read at this head, plus the vintage its title names being gone.** Its acceptance is *"`check --family PassiveTree` exit 0 under `--gate`; no GAP on the three generation-vintage metrics"*: `--gate` **exits 0** (none of the three is promoted to gate, `metrics/passive_tree.py:1008`), while the metric clause is red on all three — `ExclusionRate` **1071/1679 (637‰)** vs ≤30‰ (J13's own 2026-09-10 table said 999‰), `NameCollision` **388/1679 (231‰)** vs 0 (was 385‰), `NearDuplicate` **116/1679 (69‰)** unchanged vs ≤5‰; `MechanismRamp` is down to **1** shortfall (`wither:defensive:t9`) and `UnresolvedCount` is **92/1680 (54‰)** vs ≤50‰. The vintage is the erratum PT-J9-F2 asked for: file-level `_provenance.promptVersion` across the 42 shared documents is `tree-language/1` **22** · `mixed` **20** · **`tree-language/2` 0** (PT-J9-F2 recorded 22/4/21), node-level is `tree-language/3` **613** · absent **1,066**, and the code writes **`tree-language/3`** (`nodegen/brief.py:57`) — so J13's target version must be restated to `/3` before its acceptance can even be judged, and a `mixed` file here is `/3` nodes beside rows with **no** field, not two labelled vintages. Reproduce: `python tasks/reports/bcu2-12-vintage-reading.py --out tasks/reports/bcu2-12-vintage-reading.json`. Full table: `tasks/reports/bcu2-12-j13-readings.md`.
  - **J13's other two acceptance clauses read at this head (model-free).** *"Every regenerated seed document carries `promptVersion: tree-language/2` and a persisted `quotaCell`"*: both fields sit on the **same 700 of 2,019** node records — **613** of the 1,679 shared-tree nodes and **87** of the 340 species-tree nodes, in 28 documents; the other 1,319 carry neither, and `nodegen/emit.py:96-99`'s loader names them for what they are (*"returns None when absent (every pre-persistence committed record), never invents defaults"*), so the emit wiring landed for 700 rows and the rest are pre-wiring. *"No hand-edits of exclusion forms, names, or `kMicro` — regenerate only"*: **`kMicro` is not a field of any node record (0 of 2,019) nor of any bound/refused row (0 of 2,240)**, and the repair program rescoped its carriage (*"A4 … `kMicro = 0` + real `kindId`, or new field? ✅ RESCOPED 2026-09-15: neither"*, `tasks/passive-tree-repair-todo.md:695`), so that object of the clause is **vacuous at this head** and the live half is "regenerate only" — for which the only corpus signal is the provenance vintage, since a hand-edit and a regenerate are otherwise indistinguishable once committed.
  - **J9's own Verify line read at this head, and its stall is mechanical.** J9's acceptance is *"840 trees × 40 nodes committed; the plan regenerates byte-identically for species as well as the generic corpus; the uniqueness gate holds across all 840"*. Reading: **4 of 904 species complete** (16 started, 9 filed, 8 with a codex-resolved metadata file; the roster is 904, so J9's "840" is PT-J9-F2's stale figure). Clause 2 is green for the **generic** corpus (`python -m seedsmith trees plan --check --manifest` → *byte-identical to a fresh regeneration*, exit 0) plus the species path's 4 stubbed tests (`test_tree_species_generate_tree.py` 4 passed); there is no species plan artifact to `--check`. **Correction (same lane): both clauses of the Verify line are in fact GREEN, and the acceptance is red — do not read one as the other.** `--check` green from `dotnet run --project gk-forge/tools/TreeBinder -c Release -- --check` → exit 0 with **0 `STALE`** lines (the committed bound reports are byte-identical to a fresh run, `gk-forge/tools/TreeBinder/Program.cs:131-141`), and *"the reverse index reports no cross-namespace reference"* is green because the reverse index's U3 leak strength (`metrics/passive_tree.py:1441`, implemented `:1508-1524` — any `affix.species.<speciesId>.*` referenced by a node of another tree) counts **U3 = 0** findings. The 67 `SpeciesUniqueness` findings are the *acceptance's* uniqueness bar, split **U1 12** (a `(name, flavor)` pair on more than one node) and **U2 55** (an `(affixIds multiset, quotaCell)` fingerprint shared by trees; U2 carries the code's own caveat that a committed node record does not persist its `quotaCell` — *H4's documented wiring gap, still open* — so it measures only the cells the caller supplies). Clause 3 is red with them (`NameCollision` 388/1679, `NearDuplicate` 116/1679), and all 42 trees carry a binder `verdict=Fail`. **The stall is not throughput:** all **7** species that hold ledger rows and no node file (`Bamboo`, `BambooFurnace`, `BambooSpruce`, `BedRockSnowZombie`, `BedRockTallNut`, `BigChomper`, `BigGatling`) carry a duplicate `nameKey` inside their own rows (2/1/2/1/1/2/2) — and they are the only species that do. `build_seed_document` refuses exactly that (`nodegen/emit.py:246` → `assert_no_duplicate_name_keys`, `emit.py:48-60`), writes no document, and the records are the ledger's, so each of those seven rebuilds the same refused document on every pass: **they are the population PT-J9-F1 asked for**, and the same root as this lane's NameCollision finding (the corpus-wide name gate not holding is what creates the duplicates). Reproduce: `python tasks/reports/bcu2-12-j9-progress-census.py --out tasks/reports/bcu2-12-j9-progress-census.json`. Details: `tasks/reports/bcu2-12-j9-readings.md`.
  - **Audit finding: PT-J9-F1's tick is for *reporting* the refusal, not for the repair it names — and that is the whole stall.** `tasks/passive-tree-todo.md:7140` marks it `[x]` *"FIXED 2026-09-21 with J9-B1(b)"*, whose landed fix was `run_species_tree` catching `NodeKeyRefused` into a reported `node_key_refused_reason` (the batch survives). The row's own body specifies a different fix — *"a node-level repair for the colliding subject — re-ask that one node (supersede its ledger row) rather than refusing the tree"* — and states the consequence of not having it: *"every later pass rebuilds the identical duplicate-name document and refuses again — the species can never complete"*. Measured, that is the state: the **7** species with a self-duplicate `nameKey` in their own ledger rows are exactly the 7 with **no node file**. So the tick means "the refusal is visible", never "the species can complete" — and any reader who takes the tick as "blocker gone" will spend another 23–28 h of model time growing the unfileable backlog instead of the tree count. Its dep line above is stated from this.
  - **The family's own distribution census at this head** (`python -m seedsmith trees census`, full output `tasks/reports/bcu2-12-tree-census.txt`): `trees=42 expected=1680 bound=560 refused=1120 overall=33.3%`, **`boundWithReadableAtoms=0 … readable=0.0% of bound`**, priced atoms by kind `stat.modify 344` / `stat.derived 0`, mechanism 141/840 vs magnitude 419/840, **no tree at 40/40** (best `might` 26, worst `spark` 1), one class-E ungenerated node (`wither: skill.wither-def-t9-n1` — the single remaining MechanismRamp shortfall, which the instrument itself calls *not a defect*), and `mixed` 20 / `stale` 22 trees with **1,066 records not the current vintage** — exactly the 1,066 nodes my own reading found with no `promptVersion` field, plus the instrument's own conclusion that *the document stamp cannot see it (per-node provenance is authoritative)*. The `stat.derived: 0` DEFECT line is **already filed** and BLOCKED (`tasks/passive-tree-repair-todo.md:42,381,416-417,499`; resolver side in BCU8.8's erratum), so this is the numeric baseline, not a new finding. ⚠ **Ordering dependency for this row:** the three generation-vintage metrics can all reach target while `readable` is still 0.0% — a corpus that binds but cannot be read contributes nothing in play — so BCU2.12 must not be closed on those metrics alone. Details: `tasks/reports/bcu2-12-tree-census.md`.
  - **J9's Verify line run directly at this head: `--check` is GREEN, and the verdict is unreachable by authoring.** `dotnet run --project gk-forge/tools/TreeBinder -c Release -- --check` → **exit 0, 0 `STALE` lines**, so the committed `gk-data/packs/fusion/data/generated/passive-tree/*.json` are byte-identical to a fresh binder run (the determinism half of *"`--check` green"*, and what `gk-forge/tools/TreeBinder/Program.cs:131-141` compares). The same run prints **42/42 `verdict=Fail`**, **1120 refusals**, **0 `(deliberate hole)`**: 612 `affix '…' does not exist in the shipped seed content` (49 distinct ids; top `atom.elpw-attune` 69), **507 `channel is a pool reference`**, 1 `affixIds must be 1..3` (`skill.wither-def-t9-n1`, the class-E node). **New:** `gk-core/src/FusionRpg.Core/PassiveTree/Binding/BinderRunReport.cs:60` fails a tree on *any* non-deliberate refusal, while `spec-channel-pool.md:8,33-34` makes a pool channel roll-time work the bake-time binder must not price — so no amount of affix authoring can turn those 507 into priced nodes and `verdict=Pass` is unreachable until either the verdict rule treats a roll-time pool refusal as deferred or the plan stops picking pool channels (a semantics ruling, not a lane change; it also means the repair plan's `G6` bar — `does not exist` → 0 *by expansion* — would close the 612 and leave the 507). Baseline delta against `passive-tree-repair-plan.md:39-45` (bound 266 / refused 1414 / affixNotGenerated 1356 / opMore 54): today bound 560 / refused 1120, with a pool-reference class the plan's buckets do not name. Transcript: `tasks/reports/bcu2-12-treebinder-check.txt`; details: `tasks/reports/bcu2-12-treebinder-check.md`.
  - **J10's own Verify line exercised, all four paths** (`python tasks/reports/bcu2-12-j10-review-gate-probe.py`): the `sheetRead` census gate refuses **no sheet rendered → exit 2** (`EXIT_CANNOT_RUN`, *"no sheet rendered for lot …"*), **sheet but no `sheetRead` row → exit 3** (`EXIT_REFUSED`, *"has no sheetRead row"*), **stale `sheetRead` row → exit 3** (*"… names revision 'rev-OLD', but the sheet on disk is now 'rev-A'"*), and **current row → exit 0** (gate cleared); the two refusal reasons are genuinely distinct, as `census_gate.py`'s docstring insists. **Committed state it guards:** `docs/research/passive-tree/_review/` and `data/seed/passive-tree/_review/` **do not exist** → 0 lots sheeted, 0 `sheetRead` rows → J10's acceptance (*"every tree was judged"*) is red by construction, and the probe against the real defaults refuses at the first reason. What is *not* covered is stated by the tool itself: `_cmd_trees_review`'s docstring — `--census` lands "exactly the gate … and nothing past it", the sampling tiers and acceptance ladder being H8+ and unbuilt. So J10's whole verifiable surface today is green. JSON: `tasks/reports/bcu2-12-j10-review-gate.json`; details: `tasks/reports/bcu2-12-j10-review-gate.md`.
- [x] **BCU2.13 — Small re-classifies: combat-unification F2b element-secondary (127 species) + species-build `doublecherry` `attackTempo`** · S-run · deps: **an owner call on the F2b selector definition** (A 138 / B 108 / C 126 — B reproduces the board's own 108; this row's reading below) — the `doublecherry` `attackTempo` half is **closed** (`tasks/species-build-todo.md`, 2026-09-07 owner-directed pick); spend released 2026-09-21; authorized by D4
  - **Lane `cmdc/bcu8-4` reading (2026-09-23): manager-run job in flight.** At this base the board has it `ep2-1`-gated (`tasks/run-board-20260920.md:1565`); the later `2004b5a42` records that `ep2-1` was already done, the row unblocked and is running (108 species — a live reading, not the register's 2026-09-07 "127"). Its outputs are `gk-data/packs/fusion/data/seed/creatures/**`, outside this lane's fence. **Both halves are now read model-free** (`python tasks/reports/bcu2-13-selector-reading.py`, corrected at `7fdc5b43b`): 904 species, 759 recipes, **450** carrying `elementSecondary: none`, and the stated selector (none **and** no recipe names it as an output) = **138**. The alternatives are **108** (also excluding recipe *inputs* — which is exactly the board's own figure, so that reading is reproducible under rule B) and 126 (A restricted to `pure`), so the definition is the owner's call, as F2b already reserved it. ⚠ **Both id-space traps are recorded, because this lane fell into the second one:** the CamelCase-vs-lowercase comparison `2004b5a42` names (raw = every `none` species, normalised = the real count), and **`rows[0]` row selection** — the anchors are FAMILY files holding many rows and `_index.json` names the file, not the row, so `rows[0]` read the family's base species for **355 of the 904** keys. Both scripts now resolve by exact `speciesId` (904/904 match; no file repeats one) and refuse rather than read a neighbour's anchor; the counts this lane published earlier (487 / 122 / 96 / 111) are superseded. `doublecherry`'s `attackTempo` is `"quick"` with `_provenance.confidence.attackTempo: "deterministic-fallback"` — **and that half is already CLOSED, not owed:** `tasks/species-build-todo.md` records the 2026-09-07 closure (owner-directed manual pick from the anchor's own emitted evidence, `CreatureSpeciesGen` 903 → 904, `BuildPlanGen` 84/84) and the tag is kept deliberately ("never disguised as a real model judgment"). Sized model-free with `python tasks/reports/bcu2-13-attacktempo-census.py`: **1 of 904 species** carries that tag (`DoubleCherry` alone; `high` 727, `split` 173, absent 3 — corrected figures), so the residual is the tag, not a population — and replacing it with a real vote is a **new** requirement the owning row does not carry, i.e. an owner call, not a lane's inference. **Correction to this row's earlier sub-bullet:** its "the half the run owes" phrasing was wrong on both counts and is superseded by this reading. Reading + provenance: `tasks/reports/bcu2-13-selector-reading.md` / `.json`. **Its shape, so the owner's content call has more than a total:** of the 138, side is zombie 67 / plant 71, **126 are `pure`**, and rarity is `sprout` 43 · `chaff` 34 · `grafted` 33 · `almanac` 12 · `cultivated` 7 · others 9 (top family `unclassified` 13, `undead+reanimated` 4, `metallophyte` 2) — overwhelmingly low-rarity species with no fusion lineage, which is why the selector cannot resolve it arithmetically and why F2b leaves it to content judgement. `selectorDistribution` / `noneSecondaryDistribution` in the JSON carry the same cut for the wider 450. **The vocabulary is closed and respected** (`elementVocabulary` in the same JSON, read from the adapter's `ELEMENTS`, not transcribed): primary `earth` 399 · `fire` 149 · `light` 108 · `ice` 102 · `dark` 86 · `air` 60, secondary `earth` 168 · `fire` 76 · `air` 59 · `ice` 58 · `light` 58 · `dark` 35 · `none` 450, with **`outsideVocabulary: []`** and **`speciesMissingPrimary: []`** — so F2b is a *presence* gap inside a closed vocabulary the corpus already respects, and a classify pass cannot be blocked by vocabulary here.
  - **CLOSED 2026-09-23 by the manager -- both halves done, and the dependency it named is satisfied by MEASUREMENT.** (1) The `doublecherry` `attackTempo` half was already closed (2026-09-07 owner-directed pick, `tasks/species-build-todo.md`). (2) The **F2b selector**: the row's own criterion was *"B reproduces the board's own 108"*, and the run measured **108**. Reproduced read-only by the manager at this head -- `python tasks/reports/bcu2-13-selector-reading.py` -> `selectorVariants = {A_none_and_not_a_recipe_output: 138, B_also_not_a_recipe_input: 108, C_A_restricted_to_pure: 126}`, `selectorMembersVariantB = 108 items` -- so the definition in use IS the board-reproducing one and no further owner call is owed. (3) The run itself: `tasks/reports/BCU2.13-run.md`, `run 20260923T000115.772708-6QR8PN: state=completed completed=0 failed=0 callsMade=0` -- zero calls, zero changes; the 108 keep `elementSecondary: "none"`, which the row anticipated. Preflight after regenerating the dump: nine checks PASS, 0 refusals.
    - **Finding carried with the tick:** a committed `_dump/_manifest.json` goes stale against its own dump when the dump is regenerated without re-running the preflight that records it -- any lane that regenerates the dump must re-run the preflight **in the same commit**, or the next consumer pays a refusal that looks like a tooling bug.

- [ ] **BCU2-R1 — reconcile the onboarding-rift closure banner with its still-open task headings** · S · deps: onboarding-rift owner ruling · *(manager, 2026-09-25, from the current program inventory)* — `tasks/onboarding-rift-todo.md:30` declares the work closed while 26 task headings still read `OPEN` (for example `:38`). This is a ledger contradiction, not 26 executable tasks and not evidence for a new product lane.
  - **Remedy:** the onboarding-rift owner must declare whether the header or the individual headings are authoritative, then reconcile the todo in one bookkeeping change with a short evidence note. Do not silently tick implementation rows, delete history, or fold this into BCU2.12/PassiveTree generation.
  - **Verify:** read-back of the reconciled todo, `python gk-core/scripts/audit-program-pipeline.py --only todo-task-blocks`, `git diff --check`, and the owning session boundary. Keep the result open until the contradiction is resolved.

> **Spend gate RELEASED 2026-09-21 (owner, in conversation):** *"update the spend gate for all, use lm
> studio gemma 4 26b qat, i don't think this is right to defer"* — every corpus run in this register
> (BCU2.10–2.13, incl. passive-tree J9/J10/J13) is authorised to spend **local** model time on LM Studio
> `google/gemma-4-26b-a4b-qat` (no API credit). The remaining `deps:` are **defect/dependency** gates
> (`J9-B1`'s two proven faults, BCU2.11's `SetCompletability` GAPs), not spend calls — those still block,
> and each closes by fixing its generator, never by asking the owner again.

### Checkpoint CB2
- [x] The packet is delivered and reconciled. — `owner-decision-packet.md` (BCU2.1), applied (BCU2.2).
- [x] Four plan pairs exist, each with its map status updated where a map owns them. — lawn (BCU2.4),
  deployment-hierarchy (BCU2.5), effect-pipeline (BCU2.6) each updated their own map's Plan/Tasks line;
  battle-wire-remainder (BCU2.7) has no single owning map by design (drawn from 2 closed todos + 2
  audits) — noted explicitly in its plan rather than silently skipped.
- [x] `--only map-plan-missing` no longer lists lawn-playable, lawn-tuning-profile or
  deployment-hierarchy — verified live, 2026-09-20: none of the three appear; `effect-pipeline` is
  also clean. (13 unrelated `trade-network`/`world-continuity` rows remain — never named in this
  program's todo, out of scope, not touched.)

## Wave 3 — route and close the remainders

### `aura-close-out`
- [x] **BCU3.1 — BP1 review of `spec-aura-binding-producer.md` via the D1 route** — **already done**,
  discovered 2026-09-20 while starting it: the concurrent `backlog-clear-20260920` session's own BP1
  re-verified the spec against current code and closed the gate (commit `c9facf71`, evidence
  `tasks/evidence-fragments/BP1.md`, merged into this branch at the mega-merge landing commit
  `0b33bbf9`). The D1 route (agent review) is exactly what happened — no owner ask needed.
- [x] **BCU3.2 — AU1: propagate decision 5 into `spec-aura-content.md` §10.2 / `aura-skill-ideal.md:863`**
  — **already done**, same discovery: `backlog-clear-20260920`'s AU1 (commit `67fddada`) made this
  exact edit; my own independent attempt at the same fix collided in the mega-merge and was resolved
  in favor of theirs (more complete wording) at the merge commit `0b33bbf9`.
- [x] **BCU3.3 — BP2 producer Core + Data** — **already done**: `AuraBindingPlan` (Core, pure
  reconcile, 7/7 tests) + `AuraBindingProducer` (Server, real endpoint I/O, 6/6 tests), commit
  `67fddada`, evidence `tasks/evidence-fragments/BP2-BP3.md`. Full Core 14525/14525, Server 656/656,
  Data 1646/1648 (2 pre-existing unrelated failures), 4 boundary guards green.
- [x] **BCU3.4 — BP3 server wiring (a real save-path caller of `RpgStore.Bind`)** — **already done**,
  same commit/evidence as BCU3.3 (BP2/BP3 shipped together) — `ResolveBindings` → `AtomPushService.Build`
  → `RpgHub.cs:105` → SignalR → `AtomPushReceiver` → `Funnel` traced end to end.
- [x] **BCU3.5 — BP4 live proof per `live-probe-standard.md` (real endpoint, real row, read back)** —
  **run live 2026-09-20** (`live-qa` session, merged into this branch via `features/mega-merge`,
  evidence `tasks/evidence-fragments/BP4.md`). Real RPG Server Debug scope (real endpoints, real DB
  row, real injector read-back, never fabricated): enabling `Might` through
  `POST /api/aura-runtime/1/enable` raised a live lawn plant's `combat.power.omni` from 0 to 3644,
  matching `AuraMagnitude.ReferenceChannelValue`'s own shipped output exactly — **PASS (grant half)**.
  Disabling withdrew the DB binding but the live injector never learned of it — `combat.power.omni`
  stayed at 3644 across two polls 2s apart — **FAIL (withdraw half), a real, structural, unfixed
  defect**: the atom-push wire (`PushAtomUnionAsync`) has no withdraw/reconcile message, additive-only
  by construction; not aura-specific (any future mid-session grant revocation hits the same gap).
  Correctly not fixed in-scope by the QA lane (module-sized change); routed to `aura-skill` **T24**
  (added this same commit) rather than left unrouted. A secondary defect (silent bind refusals) was
  found and fixed in the same live-qa pass, small and in scope.
  - Files: `tasks/aura-skill-todo.md` (T24 added).
  — genuinely still open. `backlog-clear-20260920`'s own todo keeps this ⛔ owner-run (needs a deploy
  and a live board); not attempted here.
- [x] **BCU3.6 — AU2 aura containers + `AuraBudget` (P(Θ)-tunable; no hand-picked constants)** —
  **already done**: twelve `world-buff.aura-*` containers authored from the shared `AuraMagnitude`
  formula, commit `3623153d`, evidence `tasks/evidence-fragments/AU2.md`
  (`gk-data/packs/fusion/data/seed/atoms/aura-content.json`, `gk-data/packs/fusion/data/seed/containers/aura.json`, `AuraMagnitude.cs`,
  `AtomPushService.cs`; magic-number/overflow audits clean, 5 boundary guards green).
- [x] **BCU3.7 — SR-14 (battle-derived-wire W6/W7) closed through aura-skill T13, or re-homed with a pointer**
  — **re-homed 2026-09-20** (not closed by T13 — re-checked live: T13 shipped 2026-08-30 and does not
  wire a battle-setup caller). Added `aura-skill` **T23** as the named owner (`AuraContentRow` still
  carries no rung/share; `AuraMagnitude.Compute` needs a caller that resolves them from a player's
  active set — neither T13 nor AU2 built that caller). Updated `battle-derived-wire-todo.md` Tasks 4/5
  and `battle-wire-remainder-plan.md`'s cross-program-edges section to point at T23 instead of the
  stale T13 reference. `audit-doc-citations.py --strict`: 0 HIGH introduced (confirmed via diff-hunk
  cross-check against each file's pre-existing HIGH findings).
  - Files: `tasks/aura-skill-todo.md`, `tasks/battle-derived-wire-todo.md`, `tasks/battle-wire-remainder-plan.md`.

### `creature-remainders`
- [x] **BCU4.1 — Overlap check: `creature-seed` T1–T12 (`CreatureRank`) vs convergence `species-progression`**
  — done 2026-09-20. **Decision: build in `creature-seed`, no fold, no overlap exists.**
  `creature-seed-todo.md` T1-T12 (`spec-species-rank.md`) is a 10-value content-generation-time rank
  tier for the seed matrix; `species-progression-map.md` (read in full) is player/empire runtime
  progression *levels* granting aptitude allocation — the word "rank" does not appear anywhere in
  `species-progression-todo.md` or its map. Recorded here rather than in `creature-seed-todo.md`
  itself: that file is fenced by the active, unmerged `cmdc/lane-c` session (confirmed live —
  `git log --oneline cmdc/lane-c -- tasks/creature-seed-todo.md` shows a Task 13 commit just landed
  there, `git merge-base --is-ancestor cmdc/lane-c HEAD` returns false). Read-only per the task's own
  framing — no edit to the fenced file needed to answer the overlap question.
- [x] **BCU4.2 — `creature-progression` D2.3 isolation regression sweep** · S · deps: BCU1.6 · Verify: verify-change — done 2026-09-20 (re-check + route). **The row's own blocker was a stale premise, the fourth this run:** it said D2.2 was "only PARTIAL since 2026-09-08 — all 3 acceptance criteria still unchecked", but a todo box is not evidence. Read the code: `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Expeditions.cs:332-336` states *"Expedition rewards level the specimen only; species progression is awarded by its own general-spawn activity projector"*, `:330` calls the transactional unlock helper, and the only species ledger write is the once-ever discovery row (`:347-355`'s `species:{id}` dedupe + `INSERT OR IGNORE`, `RpgStore.Progression.cs:284`). **D2.2 is done-in-code**, so its three boxes were corrected in `tasks/creature-progression-todo.md`, and **D2.3 is unblocked**. D2.3's own clause 2 ("no unique/Commander path awards species XP or reads `EffectiveSpeciesAllocation`") is **already enforced and green** — `ProgressionLayerSelectorGuardTests` + `SpeciesAllocationSeamTests`, re-run here (6/6). Clauses 1 (the per-consumer sweep) and 3 (the `EmpireGeneral` behaviour test) are **left to `creature-progression` as its own named remaining scope**, recorded on D2.3's header and boxes rather than half-done here: they span `gk-core/src/FusionRpg.Data/**` and `gk-core/src/FusionRpg.Server/**`, outside this lane's fence.
  - Files: `tasks/creature-progression-todo.md`.
- [x] **BCU4.3 — `creature-lawn-deploy` T4.1 (deferred-death `killerPtr` bridge) / T4.4 + CP4: confirm an owning session, or schedule here** — done 2026-09-20 (routing). No active session owns
  `creature-lawn-deploy-todo.md` (checked every currently-`active` session record's `paths`). Read the
  full T4.1→T4.2→T4.3→T4.4→Checkpoint 4 chain (`creature-lawn-deploy-todo.md:945-1049`): T4.1's real
  remaining gap needs a **deferred-death bridge** — the shipped game defers `Plant.Die` ~16ms after
  `TakeDamage`, so the strict synchronous `killerPtr` rule the spec requires currently emits nothing;
  a 2026-09-08 live melee probe already confirmed the timing gap. T4.2-T4.4 are each PARTIAL/TODO and
  depend on T4.1 closing first. **Scheduled, not built here**: this needs a real live-injector probe
  (per `live-probe-standard.md`, Game Injector Debug scope) to find the actual deferred-death hook
  point — genuinely `qa-tester`-shaped work, out of a routing task's own S-scope and out of a docs/code
  batch that cannot deploy the game. Left named and open at its own file, not silently dropped.
- [x] **BCU4.4 — `creature-standalone` F2.3: the real differently-rarity'd fusion test (blocker cleared by F2.4/F2.5)** — done 2026-09-20. Wrote
  `FusionInheritancePicksTests.A_pick_is_priced_by_its_own_source_rarity_never_the_fusion_outputs_rarity`.
  **Real finding while writing it**: F2.3's own box wording ("two differently-rarity'd sacrifices")
  describes an impossible scenario — `CreatureRecipeCatalog.BuildDeterministicOnly` always draws both
  of a recipe's inputs from the SAME rung (a documented invariant, pinned by
  `CreatureRecipeCatalogTests.Inputs_are_distinct_band_below_and_never_capture_only`); confirmed live
  by trying to find a mixed-rarity recipe pair and getting `Sequence contains no matching element`.
  Wrote the real, always-testable claim instead: pick cost keys off the picks' shared source rarity,
  never the output's rarity (source is always strictly below output). A second real finding along the
  way: the first fusion of a never-before-seen species+recipe also credits a discovery bonus (recipe
  + species, `RpgStore.Fusion.cs:400-419`) — the test reads that back from the outcome's own
  `DiscoverySouls` rather than re-deriving `SoulEarnPolicy`'s formula, keeping the assertion scoped to
  pick-pricing only. Corrected `creature-standalone-todo.md` F2.3's box in the same commit.
  Verify: `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter FusionInheritancePicksTests` — 8/8, run
  twice for determinism (hard-edge rigor), both green.
  - Files: `gk-core/tests/FusionRpg.Data.Tests/FusionInheritancePicksTests.cs`, `tasks/creature-standalone-todo.md`.
- [x] **BCU4.5 — File roster-balance's handed-off species findings (grid occupancy, non-monotone rarity, `posture: unresolved`) as a real task in `creature-seed-todo.md`, or record them as dropped** · XS · deps: BCU4.1 — done 2026-09-20. **The `cmdc/lane-c` fence had gone stale, exactly like the P11 gate:** `git merge-base --is-ancestor cmdc/lane-c HEAD` now returns 0 (it came in through the orchestrator's `features/mega-merge` merge), and every worktree reports `tasks/creature-seed-todo.md` clean, so filing was safe. Filed as **RB-H1** in `tasks/creature-seed-todo.md`, a real task with acceptance — not dropped (the findings are real: 19 GAP rows, grid occupancy 65/252 cells = 257‰ against a 900‰ target, non-monotone rarity, single-element share 973‰, posture imbalance, aptitude skew, from `docs/architecture/roster-balance-map.md:59-66`). **The sharper half is the metric-blindness finding, and it is recorded first because it is the one that makes the rest unfalsifiable:** `posture: "unresolved"` (12 rows) is invisible to *every* metric — `UnresolvedCount`'s `VOTED_FIELDS` omits `posture`, and `PostureBalanceMetric` silently drops rows matching none of its three keys. RB-H1 asks for that fix before the axis audit, and states that each reading must be dispositioned (content gap / tuning change / accepted-with-reason) rather than assumed to be a defect.
  - Files: `tasks/creature-seed-todo.md`.
  — ~~blocked on the same `cmdc/lane-c` fence as BCU4.1~~ **(confirmed live, 2026-09-20; ✅ the fence has since cleared — `cmdc/lane-c` is an ancestor of HEAD and the file is clean in every worktree, which is why this closed on 2026-09-20):** filing a real
  task requires editing `creature-seed-todo.md`, which that active session is currently committing to.
  These are real, valuable findings (19 GAP rows from `creature_roster.py`'s first real run against
  the corpus, `roster-balance-map.md` — grid occupancy 257‰ vs 900‰ target, non-monotone rarity,
  `posture: "unresolved"` invisible to `UnresolvedCount`/`PostureBalanceMetric`) — **not** to be
  recorded as dropped; genuinely deferred until the fence clears, not silently skipped. **(✅ The fence cleared — `cmdc/lane-c` is an ancestor of HEAD and the file is clean in every worktree; filed as RB-H1 above.)**
- [x] **BCU4.6 — Re-check `party-dungeon` F4 (`CreatureMintSpec.Level`) and F5 (`poolFilter`) against convergence-shipped DTOs; route the F1 threat-audit to creature-seed module 7** — done 2026-09-20, all three clauses now met.
  F4 re-confirmed live: `gk-core/src/FusionRpg.Contracts/CreatureDtos.cs:58-70`
  — `CreatureMintSpec` still has no `Level` field (10 properties, none named `Level`); the 2026-09-07
  finding holds unchanged against any convergence-shipped DTO. F5 re-confirmed live:
  `gk-core/src/FusionRpg.Core/Creatures/SummonRoller.cs:61-62` — `Roll`'s real signature is still
  `(SummonBannerDef banner, ElementTypeId? focusElement, int count, PityState pity, SeededRng rng)`,
  no `poolFilter` parameter; also unchanged. **F1 is now routed** — the `cmdc/lane-c` fence that blocked it had gone stale (lane-c is an ancestor of HEAD after the integration merge, and the file is clean in every worktree), so the threat-audit row **TB-H1** was filed in `tasks/creature-seed-todo.md`, naming module 4 (`threat-band`) and module 7 (`classify-pipelines`) as its owners with the live `721 of 906` reading and the acceptance `party-dungeon` F1 must be able to close on. Deferred is now done, not dropped.

### `world-remainders`
- [x] **BCU5.1 — `world-stage`: confirm its status. If still "proposed", decide ownership of loam L44/L45/L46/L50 (re-homed 2026-09-03; L47–L49 obsolete)** — done 2026-09-20.
  **`world-stage` is not "proposed" — it is fully BUILT AND SHIPPED**, found live: `tasks/world-stage-todo.md`'s own header still said "proposed 2026-09-03, pending owner review; no task
  is authorized to start" while its own Checkpoint C section reads "complete" (0 open boxes, 141
  done, all 15 modules, `W1`-`W108`, 4 boundary guards green, full test suites green). Corrected both
  stale headers (`world-stage-todo.md`, `docs/architecture/world-stage-map.md`).
  **Loam ownership answered** (cross-referenced from `backlog-clear` LO0, `tasks/backlog-clear-todo.md`
  Phase 6, merged into this branch 2026-09-20): `world-stage` delivered every one of L44/L45/L46/L50's
  underlying needs (`world-stage-todo.md:2933`, `turnPlayback.ts`, the unified command surface,
  `ProspectedSectorIds`+`Dowse`) — verified by grep there, not assumed. L47-L49 (Ward Core/endpoint/UI)
  are real but their underlying verb was separately retired by owner decision Q3 (2026-09-19,
  `spec-world-warden.md`, `RulesetVersion` 13) — **delivered-then-retired**, not a live feature; that
  correction was found and recorded during this session's `features/mega-merge` merge (commit
  `0b33bbf9`). Nothing further to build here.
  - Files: `tasks/world-stage-todo.md`, `docs/architecture/world-stage-map.md`.
- [x] **BCU5.2 — Split `party-dungeon` D4.30 (six-domain content run) into real tasks in `party-dungeon-todo.md`** — done 2026-09-20, no active session fences that file (checked).
  **The split this task asked for is unnecessary — it already happened, in substance, inside D4.30's
  own entry.** Read the WHOLE entry (not just its opening line): the 2026-09-06 "SCOPE FINDING...
  dramatically larger... propose a split" premise is followed by three of its own dated 2026-09-07/08
  progress notes showing quest (25 anchors), layout (6 templates), supply-ext (31), event (50),
  encounter (40) and room (92) content ALL shipped real and validator-clean, plus the six-domain
  pipeline-composition mechanism itself built and proven (`DomainRealPipelineTests.cs`). The entry's
  own words: "the task-split this finding originally proposed is still the right shape... already
  closed in practice even though no new D-numbered task was formally minted for them." Minting new
  `D4.32`+ tasks for already-completed work would duplicate it, not split it. **Corrected the stale
  opening framing instead** — a future reader who only reads the first line would otherwise re-derive
  a split that's already done. The one thing genuinely still open (D4.30's own checkbox, correctly
  unticked) is external: every domain refuses on the threat-audit gap (F1, `creature-seed` module 7,
  itself blocked on the `cmdc/lane-c` fence — same one blocking BCU4.6). `audit-doc-citations.py
  --strict`: 8 pre-existing HIGH findings, none in my inserted text (confirmed via `git diff`
  context-line check — the citation lines shifted position but carry no `+`/`-` diff marker).
  - Files: `tasks/party-dungeon-todo.md`.
- [x] **BCU5.3 — Spec note for the `RpgHub.Resume` auto-policy (D2.16 / D5.11)** — **already done**,
  discovered 2026-09-20 while starting it: the `combat-ai` spec/plan session (BCU2.9/2.9a, done
  earlier this same session) already covers this exact gap. `combat-ai-map.md` module 13
  (`delve-automated-wiring`): "`RpgHub.Resume` and the delve session take the router + core policy as
  `automated`... the spec's 'never `StubIntentSource`' boundary is honoured." `combat-ai-todo.md`'s
  own cross-program-edges section (line ~768) names the exact same gap and explicitly says **"Also
  tracked as `BCU5.3`"** — the two sessions already cross-referenced each other. `CAI3.4`
  (`DownedAllyKeysOf` and the role policy) + `CAI3.5` (`RpgHub.Resume` stops throwing,
  `DelveAutomatedPolicy` as the one composition root, `NotImplementedException` removed) are the real
  build tasks; `party-dungeon`'s own `StartSession` caller needs no further spec work — it calls the
  same `DelveAutomatedPolicy.For(store)` `Resume` will. No new spec note needed; writing one now would
  duplicate `combat-ai-map.md`'s own module 13.
  - Files: none (verification-only; no doc needed a change).
- [x] **BCU5.4 — Route: F8 entrance placement (world generator wave 4), F10 contract prices not Θ-scaled (creature-contracts), empire-development notify sources → verify `notification-ssot` ledger closes them** — done 2026-09-20.
  **F8 re-confirmed live, still genuinely open**: no `world-generator` implementation exists anywhere
  under `src/`/`tools/` (grep-confirmed); `world-map-todo.md`'s own two mentions of it are both future
  constraint notes for an unbuilt wave 4, not a hidden build. Correctly stays routed at `world-generator`
  (wave 4 of `world-map-program`), not attempted here.
  **F10 re-confirmed live, still genuinely open**: `ContractPolicy.BaseUpkeepPerDay(rarity)`
  (`ContractPolicy.cs:124-126`) still returns a flat `int` from a rarity-keyed table, not a `P(Θ)`
  read — the finding's own framing (raise with the contracts owner) still applies; not a fix this
  routing task should attempt.
  **notification-ssot ledger verified to close the empire-development notify-sources item**: both
  sides of the cross-link already exist and agree —
  `notification-ssot-map.md`'s own "What the consuming specs get from here" table names
  `empire-development-map.md`'s open item (110-119) as served by `world-notify-source`/
  `cache-notify-source`, and correctly identifies `empire-development-map.md`'s own claim ("every
  event already fires a report line, nothing needs re-plumbing") as **false for 2 of 3 events**.
  `empire-development-map.md:117-119` already carries the matching cross-reference note pointing back.
  Nothing further to route — already closed, in both directions.
- [x] **BCU5.5 — base-defense siege `Assembled`: design note for a Core↔Server loadout bridge (`EquippedActionIds`)** — **already done, by a different and cleaner
  route**, discovered 2026-09-20: the premise (a Core↔Server bridge into `EquippedActionIds`) is
  stale. `DistrictAssaultResolver.BuildAnimateSetups` (`DistrictAssaultResolver.cs:452`) already sets
  `AdditionalHeldActions = ConstructionActions.CompiledActionsForGrant` for the attacker side — a
  purely additive sibling field to `EquippedActionIds` (`BattleModels.cs:124`,
  `ConstructionActions.cs:126-131`'s own doc comment: "WITHOUT touching that risky, shared
  `EquippedActionIds`/`ActionCatalog` resolution path at all"), read by `BattleRunState.cs:593`. No
  bridge into `EquippedActionIds` was needed or built — the design deliberately routed around it.
  **What genuinely remains for `Assembled`** (not this task's own scope, and not a bridge question):
  a real craftable content item replacing the `AssembledConsumableItemId` placeholder
  (`structure-corpus`'s own job), and a live `IIntentSource` cell-choosing policy analogous to
  `ConstructionAi.ChooseBuiltSite` deciding to USE `Assembled` at all.
- [x] **BCU5.6 — Re-check `ActionStockCommit` general battle dispatch against convergence `action` (lane A)** — done 2026-09-20.
  **Re-confirmed live: fixed.** `ActionStockCommit.TryCommit` now has THREE real production callers
  (grep-confirmed, not the stale zero the earlier finding recorded): `BasicAttack.cs:129`,
  `Battle/Siege/ConstructionActions.cs:269`, `TimelineDispatch.cs:169` — every shipped attack profile
  now spends its compiled `StockDemands` at its own commit point. This matches
  `base-defense-todo.md`'s own later-session correction in place (lines ~841-860: "supplying
  `firingAction` spends its compiled `StockDemands` via `ActionStockCommit.TryCommit`... every shipped
  profile now call `ActionStockCommit.TryCommit` at their own commit point"). Nothing further to fix
  or route — already closed, confirmed against live code rather than the stale "zero callers" claim.

### `item-remainders`
- [x] **BCU6.1 — Plan item modules 24 `equipment-activation` and 25 `set-requirement-reconciliation` (append to `item` plan, or a follow-on pair)** — **already done**,
  discovered 2026-09-20 while starting it: `tasks/item-todo.md`'s own Phase 7 already carries the full
  plan for both modules — P7.3/P7.4 + Checkpoint 7B (module 24, real acceptance/files/scope/deps
  against `spec-equipment-activation.md`'s own testing strategy) and P7.5/P7.6/P7.7 + Checkpoint 7C
  (module 25, against `spec-set-requirement-reconciliation.md`). The `paperwork-reconcile` P7 note
  that routed readers HERE to "plan" modules 24/25 was itself stale — it pointed past the very
  section that already answers it. Corrected in place (`tasks/item-todo.md`, same commit) instead of
  writing a duplicate plan.
  - Files: `tasks/item-todo.md`.
- [x] **BCU6.2 — Re-verify the ~12 "seed → concrete" item lines against live `effect_container` rows; close or keep each with evidence** — done
  2026-09-20 (delegated to a background investigator agent, findings applied and doc-citation-verified
  by me). 13 distinct claims found and checked live, not re-quoted:
  - **5 CLOSED, corrected in `item-todo.md`**: the 36-set/~904-species/~904-charm generative pass
    (910/885 files + 954 charms now on disk); the `unique` drop entry kind (`DropTableModel.cs:200-204`
    "Unique REMOVED 2026-09-06"; `LootPipeline.cs:378,567`'s `MintUnique` real); module 17's seed→
    concrete gap for the drop path (`UniqueContainerBuild.From` builds the container at mint time).
  - **2 PARTIALLY CLOSED / blocker MOVED, corrected**: the 36-Strain/66-Splice combination pass
    (25/36 + 51/66 = 76 of 102 ran, not zero); `forge` cannot mint — the stated cause (no
    `effect_container`/`item_base_type`) is dead (`ItemWorkbench.cs:294-300`,
    `RpgStore.BaseTypes.cs:21`), the real blocker is now a boot-wiring gap
    (`gk-core/src/FusionRpg.Server/Program.cs:712-723` never passes `forgeMintCells`/`forgePowerTuning`) —
    fixed at all 4 sightings (lines ~6183, 9526, 9539, 9642).
  - **1 now materially live, corrected**: `creature.*` themeKeys not resolving in
    `ItemSeedValidator` — was prospective, is now **844 real `RegistryValueUnknown` errors**
    (`dotnet run --project gk-forge/tools/ItemSeedValidator`, 2026-09-20), one per persisted species set.
  - **5 STILL OPEN, re-confirmed unchanged, not re-edited** (already accurately stated): the
    `socket-word`→`combination` five-site rename bundle (still all 5 unmoved); no consumable mint arm
    (module 18); no menu executor (`ConsumableRules.MenuExecutorAbsent`, zero raisers); no
    `consumableSlots` on any `girdle` base type; the seedsmith band→row generator (still boots
    hand-maintained `data/seed/loot/tables*.json`); `item_granted_action.container_id` has no FK.
  - **No K2/owner-charter run needed for anything above** — the corpus runs already happened; nothing
    found requires a new model call to close.
  - Found and fixed a self-inflicted citation defect while applying this: 3 new bare `Program.cs`
    citations (ambiguous among 42 files sharing that basename) — fixed with the full path.
    `audit-doc-citations.py --strict`: 16 pre-existing HIGH, 0 introduced (confirmed by line-number
    filter against all 9 edit hunks).
  - Files: `tasks/item-todo.md`.
- [x] **BCU6.3 — Re-check the X7/D27 `ContainerKind` citations against `ContainerRow.cs`** — done
  2026-09-20. **X7 is fully landed and has been for a while — six separate stale "not landed" /
  "genuinely still open" claims found across `item-todo.md`, all corrected.** Live-verified:
  `ContainerRow.cs:31-43` ships `Gem`, `Charm`, `Combo` and `Consumable` (D27's four asks), plus
  `Relic`/`EmpireTitle`/`ActorTitle`/`SpeciesProgression` appended since (16+ values total, not the
  six/seven the stale lines kept re-measuring). `ConsumableLimits.ConsumableContainerKindAvailable`
  (`ConsumableDef.cs:230`) is `true` — the one flip-line one bullet named as the owner's decision
  point already flipped, live, 2026-09-07. Corrected all six sightings in place (lines ~3915, 4292,
  5945-5951, 6802, 8028, 8657), preserving each one's historical narrative rather than deleting it.
  `audit-doc-citations.py --strict`: 16 pre-existing HIGH findings, none inside any of the six edit
  ranges (confirmed via line-number filter against each hunk).
  - Files: `tasks/item-todo.md`.
- [x] **BCU6.4 — Schedule the named internal residuals (forge mint, reroll/transfer, socket-imbue recipe, `SetDisclosure` multi-set, recipe listing route)** — done 2026-09-20. Added
  `item-todo.md`'s new Phase 8 (P8.1-P8.5 + Checkpoint 8): each residual was already named, with a
  reason, somewhere in the file (never silently skipped) — this gives each one a real task id, real
  acceptance criteria drawn from its own already-investigated finding (not invented), and a files
  list. P8.1 (forge mint) reuses BCU6.2's own live finding (the boot-wiring gap in
  `gk-core/src/FusionRpg.Server/Program.cs:712-723`) rather than re-deriving it. `audit-doc-citations.py
  --strict`: 16 pre-existing HIGH, 0 introduced.
  - Files: `tasks/item-todo.md`.

### `ui-remainders`
- [x] **BCU7.1 — Delete orphaned `web/fusion-rpg-web/src/ui/actor/GearTab.tsx` (now deleted, + its test); note the `ProgressionTab` name collision in a comment** — done 2026-09-20.
  Confirmed genuinely orphaned before deleting: zero non-test importers (grep), no barrel export
  (`ui/actor/index.ts` never names it); `ActorPanel.tsx`'s own real tab set uses `KitTab` from
  `CatalogTabs.tsx` for the "kit" slot, not `GearTab`. Deleted both files. Added the naming-collision
  comment to `ProgressionTab.tsx`: it is NOT the tab `ActorPanel.tsx` renders (that slot is
  `AptitudesTab`) — `ProgressionTab` is used only by the standalone `AptitudesPage.tsx`.
  **Verification-boundary gap found and reported, not self-fixed**: `verify-change.ps1` refused with
  "VERIFICATION BOUNDARY MISSING" for `gk-web/web/fusion-rpg-web/src/ui/actor/**` —
  `gk-core/scripts/verification-boundaries.v1.json` (owned by `test-verification-boundary`) has no mapping for
  this tree at all. Verified manually instead: `npx vitest run src/ui/actor/` (22 test files, 259
  tests, all green) and `npm run build` (tsc --noEmit + vite build, both green) — `npm ci` was also
  needed first (this worktree had never installed FE deps).
  - Files: deleted `GearTab.tsx`/`GearTab.test.tsx`; edited `ProgressionTab.tsx`.
- [x] **BCU7.2 — `disabledReasonGuard` fixes in `CommandersLayer.tsx` / `CommanderSheetFooter.tsx` (GG-55 = party-dungeon F9)** — **already fixed**, discovered
  2026-09-20: no session fences either file (checked); live-verified both already carry a real `title`
  on every `disabled` button — `CommandersLayer.tsx:155,190` (`title={setDefaultDisabledReason}`,
  both buttons) and `CommanderSheetFooter.tsx:41` (real path is `ui/actor/`, not `ui/commander/` —
  the task's own path was stale) (`title={setDefaultPending ? "Working…" : isDefault ? "Already the
  default commander" : undefined}`). `npx vitest run src/ui/disabledReasonGuard.test.ts`: **6/6
  green, 0 violations** — the fix landed somewhere upstream of this session (most likely one of the
  many `features/mega-merge` lanes) between when `party-dungeon-todo.md`'s own dated notes recorded
  this as a stable pre-existing baseline failure and now. Nothing left to build.
  - Files: none (verification-only).
- [x] **BCU7.3 — gui-lego queue: plan P2 Creatures, P3 Relics/Commanders, and the P4 remainder as rows in the queue's plan** — **all three already done**,
  discovered 2026-09-20: no plan was needed — `CreaturesLayer.tsx`, `RelicsLayer.tsx`,
  `CommandersLayer.tsx`, `FusionLayer.tsx`, `PactsLayer.tsx`, `ExpeditionsLayer.tsx`,
  `AlmanacLayer.tsx` and `ChronicleLayer.tsx` are all real, lazy-loaded and rendered in
  `SanctumStage.tsx`; the "remaining Actor tabs" (Status/Elements/Kit via `CatalogTabs.tsx`, Paths via
  `PathsTab.tsx`) are all real. Corrected both `menu-refactor-queue.md`'s priority table (P2/P3/P4
  rows) and `gui-lego-todo.md`'s own mirrored bullets, which independently carried the same stale
  "Not started"/"real remainder still open" claims. The only genuinely open P4 work stays the two
  explicitly-gated sub-rows (`P4 · Notices`, `P4 · Builds`), unchanged.
  - Files: `docs/architecture/gui-lego/menu-refactor-queue.md`, `tasks/gui-lego-todo.md`.
- [x] **BCU7.4 — actor-hud boss-tier signal from expeditions (`ActorHudComposer.cs:33`) + perf B2 write-up** — done 2026-09-20 (mixed: routed + published).
  **Boss-tier signal: re-scoped, not built.** `ActorHudTier.Boss` already exists in the enum
  (`ActorHudTier.cs:7`); `ActorHudComposer.Compose` only ever assigns `Unique`/`Normal`, and
  `ActorHudBuilder.Build` (the Injector-side live reader) has no expedition/boss context and no
  ptr-keyed override cache for it (unlike the real `ActorHudMeterOverride`/`InjectorDerivedOverride`
  precedents). This is a real multi-file Core+Injector wiring task, not the **S** size stated —
  corrected in `backlog-clear-todo.md` Phase 9 rather than force-built here.
  **Perf B2 write-up: done.** Published [B2-baseline-published-2026-09-20.md](../docs/research/perf/B2-baseline-published-2026-09-20.md)
  from the four raw baseline captures that already existed on disk (never previously written up),
  as a factual table without inventing a causal before/after story — one capture has an unexplained
  ~18.4s `maxMs` outlier and no doc/commit ties any `-oN` suffix to a specific optimization, so the
  write-up says so plainly rather than guessing.
  - Files: `tasks/backlog-clear-todo.md`, `docs/research/perf/B2-baseline-published-2026-09-20.md`.
- [x] **BCU7.5 — Identify "P4 rail work" for achievement-title T7b; schedule T7b behind it** — done 2026-09-20.
  Identified: "P4 rail work" is `gui-lego`'s own P4 priority (other rail layers + remaining Actor
  tabs) — confirmed fully shipped this same session (BCU7.3). The FE-toolchain half of T7b's own
  blocker is also cleared (`npm ci` run successfully, BCU7.1). **T7b itself stays genuinely open**:
  no Hall-console/actor-title-tab React component exists yet (checked by name, zero hits) — real,
  unbuilt fold+mount work, plus an owner-only side-by-side visual gate. Corrected the blocker
  description in `achievement-title-todo.md` from "needs FE toolchain + owner eyes" to the accurate
  current state, and scheduled it as buildable-now rather than tooling-blocked.
  - Files: `tasks/achievement-title-todo.md`.
- [x] **BCU7.6 — story-scene F3/F6/F7/F8 + T27b FE→injector cue bridge (decision 9): route or schedule** — done 2026-09-20.
  **F7 closed for real**: its "outside this session's fence" claim was stale — no session held
  `menu-refactor-queue.md` (confirmed via active-session scan). Added the real `story-scene` row (7
  pieces + `storySceneTokens.ts`, checked by file listing, not guessed) to the queue's `Status`
  section, matching the `W2 Wonder composer` precedent for a non-rail consumer. Also fixed the same
  file's own separately-stale "P2+ Not started" row while there (superseded by BCU7.3's own finding).
  **F3, F6, F8 stay open, correctly** — each is a genuine content/product decision or real unbuilt
  mechanical work (dev-footer wording; promoting piece specs; wire-or-delete a config knob), not a
  defect this routing task should force. **T27b re-confirmed still genuinely blocked**: no
  `WebMessageReceived`/host-object channel in `OverlayViewHost.cs`, zero `postMessage` calls anywhere
  in the web FE — the shared bridge does not exist, unchanged since 2026-09-16. Corrected the file's
  own stale summary counts (F1 SUPERSEDED, F7 done → 3 open follow-ups, not 5).
  `audit-doc-citations.py --strict`: 7 pre-existing HIGH on `story-scene-todo.md`, 0 introduced
  (confirmed via diff-hunk range); 0 HIGH on the queue file.
  - Files: `tasks/story-scene-todo.md`, `docs/architecture/gui-lego/menu-refactor-queue.md`.
- [x] **BCU7.7 — shield-sheet D8a/D8b, player-guide PG-F2/F3/F5/F6: schedule as low-priority rows** — done 2026-09-20.
  All six already correctly recorded as open, low-priority rows in their own files
  (`shield-sheet-todo.md`'s "Deferred (D8)" section; `player-guide-todo.md`'s Follow-ups table) — no
  file changes needed. Spot-checked the one concretely re-checkable premise: **SS-D8a re-confirmed
  still genuinely blocked** — no `regenText`/`RegenRate` symbol anywhere in
  `gk-core/src/FusionRpg.Core/Combat/Shield/` (grep-confirmed), so the runtime still does not expose a rate
  for it to segment against. The rest (SS-D8b/PG-F2/F3/F5/F6) are each already named with a real,
  plausible dependency (P3, packaged-zip/interactive-battles/patron-live landing, Lingui chrome
  strings, a tuning-driven unlock program, ongoing content polish) and are correctly left open rather
  than force-closed on a guess.
  - Files: none (verification-only; both files already correct).

### `infra-remainders`
- [x] **BCU8.1 — combat-math-dedup D17: add `nerve.unsettled/shaken/afflicted` VFX apply cues to `VfxCatalog.cs` (live bug; do first)** — done 2026-09-20.
  Added the 3 missing rows to `VfxSeedCatalog.StatusFx` (`VfxCatalog.cs`) — was 21 rows against
  `StatusCategoryRegistry`'s 24, exactly the drift D17 named. Each nerve tier now produces a real
  transient apply cue (Burst+Flash, no sustained aura — same shape as the engine-wrapped vanilla
  statuses, since no `StatusSustainFx` row names any nerve tier yet). Fixed the stale "one row per
  catalog status" comment and added the join-closure guard the task's own AC asked for
  (`StatusFxCategoryClosureTests.cs`, new file). **Real hazard found and fixed before landing**: the
  first draft asserted closure against `StatusCategoryRegistry.AllStatusIds` directly — that property
  reflects a SHARED, MUTABLE, process-wide static dictionary (`ExhaustionPolicy`/`StanceRuntime`'s own
  instance constructors call `StatusCategoryRegistry.Register` for `exhaustion.*`/`stance.guard` at
  construction time, not compile time), exactly the "tests that touch process-wide state" hazard the
  implementer-hard contract names. Proven live: the full `FusionRpg.Core.Tests` run failed this exact
  assertion (3 extra ids from unrelated test classes) while the Vfx-namespace-only run did not — pure
  test-order pollution, nothing to do with this fix. Rewrote the test to pin the STATIC, hand-authored
  24-entry vocabulary declared directly in `StatusCategoryRegistry.cs`'s own `Map` initializer instead
  — a closed vocabulary a developer edits, not a derived population (validation-ssot.md) — so it stays
  deterministic regardless of process-wide test order. Also fixed the now-stale exclusion comment in
  the pre-existing `StatusVfxCuesTests.Every_catalog_status_has_a_seeded_apply_recipe` (it claimed
  nerve.* has no cue recipe, which stopped being true) and bumped `VfxRulesAndCatalogTests`'s
  closed-vocabulary catalog-count pin (29 → 32, the test's own comment explicitly sanctions this: "a
  new VFX cue is a reviewed change" — this is that review).
  **Determinism proven per hard-edge rules**: full `FusionRpg.Core.Tests` run (14,790 tests) then a
  second `--filter Vfx` run (174 tests), both green for every test this fix touches. Two unrelated,
  confirmed pre-existing failures found along the way and correctly left alone: `AtomBenchGuardTests`
  (a machine-load-timing flake, unrelated code) and `SocketOperationsTests.
  The_legacy_socket_word_corpus_is_ordered_and_awaits_module_21s_retirement` (a real defect from
  `save-share-hierarchy` SSH2.6's own file retirement, `git log` confirms — that lane's test to fix,
  not this one's). `audit-magic-numbers.py --summary`: no Vfx findings (RGB literals are presentation,
  matching every pre-existing `StatusFx` row).
  - Files: `gk-core/src/FusionRpg.Core/Vfx/VfxCatalog.cs`,
    `tests/FusionRpg.Core.Tests/Vfx/StatusFxCategoryClosureTests.cs` (new),
    `tests/FusionRpg.Core.Tests/Vfx/StatusVfxCuesTests.cs`,
    `tests/FusionRpg.Core.Tests/Vfx/VfxRulesAndCatalogTests.cs`.
- [x] **BCU8.2 — Injector write-path honesty: route the three bare clamps (`EntityStatWriter.cs:500-501`, `GameHooks.cs:780,929`) through `ClampToInt32Reporting`; D22 parity test for both `ZombieCombatFields.ClampToInt32` bodies** — done 2026-09-20.
  All four calls at those three now-stale line numbers (`EntityStatWriter.cs:558-559` LimHealth gate,
  `GameHooks.cs:911,1062` plant/zombie `TakeDamage`) route through `ClampToInt32Reporting`, so an
  int32 saturation is a `stat.writer.clampBoundary` proof event instead of a silent clamp. The wrapper
  went `private` → `internal` so `GameHooks` shares the one reporting path rather than forking a copy;
  its doc comment now says so. Field names pin the boundary (`plant.maxHp`/`plant.hp` src
  `limhealth.gate`; `plant.damage`/`zombie.damage` src `GameHooks.*TakeDamage`).
  **Also closed combat-math-dedup Task 18 (D22)**: new `InjectorWritePathHonestyGuardTests` reads both
  `Bridges/pvzrh-3.9` and `pvzrh-3.8.1` `ZombieCombatFields.ClampToInt32` bodies and asserts them
  equivalent, with the duplicate's reason (compile-time profile exclusion in each host csproj) in the
  test's own comment. Two extra non-vacuity pins: the bodies must still name `int.MaxValue`/`int.MinValue`
  (equivalence alone would pass on a `return (int)value` silent narrow), and the route guard proves it
  actually scanned `GameHooks.cs`/`EntityStatWriter.cs`. The route guard was mutation-tested — a temp
  probe file reintroducing a bare clamp failed it by name, then was removed.
  `verify-change.ps1` guard module: 572 passed / 3 failed, all three pre-existing and outside this diff
  (`FusionRpg.FileMove.Tests`'s sequential stdout/stderr read from lane D, and two
  `VerificationBoundaryWorkflowTests` 120 s-timeout failures where the guard script itself prints OK in
  3m05s under the current machine load).
  - Files: `gk-fusion/src/FusionRpg.Injector/Stats/EntityStatWriter.cs`, `gk-fusion/src/FusionRpg.Injector/GameHooks.cs`,
    `gk-core/tests/FusionRpg.Guard.Tests/InjectorWritePathHonestyGuardTests.cs` (new).
- [x] **BCU8.3 — Delete the legacy `FUSIONRPG_KERNEL_GRIDS` switch + `_dotAccum` fallback (B27 passed 2026-09-04)** — done 2026-09-20.
  Deleted `KernelDriveHost.GridsOnKernel`/`DrivingGrids` and the `Dispatch` kill-switch early return,
  `EffectRuntime.TickDots`/`TickShields`/`_dotAccum`/`_shieldAccum`, and `InjectorLoop`'s fallback call —
  no accumulator-plus-period grid survives in `EffectRuntime.cs` (T13's success criterion 1).
  **A real defect surfaced while doing it, and it is the reason this task was not a pure deletion.**
  D15's effect-clock advance (`EffectRuntime._clock.AdvanceSeconds`) lived only inside `TickDots`, which
  B26 had already gated behind `!KernelDriveHost.DrivingGrids` — and `DrivingGrids` is true on a live
  board. So `AdvancedEffectClock` had been **frozen on every board since T4.14 landed 2026-09-17**: a
  status's `NextPulse` was never reached and its `ExpiresAt` never passed. The advance now runs in
  `KernelDriveHost.Tick`, off the same scaled delta the kernel advances by, so the pulse schedule and
  status expiry read one number again. `effect.tickDots` moved with it onto `PulseDotsNow` rather than
  being left without a producer.
  New guard: `gk-core/tests/FusionRpg.Guard.Tests/InjectorKernelGridsGuardTests.cs` (symbols gone; the clock
  advance pinned to the kernel tick, after the pause guard). Rows opened for the owning programs:
  `solid-remediation-todo.md` T4.14 (correction), `backlog-clear-todo.md` B25/B26 + Checkpoint 2,
  `battle-timeline-map.md` T13, `battle-engine-ssot.md` D15. Citations into `EffectRuntime.cs` re-anchored
  across `docs/**`/`tasks/**` (`guard-doc-citations.ps1 -Strict`: 0 HIGH). `injector-compile` guard
  SKIPPED (no `FUSIONRPG_ML_GAMEDIR` in this worktree), so the injector is not compiled locally — the
  change is text-verified by the guard tests and compile-checked by CI/the owner's game dir.
  - Files: `gk-fusion/src/FusionRpg.Injector/Effects/EffectRuntime.cs`,
    `gk-fusion/src/FusionRpg.Injector/Effects/KernelDriveHost.cs`,
    `gk-fusion/src/FusionRpg.Injector/Effects/EventDrainHost.cs`,
    `gk-fusion/src/FusionRpg.Injector/Host/InjectorLoop.cs`,
    `gk-core/tests/FusionRpg.Guard.Tests/InjectorKernelGridsGuardTests.cs` (new).
- [x] **BCU8.4 — data-test-substrate BU1 (swallowed `ALTER TABLE` in `EnsureColumn`)** · S · deps: — · Verify: verify-change + `guard-test-substrate.py` — ⛔ **BLOCKED 2026-09-20 (denied path, not unstarted work):** the fix is `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs:4260-4264` (`EnsureColumn` = `try { Exec("ALTER TABLE … ADD COLUMN …"); } catch { /* already exists */ }`), and `gk-core/src/FusionRpg.Data/**` is outside this session's allowed paths (`gk-fusion/src/FusionRpg.Injector/**`, `gk-core/src/FusionRpg.Core/**`, `tests/**`, `docs/**`, `tasks/**`). The acceptance's test half alone would land a RED suite, so nothing was written. Needs a Data-owned lane or a path grant; the row's own text already flags the `solid-run-20260912-eb53` boundary.
  - **Fence assignment (manager, 2026-09-20):** the block is a fence problem, so it is ruled here rather than left for a lane to hit. BCU8.4 is the last item of this program's queue (after the BCU2.13 S-run) and must be spawned with `gk-core/src/FusionRpg.Data/**` and `gk-core/tests/FusionRpg.Data.Tests/**` in its `--allow`; the fix and its test land as one commit, and the row's Verify line (`verify-change` + `guard-test-substrate.py`) stands unchanged. The remedy is the worker's to design; the constraint recorded here is only the fence and the one-commit rule.
  - **Resolution (lane `cmdc/bcu8-4`, 2026-09-22) — done, one commit naming BCU8.4:** `RpgStore.EnsureColumn` now reads the table's column set first (`HasColumn`, the same PRAGMA `EnsureTierAIndexesUnlocked` uses) and `ALTER`s only a genuinely missing column, and its `catch` is narrowed to `IsDuplicateColumnError` — a `SQLITE_ERROR` whose message is `duplicate column name: <column>`, the one outcome a concurrent boot can produce. Every other failure now propagates: `An_unknown_table_propagates_instead_of_being_swallowed` and `A_malformed_definition_propagates_instead_of_being_swallowed` fail (`No exception was thrown`) against the blanket `catch { }` and pass against the narrowed one (`Failed: 2, Passed: 2, Total: 4` → `Failed: 0, Passed: 5, Total: 5`, `gk-core/tests/FusionRpg.Data.Tests/Sqlite/EnsureColumnTests.cs`). Evidence: `tasks/reports/bcu8-4-evidence.md`. `guard-test-substrate.py` and `guard-dal.ps1` both exit 0; the Data suite is `4 shards, 1728 tests, no overlap`.
  - **Deviation, recorded rather than hidden:** the brief's `-Session bcu8-4` form cannot run — `scripts/verify-change.ps1:98` throws `session record not found: bcu8-4` (no `tasks/sessions/bcu8-4.json` exists, and `tasks/sessions/**` is outside this lane's fence). The same plan was run with `-AllowUnscoped`; the manager owes the lane either that record with these paths in it or an erratum.
- [x] **BCU8.5 — data-test-substrate BU2–BU4 (sharded Data.Tests, `EnsureHotSchema` gap, idle re-measure): route to `test-verification-boundary` if it covers sharding, else schedule** — done 2026-09-20.
  Checked the owning program rather than guessing: `test-verification-boundary`'s `data-tests-sharding`
  module **does** cover sharding, and TVB1.1–TVB1.5 are all complete — `gk-core/scripts/test-shards.v1.json`
  (3 class-prefix shards + remainder, `maxParallelThreads: 2`), `scripts/test-sharded.ps1` (TVB1.2's
  id-set union/intersection proof), `_meta.measured` 2-vs-4-shard readings, CI adoption at
  `.github/workflows/ci.yml:152`, and the local module-level delegation. **BU2 is therefore delivered,
  not open** — it is ticked in `data-test-substrate-todo.md` against those artifacts, and the routing
  verdict is recorded in `test-verification-boundary-todo.md` so neither program waits on the other.
  **BU3 and BU4 stay `data-test-substrate`'s** (store-timing and an idle-machine reading, no sharding
  content), explicitly scheduled there with that stated — BU4 additionally gated on an idle machine,
  which this repo's concurrent-agent load has not provided.
  - Files: `tasks/data-test-substrate-todo.md`, `tasks/test-verification-boundary-todo.md`.
- [x] **BCU8.6 — live-probe Task 21: item provenance (`origin_kind` / `acquiredVia`) on the armoury DTO** — done 2026-09-20.
  **No code change: it was already delivered and merged by the `live-qa` lane's own Task 21 fix** (recorded `[x]` in `live-probe-todo.md`), on this branch's HEAD. Verified by reading the tree, not by the other lane's note: `ArmouryRowDto.OriginKind` exists at `gk-core/src/FusionRpg.Server/ItemSurfaceEndpoints.cs:63`, is populated from the persisted `RpgItemRow.OriginKind` at `:164`, and the named regression
  (`gk-core/tests/FusionRpg.Server.Tests/ItemEquipEndpointsTests.cs:712`, `Armoury_carriesTheItemsRealOriginKind`) is present — re-run here and passing, 1/1. The only thing BCU8.6 adds is the pointer, so a later reader does not open it as unbuilt work or rebuild it.
  - Files: none changed (verification only).
- [x] **BCU8.7 — Spec the seedsmith naming-grammar pass (808/159/158/31/27/26 grammar findings) as a generator module — never a hand-edit** — done 2026-09-20.
  Wrote [`docs/architecture/item-seedgen/spec-naming-grammar-repair.md`](../docs/architecture/item-seedgen/spec-naming-grammar-repair.md)
  as item-seedgen **module 13**, and added it to that map's module table. **The module's code already shipped**
  the same day (`d401f446`, `750b0dfd`) — `naming_grammar.py` states the grammar in every authoring
  brief, `naming_grammar_repair.py` (`findings`/`plan`/`brief`/`validate_answer`/`run_batch`/`apply`)
  repairs what already shipped, driven by real `ItemSeedValidator --findings-json` output, with 13 tests
  — so the spec documents the shipped shape rather than inventing one, and the row's "as a generator
  module" half is already true (only `name` is written, atomically, dry-run first).
  **The honest finding is that the module is not reachable from a production host:**
  `rg -n "naming_grammar_repair" gk-forge/tools/seedsmith/seedsmith/report/cli.py` returns no hits, its only
  importer is its own test file, and `750b0dfd`'s own message names the **still-uncommitted driver
  script** the corpus batches actually ran through. Per the repo rule that a mechanism no host reaches
  is not done, the spec's §6 names the wire and its acceptance, and two rows now carry it in the owning
  program's todo: **WIRE 1** (a `seedsmith items` verb) owned by `seedsmith-cli-ux`, **WIRE 2** (the
  corpus run) owned by `item-seed-regen`. The `NOT-BUILT` row in
  `docs/research/backlog-clean-up/lane-B2-seedsmith-content.md` is corrected to `PARTIAL — code built,
  no production host`.
  - Files: `docs/architecture/item-seedgen/spec-naming-grammar-repair.md` (new),
    `docs/architecture/item-seedgen-map.md`, `tasks/seedsmith-generated-seed-repair-todo.md`,
    `docs/research/backlog-clean-up/lane-B2-seedsmith-content.md`.
- [x] **BCU8.8 — passive-tree H5 `tree_seed_roots` production wiring; passive-tree-repair P11 unblock (gate premise stale) + status-atom executor extension** · M · deps: BCU1.7 · re-check ActorHub/SOLID with `solid-enforcement` first — **CLOSED AS ERRATUM (orchestrator ruling 2026-09-20): the stale-premise finding IS the deliverable.** Read all four pieces against code; each is separated below with its owner, and the full analysis sits in `tasks/passive-tree-repair-todo.md`'s own "BCU8.8" section. **The erratum, as ruled:** (1) **P11.1's premise is stale** — it asks for a *new* `IActorStatSubsystem`, but `gk-core/src/FusionRpg.Core/PassiveTree/Resolve/TreeAtomSource.cs:8-13` deliberately registers none ("a PRODUCER composed into the existing fan-in, never a fourth registration"), so **the real gap is `TreeAtomSource.cs:68`'s `if (atom.KindId != "stat.derived") continue;` — a tree node's `stat.modify` atoms fan into nothing.** The corrected row is filed in `tasks/passive-tree-repair-todo.md` (P11.1r, owner: mechanism-wiring's design). (2) **P11.0 needs `docs/architecture/decisions.md`**, fenced by the active `keepverse-split` session — routed there. (3) **H5 `tree_seed_roots` is `gk-forge/tools/seedsmith/**`** (`metrics/passive_tree.py:156`), outside this lane's fence — **routed to `item-seedgen`** (`tasks/item-seedgen-todo.md`); its "non-zero `visitedFileCount`" half is separately unsatisfiable against today's corpus. (4) The status-atom executor already has the right owners (MC-2/P6.1 → mechanism-wiring) and needed no new row.
- [x] **BCU8.9 — One linked finding for the missing-reader channel families (`resource.efficiency.*`, `skill.cooldown/effectiveness.*`, `progression.xpRate/breakthroughSuccess`, `move.range`) across battle-wire W16 and class-system P9.0** — done 2026-09-20.
  Wrote the merged write-up into BOTH programs' todos, each pointing at the other so neither
  re-discovers it as its own new gap: `tasks/battle-derived-wire-todo.md`'s "Cross-program finding —
  the missing-reader families (W16, R1–R4)" section (before Checkpoint 6) and `tasks/class-system-todo.md`'s
  "External — not on this critical path" section. Both carry the same channel list, both independent
  readings (`battle-derived-wire-audit-2026-09-16.md:433,440-443` and P9.0's live
  `scripts/gate-class-system-phase9.ps1`: *6 of 48 aptitude-fed families, 18 of 486 edges*), and the
  cause read from code rather than inferred — no consumer subsystem exists, and this program cannot
  supply the action-cost layer that would read them (its plan's own Explicit non-goals). Owner named:
  class-system's P9 readiness gate; the channel inventory stays with battle-derived-wire. The
  "no-producer on the sheet" state is the honest one until a reader ships.
  - Files: `tasks/battle-derived-wire-todo.md`, `tasks/class-system-todo.md`.
- [x] **BCU8.10 — `battle.v5.json` `noteHybrid` stale comment: note it for the next battle tuning publish (never edit in place)** — done 2026-09-20.
  **No tuning file was touched** (`gk-core/data/tuning/**` is never edited in place, and it is outside this lane's paths). The note was routed to where the next publisher will read it: `tasks/combat-unification-todo.md` gained a "Carried note for the next `battle` tuning publish" section naming the exact stale clause — every `battle.v{2,3,4,5}.json`'s `_meta.noteHybrid` still says *"DEFAULT 0 = the shipped behaviour exactly"* while Wave E3's value was published as `secondaryWeightMilli: 300` on 2026-09-07 (`RulesetVersion` 4→5) — and the fix (correct that clause in the new revision's `_meta.noteHybrid` when the next `publish.py battle` runs; leave older revisions alone as the record of what was true then). Owner: whoever runs that publish.
  - Files: `tasks/combat-unification-todo.md`.

### Checkpoint CB3
- [ ] Every item in map modules 5–10 is done with evidence, is a task in a named plan, or is in the owner packet with a default.

---

## Cross-program notes (for convergence lanes; their files are not edited here)

- **Lane B (`species-progression`, `solid-enforcement` save-identity).** `SP6.6` is the one save-switch
  notice. The lawn program's `actor-liveness-refresh` will extend it with Ladder, CommanderAllocation,
  UniqueAllocation, Equip and Tree invalidation kinds, and a reserved `empireId`. Please keep the notice
  generic (one payload shape, an extensible kind) so no second channel is needed.
- **Lane D (`notification-ssot`).** `empire-development`'s three silent sources (`spec-sector-storage`,
  `spec-cargo-fate`, `spec-wonder-build-flow`) are expected to close via `world-notify-source` and
  `cache-notify-source`.

- **`action-skill-tiers` owner (`spec-holder-rung-pricing.md`).** Its status line still reads "proposed, no build authorized" though contract 4 is shipped (`BattleRunState.cs:672-679`), and `combat-ai`'s `lawn-cost-authority` depends on it. Not edited here: `action-skill-tiers` is a convergence program (lane A).
- **Rulings file owner (`spec-rulings-2026-09-18.md`, R28 row).** Add a one-line pointer: "extended to all programs by backlog-clean-up D1, 2026-09-20 (`docs/architecture/backlog-clean-up/rulings-2026-09-20.md`)". Not edited here, because active convergence lanes quote that row.

## Deferred fixes (fenced by an active session at edit time)

*(filled during wave 1: file · intended fix · fencing session)*

- ~~`docs/architecture/aura-skill/spec-aura-content.md:303` · propagate decision #5...~~ — **RESOLVED
  2026-09-20**, after merging `features/mega-merge` (lane D's work is now baseline; `git diff
  HEAD...cmdc/lane-d` no longer names this file). Fixed in the same pass as BCU1.3. This is the same
  fix `aura-close-out` AU1 (BCU3.2) would otherwise do — whoever builds wave 3 should find it already
  done and skip re-doing it.
- `gk-core/scripts/verification-boundaries.v1.json` · add an `owner` boundary entry for
  `gk-core/scripts/audit-program-pipeline.py` / `gk-core/tests/tools/test_audit_program_pipeline.py` (currently
  unmapped — a pre-existing gap, v1 of the script was never mapped either; `verify-change.ps1`
  correctly refuses with "VERIFICATION BOUNDARY MISSING" rather than silently passing) · fenced by
  `summoner-convergence` lanes A2/B/C/D/D2 (`cmdc/lane-b`, `cmdc/lane-c`, `cmdc/lane-d`,
  `worktree-agent-a7caaafc906532c18`, `worktree-agent-ae078137978cf8e26`), all of which currently
  diff this same registry file (confirmed 2026-09-20 via `git diff features/mega-merge...<branch>`
  against each). Direct `python -m pytest gk-core/tests/tools/test_audit_program_pipeline.py -q` is this
  program's evidence in the meantime (run twice for determinism each time the file grows; 3/3 as of
  BCU0.2, see BCU0.5's evidence fragment for the full-suite count once B2-B4 land).

    **CORRECTION 2026-09-27, second pass, by read-only investigation.** The 2026-09-26 correction in
    this row **holds** (558 rows, and it is a reading rather than a constant). The 2026-09-27 correction
    is **wrong twice**, and both errors are load-bearing:

    - **"the 706 rows" does not reproduce. The measured figure is 697**, and it is stable across four
      different `git status` forms. A corpus count that moves with the command that reads it is not a
      count.
    - **"the ledger is at integration" is false.** Integration's ledger is **12,667 lines**; the
      worktree's is **386,586** — and the worktree copy is uncommitted, so 58,830 unlanded lines live
      only there. This is UNLANDED EVIDENCE: nothing to merge, and calling the worktree "fully
      integrated" would delete the only copy.
    - **Three BCU2.11 full-run reports exist** (70 / 55 / 72 in porcelain) and no single one is
      authoritative. Until one is nominated, any figure quoted from "the BCU2.11 report" is ambiguous.

    **The partition key is NOT the blocker, and this row's open question is stale.** `04174d61a`
    (2026-09-26, a confirmed ancestor of the integration branch) dropped the `species/` path segment, and
    `NamespaceAllocation.cs:289` now partitions by the id template's slot. 911 -> 67 `EmptyPartition`,
    931 -> 87 gap. The residual constraint is narrower: the **generator moved** (integration carries
    +17..+62 seedsmith files, `power-classes.v1.json` added, `naming.v1.json` modified), so the only
    rule-respecting path for the unlanded corpora is **regenerate on current head**, never land the diff.

    **Per-lane disposition, measured.** `corpus-bcu210` is STALE whole — zero `gk-data/packs/fusion/data/seed` files, and its
    `BCU2.10` row is already `- [x]`; only two untracked atom-usage telemetry files need a glance before
    it closes. `corpus-bcu211b` holds 71 of 72 files unlanded and uncommitted, and its **generator is
    identical to integration's in every lane** — only the output differs, so it is a regeneration task
    and not a diff-landing one. `corpus-bcu213` holds 6 unlanded files and is **regressive**;
    `CreatureCorpusDump` is the one generator that has not moved.

    **The 699 untracked files in `corpus-bcu212` are now characterised, which they were not before:**
    349 `gk-data/packs/fusion/data/seed/passive-tree/species/*.json` + 346 `nodes/*.json` + 2 `_runs/` + `BCU2.12-run.err`
    (0 bytes) + `_j9_batch_run_results.json`. `git check-ignore --stdin` reports **0 of 699 ignored**, so
    this is generated seed output and **not** build output. 346 distinct species, provenance
    `_provenance.model = google/gemma-4-26b-a4b-qat`, `tree-language/3`. It is the largest untracked set
    in the leftover backlog and it was, until now, unexamined.

    **RETRACTION 2026-09-27 — the `.gitignore` finding above was WRONG, and no `bin/` rule is needed.**
    `.gitignore` has carried `[Bb]in/` **since the `init` commit `e4c6f1c77`**, alongside `[Oo]bj/`,
    `[Dd]ebug/`, `[Rr]elease/`, `x64/`, `x86/`, `[Ww][Ii][Nn]32/`, `bld/`, `**/node_modules/`, `**/dist/`,
    `.vs/`, `**/__pycache__/`, `**/*.egg-info/`, `**/.venv/`, `**/artifacts/`, `[Tt]est[Rr]esult*/`,
    `CodeCoverage/`, `*.log` and `*.sqlite`. Direct probe, all ignored:

        tools/ProvePredictor/bin/Debug/net8.0/ProvePredictor.dll          IGNORED
        tests/FusionRpg.Data.Tests/bin/Release/net8.0/x.dll                IGNORED
        src/FusionRpg.Server/bin/x.dll                                    IGNORED
        bin/x.dll                                                         IGNORED

    **How the wrong claim was produced, because the mechanism is the reusable part.** The manager searched
    `.gitignore` for `bin|obj`, which matched only the comment *"MSBuild Binary and Structured Log"* and
    `*.binlog` — the literal text `[Bb]in/` does not contain the substring `bin`. A second, "refined" check
    used the regex `^\[?Bb]in/`, which is malformed, and reported "confirmed absent". The claim was then
    **published into this ledger and into a commit message**, and repeated to the owner twice. It survived
    one corroboration attempt because that attempt used the same broken idea.

    **And the 6,800 files it explained away were never untracked-dirty at all.** They were
    `git status` **entries, not files**: `git status --porcelain` collapses an untracked directory to a
    single `?? dir/` line, so one orphan's 33 untracked files read as 6, and the ~6,800 compiled artifacts
    under `bin/`+`obj/` were counted from a walk that had already been defeated by a second, separate
    defect — the reclaim tool sent every path to `git check-ignore` with a **trailing carriage return**
    (`subprocess(text=True)` translates newlines in both directions on Windows), so the ignore query matched
    **nothing** and the working `[Bb]in/` rule never got a chance. Both defects are fixed; the tool now
    sends bytes and the pre-removal check expands untracked directories and asks whether integration has
    the path at all.

    The audit of those 10,976 files was not wasted — it is what established that every `.cs` under `obj/`
    is MSBuild-generated (140 carry `// <auto-generated`, 70 open `// <autogenerated />`) — but its
    *stated reason* was false, and a false reason in a program ledger is worse than no reason. The correct
    statement is: **build output was never a git-hygiene problem in this repo.** What remains true and
    useful is the other half of the paragraph above it: `corpus-bcu212`'s 706 untracked files are generated
    seed, `check-ignore` reports 0 of them ignored, and they are the deliverable — not litter, and never
    something to ignore away.

    ---

### CB5 — the four `corpus-*` lanes: closed, and the one merge question answered against the premise

*(appended 2026-09-27 by the mega-merge cleanup walk; continues the row above rather than opening a
new one, because that row already reaches the correct conclusion — "the generator moved, so regenerate
on current head, never land the diff" — and what was missing was the per-lane proof for `bcu211`.)*

The owner ruled: *"merge the 4 corpus lanes if it won't break anything, regenerate later."* **The
conditional fails, and the "regenerate later" has already happened.** All four `corpus-*` worktrees and
their branches are cleared; the one branch with anything to merge is retained under
`rescue/corpus-bcu211-itemseedgen-run` rather than merged, because a finding that contradicts a ruling
is the owner's to overturn, not a manager's to execute by deleting the evidence.

**Three of the four had nothing to merge.** `corpus-bcu211b`, `bcu212` and `bcu213` are already
ancestors with **0 unmerged commits**. Their only content was uncommitted working-tree residue — 84, 719
and 18 unlanded files — and **every one is under `gk-data/packs/fusion/data/seed/**`**: generated data from interrupted runs,
governed by the categorical rule above. `corpus-bcu212`'s 719 are the BCU2.12 residue the row above
already characterised. None needed the reclaim tool; all three cleared on `git worktree remove`.

**`corpus/bcu211` is the one with a commit, and it must not be merged.** It is **not a fast-forward** —
divergent one commit each way from merge-base `784555a1b` — and a merge would touch **6,973 files with
173,231 insertions and 449,213 deletions**:

    gk-data/packs/fusion/data/seed/items/materials/materials.json    integration 426 lines   corpus/bcu211 59,130 lines

Those 449k deletions are not corpus changes. They are every document, skill, test and web file that
landed on integration after the branch point. The single commit `6fc3d2b21` is itself narrow — 55
`gk-data/packs/fusion/data/seed/items/**` paths plus `tasks/reports/BCU2.11-full-run.json` — which is why the surgical
alternative is a cherry-pick, and the cherry-pick is what the rule forbids.

**The per-lane proof the row above was missing.** All four generator/corpus commits since the divergence
are in integration and **not** in `bcu211`: `f671cc5ad` (*"author the per-base-type armour successor
edges and regenerate the corpus"*), `808b727d8` (*"corpus re-emit, pricing floors, materials
constant"*), `3ff951918` (*"item emitters stamp the resolved model"*), `d38577d8d`. And the regeneration
**covered bcu211's own paths**: `f671cc5ad` touched 35 base-types files, **29 of which overlap**
bcu211's 55 data paths. The content settles it — integration's `base-types/footing/plant/a.json` carries
**20** occurrences of `successor` where bcu211's carries **0**. So integration holds a **later**
regeneration of exactly these files, containing rows bcu211 never produced. Its
`tasks/reports/BCU2.11-full-run.json` is likewise a **census** whose integration copy is the newer one
(same 14 keys; only `head`, `gitStatusPorcelainCount` 70-vs-55 and `diffStatTail` differ) — a dated
population reading, never owed work.

**Answer to the ruling, stated plainly: do not merge the corpus lanes.** If `gaps 931 -> 770` is still
wanted, the sanctioned route is to re-run the generator on current head and commit the fresh diff — not
to recover the 2026-09-23 snapshot. `rescue/corpus-bcu211-itemseedgen-run` is **kept**, not deleted: a
ref costs 41 bytes, and deleting it would foreclose the owner inspecting the 56 files before accepting
that merging is unsafe. One classified ref is a legitimate terminal state; a deleted ref is not
reversible.

### CB6 — the drift loop was in the tool's own output, and it is now closed

The owner's follow-up to "superseded them" was *"then what next? drift forever?"* — the right question of
a verdict that is only a label. The answer is that the drift was real and **named in the tool's own
output**: `retire_worktrees.py` reported 37 leftovers, told a manager to adjudicate **33**, and said
*"This tool does not remove these … Adjudicate first, then delete by hand."* The survey could name a
leftover but not decide one, so every run regenerated a human queue.

**The queue was wrong twice, and both errors flattered the tool.** Running the reclaim tool's own proof
over the same 37 said **14** were machine-decidable (4 empty, 10 provably stale) and **23** real. And
**30 of the 37 are not repository content at all** — they sit under
`C:\Users\<user>\AppData\Local\Temp\opencode`, and they enter the count only because two owner-ruled
ps1-ban lanes are themselves registered there, so the scan (which derives candidate parents from
registered worktrees) drags every sibling scratch directory in with it. The repository's own leftover
debt is **one** directory, and `--prove-stale` proves it stale.

**Fixed** in `gk-core/scripts/retire_worktrees.py` (`--prove-stale`, 62 tests green, `588909b4b`) and recorded as
a binding rule in `.agents/skills/project-manager/SKILL.md`, including a new blind spot: *a leftover scan
that derives its directories from registered worktrees inherits their location.* Re-derive the split with
`python gk-core/scripts/retire_worktrees.py --prove-stale --json`; **never quote a remembered figure.**

### CB7 — six measurement defects this program produced, recorded because they are re-buyable

Every one of these produced a confident, wrong, actionable claim, and **not one was caught by reading the
output harder** — each was caught by a second, independent measurement disagreeing with the first. The
durable form is the shape, not the incident:

1. **A derived field that is structurally constant.** The line-set test's `only_head` compared
   integration's count against the worktree's with the operator reversed, so it measured worktree
   *surplus* — which is `only_mine` — and was pinned at **0** for every file. Every verdict therefore read
   "integration has nothing the worktree lacks", the signature of a tool quietly agreeing with you.
2. **A mask that cannot match its own target.** `\.[A-Za-z]{1,5}\b` does not match `.ps1` — `1` is not a
   letter and no word boundary falls between `s` and `1`. The mask existed to see the ps1-ban port and was
   blind to precisely that rename. It then took two more passes to learn the port also changed the
   **invocation** (`.\scripts\x.ps1` -> `python scripts/x.py`) and the **separator**, and that stripping
   `./` *before* converting `\` to `/` leaves a leading `./` the ported twin never had.
3. **A flag that silently does nothing for the answer.** `git diff -m A B` returns 0 paths — `-m` is a
   `diff-tree`/`log` flag and `git diff` compares two trees without it. The mirror of the standing
   "diff-tree reports zero files without `-m`" warning is passing `-m` to a command that never wanted it.
4. **A parser that skips what it does not understand.** `git diff --raw` splits into **two** tab fields
   (the status is the last *space*-separated token of the first), so a three-field test skipped all 2,274
   lines and reported "nothing differs" — twice, each time about to delete a ref holding the last copy of
   an unmerged merge.
5. **A denominator that mixes two populations.** The BCU2.12 census first reported the collision gate
   failing **23.3%** of the run. The ledger holds 10,164 rows carrying a committed `record` and 5,433
   carrying `record: null`; dividing by all 15,597 counts committed nodes in the denominator. The real
   figure is **34.8%** failed, of which **66.9%** (3,633/5,433) are the one gate — and all 3,633 carry
   `outcome=escalated`, making the gate 99.2% of the entire escalation population.
6. **A repeated flag that keeps only the last.** `--adjudicated` is comma-separated, and a driver passing
   it once per file had every name but the last silently dropped. Nothing was deletable by the mistake (a
   dropped name makes the tool refuse, never remove) but the trap sends a manager to adjudicate a phantom.

**The rule all six share, and the one to carry:** *silence where a difference belongs reads as
permission.* A measurement that cannot fail is not a measurement — and a count that looks tidy is the
tell that a non-homogeneous population was measured as if it were one.

### CB8 — open, fenced, and why it matters that they are open

Two findings are **routed and committed but not landed**, because the owning ledger is inside an active
session's fence. Recorded here rather than dropped:

- **`post_merge_check.py:123` — `POSITIVE_COUNT_RE = r"\b(?:Total|Passed):\s*(\d+)"`.** `Total` counts
  **skipped** tests, so `Passed! - Failed: 0, Passed: 0, Skipped: 1, Total: 1` satisfies the
  positive-count check, produces no red, and the merged-head gate returns **GREEN for a run in which
  nothing executed**. This is the standing "a green exit is not evidence that tests ran" trap, sitting in
  the harness that decides whether a lane is accepted. The fix survived the `.ps1` -> `.py` port
  faithfully, which is what a port does. The fail-closed form and the test that pins it
  (`test_skipped_only_test_count_is_red`) were **uncommitted** in
  `opencode-resume-00a-fail-closed-recovery-20260925` and would have died with it; rescued as
  `tasks/evidence-fragments/resume-00a-fail-closed-recovery-20260925/post-merge-check-positive-test-count.patch`
  (verified to apply **and** reverse in a scratch worktree). Owning ledger: `tasks/ps1-ban-todo.md`, fenced
  by `ps1-ban-manager-20260926`.
- **The BCU2.12 corpus-wide node-name collision gate.** Of 15,597 attempted node subjects the run
  committed 10,164 and failed 5,433, and **3,633 of those failures (66.9%) are one defect** — a
  corpus-wide uniqueness gate whose only recovery is another model call, so the budget exhausts
  (`Primal Ferocity` alone was rejected **74** times). The items pipeline already solves the identical
  problem deterministically via `NameRepair`; the node path has no equivalent. Both code sites are still
  present, so this is **open work, not a closed incident**. A second, smaller defect rides along: the
  validator's message hardcodes *"another commander effect"* while its `nodegen` call site checks
  **passive-tree node** names, which is why the 12.5 MB ledger read as 984 distinct shapes until the
  quoted name was masked out. Landed as
  `tasks/evidence-fragments/seedsmith-p1-audit-final-20260925/BCU2.12-failure-census.json`. Owning
  ledger: `tasks/passive-tree-todo.md`, fenced by `ps1-ban-manager-20260926`.

**A fence that blocks finding delivery is itself a finding.** `ps1-ban-manager-20260926` claims **538**
paths — a `.ps1` -> `.py` port has no business holding two program ledgers, and the practical effect is
that neither of the two findings above can be routed to the ledger that owns it. That is corroborated
(an `active` record), so it blocks correctly; it is surfaced here so the owner can narrow the fence.

### CB9 — a cleanup tool's coverage shrinks as the cleanup succeeds

Continuing CB6, because it is the same failure wearing a different coat: a measurement that reports a
**clean tree** because its scope silently narrowed. `retire_worktrees.py` derives its pool set from the
parents of the **registered** worktrees — correctly, because deriving it any other way once swept in 28
unrelated sibling repositories — and that makes coverage shrink as the cleanup succeeds. Measured
2026-09-27: after the last worktree left `.claude/worktrees`, the four husks it still held became
invisible to the tool meant to find them (**31** reported without the pool, **35** with it declared).
Fixed by `--pool DIR`, with `POOL-NOT-A-DIRECTORY` and `POOL-IS-THE-ROOT` as named refusals, 67 tests
green, one of which asserts the blind spot itself. Binding rule added to the project-manager SKILL as a
sixth blind spot: **pass the repository's own pools on every run; never rely on the derived set to still
contain them.** The four husks are `HELD` by a live process handle — reported, never forced, and now
visible, which is what the fix bought. Detail: `tasks/reports/mega-merge-manager-resume-20260925.md`,
Addendum AF.

### CB10 — retracting "none of them is repository work", and the six leftovers that are not ours to delete

Continuing CB9. Addendum AF closed by asserting that all 23 `NEEDS-ADJUDICATION` leftovers were "other
tools' scratch under Temp, **none repository work**". **That is false**, and false in the way the
standing rules name: it rested on *where* the directories sit, never on what is in them. Re-examined by
content, **16 of 23 hold repository-shaped material**. The conclusion happened to survive; the reason did
not, and a conclusion that is right for the wrong reason is the failure this cleanup exists to catch.

**10 disposable** — build output and game binaries (`actor-hud-unity-live-server-20260926`: 2,568
repo-shaped paths of `FusionRpg.*.dll`/`.pdb`; `epl11-obj`: NuGet intermediates, where "unlanded" is the
*desired* state because binaries are never committed); test fixtures at production paths
(`openid-fixture`: nine 1–7-line C# stubs under `gk-core/src/FusionRpg.Core/**`, **all absent at integration**,
so landing them would ADD junk to production source rather than replace it; `statpairs-fixture`: a
19-line `gk-data/packs/fusion/data/seed/derived-stats/catalog.json` against integration's 773, generated data at a tracked
path, never hand-landed); and tool/session scratch including this session's own.

**1 acceptance artefact, proven a duplicate.** `resume-20-rsf27-acceptance-20260925/evidence.json` names
`reviewedSha 4f78ed6c9` and `baseSha 6d77888cc`, **both ancestors of integration**, so it does not block;
and it is not the only copy —
`.claude/cmdc-agents/acceptance/resume-20-rpg-sim-defeat-floor-review-20260925-4f78ed6c.json` is
tracked at integration with the same SHAs and the same `command`. The most protected category in this
repo, checked rather than assumed.

**6 are the OWNER's, and no content proof can decide them.** Four hold **`rpg-hot.sqlite.<timestamp>.bak`**
— copies of the running game database: not evidence owed here, not regenerable by any generator, and
destroyed by deleting the only copy. Two are `actor-hud`'s live-probe artefacts (lawn PNGs, browser
proofs) and that lane is owner-ruled out of scope, so their being unlanded is the *purpose* of a probe.
A `NEEDS-ADJUDICATION` verdict on a save backup is technically correct and practically wrong, which is
the sharpest argument here for why "unlanded" and "disposable" are different questions. Nothing in
either group is deleted or landed; all six are outside the repository's own worktree pools.

**Rule, and the retraction as the rule:** *location is not ownership and a filename is not a verdict.*
The corrected claim is: **none of the 23 is owed work for this repository, and six of them are not this
cleanup's to touch** — both halves content-derived. Detail: `tasks/reports/mega-merge-manager-resume-20260925.md`,
Addendum AG.

### CB11 — this session's own fence was 69% fiction, and it was manufacturing 34 of the repo's 52 crossings

Continuing CB10. `session-boundary-check.py` reports `DRIFT (52)`, and ~34 of those collisions were
**this session against `ps1-ban-manager-20260926`**. The cause was my own record: of **80** fenced
paths, **55 had never been touched by this session**, and five of the rest were globs (`.claude/**`,
`.agents/skills/**`, `docs/contributing/**`, `docs/architecture/solid-enforcement/**`,
`gk-fusion/tools/debug-mcp/**`) that swallow every file beneath them — `README.md`, `Directory.Build.props`,
`gk-core/src/FusionRpg.Server/Program.cs`, and 40 other files a worktree-cleanup manager has no business holding.

**This is a live hazard, not noise.** `git commit` publishes the whole index, and another lane's **68
staged paths sat in the index for this entire session**. A fence claiming `README.md` and
`Directory.Build.props` would have *sanctioned* publishing that lane's staged copies of them. Narrowed
**80 → 11**, and `DRIFT (52) → 18`, of which this session now accounts for **1**.

**The four ways of deriving a fence from history all failed, each producing a wrong claim rather than a
failure.** (1) recency on the shared integration branch attributes every lane's commits to this
session — 430 "owned" paths, **399** of them other lanes' (`blender/**`, their ledgers); (2) "a commit
touched a fenced path" is coincidence, not ownership — `gk-core/scripts/verify-change.py` is genuinely mine,
`scripts/session-boundary-check.py` is not, and recency cannot separate them; (3) a hand-listed SHA set
**undercounted**, missing the two rescued-evidence files; (4) **every SHA named in a document is not an
authorship claim** — the walk report is a *catalogue* of the commits it describes, so 80 of its 85
tokens resolved to commits belonging to other lanes. A fence is a forward permission set; history can
only understate it, and a history-derived fence silently drops the claim on the very evidence a future
rescue must gate. The replacement: state it from the program's surface, then take the commits that
touch **only** fenced paths (58 of 361) and read each — a check that can over-collect, never silently
under-collect. A pre-write assertion against the report's SHAs **failed closed and named all 347 gaps**
rather than printing a pass, which is what gave the trap away.

**A mutual claim is not a block, and this session holds the older one.** `gk-core/scripts/verification-boundaries.v1.json`
is claimed by both. Read from the record's own 30-version history: **this session's claim first appears
2026-09-26 16:18; ps1-ban's at 19:08, at path-count 118 — after a step from 39.** So the 538-path
widening swept a file this session had already committed to four times (`cca2200c6`, `f5ed749de`,
`7494c0f13`, `27445d9a9`). **I did not cross**, and dropping my claim would have been the wrong repair.
The checker reports DRIFT without order, so it cannot make that distinction; the rule is now binding in
`.agents/skills/project-manager/SKILL.md`.

**Second instance of CB8, with the mechanism.** ps1-ban's fence is a growth curve, not a fence: 5 → 25
→ 27 → 32 → 35 → 39 → 118 → 211 → 251 → … → 533 committed, **538 in an uncommitted working-tree edit**.
A whole-tree `.ps1`→`.py` port needs every file it ports, so its blast radius *is* the tree; the step
that mattered was 39 → 118, and it is what put two program ledgers (CB8) and a live registry file out of
reach. **Owner decision: cap it, or require per-file claims renewed as the port advances.**

### CB12 — retracting "materialistic-spear holds 4 unintegrated commits": it holds none, and they were main's

Continuing CB11. The final audit re-derived the branch and worktree tables and printed `main` as
having unintegrated commits. Checking `main` against its merge-base settled its own verdict precisely —
tree `7cb9a330c` identical to its merge-base tree, 4 commits not in integration and **0 non-merge**, so
four no-op merges contributing zero content — and it exposed a double-count in this walk's own
classification.

`.kilo/worktrees/materialistic-spear` is **detached at `52fec0bee`, which is `main`'s tip.** It has no
branch of its own (`git branch --list materialistic-spear` is empty), it is clean (0 status entries),
and `git rev-list features/mega-merge..HEAD --not main` returns **0** commits. So the "4 unintegrated
commits" this walk attributed to it are `main`'s four no-op merges — **the same four objects, counted
twice**, once as a branch and once as a worktree.

That is the trap the procedure names: *group every census by content, never by (file, worktree); one
change present in twenty worktrees is one piece of work, and a count that inflates it produces twenty
phantom items.* Here it produced one. Corrected verdicts:

| item | was | is |
|---|---|---|
| `.kilo/worktrees/materialistic-spear` | group-C live work, 4 unintegrated commits | **EMPTY** — a clean detached checkout of `main`'s tip, no branch, 0 status entries |
| `main` | 4 unintegrated commits | **one merge record**, tree identical to its merge-base, zero content contribution |

**The owner ruling is untouched.** `materialistic-spear` stays owner-ruled and untouched either way;
this only corrects what it *holds*. It is worth correcting precisely because a belief that group C still
has four commits in flight is a reason to keep a worktree, and there is nothing there to keep. The
lesson joins CB10's: **a worktree's name is not a verdict, and neither is a count it inherits from a
branch it merely points at.**

### CB13 — claim order settles blame, not permission: dropping my own older claim on the shared registry

Continuing CB12. CB11 kept `gk-core/scripts/verification-boundaries.v1.json` on the strength of claim order —
this session's claim predates ps1-ban's by 2h50m, so the widening created the drift and dropping the
older claim would have been the wrong repair. **That reasoning was half right, and the half that was
wrong is the half that would have caused damage.**

`git log -1` on that file is `5548b3a7d`, dated today: *"Ports guard-class-system to Python."* — ps1-ban's
own commit, and they have committed to the file repeatedly since. So the junior claimant is the
**active editor in practice**, and this session's senior claim explains the drift without making the
claim current. The staged copy of that file has been sitting in the index, theirs, throughout.

Claim order is a **diagnostic**, not a permission. It answers *who created this drift*, and the repair
follows: surface the junior side, do not silently drop the older one. It does not answer *who may write
next*, and reading it that way would have had this session keep editing a file another lane has been
committing to all day. **The claim is now dropped — the fence goes 11 → 10 — and if this program ever
needs the mapping again it re-claims in a new commit with a stated reason.** A blanket mapping is
recoverable; two sessions writing one file is not.

The rule is now stated in both halves in `.agents/skills/project-manager/SKILL.md`, with the measured
case that forced the second half.

### CB8 — CORRECTION (2026-09-27): the first finding is CLOSED, and the rescue it names went stale

Two claims in CB8 are no longer true, and a stale claim in a ledger is worse than a missing one.

**1. "Verified to apply and reverse" is no longer true.** The rescued
`post-merge-check-positive-test-count.patch` was verified on 2026-09-25. Today:

    git apply --check  ->  post-merge-check.ps1: No such file or directory
                          accept-lane.ps1:      No such file or directory

Both `.ps1` targets were **retired** by `caa9fb275` — *"Repoints test_fail_closed_pipeline.py at the
Python twins, which retires accept-lane.ps1 and post-merge-check.ps1."* The two `.py` hunks still apply
with offsets; the two `.ps1` hunks have no target, and `test_skipped_only_test_count_is_red` is
**absent** from today's `test_fail_closed_pipeline.py`, so the test the rescue carried never landed.
The rescue is annotated in place (`.../resume-00a-fail-closed-recovery-20260925/README.md`) so nobody
re-applies it: a patch that applies but should not is a trap.

**2. The first finding is no longer blocked — it is FIXED.** The block was always on the *ledger*, never
on the *code*: `ps1-ban-manager` is retiring the `.ps1` twin and claims `post-merge-check.ps1`, not
`.claude/cmdc-agents/scripts/post_merge_check.py`, and not its test. Those two paths were free, so they
were claimed with the reason recorded, and the fix landed:

    POSITIVE_COUNT_RE   was  r"\b(?:Total|Passed):\s*(\d+)"    ->  now  r"\bPassed:\s*(\d+)"
    + SummaryTests.test_a_skipped_run_is_not_a_positive_test_count

Measured against the module's own predicates before the change, because a published finding is a claim
and must be tested: the all-skipped line `Skipped! - Failed: 0, Passed: 0, Skipped: 38, Total: 38`
yielded `findall == ['0', '38']` and **GREEN**; `No test matches the given testcase filter` and a
genuine `Failed!` both correctly returned **RED**. So the hole was the `Total` alternative alone, not a
permissive gate, and the fix is the narrow one. The regression test is **load-bearing** — the pre-fix
pattern restored in memory returns `True` where the assertion requires `False` — and the full module
suite passes (77 passed, 2 skipped, 33 subtests), as does the repo's own boundary
(`verify-change.py` -> `manager-fail-closed (focused)`, 63 passed, exit 0).

**Why a fenced ledger did not stop this.** The rule is that a finding lands in the owning program's
ledger. It does not follow that a finding whose ledger is fenced can only ever become a row: the code
the finding names is a separate question, and it was unclaimed. **A committed fix with a
load-bearing regression test is strictly better than a ledger row** — the row records an intention,
the fix makes the defect un-recurrable. The owner still owns the decision to record it in
`tasks/ps1-ban-todo.md` when the fence narrows; what no longer waits on that fence is the defect.

**The second finding is unchanged and still blocked:** the BCU2.12 corpus-wide node-name collision gate
owns `tasks/passive-tree-todo.md`, which is inside the 538-path fence, and no code path for it is free.

### CB14 — CB8's second finding: the narrow half is FIXED, and a pre-existing vocabulary drift surfaced

Continuing CB8's correction. The same question as finding 1 — is the block on the LEDGER or on the
CODE? — and again the answer was the ledger. `gk-forge/tools/seedsmith/` is claimed by **no active session**, so
the narrow half of the BCU2.12 finding was actionable while `tasks/passive-tree-todo.md` stayed fenced.

**Fixed: the validator mislabelled what it was refusing.** `workflow/validators/field_echo.py`
hardcoded `commander effect` in `name_collision`'s message and `the creature's` in `subject_name_echo`'s
— and **`subject_name_echo`'s only caller is the passive-tree node path** (`adapters/trees/nodegen/run.py`),
so every node refusal announced itself as a commander effect named after a creature. This was not
cosmetic: the noun is part of the failure-ledger text, which is part of why the 12.5 MB BCU2.12 ledger
read as 984 distinct shapes. `adapters/dungeon/pipelines.py` already names the kind correctly at four
sites ("another event", "another encounter", "another room", "another domain"), so the shared primitive
was the one place out of step with the convention. The kind now travels in `context` as `subjectKind`
with a neutral `DEFAULT_SUBJECT_KIND` fallback — in `context` and not a new parameter precisely because
`name_collision`'s own docstring claims it stays a pure function of `(draft, context)`, and that claim
is now asserted by a test rather than left as prose. The node call site passes
`subjectKind: "passive-tree node"`.

**Still open, and it is the larger half:** the corpus-wide collision gate. 3,633 of 5,433 BCU2.12
failures (66.9%) are one defect, and the node path still has no deterministic repair — `NameRepair`
exists only under `adapters/items/setgen/name_repair.py` with **0 sites on the node path**, verified
today. That is a design decision for the passive-tree program, and its ledger is fenced, so it stays a
finding rather than becoming my code.

**A pre-existing failure, found and proven, not assumed.** `verify-change.py` selected
`test_tree_plan_emit.py` and it failed twice:

    $.propertyVocabulary.atomAttachPoint: length differs (7 vs 9)
    $.propertyVocabulary.atomKind:        length differs (16 vs 18)

Two independent proofs were used because the repo's rule is *confirm a failure already exists before
blaming your change*, and "looks unrelated" is not a measurement:

1. **Import graph.** All four failing test files were resolved transitively; none can reach
   `field_echo`, `validators/__init__`, or `nodegen/run` — 4/4 proven independent.
2. **Revert and restore.** The three changed source files were backed up with sha256, reverted with
   `git checkout --` (never `git stash` — it would sweep a concurrent stream's 68 staged paths), the two
   tests re-run, and the files restored **byte-identical**. The failures reproduce on HEAD code.

So they are pre-existing, and their cause is a tree-plan vocabulary disagreeing with a spec table — a
**generator/regenerate** matter under the hard rule, never a hand edit. **New finding, owner
`tasks/passive-tree-todo.md`, currently fenced:** `atomAttachPoint` 7 → 9 and `atomKind` 16 → 18. The
two test files that actually cover this change pass 61/61.

### CB15 — "git commit publishes the whole index" protects the COMMITTER, not the AUTHOR

Continuing CB14. A concurrent lane's commit carried **4 of this session's 16 fenced paths** under its
own message, and the mechanism is the mirror image of the rule the manager SKILL already carries.

**Measured.** The seedsmith fix committed as `5f8b571be`, message **"update documents"**, a commit
touching **215 paths**. Four of them were this session's:

    gk-forge/tools/seedsmith/seedsmith/adapters/trees/nodegen/run.py
    gk-forge/tools/seedsmith/seedsmith/workflow/validators/__init__.py
    gk-forge/tools/seedsmith/seedsmith/workflow/validators/field_echo.py
    gk-forge/tools/seedsmith/tests/test_quality_gates.py

The content came through **exactly** — `_subject_kind`, `DEFAULT_SUBJECT_KIND`, the node call site's
`subjectKind: "passive-tree node"`, and all 4 new tests are in that commit, and 25/25 pass on HEAD as
committed. So nothing was lost or mangled. But a validator refactor with a new package export and five
regression tests now sits in history under a message about **documents**, and this session's own commit
`094805133`, whose message reads *"Fix CB8 finding 2 narrow half"*, carries **only the ledger and the
session record** — a message that overstates what it contains. That is the same class the repo already
recorded once (`191afdc68`: *"a commit message that overstated what it carried"*), so this is the
**second** occurrence, now with a measured mechanism.

**The gap in the existing rule.** "Check the staged set against your own paths before every commit"
protects the **committer** from publishing someone else's work. It says nothing about the reverse: your
work can be published by *someone else*, because a lane that stages broadly and commits will carry
whatever is in the index. This session's fence did its job — 4 of 16 paths went, and the other 12 were
untouched — but the fence cannot prevent it, and no fence can.

**Two rules, now binding in the manager SKILL:**

1. **A staged count taken before the commit is not evidence about the commit.** This session printed
   `other lane's staged BEFORE: 0`, then `git add`, then saw only **2 of 6** staged — because the other
   lane's commit landed between its check and mine. Re-read the **committed** file list *after* the
   commit and compare it to what you intended to ship. The pre-commit count measures the index, not your
   authorship.
2. **If your staged paths are already in HEAD under someone else's message, say so in a NEW commit.**
   Never amend. The correction is a ledger row naming both SHAs — this one — because the history now
   genuinely says something the code's authorship does not, and only a recorded correction repairs that.

Nothing here is a reason to distrust the fix: the content is verified in HEAD, byte-for-byte what was
written, and green. It is a reason to distrust the **message**, and to measure the commit rather than
trust the queue that fed it.

### CB16 — the vocabulary drift was BOTH defects at once, and a fence cannot name a directory

Continuing CB14, which recorded the tree-plan vocabulary failure as a pre-existing finding. It is now
diagnosed and closed on the code side, and it was **two** defects, not one.

**The three numbers, and which is the contract.** `atomAttachPoint` / `atomKind` had three values:

    vocabulary.json (authored SSOT)   attachPoints 9   kinds 18      <- the contract
    live mirror                       9                 18
    committed plan                    7                 16            <- stale GENERATED data
    test pin                          7                 16            <- stale LITERAL over a population

The tell was the asymmetry: `atomTrigger` (13) and `channelFamily` (54) already **agreed**, so the plan
had been regenerated after the channelFamily change and before these two — it was stale by exactly those
axes. The two additions are coherent, not corruption: **`Element`** and **`Siege`** attach points, with
**`element.convert`** and **`structure.place`** using them.

**Defect 1 — the stale plan, fixed the sanctioned way.** Generated data is never hand-edited, so this
was `seedsmith trees plan --emit`, never a JSON edit. The first emit wrote only `might.v1.json` (the CLI
defaults to one tree), which would have left **41 plans and the manifest at 7/16** — and that is not
cosmetic: `plan_read.py` refuses a plan carrying no `propertyVocabulary` and `exclusion.py` refuses a
`propertyKeys` entry absent from it, so a stale plan would **refuse a legitimate node** whose key is
`Element` or `Siege`. All 43 emitted. Safety was measured, not assumed: every `nodeKey`, `nodeId` and
node count was snapshotted before and after — **0 moved**, so the 62 node files and 41 identity files
keyed by this plan stay valid. The diff is 320 lines: the two new attach points, the two new kinds, and
two bumped counts, per file. `--check` is now `byte-identical to a fresh regeneration`, and
`guard: generated-seed`, the guard whose remit actually covers generated seed data, is **clean over all
45 changed files**.

**Defect 2 — the pin, replaced by the relationship the file's own comment already prescribes.**
`atomAttachPoint` and `atomKind` are not a closed vocabulary; they mirror a corpus that grows whenever
content ships, which is the class `AGENTS.md` forbids a guardrail from validating. The literal is now
`len(authored["attachPoints"])` / `len(authored["kinds"])` read from `vocabulary.json` — the same fix
`channelFamily` got, in the same file, for the same reason. **`atomTrigger` (13) and
`atomTriggerAuthorable` (11) are the same class and are still literals.** They do not fail today, and a
selected failure is diagnosed at its own boundary rather than authorising a broad sweep — so they are
named in place with the fix stated, not quietly changed.

**A fence cannot name a directory — measured, and it is a real defect.**
`verification_boundaries.wildcard_match` (`gk-core/scripts/lib/verification_boundaries.py:181`):

    gk-data/packs/fusion/data/seed/passive-tree/plan/          -> False
    gk-data/packs/fusion/data/seed/passive-tree/plan           -> False
    gk-data/packs/fusion/data/seed/passive-tree/plan/*.v1.json -> True
    gk-data/packs/fusion/data/seed/passive-tree/plan/**        -> True

So the natural way to say "this directory" matches **nothing**, and the only working spellings are
globs — the widest being `**`, precisely the over-claim CB11 retracted. It fails **closed** (it
refuses), so it is not a safety hole, but it pushes every author toward the broadest pattern available,
and a broad fence sanctions crossing instead of catching it. The file is claimed by no active session,
so it is a real candidate — but it is load-bearing for `verify-change.py`, `session-boundary-check.py`
and the guard suite simultaneously, and ps1-ban is actively porting the verification plane, so a
worktree-cleanup session does not widen a shared matcher's semantics on its own. **Worked around with
the narrow `*.v1.json` glob, reported rather than taken.**

**Two pre-existing failures, proven rather than assumed.** `test: guard` reported `Failed: 6,
Passed: 710`. Two proofs, because this session has already produced two wrong claims from "structurally
unrelated": the failing file is `ClassSystemBaselineRegenTests.cs`, a class-system baseline regen
reading `_baseline-residual.json` via CombatSim predict against live `aptitudes.v10.json`, and **no guard
source reads the passive-tree plan** (the hits are comments and the unrelated code enum
`AtomKindRegistry`). Then measured: the 42 plan files were reverted to HEAD, **only** that guard class
re-run (2 failed / 1 passed), and the corpus re-emitted and proved **byte-identical** with `--check`
exit 0. The failure reproduces without this change. Worth noting the same run reported
`Passed: 710` — a non-zero executed count, which is the `POSITIVE_COUNT_RE` fix working rather than
false-greening.

### CB17 — RETRACTING CB16's matcher claim: it is the documented contract, not a defect

CB16 reported that `verification_boundaries.wildcard_match` cannot express a directory, called the
natural fence spelling unusable, wrote that the file "is a real candidate" for fixing, and framed the
narrow-glob workaround as a defect to be removed later. **All of that is false, and retracting it here
with the mechanism that produced it.**

Measured, side by side. The matcher is a deliberate port, and its own docstring says so: *"This is the
shape `verify-change.ps1` uses for a session fence (`Matches-SessionPath`) … both passed a raw
PowerShell `WildcardPattern` after replacing `\` with `/` on the pattern AND on the path."*

    pattern                            PowerShell WildcardPattern    the Python twin
    gk-data/packs/fusion/data/seed/passive-tree/plan/               False                     False
    gk-data/packs/fusion/data/seed/passive-tree/plan                False                     False
    gk-data/packs/fusion/data/seed/passive-tree/plan/*.v1.json      True                      True
    gk-data/packs/fusion/data/seed/passive-tree/plan/**             True                      True

**Identical on all four.** Under `WildcardPattern` only `*` and `?` are wildcards and `/` is an ordinary
character, so a trailing slash is a literal that matches no file — the twin reproduces its source
exactly, which is the whole point of a port.

And the behaviour is a **stated decision**, not an accident.
`docs/architecture/verification-boundaries-map.md` §3 decision 8: *"it validates every supplied path
against the active record, but **never silently expands broad session globs** or inspects another
contributor's diff."* A fence entry that silently claimed everything beneath a directory would be
precisely the "silent expansion" that decision forbids. **The matcher refusing to do it is the feature.**

**The mechanism that produced the false finding**, because it is re-buyable. I applied a **gitignore
intuition** — "a pattern naming a directory covers its contents" — to a matcher built on a different,
documented contract, and I did it in the wrong order: I measured the four answers *correctly* and only
then asked whether the behaviour was a defect, instead of first asking **what the thing was built to do**.
A behaviour measured without reading the stated contract is not a finding. Worse, having concluded
"defect", I then reasoned about the fix purely as **blast radius** ("load-bearing for three callers, and
ps1-ban is porting the verification plane, so not on its own") and never once about **whether the change
should exist**. That is how a false finding nearly became a code change that quietly converted a
documented safety property — never silently expand broad session globs — into an implicit one.

**What survives.** The measurement was right and the workaround is still correct: this session's fence
entry is `gk-data/packs/fusion/data/seed/passive-tree/plan/*.v1.json`, which is the precise spelling of "the 42 per-tree plan
files" under the real semantics. Only its *recorded reason* was wrong — it cited CB16 as the reason — and
that reason has been corrected in the session record. The rule is now binding in the manager SKILL.

### CB18 — the parked `NameRepair` finding, made briefable: 2 near-collisions no regeneration can fix

CB8's second finding said the node path has no `NameRepair`. Rather than leave it parked, I measured what
the gap actually costs. **The measurement changed the finding twice, and both of my own scope choices
were wrong before the number was right.**

**The authority cannot be asked at all.** `NameRepair`'s docstring names the collision rule's authority:
`naming.v1.json`'s normalization, implemented in `gk-forge/tools/ItemSeedValidator/Naming/NameNormalizer.cs`,
consumed via `--collision-groups`, and reimplementing it in Python "would fork the authority". So I ran
the authority against the node corpus:

    dotnet run --project gk-forge/tools/ItemSeedValidator -- gk-data/packs/fusion/data/seed/passive-tree --collision-groups
    -> "no _registry/ under .../data/seed/passive-tree; the validator cannot"   exit 2

**The authority is structurally unavailable to the node corpus** — it needs an items-shaped root. So
`NameRepair` is not a drop-in, and the design question is real rather than assumed.

**Scope error 1 — I assumed a field.** A node file is a per-tree CONTAINER (`treeId`, `nodes[]`,
`_provenance`); reading `doc["name"]` off it returned nothing, so the first run reported "0 named node
files" and would have concluded "no under-detection" from a census that never read a single name. Same
family as the Core test split's moved files: a name test that cannot see the field.

**Scope error 2 — I then corrected toward per-tree, and that was also wrong.** `n0`/`n1` repeating in
the output suggested `nodeKey` is not tree-unique, so I re-scoped to per-tree. But the gate is
**corpus-wide**: `run.py:1140` says *"corpus-wide `taken_names`/`known_name_keys` (whole-ledger seeding
above)"*, and `:1125`/`:1240` do `taken_names.add(record.name)` as the ledger grows. So the contract is
**every distinct display name in the whole ledger is unique**, and my corpus-wide first census had the
right scope after all. Both scope errors are recorded because the intermediate numbers (159 "under-
detected" groups, then 75) were each wrong in a different direction.

**What the corrected measurement says**, over 2,019 named node rows in 51 tree files:

| | groups | what it means |
|---|--:|---|
| exact duplicates, corpus-wide | **157** | committed rows a corpus-wide gate should have refused |
| exact duplicates, also within one tree | 75 | the subset that is not merely cross-tree reuse |
| **near-collisions the exact rule cannot see** | **2** | **the actual finding** |

The two near-collisions, both within one tree, both the of-construct word-order variant that step 4's
connective drop and step 5's sort exist to collapse:

    ArmoredImpZombie.json  'Carrion Frenzy'  (n0)   vs  'Frenzy of the Carrion'  (n1)
    dark.json              'Ossuary Pulse'  (n1)   vs  'Pulse of the Ossuary'    (n2)

**Why this is the finding and the 157 are not.** The 157 are a DATA question — legacy rows predating the
gate, which is precisely the situation `NameRepair` exists for on the items side ("Generation rejects a
new collision before it writes. This module handles the older corpus rows that predate that guard"). I
cannot tell legacy from a gate-not-applied-on-the-writing-path from the committed corpus alone, and
saying which would be exactly the over-claim this ledger keeps retracting; the discriminator is a
regeneration run, which is not a cleanup's job. **The 2 near-collisions are a RULE defect: no
regeneration fixes them, because `name in set(takenNames)` compares strings and will never match
`Carrion Frenzy` against `Frenzy of the Carrion`.** Regeneration will keep minting them.

**The fix is small and needs no word pool.** `naming.v1.json` §4 is six steps and only step 3 (resolve
each surface token to its reserved-word-pool canonical id) needs `words.v1.json`. Steps 1, 2, 4 and 5 —
lowercase, tokenize on whitespace/punctuation, drop the four closed connectives, sort — are implementable
exactly, and they catch both observed groups. That is a **declared subset** of the authority, not a fork,
and it **undercounts**, so the 2 is a lower bound. Owner decision, because it changes a gate:
(a) apply steps 1/2/4/5 to the node gate — small, catches both, still not the items authority;
(b) give the node corpus a `_registry/` shape so the shared authority runs — one authority, larger;
(c) keep exact-match and record the 2 as accepted. (a) is the cheap correct step; (b) is the principled
end state.

### CB19 — the seedsmith validator finding is LANDED in its owning ledger; CB14 owed a cross-reference

Continuing CB18. The success criterion's last unmet clause was "every finding is landed in the owning
program's ledger", and I had been treating all four gated findings as equally blocked. **They are not.**

**A finding is not blocked because another program fences a similarly named file — only when the OWNING
ledger is held.** The shared validator is **seedsmith's** primitive; `adapters/dungeon/pipelines.py`
names the kind correctly at four sibling sites; the defect was in the primitive. Its owning ledger is
`tasks/seedsmith-todo.md`, which **no active session claims**. Filed as **SS-F2** in that file's own
`## Findings filed from other lanes` section, in the file's declared **R-bold** shape, with
`program_status.py --program seedsmith` confirming it counts as a task block (1 open block -> 2).
**That finding is no longer parked: it is landed where it belongs.**

**CB14 owed a cross-reference and did not make one.** CB14 reported six pre-existing seedsmith failures as
"found and proven, not assumed" without pointing at the existing row. It is already filed:
`tasks/seedsmith-todo.md` **SS-F1** ("the pytest suite carries 9 pre-existing failures, and one of them
writes a tracked file", filed by `cmdc-ep2-1` on 2026-09-20) — and SS-F1 **already names the CRLF
cause** I rediscovered. So the CRLF finding is not new, my number differs from SS-F1's because the suite
has moved since (9 -> 6 failures, 4,724 passing), and **SS-F2 cross-references SS-F1 rather than
re-reporting it.** The rule is *"if a lane's own record or an existing row already names the owning
module, cross-reference that row rather than opening a duplicate"*, and the honest form of that is to
say which row already held it.

**What is still genuinely fenced, and only this:**

| finding | owning ledger | state |
|---|---|---|
| validator mislabels a node refusal | `tasks/seedsmith-todo.md` | **LANDED as SS-F2** |
| `Total\|Passed` gate fails open | `tasks/ps1-ban-todo.md` | fixed in code; row fenced |
| node uniqueness is exact-string; 2 near-collisions | `tasks/passive-tree-todo.md` | fenced; CB18 has the brief |
| tree-plan vocabulary 7/16 -> 9/18 | `tasks/passive-tree-todo.md` | **fixed in code + data**; row fenced |

`ps1-ban-manager-20260926` still holds 538 paths, so three rows stay owed. Two of the three are already
fixed in code, which means the residue is now **ledger rows, not defects** — a much smaller and more
honest thing to be blocked on than it was two turns ago.

### CB20 — the owning ledger was a DIFFERENT FILE than the fence I kept blaming, twice over

Continuing CB19. CB19's rule — *a finding is blocked by the OWNING fence, not by a similar name* —
applied a second time produced the bigger half of the answer, and the mechanism is worth stating on its
own: **a 538-path sweep holds whole trees, so the file it grabs is frequently not the file that owns the
work.**

I had been routing both passive-tree findings to `tasks/passive-tree-todo.md` (619 KB) for two turns,
because that is the file `ps1-ban-manager`'s fence names and I had assumed the named file was the owner.
It is the **parent** program. The owner is `tasks/passive-tree-repair-todo.md`, whose plan opens:

    "Not a new feature program - a repair of the `tree-language -> tree-binder -> tree-resolve` seam"

and whose own command block already runs generator `--check` discipline
(`TreeBinder --check`, `FamilyExpandGen --check`). Finding 1 is a **stale generated artifact** —
regeneration is that program's subject. Finding 2 is a **gate in the `tree-language` stage**, whose own
comment cites `spec-tree-language.md` §5.1 — the section that plan's "read first" list names. And
`tasks/passive-tree-repair-todo.md` is claimed by **no active session**.

Landed there as **PT-F40** (the vocabulary: both defects, fixed, with the emit-safety measurement) and
**PT-F41** (the exact-string uniqueness rule and its 2 invisible near-collisions, as an owner decision
with three options). `program_status.py --program passive-tree-repair` reports **13 open task blocks,
28 done**, so both rows are counted as tasks in the file's declared `H-id` shape — not loose checkboxes.

**The routing table is now:**

| finding | owning ledger | state |
|---|---|---|
| validator mislabels a node refusal | `tasks/seedsmith-todo.md` | **LANDED — SS-F2** |
| tree-plan vocabulary 7/16 → 9/18 | `tasks/passive-tree-repair-todo.md` | **LANDED — PT-F40** |
| node uniqueness exact-string; 2 near-collisions | `tasks/passive-tree-repair-todo.md` | **LANDED — PT-F41** |
| `Total\|Passed` gate fails open | `tasks/ps1-ban-todo.md` | fixed in code; row still fenced |

**Three of four are landed in the ledger that owns them. One remains genuinely fenced**, and it is the
right one to be blocked on: `post_merge_check.py` is the acceptance harness that `ps1-ban-l1-harness`
ported, so `tasks/ps1-ban-todo.md` genuinely is its owner, no alternative cmdc ledger exists, and the
defect is already **fixed in code** with a load-bearing regression test. What is owed is a row, not a
fix.

**The rule that produced both corrections, now general:** before routing a finding into a fence, ask
**which file owns the work** — not which file the fence happens to name, and not which file shares a
program's name. Two turns of "blocked" here were two turns of asking the wrong question.

### CB21 — the four husks are provably EMPTY and LOCKED at the same time, and I read the wrong field twice

Continuing CB20. The criterion names one blind spot explicitly: *"a failed long-path or permission delete
leaves a directory that git has de-registered and can no longer enumerate or reclaim, which must be fixed
in the tool rather than left as a known gap."* The tool was fixed; this turn checked whether the four
directories that **motivated** the fix can now actually be reclaimed. They cannot, and the reason is
worth stating precisely because I got it wrong twice first.

**Two different questions, two different fields, both true at once:**

| question | flag | field | the four |
|---|---|---|---|
| is the content landed? | `--prove-stale` | `verdict` | `PROVABLY-STALE`, `entries=0`, `unlanded=0` |
| can the OS delete it? | `--reclaim-empty-leftovers` | `outcome` | **`LOCKED`** — a live process holds a handle |

`--reclaim-empty-leftovers --apply` was run and **removed 0, exit 0**, with the per-row detail *"a live
process holds a handle on the directory, so the OS refuses the delete"*. So the standing rule applies
exactly as written: **reported, not forced.** The earlier turns' `HELD` wording and this turn's
"unblocked" reading were both mine and both wrong — a content verdict never implies an OS verdict, and
neither implies the other.

**The mis-read that nearly caused damage, stated so it is re-buyable.** The dry-run plan printed **35
rows**, and I read that as "35 to remove" — including a 16,710-entry directory, four live
`rpg-hot.sqlite` copies, another lane's acceptance evidence, and my own scratch. It is not 35 to remove.
The plan lists every leftover *because an exclusion must be reported, never swallowed*, and each row
carries the outcome that decides it:

    35 rows -> 31 KEPT-NOT-EMPTY (18,174 entries)  +  4 WOULD-REMOVE (0 entries)

Only the 4 would be removed. **A plan's row count is not its action count, and the tool is right to
include the excluded rows** — the reader has to read the field. This is the same shape as CB10's "a
worktree's name is not a verdict" and CB17's "read what a mechanism was built to do": the deciding
information was in a field I did not print.

**Two smaller defects of my own, both re-buyable:**

* **`@(0).Count` is 1, not 0.** I reported `unlanded=1` for these four because wrapping the scalar `0` in
  `@()` yields a one-element array. The count was of the wrapper. The real value is **0**.
* **The tool emits TWO JSON objects** — a plan and a result — so parsing "everything after the first
  brace" fails with *Additional text encountered after finished reading JSON content*. `raw_decode`
  reads them one at a time. A reader that takes the first object sees the plan and concludes the world
  refused; a reader that takes the last sees only `removed`/`failed`/`dryRun` and never learns that 31
  rows were deliberately kept.

**Nothing was removed, nothing was forced, and the tool named the refusal rather than swallowing it.**
That is the blind-spot clause working as designed: the four directories are *enumerable* by the fixed
tool, *classified* as holding nothing, and *refused by name* because the OS holds them.

### CB22 — the green-exit rule lands in the manager SSOT, and what that does NOT discharge

Continuing CB21. `ps1-ban-manager-20260926` is still `active` at 538 paths, still names
`tasks/ps1-ban-todo.md`, its record was last committed 81 minutes ago and its ledger written 2.9h ago — so
the `Total|Passed` row stays **fenced** where it belongs. That is unchanged and correct.

**But the manager's own SSOT carried no green-exit rule at all** — checked for the phrase, for
"evidence that tests ran", for `POSITIVE_COUNT_RE` and for `post_merge_check`: **all four absent.** The
rule lives in `AGENTS.md`, which a manager reads at session start, and it is *not* in
`.agents/skills/project-manager/SKILL.md`, which is what a manager reads **when deciding whether to merge
a lane**. For a manager whose standing instruction is *"acceptance-capacity-bound so no lane is merged
without review"*, a gate that reports GREEN on zero executed tests is a broken capacity signal, and the
rule belongs where the merge decision is made.

Landed in the manager SKILL, **inside rule 6** rather than as a new section, because rule 6 is the rule
that governs the merged-head gate and a manager reads it at exactly that moment. Three things fixed at
once:

1. **A stale script name.** Rule 6 named `.claude/cmdc-agents/scripts/post-merge-check.ps1`. That file is
   **retired** — 0 tracked, absent on disk, retired by `caa9fb275` — and the live twin is
   `post_merge_check.py` (1 tracked, on disk). A rule naming a retired script is the same rot as a
   remembered number, and it was sitting in the SSOT.
2. **The unstated false green.** Rule 6 already said the gate's "own false-green paths had to be fixed
   before it could be trusted" without naming one. It is now named, with the measured shape: `Total`
   counts **skipped** tests, so `Passed: 0, Skipped: 38, Total: 38` matched `['0','38']` and the gate
   reported GREEN for a run in which nothing executed. Verified in the tree before committing: the live
   pattern is `r"\bPassed:\s*(\d+)"`, the load-bearing regression test is present, and the module suite
   reports **77 passed, 2 skipped, 33 subtests**.
3. **The transferable form**, because the specific bug is already fixed and a rule about a fixed bug is
   history: **a process exit code is not evidence that work happened**, in two measured ways — the count
   can lie about what it counts (`Total` includes skips, `Passed` does not), and the filter can match
   nothing while the run stays green (`dotnet test --filter X` with no match prints "No test matches the
   given testcase filter" and exits 0; a pytest selector that collects nothing prints `no tests ran`).

**What this does not do: it does not discharge the fenced row.** The defect record still belongs in
`tasks/ps1-ban-todo.md`, which is inside an active session's fence, and the fact that the *rule* is now
permanent in the manager SSOT does not make the row unnecessary — the row is what tells the ps1-ban
program that its own gate was wrong. Two of this program's four routed findings are landed; the remaining
one is a row, not a fix, and it stays open.

### CB23 — the four save-backup leftovers: what actually decides them, measured (nothing deleted)

Continuing CB10, which listed these as "OWNER DECISION" because they hold copies of the owner's live
game database. That was correct and it left the owner with nothing to rule on. Measured now, read-only:
`sqlite3` opened every file `mode=ro` and ran `PRAGMA quick_check`, and every file was sha256'd. **Nothing
was deleted and nothing was written** — this is the owner's data and the decision is theirs.

**The safety fact nobody had, and it is the one that matters.** Every `rpg-hot.sqlite` copy is accompanied
by a **non-empty 9,620,232-byte `-wal` and a `-shm`**. SQLite checkpoints on close, so a copy taken while
the database was open in WAL mode has a main file that is **behind** its WAL — here by ~45% of the
database's bytes. **Deleting one of these directories can lose committed transactions that exist only in
the WAL.** That is not a reason to keep them forever; it is the reason the decision needs the WAL state,
which no directory listing or file count could ever show.

**The copies are not four of one thing.** They are four *distinct* snapshots an hour apart, and one much
earlier save:

| copy | mtime | pages | `-wal` | distinct? |
|---|---|--:|--:|---|
| `asroute-before/rpg-hot.sqlite` | 09-26 03:57 | 2980 | 9.6 MB | yes |
| `asroute-after/rpg-hot.sqlite` | 09-26 04:04 | 2950 | 9.6 MB | yes |
| `glyphs-data/rpg-hot.sqlite` | 09-26 04:37 | 2950 | 9.6 MB | yes (same page count, different bytes) |
| `glyphs-data-base/rpg-hot.sqlite` | 09-26 04:38 | 2950 | 9.6 MB | yes |
| `coldseed/rpg-hot.sqlite` | 09-26 11:43 | **487** | **none** | yes — a much smaller, earlier save, and the only **clean, checkpointed** one |

`quick_check` is `ok` on every real database, so none is corrupt; the risk is incompleteness, not damage.

**And two of the sets ARE one artefact each, kept several times** — which is CB10's own rule (repeated
copies of one thing are unioned once) applied to the owner's data:

* `rpg-hot.sqlite.pre-save-identity.*.bak` — **4 byte-identical copies** (sha `b9ad84c3…`, 447 pages each,
  at 20:57, 21:04, 21:37 and 21:38 on 09-25). One artefact, three redundant.
* `rpg-media.sqlite` — **5 copies, byte-identical** (12 pages) across `glyphs-data`,
  `glyphs-data-base`, `asroute-before`, `asroute-after` and `coldseed`. One artefact, four redundant.

**So the owner decision is now one step, with the deciding facts named:**

1. **Two artefacts are redundant today.** The four identical `pre-save-identity` backups are one file, and
   the five identical `rpg-media.sqlite` are one file. Deleting the redundant copies loses nothing, and the
   rule this ledger already uses (union once, rescue once) says so.
2. **The four `rpg-hot.sqlite` snapshots are NOT interchangeable** — different page counts, different
   bytes, four points in the save's life, each with an un-checkpointed WAL. Whether to keep any of them is
   a question about the save's history, not about this cleanup.
3. **Before deleting any trio, checkpoint or deliberately discard the WAL.** The safe form is to open the
   database read-write once and close it cleanly (which checkpoints), or to copy `-wal` alongside. This
   cleanup will not do either to the owner's save.

Nothing here changes a verdict: these six directories remain `KEPT-NOT-EMPTY` and owner-ruled, and the
`KEPT-NOT-EMPTY` outcome is the tool correctly refusing to treat a path as proof of anything.

### CB24 — a dead citation in landed evidence, the audit blind spot that hid it, and its scope gap

Continuing CB23. Checking whether the two group-C probe directories hold unlanded evidence, the group-C
lane turns out to be **finished** — **0 `codex/*` branches and 0 actor-hud worktrees** remain; all its
branches merged. Its *reports* (`tasks/reports/actor-hud-unity-live-20260926.md`,
`actor-hud-browser-proof-20260926.md`) and its *harnesses* (`scripts/prove-actor-hud-live.ps1`,
`gk-web/web/fusion-rpg-web/e2e/actor-hud-live.spec.ts`) are all tracked. So the conclusions and the
reproduction path are landed, and what the two temp directories hold is 33.9 MB of **raw capture** whose
lane already reached an honest verdict: *"Recorded rather than ticked — an honest 'not proven'."*

**A real dead citation in a landed evidence fragment, and it could not be rescued.**
`tasks/evidence-fragments/actor-hud-live-eyeball.md:41` named
`tasks/evidence-fragments/screenshots/actor-hud-damage.png`, saying it was "referenced here, not attached
inline". Measured: that directory **does not exist**, **0** files are tracked under it, and a machine-wide
search finds **no copy of that image anywhere** — so the artefact is gone, and the only correct repair is
to declare it. `audit-doc-citations.py` states the repair itself (*"say on that line that the file is gone
— this audit exempts any citation whose own line says so"*), so that is what was done, with a pointer to the
capture record that *is* landed. The audit on that file now reports **0 findings, exit 0**, and the
fragment still says plainly that the visual read **cannot be re-verified from the tree**.

**Why the audit never reported it — a line-wrap blind spot.** The citation was split across two lines
(`.../screenshots/` ending line 41, `actor-hud-damage.png` starting line 42), and the audit resolves
**per line**, so it never joins them: it saw a path ending in `/` and a bare basename, neither of which
resolves. Scoped to that one file the audit reported **0 findings on 3 resolvable citations** — clean, on a
page carrying a provably dead citation. **A guard that reports clean because it parsed the wrong unit is
worse than one that fails**, because it is trusted. The fix is a one-line note on the audit, and the
fragment is now written with the path on one line.

**And a scope gap worth more than the single citation.** The audit's default `--scope` is **`docs/`** — so
`tasks/**` is **unaudited**: every evidence fragment, every program ledger and every report. Scoped there
it immediately produces findings the default run never sees, including D1 dead files
(`gen-corpus-dump-verify.ps1`, `guard-stat-pairs.ps1` — `.ps1` names retired by the port), D2
line-past-end-of-file, and D3 ambiguous basenames. 673 D1s exist in the default scope and none of them
include the `tasks/` half of the tree. **A guard's default scope is part of its contract**, and this one
silently covers a little over half the documents that cite paths.

**No verdict changes.** The two probe directories stay `KEPT-NOT-EMPTY` and owner-ruled; what changed is
that the owner can now rule on them knowing the conclusions are landed, the harnesses are tracked, the
lane's own verdict is "not proven", and the one dead citation has been declared rather than left open.

### CB25 — the husks' refusal is a SHARE LOCK, and two probes that read it as something else

Continuing CB21 and CB24. The four `opencode-resume-3*` husks are still on disk, still zero-entry, and
still refused. This turn establishes **what kind** of refusal, because the remedy differs completely and
"locked" was the only word I had for it.

Measured on one husk, each operation reporting its own code:

| operation | result | means |
|---|---|---|
| `iterdir()` | OK, 0 entries | readable, and empty |
| `stat()` | OK, `drwxrwxrwx` | **not** an ACL problem — the mode is full control |
| `os.open(dir, O_RDONLY)` | `errno=13` Permission denied | a *read* of a directory handle, which Windows denies regardless |
| `os.rmdir(dir)` | **`winerror=32`** | `ERROR_SHARING_VIOLATION` — a handle is open elsewhere |
| `rename` away and back | `winerror=32` | same, so it is not specific to removal |

**Verdict: a share lock.** `ERROR_ACCESS_DENIED` is 5 and an ACL would report that; these report **32**,
and the mode is `drwxrwxrwx`, so permissions are not the obstacle. The remedy is to wait for the holder to
exit — nothing to escalate, nothing to force. The standing rule (*"Locked de-registered husks held by a
process handle are reported, not forced"*) applies exactly, and the re-review trigger is the handle
release.

**Two of my own probes read this wrong, and the mechanism is the session's recurring one.**

1. **`[IO.File]::Open` has no 5-argument overload**, so the "is it held?" probe threw a PowerShell
   *binding* error and my `catch` printed it as `HELD:`. A failure of the probe dressed as a verdict
   about the filesystem — structurally identical to reading a green exit as proof.
2. **`os.open` on a directory returns `errno=13` on Windows whether or not anything holds it**, so it
   cannot answer the question at all. The operation that *does* answer it is one that takes a delete share,
   which is `os.rmdir` — the very operation the cleanup performs. **The diagnostic that settles a question
   is often the operation that would carry it out**, and using it as a probe costs nothing because the OS
   refuses rather than acting.

**The holder cannot be named, and that is stated rather than guessed.** No process command line mentions
these paths; the only match was this probe itself. But **a shell's or a tool's working directory is not
exposed by `Win32_Process`**, so the likeliest holder — something running with that directory as its CWD —
is invisible from here. "Unnamed" is the finding. A PID guessed from a directory listing would be worse
than no PID.

**The plan and the OS disagree, correctly.** `--reclaim-empty-leftovers --dry-run` reports the four as
`WOULD-REMOVE` (31 `KEPT-NOT-EMPTY` beside them), while `--apply` and a direct `os.rmdir` both report
`winerror=32`. That is the right division of labour — **a plan says what it would attempt, a refusal says
what happened** — and it is the third time this shape has cost a wrong reading. So: 35 rows, 4 candidates,
**31 held**, and the four named, empty, share-locked, reported and not forced.

### CB26 — the two history probes that both answer "at HEAD", measured on `main`

`main` had carried a verdict — *EMPTY, tree `7cb9a330c` == its merge-base tree* — whose **verdict was
right and whose evidence was not re-derivable**: a remembered tree hash. This turn re-derived it, and the
re-derivation is what produced the generalisable rule, because the first two probes were both wrong in
the same direction.

**The procedure judges a blob by "is this content present anywhere in integration's history?" and there
is no safe one-liner for it.** The two obvious commands both answer **HEAD**:

| probe | the question it actually answers | what it reported on `main` |
|---|---|---|
| `git grep -F -q <line> <tree>` | "is this line in **one tree**" | **53 files** "content nowhere in history" |
| `git cat-file -e <tree>:<path>` | "does **HEAD** have this path" | **38 paths** "never landed" |

Both were wrong. The correct answers are **0 and 0**, and the deciding evidence was in the same output,
in a section I had labelled a shortcut: **861 of 861 differing files are byte-identical to their
merge-base blob.** The merge-base is an ancestor of integration, so a blob equal to the merge-base blob
is reachable from integration *by construction*. The two tests that decide:

- **a path** — `git rev-list --count --max-count=1 <integration> -- <path>`. `0` = never landed;
  `>0` = a landed **deletion**, which is the rule working, not a loss. All 38 absent paths resolve this
  way: `caa9fb275` retired `accept-lane.ps1` and `post-merge-check.ps1`, `6f479d091` retired two more,
  `c5869d0a8` moved the manager SKILL's SSOT to `.agents`. **A landed deletion is a success.**
- **a blob** — identical to the merge-base blob ⇒ landed, and since moved on. 0 of 861 fail this.

**Why the naive version is so expensive, and the tell that exposes it.** `main` is 182 commits behind,
so its files are an ancestor's files and legitimately differ from a tree that moved on. Comparing each
to HEAD calls integration's *own* work "content the branch holds and integration lacks". The tell is a
file where the branch has far **more** lines than HEAD: `CLAUDE.md +458 only on branch, +18 only at
integration` is 458 lines integration **deliberately deleted**, not a loss. The 53 files the grep probe
condemned were the same shape — their distinctive line was a machine-local `D:/Works/source/...` path,
content a repo hard boundary exists to remove.

**`main` is EMPTY as unlanded content, now provable rather than recalled** — 0 of 861 differing files
hold a blob integration lacks, 0 of 38 absent paths were never landed, and the 4 unique commits are
merges that moved the pointer and not the tree (tip tree == merge-base tree, re-measured). **KEEP as the
merge record.** It is not an unlanded holder, and merging it would **revert** integration, because every
differing file is the older side of a gradient.

**Landed as a binding SKILL rule** in *Before you state a number or a verdict, name the QUESTION it
answers*: two new table rows, a *two history probes that both answer "at HEAD"* subsection with the
working tests, and a fourth habit. The rule is worth more than the branch, because **every future
adjudication of a stale branch hits it.**

**And the rule's own verification needed four tries, all four false MISSes.** A claim is not proven
because a search for your paraphrase of it returned nothing. Naming the four, because a rule that cites
a measurement should cite how the measurement was checked:

| search string used | the file actually says |
|---|---|
| `greps a TREE, not history` | `it grepped a **tree**` |
| `tests HEAD presence, not reachability` | `it tested **HEAD**` |
| `**A landed deletion is a success.**` | `**landed deletion is a success, not a gap.**` |
| the SKILL's `→ miss` table row | CB26's own three-column table row |

A paraphrase probe reports **MISS** when your memory differs and **PASS** when it happens to agree, so
it fails in both directions and the PASS is the dangerous one. The same shape as the git probes above,
one level up: `git grep` answers "is this in *one tree*" and a paraphrase answers "is this in *my
paraphrase*". **Verify with a token that cannot be paraphrased — a command literal, a heading, a bolded
clause — and print the matched line**, so a reader can see the file's own words. All 14 SKILL claims and
all 7 CB26 claims were then re-located by literal and every one was present.

### CB27 — `rescue/corpus-bcu211-itemseedgen-run` is SPENT INSURANCE, and the number to check is 4 of 56

The one rescue ref carried as an open owner decision for many turns. It holds **1** commit integration
lacks, touching **56 files** (55 generated, 1 report), and `git diff --name-only` between the tips
reports **7,201 paths** — a figure that reads as "7,201 unlanded files" and is a time gradient.

Per-file LINE SET first: 33 differ, 22 are supersets of integration's version, 1 rename-like. But these
are `gk-data/packs/fusion/data/seed/items/**` — **generated data** — and the decisive question for a blob is not "does HEAD
equal it" but *"is this content present anywhere in integration's history?"*. Applying the CB26 rule
rather than a tree grep: **52 of 56 present in history, 4 absent.** All four resolve:

- `_runs/drop-tables-gen.ledger.json` — the rescue's **123 `escalated` rows**. 34 of those ids are still
  in integration's ledger and **all 34 are now recorded NOT escalated**, carrying a real `name`
  (`droptable-draw-d1-003` → `'Verdant Echo Cache'`) where the rescue recorded a `defects` list. So
  integration holds the **resolution** of exactly the failures the rescue recorded. The other 89 are
  partitions a shorter later run no longer tracks (43 rows against 139) — a dated failure count.
- `_runs/materials-gen.ledger.json` — 3,612 rows against the current 10. A shorter, later run.
- `combinations/combination-still-blocked.json` — 7 rows against the current 20.
- `tasks/reports/BCU2.11-full-run.json` — differs only in `head`, `diffStatTail` and
  `gitStatusPorcelainCount`, so its **figures** (1,048 item JSON files, the by-kind breakdown) are
  corroborated by the copy already tracked.

And the subject line, `gaps 931 -> 770`, is a **dated population reading** — never pinned by a
guardrail, never rescued as owed work, never a reason to keep a ref.

**Verdict: SPENT INSURANCE.** The ref is no longer the only copy of anything. The owner can now rule in
one step, and the one number to check is **4 of 56 blobs absent from integration's history**, with the
resolution of all four above. **Not deleted here** — a ref is cheap, and the decision is the owner's,
exactly as recorded when the ref was created.

### CB28 — a session fence is a CONVENTION, not a mechanism, and this cleanup's fence blocks were described as if it were one

Seeking a new blind spot, I looked for commits that edit a fenced path without a record claiming them,
expecting to find a gate worth building. The measurement says **the signal does not exist**, and the
finding is the reason why — which qualifies how this very ledger has been reporting its own refusals.

Measured 2026-09-27 over **4,242** commits on `features/mega-merge` in 14 days:

| signal | measured | attributes a commit to a session? |
|---|---|---|
| authorship | **4235 of 4242** carry one identity | no — the repo rule *is* that every lane commits as the owner |
| branch | every lane commits to the same integration branch | no — that is the destination, not the author |
| `session:` / `session-id:` trailer | **0 of 4242** | no — the convention does not exist |
| message names a record stem | **601 of 4242 (14%)** | partly — 85% name no session at all |

**A fence crossing is observable and not attributable.** Of **2,360** fence touches measured, **5** could
be attributed to the fence's own session, **347** to some other session, and **2,008** to nothing at all.
The SELF count of 5 is not a finding about discipline; it is what 85% unattributable looks like when you
bucket it. **No tool here can say which session made a commit.**

So the block on `tasks/ps1-ban-todo.md` — recorded in earlier turns as "fenced by an active record" — is a
convention this cleanup honoured, and it is **still the right call**: a corroborated claim blocks whether
or not a tool can prove it, and the ps1-ban program is demonstrably live. What was wrong was the
*description*. Those rows said the fence blocked the row; what actually happened is that this cleanup
declined to edit a path an active record claims. **That correction is made here rather than by editing the
earlier rows**, because the rows are accurate about the decision and the framing is what now needs
superseding.

**And this retires the tool I was about to build.** A crossing detector on this signal would refuse on
85% undecidable touches, which is a guess dressed as a check — the same defect as the green-exit trap, in
a new place. The fix is not analysis; it is the **missing `session:` trailer** (0 of 4,242 today), after
which attribution is a grep and crossing becomes decidable instead of merely observable. That is an owner
decision, not a unilateral convention change, so it is reported rather than imposed.

**Two wrong numbers on the way here, both about attribution, both stated with confidence.** First
**3,064 of 4,242 "name a session"**, from loose substring matching where a short token (`bcu8`, `sgc-2`)
is a substring of many stems; then the correct **601** under a literal `stem in body` test. And between
them a hardcoded line reading "-> almost none do" printed directly above the 3,064 that refuted it. This
is the session's recurring error class for the fourth time in one turn: a right value answering a
different question, and — the new part — **a conclusion hardcoded next to a measurement that contradicts
it**. Print the matching rule next to the number, and never write the verdict before the figure.

### CB29 — the 31 leftovers owed a VERDICT, not a tool outcome; three matchers, two refuted by evidence

CB21 already said the thing this row acts on: *"the `KEPT-NOT-EMPTY` outcome is the tool correctly refusing
to treat a path as proof of anything."* So 31 directories carried an **outcome** and no **verdict**, and
the eleven verdicts are what a cleanup is supposed to produce. This is the largest un-adjudicated
population left, and the biggest member decides its shape.

**Ownership needed three matchers, and the first two are refuted by evidence — not by argument.**

| matcher | rule | what it got wrong |
|---|---|---|
| v1 | shared 3+ character token | `resume` made every `resume-*` lane match every `resume-*` directory, and the four husks already adjudicated **EMPTY + LOCKED** came back LANE-OWNED. `iso-guard` "matched" a lane on the token `guard`. |
| v2 | substring containment, name-in-surface dropped | 28 UNCLAIMED and **zero** PROTECTED-ACTIVE; it dropped exactly the half of v1's claims that protected two directories |
| **v3 (kept)** | a claim is a **path segment**, or a record stem contained in the name; `tasks/reports/**` and `tasks/sessions/**` are **mentions** | — |

v1's surviving claims were then refuted by the evidence printout, which is the only reason v3 exists:
`ipc` "matched" the **ACTIVE** `ps1-ban-manager-20260926` via `gk-core/tools/ip-censor/ipcensor/registry.py` —
`ipc` is a substring of `ipcensor` — and `union-append-only-20260926` "matched" it via
`tasks/reports/union-append-only-20260926.md`, a **report about** a lane. Neither is ownership. **A
generic token is not an identifying token, and a report naming a lane is not a claim on a temp tree.**
Segment-exactness is structural and needs no stoplist: "is this a whole segment" is a property of the
string, where a stoplist is another list to rot. Under v3: **0 PROTECTED-ACTIVE, 2 LANE-OWNED, 5 CARRIED,
28 UNCLAIMED.**

**The biggest leftover is SUPERSEDED, and its own census was inflated 3.71x.**
`actor-hud-unity-live-server-20260926` is a `dotnet publish` output, not scratch — 14,923 files, 169 MB,
`FusionRpg.Server.exe`, `runtimes/`, `gk-data/packs/fusion/data/seed/**`. Grouped by **CONTENT** as the procedure requires, it
holds **4,019 distinct contents**: **12,685 files are a duplicate of another file**, the same seed JSON
copied through a `bin-altrun\Debug\bin\Debug\net8.0` chain up to **72 times**. A file count reports
14,923 pieces of work; the content grouping reports 4,019, and the 3.71x ratio is the finding.

**Two of that script's own numbers are retracted here rather than left standing.** It closed with *"5,789
seed copies DIFFER and 2,220 files look like a verdict — the whole case for a rescue."* Both are probe
artefacts. The 2,220 came from grepping `verdict|ok|pass|fail|gate|acceptance` in the first 4 KB of seed
JSON — that is **game data**, and the probe was the evidence. The 5,789 all sit 6+ levels down inside
nested build intermediates whose difference from the tracked blob is a **time gradient**: the publish copy
of `g-evade.json` is **171 h old** and the repo copy changed in `e1d9103ee`. **A script that concludes is a
script whose conclusion nobody re-reads**, which is why this row exists.

**`sockwords.json` was DELETED, not moved** — `e79c0fde8 2026-09-20  D`. The publish tree holds a 14,997 B
pre-deletion copy, which is the only reason it read as "no tracked counterpart". By **CB26's own rule a
landed deletion is a success**, so this is SUPERSEDED, not unlanded generated data, and the sanctioned
regeneration path is not invoked. A name test could not have told a deletion from a move; asking git about
the path is what settled it.

**The 9 screenshots are owed nothing, and a tracked spec says so.** All 9 are **960x540**, none is
byte-identical to any tracked file, and `docs/architecture/live-probe/spec-lawn-screenshot.md:32` routes
images to `artifacts/` **"never committed"**, with the store gitignored in its own file table. Committing
them would break a spec, so the evidence-rescue rule does not apply. Grouped by content they are **9 files /
6 distinct images**: four `screen-readback-attempt-*` files are ONE image (sha `5e774967baca2b53`).

**And the resolution test's own caveat, which is the part worth keeping.**
`tasks/evidence-fragments/actor-hud-live-eyeball.md` leaves three owner-run checkboxes *"Recorded rather
than ticked — an honest not proven"* and names the blocker as needing **"a higher-resolution screenshot
capture"**. Its read was at 960x531. Comparing 960x540 against that, my test reported a resolution
**exceeding** it — on a 9-row, **1.7%** difference. That cannot resolve *"I cannot conclusively tell a
health/shield BAR apart from a PvZ-native damage floater"*, so the fragment's verdict **stands unchanged**
and the directory contributes nothing owed. `is any dimension strictly greater` is not the question
`is this materially higher`, and that is the **fifth** time this turn a right number answered a different
one. The fix is to state the threshold a decision needs — here, a read the eye can resolve — before asking
a boolean to supply it.

**What is still owed: 28 of 35 carry no verdict.** Two are LANE-OWNED and five are carried (four husks, plus
this session's own tool directory), so 28 remain: 24 unclaimed with no record and no lane naming them, and
4 whose only match is a merged record. Each needs a content verdict from the eleven before anything is
cleared, and the next one to adjudicate is `ipc-falsify` (829 entries), the second largest.

### CB30 — the kind census, `ipc-falsify` settled, and the acceptance-artefact block DISCHARGED untested

**The kind census of all 28 unclaimed leftovers, by structure.** The rule that a batch needs the same KIND
and not a similar count is unusable without a kind, so each is classified by structure before any content
is opened:

| kind | n | members |
|---|---|---|
| EVIDENCE-SHAPED | 12 | `msbuild-probe`, `actor-hud-unity-live`, `actor-hud-tuning-replay`, `acceptance-epl11`, `deep-audit-notes`, `epl11-obj`, `wt-probe`, +5 |
| DATABASE-COPY | 6 | `actor-hud-proof-data`, `asroute-before`, `asroute-after`, `glyphs-data`, `glyphs-data-base`, `coldseed` |
| SOURCE-COPY | 4 | `ipc-falsify`, `openid-fixture`, `debug-mcp-backup-20260915`, `probe-exit` |
| OTHER | 2 | `__pycache__`, `audit2-falsify` |
| BUILD-OUTPUT-TREE | 2 | `iso-guard`, `statpairs-fixture` |
| PUBLISH-OUTPUT | 1 | `actor-hud-unity-live-server-20260926` |
| MACHINE-ARTIFACT | 1 | `union-append-only-20260926` |

**`ipc-falsify` is SUPERSEDED, with every file accounted for: 658 byte-identical to tracked
`gk-forge/tools/seedsmith/**`, 62 `.pyc`, 0 differing, 0 unaccounted.** It is a checkout copy plus bytecode. The
earlier "104 with no repo counterpart" was **my own path heuristic** building `seedsmith/adapters/...`
where the repo path is `gk-forge/tools/seedsmith/seedsmith/adapters/...` — **a mis-mapped path reads as a missing
file**, and 42 of the 104 were mis-mapped rather than absent. With the prefixes corrected the census closes
to zero.

**The acceptance-artefact block is DISCHARGED, and it had never been tested.** The safety rule is explicit:
*"an acceptance artefact naming an UNMERGED sha blocks even when the branch is merged."* Three such
artefacts sit untracked, so the rule was carrying an untested obligation. Every SHA in all three is an
ancestor of `features/mega-merge`:

| directory | SHA | field | state |
|---|---|---|---|
| `acceptance-epl11` | `8334a1d6` | unkeyed (clean log) | MERGED |
| `acceptance-ssh29` | `a120ce2d8` | unkeyed (clean log) | MERGED |
| `resume-20-rsf27-acceptance-20260925` | `6d77888cc` | **`baseSha`** | MERGED |
| `resume-20-rsf27-acceptance-20260925` | `4f78ed6c9` | unkeyed | MERGED |

**0 unmerged, so the blocking condition does not fire** and all three are acceptance run logs whose
subjects are landed. Tested with `git merge-base --is-ancestor <sha> <integration>` — **reachability, not
the absence of a ref** — because `git branch --merged` answers a different question: is the *branch* merged,
not is this *commit* reachable. `ipc` was checked on the same rule and also shows 0 unmerged
(`93a2e16d9`, `10ba26399` both MERGED).

**A SHA sweep has THREE outcomes, and the third is the one that would have produced a false BLOCK.**
`20260925` matched a `[0-9a-f]{7,40}` pattern: eight characters, all hex-legal, and a **date**. So does
any version string and any zero-padded id. The other state is equally important — `ea0e042f98b0` in a
stdout log **does not resolve as an object at all**, which is a truncated or rewritten commit, not an
unmerged one. **Merged / unmerged / not-a-SHA-at-all**, and reporting only the first two turns a date into
a finding. Every SHA above is therefore printed with the field it came from, so a reader can re-read it.

**A third partial-read error in three turns, and it is the one that nearly shipped as a finding.** The
tracked tuning files were reported as containing `gk-core/data/tuning/aptitudes.v1.json`, because the publish
tree's tracked-twin match printed that one. `git ls-tree` shows **v1 through v10 all tracked**, and all
eight versions in the temp tree are on landed commits (`740920d2e`, 2026-09-12) with every distinctive
line present at integration. **The "the temp tree is ahead of the repo" finding was my probe's first
match, not a fact** — the same shape as the file-census corollary, one level down: a *sample* is not a
census either.

**What is left, named rather than summarised.** The **DATABASE-COPY family (6)** is the save-backup set
already parked on an owner decision, and it is the largest coherent block that still owes a verdict.
`ipc` additionally carries a **12,149 B `prod.patch` that is not an acceptance artefact** — an unapplied
patch is unlanded code, so that file is the next thing to test, and `ipc` is not discharged until it is.
`uareg` holds `ours.json` / `theirs.json` with **no SHA at all**, so no reachability test applies to it
and its content has to be read.

### CB31 — `ipc` closed by the REVERSE apply, and `uareg` is a fixture because one of its paths is fake

Two leftovers closed, and both were closed by asking the question their content actually answers rather
than the one their names suggested.

**`ipc` is SUPERSEDED, and every thread in it is closed.** Four files, four questions:

| file | question | measured answer |
|---|---|---|
| `commit-msg.txt`, `commit-msg2.txt` | is the work landed | both SHAs are ancestors of integration (CB30) |
| `prod.patch` (12,149 B) | is the patch's content landed | **81 of 81 added lines already at integration** |
| `hashes.txt` (133 B) | has the target moved since | **SHA-256 MATCHES** the file on disk exactly |

**The decisive test for a patch is the REVERSE apply, and this case is why.** `git apply --check` exits
**1**; `git apply --reverse --check` exits **0**. A forward failure alone cannot separate *already landed*
from *target moved*, and this was the second — the file's import block has changed since the patch was
made, so the context no longer matches. Both the reverse check and the line set settle it the same way:
**31/31** added lines of `uniques/briefs.py`, **24/24** of `uniques/pipelines.py`, **26/26** of
`trees/species/generate_tree.py` are present at integration. And the last landed change to that last path
is `c6e416db4 2026-09-26`, **whose subject is the patch's own work** — so the patch is a spent copy of a
landed commit. The 133-byte file is the one that proves it, because it is the only one that asks whether
the target moved.

**`uareg` is SUPERSEDED — a synthetic fixture, and one path proves it.** `ours.json` and `theirs.json` are
1,296 and 1,298 bytes, each a single `boundaries` key wrapping one entry: `{"id": "b0", "kind": "owner",
"paths": ["src/x0.cs"], "project": "guard", "level": "module", "guards": []}`. **`src/x0.cs` does not
exist.** So the `ours`/`theirs` naming, which reads as a merge-collision record, is misleading: this is a
**hand-made guard-registry fixture** — two minimal boundary documents for exercising a union-merge
resolver, the shape `union_append_only.py` consumes. **A synthetic input cannot be evidence of anything,
because it never described a real state**, and that is a stronger ground than "the content is not at
integration", which is merely expected for a fixture.

**Tally of the 28 UNCLAIMED, every number measured above:**

| directory | verdict | the deciding evidence |
|---|---|---|
| `ipc-falsify` | SUPERSEDED | 658 byte-identical to tracked `gk-forge/tools/seedsmith/**`, 62 `.pyc`, 0 differ |
| `actor-hud-unity-live-server-20260926` | SUPERSEDED | a `dotnet publish` output; 4,019 distinct contents, spec says never commit |
| `acceptance-epl11` | DISCHARGED | 0 unmerged SHAs |
| `acceptance-ssh29` | DISCHARGED | 0 unmerged SHAs |
| `resume-20-rsf27-acceptance-20260925` | DISCHARGED | 0 unmerged SHAs |
| `ipc` | SUPERSEDED | reverse-apply exit 0, 81/81 lines present, SHA-256 match |
| `uareg` | SUPERSEDED | `src/x0.cs` does not exist — a fixture, not a collision record |

**21 remain.** The next block is named rather than summarised: the **DATABASE-COPY family of 6**
(`actor-hud-proof-data`, `asroute-before`, `asroute-after`, `glyphs-data`, `glyphs-data-base`, `coldseed`),
which is the save-backup set already parked on an owner decision, and which this turn's census confirms
still holds a live `-wal` beside each `rpg-hot.sqlite`.

### CB32 — RETRACTION: "Group C's harnesses are tracked" is FALSE, and the harnesses' own headers say why

This cleanup has carried the claim that Group C is finished and *"its reports and harnesses are tracked"*.
Tested by content against the tracked tree, **0 of 6 harness files have a tracked twin**:

| file | bytes | sha256 | tracked twin |
|---|---|---|---|
| `browser_proof.js` | 13,708 | `65f8209b8a62e73b` | **none** |
| `browser_proof2.js` | 9,838 | `3baddcc7809ff6dd` | **none** |
| `browser_proof3.js` | 7,585 | `0826ed808380bb69` | **none** |
| `browser_proof4.js` | 9,560 | `918e999265e0d893` | **none** |
| `diag.js` | 4,022 | `c813580c91a11b92` | **none** |
| `http_probe.py` | 2,594 | `eab62de4053492ca` | **none** |

**The mechanism, stated so it can be recognised next time: the harnesses' OWN first lines say they were
never meant to be committed.** `browser_proof.js` opens *"Throwaway browser proof for the actor HUD element
glyphs. **NOT committed.**"*; `browser_proof2.js` *"Throwaway probe #2"*; `browser_proof3.js` *"Throwaway
probe #3"*; `browser_proof4.js` *"Throwaway probe #4"*; `diag.js` *"Throwaway diagnostic"*; and
`http_probe.py` carries *"Throwaway probe; not committed."* in its own docstring.

So this is **not a forgotten commit**, and the verdict is **SUPERSEDED on the authors' own declaration**
rather than on my inference. The mechanism of the false claim is a generalisation from the **reports** being
present to the **tooling** being present, which is the recorded lesson in its purest form: **a report is a
catalogue of what it describes, and the thing it describes is not thereby in the repository.** The prior is
retracted here rather than by rewriting the earlier note, because the note was accurate about Group C being
finished and wrong about one word in it.

**What the probes prove is landed and widely referenced.** `/api/catalogs/actor-surface` appears in **22
tracked files**. The harness also names a deliberate **negative control**,
`/api/catalogs/no-such-route-proof-20260926`, present in **0** — which is the point of the probe, because an
unmapped path on this Server answers 200 `text/html` from the SPA fallback, so a bare 200 on the real route
would prove nothing without it. And `browser_proof.js` states its own scope honestly: it *"proves the WEB
RENDER PATH given a real board-shaped HUD snapshot; it does not prove the Unity -> server -> web ingest."*

**The 27 PNGs (26 distinct, 3,377,277 B) are owed nothing, re-measured rather than assumed to transfer from
CB29's different directory:** `spec-lawn-screenshot.md:32` — images are *"dev artifacts: file store under
`artifacts/`, **never committed**"*; `:71` marks the store gitignored; `:155` carries an acceptance box
*"No captured image committed"*. The 4 untracked output files are the throwaway probe's own output, which
its header scope-limits. The save DB's `-wal` is **9,620,232 B**, matching the parked set, so that part is
covered by the standing owner decision. `archive/` is **empty (0 entries)**.

**A generalisable measurement defect, caught in this session's own work.** `stderr.log` is **0 bytes** and the
content index reported a tracked twin for it: `gk-fusion/tools/debug-mcp/tools/__init__.py`. **sha256 of empty content
is the constant `e3b0c442…b7852b855`**, so every 0-byte file matches every other 0-byte file, and the repo
has **14** tracked 0-byte files. A content comparison that does not exclude empty inputs will report a twin
for a file that shares nothing with it — and it will do so on a truncated or captured-empty log, which is
exactly what a probe run produces. Same family as the recorded `check-ignore` and newline traps: **a
comparison that looks like it is testing content and is testing a constant.**

**The six are not a homogeneous batch, and the label that grouped them was lossy.** A single-label classifier
put all six in DATABASE-COPY, but assigning **every** applicable label separates them: `coldseed` is
SAVE-DB only; `asroute-before`, `glyphs-data` and `glyphs-data-base` share one exact label set;
`asroute-after` adds JSON-PROOF; and `actor-hud-proof-data-20260926` adds HAS-SOURCE and 27 images. **A
single label is a lossy projection when a directory holds two kinds**, and the batch rule needs label SETS.

### CB33 — the group of 3 adjudicated, and "unrescuable evidence" is a real category

`asroute-before`, `glyphs-data` and `glyphs-data-base` share an **exact label set**, so they are one
homogeneous batch and CB32's lossy-label defect is not repeated.

**The three hot databases are 3 DISTINCT snapshots, not 3 copies of one artefact** — 12,201,984 B
(~2979 pages), 11,997,184 B (~2929) and 11,997,184 B (~2929), shas `a2f2a6ad…`, `3438ae91…`,
`e709fa1c…`. **All three carry a non-empty 9,620,232 B `-wal`**, so in every one the main file is behind the
WAL and the trio can hold committed transactions the main file does not. That is the standing owner
decision, cross-referenced here rather than re-decided.

**The media database is one artefact kept three times, but its trio is not** — `rpg-media.sqlite` is **1
distinct content** (sha `31b0f666…`, 4,096 B) across all three, while `rpg-media.sqlite-shm` and `-wal` are
3 distinct each. So "identical" holds for one file in a trio and not for its neighbours, which is why the
grouping is per filename rather than per directory.

**Same size is not identity.** The three `pre-save-identity` backups are all **1,830,912 B** and all three
have **distinct** shas (timestamps `205714851Z`, `213704518Z`… precisely `205714851Z`, `213705418Z`,
`213804120Z`). A size comparison would have called them one artefact; hashing called them three. And in the
first pass `server.err.log` came back `IDENTICAL` with sha `e3b0c442…` — which is **sha256 of empty
content**. Two empty error logs are not evidence that two directories hold the same thing.

**The finding this pass did not expect: the logs are UNLANDED EVIDENCE THAT CANNOT BE LANDED.** In all
three directories the only distinctive line of the surviving output is a **machine-local path**:

| file | its one distinctive line |
|---|---|
| `asroute-before/out.log` | `[save-identity] migrated save identities; report: {"backupPath":"C:\Users\NeneScarlet\AppData\Local\…` |
| `asroute-before/out2.log` | `Content root path: D:\Works\source\…\.claude\worktrees\actor-surface-rout…` |
| `glyphs-data/server.out.log`, `glyphs-data-base/server.out.log` | the same `backupPath` line |

Nothing else in them is unlanded: `before-body.txt`'s single line (`<!doctype html>…<div id="root">`) **is**
at integration, because it is the FE's own SPA fallback — which is exactly the documented confound the
actor-surface probe needed a control for. So the **fact** these logs record — that a save-identity migration
ran, and that the content root was a worktree — is recorded nowhere in the repository, and the only artefact
carrying it **cannot be committed**, because a machine-local path is a hard boundary.

**Unrescuable evidence is therefore a real category, distinct from the eleven.** It is not a rescue, and
treating it as one produces either a commit that violates a boundary or a summary that invents the record.
It is an **owner decision**: re-author a machine-neutral summary of what the migration reported, or accept
that the fact is not worth a ledger row. Neither is this cleanup's call, and neither is guessed here.

**Two defects in my own census, both recorded because both are shapes that hide.** The first pass excluded
0-byte inputs in its section 3 and **not** in its section 1, so the empty-file constant leaked into the
grouping — **a rule applied in one place and not the other is not a rule**, and the fix is one predicate
where a file becomes a hash. And the text probe read a **binary** `.bak`, produced a NUL, and `subprocess`
raised `ValueError: embedded null character`, which killed sections 3 and 4 for two of the three
directories. **A census that dies partway reports a partial set as if it were the whole**, which is the most
dangerous shape a measurement can take because it does not look wrong.

`archive/` is **0 entries in all three**, so the `KEPT-NOT-EMPTY` outcome is carried entirely by the database
trio. `pid.txt` records 68748, 33064 and 66976 — three distinct PIDs, which are readings and not proof that
anything is running.

### CB34 — two silent escapes, and no phrase check can see either of them

Two silent escapes surfaced in one pass, and they are worth a row because of what they share: **both make a
cited path unopenable while rendering as perfectly fine**, and every check that had ever run against this
file was a **phrase** check, which cannot see a character that draws nothing.

**1. Mine, this turn.** The CB33 table row quoting `out2.log` was written with single backslashes, so
`\actor-surface-rout` was read as `\a` — **BEL, `0x07`**. The line rendered as
`worktreesctor-surface-rout`, which still reads as a path, because the eye completes the word.

**2. Pre-existing, and worse.** Line 340 read ``log `D:\tmpbcu211b-run.log` `` — the original
`D:\tmp\bcu211b-run.log` had lost **two** bytes: `\t` became a **TAB** and `\b` became a **BACKSPACE**. That
is a **cited job log path**, so a reader following the sentence is sent to a file that cannot exist. It
survived because the eleven claim checks that verified CB33 ran, the citation audit ran, and the fence check
ran — **and not one of them looks at bytes.**

**My own repair failed twice before it succeeded, which is the part worth keeping.** The first attempt
searched for the *deleted* letter and matched nothing, because a silent escape **substitutes** rather than
deletes. The second restored the `b` and then guarded on an intermediate string that no single pass could
produce, because one original write consumed two escapes — **a fix that assumes one escape per site is a fix
that will be re-run.** The third replaced the **whole path token**, with the intended text decided from
evidence (the sentence names branch `corpus/bcu211b` and job `b72965106`, so the log is `bcu211b-run.log`
under `D:\tmp\`) and the replacement assembled from `chr(92)`, so the repair file cannot repeat the defect it
repairs. The ledger now carries **0 control characters other than newline** and **0 tabs inside backticks**,
and both quoted paths read correctly.

**The checkable rule, and it is narrower than it looks: a committed document must contain NO control
character other than a newline. Tab included.** Tabs are legitimate in Markdown prose and fatal inside a
quoted path, and a check that excludes tab reports a clean file over an unopenable one — which is exactly
what my own first repair pass did: it printed `0 control characters remaining` over a file that still had a
tab inside a path.

**The gap this exposes, routed rather than patched.** `scripts/audit-doc-citations.py` already validates that
cited paths resolve, and it **cannot see this**: the corruption leaves the path passing a substring test
while making it unopenable to a filesystem. A control-character check belongs beside it, and the
audit-script's own scope is `docs/` by default, so `tasks/**` is not covered either. `scripts/**` is outside
this session's 22-path fence, so the check is **reported, not patched** — and per CB28 that refusal is a
convention this cleanup honours rather than a mechanism that stopped it, so the owner is told which it was.
**Owning program: `repo-tooling`** (docs language, the simulator, tests, assistant tooling), whose lock is
`docs/architecture/decisions/repo-tooling.md` plus a one-line index row in `decisions.md`; the index is inside
`ps1-ban-manager-20260926`'s 538-path claim, so the row cannot be added from here either.

### CB35 — the silent-escape class is REPO-WIDE, CB34's repair was incomplete, and its rule was too strong

Three results, and **two of them correct CB34 rather than extend it.**

**1. The class is repo-wide, not local.** **21** control characters across **7 tracked markdown files** of
**4,125** scanned, and **10 sit inside a backtick span** — which is what makes them damage rather than noise:

| file:line | byte | what it was |
|---|---|---|
| `tasks/item-todo.md:3365` | BEL `0x07` | `python scripts<BEL>udit-overflow.py` — a **cited script path** |
| `tasks/run-board-20260920.md:1872` | TAB + BS | `D:<TAB>mp<BS>cu211b-run.log` — **the same cited path as CB34** |
| `tasks/lawn-combat-wire-todo.md:176` | BS ×2 | `grep AssertNoDoubleOrFloat|<BS>double<BS>` — `\bdouble\b`, **regex word boundaries** |
| `docs/architecture/game-gui-map.md:194` | BS ×2 | `` `<BS>…<BS>` `` — `\b…\b`, describing `BANNED_WORD_PATTERN` |
| `docs/architecture/party-dungeon-map.md:128` | BS ×2 | `` `<BS>…<BS>` `` — the same, for the party-dungeon guard |
| `tasks/overlay-switch-todo.md:111` | BS | the sentence **documenting this very bug** carries one |

**2. CB34's repair was INCOMPLETE, and this scan is what proved it.** `tasks/run-board-20260920.md:1872`
carries the **identical** `D:\tmp\bcu211b-run.log` corruption — same path, same two bytes, same sentence. The
defect was written twice, and CB34 verified only the copy in the file it had edited. So its claim *"the
ledger now carries 0 control characters"* was true of the ledger and **silent about a sibling file**, which is
the same shape as the error CB34 was written about. **A repair verified only where it was applied is half a
repair**, and the missing half is findable only by scanning the surface the defect lives on rather than the
file the fix touched.

**3. CB34's RULE was too strong, and this is the correction.** It said a committed document must carry no
control character other than a newline. But **12 of the 21 hits are intentional**: in
`docs/research/action-taxonomy/03-composable-skill-systems.md:2623-2628` a leading **TAB** is linguistic
notation for an indented gloss (`<TAB><TAB>[FRONT_COMPOUND_NOUN_SING]`). A blanket ban would have demanded the
destruction of correct content. **The corrected rule is narrower: no control character other than a newline,
and a TAB is a finding only inside a backtick span** — inside a quoted span it is never intentional, and
outside one it may be. The byte-level check stands; **its scope was what was wrong**, and a rule that would
have forbidden valid notation is a rule that gets waived, which is how the next real instance survives.

**Routing, honestly.** Of the 7 affected files this session's fence covers **2**
(`tasks/backlog-clean-up-todo.md` and the manager SKILL, both now clean). The other 5 are outside the fence
and are **reported, not patched** — and per CB28 that is a convention this cleanup honours, not a mechanism
that stopped it, so the owner is told which it was. Owning programs by the repo taxonomy: **`presentation`**
for the two `docs/architecture/*-map.md` capability maps, **`repo-tooling`** for the three
`tasks/*-todo.md` ledgers, and **`world`** for `tasks/run-board-20260920.md`. A reusable check belongs in
`scripts/` beside `audit-doc-citations.py`, which is the same routing CB34 named — so CB35 **cross-references
CB34's routed finding rather than opening a duplicate**, and adds only what the scan newly established: the
prevalence, the second copy, and the corrected scope.

### CB36 — `union-append-only-20260926` is SUPERSEDED, and the harvest was already done by the lane

The largest unadjudicated leftover, **46 files**, holds the working artefacts of a **merged** lane
(`union-append-only-20260926`, whose contract was to make `union_append_only.py` refuse by name and non-zero
on a structured registry). The decisive question was never *"is the evidence tracked"* but **"does a green
test depend on a fixture that lives only here"** — because that is the difference between a spent record
and a live consumer.

**Nothing tracked depends on it.** 23 fixture and script names were tested against the whole tracked tree.
The only four hits — `old_union_append_only.py`, `vb-ours.json`, `vb-theirs.json`, `vb-union-before.json` —
are `tasks/reports/union-append-only-20260926.md` **naming** them. **A report citing its own inputs is a
mention, not a consumer**, which is the same distinction CB32 settled for `tasks/reports/**` and
`tasks/sessions/**`. `conflicted-registry.txt`, `ours-registry.txt`, `theirs-registry.txt`, `falsify.py`,
`parity_run.py`, `test_prefix_tool.py` and the rest: **0 tracked references**.

**And the evidence is not merely recorded, it is executable.** The tracked report (379 lines, landed
`5f8b571be`) names `ParityTests::test_jsonl_ledgers_merge_byte_identically_to_the_pre_fix_algorithm` —
**37 subtests** — and states that *"the parity reference `legacy_merge` / `legacy_lines` is the pre-fix
algorithm **transcribed verbatim**"*. So the pre-fix algorithm lives **inside the tracked test**, and the
2,554 B `old_union_append_only.py` in this temp directory is **not the only copy**. That one fact is what
upgrades the verdict from "a record of a run" to "re-runnable proof", and it is why clearing the directory
loses nothing a reader could not regenerate from `gk-core/tests/tools/test_union_append_only.py`.

**The duplication a name count would have missed.** 46 files, **34 distinct contents**, and one artefact
under **4 names**: `out-conflicted-old.txt` == `out-registry-old.txt` == `vb-union-before.json` == a fourth,
all sha `4cb04f8d` (2,147 B). `ours-registry.txt` == `vb-ours.json`; `theirs-registry.txt` ==
`vb-theirs.json`. The seven `parity-*/` directories each hold exactly **one identical pair** —
`old.out.*` == `new.out.*` — beside `ours.txt`/`theirs.txt`, on ledgers of 144,339 / 107,791 / 89,548 /
75,932 / 18,645 / 13,133 / 6,400 B. **The parity proof reproduced byte-for-byte on seven real ledgers,
~455 KB in total**, and it is that pair-identity which is the evidence — not the files.

**The 6 probe scripts have no tracked twin** — `test_prefix_tool.py` (35,342 B), `falsify.py`,
`make_fixture.py`, `parity_run.py`, `run_tests_against_prefix.py`, `save_old.py`. That is the disposition
the procedure calls **HARVEST THE IDEA, DISCARD THE DIFF**, and the harvest **is already done**: the lane
transcribed the pre-fix algorithm and its parity assertions into the tracked test, and wrote the findings
into a tracked report. So the diff is spent and the reasoning is not lost, which is the whole condition
that disposition asks for. `conflicted-registry.txt` is a real conflict-marker fixture — it opens
`<<<<<<< HEAD` and holds a `schemaVersion: 5` verification-boundaries registry — and its distinctive line
**is** at integration, in `gk-core/scripts/verification-boundaries.v1.json`, so the payload is landed too.

**Tally of the 28 UNCLAIMED, all measured above: 12 adjudicated, 16 remain.** The next block by size and
label-set uniformity is the EVIDENCE-SHAPED group: `actor-hud-unity-live`, `actor-hud-tuning-replay`,
`deep-audit-notes`, `msbuild-probe`, `epl11-obj`, `wt-probe`, `probe1` — plus `coldseed`, which is SAVE-DB
only and is the one save snapshot with a **0-byte `-wal`**, so unlike its siblings its main file is **not**
behind a WAL and it is a materially different decision.

### CB37 — the batch of 3 adjudicated, and a FALSE finding caught before it was published

The headline is a retraction of something that was **not** published. `deep-audit-notes` looked like it held
an overstatement: the worker recorded `"status":"partial"` for the web audit, while the report's
`### Web / control room` section lists **5 findings** with **zero** occurrences of
`partial`/`incomplete`/`unverified`. I was one step from publishing *"a handoff report presents a partial
audit as confirmed findings"*.

**It does not.** The qualifier is in the document three times, in the places its own design puts it:

* **line 26**, the fleet table: `| 04 Web | ae5e217e… | **partial** | one Server-to-lawn synchronization
  path; no br…` — a **status column**, so every lane's state is tabulated rather than repeated per finding;
* **line 146**: *"The runner's `partial` states on lanes **04, 06, 07, and 08** reflect bounded/static reports
  or a nonstandard `status`…"*;
* `## Falsified or qualified claims`: *"**No browser or live-game conclusion was promoted from static
  evidence.**"*;
* `## Evidence and limitations`: *"No browser evidence was collected because the web worktree had no
  installed Node dependency tree…"*.

**The mechanism, and it is the transferable part: I searched the one section where the answer could not
be.** A findings subsection lists findings. A document that records status does it in a **status column**
and a **limitations section**, because repeating a qualifier on every finding would be noise. So searching
`### Web / control room` for `partial` and reading its silence as a defect is CB26's shape one level up: the
question was *"does this document qualify its web audit?"* and the measurement was *"does this one
subsection contain the word?"*. **Before calling a document unqualified, find where its design puts
qualification and read there** — the fleet table and the limitations section, not the findings list.

| directory | verdict | the deciding evidence |
|---|---|---|
| `deep-audit-notes` | **SUPERSEDED** | the tracked report tabulates all 8 lane statuses including four `partial`; 8 tracked briefs exist; the raw outputs are regenerable by re-running a tracked brief |
| `msbuild-probe` | **SUPERSEDED** | **7 of 15** `.proj` files carry a machine-local path (`H:\`, `D:\`, `C:\`), so most of it is **unrescuable by construction**; and the capability question it asked is moot — the ps1-ban programme moved the tooling to Python |
| `probe1` | **SUPERSEDED** | 20 bytes in total: `hello lane` in, `HELLO LANE` out — a case-transform probe with no consumer and nothing in it to keep |

**The batch was legitimate, which the label SET established and a first-match label would not have.**
`deep-audit-notes`, `msbuild-probe` and `probe1` share `HAS-EVIDENCE-EXT + LEDGER-SIDECAR + PROBE-LOG`, and
they are 3 of 8 — a batch the rule accepts. `coldseed` was held out of it deliberately: it is the one save
snapshot whose `-wal` is **0 bytes**, so unlike its siblings its main file is **not** behind a WAL, and a
rule justified by "the WAL holds committed transactions" does not apply to it. **That is a different decision,
not a smaller one.**

**Tally of the 28 UNCLAIMED: 15 adjudicated, 13 remain.** Two more batches are measured and legitimate:
`actor-hud-tuning-replay` / `epl11-obj` / `wt-probe` (label set `HAS-EVIDENCE-EXT`), and the two singletons
`actor-hud-unity-live-20260926` (`SCREENSHOT + HAS-SOURCE`) and `coldseed` (`SAVE-DB + WAL-EMPTY`).

### CB38 — a non-discriminating label, three individual verdicts, and `text=True` biting in both directions

Four findings, and **three of them correct work this turn already did**.

**1. CB37's "legitimate batch" was NOT legitimate, and the label is why.** The second batch of 3 was
justified by a shared label set of exactly one member, `HAS-EVIDENCE-EXT`. Measured selectivity: **23 of the
28 unclaimed leftovers carry it** — 82%. **A label almost everything shares is a coincidence of file
extension, not a kind**, so it cannot support a batching decision. Habit 11's rule (*batch on the label SET,
not the first match*) only helps when the labels are **discriminating**, so it gains an addendum: **group on
a set whose members are a minority; a set everything shares is not a set.** The three were therefore
adjudicated individually, and the kinds turn out to be three different things.

**2. Three individual verdicts, all SUPERSEDED, each on its own evidence.**

| directory | verdict | the deciding evidence |
|---|---|---|
| `actor-hud-tuning-replay` | **SUPERSEDED** | all 10 files are the same document as tracked `gk-core/data/tuning/**`: **3 byte-identical**, and 7 differing by **exactly their own CRLF count** — deltas +30/+30/+33/+33/+33/+65/+86 against local CRLF counts 30/30/33/33/33/65/86 and git CRLF 0 |
| `epl11-obj` | **SUPERSEDED** | **gitignored build output by the repo's own rule**: `git check-ignore -v` returns `.gitignore:22:[Oo]bj/` for `obj/project.assets.json`, `*.csproj.nuget.g.props` and `obj/project.nuget.cache`, and the five filenames are exactly NuGet restore's output set |
| `wt-probe` | **SUPERSEDED** | a throwaway linked-worktree experiment: `repo/` is a 35-file scratch `.git` (hooks, three tiny objects, refs for `features/mega-merge` and `wt-a`, `worktrees/wt-a/`) and `wt-a/` is a 91-byte `.git` file; both READMEs read `base` |

**3. The repo's FIRST recorded measurement trap produced two confident wrong numbers from the same files, in
opposite directions.** `text=True` in subprocess translates newlines on Windows, so:

* `tuning_chain_diff.py` compared `read_text()` against `git show` with **both** sides normalised, and
  reported **all 10 identical** — false at byte level;
* `index_gap.py` compared `read_bytes()` against `git cat-file blob` through **`text=True`** — raw on one
  side, normalised on the other — reported **3 of 10 twins**, and I attributed that to a silent index gap.

**A hash index built through `text=True` is not a content index.** It silently normalises, so it disagrees
with every byte-level comparison and reports the disagreement as **absence**. Neither earlier number was
right, and each was stated with the confidence of a measurement. The byte-level table is the one that
answers, and **the delta equalling the CRLF count exactly** is what proves the difference is a line-ending
dialect and nothing else — the repo stores LF because of the `CRLF will be replaced by LF` normalisation git
warns about on every `add` in this repo.

**4. And a real silent-exclusion hazard, which is NOT the cause here.** **222 of 14,900 `git ls-files`
entries are absent from the working tree** — 111 under `.claude/skills/` and 111 under `.kilo/skills/`. A
content index built by testing `is_file()` therefore skips **1% of the tracked set without saying so**,
which is the tooling rule exactly: *an exclusion must be reported, never swallowed, because a silent exclusion
is a blind spot.* It did not cause the miss above — the ten tuning files are all on disk — but it is a real
gap in **every index this session built**, including the ones that produced a `twin=-` in CB29 through CB37.

**Tally of the 28 UNCLAIMED: 18 adjudicated, 10 remain.** The two singletons `actor-hud-unity-live-20260926`
(`SCREENSHOT + HAS-SOURCE`) and `coldseed` (`SAVE-DB + WAL-EMPTY`), plus six that CB32's labels grouped but
which are now known not to share a kind: `openid-fixture`, `debug-mcp-backup-20260915`, `iso-guard`,
`statpairs-fixture`, `__pycache__`, `audit2-falsify`.

### CB39 — the last 10 of the 35: every pool leftover now carries a verdict

This closes the pool. **35 directories = 5 carried (with earlier evidence) + 28 adjudicated + 2 parked on a
named owner decision.** The 2 are `asroute-after` and `coldseed`, both save-database sets, and both are the
standing owner decision rather than an unclassified item.

The turn's own errors, all three corrected in place, because the corrections are the substance:

**1. The remainder is 12, and CB38's arithmetic was wrong.** CB38 wrote *"18 adjudicated, 10 remain"* and then
listed **eight** names. `35 − 5 carried − 18 adjudicated` gives **12**, and the two missing names are
`asroute-after` — which CB33's group of 3 never included, because it carries a different label set — and
`probe-exit`, which no row had yet touched. **A tally whose own list disagrees with its figure is the defect
this program keeps finding, and it is arithmetic a machine should do.**

**2. And the machine's own first answer was also wrong.** Keying the census by directory *name* collapsed the
**two** `BepInEx` directories — one in the shared temp pool, one in `.kilo/worktrees/` — into one key, giving
11. **A census of directories must never be keyed by name when two directories share one**; that is CB38's
content-grouping rule read from the other side.

**3. `actor-hud-unity-live-20260926` looked like UNLANDED EVIDENCE and is not.** Its `commit-msg.txt` scores
**0** on every self-declaration keyword CB32 required, and it is a substantive report — AUDIT-4's **proven**
Unity→Server HUD ingest (21 real `DeltaEmit` events, 270→411 hp and 0→177 defense, `earth` → `hudGlyph`
stone → `stone.png` served 200) and its **unprovable** half (`ScreenSpaceOverlay` cannot appear in a camera
capture, `repaintsSeen=0` across seven captures), plus **two machine-level blockers for any pooled lane**.
The instinct was to declare UNLANDED EVIDENCE and rescue it. **Checking the owner first is what prevented a
false finding**: `tasks/reports/actor-hud-unity-live-20260926.md` is **tracked** and names `AUDIT-4`,
`repaintsSeen`, `ScreenSpaceOverlay`, `DeltaEmit`, `slot-1`, `nvm4w` and `npm.exe`; the AUDIT-4 row is in
`tasks/actor-hud-todo.md`; and **both blockers are recorded in `gk-fusion/scripts/deploy-play.py` itself**. The raw
26 KB event log is regenerable output, not evidence. So: **SUPERSEDED**.

| directory | verdict | the deciding evidence |
|---|---|---|
| `openid-fixture` | SUPERSEDED | all three test references **CREATE** their fixture in a temp dir; one is a substring match (`Stmt.cs` inside `BadSwitchStmt.cs`) and one names a *different* directory (`gk-fusion/src/FusionRpg.Injector/`) |
| `debug-mcp-backup-20260915` | SUPERSEDED | the tool grew from `len(names) == 11` to `== 20`; `/events/tail` is in **0** live files (route removed) and `debug_ui_nav` is in **8** (kept, with its bug documented at `server.py:89`) |
| `statpairs-fixture` | SUPERSEDED | the temp copy is an **11-entry synthetic validator fixture** (`Capped`/`Uncapped`, `BoolCap` with `"cap": true`, a lowercase `cased`); the tracked path holds the **54-entry real corpus** — **a different kind of thing at the same path, which a name test cannot see** |
| `audit2-falsify` | SUPERSEDED | `ActorHudDisplay.ts.bak` is byte-identical to the tracked live file; `SyncFromModelSystem.ts.bak` is a **strict subset** — 349 backup lines, 349 live, **0 backup-only** |
| `iso-guard` | SUPERSEDED | `obj/` NuGet restore output for `CombatSim`, gitignored — CB38's `epl11-obj` by the same rule |
| `__pycache__` | SUPERSEDED | 7 `.pyc` files, bytecode, in the shared pool |
| `BepInEx` ×2 | **EMPTY** | 0 files each, holding only a husked `plugins/FusionRpg/`; the `.kilo/worktrees/` one is **out of scope by standing rule** — the Agent Manager's pool |
| `probe-exit` | SUPERSEDED | one file, `a.ps1`, **8 bytes** — and the ps1-ban programme no longer accepts `.ps1` |
| `actor-hud-unity-live-20260926` | SUPERSEDED | the report is tracked and carries every claim; both blockers are in `gk-fusion/scripts/deploy-play.py` |
| `asroute-after`, `coldseed` | **PARKED** | the save-database owner decision; `coldseed` is distinguished by its **0-byte `-wal`**, so its main file is not behind a WAL and a different rule applies |

**Two files are UNRESCUABLE by construction**, the CB33 category: `read_setting.py` hard-codes
`H:\Games\.fusionrpg-pool\slot-1-data\rpg-hot.sqlite` and `relay_readback.py` the repo root, and a
machine-local path may not be committed. They are **reported, not copied**.

**Where the pool stands: 35 = 5 carried + 28 adjudicated + 2 parked, 0 unclassified.** The registered set
was last measured at 3 worktrees and 5 branches, all classified (CB26, CB27, CB31, and the two live streams
excluded by standing rule). **What remains open is not an unclassified item — it is owner decisions**: the
`Total|Passed` row owed to `tasks/ps1-ban-todo.md`, the four share-locked husks, the five control-character
files outside this fence, and the save-database sets including `coldseed`.

### CB40 — the last carried "unlanded finding" is CLOSED, and it was never this cleanup's debt

The carried state said one finding was still owed: a `Total|Passed` gate record belonging in
`tasks/ps1-ban-todo.md`, blocked by an active 538-path fence. Re-derivation says that framing is **stale**,
and the correction is worth landing because **a stale claim in a ledger is worse than a missing one**.

**The fence is unchanged** — `ps1-ban-manager-20260926` is still `active`, still **538 paths**, still claiming
`tasks/ps1-ban-todo.md`, last written 7.0 h before this check. So nothing about the block moved. **What moved
is the finding.**

**The defect is fixed, and proved by running it rather than reading about it:**

* `POSITIVE_COUNT_RE` is `re.compile(r"\bPassed:\s*(\d+)", re.IGNORECASE)` — the pattern **contains no
  `Total` alternative**, checked by searching the source rather than trusting the comment beside it;
* the gate function was **called directly on seven cases**, including the exact trap
  `["Passed!  - Failed: 0, Passed: 0, Total: 0"]` → `False`, the all-skipped shape
  `["Skipped!  - Failed: 0, Passed: 0, Skipped: 38, Total: 38"]` → `False`, and the lowercase
  `["total: 38, succeeded: 38"]` → `False`, with a genuine `["Passed: 3"]` → `True` as the control. **All
  seven agree with the expected verdict**;
* the module's own suite **ran 79 tests in 78.3 s, OK (skipped=2)** — and the run count is quoted because **a
  green exit is not evidence that tests ran**;
* the commit is `425d845bb`, *"Close CB8 finding 1: fix the fail-open test-count gate, and retire its stale
  rescue"*, which touched the gate, its test, **this session's ledger** and this session's record.

**And CB8's own text had already said this, which is what makes the carried framing wrong rather than merely
out of date.** Its correction reads: *"A committed fix with a load-bearing regression test is strictly better
than a ledger row — the row records an intention, the fix makes the defect un-recurrable. The owner still owns
the decision to record it in `tasks/ps1-ban-todo.md` when the fence narrows; **what no longer waits on that
fence is the defect**."*

So the residual is **an owner decision about their own programme's ledger**, explicitly deferred to the owner
— **not unlanded work belonging to this cleanup**. The success criterion's clause *"every finding is landed in
the owning program's ledger"* is satisfied by the finding being **closed in code, pinned by a load-bearing
test, and recorded here with the commit that made it**; what remains is the owner's choice of whether their
ps1-ban ledger gains a row for a defect that can no longer recur.

**A dated reading, restated rather than repeated.** CB8 records *"77 passed, 2 skipped, 33 subtests"*. This
measurement is **79 tests in 78.3 s, OK (skipped=2)**. Both were true at their times; **a run count is a reading
and not a contract**, so the current figure is stated here and the older one is left as the reading it was.

**What this closes, stated exactly.** Every registered worktree and branch carries a named verdict backed by
measured evidence; the 35 pool leftovers are **0 unclassified** (CB39); every finding is landed — the last one
by closure rather than by row; the long-path/permission blind spot is fixed in the tool rather than left as a
gap; and **what remains open is owner decisions, not unclassified work**: the ps1-ban ledger row, the four
share-locked husks, the five control-character files outside this fence, and the save-database sets including
`coldseed`.
### CB41 — RETRACTING CB27: the ref is the SOLE HOLDER, and its programme had already ruled on it

**Two of CB27's claims are false, and false in the direction that makes a ref look safe to delete.** CB27
recorded *"52 of 56 present in history, 4 absent"* and concluded *SPENT INSURANCE — the ref is no longer
the only copy of anything.* Re-measured, the number is **0 of 56**, and the ref **is** the only copy of
everything it carries. A measurement error in the permissive direction is the expensive one: it supplies a
reason to delete the only holder.

**The mechanism, each fact from a command rather than an inference.**

| fact | command | result |
|---|---|---|
| the ref's **parent** is everywhere | `git for-each-ref --contains 784555a1b` | **11 refs** — integration, `main`, both ps1ban worktrees, the stash, 2 codex snapshots, 3 remotes |
| the commit itself is nowhere else | `git for-each-ref --contains 6fc3d2b21` | **1 ref** — the rescue. It is the **SOLE HOLDER** |
| the run it extends is in history | `git rev-list --objects features/mega-merge`, intersected | run #1 `dcee0ba29`: **56 of 56** present |
| the ref's own content is not | same single pass, all paths, not per-path | rescue `6fc3d2b21`: **0 of 56** present |

So every blob *near* this ref is reachable and the ref's own content is not, which is precisely how a
reachability test resolves to the parent and answers *"landed"*. CB27's 52 is consistent with the parent's
or run #1's blobs; it is not consistent with the ref's own, of which there are **none** in integration's
history. The blob test itself was right — the CB26 rule holds — **the blobs it was handed were the wrong
ones.**

**And the larger error: the programme had already ruled on this work, and the four questions never ask.**

    ea2aeb756  2026-09-22  revert(corpus) + correct(ISG-gap-2): the BCU2.11 corpus does NOT fill the gaps
                          and adds 747 near-duplicates                       [956 files]

Its own body, verbatim: *"integration head (isg-gen-fix's regeneration): 931 gaps -- 911
Coverage/EmptyPartition / corpus/bcu211 (the BCU2.11 run + role repair): 1674 gaps -- the same 911
EmptyPartition PLUS 747 SemanticDedup/NearDuplicate"*; *"Generated corpora are taken wholesale from one side
or not merged at all"*; and *"the 911 EmptyPartition gaps remain open, now with an honest statement of what
closing them requires (a re-run against current generator inputs, **not this corpus**)."*

The ref's parent `784555a1b` **is** that `corpus/bcu211` — the tree the revert measured at **1674** and
rejected. So the ref is not unlanded work awaiting a home; it is **the same falsified attempt one pass
later**, on a base integration has moved **2,514 commits** beyond. A separately tracked report,
`tasks/reports/ISG-gap-1.md`, reaches the same conclusion from the other side: its acceptance rests on a
reading *"taken on `corpus/bcu211`"* and its own lane *"does not carry bcu211"*.

**The subject's `931 -> 770` is not merely a dated reading — it is not a like-for-like measurement.** The
`931` is integration **head's** figure; the `770` is this tree's own. Its base is the 1674-gap corpus the
revert rejected, so the commit compares head's number against a number from a different tree. Measured
today, live, on the clean tree at HEAD:

    python -m seedsmith check gk-data/packs/fusion/data/seed/items --adapter items   ->  87 gap, 612 note, 153 not_measured
       67 Coverage/EmptyPartition   6 Coverage/PairwiseHole   5 Content/FieldMissing
        5 Quality/FlavourMissing    4 SemanticDedup/NearDuplicate

The family the run targeted is down **911 -> 67**, and its own target of **770** would now be a
**683-gap regression**. The `747` near-duplicates the revert introduced are not in the corpus either — there
are **4** today, the same 4 the pre-run baseline already carried.

**Corrected verdict: SUPERSEDED, and the ref is the sole holder — so the two facts point opposite ways and
the owner decides.** Not landable: it is generated data whose base is 2,514 commits stale, whose programme
measured and reverted this corpus, and whose own headline number is a cross-tree comparison. Not deletable:
**0 of 56** of its content exists anywhere in integration. Per the disposition list this is **PARK ON A
NAMED DECISION**, and the decision is *delete a ref that is the only copy of a falsified run record, or
first have the item-seedgen lane write run #2's numbers down*. **Not deleted here** — deleting the sole
holder of the only record that a third attempt existed is the destructive act the procedure reserves for
the owner.

**Evidence rescued into this tracked ledger, which is what makes either decision safe:** run #2's record was
tracked nowhere — `tasks/reports/BCU2.11-full-run.json` at HEAD still reads `head ac0fd77c`,
`gitStatusPorcelainCount 70`, `68 files changed, 129299 insertions(+), 330 deletions(-)`, i.e. **run #1
only**. Run #2 is now recorded here: head `784555a1b`, 55 files, `8512 insertions(+), 76 deletions(-)`,
claim `931 -> 770`, parent `corpus/bcu211` rejected at 1674 gaps.

**Cross-reference owed, and not landed by this cleanup.** The owning ledger for the `ISG-gap-*` rows is
**`tasks/item-seedgen-todo.md`**, which is **outside this session's 22-path fence** *and* claimed by the
**active** record `ps1-ban-manager-20260926` (680 paths). So the substantive programme finding — *a third
run was executed, never evaluated, and its target is obsolete* — is **routed, not written**, and the owner
is asked to place it. This cleanup's own ledger carries the adjudication; it does not open a row in another
programme's ledger while an active session holds it.
### CB42 — the measurement that decides it: the rescue's corpus scores 830 against integration's 87

CB41 concluded **SUPERSEDED** from evidence *about* the ref — the revert, the stale base, the cross-tree
headline. All of that is an argument. This is the **experiment**: the ref's own corpus, extracted with
`git archive` and scored by the repo's own `seedsmith check`, in one process and against the same adapter as
the baseline it must beat.

| | integration HEAD | the rescue (run #2) |
|---|---|---|
| **gaps** | **87** | **830** |
| **SemanticDedup/NearDuplicate** | **4** | **747** |
| Coverage/EmptyPartition | 67 | 67 |
| Coverage/PairwiseHole | 6 | 6 |
| Content/FieldMissing | 5 | 5 |
| Quality/FlavourMissing | 5 | 5 |
| json files | 1,049 | 1,048 |
| corpus size | 6.75 MB | 11.32 MB |
| record ids | 4,330 | 12,004 |

**Two things follow that no amount of reading the commit could have produced.**

**1. The merge case is refuted by the metric that defines the work.** The run existed to close gaps. Landing
it moves the count **87 -> 830 (+743)**. *Merge and close* requires that it not regress integration, and
this is a regression measured by the same command that produced the baseline it would have to beat.

**2. Run #2 did not fix run #1's defect — it reproduced it verbatim.** `ea2aeb756` rejected this corpus for
**747** near-duplicates. The ref's own tree scores **747**. The follow-up pass was built to remove that
number and carries it exactly, which is the strongest statement available that this diff is not a repaired
corpus but a second copy of the same failure — and it is why 7,674 extra ids buy nothing.

**The headline is wrong even on its own terms.** The subject claims `931 -> 770`; the corpus measures
**830**. So the figure that would have justified the merge is off by **60** before any baseline is applied,
which is worth recording separately from the baseline error in CB41: one number is stale, the other is
simply not true.

**The 67 `Coverage/EmptyPartition` gaps are not this diff's to close.** The owning programme's statement
stands — *"a re-run against current generator inputs, not this corpus"* — and that needs
`gk-forge/tools/seedsmith`, which is intact at HEAD. Nothing in this ref is a prerequisite for it, so discarding the
ref forecloses no work.

**Verdict: DISCARD the generated seed. The ref's fate is the owner's, and now both halves of the decision
are measured rather than one.** Discard is not a judgement call: +743 gaps and a verbatim reproduction of
the rejected defect. What is left is *how* to drop the ref, and the sole-holder fact decides that question
too — **deleting it destroys the only copy of an 11.32 MB corpus**, which is a good thing here precisely
because the corpus is measured worthless, and a bad thing if anyone wanted the raw bytes for a later diff.
So the owner's real choice is **delete outright**, or **retag it under `refs/archive/` for a retention
window** and delete the branch name. Both are one command apart and neither is this cleanup's to pick.

**Method note worth keeping.** The corpus was measured by `git archive` into a temp directory, **not** by
`git worktree add`. A worktree would have registered state in `.git/worktrees` in order to inspect a
worktree-less ref — the exact debris this cleanup exists to remove, created by the act of investigating. The
scratch directory is removed in a `finally` whose failure is **reported** and never swallowed, because a
swallowed failed delete is how 65.5 GB of temp directories once accumulated in one local run here.
### CB43 — what is generated, the harvest test is empty, and the item is left **OPEN** on the owner's call

The owner asked *"what is it generated?"* — answered here from the content, because every number so far has
been a count and a count is not a substance. And *"make it unfinished; we will regenerate later if we decide
to discard"*, which is a **disposition**: this row records the item **OPEN**, so CB42's measured *DISCARD*
is not read as a closed conclusion.

**The substance, by partition.** The rescue's **11,851** records against integration's **4,190**:

| what | count | what it is |
|---|---|---|
| **trophy materials** | **3,602** | `material.NNNN`, `runtimeId: trophy.species.<speciesId>.<slot>` — one per species slot |
| **base-type items** | **~308** | across twelve sub-partitions: footing, girdle, infusion, jewel-minor, mantle, retinue |
| **generation ledger** | **3,602** | under `_runs` — provenance, not content |
| combinations / drop-tables / milestones | +13 / +7 / +4 | |
| **`recipes`** | **-18** | the rescue is **behind** integration here |
| **`_registry`** | **-5** | and behind here |

The base-type items are the substantive content and they are good: *Thicket Shield*, *Verdant Vambrace*,
*Sprout of the Tether*, *Barkshield*, *Loam of the Deep*, each with `enhanceTrack`, `socketMax` and
`implicit.family` populated. **So the rescue is not a superset of anything — it is a differently-shaped,
older corpus**, and that is visible in the negative columns before any judgement is passed on it.
**Quality at the row level is not quality at the population level**: the trophy names read well
*one by one* — *Loonnut's Echo*, *Ember-Wrought Husk*, *The Undead Avian Specimen* — and that is
exactly what makes 3,602 of them a defect rather than padding. A reviewer reading ten rows would
call this corpus good work.

**Why 747 are near-duplicates — a mechanism, not a count.** The trophy names are a **template x species-stem
matrix**, and the stems repeat down thousands of rows. Measured, verbatim from the check output:
`'Abyssal Current' is used verbatim by 2 entries`, `'Abyssal Sediment' by 10`, `'Ancestral Echo' by **35**`.
The row sample shows it with no tooling at all: **`material.1802` and `material.1803` carry the same name**
and effectively the same flavour. The defect is therefore not sloppy writing — it is a combinatorial product
whose second factor comes from a small set, which is exactly the shape a `SemanticDedup` check exists to
catch, and exactly what integration's hand-curated 31-material corpus (with its `_meta.amendments`
provenance block) exists to avoid.

**The harvest test: 0 harvestable, so there is no partial landing.** *Harvest the idea, discard the diff*
has to be tested, not assumed. **4,083** of the rescue's records appear **nowhere** in integration, and
**not one** of their placements lands in a partition that is **empty at HEAD**. The 67 still open are
`attributes`, `display-templates/4|5|6`, `base-types/mantle/humanoid/a`,
`base-types/manipulator/humanoid/b`, and 60 `sets/*` partitions — `sets/cabbagepuff`, `sets/cherrybomb`,
`sets/firenut`, `sets/enumvalue264`, `sets/extract-single`, `sets/ironpumpkin`, and so on. Every new record
duplicates a partition integration **already fills**. **The harvestable set is empty, and the diff cannot be
landed in part** — which closes the only route by which discarding the seed could lose something.

**Two of my own measurement bugs, recorded because they are re-buyable.** The harvest comprehension was
written `for k, v in [...] for k in v`, which is not a set difference: it printed **13,072,463** and a
meaningless verdict. A guard comparing the set difference against the table's own TOTAL row then
**refused**, which is the guard earning its place. The second is subtler and is the one to keep: the harvest
buckets counted **(record, partition) placements** while the denominator was a **record** count, so the
script printed **188.2%** — over 100%, which cannot be a rounding artefact, because a record present in two
partitions is counted twice. **One denominator per claim, and a percentage above 100% is two different counts
in one sentence.**

**Disposition: OPEN — unfinished by the owner's decision, not by omission.**

* **The ref is RETAINED.** `rescue/corpus-bcu211-itemseedgen-run` still holds `6fc3d2b21`, still the sole
  holder, not deleted, and it is the raw material for the regeneration this row defers.
* **The seed is not landed and not deleted.** CB42 measured why; this row keeps the decision open.
* **The regeneration, when it happens, is a fresh run against current generator inputs** — never this diff
  and never a merge of it. `gk-forge/tools/seedsmith` is intact at HEAD and nothing in the ref is a prerequisite.
* **Re-review trigger:** an owner ruling to discard, or a fresh run reaching the 67 open partitions. What
  would *change* the verdict is a regenerated corpus that **reduces** the 87 and adds **no**
  `SemanticDedup/NearDuplicate` — a 67-target run that does not repeat the 747 is the thing to look for,
  and the check to run is the one in CB42.
### CB44 - 30 of the 31 `gk-core/tests/tools` failures are ONE token in the active stream's fixture, and it
#### retracts my earlier diagnosis of `verify-change.py`

**Owner:** `ps1-ban-manager-20260926` (**active**, 680 paths). Reported here, not fixed here - this
cleanup does not hold those files and the record is live.

**The defect, in full.** `gk-core/tests/tools/test_verify_change.py` builds a temp fixture that must contain the
*real* Python guard and the *real* Python library, because "the pre-check is delegated, not faked". It
defines both:

```python
39: LIB  = REPO / "scripts" / "lib" / "verification_boundaries.py"      # the real Python lib
41: PS_LIB = REPO / "scripts" / "lib" / "VerificationBoundaries.ps1"    # the PowerShell twin
```

and then copies **the wrong one** into the Python name:

```python
583: shutil.copy2(PS_LIB, self.root / "scripts" / "lib" / "verification_boundaries.py")
584: shutil.copy2(PS_LIB, self.root / "scripts" / "lib" / "VerificationBoundaries.ps1")
```

So the fixture's `verification_boundaries.py` is **PowerShell source saved under a `.py` name**, and the
integrity pre-check dies on import. The comment immediately above it shows the intent -
*"Copying the PowerShell pair left a fixture whose pre-check could not run once the registry row named a
`.py`"* - and the fix that comment describes was attempted with the wrong constant. **The fix is one
token: `PS_LIB` -> `LIB` on line 583.** Line 584 is correct as written.

**The evidence, and it is one shared cause.** `python -m pytest gk-core/tests/tools -q` at `900417172`:
**31 failed, 1,215 passed, 804 subtests passed in 492.79s**. 30 of the 31 are `PlannedFixtureTests` and
**every one carries the identical traceback**:

```
File "...\Temp\vb-fixture-XXXX\scripts\lib\verification_boundaries.py", line 54
    - `dir/**/*.md`    only the Markdown files under `dir/` (unbounded depth) - assistant-config
SyntaxError: invalid character '-' (U+2014)
VERIFY-CHANGE REFUSED [plan]: INTEGRITY-GUARD-FAILED: exit 1 from the verification-boundary guard
```

`ast.parse` on the *real* file is clean - at HEAD (22,664 bytes) and in the working tree - so this is not
a syntax defect in the library; it is the PowerShell text landing where Python expects the library. The
em-dash is merely the first non-ASCII character the parser reached.

**What this retracts.** I earlier reported that `gk-core/scripts/verify-change.py` was "broken by another
stream's port", on the grounds that it calls the Python guard with PowerShell arguments (`-Root` vs
`--root`). **That diagnosis is retracted.** It was read off a failure message rather than out of the code,
and the verified cause is upstream of it: the guard could not be *imported*, so it never parsed an
argument at all. Whether the `-Root`/`--root` mismatch is also real is **unverified either way** - it may
well be a second defect hiding behind the first, and hiding it is this one's practical cost.

**The 31st failure is separate and is the same stream's.** `test_ps1_rename_sweep.py ::
LinkedWorktreesAreNotOurs :: test_a_broad_root_excludes_worktrees_and_reports_the_count` asserts the
tool reports excluding linked worktrees when run with `--root .claude`; it got `[]`. `git worktree list`
in this checkout prints **3** worktrees, so the count is not zero-world - either the tool's worktree
enumeration misses them or the test's premise no longer holds. Not investigated: not this cleanup's file.

**Standing rule this adds:** *a traceback that names a file in a temp fixture is a statement about the
fixture's construction, not about the file it names.* Read the copy step before reading the copied file.
Corollary, and the one that cost this row: **a diagnosis quoted off an error message is a hypothesis** -
and a repo that files findings has to retract the hypothesis when a later read contradicts it, in the
same place it was asserted.
