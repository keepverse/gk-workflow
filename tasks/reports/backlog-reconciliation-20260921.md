# Backlog reconciliation — the truth before the metric

**Lane:** `recon-1` · **Session:** `backlog-recon-20260921` · **Program:** cross-program (measurement)
**Measured tree:** the **live** checkout `features/mega-merge` @ **`65b31d41f`** (2026-09-21T23:40+07),
merged into this lane's branch before finishing (per the orchestrator). Measured once at `614fd2abf`,
then re-run after the merge: `tasks/*todo*.md` is byte-identical across the two (`git diff
614fd2abf..65b31d41f -- 'tasks/*todo*.md'` → empty), and the two rows that changed tick state
(`TVB6.1`, `EP4.x`) are recorded in §5.1. The tree advanced **four** times while this lane ran
(`39029506f` → `85f205a79` → `27728f9e7` → `614fd2abf` → `65b31d41f`); every number below is pinned to
`65b31d41f` and recomputable from §10. **Not** this lane's worktree base `39029506f160`, which was 4
todo files behind — see §8.9, it is itself a finding.
**Fence:** this report only. No todo, doc, script or source file was edited.

## Verdict in one paragraph

A `- [ ]` line is not a unit of work. Across the 118 `tasks/*todo.md` files the live tree holds
**2,158 unticked `- [ ]` lines**, but **858 open task blocks** — and **1,018 of those 2,158 lines
(47%) sit inside blocks the same file already declares closed**. Seven files carry a machine-readable
`closed by the header above` banner, one (`species-gear-chain`) an explicit "boxes are the original
contract" clause, and one (`item-todo`) ticks with `✅`/`⭐` headings whose sub-boxes are never
re-ticked; the ten files involved hold **1,018 of the 2,158 unticked lines**. The manager's
`524 open / 967 done` headline **does not reproduce** under any of 13 candidate definitions (§2.2)
and its provenance is not recorded anywhere I could read. The repairable move is not to discount
boxes; it is to count **task blocks**, and to print the box count beside it labelled non-indicative —
the 858/2,705 pair below.

---

## 1. Method — what a "task" is, per file

The files do **not** share a row shape. Assuming one shape is how this was got wrong three times. I
read each file and classified it against six observed shapes; the shape and its marker are printed
per file in §3.

| # | shape | marker (regex) | tick source |
|---|---|---|---|
| S1 | **heading task** | `^#{2,6}\s+.*\bTask\b\s+<id>` | heading emoji (`✅`/`⭐`/`⛔`) → else the block body |
| S2 | **ID heading** | `^#{2,6}\s+<ID>[:.—-]` (`P7.3`, `D1.1`, `J9-B1`, `W19` …) | heading marker → else block body |
| S3 | **bold checkbox row** | `^- \[[ xX]\] \*\*<id>` at column 0 | the checkbox itself |
| S4 | **plain checkbox row** | `^- \[[ xX]\] ` at column 0, no heading tasks | the checkbox itself |
| S5 | **bracket heading** | `^#{2,6} \[[ xX]\] <id>` (only `trade-network`) | the bracket |
| S6 | **checkbox inside the heading** | `^#{2,6} - \[[ xX]\] <id>` (only `derived-stats`) | the bracket |
| — | **no reliable marker** | — | reported as `NONE`, count not invented |

**Block rule** (S1/S2). A task's block runs from its heading to the next heading of the same or
higher level. Within that block, in this order:
1. heading carries a positive marker (`✅ ⭐ 🔶 DONE CLOSED BUILT SHIPPED`) or a negative declaration
   (`⛔ EXCLUDED SUPERSEDED BLOCKED GENUINELY OWNER-ONLY`), or the **file header** carries
   `closed by the header above` → **done** (a declared-excluded row is not queued work);
2. else the body carries a closure phrase (`closed … by pointer`, `**Done <date>**`, `CLOSED <date>`)
   → **done** — this is checked **before** the boxes, because `battle-derived-wire` Task 0 is
   `Closed 2026-09-20 by pointer` while its acceptance boxes stay `- [ ]`;
3. else the block contains a column-0 `- [ ]` → **open**;
4. else the block contains `- [x]` → **done**;
5. else → **open**, flagged `(prose-only)` (a description-only block with no closure note is an
   unstarted task, which is what `combat-math-dedup`'s Tasks 9–18 are).

Step 2's ordering is load-bearing: checking the boxes first moved 68 blocks (858 → 790 in one run of the
same classifier) and would have reported `battle-derived-wire` as 19 open instead of 14.

Overrides are listed per file in §3's notes column where the rule needed a hand decision
(`achievement-title`'s banner covers Task 1–7a only; `game-gui`'s five ⛔ rows; `derived-stats`'s S6).

**Deliberately not used:** a single repo-wide regex. §2.2 shows what that produces.

---

## 2. The numbers

### 2.1 Headline

```
$ python - <<'PY'   # counts over tasks/*todo*.md on features/mega-merge @ 65b31d41f (see §10 cmd 2)
unchecked=2158 checked=6123 shaded-union=1018 (47%)
```

| reading | value | what it is |
|---|---:|---|
| open **task blocks** | **858** | the work count, per §1 |
| done task blocks | 2,705 | blocks whose own vocabulary says closed |
| unticked `- [ ]` lines | 2,158 | **non-indicative** — 47% are inside closed blocks |
| checked `- [x]` lines | 6,123 | also non-indicative (one task can tick 10 sub-boxes) |

### 2.2 The manager's metric does not reproduce

The manager's brief cites **524 open / 967 done**. I could not reproduce either number, and no file in
`tasks/sessions/`, `tasks/reports/` or `.claude/cmdc-agents/briefs/` contains both numbers, so the
definition is unrecorded. Thirteen candidate definitions on the live tree:

| definition | open | done |
|---|---:|---:|
| all indented `- [ ]` lines | 2,158 | 6,123 |
| column-0 `- [ ]` lines | 2,136 | 5,600 |
| any-indent `- [ ] **` rows | 592 | 2,451 |
| column-0 `- [ ] **` rows | 590 | 2,414 |
| `- [ ] **` starting with a letter | 572 | 2,177 |
| `- [ ]` followed by a capital/digit | 951 | 2,389 |
| column-0 `- [ ]` + capital | 934 | 2,061 |
| `- [ ] **<1-4 letters><digit>` (a task id) | 446 | 1,631 |
| **manager's brief** | **524** | **967** |

Nearest candidates are 590/2,414 and 572/2,177. **Neither 524 nor 967 matches anything I can
compute**, and 967 is far below every "done" reading on the live tree. Treat the brief's pair as
unverified — the decisions it was about to drive (lane count, program split) should use §2.1 instead.

### 2.3 What is shaded (the clause's footprint)

Shaded = unticked lines inside a banner-closed file **or** a positively-marked heading block, counted
once (union, so a banner file's `✅` headings are not double-counted).

| file | unticked lines | shaded (union) | why |
|---|---:|---:|---|
| `tasks/species-gear-chain-todo.md` | 286 | **240** | 41 `✅ Task` headings; contract clause `:16-17` |
| `tasks/story-scene-todo.md` | 261 | **261** | banner `:8` (T1–T26) |
| `tasks/rift-gate-todo.md` | 134 | **134** | banner `:9` (13 tasks) |
| `tasks/onboarding-rift-todo.md` | 110 | **110** | banner `:30` |
| `tasks/item-todo.md` | 137 | **109** | `⭐`/`✅` `P#.#` headings |
| `tasks/debug-mcp-todo.md` | 61 | **61** | banner `:12` (10 tasks) |
| `tasks/achievement-title-todo.md` | 40 | **40** | banner `:3` (Task 1–7a) |
| `tasks/game-control-todo.md` | 31 | **31** | banner `:14` |
| `tasks/live-probe-screenshot-todo.md` | 22 | **22** | banner `:11` |
| `tasks/passive-tree-todo.md` | 36 | **10** | `✅`/`⭐` headings |
| **shaded total** | **1,018 of 2,158 (47%)** | | 9 files + 1 banner-only file |

---

## 3. Per program — true remaining work

Counts are open/done **task blocks**. The unticked-line column is printed beside each row and is
**NON-INDICATIVE**; do not read it as work. `NONE` means the file has no reliable task marker and I
refused to invent a count (the two tables and the checkbox-in-heading file are still measurable — see
their notes).

| file | shape / method | open | done | unticked `- [ ]` **NON-INDICATIVE** | notes |
|---|---|---:|---:|---:|---|
| `tasks/achievement-title-todo.md` | S1 heading task + block rule | 3 | 8 | 40 | open: Task 1: Registry grammars + tuning | Task 2: Evaluator Cold worker + un | Task 3: Bundle client wiring + fan |
| `tasks/action-corpus-todo.md` | S3 bold checkbox row | 0 | 10 | 0 |  |
| `tasks/action-distribution-gaps-todo.md` | S3 bold checkbox row | 7 | 23 | 12 |  |
| `tasks/action-enrich-todo.md` | S3 bold checkbox row | 0 | 10 | 0 |  |
| `tasks/action-skill-tiers-todo.md` | S3 bold checkbox row | 0 | 24 | 0 |  |
| `tasks/action-todo.md` | S3 bold checkbox row | 3 | 111 | 12 |  |
| `tasks/actor-hub-and-combat-power-solid-fixing-todo.md` | S1 heading task + block rule | 0 | 23 | 1 |  |
| `tasks/actor-hub-enforcement-todo.md` | S4 plain checkbox row | 2 | 21 | 2 |  |
| `tasks/actor-hud-todo.md` | S2 ID heading + block rule | 0 | 1 | 10 |  |
| `tasks/actor-sheet-derived-todo.md` | S4 plain checkbox row | 0 | 6 | 0 |  |
| `tasks/actor-sheet-shell-todo.md` | S4 plain checkbox row | 0 | 5 | 0 |  |
| `tasks/actor-sheet-todo.md` | S4 plain checkbox row | 3 | 12 | 3 |  |
| `tasks/almanac-todo.md` | S3 bold checkbox row | 0 | 8 | 0 |  |
| `tasks/aptitude-sheet-todo.md` | S3 bold checkbox row | 0 | 17 | 5 |  |
| `tasks/atom-family-expansion-todo.md` | S1 heading task + block rule | 0 | 9 | 0 |  |
| `tasks/aura-skill-todo.md` | S3 bold checkbox row | 2 | 31 | 2 |  |
| `tasks/backlog-clean-up-todo.md` | S3 bold checkbox row | 5 | 63 | 6 |  |
| `tasks/backlog-clear-todo.md` | S3 bold checkbox row | 1 | 24 | 13 |  |
| `tasks/base-defense-todo.md` | S3 bold checkbox row | 14 | 158 | 14 |  |
| `tasks/battle-derived-wire-todo.md` | S1 heading task + block rule | 14 | 5 | 104 | open: Task 2 — Supply `ActorResolve` and | Task 3 — Make `resource.restore.hp | Task 4 — Give `BattleActorSetup.Ac | Task 5 — Give `Host.AddDerivedCont | Task 6 — Close the status-sourced  |
| `tasks/battle-tempo-todo.md` | S3 bold checkbox row | 0 | 33 | 0 |  |
| `tasks/battle-timeline-todo.md` | S3 bold checkbox row | 0 | 48 | 0 |  |
| `tasks/battle-wire-remainder-todo.md` | S3 bold checkbox row | 13 | 0 | 16 |  |
| `tasks/buff-debuff-scope-todo.md` | S3 bold checkbox row | 4 | 14 | 4 |  |
| `tasks/build-preset-todo.md` | S3 bold checkbox row | 21 | 11 | 27 |  |
| `tasks/class-system-todo.md` | S3 bold checkbox row | 6 | 60 | 9 |  |
| `tasks/combat-ai-todo.md` | S3 bold checkbox row | 24 | 26 | 35 |  |
| `tasks/combat-math-dedup-todo.md` | S1 heading task + block rule | 12 | 6 | 56 | open: Task 5: CombatSim gets a verificat | Task 7: CombatSim's status model c | Task 8: Pool regen has one impleme | Task 9: `UiPresentTagValues` deriv (prose-only) | Task 10: Area shapes declared once (prose-only) |
| `tasks/combat-unification-todo.md` | S3 bold checkbox row | 1 | 27 | 2 |  |
| `tasks/commander-surface-todo.md` | S3 bold checkbox row | 0 | 3 | 1 |  |
| `tasks/commit-mcp-todo.md` | S4 plain checkbox row | 0 | 9 | 0 |  |
| `tasks/condition-glance-todo.md` | S3 bold checkbox row | 1 | 15 | 2 |  |
| `tasks/content-stack-todo.md` | S3 bold checkbox row | 1 | 48 | 1 |  |
| `tasks/creative-mode-followups-todo.md` | S4 plain checkbox row | 0 | 4 | 0 |  |
| `tasks/creature-corpus-self-heal-todo.md` | S3 bold checkbox row | 0 | 25 | 0 |  |
| `tasks/creature-lawn-deploy-todo.md` | S2 ID heading + block rule | 1 | 17 | 10 | open: T4.4 — Conformance and regression  |
| `tasks/creature-progression-todo.md` | S2 ID heading + block rule | 0 | 7 | 11 |  |
| `tasks/creature-seed-todo.md` | S3 bold checkbox row | 4 | 5 | 30 |  |
| `tasks/creature-standalone-todo.md` | S3 bold checkbox row | 0 | 9 | 1 |  |
| `tasks/data-test-substrate-todo.md` | S3 bold checkbox row | 3 | 45 | 3 |  |
| `tasks/debug-mcp-todo.md` | S1 heading task + block rule | 0 | 10 | 61 |  |
| `tasks/deployment-hierarchy-todo.md` | S3 bold checkbox row | 10 | 0 | 14 |  |
| `tasks/derived-cook-todo.md` | S3 bold checkbox row | 1 | 11 | 2 |  |
| `tasks/derived-stats-todo.md` | S6 checkbox in heading | 0 | 28 | 0 |  |
| `tasks/drop-tables-todo.md` | S1 heading task + block rule | 0 | 8 | 0 |  |
| `tasks/effect-atom-todo.md` | S3 bold checkbox row | 2 | 27 | 2 |  |
| `tasks/effect-pipeline-todo.md` | S3 bold checkbox row | 6 | 0 | 10 |  |
| `tasks/empire-development-todo.md` | S4 plain checkbox row | 11 | 64 | 11 |  |
| `tasks/empire-progression-todo.md` | S3 bold checkbox row | 10 | 59 | 22 |  |
| `tasks/fe-essentials-todo.md` | S3 bold checkbox row | 0 | 18 | 0 |  |
| `tasks/first-session-progression-todo.md` | S1 heading task + block rule | 1 | 14 | 6 | open: Task 15: full regression and close |
| `tasks/game-control-todo.md` | S1 heading task + block rule | 5 | 0 | 31 | open: Task 1: `ControlInspect` + `debug. | Task 2: `ControlRefs` + `ControlCl | Task 3: `Win32Input` + `debug.curs | Task 4: `ControlAct` place/shovel/ | Task 5: Distinguished MCP adapters |
| `tasks/game-gui-todo.md` | S1 heading task + block rule | 2 | 28 | 6 | open: Task 5: Shared fixtures from the s | Task 13: Code splitting and budget |
| `tasks/gui-lego-condition-todo.md` | S4 plain checkbox row | 0 | 13 | 0 |  |
| `tasks/gui-lego-todo.md` | S4 plain checkbox row | 1 | 26 | 1 |  |
| `tasks/identity-rename-todo.md` | S3 bold checkbox row | 19 | 0 | 34 |  |
| `tasks/injector-stub-todo.md` | S4 plain checkbox row | 1 | 4 | 1 |  |
| `tasks/ip-censor-todo.md` | S3 bold checkbox row | 25 | 0 | 46 |  |
| `tasks/item-content-todo.md` | S3 bold checkbox row | 0 | 15 | 0 |  |
| `tasks/item-seedgen-todo.md` | S3 bold checkbox row | 1 | 53 | 1 |  |
| `tasks/item-todo.md` | S2 ID heading + block rule | 10 | 38 | 137 | open: P0.2 — seedsmith: `theme-refresh`  | P0.4 — seedsmith: `X1 frame-classi | P0.2 — `theme-refresh` (prose-only) | P0.3 — `theme-enrich` (prose-only) | P0.4 — `X1 frame-classify` (prose-only) |
| `tasks/keepverse-split-todo.md` | S3 bold checkbox row | 16 | 22 | 16 |  |
| `tasks/lawn-combat-wire-todo.md` | S1 heading task + block rule | 1 | 15 | 4 | open: Task splits — [audit] two tasks ex (prose-only) |
| `tasks/lawn-interactive-todo.md` | S4 plain checkbox row | 1 | 19 | 1 |  |
| `tasks/lawn-todo.md` | S3 bold checkbox row | 17 | 0 | 24 |  |
| `tasks/live-probe-screenshot-todo.md` | S1 heading task + block rule | 3 | 1 | 22 | open: Task 1: Arm in Drain + end-of-fram | Task 2: Upload + `POST/GET` + file | Task 3: Latest-frame panel in the  |
| `tasks/live-probe-todo.md` | S1 heading task + block rule | 0 | 12 | 1 |  |
| `tasks/live-setup-skip-todo.md` | S4 plain checkbox row | 0 | 7 | 0 |  |
| `tasks/loam-todo.md` | S3 bold checkbox row | 8 | 55 | 15 |  |
| `tasks/narrative-seed-todo.md` | S3 bold checkbox row | 73 | 0 | 93 |  |
| `tasks/notification-ssot-todo.md` | S3 bold checkbox row | 5 | 63 | 9 |  |
| `tasks/npc-story-events-todo.md` | S3 bold checkbox row | 101 | 0 | 111 |  |
| `tasks/onboarding-rift-todo.md` | S1 heading task + block rule | 0 | 26 | 110 |  |
| `tasks/overlay-switch-todo.md` | S3 bold checkbox row | 0 | 14 | 0 |  |
| `tasks/party-dungeon-todo.md` | S3 bold checkbox row | 23 | 115 | 23 |  |
| `tasks/passive-tree-repair-todo.md` | S2 ID heading + block rule | 12 | 29 | 24 | open: P6.1: Carry mechanism-class atoms  | P7.1: End-to-end proof — one node  | P8.2: Re-run the distribution cens (prose-only) | P10.1: `affix-power-class` (effect (prose-only) | P10.2: `affix-channel-weights` (ef (prose-only) |
| `tasks/passive-tree-todo.md` | S2 ID heading + block rule | 2 | 82 | 36 | open: J10: The full census | J13: Regenerate the 42 shared tree |
| `tasks/phaser-kernel-todo.md` | S3 bold checkbox row | 0 | 19 | 0 |  |
| `tasks/phaser-scene-poc-todo.md` | S4 plain checkbox row | 1 | 6 | 1 |  |
| `tasks/player-guide-todo.md` | **NONE** | 0 | 0 | 0 | no reliable task marker — not counted |
| `tasks/power-todo.md` | S3 bold checkbox row | 1 | 32 | 1 |  |
| `tasks/rift-gate-todo.md` | S1 heading task + block rule | 13 | 0 | 134 | open: Task 1: 3.9 interop verification — | Task 2: Presence signal — closed e | Task 3: Presence semantics tests + | Task 4: Attach a uGUI affordance + | Task 5: Gap 6 — the injector-host  |
| `tasks/roster-balance-todo.md` | S3 bold checkbox row | 0 | 11 | 0 |  |
| `tasks/scope-side-wide-todo.md` | S3 bold checkbox row | 1 | 3 | 1 |  |
| `tasks/seed-to-concrete-todo.md` | S3 bold checkbox row | 0 | 67 | 0 |  |
| `tasks/seedsmith-cli-ux-todo.md` | S4 plain checkbox row | 0 | 28 | 0 |  |
| `tasks/seedsmith-content-standard-todo.md` | S1 heading task + block rule | 0 | 19 | 0 |  |
| `tasks/seedsmith-generated-seed-repair-todo.md` | S3 bold checkbox row | 0 | 5 | 3 |  |
| `tasks/seedsmith-todo.md` | S3 bold checkbox row | 1 | 57 | 1 |  |
| `tasks/shield-sheet-todo.md` | S3 bold checkbox row | 2 | 10 | 3 |  |
| `tasks/shield-todo.md` | S3 bold checkbox row | 1 | 16 | 1 |  |
| `tasks/solid-enforcement-todo.md` | S3 bold checkbox row | 24 | 61 | 41 |  |
| `tasks/solid-remediation-todo.md` | S3 bold checkbox row | 1 | 67 | 1 |  |
| `tasks/species-build-todo.md` | S3 bold checkbox row | 0 | 39 | 1 |  |
| `tasks/species-gear-chain-todo.md` | S1 heading task + block rule | 6 | 60 | 286 | open: Task T37: `item-upgrade-tree` a —  | Task T57: tuning tooling — `publis | Task T55: verification-boundaries  | Task T58: `setClass`'s RUNTIME con (prose-only) | Task T59: routed register — nine m (prose-only) |
| `tasks/species-progression-todo.md` | S3 bold checkbox row | 9 | 34 | 12 |  |
| `tasks/status-rail-todo.md` | S4 plain checkbox row | 0 | 28 | 0 |  |
| `tasks/story-scene-todo.md` | S1 heading task + block rule | 24 | 3 | 261 | open: Task 1: Fix the four shared-kit re | Task 2: Number homes (`scene-tunab | Task 3: `DialogShell` `size` contr | Task 4: Band compliance (this prog | Task 5: Piece contract, group regi |
| `tasks/strain-splice-host-todo.md` | S3 bold checkbox row | 22 | 49 | 44 |  |
| `tasks/summoner-convergence-todo.md` | S3 bold checkbox row | 1 | 2 | 6 |  |
| `tasks/test-verification-boundary-todo.md` | S3 bold checkbox row | 35 | 49 | 43 |  |
| `tasks/todo.md` | S3 bold checkbox row | 0 | 11 | 1 |  |
| `tasks/trade-network-todo.md` | S2 ID heading + block rule | 199 | 0 | 4 | open: [ ] ES2.1 `call-budget-dry-run` —  (prose-only) | [ ] ES2.2 `decision-45-revision` — (prose-only) | [ ] ES3.1 `world-namer` — identity (prose-only) | [ ] ES4.1 `legion-seed-contract` — (prose-only) | [ ] ES5.1 `legion-bands` — legion  (prose-only) |
| `tasks/verification-boundaries-todo.md` | S4 plain checkbox row | 4 | 5 | 4 |  |
| `tasks/vfx-identity-batch1-drip-todo.md` | S3 bold checkbox row | 0 | 4 | 0 |  |
| `tasks/vfx-identity-batch2-crackle-todo.md` | S3 bold checkbox row | 0 | 4 | 0 |  |
| `tasks/vfx-identity-batch3-orbit-todo.md` | S3 bold checkbox row | 0 | 4 | 0 |  |
| `tasks/vfx-identity-batch4-apply-todo.md` | S3 bold checkbox row | 0 | 4 | 0 |  |
| `tasks/vfx-identity-batch45-audit-todo.md` | S3 bold checkbox row | 0 | 6 | 0 |  |
| `tasks/vfx-identity-batch5-pulsering-todo.md` | S3 bold checkbox row | 0 | 4 | 0 |  |
| `tasks/vfx-identity-batch6-live-todo.md` | S4 plain checkbox row | 0 | 9 | 0 |  |
| `tasks/vfx-v2-todo.md` | S3 bold checkbox row | 0 | 8 | 0 |  |
| `tasks/vfx-v3-todo.md` | S3 bold checkbox row | 0 | 11 | 0 |  |
| `tasks/world-map-gaps-followup-todo.md` | **NONE** | 0 | 0 | 0 | no reliable task marker — not counted |
| `tasks/world-map-runtime-gaps-todo.md` | S2 ID heading + block rule | 0 | 16 | 0 |  |
| `tasks/world-map-runtime-todo.md` | S2 ID heading + block rule | 0 | 17 | 0 |  |
| `tasks/world-map-todo.md` | S3 bold checkbox row | 0 | 80 | 0 |  |
| `tasks/world-stage-todo.md` | S1 heading task + block rule | 1 | 0 | 3 | open: Task numbering (prose-only) |
| **TOTAL (118 files)** | | **858** | **2705** | **2158** | |

---

## 4. How far the "boxes are the original contract" clause spreads

**Answer: 7 files carry a machine-readable banner, 1 an explicit contract clause, 1 a per-row note,
36 tick as work lands, and 68 are mixed.** The banner convention already exists and is already read
by `gk-core/scripts/audit-program-pipeline.py` (`RECONCILED_BANNER_RE`, line 99) — so this is **repairable by
using the existing convention**, not by inventing one.

### 4.1 Banner files — quote with `file:line`

| file:line | header text (quoted) | unticked lines it closes |
|---|---|---:|
| `tasks/story-scene-todo.md:8` | `**All boxes below are closed by the header above**, per the HANDOFF section at the bottom of this file … "T1–T26 done and committed; T27 assessed"` | 261 |
| `tasks/rift-gate-todo.md:9` | `**All boxes below are closed by the header above** (verified 2026-09-20, backlog-clean-up `paperwork-reconcile` P1: commits ea4d58a74..273faaabe …)` | 134 |
| `tasks/onboarding-rift-todo.md:30` | `**All boxes below are closed by the header above** (verified 2026-09-20 …) … Per this program's own rule 4, the 110 boxes stay unticked individually; this line is the pointer `pipeline-audit-v2` reads.` | 110 |
| `tasks/debug-mcp-todo.md:12` | `**All boxes below are closed by the header above** (verified 2026-09-20 …) … the 60 sub-boxes stay unticked individually` | 61 |
| `tasks/game-control-todo.md:14` | `**All boxes below are closed by the header above** (verified 2026-09-20 …) … the 31 boxes stay unticked individually` | 31 |
| `tasks/live-probe-screenshot-todo.md:11` | `**All boxes below are closed by the header above.**` (trailing `.` inside the bold) | 22 |
| `tasks/achievement-title-todo.md:3` | `**All Task 1–7a boxes below are closed by the header above** … T7b-Hall-fold/-mount, T7b-actor-fold/-mount stay genuinely open` | 36 of 40 |

`RECONCILED_BANNER_RE = re.compile(r"closed by the header above", re.IGNORECASE)` (`gk-core/scripts/audit-program-pipeline.py:99`)
matches all seven, including the two wording variants above. **No finding** — I checked this
specifically because the two variants look like a regex gap; they are not.

### 4.2 The contract clause and the per-row note

- `tasks/species-gear-chain-todo.md:16-17` — *"A ticked task's acceptance boxes are its original
  contract; the commit's own verification is the evidence, and they were not re-run one by one in
  this planning pass."* This is the **weakest form**: no banner phrase, so `pipeline-audit-v2` cannot
  see it. Consequence: 240 of its 286 unticked lines (84%).
- `tasks/creature-seed-todo.md:132-133` — a one-off per-row note: *"this box was just never re-ticked
  to match."* Not a clause; listed for completeness.

### 4.3 A third, undocumented variant: the phase-level closing banner

`tasks/loam-todo.md:1361` closes a *phase* mid-file:

> `> **⛔ CLOSED — SUPERSEDED, 2026-09-03. Do not start L44–L50; this phase is not coming back.**`

Seven rows (`L44`–`L50`, from `:1375`) stay `- [ ]`, and the commit that acted on it
(`2a5d4912c backlog-clear LO0: loam Phase 6 (L44-L50) is stale, close without building`) is on HEAD.
`pipeline-audit-v2` scans only the **first 15 lines** for a banner, so this one is invisible to it —
`loam` is one of the 24 rows its `todo-header-vs-boxes` kind currently reports, i.e. the audit calls
this a defect where the file's own banner says it is closed. See §7.

### 4.4 Files that tick as work lands (the good shape)

36 files have **0 unticked lines and >0 ticked**: `action-corpus`, `action-enrich`,
`action-skill-tiers`, `actor-sheet-derived`, `actor-sheet-shell`, `almanac`, `atom-family-expansion`,
`battle-tempo`, `battle-timeline`, `commit-mcp`, `creative-mode-followups`,
`creature-corpus-self-heal`, `drop-tables`, `fe-essentials`, … (full list from the §10 command).
68 are mixed (both ticked and unticked lines, mostly a checkbox task row plus unticked
acceptance prose). 11 are all-open (new, unstarted programs: `narrative-seed`, `npc-story-events`,
`trade-network`, `ip-censor`, `lawn`, …). 3 have no checkboxes at all.

---

## 5. Spot-check — tick state against the tree

Commands used, per id: `git log --oneline HEAD --grep='(^|[^A-Za-z0-9])<id>([^0-9A-Za-z]|$)' -E`
(word-boundary), `ls tasks/evidence-fragments/<id>.md`, and a read of the named row. Ten programs,
≥3 ticked and ≥3 open each.

| program | ticked rows checked | tree agrees? | open rows checked | tree agrees? |
|---|---|---|---|---|
| `species-gear-chain` | T1, T28, T53, T54, T61 | **yes** — fragments `T28.md T53.md T54.md` present; `7e9cb327e` = "T61 (half B) … closes" | T37, T55, T57 | yes — T37's block carries 12 `- [ ]` / 0 `- [x]`; T55/T57 commits only *file* the row |
| `story-scene` | T1–T26 (banner-declared) | **yes** — `tasks/evidence-fragments/T22..T27.md` present; `gk-web/web/fusion-rpg-web/src/features/story-scene/{actorCast.ts,foldStorySceneVm.ts}` exist; `f384b3809` = PR #7 merge on HEAD | T27, T27b | yes — T27's fragment exists but the banner says only "assessed"; T27b stays open in `backlog-clean-up` BCU7.6 |
| `test-verification-boundary` | TVB0.1, TVB1.1, TVB1.2 | **yes** — merged, files named by the rows exist | TVB6.1, TVB6.2, TVB4.7 | TVB6.1 now **ticked** (see 5.1 #3); TVB6.2 open with its residue documented at `:803` |
| `item-todo` | P1.2-L, P1.4-E, P1.5-B (`⭐`) | yes (no contradicting evidence) | P7.3–P7.7 | yes — `bf0b9d4ec` only routes them to BCU6.1 to be *planned* |
| `solid-enforcement` | SE0.1, SE0.2 | yes — `gk-core/scripts/enforcement-registry.v1.json` exists | SE4.30, SE4.31 | **no** — see 5.1 |
| `combat-ai` | CAI1.1, CAI1.12 | yes — spec-doc commits `8028b9833`, `a9c4a81d6` | CAI2.2, CAI3.1 | yes — commits are "CAI2.1 closed" / overview fixes, not landings |
| `passive-tree` | J9-B1 (ticked in the live tree) | yes | J10, J13 | yes — `222f9133d`-class commits are on the unmerged/partial path; rows marked as such |
| `base-defense` | V1, 18.3 | yes — evidence lines on the rows | 21.3 | yes — 0 commits on HEAD; row marked "⛔ PAUSED" |
| `party-dungeon` | D1.1, D1.2 | yes — the nine registry JSONs exist | D3.3, D3.5 | yes — rows read "PARTIALLY BUILT" |
| `empire-progression` | EP4.9–EP4.12 (ticked in the live tree) | **yes** — `9fafe01a4 feat(EP4.9)` etc. are on HEAD; the rows are `- [x]` **on the live tree** | EP4.13 | yes — `feat(EP4.13, partial)` and the row stays open |
| `narrative-seed`, `npc-story-events`, `trade-network` | *none exist* — 0 ticked rows | n/a | sampled | yes — the `NS5`/`NS6` grep hits are **notification-ssot** ids (`NS5.6`, `NS6.4`), a prefix collision, not this program |

Anti-pattern found while checking: a mechanical "does the ticked row's named path exist" sweep is
**not usable** — most rows cite bare basenames (`Program.cs`, `derive.py`), and at least one ticked
row (`backlog-clean-up-todo.md:603` BCU7.1) legitimately cites a file that task **deleted**. That
sweep produced 221 false positives out of 289 rows; do not build a guard on it (§8).

### 5.1 Disagreements between a tick and the tree

1. **`solid-enforcement` SE4.30** — `tasks/solid-enforcement-todo.md:568` is `- [ ] **SE4.30 …**`,
   but `8aba2900f ruling(convergence): SE4.30 closes on the migration probe, by owner decision` is on
   HEAD and its body says *"Closes the row the audit kept open … the two clauses that were not met
   are recorded on the row rather than dropped."* **A ruling closed the row; the row is still
   unticked.** Owning program: `solid-enforcement`.
2. **`loam` L44–L50** — `tasks/loam-todo.md:1361`'s banner closes the phase as SUPERSEDED and
   `2a5d4912c backlog-clear LO0` executed the closure, but seven rows at `:1375+` stay `- [ ]`.
   Owning program: `loam`.
3. **`test-verification-boundary` TVB6.1/TVB6.2 — RESOLVED by the merge, no longer a disagreement.**
   At `614fd2abf` both rows were `- [ ]` while `222f9133d feat(tvb): TVB6.1 …` was on HEAD. At
   `65b31d41f` `tasks/test-verification-boundary-todo.md:274` reads `- [x]`; only `:279` (TVB6.2)
   stays open, and its one matching commit `21717632d fix(tvb): TVB-F18` repairs TVB6.1's analyzer
   rather than landing TVB6.2's per-area owners (`:803` TVB-F17 documents the residue). Recorded
   because the tick lagged a merged lane for one commit — a real, if self-correcting, pattern.
4. **`onboarding-rift` internal contradiction** — `:30`'s banner closes all 110 boxes, yet all 26
   task headings read `— OPEN` (e.g. `tasks/onboarding-rift-todo.md:38` `### Task 1: reconcile source
   specs and legacy references — OPEN`) and `:36` lists live residue ("Still open: live
   `scripts/prove-vfx.ps1`, full Data suite in CI, browser accessibility/320px sweep, …"). A reader
   cannot tell from the file which side wins. Owning program: `onboarding-rift`.
5. **`npc-story-events` header vs rows** — `tasks/npc-story-events-todo.md:4` states *"94 tasks
   (NR0.1–NR6.7, NR-LP1, NR-LP2, NRX.1–NRX.3)"*; the file contains **101** open bold-ID rows. The
   seven-row delta is unnamed. Owning program: `npc-story-events`.

No tick was corrected: this lane reports.

---

## 6. The manager's actual load (item 4)

Sources: `.claude/cmdc-agents/registry.jsonl` (1,419 events, 34 lanes lifetime),
`.claude/cmdc-agents/agents/*/status.json` (spot-read: `tvb58`, `isg-gen-fix`, `sgc-1`,
`combat-ai-3`), `.claude/cmdc-agents/acceptance/*.json` (27 artefacts, 13 lanes).

### 6.1 Live lanes and pending merges (as at 2026-09-21T23:45+07)

| lane | last registry event | state | program (per `.claude/cmdc-agents/briefs/<lane>.md`) |
|---|---|---|---|
| `tvb58` | `continued` 22:53:46 | running (`status.json` state=running, pid 37064) | `test-verification-boundary` |
| `isg-gen-fix` | `segment_end` 23:08:30 | mid-lane (between segments) | `item-seedgen` |
| `j9-vote` | `spawned` 23:00:21 | running | `passive-tree` J9 (no brief file yet) |
| `recon-1` | `segment_end` 23:11:13 | this lane (measurement) | — |

**3 live lanes besides this one**, across 3 programs.

```
$ for b in $(git branch --format='%(refname:short)' | grep '^cmdc/'); do
    printf "%-24s ahead=%s\n" "$b" "$(git rev-list --count HEAD..$b)"; done
cmdc/ssh27               ahead=2
cmdc/tvb58               ahead=1
cmdc/tvb59               ahead=2
```

**3 cmdc branches carry unmerged commits**: `cmdc/ssh27` (2), `cmdc/tvb58` (1, live), `cmdc/tvb59`
(2). At 23:03 the same command gave `ssh27=2, tvb59=6` with `ep-3=11→0` and `tvb58=12→0` merging
*inside* the lane — the merge queue turns over faster than a backlog survey can, which is itself an
argument for a cheap, scripted metric over a hand count.

### 6.2 Acceptance turnaround — idle after reaching an actionable state

Measured per acceptance artefact as `acceptance.when − last registry event for that lane before
`when`` (timezone-normalised to +07:00). This is the lane's **idle** time while a decision it could
not make itself was outstanding.

| statistic | minutes (n=29, 23:45) | minutes (n=27, 23:03) |
|---|---:|---:|
| n | 29 | 27 |
| min | 0.3 | 0.3 |
| p50 | **3.2** | 2.9 |
| p75 | 9.3 | 6.5 |
| p90 | 15.1 | 15.1 |
| max | **66.2** | 66.2 |
| mean | 7.7 | 7.8 |

Distribution (n=29): **16 ≤5 min**, **10 in (5, 15]**, **3 >15** — `item-seed-gen` 66.2,
`ssh27` 29.7, `ns-1` 15.1. The long tail is 3 lanes of 14; the median lane waits ~3 minutes.
`ep-3` produced two artefacts four hours apart, the second 0.3 min after its lane stopped —
retest churn, not idling. Two more artefacts (`tvb59`) landed between the two snapshots; the
distribution did not move materially, which is the useful finding: the tail is structural, not noise.

**Limitation, stated:** this is lane idleness, not manager idleness — the manager works several lanes
concurrently, and a lane that was `continued` (resumed) after its last `finished` was not idle at all.
Five of the 29 rows have `continued`/`segment_end` as their last pre-acceptance event and should be
read as an upper bound. On this evidence **a sub-leader for acceptance turnaround is not indicated**:
the median is 2.9 minutes and the queue is already merged ahead of the survey.

---

## 7. Proposed replacement metric (one commit)

**Count:** open **task blocks** per `tasks/<program>-todo.md`, using a declared per-file marker.
**Print beside it:** (a) the file's unticked `- [ ]` line count, suffixed `(not a work count)`;
(b) the **shaded** count — unticked lines inside a banner-closed or positively-marked block.

Design, in the shape it can land:

| what | file | detail |
|---|---|---|
| the counter | `gk-core/scripts/audit-program-pipeline.py` | add kind **`todo-task-blocks`** to the existing v2 audit (do **not** write a second tool — `todo-header-vs-boxes`, `header_claims_complete` and `RECONCILED_BANNER_RE` already live there). Reuse `RECONCILED_BANNER_RE`; print `open=<n> done=<m> boxes=<k> (not a work count) shaded=<s>`. |
| the marker map | `gk-core/scripts/todo-shapes.v1.json` (new) | per file: `{ "shape": "H-task\|H-id\|R-bold\|R-plain\|H-bracket\|H-checkbox-heading\|none", "exemplar": "<one real heading>" }`. A file absent from the map, or with `"shape":"none"`, is reported as **unmeasured**, never defaulted. |
| two real defects to fix in the same commit | `gk-core/scripts/audit-program-pipeline.py` | (i) `header_claims_complete` scans only the file's first `HEADER_SCAN_LINES` (15) lines — `tasks/loam-todo.md:1361`'s phase banner is invisible, so `loam` is a false **defect** today; scan the whole file, or emit a distinct kind `banner-closed-unticked` when an unticked row sits under a closing banner. (ii) `species-gear-chain`'s contract clause (`:16-17`) has no banner phrase, so it is not recognised — recognise the clause or add the banner to that file's header. |
| the guard | `gk-core/tests/tools/test_audit_program_pipeline.py` | fixture-only. Three fixtures: a heading-task file (2 ticked, 1 open → `open=1 done=2`), a banner file (3 unticked, 0 open), a mid-file banner with a row under it. **Assert the behaviour, never a repo population count** — `docs/architecture/validation-ssot.md`. |
| the reading | `tasks/reports/*.md` | this report is the prototype; the manager reads the printed line, the guard pins only the shape. |

**What it cannot prove.** That a tick is *true* (the file is the only witness; §5 samples, it does not
re-run). That an open block is *unfinished* rather than deferred, blocked, superseded or
owner-only — the vocabulary overlaps and is per-file. That the marker map is complete — files with no
reliable marker stay unmeasured by design. That no work exists outside the todo (plans, ideas, filed
findings). And the **size** of any block: `L-run` and `XS` count the same, so this metric measures
*remaining rows*, not remaining effort.

---

## 8. NOT-proved

1. **The manager's `524 / 967`.** Not reproducible under 13 definitions; provenance absent from
   `tasks/sessions/`, `tasks/reports/` and `.claude/cmdc-agents/briefs/`. Reported as unverified.
2. **The manager's own per-program figure for `species-gear-chain`** ("25 task headings, 24 shipped by
   name, 7 open") does not reproduce: the file has **66** task headings, **41** positively marked,
   **25** unmarked — of which **19 are body-ticked** (e.g. T30, T34d) and **6 are open** (T37, T55,
   T57, T58, T59, T60). The brief's three numbers are mutually inconsistent (24+7≠25).
3. **Whether any tick is truthful.** §5 checks 30-odd rows by `git log --grep`/fragment/file. A
   ticked task whose commit exists but whose acceptance is false is not detectable this way.
4. **File-existence as evidence.** Abandoned: bare-basename citations make it meaningless, and
   deletion tasks legitimately cite absent paths (BCU7.1). 221/289 "missing" were false positives.
5. **The exact lane→program map for `j9-vote`** — spawned 23:00:21, no brief in
   `.claude/cmdc-agents/briefs/`. Mapped to `passive-tree` J9 from the registry id only.
6. **Whether the manager was idle during the turnaround window** — §6.2 measures lane idleness.
7. **`passive-tree-repair`'s four prose-only blocks** (P8.2, P10.1, P10.2, P10.3) — counted
   separately, left for the owning program to classify.
8. **Any line count inside a generated/derived doc** — only `tasks/*todo.md` was measured; plans and
   maps were not.
9. **This lane's own worktree base is stale.** `39029506f160` is 4 `tasks/*todo.md` files behind the
   live tree (+104 lines: `empire-progression`, `passive-tree`, `strain-splice-host`,
   `test-verification-boundary`). Measuring the worktree produced two **false** EP4.9–EP4.12
   tick-vs-tree "disagreements" (§5), caught only by re-reading the rows in the main checkout. Any
   backlog survey must measure the live tree, or state its base commit in the finding.

---

## 9. Findings owned by other programs (listed, not routed, not fixed)

| # | finding | `file:line` | owning program | cause read |
|---|---|---|---|---|
| F1 | SE4.30 unticked under an owner ruling that closes it | `tasks/solid-enforcement-todo.md:568` | `solid-enforcement` | the ruling landed in `features/mega-merge` as a commit, not as a row edit |
| F2 | phase banner closes L44–L50; the rows stay unticked | `tasks/loam-todo.md:1361` (rows `:1375+`) | `loam` | banner is file-level; the audit scans only the first 15 lines |
| F3 | TVB6.1's tick lagged one commit after its lane merged; TVB6.2 still carries residue | `tasks/test-verification-boundary-todo.md:274` (fixed), `:279` | `test-verification-boundary` | the fix commit `21717632d` repaired TVB6.1's analyzer but did not tick either row |
| F4 | banner closes 110 boxes while all 26 headings read `— OPEN` | `tasks/onboarding-rift-todo.md:30` vs `:38+` | `onboarding-rift` | both a banner and per-heading `OPEN` markers were written; neither was removed |
| F5 | header says 94 tasks; 101 open bold-ID rows exist | `tasks/npc-story-events-todo.md:4` | `npc-story-events` | seven rows (checkpoints/sub-items) are counted in the rows but not the header |
| F6 | contract clause unrecognised by `RECONCILED_BANNER_RE` | `tasks/species-gear-chain-todo.md:16-17` | `species-gear-chain` (metric-adjacent) | the clause has no banner phrase, so 240 unticked lines look open to a box counter |
| F7 | mid-file closing banner invisible to `header_claims_complete` | `gk-core/scripts/audit-program-pipeline.py:232` (`HEADER_SCAN_LINES`) | pipeline tooling | the function scans `text.splitlines()[:HEADER_SCAN_LINES]`; F2 is its consequence |
| F8 | three todos have no checkbox task marker (S6/tables) | `tasks/derived-stats-todo.md`, `tasks/player-guide-todo.md`, `tasks/world-map-gaps-followup-todo.md` | those three programs | shapes never entered a registry; the metric must declare them, not guess |
| F9 | `session-boundary-check.py` false-positives when run **from inside a worktree** | `scripts/session-boundary-check.py:92` (`Test-Path $rec.worktree`) | repo tooling / `docs/contributing/session-boundary.md` | `worktree` is stored repo-root-relative but tested against the current directory, so `…/cmdc-recon-1/.claude/worktrees/cmdc-recon-1` is probed; 7 records report "worktree path … no longer exists" while every one of those paths exists. From the repo root the same run is `clean for 'backlog-recon-20260921'`. |

Per the lane rules these are **not filed as rows** — the manager routes them, and this lane's fence
(`tasks/reports/**`) forbids touching another program's todo.

---

## 10. Evidence — exact commands and what they printed

```bash
# 1. live tree, and that it is clean
cd /d/Works/source/plant-vs-zombie-rise-of-summoner
git rev-parse --short HEAD            # 65b31d41f (after merging features/mega-merge)
git status --porcelain tasks/         # (no output)

# 2. headline: box lines vs shaded box lines
python - <<'PY'
import glob,re
POS=re.compile(r'✅|⭐|🔶|\bDONE\b|\bCLOSED\b|\bBUILT\b|SHIPPED|\(DONE\)|\(CLOSED\)')
BANNER='closed by the header above'
tot=od=shaded=0
for f in sorted(glob.glob('tasks/*todo*.md')):
    L=open(f,encoding='utf-8').read().split('\n')
    o=sum(1 for x in L if re.match(r'^\s*- \[ \]',x)); d=sum(1 for x in L if re.match(r'^\s*- \[[xX]\]',x))
    isb=any(BANNER in x for x in L[:40]); tot+=o; od+=d
    hs=[(i,len(m.group(1)),m.group(2).strip()) for i,l in enumerate(L) for m in [re.match(r'^(#{2,6})\s+(.*)$',l)] if m]
    closed=set(range(len(L))) if isb else set()
    for k,(i,lv,t) in enumerate(hs):
        if not re.match(r'^[^\w]*(Task|T[0-9]|P[0-9]|[A-Z]{1,4}[0-9])',t): continue
        end=len(L)
        for j,lv2,_ in hs[k+1:]:
            if lv2<=lv: end=j;break
        if POS.search(t): closed|=set(range(i+1,end))
    shaded+=sum(1 for i,x in enumerate(L) if i in closed and re.match(r'^\s*- \[ \]',x))
print(f"unchecked={tot} checked={od} shaded-union={shaded} ({shaded*100//tot}%)")
PY
# unchecked=2158 checked=6123 shaded-union=1018 (47%)
#   species-gear-chain 286/240 · story-scene 261/261 · rift-gate 134/134 · onboarding-rift 110/110
#   · item 137/109 · debug-mcp 61/61 · achievement-title 40/40 · game-control 31/31
#   · live-probe-screenshot 22/22 · passive-tree 36/10

# 3. task-block table (§3) — shape classifier + block rule, overrides printed per row
#    (the generator is section 1's rules; TOTAL line printed)
# | **TOTAL (118 files)** | | **858** | **2705** | **2158** | |

# 3b. clause spread (§4.4): files with 0 unticked lines and >0 ticked
python - <<'PY'
import glob,re
c=[f for f in sorted(glob.glob('tasks/*todo*.md'))
   if sum(1 for x in open(f,encoding='utf-8') if re.match(r'^\s*- \[ \]',x))==0
   and sum(1 for x in open(f,encoding='utf-8') if re.match(r'^\s*- \[[xX]\]',x))>0]
print(len(c), [f.split('/')[-1] for f in c])
PY
# 36 files tick as work lands

# 4. banner files and their line numbers
grep -rn -E 'All .*boxes below are closed by the header above' tasks/*todo*.md
# achievement-title:3, debug-mcp:12, game-control:14, live-probe-screenshot:11,
# onboarding-rift:30, rift-gate:9, story-scene:8

# 5. the existing convention in the audit tool
grep -nE 'RECONCILED_BANNER_RE|HEADER_SCAN_LINES' gk-core/scripts/audit-program-pipeline.py
# 99:RECONCILED_BANNER_RE = re.compile(r"closed by the header above", re.IGNORECASE)
python gk-core/scripts/audit-program-pipeline.py --only todo-header-vs-boxes   # 24 open rows (loam among them)

# 6. tick-vs-tree: open rows whose id is a commit subject on HEAD
python - <<'PY'
import glob,re,subprocess
subs=subprocess.run(['git','log','--format=%s','HEAD'],capture_output=True,text=True,encoding='utf-8',errors='replace').stdout.split('\n')
hits=[];checked=0
for f in sorted(glob.glob('tasks/*todo*.md')):
    L=open(f,encoding='utf-8').read().split('\n')
    for i,l in enumerate(L,1):
        m=re.match(r'^- \[ \] \*\*([A-Za-z0-9][A-Za-z0-9.\-]{2,14})\b',l) or re.match(r'^#{2,6} \[ \] ([0-9A-Za-z][0-9A-Za-z.\-]{2,14})\b',l)
        if not m: continue
        ident=m.group(1).strip('.-'); checked+=1
        for s in subs:
            if not re.search(r'(?<![A-Za-z0-9])'+re.escape(ident)+r'(?![0-9A-Za-z])',s): continue
            if re.match(r'^[A-Za-z]+[\(:]\s*'+re.escape(ident)+r'(?![0-9A-Za-z])',s) or re.search(r'[\(\[]'+re.escape(ident)+r'(?![0-9A-Za-z])',s):
                hits.append((f.split('/')[-1],i,ident,s[:88])); break
print(f"checked={checked} named={len(hits)}")
PY
# checked=698 named=35  -> classified by hand into route/partial/blocked (29, legitimate) and
#   the four in §5.1; the rest are prefix collisions (narrative-seed NS5 vs notification-ssot NS5.6)

# 7. disagreements, individually
git merge-base --is-ancestor 8aba2900f HEAD && echo IN-HEAD          # IN-HEAD
grep -n 'SE4.30' tasks/solid-enforcement-todo.md                     # 568:- [ ] **SE4.30 ...
git log -1 --format='%s%n%b' 8aba2900f | head -6                     # "Closes the row the audit kept open"
sed -n '1361p;1375p' tasks/loam-todo.md                              # banner + an unticked L44
git merge-base --is-ancestor 222f9133d HEAD && echo IN-HEAD          # IN-HEAD (TVB6.1)
grep -n 'TVB6.1\|TVB6.2' tasks/test-verification-boundary-todo.md    # 274 "- [x]" (ticked in the merge); 279 "- [ ]"

# 8. manager load
python - <<'PY'   # registry.jsonl: last event per lane
import json
rows=[json.loads(l) for l in open('.claude/cmdc-agents/registry.jsonl',encoding='utf-8')]
last={}; [last.__setitem__(r['id'],r) for r in rows]
term={'finished','merged','abandoned','accepted','closed'}
print([(k,v['event'],v['ts']) for k,v in last.items() if v['event'] not in term])
PY
# [('tvb58','continued',22:53:46), ('isg-gen-fix','segment_end',23:08:30),
#  ('j9-vote','spawned',23:00:21), ('recon-1','segment_end',23:11:13)]
# pending merges (any cmdc/* with HEAD..branch != 0)
for b in $(git branch --format='%(refname:short)' | grep '^cmdc/'); do
  a=$(git rev-list --count HEAD..$b); [ "$a" != 0 ] && printf "%-24s ahead=%s\n" "$b" "$a"; done
# cmdc/ssh27 ahead=2 ; cmdc/tvb58 ahead=1 ; cmdc/tvb59 ahead=2

# 9. acceptance turnaround (acceptance/*.json x registry timestamps)
# n=29  median 3.2 min, p75 9.3, p90 15.1, max 66.2  (distribution: 16 / 10 / 3)
```

---

## 11. Verification of this report

```powershell
# every program file appears in the report
Select-String -Path tasks/reports/backlog-reconciliation-20260921.md -Pattern 'achievement-title-todo.md' -SimpleMatch | Measure-Object
# 1 (plus the §3 table row for every one of the 118 tasks/*todo*.md files)
python scripts/session-boundary-check.py --session backlog-recon-20260921
```

`verify-change.ps1` selects nothing for a markdown-only change, so it was not run (stated rather than
substituted). `session-boundary-check.py` is clean when run from the repo root — run from inside this
worktree it false-positives on its own record (finding F9):

```
$ cd <repo root> && python scripts/session-boundary-check.py --session backlog-recon-20260921
[session-boundary] clean for 'backlog-recon-20260921'   # exit 0
```

**Session record:** `tasks/sessions/backlog-recon-20260921.json` (written by the manager, merged into
this lane's branch before it finished) records the fence as `tasks/reports/**`; this lane wrote exactly
one file inside it. No todo, doc, script, source file or other session's record was touched
(`git status` before committing: one untracked path, the report).
