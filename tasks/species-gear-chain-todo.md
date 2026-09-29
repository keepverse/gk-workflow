# Tasks: `species-gear-chain`

**Plan:** [species-gear-chain-plan.md](species-gear-chain-plan.md) · **Specs:**
`docs/architecture/species-gear-chain/spec-<module-id>.md` · **Map:**
`docs/architecture/species-gear-chain-map.md`

**Revision 2** — see the plan's § Round-2 corrections for what changed and why. Each task cites its
owning spec — read that file's Design/Code style/Testing strategy/Boundaries before starting; this
list gives acceptance criteria, verification and scope, not full design detail.

**Revision 4 (2026-09-18, session `plan-sgc-20260918`)** — amended under the parent
[summoner-convergence-plan.md](summoner-convergence-plan.md) (lane C). What changed:

- **24 tasks ticked as shipped** (T1–T21, T18b, T35, T36), each with its commit hash and one piece of
  code evidence, checked on `HEAD` with `git log --grep "species-gear-chain"` and a read of the named
  file — never on a doc's word. A ticked task's acceptance boxes are its original contract; the
  commit's own verification is the evidence, and they were not re-run one by one in this planning pass.
  Checkpoint boxes are ticked only where this pass checked the evidence line itself.
- **Amended to the strengthened specs:** T23 (materials publish), T24 (bands answered, v3 rule),
  T29 (credit site), T30, T31, T32, T33; **T34 rewritten** for R9 (2/8/0, trophy planner,
  `species-material-run.v1.json`, no general layer, `perGeneral` refused) and split into T34–T34d with
  R22 (per-kill family roll; the species counts in every listed family). **New:** T30b (parametric
  trophy entry), T39–T46 + T49 (`craft-assurance`, the free-ward fix **first**), T47 (creature-seed
  ask 4), T48 (stale comment).
- **No in-place tuning bump.** Every revision is a new `v{n+1}` file from `gk-core/tools/tuning/publish.py`
  (`--add-key` exists for new keys) with the host reader switched **in the same commit** (parent H7).
  Order for shared files is the parent's §5 ledger — see the plan's § Tuning publishes.
- **Numbering is stable:** no existing id was renumbered; new ids are T30b, T34b–T34d, T39–T49.
- **Arm 2 of `socket-combat-wiring` (combination-grant binding) has no task here** — it is
  `SSH combo-bind`'s (strain-splice-host map §6 C15; `spec-socket-combat-wiring.md` § Design 5).

---

## Wave 0 — fix first (live defect), and two small items with no dependencies

#### ✅ Task T39: `craft-assurance` a — the free ward is a live defect: refuse `wardLoaded: true`, delete the checkbox
- [x] **Shipped** — see `tasks/evidence-fragments/T39.md` for the executed rows — `WorkbenchEndpoints.cs` refuses `wardLoaded: true` via `MutationRules.Violated("enhance.ward-flag-retired", …)`; `ItemWorkbench.Enhance` no longer takes a ward and passes `WardLoaded: false`; the FE checkbox, its state and the `items.ts` field are gone. Server `~Workbench` 50 passed; web vitest 17 passed; `npm run build` green.
**Description:** ⛔ **Fix first** (parent lane C's first task). `WorkbenchEndpoints.cs:37` declares
`EnhanceRequest(... bool? WardLoaded)` and `:191` forwards `body.WardLoaded ?? false` into
`ItemWorkbench.Enhance` (`ItemWorkbench.cs:494`, `:506`) — downgrade protection that **nothing
debits**. This task closes it without waiting for the consumable: the endpoint refuses `true` by name
(`enhance.ward-flag-retired`, under the registered `enhance.*` namespace — never a new error code),
accepts and ignores `false`/absent (the shipped FE sends the key on every enhance, usually `false`),
and passes no ward to the policy. The FE checkbox, its test and the `items.ts` field are deleted in the
**same** change (`spec-craft-assurance.md` § Design 3) — leaving it would make the FE's one ward path a
guaranteed 4xx. Paid protection returns in T42, as a debited `assurance.protect` line. Level loss starts
at `+17`, which shipped item levels cannot reach, so removing the free ward costs a player nothing today.

**Acceptance criteria:**
- [ ] `wardLoaded: true` is refused by name with no level change, no debit and no op row;
      `wardLoaded: false` and an absent key are accepted and ignored
- [ ] No request field reaches `EnhanceContext.WardLoaded` any more (it is `false` until T42 derives it
      from debited lines)
- [ ] The ward checkbox, its test cases and the `wardLoaded` field in `items.ts` are gone; the FE build
      and the workbench test pass

**Verification:**
- [ ] `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Server/WorkbenchEndpoints.cs,gk-core/tests/FusionRpg.Server.Tests/ItemWorkbenchEndpointsTests.cs,gk-web/web/fusion-rpg-web/src/layers/relics/Workbench.tsx,gk-web/web/fusion-rpg-web/src/layers/relics/workbench.test.tsx,gk-web/web/fusion-rpg-web/src/lib/bus/items.ts -Session <id>`
- [ ] `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~Workbench"`
- [ ] `cd gk-web/web/fusion-rpg-web; npx vitest run src/layers/relics/workbench.test.tsx; npm run build`

**Dependencies:** None
**Files:** `gk-core/src/FusionRpg.Server/WorkbenchEndpoints.cs`, `gk-core/tests/FusionRpg.Server.Tests/ItemWorkbenchEndpointsTests.cs`, `gk-web/web/fusion-rpg-web/src/layers/relics/Workbench.tsx`, `workbench.test.tsx`,
`gk-web/web/fusion-rpg-web/src/lib/bus/items.ts`
**Size:** S · *(spec: `craft-assurance`)*

---

#### ✅ Task T47: coordinate `creature-seed` ask 4 — the C# `speciesKind: "excluded"` mirror in `CreatureAdmission`
- [x] **Closed** — the ask landed as `creature-seed` **Task 13** (filed by the orchestrator, `5d59f478`) and lane C built it: **CS13 = `be3ac8a6`**. `AnchorRowReader` → `SpeciesExpander` → `ConcreteSpecies` → `CreatureSpeciesDef` → `CreatureAdmission` refuses `excluded` in every context; the twelve rows are now refused (`gk-data/packs/fusion/data/generated/creatures/Pit.json` etc. carry the mark). Evidence: `tasks/evidence-fragments/CS13.md`. No stopgap filter was added in this program — `CreatureAdmission` stays the one declaring site.
**Description:** A coordination task, not a build in this program. `creature-seed-map.md:319` files ask
4: the 12 `speciesKind: "excluded"` rows ship as `Summonable` and `CreatureAdmission.cs:14-24` admits
them in every context; there are zero C# readers of `speciesKind`. `creature-seed`'s todo has **no task
for it** (checked 2026-09-18). The trophy planner (T34) skips excluded species, so until the mirror
lands a kill of one of them would resolve a trophy entry to an absent id and refuse its loot by name
(`spec-species-materials.md` Strengthen pass item 1; `spec-creature-drop-tables.md` Strengthen pass
item 2). **This is the parent's §3 coupling "Excluded-species admission" — soft, not a hard edge.**

**Default shipped behind (no gate):** everything in this program proceeds; only the **trophy draw
groups** (T34c) wait for the mirror, and T34c's acceptance refuses to author them before it exists.
E1/E2/E3a (T29–T31) and every other trophy task are unaffected.

**Acceptance criteria:**
- [ ] A task for ask 4 exists in `tasks/creature-seed-todo.md`, owned by that program's session (this
      task asks for it; it does not write another program's todo)
- [ ] When that task lands, its commit hash is recorded here and T34c's dependency line points at it
- [ ] `CreatureAdmission` stays the one declaring site — no per-roller or per-table excluded filter is
      added in this program as a stopgap

**Verification:**
- [ ] `grep -n "speciesKind" gk-core/src/FusionRpg.Core/Creatures/CreatureAdmission.cs` shows the mirror once
      it lands; `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~CreatureAdmission"`

**Dependencies:** None (cross-program: `creature-seed` ask 4)
**Files:** this todo only (the dependency line on T34c)
**Size:** XS · *(spec: `species-materials`, `creature-drop-tables`)*

---

#### ✅ Task T48: correct the stale "zero production callers" comment in `DelveBattleSessionManager`
- [x] **Shipped** — see `tasks/evidence-fragments/T48.md` — the comment now names `DelveBattleSession` for `DelveBattle.Run` (`DelveBattleSession.cs:192`) and `ResolveRoomEncounter` for `Encounter.Build` (`:178`), with no unre-derivable search claim; comment-only. `verify-change` green (server 553). Spec `:11` propagated.
**Description:** T20 made `DelveBattleSessionManager.ResolveRoomEncounter` the production caller of
`Encounter.Build`, and `DelveBattleSession.cs:179` now calls `DelveBattle.Run` — but the class comment
at `DelveBattleSessionManager.cs:27-28` still says *"zero production callers of `DelveBattle.Run` exist
anywhere today, confirmed by a direct search this session."* `spec-delve-species-wiring.md:11` reports
it as a code-owner fix. Comment-only change.

**Acceptance criteria:**
- [ ] The comment names the real callers (`DelveBattleSession.cs` for `DelveBattle.Run`,
      `ResolveRoomEncounter` for `Encounter.Build`) with no claim a search cannot re-derive
- [ ] No code change in the file

**Verification:**
- [ ] `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Server/DelveBattleSessionManager.cs -Session <id>`

**Dependencies:** None
**Files:** `gk-core/src/FusionRpg.Server/DelveBattleSessionManager.cs`
**Size:** XS · *(spec: `delve-species-wiring`)*

---

## Phase 1 — foundations

### Sub-checkpoint 1a — ladder and tuning fixes

#### ✅ Task T1: `tier-propagation-contract` a — derive `RungCount`, guard the identity
- [x] **Shipped** — `7e7b3456b` — `CreatureRarityLadder.cs:15` reads `RungCount => All.Count`. On `HEAD` of `features/mega-merge`, re-checked 2026-09-18.

**Description:** `CreatureRarityLadder.RungCount` is a `const` while `All` derives from
`Enum.GetValues`; make `RungCount` derived so they cannot disagree.

**Acceptance criteria:**
- [ ] `RungCount => All.Count`, no `const` left
- [ ] `OneRungAbove`'s throw is proven correct at a *widened* enum width via a test double, not at
      the literal width 10

**Verification:**
- [ ] `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~LadderDeclaration"`
- [ ] `.\scripts\guard-actor-hub.ps1`

**Dependencies:** None
**Files:** `gk-core/src/FusionRpg.Core/Creatures/CreatureRarityLadder.cs`,
`gk-core/tests/FusionRpg.Core.Tests/Creatures/LadderDeclarationTests.cs`
⚠ *Re-anchored 2026-09-23 (lane sgc-6):* this line named
`tests/FusionRpg.Core.Tests/Creatures/CreatureRarityLadderTests.cs`, which **never existed** in this
repository's history (`git log --all --pretty=format: --name-only | sort -u | grep -i rarityladder`
lists no such path on any branch) — a planned name from the task's own text. The file that shipped
is `LadderDeclarationTests.cs`, which is also what this row's own verify filter
(`~LadderDeclaration`) selects.
**Size:** XS

---

#### ✅ Task T2: `tier-propagation-contract` b — remove restatements, guard, split T-5
- [x] **Shipped** — `73817463a` — restatements removed, guard + T-5a/T-5b split in the same commit. On `HEAD` of `features/mega-merge`, re-checked 2026-09-18.

**Description:** Remove the three in-repo rarity/threat restatements (`EncounterTuning.ThreatRungIds`,
the two Python `RARITY`/`THREAT_BAND` tuples), add a guard that fails on a new one, and split T-5 into
T-5a (actor-magnitude `thetaOffset`, additive only) / T-5b (economy-cost coefficient, each owing its
own §10 row) in `ssot-power-scale.md` §10. Leave `Items/RarityLadder.RungIds` **allowlisted**, not
converted, per the spec's Open question 1.

⚠ **Coordinate with T3:** both touch `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/anchor/schema.py`.
Land this task first within this sub-checkpoint.

**Acceptance criteria:**
- [ ] Sites 1–3 read from tuning instead of restating ids; no behaviour change
- [ ] A new test fails if a fourth restatement is added anywhere the guard scans (C# and Python)
- [ ] `ssot-power-scale.md` §10 states T-5a/T-5b explicitly, replacing the single-clause version

**Verification:**
- [ ] `dotnet test gk-core/tests/FusionRpg.Guard.Tests`
- [ ] `$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests -q`
- [ ] `python gk-core/scripts/audit-magic-numbers.py --summary`

**Dependencies:** None
**Files:** `gk-core/src/FusionRpg.Core/Dungeon/Tuning/EncounterTuning.cs`,
`gk-forge/tools/seedsmith/seedsmith/adapters/creatures/anchor/schema.py`,
`gk-forge/tools/seedsmith/seedsmith/adapters/structures/anchor/schema.py`,
`gk-core/tests/FusionRpg.Guard.Tests/`, `docs/architecture/power/ssot-power-scale.md`
**Size:** M

---

#### ✅ Task T3: `threat-band-fill` — score first, default second, with provenance
- [x] **Shipped** — `bbf6e1e39` (generator) + `0faad36e9` (corpus) + `18ed440e1` (follow-up regen) — `anchor/derive.py` stamps provenance. On `HEAD` of `features/mega-merge`, re-checked 2026-09-18.

**Description:** Try `classify()` before falling back to the flat `inferredDefaultRung`; record which
happened; re-validate that no rung is empty by construction after the fill.

**Acceptance criteria:**
- [ ] Every species with a scoreable power seed (`observed`/`stated` basis) carries a **scored**
      `threatBand`, not the flat default
- [ ] Every species carries provenance distinguishing `scored`/`default`/`authored`
- [ ] `SpeciesExpander.cs:31-33`'s exclusion of `threatBand` from the batch-refusal list is
      **preserved** (it is correct), with a comment recording why
- [ ] The fitted deciles are re-validated against the post-fill distribution and the result is
      **reported**, not asserted — no rung is empty by construction
- [ ] The corpus diff is a pure regeneration — no hand edits, proven by re-running the generator and
      getting a byte-identical tree

**Verification:**
- [ ] `$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/test_anchor_derive.py gk-forge/tools/seedsmith/tests/test_run_runner.py -q`
- [ ] `cd gk-forge/tools/seedsmith; python -m seedsmith check gk-data/packs/fusion/data/seed/creatures --adapter creatures`
- [ ] `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Threat"`
- [ ] `dotnet run --project gk-forge/tools/CreatureQualityReport` — print the histogram **including
      zero-occupant rungs** and the provenance split; never assert either

**Dependencies:** None (⚠ shares `anchor/schema.py` with T2 — land after T2 within this sub-checkpoint)
**Files:** `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/anchor/derive.py`,
`gk-forge/tools/seedsmith/seedsmith/adapters/creatures/run/runner.py`,
`gk-forge/tools/seedsmith/seedsmith/adapters/creatures/anchor/schema.py`,
`gk-data/packs/fusion/data/seed/creatures/species/**` (regenerated)
**Size:** M

---

#### ✅ Task T4: `socket-allowance-by-kind` — the per-kind table, shift-before-roll
- [x] **Shipped** — `72607c136` — `socketAllowanceByKind` present in `sockets.v1.json` (an in-place `version` 2→3 edit: grandfathered history, map § Corrections #11 reversal — never a template). On `HEAD` of `features/mega-merge`, re-checked 2026-09-18.

**Description:** Add `socketAllowanceByKind` to `sockets.v1.json` (version 2→3); shift the rarity
window before the roll; enforce all four rejections the derived table needs, not just the inverted
case; pin rows to `catalog_revision`, append-only.

**Acceptance criteria:**
- [ ] Composition order: window shift → roll → base `socketMax` clamp → role ceiling → structural
      bound (throws above `structuralCeiling`)
- [ ] All four rejections load-reject naming kind and rung: **inverted**, **non-overlapping**,
      **non-monotonic**, **negative** — OD4's overlap/monotonicity guarantee is preserved for the
      derived table, not just the authored one
- [ ] `socketAllowanceByKind` rows are append-only, pinned to `catalog_revision` — same contract as
      `rarityGrant`; **no shipped `rarityGrant` row is edited**
- [ ] The inversion's boundedness at `sunwoven`/`almanac` (already at the structural ceiling) is
      **reported**, not hidden
- [ ] An ordinary item's socket count is byte-identical to today for every rung/role

**Verification:**
- [ ] `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Socket"`
- [ ] `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~ItemSocket"`
- [x] `dotnet run --project gk-forge/tools/ItemSeedValidator`
- [ ] `dotnet test gk-core/tests/FusionRpg.Guard.Tests`

**Dependencies:** None
**Files:** `gk-core/data/tuning/sockets.v1.json`, `gk-core/src/FusionRpg.Core/Items/Sockets/SocketTuning.cs`,
`tests/FusionRpg.Core.Tests/Items/Sockets/`
**Size:** M

---

### Checkpoint — sub-group 1a
*All tasks in this group shipped (see each tick). Suite-green lines are not re-run in this planning pass — the next full-suite point is the parent's CC8.*
- [ ] `dotnet test gk-core/tests/FusionRpg.Core.Tests`, `Guard.Tests` green
- [ ] seedsmith pytest for the touched adapters green
- [ ] No golden re-blessed

---

### Sub-checkpoint 1b — species selection admission + gems

#### ✅ Task T5: `CreatureAdmission` — the shared admission policy type (new)
- [x] **Shipped** — `cb43a0049` — `gk-core/src/FusionRpg.Core/Creatures/CreatureAdmission.cs` is the one declaring site. On `HEAD` of `features/mega-merge`, re-checked 2026-09-18.

**Description:** One declaring site for the per-context creature-acquisition rule, replacing the two
governing specs' inconsistent claims about who owns it. `spec-wild-species-spawn.md` states *"whichever
of the three modules ships first creates it"*; `spec-wave-species-roll.md`'s own code sample instead
inlines the filter — that inline sample is **superseded** by this task.

**Acceptance criteria:**
- [ ] `CreatureAdmission.ForWave` / `ForWildMap` / `ForDelve` exist in one file
- [ ] `EventOnly` is refused first and unconditionally in every context; `ForWave` refuses
      `CaptureOnly`, `ForWildMap`/`ForDelve` admit it
- [ ] A species carrying `Summonable | EventOnly` (synthetic — none shipped carries both today) is
      refused by every context, proven by test — the population alone must not be the only thing
      making the filter correct

**Verification:**
- [ ] `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~CreatureAdmission"`

**Dependencies:** None
**Files:** `gk-core/src/FusionRpg.Core/Creatures/CreatureAdmission.cs` (new),
`gk-core/tests/FusionRpg.Core.Tests/Creatures/`
**Size:** XS

---

#### ✅ Task T6: `wave-species-roll` — seeded weighted draw, calling the shared admission type
- [x] **Shipped** — `63b9e8eb9` — `WaveCatalog.cs:172` filters `.Where(CreatureAdmission.ForWave)` (`waves.v1.json` edited in place: grandfathered, as T4). On `HEAD` of `features/mega-merge`, re-checked 2026-09-18.

**Description:** Replace `WaveCatalog`'s `pool[i % pool.Count]` with a seeded weighted draw over a
rarity window, calling `CreatureAdmission.ForWave` — **not** the spec's own inline sample, which T5
supersedes.

**Acceptance criteria:**
- [ ] Draw is seeded and replay-stable, proven across a shuffled catalog order (not just a fixed one)
- [ ] `Band` calls `CreatureAdmission.ForWave` rather than an inline predicate
- [ ] `EventOnly` refused by rule, proven with a synthetic `Summonable | EventOnly` species
- [ ] Waves can draw from all ten rungs; the 486-species `Fused` rung is reachable by configuration
      alone
- [ ] `waves.v1.json` gains `schemaVersion`/`version` (an **add**, not a bump — the file has neither
      field today) plus the window/weight tables; no weight is a `const` in C#
- [ ] The stale four-rung comment at `WaveCatalog.cs:121-126` is corrected or deleted

**Verification:**
- [ ] `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~WaveCatalog"`
- [ ] `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "Category=BalanceGuard"`
- [ ] `dotnet test gk-core/tests/FusionRpg.Guard.Tests`, `gk-core/tests/FusionRpg.Data.Tests`
- [ ] Confirm no golden re-blessed

**Dependencies:** T5
**Files:** `gk-core/src/FusionRpg.Core/Battle/WaveCatalog.cs`, `gk-core/data/tuning/waves.v1.json`,
`gk-core/tests/FusionRpg.Core.Tests/Battle/`
**Size:** M

---

#### ✅ Task T7: `wild-species-spawn` — sector-weighted roll, calling the shared admission type
- [x] **Shipped** — `d2361c761` — `World/Loam/WildSpawnRoller.cs` calls `CreatureAdmission.ForWildMap`; `gk-core/data/tuning/world-spawn.v1.json`. On `HEAD` of `features/mega-merge`, re-checked 2026-09-18.

**Description:** Replace `SpawnTheUnmade`'s `"normalzombie"` literal with a sector/climate-weighted
roll, calling `CreatureAdmission.ForWildMap`. ⚠ **Ships with the flat `LoamPolicy.UnmadeMemberHp`
as an interim value** — the owner decided (2026-09-13) that wild members should ultimately take their
own species' `P(Θ)`, but that needs `species-magnitude-synth` (Phase 2), so it is **T18b**, a small
follow-on task, rather than a dependency that would pull this whole task into Phase 2.

**Acceptance criteria:**
- [ ] Wild warband composition is rolled, seeded from `(worldSeed, sectorId, turn)`, replay-stable —
      proven twice and across a shuffled catalog order
- [ ] `CaptureOnly` admitted, `EventOnly` refused, each proven with a species carrying that flag
- [ ] Climate weighting is live and tunable; `offClimateMilli` reuses the shipped key name
- [ ] Spawn cadence, occupancy guarding, and the `unmade.spawned` turn-report event are unchanged
- [ ] The weight table is data; no species id and no weight is a `const` in C#
- [ ] A sector whose admissible pool is empty does **not** throw — it falls back to a named,
      documented species rather than crashing a turn
- [ ] The spawn table can express a non-recruitable wild creature, even though none is authored yet
      (the demon/void-beast third category the owner introduced — named only, no content here)
- [ ] Each member's `Hp` field is left as a clearly-named interim value (e.g. a local constant
      referencing `LoamPolicy.UnmadeMemberHp` with a comment pointing at T18b), not hardcoded fresh

**Verification:**
- [ ] `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Loam"`
- [ ] `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~WorldTurn"`
- [ ] `dotnet test gk-core/tests/FusionRpg.Guard.Tests`, `gk-core/tests/FusionRpg.Data.Tests`

**Dependencies:** T5
**Files:** `gk-core/src/FusionRpg.Core/World/Loam/LoamPhases.cs`, `gk-core/data/tuning/` (new world-spawn domain file),
`gk-core/tests/FusionRpg.Core.Tests/World/`
**Size:** M

---

#### ✅ Task T8: `gem-tier` a — derive tier from `powerBand`, stop hardcoding 1
- [x] **Shipped** — `15ffb5f97` — `GemInsertCorpus` reports `TierOfPowerBand` (`ItemCardEndpoints.cs:132-138`); `UnauthoredInsertTier` survives only as the unauthored-container fallback. On `HEAD` of `features/mega-merge`, re-checked 2026-09-18.

**Description:** Replace the hardcoded `UnauthoredInsertTier = 1` at the three socket call sites with
`UniqueBudget.TierOfPowerBand(gem.PowerBand)`. **Do not author a `tier` field on a gem entry** —
`entry-shapes.md:81` makes that an `OwnershipViolation`.

**Acceptance criteria:**
- [ ] Every shipped gem reports a tier derived from its own `powerBand`, at all three call sites
- [ ] An unknown `powerBand` is a rejection naming the gem; no silent fallback to tier 1
- [ ] `UnauthoredInsertTier` is reached only for a container the corpus does not carry, and its
      comment says so
- [ ] Every combination whose ingredient families are all present in the gem corpus becomes
      satisfiable, proven by a test computing both sides from the corpus (not a pinned count)
- [ ] The mirror/registry reconciliation test is green: `TierOfPowerBand` agrees with
      `bands.v1.json powerBand.tierMap` key-for-key
- [ ] `insertTiers.count` remains a soft axis — a tier above it is accepted, proven by test
- [ ] No gem entry gains a `tier` field; `ItemSeedValidator`'s `OwnershipViolation` check stays green

**Verification:**
- [ ] `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Gem"`
- [ ] `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~Socket"`
- [ ] `dotnet run --project gk-forge/tools/ItemSeedValidator`

**Dependencies:** None
**Files:** `gk-core/src/FusionRpg.Server/ItemCardEndpoints.cs`, `ItemSurfaceEndpoints.cs`, `ItemWorkbench.cs`
(the three hardcoded-1 sites), `gk-core/tests/FusionRpg.Core.Tests/Items/`
**Size:** S

---

#### ✅ Task T9: `gem-tier` b — the upcycle verb and `recipegen` content
- [x] **Shipped** — `50368b576` (verb + endpoint + emitter) + `eddd9e11b` (regenerated recipe row) — `ItemWorkbench.ForgeGem` at `ItemWorkbench.cs:311`. On `HEAD` of `features/mega-merge`, re-checked 2026-09-18.

**Description:** ⚠ **New task — split out of T8 after the coverage audit found the module's own SC6–8
silently dropped.** Wire `SocketTuning.UpcycleInputPerOutput`'s first production reader, add the
sixth `ItemWorkbench` verb (shaped on `Upcycle` — a stock-to-stock mint, no host instance, no new
`MutationOpKind`), and extend `recipegen` to emit `forge-gem` rows.

**Acceptance criteria:**
- [ ] `SocketTuning.UpcycleInputPerOutput` has a real production reader
- [ ] `ItemWorkbench` exposes a new verb with a POST endpoint, consuming exactly
      `upcycleInputPerOutput` input gems per output gem, idempotent on `(playerId, correlationId)`
- [ ] `forge-gem` recipe rows exist because `recipegen` emits them, and the regenerated diff is
      committed — no seed JSON is hand-edited
- [ ] No new `CraftOperation`/`MutationOpKind` member — `ForgeGem` already exists and is already
      priced; this task uses it, it does not widen either enum

**Verification:**
- [ ] `dotnet test gk-core/tests/FusionRpg.Server.Tests`
- [ ] `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~InstanceOp"`
- [ ] `$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests -q -k recipe`
- [ ] `dotnet run --project gk-forge/tools/ItemSeedValidator`

**Dependencies:** T8
**Files:** `gk-core/src/FusionRpg.Server/ItemWorkbench.cs`, `WorkbenchEndpoints.cs`,
`gk-forge/tools/seedsmith/seedsmith/adapters/items/recipegen/`, `gk-data/packs/fusion/data/seed/items/recipes/recipes.json`
(regenerated)
**Size:** M

---

### Checkpoint — sub-group 1b
*All tasks in this group shipped (see each tick). Suite-green lines are not re-run in this planning pass — the next full-suite point is the parent's CC8.*
- [x] `CreatureAdmission` has exactly one declaring site; T6 and T7 both call it, neither inlines — checked 2026-09-18: `WaveCatalog.cs:172` (`ForWave`), `WildSpawnRoller.cs` (`ForWildMap`), and T20's `ForDelve`
- [ ] `dotnet test gk-core/tests/FusionRpg.Core.Tests` green
- [ ] Every shipped gem's tier resolves from `powerBand`; `ItemSeedValidator` green

---

### Sub-checkpoint 1c — risk ladder, durability slice, executors

#### ✅ Task T10: `craft-risk-ladder` Stage 1 — potential, always-succeeds
- [x] **Shipped** — `f67930ace` (with T11) — `CraftRiskPolicy.cs`; `CanDecay` is the named `false` stub T24 replaces. On `HEAD` of `features/mega-merge`, re-checked 2026-09-18.

**Description:** Add `craft_potential_max`/`craft_potential_current` columns to `effect_instance`
(idempotent, nullable, lazy backfill); derive from `class`/`rarity`/`tags` with an explicit-or-absent
authored override (never a sentinel). **Two of the module's seven cross-program asks are explicit
preconditions and are filed as part of this task, not skipped:**

- Ask #6 (*"File it; do not build through it"*) — reconcile the authored-override design against
  `deployment-hierarchy` module 7's own Never list (`spec-item-durability-repair.md:408` forbids
  per-item authored derived fields) **before** writing the override mechanism.
- Ask #7 (*"Agree the section layout before Stage 1 builds"*) — since T11 (below) now creates
  `gk-core/data/tuning/deployment-hierarchy.v1.json` in the same sub-checkpoint, agree its section layout
  with T11 before either reads/writes it.

**Acceptance criteria:**
- [ ] Asks #6 and #7 are filed and resolved (a short written reconciliation, reviewed) **before** the
      override mechanism and the shared tuning file are implemented
- [ ] Every rolled equipment instance carries a derived potential pair; pre-existing instances
      backfill lazily and are never mistaken for exhausted
- [ ] The override is explicit-or-absent; an expected-but-missing one throws naming the base type
- [ ] While potential remains, every craft verb succeeds — proven across the priced operations
- [ ] No decay, no destroy path, no `EnhanceOutcome` member added — this task stops at "assured."
      **This is no longer a permanent state** — T24 (Phase 2) wires the decay path once T11's
      durability storage exists, so the hard-stop risk `AGENTS.md` forbids is bounded to this plan's
      own short Phase-1→Phase-2 gap, not an indefinite external wait

**Verification:**
- [ ] `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~InstanceOp"`
- [ ] `dotnet test gk-core/tests/FusionRpg.Core.Items.Tests --filter "FullyQualifiedName~Potential"`
- [ ] `.\scripts\guard-dal.ps1`, `python gk-core/scripts/guard-test-substrate.py`, `.\scripts\guard-actor-hub.ps1`
- [ ] `python gk-core/scripts/audit-overflow.py`

**Dependencies:** None (coordinate with T11 on the shared tuning file's section layout)
**Files:** `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.InstanceOps.cs`,
`gk-core/src/FusionRpg.Core/Items/*/PotentialTable.cs` (new), `gk-core/data/tuning/deployment-hierarchy.v1.json`
(new, shared with T11), `gk-core/tests/FusionRpg.Data.Tests/Items/`
**Size:** M

---

#### ✅ Task T11: `durability-slice` a — storage + derivation + at-zero filter (pulled forward)
- [x] **Shipped** — `f67930ace` (with T10) — `deployment-hierarchy.v1.json` created; `v2` since `ecc18cf3` (magic-numbers sweep); note filed at `deployment-hierarchy-map.md:168-186`. On `HEAD` of `features/mega-merge`, re-checked 2026-09-18.

**Description:** ⚠ **New task — owner-approved 2026-09-13 pull-forward of a minimal slice of
`deployment-hierarchy` module 7**, built exactly to `spec-item-durability-repair.md` §1/§2/§6, so it
is a subset of that module's own eventual full build, not a parallel invention. **Skips:** field
touch-up (needs `PackGrid`, unbuilt), death-drop decay (needs `corpse-cache`, unbuilt), commander-pouch
parity (D6) — those stay `deployment-hierarchy`'s own future work. File a note in
`deployment-hierarchy-map.md` recording that this slice exists, so that program's own plan does not
duplicate it.

**Acceptance criteria:**
- [ ] `durability_max`/`durability_current` columns added to `effect_instance`, idempotent, nullable,
      lazy-backfilled — exact `enhance_level` precedent
- [ ] `DurabilityTable.Build(baseTypeEntries, tuning)` derives `max` from `class`/`rarity`/`tags`,
      `checked`, widen-first, divide-last, refusing at load on an unknown id, never defaulting
- [ ] The at-zero filter is one `.Where(...)` clause in `MaterializeRolledEquipRuntime`'s assignments
      query — reuses the existing withdraw-on-absence machinery, adds no new Hub gate
- [ ] Stock-backed (`ref_kind != "rolled"`) assignments never populate these columns
- [ ] A note is filed in `deployment-hierarchy-map.md` recording this slice's exact scope and what it
      deliberately excludes

**Verification:**
- [ ] `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~Durability"`
- [ ] `.\scripts\guard-dal.ps1`, `.\scripts\guard-actor-hub.ps1`, `python gk-core/scripts/guard-test-substrate.py`
- [ ] `python gk-core/scripts/audit-overflow.py`

**Dependencies:** None (coordinate with T10 on the shared tuning file's section layout)
**Files:** `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.InstanceOps.cs`,
`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Items.cs` (`MaterializeRolledEquipRuntime`),
`gk-core/src/FusionRpg.Core/Items/*/DurabilityTable.cs` (new),
`gk-core/data/tuning/deployment-hierarchy.v1.json` (new, shared with T10),
`docs/architecture/deployment-hierarchy-map.md` (the filed note)
**Size:** M

---

#### ✅ Task T12: `enhance-track-wiring` a — generate the missing `atom.enhance-*` rows
- [x] **Shipped** — `876641fc7` — `atom.enhance-*` rows regenerated by the widened `FamilyExpandGen`. On `HEAD` of `features/mega-merge`, re-checked 2026-09-18.

**Description:** `FamilyExpandGen` reads only `affix-families/`, top-directory-only, so
`atom.enhance-*` has zero expanded atom rows. Widen the generator's scope; regenerate.

**Acceptance criteria:**
- [ ] `atom.enhance-*` families produce real rows in `gk-data/packs/fusion/data/seed/atoms/generated/**`
- [ ] `FamilyExpandGen --check` is green; the diff is a pure regeneration
- [ ] Every shipped `enhanceTrack[].family` resolves against the regenerated corpus, asserted as a
      join, not a count

**Verification:**
- [ ] `dotnet run --project gk-forge/tools/FamilyExpandGen -- --check`
- [ ] `python -m pytest gk-forge/tools/seedsmith/tests/test_base_types_gen.py -q -k enhance_track` ⚠ *corrected 2026-09-23 (lane sgc-6):* this box used to be a `dotnet test` filter over `FusionRpg.Core.Tests` for `~EnhanceTrack`, which selects **nothing** — the token `EnhanceTrack` appears in no test NAME in any project under `tests/**`, only as a parameter name in `ItemWorkbenchEndpointsTests.cs:1643`; the join this box wants is asserted Python-side, and `-k enhance_track` selects **5 passed, 67 deselected**

**Dependencies:** None
**Files:** `gk-forge/tools/FamilyExpandGen/Program.cs`, `gk-data/packs/fusion/data/seed/atoms/generated/**` (regenerated)
**Size:** S

---

#### ✅ Task T13: `enhance-track-wiring` b — wire the milestone append
- [x] **Shipped** — `f9d81a965` — `EnhancePolicy.IsMilestoneLevel` has a production caller (`ItemWorkbench.cs:648`). On `HEAD` of `features/mega-merge`, re-checked 2026-09-18.

**Description:** `ItemWorkbench.Enhance` passes `Array.Empty<AtomAppend>()`, and
`RpgStore.AppendMutationOpUnlocked` applies `result.Suppressed` but never inserts for
`result.Appended` — a second inert seam. Fix both.

**Acceptance criteria:**
- [ ] An enhancement to an authored milestone level appends a real atom, recorded in the op ledger
      **and** present on `effect_instance_atom` — proven on a live item
- [ ] `EnhancePolicy.IsMilestoneLevel` gains a production caller
- [ ] The ladder is unbounded above — a milestone still grants far past the last authored `atLevel`,
      asserted by test (no hard ceiling)
- [ ] Replay appends exactly once and never re-resolves the family, on `(instanceId, correlationId)`
- [ ] Missing tuning section, unknown family, unknown tier all reject by name — no default anywhere
- [ ] Zero members added to `MutationOpKind`/`CraftOperation` by this task

**Verification:**
- [ ] `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~InstanceOp"`
- [ ] `dotnet test gk-core/tests/FusionRpg.Server.Tests`
- [ ] `.\scripts\guard-dal.ps1`, `.\scripts\guard-actor-hub.ps1`
- [ ] `dotnet run --project gk-forge/tools/ItemSeedValidator`
- [ ] `python gk-core/scripts/audit-overflow.py`

**Dependencies:** T12
**Files:** `gk-core/src/FusionRpg.Server/ItemWorkbench.cs`,
`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.InstanceOps.cs`, `gk-core/tests/FusionRpg.Data.Tests/Items/`
**Size:** M

---

#### ✅ Task T14: `craft-executor-completion` a — the `Forge` executor
- [x] **Shipped** — `e66618a3e` — `ItemWorkbench.Forge` at `ItemWorkbench.cs:393`. On `HEAD` of `features/mega-merge`, re-checked 2026-09-18.

**Description:** `ItemWorkbench.cs:189-193`'s "forge cannot run" comment is stale —
`EquipmentContainerBuild.From` already builds the container on the fly. Wire the seventh recipe verb.
**No dependency on `rarity-promotion`** — the owning spec's own header corrects the map's stale claim
that it does; this task needs zero enum members.

**Acceptance criteria:**
- [ ] All 7 authored `forge` recipes execute end to end and mint a real, saved instance with
      `InstanceOrigin.Craft` — computed from the corpus, not a pinned count
- [ ] `ItemWorkbench.cs:189-193`'s comment is corrected, with the evidence cited
- [ ] Zero members added to `CraftOperation`/`MutationOpKind` by this task
- [ ] `imbue` and `forge-gem`-as-a-mint (distinct from T9's upcycle verb) are documented as a
      **content** gap with a named owner (`recipegen`, module 16) and a named path — neither is
      closed by hand-editing seed data

**Verification:**
- [ ] `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~InstanceOp"`
- [ ] `dotnet test gk-core/tests/FusionRpg.Server.Tests`

**Dependencies:** None
**Files:** `gk-core/src/FusionRpg.Server/ItemWorkbench.cs`, `WorkbenchEndpoints.cs`
**Size:** M

---

#### ✅ Task T15: `craft-executor-completion` b — `RerollOne`/`RerollAll`
- [x] **Shipped** — `99e413984` — `ItemWorkbench.RerollOne`/`RerollAll` at `ItemWorkbench.cs:566`/`:572`. On `HEAD` of `features/mega-merge`, re-checked 2026-09-18.

**Description:** Wire the remaining two verbs through the already-built `RerollPolicy`.

**Acceptance criteria:**
- [ ] All authored `reroll-one` and `reroll-all` recipes execute end to end
- [ ] `reroll-all`'s suppress and append both reach `effect_instance_atom`
- [ ] `ItemWorkbench` exposes nine verb methods total, in one consistent shape, each with a POST
- [ ] The debit and the product commit together; replay is idempotent for all three new verbs (this
      task's two plus T14's forge)
- [ ] A contract test makes any future priced-but-unroutable verb fail loudly rather than silently
      (the same class of bug `forge`/`reroll-*` were)

**Verification:**
- [ ] `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~InstanceOp"`
- [ ] `dotnet test gk-core/tests/FusionRpg.Server.Tests`
- [ ] `dotnet test gk-core/tests/FusionRpg.Core.Tests` (full suite — this task claims none stranded remain)
- [ ] `dotnet test gk-core/tests/FusionRpg.E2E.Tests`
- [ ] `dotnet run --project gk-forge/tools/ItemSeedValidator`
- [ ] `.\scripts\guard-dal.ps1`, `.\scripts\guard-actor-hub.ps1`
- [ ] `python gk-core/scripts/audit-overflow.py`

**Dependencies:** T14
**Files:** `gk-core/src/FusionRpg.Server/ItemWorkbench.cs`, `WorkbenchEndpoints.cs`,
`gk-core/tests/FusionRpg.Data.Tests/Items/`
**Size:** M

---

#### ✅ Task T35: `requirement-profiles-pullforward` a — resolver + evaluator (new)
- [x] **Shipped** — `ac2dae72e` — `gk-core/src/FusionRpg.Core/Items/Requirements/RequirementProfileResolver.cs`, `RequirementTrialEvaluator.cs`. On `HEAD` of `features/mega-merge`, re-checked 2026-09-18.

**Description:** ⚠ **New — owner-approved 2026-09-13 pull-forward of `item` module 23
`requirement-profiles`**, built exactly to its own complete, approved spec
(`docs/architecture/item/spec-requirement-profiles.md`), not a parallel invention. A pure,
deterministic resolver: `(rollSeed, resolverRevision, catalogRevision, tuningRevision, contentTheta,
P(Θ), PowerVector, rarityId, buildFavorPool) → RequirementProfile | RequirementProfileRejection`,
plus `RequirementTrialEvaluator` (pure, unassisted actor-input evaluation). **No schema/persistence
change** — the spec's own v1 scope explicitly excludes it, deferring persistence to module 24.

**Acceptance criteria:**
- [ ] Every valid concrete input resolves to one frozen, replayable profile or one named rejection —
      never a fallback
- [ ] A generated requirement never turns an otherwise-legal assignment into a refusal; an unmet
      trial is observable evaluation data only
- [ ] `RequirementTrialEvaluator.EvaluateRatio` uses `checked` `long` arithmetic
      (`aptitudePoints * 1000 >= grandAllocationPoints * minimumShareMilli`), never the `double`
      convenience reader
- [ ] Rarity selects the distribution-matrix row only; threshold/reserve/cost/period lookups never
      receive rarity after a profile kind is selected
- [ ] Six named `SeededRng.DeriveStream` streams (`item.requirements:v1:profile` etc.), ordinally
      sorted, unique candidates before each draw

**Verification:**
- [ ] `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~RequirementProfile"`
- [ ] `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~AptitudeAllocation"`
- [ ] `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Power"`
- [ ] `python gk-core/scripts/audit-magic-numbers.py`

**Dependencies:** None
**Files:** `gk-core/src/FusionRpg.Core/Items/Requirements/RequirementProfile.cs` (new),
`RequirementProfileResolver.cs` (new), `RequirementTrialEvaluator.cs` (new),
`tests/FusionRpg.Core.Tests/Items/RequirementProfileTests.cs`
**Size:** M

---

#### ✅ Task T36: `requirement-profiles-pullforward` b — tuning + Seedsmith validation (new)
- [x] **Shipped** — `b158acf13` — `gk-core/data/tuning/equipment-requirements.v1.json`; note filed at `item-map.md:317-350`. On `HEAD` of `features/mega-merge`, re-checked 2026-09-18.

**Description:** `gk-core/data/tuning/equipment-requirements.v1.json` (rarity × power-band × focus-band
profile weights, maintenance eligibility bands, jackpot weight); Seedsmith build-favor-label
classification, validated and resolved to legal aptitude ids, never a model-supplied magnitude.

**Acceptance criteria:**
- [ ] All balance values come from `equipment-requirements.v1.json`; source contains no balance
      literals
- [ ] Lower power bands give maintenance zero weight; rarity alone cannot create upkeep
- [ ] Invalid Seedsmith classification or tuning blocks acceptance with no partial profile
      (`blocked`, writes no seed — the pipeline's validate-before-accept rule)
- [ ] A model never supplies a magnitude, probability, duration, resolver decision, or runtime input

**Verification:**
- [ ] `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~RequirementProfile"`
- [ ] `$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests -q -k requirement`
- [ ] `python gk-core/scripts/audit-magic-numbers.py`

**Dependencies:** T35
**Files:** `gk-core/src/FusionRpg.Core/Items/Requirements/RequirementProfileTuning.cs` (new),
`gk-core/data/tuning/equipment-requirements.v1.json` (new), `gk-forge/tools/seedsmith/seedsmith/adapters/items/`
**Size:** M

---

### Checkpoint — Phase 1 (complete)
*All tasks in this group shipped (see each tick). Suite-green lines are not re-run in this planning pass — the next full-suite point is the parent's CC8.*
- [ ] `dotnet test gk-core/tests/FusionRpg.Core.Tests`, `Guard.Tests`, `Data.Tests`, `Server.Tests` green
- [ ] `$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests -q` green
- [ ] No golden re-blessed, or a separately reviewed commit names which moved and why
- [x] `deployment-hierarchy-map.md` carries the filed note for the durability-slice pull-forward — `:168-186`
- [x] `item-map.md` carries the filed note for the requirement-profiles pull-forward — `:317-350`
- [ ] **Review with owner before Phase 2** — Phase 2 is half-built (T16–T21 shipped); no record of this review was found, so it is left open rather than assumed

---

## Phase 2

#### ✅ Task T16: `ladder-consistency-repair` a — publish `themes.v2.json`
- [x] **Shipped** — `2b1d24642` — `gk-data/packs/fusion/data/seed/creatures/_registry/themes.v2.json`; `setgen/themes.py` reads v2 (`item-map.md:139`). On `HEAD` of `features/mega-merge`, re-checked 2026-09-18.

**Description:** Publish v2 with `rarity` re-derived from the current anchor and every other field
byte-identical; migrate `set-charm-gen` and the other v1 readers.

**Acceptance criteria:**
- [ ] `themes.v2.json` has 904 rows, zero retired rarity ids, every non-`rarity` field byte-identical
      to v1 (a closure property, not "84 were fixed")
- [ ] No `themeKey` renamed — the 844 bound set entries are unaffected
- [ ] `set-charm-gen` and the other v1 consumers read v2; v1 stays in place, unretired
- [ ] The refresh is idempotent — a second run produces a byte-identical tree

**Verification:**
- [ ] `$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests -q -k theme`
- [ ] `cd gk-forge/tools/seedsmith; python -m seedsmith check gk-data/packs/fusion/data/seed/creatures --adapter creatures`

**Dependencies:** T2
**Files:** `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/generate_themes.py`,
`gk-data/packs/fusion/data/seed/creatures/_registry/themes.v2.json` (new),
`gk-forge/tools/seedsmith/seedsmith/adapters/creatures/generate_families.py`, `theme_enrich.py`
**Size:** M

---

#### ✅ Task T17: `ladder-consistency-repair` b — FE roster sort by ordinal
- [x] **Shipped** — `e866b9bef` — the `rarityLadder` module + ordinal sort in `rosterSplit`/`CreaturesPage`. On `HEAD` of `features/mega-merge`, re-checked 2026-09-18.

**Description:** Replace the four sites keying on the retired vocabulary with an ordinal comparator
that surfaces an unknown id instead of defaulting; correct the stale "84 rows" comments.

**Acceptance criteria:**
- [ ] The FE roster sort visibly sorts, proven with species spanning several rungs
- [ ] An unknown rarity id renders a visible "unknown" marker rather than silently sorting to a
      default
- [ ] `npm run build` (`tsc --noEmit`) passes — no site still references a retired id
- [ ] The stale *"themes.v1.json (84 rows)"* comments (a different, unrelated 84 from the old catalog
      size) are corrected where encountered, explicitly not conflated with the retired-id count

**Verification:**
- [ ] `cd gk-web/web/fusion-rpg-web; npm test`
- [ ] `npm run build`
- [ ] `npm run check:bundle`

**Dependencies:** None
**Files:** `gk-web/web/fusion-rpg-web/src/features/creatures/rosterSplit.ts`,
`src/lib/bus/creatures.ts`, `src/layers/pacts/PactsLayer.tsx`, `src/pages/CreaturesPage.tsx`
**Size:** M

---

#### ✅ Task T18: `species-magnitude-synth` — synthesize containers at import time
- [x] **Shipped** — `4feb57419` — species-magnitude containers synthesized in `RpgStore.Species.cs`. On `HEAD` of `features/mega-merge`, re-checked 2026-09-18.

**Description:** Synthesize `trait.species-magnitude-*` containers in `ImportCreatureSpecies` from
rows already in `creature_species_magnitude` — upsert, never a committed corpus.

**Acceptance criteria:**
- [ ] A deployed creature specimen binds its species-magnitude container instead of taking the
      fail-closed return — proven end to end
- [ ] Every species with magnitudes has exactly one container; every species without has none
- [ ] Container members reconcile exactly against `creature_species_magnitude`; import is idempotent
- [ ] A magnitude change withdraws the stale binding and rebinds — the existing machinery still holds
- [ ] Zero species-magnitude files committed to `data/`; values are `long` end to end

**Verification:**
- [ ] `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~Species"`
- [ ] `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~UniqueActor"`
- [ ] `.\scripts\guard-dal.ps1`, `.\scripts\guard-actor-hub.ps1`, `python gk-core/scripts/guard-test-substrate.py`
- [ ] `python gk-core/scripts/audit-overflow.py`

**Dependencies:** T3 (rewrites every magnitude — must land first)
**Files:** `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Species.cs`, `gk-core/tests/FusionRpg.Data.Tests/`
**Size:** M — **do not modify** `RpgStore.UniqueActors.cs:1619-1620`

---

#### ✅ Task T18b: `wild-species-spawn` — wire species `P(Θ)` for wild member HP (new)
- [x] **Shipped** — `ee09f9d7a` — wild members read species `P(Θ)`; `LoamPolicy.UnmadeMemberHp` kept as the named fallback. On `HEAD` of `features/mega-merge`, re-checked 2026-09-18.

**Description:** ⭐ **Owner decision, 2026-09-13** (`spec-wild-species-spawn.md` Open question 2).
Replace T7's interim `LoamPolicy.UnmadeMemberHp` with each spawned member's own species-derived
`P(Θ)`, now that `species-magnitude-synth` (T18) has landed containers for every species.

**Acceptance criteria:**
- [ ] A spawned wild member's HP comes from its own species' derived magnitude, not one flat value
      shared by all
- [ ] A species with no magnitude container (should not exist post-T18, but defensively) falls back
      to the same named interim constant T7 used, never a crash
- [ ] `LoamPolicy.UnmadeMemberHp` is either removed or explicitly retained only as that fallback, with
      a comment saying so
- [ ] No new ActorHub composer — the magnitude is read from the container T18 already binds through

**Verification:**
- [ ] `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Loam"`
- [ ] `.\scripts\guard-actor-hub.ps1`
- [ ] `python gk-core/scripts/audit-overflow.py`

**Dependencies:** T7, T18
**Files:** `gk-core/src/FusionRpg.Core/World/Loam/LoamPhases.cs`, `gk-core/src/FusionRpg.Core/World/Loam/LoamPolicy.cs`,
`gk-core/tests/FusionRpg.Core.Tests/World/`
**Size:** S

---

#### ✅ Task T19: `delve-species-wiring` a — fix the `CreatureTypeId` collision
- [x] **Shipped** — `937390c3b` — `CreatureSpeciesCatalog.CreatureTypeIdFor` (`CreatureSpeciesCatalog.cs:62`), called by all three sites. On `HEAD` of `features/mega-merge`, re-checked 2026-09-18.

**Description:** `SlotFilter.CreatureTypeId` omits the plant offset the other two sites apply,
colliding 102 measured plant/zombie `gameTypeId` pairs. Extract one
`CreatureTypeIdFor(side, gameTypeId)` function; convert all three sites to call it.

**Acceptance criteria:**
- [ ] `CreatureTypeId` is unique across the full catalog, enforced by a test
- [ ] The plant offset lives in exactly one function, called by all three sites
- [ ] A plant and a zombie sharing a `gameTypeId` get different ids

**Verification:**
- [ ] `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~CreatureTypeId"`

**Dependencies:** None
**Files:** `gk-core/src/FusionRpg.Core/Creatures/CreatureSpeciesCatalog.cs`,
`gk-core/src/FusionRpg.Core/Delve/Encounter/SlotFilter.cs`,
`gk-core/src/FusionRpg.Core/Creatures/Generation/ConcreteSpeciesSeedReader.cs`, `CreatureSpeciesGenerator.cs`
**Size:** S

---

#### ✅ Task T20: `delve-species-wiring` b — production caller for `Encounter.Build`
- [x] **Shipped** — `50a054c1e` — `DelveBattleSessionManager.ResolveRoomEncounter` calls `Encounter.Build`, admits via `CreatureAdmission.ForDelve` (`:125`). ⚠ It left a stale class comment at `DelveBattleSessionManager.cs:27-28` — **T48**. On `HEAD` of `features/mega-merge`, re-checked 2026-09-18.

**Description:** Wire the Delve's room resolution to call `Encounter.Build`; surface
`EncounterRefusal`; admit via `CreatureAdmission.ForDelve`.

⚠ Confirm the `E2E.Tests` baseline before attributing any failure to this task (a known pre-existing
cluster exists).

**Acceptance criteria:**
- [ ] A real delve room resolves through `Encounter.Build`
- [ ] `EncounterRefusal` surfaces and is reported, never silently defaulted
- [ ] `offClimateMilli`, `sameSpeciesMaxMilli`, `threatWindow` become live for the first time
- [ ] Encounter selection is deterministic for a given seed

**Verification:**
- [ ] `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Encounter"`
- [ ] `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Delve"`
- [ ] `dotnet test gk-core/tests/FusionRpg.Server.Tests`
- [ ] `.\scripts\guard-actor-hub.ps1` — this module adds a *caller*, not a contributor to the
      grandfathered `BattleStatComposer` fork; must not deepen it (remediation program:
      `FUSE-battle-hub`, owed and unwritten)

**Dependencies:** T3, T5, T19
**Files:** `gk-core/src/FusionRpg.Server/DelveBattleSessionManager.cs`
**Size:** S

---

#### ✅ Task T21: `socket-combat-wiring` a — the `EquipProjector` contribution seam
- [x] **Shipped** — `0bcdbc332` — insert contributions through `EquipProjector`, `ContributionSourceIds.Insert`, §8.1 amended. On `HEAD` of `features/mega-merge`, re-checked 2026-09-18.

**Description:** Wire a socketed insert's contribution through `EquipProjector` (never a second
composer — `ApplyEquipProjection` reaps any binding outside its own `desired` set) into `ActorHub`;
file the GG-49 `ContributionSourceIds` grammar amendment.

**Acceptance criteria:**
- [ ] A socketed gem measurably changes a combat number, proven end to end: socket → deploy →
      `ActorHub.ResolveDerivedWithContributions` → the channel moved — **has never been true before**
- [ ] The contribution is attributed (insert, host item, role, socket index) under the amended §8.1
      grammar
- [ ] The contribution survives a second `MaterializeRolledEquipRuntime`
- [ ] No second `*Composer*` introduced anywhere
- [ ] An actor with no sockets resolves byte-identically to today, on both the Hub and battle paths

**Verification:**
- [ ] `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~EquipProjection"`
- [ ] `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Socket"`
- [ ] `.\scripts\guard-actor-hub.ps1`

**Dependencies:** T8
**Files:** `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Items.cs` (`ApplyEquipProjection`/`EquipProjector`),
`docs/architecture/actor-hub-ssot.md` §8.1, `gk-core/tests/FusionRpg.Data.Tests/Items/`
**Size:** M

---

#### ✅ Task T22: `socket-combat-wiring` b — withdraw, orphan, refusal
- [x] **Shipped** — see `tasks/evidence-fragments/T22.md` — the withdrawal reaper and the by-name insert refusals were already in T21; this adds the missing **Data**-level column contract (`SocketInsert_stores_a_real_insert_instance_id_and_never_an_empty_string`: filled ⇒ real id, empty ⇒ NULL, never `""`) so the todo's `~SocketInsert` Data filter selects a row. Server `~SocketInsert` 9 passed; Data `~SocketInsert` 1 passed; guards + overflow clean.
**Description:** Unequip/remove withdraws the contribution; an unresolvable insert refuses by name.

**Acceptance criteria:**
- [ ] Unequipping the host, and removing the insert, each withdraw the binding — no orphan
- [ ] `item_socket.insert_instance_id` holds a real instance for every filled socket; `""` no longer
      appears on that column in production
- [ ] An unresolvable insert refuses the socket-insert by name and writes no partial state

**Verification:**
- [ ] `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~SocketInsert"`
- [ ] `dotnet test gk-core/tests/FusionRpg.Server.Tests`
- [ ] `dotnet test gk-core/tests/FusionRpg.E2E.Tests`
- [ ] `python gk-core/scripts/guard-test-substrate.py`, `.\scripts\guard-dal.ps1`, `.\scripts\guard-single-writer.ps1`,
      `.\scripts\guard-funnel-delta.ps1`
- [ ] `python gk-core/scripts/audit-overflow.py`

**Dependencies:** T21
**Files:** `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Sockets.cs` (correct the stale "equip path reads it"
comment at `:32-33`), `gk-core/tests/FusionRpg.Data.Tests/Items/`
**Size:** S

---

#### ✅ Task T23: `durability-slice` b — workbench repair, the `Repair` op_kind
- [x] **Shipped** — see `tasks/evidence-fragments/T23.md` — `Repair` is the eleventh member of both closed vocabularies (with the §5.3 row), `RepairPolicy` rolls the destroy first (D1) and grades the restore (D2), `ItemWorkbench.Repair` + `POST /api/items/workbench/repair` drive it against the real store, and the row is **generated**: `recipegen.repair` emits `recipe.069` through the new `--emit-deterministic` write path. Three tuning publishes (materials v2, deployment-hierarchy v3/v4) with every reader switched. Server 55, Data 118, Core items 41, pytest 63, guards + overflow clean.
**Description:** The workbench-only half of `spec-item-durability-repair.md` §5: `ItemWorkbench.Repair`
following `Enhance`'s shape; `RepairPolicy.Resolve(current, max, materialCoverageMilli, tierCapMilli,
rng)`; the eleventh `MutationOpKind` **and** eleventh `CraftOperation` member (`Repair` — already
filed by `deployment-hierarchy-map.md:89`, fulfilled here); the shard-leg-at-high-rungs cost shape
matching `elevate`'s precedent. **No field touch-up** (needs `PackGrid`, unbuilt).

**Acceptance criteria:**
- [ ] `Repair` is added to both `MutationOpKind` and `CraftOperation`, under a reviewed
      `ssot-enhancement.md` §5.3 amendment — the ordinal that was reserved for it
- [ ] Workbench repair resolves via `RepairPolicy.Resolve`; material coverage below what
      `missingFraction` needs falls back to a `tierCapMilli`-capped partial result, never a refusal
- [ ] The destruction chance is rolled **before** computing the restore, on the op's own named
      stream; on destruction, `Disposition` becomes `"destroyed"` and the instance is deleted via the
      existing salvage path — never a new deletion path
- [ ] `operations.repair` prices souls+substrate+catalyst.temper at low/mid rungs, +shard at top
      rungs, matching `elevate`'s shape — ⛔ *amended 2026-09-18:* published as a **new**
      `materials.v{n+1}.json` through `gk-core/tools/tuning/publish.py` (`--add-key` for the new row), with
      `gk-core/src/FusionRpg.Server/Program.cs:343`'s reader switched **in the same commit** (parent H7) — never an in-place edit of
      `materials.v1.json`
- [ ] Replay is idempotent per `correlation_id`, exactly like `Enhance`

**Verification:**
- [ ] `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~InstanceOp"`
- [ ] `dotnet test gk-core/tests/FusionRpg.Server.Tests`
- [ ] `.\scripts\guard-dal.ps1`
- [ ] `python gk-core/scripts/audit-overflow.py`

**Dependencies:** T11
**Files:** `gk-core/src/FusionRpg.Core/Items/Mutation/MutationOp.cs`,
`gk-core/src/FusionRpg.Core/Items/Materials/CostClassMatrix.cs`,
`gk-core/src/FusionRpg.Core/Items/*/RepairPolicy.cs` (new), `gk-core/src/FusionRpg.Server/ItemWorkbench.cs`,
`WorkbenchEndpoints.cs`, `data/tuning/materials.v{n+1}.json` (published), `gk-core/src/FusionRpg.Server/Program.cs`,
`docs/architecture/item/ssot-enhancement.md`
**Size:** M — over the five-file guide; suggested build seam: land the enum amendment
(`MutationOp.cs` + `CostClassMatrix.cs` + `ssot-enhancement.md` §5.3) as its own commit, then the
executor + publish.

⚠ **Tuning-ledger note (amended 2026-09-18):** this is a `materials` revision the parent §5 ledger does
not list (its row is `T32 → T34 → SSH socket-pricing`). The ledger is a tie-break, and `publish.py`
takes `n` from disk, so whichever publish lands first takes the next number and the later one rebases —
flagged to the parent in this revision's report, not a block.

---

#### ✅ Task T24: `craft-risk-ladder` Stage 2–3 — decay past exhaustion
- [x] **Shipped** — see `tasks/evidence-fragments/T24.md` — `CraftRiskPolicy.CanDecay`/`WearFor`/`AfterWear` are real (null potential is Assured, never exhausted); `WorkbenchMutation.DurabilityCurrent` carries the decided wear and `SetDurabilityCurrentUnlocked` applies it in the craft's own transaction; the executor decides it once in `CraftWearFor`. Core `~CraftRisk|~Potential` 21 passed, Data `~InstanceOp` 16 passed, Data suite 1558 passed, guards + overflow clean. One host wire remains (the `CraftWearSource`), named in the fragment.
**Description:** ⚠ **Un-deferred by the durability pull-forward.** Past potential exhaustion, a craft
succeeds and decays `durability_current` by a flat per-mille of `max` — the same unit battle wear
uses (`ceil(durability_max × wearPerBattleMilli / 1000)`), so the two decay sources stay comparable.
Stage 3 (broken, unusable, never destroyed by wear) is already enforced by T11's at-zero filter. Stage
4 (repair-can-destroy) needs no new code here — it is inherited from T23's repair executor.

⛔ **Amended 2026-09-18 to the strengthened spec** (`spec-craft-risk-ladder.md` § Design 3, 5, Tunables):
- **R-G1: one pool, one unit, two formulas.** Craft wear is its **own** table — today the one flat key
  `craftWearPerAttemptMilli` (`deployment-hierarchy.v2.json:97`, read at `DeploymentHierarchyTuning.cs:82`,
  shipped starting value `50`) — never a shared wear block with battle's reserved `wearPerBattleMilli`.
- **The bands question is answered — they stay** (`item-map.md` *"Filed decision 2026-09-15 — ask #4"*).
  This task does not touch `EnhancePolicy`'s bands; the old "remove the bands **or** file a decision"
  bullet is closed by the filed decision and struck below.
- **Tuning:** the key already exists, so T24 needs **no publish** to ship the mechanism. The
  `deployment-hierarchy` **v3** in the parent §5 ledger lands with this task only if T24 changes the
  table (e.g. a second craft-wear input becoming a `craftWear` object); otherwise it lands with T49's
  one-pass balance. Either way: `publish.py`, and `gk-core/src/FusionRpg.Server/Program.cs:219` + `DeploymentHierarchyTuning.cs:6`
  switched in the same commit (H7).
- **Protect hook:** the decrement is computed in one place so T43 can suppress it for a debited
  `assurance.protect` — no second decay path.

**Acceptance criteria:**
- [ ] While potential remains, every craft succeeds untouched (T10's behaviour, unchanged)
- [ ] Past exhaustion, a craft succeeds **and** decays durability by `craftWearPerAttemptMilli`, in
      battle wear's unit
- [ ] Durability floors at 0; the item is unusable (excluded from assignments) but **never destroyed
      by crafting** — `Disposition` stays `"owned"`, proven by driving durability to zero purely
      through crafting
- [ ] No destroy outcome is emitted on the craft path; `EnhanceOutcome` gains no member
- [x] ~~Enhancement's Safe/Risk bands are removed, **or** an explicit, filed decision records why they
      stay~~ — closed by the filed decision (`item-map.md`, 2026-09-15: the bands stay; one vocabulary
      **per question**). This task leaves the bands untouched
- [ ] `CraftRiskPolicy.CanDecay`'s `false` stub (`CraftRiskPolicy.cs:25`) is replaced, and craft wear
      reads only the craft-wear key — never `wearPerBattleMilli`

**Verification:**
- [ ] `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~InstanceOp"`
- [ ] `dotnet test gk-core/tests/FusionRpg.Core.Items.Tests --filter "FullyQualifiedName~CraftRisk"`
- [ ] `.\scripts\guard-actor-hub.ps1`, `.\scripts\guard-dal.ps1`, `python gk-core/scripts/guard-test-substrate.py`
- [ ] `python gk-core/scripts/audit-overflow.py`

**Dependencies:** T10, T11
**Files:** `gk-core/src/FusionRpg.Core/Items/Materials/CraftRiskPolicy.cs`,
`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.InstanceOps.cs`, `gk-core/tests/FusionRpg.Data.Tests/Items/`,
`gk-core/tests/FusionRpg.Core.Tests/` (CraftRisk); `gk-core/data/tuning/deployment-hierarchy.v3.json` +
`DeploymentHierarchyTuning.cs` + `Program.cs` **only if** the table changes (see above)
**Size:** M

---

#### ✅ Task T25: `rarity-promotion` a — item-side rung arithmetic + the `op_kind` ask
- [x] **Shipped** — see `tasks/evidence-fragments/T25.md` — `Items/RarityLadder` gains `RungCount` (derived), `RungIndexOf`, `IsTopRung` and `OneRungAbove` (throws at the top, never clamps); `MutationOpKind.Promotion` is the twelfth member with no new `CraftOperation` (the shipped `elevate` rows price it); `ssot-enhancement.md` §5.3 gains `promotion` **and** the drifted `socket-imbue` row; `ssot-power-scale.md` §10.1 gains row 28 for the rung-keyed cost coefficient. Core 67 passed, Server 55, Data 16, guards + overflow clean.
**Description:** `Items/RarityLadder` has no `IsTopRung`/`OneRungAbove`/`RungCount`. Build the
item-side rung arithmetic (mirroring `CreatureRarityLadder`'s shape without sharing its type), and
file the promotion `MutationOpKind` amendment — the **twelfth** member, since T23's `Repair` now
claims the eleventh.

**Acceptance criteria:**
- [ ] `Items/RarityLadder` gains `IsTopRung`/`OneRungAbove` over the string-keyed, 10/20-ordinal item
      ladder
- [ ] `MutationOpKind` gains exactly one new member (promotion), under a reviewed
      `ssot-enhancement.md` §5.3 amendment landed in the same commit
- [ ] The same amendment adds the missing `socket-imbue` row to §5.3's table (a pre-existing drift
      found this session — `MutationOp.cs:42-47` mints it, §5.3 never listed it)
- [ ] The `promoteCostSoulsMilli` cost ladder's `ssot-power-scale.md` §10 row is filed (shared filing
      with `species-cost-shaping`'s T32, whichever lands second confirms the other's row)

**Verification:**
- [ ] `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~RarityLadder"`
- [ ] `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Mutation"`

**Dependencies:** T10, T23
**Files:** `gk-core/src/FusionRpg.Core/Items/RarityLadder.cs`,
`gk-core/src/FusionRpg.Core/Items/Mutation/MutationOp.cs`, `docs/architecture/item/ssot-enhancement.md`,
`docs/architecture/power/ssot-power-scale.md`
**Size:** M

---

#### ✅ Task T26: `rarity-promotion` b — the executor + the card mark
**Description:** Copy the shipped `ItemWorkbench` verb pattern; surface `promoted_from_ordinal`.
⚠ **Owner decided 2026-09-13 that `species-cost-shaping`'s per-rung multiplier applies to `elevate`
too** (`spec-rarity-promotion.md` Open question 2). That does **not** make T32 (Phase 4) a dependency
of this task: `elevate`'s cost must resolve through the **same shared cost-resolution function** every
other verb uses (never a bespoke elevate-only calculation), so when T32 wires the species multiplier
into that shared function, `elevate` picks it up automatically with no further change here. This
task's own job is only to confirm it did **not** write a private cost path.

**Acceptance criteria:**
- [x] All ten authored `elevate` recipes execute end to end
- [x] Promotion is provably additive: every affix survives identically
- [x] `promoted_from_ordinal` is written, correct across multiple promotions, visible on the card
- [x] Promotion has no private failure chance (defers entirely to `craft-risk-ladder`); top-rung
      promotion refuses cleanly, never reaching the ladder's throw
- [x] `ItemWorkbench` exposes this as its own verb, in the shape of the shipped ones, with a POST
- [x] `elevate`'s cost resolves through the shared cost-resolution function, not a bespoke
      calculation — the hook T32 needs later already exists

**Verification:**
- [x] `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~InstanceOp"`
- [x] `dotnet test gk-core/tests/FusionRpg.Server.Tests`
- [x] `dotnet run --project gk-forge/tools/ItemSeedValidator` (pre-existing corpus drift, unrelated; its test project 83/83 green)
- [x] `.\scripts\guard-dal.ps1`, `.\scripts\guard-actor-hub.ps1`

**Dependencies:** T25
**Files:** `gk-core/src/FusionRpg.Server/ItemWorkbench.cs`, `WorkbenchEndpoints.cs`,
`gk-core/tests/FusionRpg.Data.Tests/Items/`
**Size:** M

---

### Checkpoint — Phase 2
- [x] All ten authored `elevate` recipes execute end to end (T26)
- [x] A socketed gem measurably changes a combat number, proven through `ActorHub` (T21–22)
- [x] `craft-risk-ladder` is complete (Stages 1–4, T10/T24) — the hard-stop risk from revision 1 is
      resolved
- [x] `guard-actor-hub.ps1`, `guard-dal.ps1` green — no second composer anywhere in Phase 1–2
- [x] `themes.v2.json` published; 844 bound set entries unaffected
- [ ] **Review with owner before Phase 3**

**Five of six boxes closed 2026-09-20 by `species-gear-chain` wave 1** — each re-run that session,
numbers in `tasks/evidence-fragments/SGCCP2.md` (Server `~Every_authored_elevate` 1 passed; Core
`~EquipAtomSourceIdTests` 4 passed incl. a NEW test that drives an `insert:` contribution through
`ActorHub.ResolveDerivedWithContributions` — channel 5 → 50 — plus Data `~EquipProjection` 5 passed;
Core `~CraftRisk|~Potential` 21 passed; both guards OK; 904 themes rows in v1 and v2 with 0 keys
renamed and all 844 bound entries resolving). The sixth box is the owner review and stays open.

---

## Phase 3

#### ✅ Task T27: `set-species-binding` a — schema + forward emission — **ruled 2026-09-21 (owner): build the set-planning system**
**Description:** Add `speciesId`/`setClass` to the set entry schema; extend `set-charm-gen` to emit
both going forward.

**Acceptance criteria:**
- [x] ⛔ Every set entry carries `speciesId` (a real id or explicit absent) — **built,
      proven** — and `setClass` — **ruled 2026-09-21 (owner): build the set-planning system.** The
      2026-09-10 topology classes are the target, not a dead design: their three role-count shapes are
      authored into a real set-planning system and the 910 shipped sets are brought onto it. — the four
      commits delivered exactly the spec's rows: S1 `be608027`, S2 `5209971e`, S3 `b7463f6d`, S4 `ca790b44`,
      and the manager's rows that carry that work are each backed with their commit + fragment — T52
      (`e91152ea`, `tasks/evidence-fragments/T52.md`), T53 (`587c1d7d`, `tasks/evidence-fragments/T53.md`),
      T54 (`0f607962`, `tasks/evidence-fragments/T54.md`).
      ⛔ **RE-OPENED 2026-09-21 (manager ruling): a closed row may not rest on a corpus that fails the
      corpus gate.** `ItemSeedValidator` reports **910 errors, all 910 `unknown key 'setClass'`**, on this
      corpus, so this box is unchecked until that is green. The cause is proved single-variable, not
      inferred: the identical corpus with only those 910 fields removed (temp seed root, never the repo)
      is `errors 0 — PASS`, so the rejection is the C# validator's own allowed-field list
      (`gk-forge/tools/ItemSeedValidator/Registries/KindCatalog.cs:112` omits the field while
      `gk-forge/tools/seedsmith/seedsmith/adapters/items/kinds.py:87` declares it) and **no generator change can clear it** — the emitter is
      *required* to write the field by T53's own criterion. The one-field fix is filed as **T56**; this
      row, and T52/T53/T54, stay open until it lands. Evidence: `tasks/evidence-fragments/T56.md`.
- [x] `SetEvaluator` behaviour is unchanged (class-agnostic today, stays so)

**Verification:**
- [x] `$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/test_items_adapter.py -q`
      (confirm this test's pre-existing failure baseline first)
- [x] `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Set"`

**Dependencies:** T16
**Files:** `gk-forge/tools/seedsmith/seedsmith/adapters/items/setgen/`
**Size:** S

---

#### Task T28: `set-species-binding` b — deterministic backward repair + runtime import
**Description:** Repair the existing 910 entries, reading `themes.v2.json`'s `speciesId` field as the
primary join (case-normalising cross-check against the `themeKey` suffix parse), persisting the
runtime catalog's spelling. ⚠ **Expanded scope after the coverage audit found the module's own
Objective — "make the field queryable" — needs the C# runtime side, which the original task list
omitted:** the `FusionRpg.Data` set-import path, and `ItemSeedValidator`'s closure check.

**Acceptance criteria:**
- [x] Every `creature.*` themeKey resolves, or the run fails naming the unresolved key
- [x] `build.*`/`theme.*` keys (no species) get an explicit absent value, never a guess
- [x] `speciesId` is persisted in the **runtime catalog's spelling** (lower-case, matching
      `CreatureSpeciesCatalog`), not the PascalCase generated-corpus spelling
- [x] `FusionRpg.Data`'s set import reads and persists the new field — the field is queryable at
      runtime, not just on disk
- [x] `ItemSeedValidator` asserts every non-absent `speciesId` resolves in `CreatureSpeciesCatalog`
      (read via the same theme registry `species_repair.py` joins against — see evidence fragment)
- [x] No set bonus magnitude changes — proven by a raw diff (`members`/`thresholds` byte-identical
      across all 844 changed files; those are the only fields `SetEvaluator` reads)
- [x] The repair is idempotent and deterministic (byte-identical on a second run); no model call
      anywhere on this path

**Verification:**
- [x] `cd gk-forge/tools/seedsmith; python -m seedsmith check gk-data/packs/fusion/data/seed/items --adapter items`
- [x] `dotnet run --project gk-forge/tools/ItemSeedValidator`
- [x] `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~ItemSet"`

**Dependencies:** T27, T16
**Files:** `gk-forge/tools/seedsmith/seedsmith/adapters/items/` (new repair pass), `gk-data/packs/fusion/data/seed/items/sets/**`
(regenerated), `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.ItemSets.cs`, `gk-forge/tools/ItemSeedValidator/Program.cs`
**Size:** M

---

#### ✅ Task T29: `creature-drop-tables` a — E2 material-shelf credit
- [x] **Shipped** — see `tasks/evidence-fragments/T29.md` — `PersistLootUnlocked` now credits a drawn `Material` entry to the shelf and a `Currency` `souls` entry to the balance, in the caller's transaction and after the replay early-return; the id is parsed once, checked (`loot.credit-player-id-not-numeric`). Data 1554 passed, Server 554 passed, guards + overflow clean.
**Description:** A drawn `Material` entry is drawn and the grant emitted, but the shelf is never
credited — 2–3 Data files + tests, including the `PersistLootUnlocked`/credit-helper `string`/`long`
player-id type mismatch.

⛔ **Amended 2026-09-18 — the credit site was named wrong** (`spec-creature-drop-tables.md` § Design 1,
strengthen pass): `Material`/`Currency` grants are added to `manifest.Grants` directly and **never
reach `LootMintAt.Mint`** (its own doc comment, `LootMintAt.cs:44-51`). The credit belongs in
`PersistLootUnlocked` (`RpgStore.Loot.cs:567`) alone: **after** the `(player_id, correlation_id)` early
return (`:576-584`) so a retried resolution credits nothing twice, and **inside** the caller's
transaction so the drop-log row and the credit commit together (the Delve path's `CloseDelve` owns the
transaction, `RpgStore.Delve.cs:707`).

**Acceptance criteria:**
- [ ] A drawn `Material` entry credits the shelf end to end; a replayed correlation id leaves the shelf
      unchanged; a thrown credit rolls the drop-log row back with it
- [ ] The `string` drop-log player id is converted to the credit helpers' `long` **once, checked** — a
      non-numeric id refuses the whole persist by name, never credits a default row
- [ ] The shipped drop-rate floor (`drop-rate-floor.v1.json`) is consumed; no second floor introduced

**Verification:**
- [ ] `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~Loot"`
- [ ] `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Loot.cs,<test file> -Session <id>`
- [ ] `.\scripts\guard-dal.ps1`

**Dependencies:** T18
**Files:** `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Loot.cs` (`PersistLootUnlocked`), the credit helper it
calls (`src/FusionRpg.Data/Sqlite/RpgStore.*`), `gk-core/tests/FusionRpg.Data.Tests/Items/`
**Size:** M · *(spec: `creature-drop-tables`)*

---

#### Task T30: `creature-drop-tables` b — E1 the ninth source kind + paired arm
**Description:** Add a ninth `source_kind` for a creature kill, its authored tables in
`gk-data/packs/fusion/data/seed/loot/` (the **runtime** corpus — not `droptablegen`'s output tree,
`gk-data/packs/fusion/data/seed/items/drop-tables/`), and the paired `LootCorrelation.Derive` arm. ⚠ **Scope decided
2026-09-13 (owner):** authored tables carry **both** `Material` and `Equipment` entries — not
materials-only as the spec originally recommended. `DropEntryKind.Equipment` is already a built mint
arm (`LootMintAt.cs:77-87`); no new equipment-roll mechanism is built here.

⛔ **Amended 2026-09-18 to the strengthened spec:** `DropEntryKind` has **ten** members (`Relic` was
added since — `DropTableModel.cs:20-32`), still closed, still gaining none here. The source-kind list
lives at `DropTableValidator.cs:52-59` with its own warning that each kind *"also gains a
`LootCorrelation.Derive` arm — neither list is complete without the other"*: both land in one commit.
`gk-data/packs/fusion/data/seed/loot/**` is **authored** (item module 11), validated by `DropTableValidator`, not generated —
the no-hand-edit rule does not bind it; generated input lives in `gk-data/packs/fusion/data/seed/items/drop-tables/`.
**Trophy entries are not in this task** — their persisted shape is T30b and their content is T34c.
The ninth `source_kind` is an ask-first closed-vocabulary change: file it as a row in the `drop-tables`
owning map in the same commit (the plan's approval is the answer on record; no pre-work gate).

**Acceptance criteria:**
- [x] A ninth `source_kind` id exists in the closed vocabulary **and** its `LootCorrelation.Derive` arm,
      in one commit, with authored per-rung tables in `gk-data/packs/fusion/data/seed/loot/` carrying `Material` and
      `Equipment` entries (*1 generic + 3 commons + 1 rare gate*, per-million weights — never per-mille)
- [x] Kill attribution keys on a source the expedition/delve/wild path supplies — not the lawn, where
      `KillerActorKey` carries nothing
- [x] No new material id and no new `DropEntryKind` member; every table id resolves; every
      `source_kind` is in the closed vocabulary (contract test, not a table count)

**Verification:**
- [x] `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~DropTable"`
- [x] `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~Loot"`
- [x] `.\scripts\verify-change.ps1 -Paths <every touched path> -Session <id>`

**Dependencies:** T18, and at least one of {T6, T7, T20} (all three shipped)
**Files:** `gk-core/src/FusionRpg.Core/Items/Drops/DropTableValidator.cs`, `LootPipeline.cs`,
`gk-data/packs/fusion/data/seed/loot/**` (new tables), `tests/FusionRpg.Core.Tests/Items/Drops/`
**Size:** M · *(spec: `creature-drop-tables`)*

---

#### ✅ Task T31: `creature-drop-tables` c — E3a shard-by-rung at plan time, shared with the equipment arm
- [x] **Shipped** — see `tasks/evidence-fragments/T31.md`. The 2026-09-20 regression row (the E2E assertion pinned `shard.chaff` while the resolver mints the planned wave's rung shard) is fixed in the same commit as this line: the expectation is derived through the resolver's own `PlannedRungFor` + `CreatureYieldTuningHub.ShardFor`.
**Description:** Replace `isBoss ? ShardRare : ShardCommon` with a lookup on the killed species' own
rarity rung, computed at plan time from the planned wave's species — preserving manifest determinism.
**The same rung-derived `theta` input feeds `Equipment`-kind entries' `thetaContent`** (T30's scope
addition) — one derivation, two consumers, not two mechanisms.

⛔ **Amended 2026-09-18:** the rung → shard map lives in **new `gk-core/data/tuning/creature-yield.v1.json`,
owned by this module alone** (strengthen pass — it was "shared with `species-materials`, whoever
first"; `species-materials` now reads nothing from it). A ten-row identity map is a legal first value;
a missing rung is a load rejection (T5). Core never reads the file — the server host loads and injects
it (T7.2), in the same commit that creates it (H7's spirit: no dark file). This is the file's `v1`
creation (parent §5, last row); any later change is a `v2` publish through `publish.py`.

**Acceptance criteria:**
- [x] The shard a creature yields follows its rung, not `isBoss`; an `Equipment`-kind creature drop
      mints via `LootMintAt.cs:77-87` with `thetaContent` from the same species-rung input — proven with
      a real minted, saved instance
- [x] Expedition manifests stay byte-identical for a given seed, before and after — a regression test;
      T34c re-asserts it **with** trophy groups present (strengthen pass item 3)
- [x] `creature-yield.v1.json` is loaded by the host with a throw-on-missing-rung parser; a per-species
      yield distribution report is **printed** for both entry kinds, never asserted

**Verification:**
- [x] `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Expedition"`
- [x] `.\scripts\verify-change.ps1 -Paths <every touched path> -Session <id>`
- [x] `python gk-core/scripts/audit-magic-numbers.py --targets M1`

**Dependencies:** T30
**Files:** `gk-core/src/FusionRpg.Core/Expeditions/ExpeditionResolver.cs`, `gk-core/data/tuning/creature-yield.v1.json`
(new), a strict loader beside it in Core (new), `gk-core/src/FusionRpg.Server/Program.cs` (host injection),
`tests/FusionRpg.Core.Tests/Expeditions/`
**Size:** M (was S — the tuning file and its host wiring moved in) · *(spec: `creature-drop-tables`)*

- [x] **T31 regression — fixed 2026-09-20 (this session).** `ExpeditionE2ETests.Full_loop_dispatch_force_due_collect`
      asserted a pinned `shard.chaff` while `gk-core/src/FusionRpg.Core/Expeditions/ExpeditionResolver.cs:101` mints
      `CreatureYieldTuningHub.ShardFor(PlannedRungFor(setup.Wave))` — the shelf held `shard.fused`.
      The assertion now keys on the planned wave's rung (`ExpeditionResolver.PlannedRungFor(WaveCatalog.Get("rift-skirmish").Enemies)`
      then `CreatureYieldTuningHub.ShardFor`), proven red→green: `Failed 1` → `ExpeditionE2ETests` 6 passed,
      `verify-change` e2e module 231 passed. See `tasks/evidence-fragments/T31.md`.
      **Residual (reported, not hidden):** the `rift-skirmish` id restates the resolver's *private* tier chain because
      `gk-core/src/FusionRpg.Core/Expeditions/ExpeditionResolver.cs` is outside this lane's fence — moving `WaveChain`
      to an internal accessor is a `species-gear-chain` follow-up, not a defect in the fix.

Merge note (2026-09-21, lane sgc-2): the bullet above is the fixed state as it landed on the head. An earlier lane fixed the same regression its own way; that record is kept in tasks/evidence-fragments/T31.md under its own 'Merge note', which also says why the head's assertion is the stronger one (it derives the expected shard through the resolver's own two calls).

---

- [x] **T31 regression — `ExpeditionE2ETests.Full_loop_dispatch_force_due_collect` — CLOSED 2026-09-21.**
      `gk-core/tests/FusionRpg.E2E.Tests/ExpeditionE2ETests.cs:90` still asserts the battle tick drops
      `shard.chaff`; `gk-core/src/FusionRpg.Core/Expeditions/ExpeditionResolver.cs:101` now mints
      `CreatureYieldTuningHub.ShardFor(PlannedRungFor(setup.Wave))`, and this summon's species rung is
      `fused`, so the real response is `[{"materialId":"shard.fused","qty":1}]`. Reproduced
      deterministically: `dotnet test gk-core/tests/FusionRpg.E2E.Tests --filter "FullyQualifiedName~ExpeditionE2ETests.Full_loop_dispatch_force_due_collect"`
      → `Failed: 1, Passed: 0`. The assertion must key on the planned wave's rung (or the map's value),
      not a pinned `shard.chaff`; the E2E file was not in T31's `Files:` list. **Not fixed by the QA lane
      — `tests/**` is outside its allowed paths.** **Fixed 2026-09-21:** the assertion now reads the
      rung map through `CreatureYieldTuningLoader` and requires exactly one dropped material to be one
      of the map's OWN values with `qty == 1`, so it moves with a `publish.py` rung compression instead
      of re-breaking on it. Reproduced first-hand against the legacy assertion (`Failed: 1, Passed: 0`,
      collection `[{"materialId":"shard.fused","qty":1}]`) and green (`Passed: 1`) with the fix;
      evidence: `tasks/evidence-fragments/T31.md`.

---

#### Task T37: `item-upgrade-tree` a — the executor, armour successor edge — **ruled 2026-09-21 (owner): author the per-base-type edges**
**Description:** ⚠ **Un-deferred 2026-09-13** — see T35/T36. An item-typed cost line, a
consume-and-replace `output_kind`, the twelfth `MutationOpKind` member and eleventh
`CraftOperation` member (ask-first, closed enums — file both amendments in the same commit), the
armour class-ladder successor edge, and the two mandatory rules affix-pool legality demands: the
successor's affix set must be legal on its own pool (refuse, never drop or re-tier), and the implicit
change is presented on the card **before** the input is consumed.

**Acceptance criteria:**
- [ ] ⛔ An armour piece upgrades to the next rung within its own `(ladder, frame)`, consuming the
      input — **ruled 2026-09-21 (owner): author a per-base-type `successorOf` edge; never derive it
      from the class ladder.** The corpus analysis below is the cause the ruling rests on. Design §1's own claim ("armour reads the class
      ladder's `rung` — one lookup function") does not resolve to a UNIQUE successor container: the
      REAL corpus has no per-base-type edge distinguishing which of several same-`(role, frame,
      class, band)` variants a specific input becomes. Verified: humanoid `footing` has 6 `cloth` +
      6 `leather` base types whose `(implicit.family, powerBand)` pairs REPEAT within each class (no
      attribute or position bijection), and `band` does not track `rung` consistently either —
      humanoid `core-guard` variant counts per `(class, band)` are `cloth-a=7, cloth-b=1, leather-a=9,
      leather-b=7, plate-a=12, plate-b=15, scale-b=6`, ruling out any general derived rule (not just
      footing's own coincidental 6/6/6/6). The Tunables table already names this as **authored
      content, not a formula** — `classes.v3.json` is `frozen: true` with `minCompatibleVersion`
      semantics, and the spec's own Boundaries mark **any change to it ask-first**. Resolving this
      needs the owner to either author real successor edges or rule on a deterministic executor-side
      pick — not an implementer's call to invent unilaterally against a frozen, ask-first registry.
- [ ] Every affix carries across identically **and** is legal on the successor's `affix_pool_tag** —
      an illegal combination refuses, it does not launder or re-tier
- [ ] The implicit change is shown on the card before the input is consumed — refuse-never-warn,
      matching the requirement-refusal posture
- [ ] A requirement the owner cannot meet (via T35/T36's `RequirementTrialEvaluator`) refuses, and
      consumes nothing — proven byte-identically
- [ ] The card presents the result as a chassis carrying its own identity, not the named successor
- [ ] Hub bindings against the consumed instance are withdrawn via the existing machinery
- [ ] No reroll, no private failure chance (defers to `craft-risk-ladder`), no hard ceiling

**Verification:**
- [x] `dotnet test gk-core/tests/FusionRpg.Core.Items.Tests --filter "FullyQualifiedName~ItemUpgrade"` (⚠ *project corrected 2026-09-23, lane sgc-6 — the Core split moved every `ItemUpgrade*` test out of `FusionRpg.Core.Tests`, where the old line selected **nothing**; measured now: **32 passed, 0 failed**)
- [x] `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~InstanceOp"` → measured 2026-09-23 (lane sgc-6): **Passed! Failed: 0, Passed: 16, Skipped: 0, Total: 16**
- [x] `dotnet test gk-core/tests/FusionRpg.Server.Tests` → measured 2026-09-23 (lane sgc-6, `--no-build` after a 12s build): **Passed! Failed: 0, Passed: 859, Skipped: 0, Total: 859** in 3m10s — so the recorded `Failed: 1, Passed: 766` was STALE at this head (the foreign combination-corpus failure has since been fixed, and 93 more tests exist). ⚠ Without `powershell` on `PATH` the same run reports **Failed: 2, Passed: 857**: both are `Win32Exception: An error occurred trying to start process 'powershell' … The system cannot find the file specified` from `RealRunCollectorTests.cs:154`'s bare `FileName = "powershell"` — a PATH artifact, not this row's, and filed as SGC5-F5
- [x] `.\scripts\guard-dal.ps1`, `.\scripts\guard-actor-hub.ps1` → measured 2026-09-23 (lane sgc-6): `DAL GUARD OK — no SQLite/SQL outside FusionRpg.Data` and `ACTOR-HUB GUARD OK`
- [ ] `dotnet run --project gk-forge/tools/ItemSeedValidator` → ⛔ still RED on exactly T37's 498 authored `successorOf` rows (`SameStageReference`); the ready patch is `tasks/evidence-fragments/T37-validator-successor-edge-exemption.patch` and `gk-forge/tools/ItemSeedValidator/**` is a denied path for this lane. Unchanged.

**Dependencies:** T26, T24, T36
**Files:** `gk-core/src/FusionRpg.Core/Items/Mutation/MutationOp.cs`,
`gk-core/src/FusionRpg.Core/Items/Materials/CostClassMatrix.cs`,
`gk-core/src/FusionRpg.Core/Items/*/ItemUpgradePolicy.cs` (new), `gk-core/src/FusionRpg.Server/ItemWorkbench.cs`,
`WorkbenchEndpoints.cs`, `docs/architecture/item/ssot-enhancement.md`
**Size:** M

⚠ *Amended 2026-09-18:* if the item-typed cost line adds a `materials` `operations` row
(`upgradeCostSoulsMilli`), it is a new `materials.v{n+1}.json` through `publish.py`, landing **after**
T34d in the map's order, with `gk-core/src/FusionRpg.Server/Program.cs:343` switched in the same commit — and it owes its
`ssot-power-scale.md` §10 row first.

**Progress 2026-09-21 (wave 1, slice 1) — the pure executor landed; the row stays OPEN.**
`gk-core/src/FusionRpg.Core/Items/Mutation/ItemUpgradePolicy.cs` + `tests/.../ItemUpgradePolicyTests.cs`
(14 passed) implement the one successor lookup over the **authored per-base-type edge** the owner ruled
on 2026-09-21 (`d12dcb90`) — never a class-ladder derivation — with the spec's three mandatory rules:
affix-pool legality refuses rather than relabels (§2a Rule 1), both implicits are named in the plan (§2a
Rule 2), and the requirement is checked before any consume (§4). Six named refusals
(`upgrade.no-successor`, `.top-rung`, `.standard-refused`, `.successor-unknown`, `.successor-not-next-rung`,
`.successor-not-same-ladder-and-frame`); no RNG, so no private failure chance. Remaining for this row:
the 13th `MutationOpKind` / 12th `CraftOperation` member **with** the verb that emits it
(`ItemWorkbench.Upgrade` + `POST /api/items/workbench/upgrade`), the item-typed cost line, the authored
armour edges (generator input + regeneration), the `upgradeCostSoulsMilli` publish, the Hub withdrawal,
and the FE card mark. ⛔ The `ssot-enhancement.md` §5.3 row is outside this lane's fence — routed in the
lane report; `tasks/item-todo.md` is claimed by an active session, so no row was written into it.
Evidence: `tasks/evidence-fragments/T37.md`.

**Erratum 2026-09-21 (slice 3 recon) — Rule 1 has no field behind it.** The spec's affix-legality rule
names `affix_pool_tag`, which `ssot-item-categories.md:295` declares a real `TEXT NOT NULL` column with
worked values at `:532`/`:572`/`:599` — but **no shipped base-type row carries it** and **no affix-family
row carries it** (families carry `roles`, a per-role allow-list, plus `powerBand`/`frames`/`side`). So the
production executor cannot evaluate Rule 1 from the corpus today; it is proven only against caller-supplied
data. The spec now carries the erratum with the two ways out (emit the column, or re-express the rule over
`role`/`class` + each family's `roles` allow-list). **This is a design decision owed before slice 3's
verb can honestly claim production-enforced affix legality**, alongside the `WorkbenchMutation`
consumed/produced-instance gap.

**Design 2026-09-21 (slice 3, step 1 — the manager ruled the design lands in this row's own spec).**
`spec-item-upgrade-tree.md` now carries § *The executor's consume-and-replace seam*, which settles the
part the corpus/tuning/store shapes had to decide: the cost is the input instance (on the mutation, not
a cost line) plus souls from `upgradeCostSoulsMilli`; a new `RpgStore.TryUpgradeAndApply` sits beside the
existing `TrySpendSocketInsertAndApply` (one transaction: op row for the consumed instance → salvage-shaped
disposition → `SaveInstanceUnlocked` for the successor → the successor's `item_generation` row → successor
id as the outcome ref); replay/idempotence and Hub withdrawal are inherited from the existing replay
short-circuit and withdraw-on-absence machinery; the successor's container comes from the one container
builder. The same commit **resolved the Rule 1 erratum** by choosing option 2 (legality reads the
affix-family `roles` allow-list against the successor's role/frame — the drop path's own filter) with the
`affix_pool_tag` column left as one injected-predicate swap away. Implementation follows against this
design; the row stays open until the enums, verb, endpoint, publish and both doc rows land.

**Progress 2026-09-21 (slice 3, criterion 6 — a real defect found by a Data probe and fixed).** A new
`ItemUpgradeStoreTests` case assigns a projecting host to a specimen, reconciles (`MaterializeRolledEquipRuntime`),
upgrades it, and reconciles again. It FAILED first: the consumed instance's binding SURVIVED, because the
assignment still named the consumed instance, so the projection's own `desired` set kept it and the
withdraw-on-absence reaper held a live binding on a **destroyed** item (which would go on composing its atoms).
`TryUpgradeAndApply` now clears the consumed instance's rows from `rpg_item_assignment` and
`rpg_player_item_assignment` in the same transaction, and the EXISTING reconcile withdraws by absence — no
second withdrawal path. ⚠ Re-pointing the loadout at the successor is a UX decision nobody has ruled on and is
deliberately not invented. The test now passes (4/4 in the file), so criterion 6 is proven rather than assumed.

**Progress 2026-09-21 (slice 3, final step — the verb proven through its endpoint).**
`gk-core/tests/FusionRpg.Server.Tests/ItemUpgradeEndpointTests.cs` stands up its own app (the shared workbench
fixture deliberately does not wire `affixFamilyRoles`/`forgeMintCells`, and wiring them there would break
the forge refusal its own test asserts) and POSTs `POST /api/items/workbench/upgrade`: 3 passed — the
input is consumed and a DIFFERENT instance comes back wearing the authored successor chassis with the
consumed instance's own atoms; the op is recorded against the consumed item and the row is not deleted;
a replayed correlation is idempotent and spends once. Two closed-vocabulary pins were updated where the
T37 ruling authorizes growth (`MaterialVocabularyTests` twelve verbs, `RerollPolicyTests` thirteen op
kinds, plus `MaterialCorpusTests` and `ClosedVocabularies_gainZeroMembers`). Two tunings published with
every reader switched: `materials.v5` (`operations.upgrade` souls 80/rung) and `deployment-hierarchy.v5`
(`potentialCostPerVerb.upgrade = 1`). ⚠ Disclosed wart, asserted as-is in the endpoint test rather than
papered over: a REPLAYED response names the consumed instance (the op ledger's own key), because
`AppendMutationOpUnlocked` carries no output ref — a follow-up should record the produced id.

**Progress 2026-09-21 (slice 3, step 2 — the Core decision layer, no vocabulary member).** The
executor's decision layer now matches the design: `ItemUpgradePolicy.Decide` takes an injected
`IAffixLegality` (`PoolTagLegality` as the historical default, **`RoleAllowListLegality`** as the
production rule reading each affix family's `roles` allow-list), and the ladder/rung shape checks run
**only for callers that declare rung data** — the runtime cannot read a class or band
(`RpgStore.GetBaseType` returns frame+role), so production passes none and is never asked to invent
one. `ItemUpgradeNode` gained the runtime-readable `Role`. `ItemUpgradeEdges` landed: the pure parser +
hub for `successor-edges.v1.json` (empty table legal; missing/non-object `edges`, empty ids and
self-edges are named rejections; `EdgeFor` returns null for the ordinary unauthored case). 23 tests in
`ItemUpgradePolicyTests`. ⛔ **`MutationOpKind.Upgrade` / `CraftOperation.Upgrade` are deliberately NOT
in this step**: `MaterialCorpusTests` pins that the tuning prices every operation, so the members land
with the publish and the verb that emits them, exactly as the ruling requires. Verify-change on these
paths: EXIT=0, Core 15075 passed / 0 failed, Guard.Tests 4 passed, doc-citations 30 citations 0 HIGH.

**Design refinement 2026-09-21 (slice 3, step 3 — found by reading the container builder).**
`EquipmentContainerBuild.From` returns a chassis and its POOL (tier range from the grant's
`MinTier`/`MaxTier`), not an item's rolled affixes — which is right for a drop and wrong for an upgrade,
because letting that pool decide the successor's affixes IS the reroll §2 forbids. The spec now states
the rule the implementation will follow: the executor synthesizes the `LootGrant` for the successor
chassis (BaseTypeId/Frame/Role), takes the container from `From`, and gives the successor
`InstanceRow.Atoms` the CONSUMED instance's own atom list, unchanged. Remaining for the row is then one
commit: enum members + the `operations.upgrade` publish (which `MaterialCorpusTests`' all-operations pin
requires) + the Data method + the verb and endpoint + both doc rows + tests.

Merge note (2026-09-21, lane sgc-2): the section above is lane sgc-1's executor progress -- the manager routed the executor half there (src/** fence). The section below is this lane's in-fence half: the spec erratum that recorded the owner ruling and decided the field's home. The head's spec text supersedes the erratum's wording and keeps its substance (one successor source, an authored edge, zero rows authored, no classes.v*.json change).

**Defect + fix 2026-09-21 (lane sgc-1) — the preview quoted a price the commit would refuse.** Writing the
missing-leg test exposed a divergence by contrast: with `operations.upgrade`'s souls leg removed, the VERB refused
`upgrade.tuning-missing-souls-leg` while the PREVIEW answered `ok` with a 0-soul price. The parity test was written
first and failed ("Assert.False() Failure — Expected: False, Actual: True"), then the check moved into the shared
`DecideUpgrade` path so both sides refuse the same way by construction, and the verb's duplicate check was removed
(it read the leg directly, with a comment naming what proves it present). **13 passed** in the file.

**Coverage 2026-09-21 (lane sgc-1) — the verb's four infrastructure refusals now have tests.** `grep` for
each `upgrade.*` code showed `legality-unavailable`, `container-unavailable` and `tuning-missing-souls-leg`
covered by **zero** test files, and the verb's own `successor-unknown` path not exercised at all. Each is a
branch that exists so a host with an unwired input refuses BY NAME instead of guessing, so each now has a case
in `ItemUpgradeEndpointTests`: a bench without the affix role map, a bench without the container lookups, a bench
over a tuning whose `operations.upgrade` row has its souls leg removed (the row is required, the leg optional),
and an edge naming a base type the store never imported. All four assert the named code AND that nothing was
written (no op row, instance intact): **12 passed** in the file. Verify-change over the path: Server.Tests
`Failed: 1, Passed: 766, Total: 767`, the single failure being the head's foreign combination-corpus case.

⚠ **Blocked-reason correction 2026-09-21 (lane sgc-1).** The blocked entry recorded for this row lists
"authored armour edges (edges rows 0) and the FE card mark" with "ItemSeedValidator red is T56". Two of those
three are no longer true, measured today: the **FE card mark shipped** (`UpgradeSwapLine` + the Upgrade section
in `Workbench.tsx`, ff19d959, and the consumed-piece notice f06f85b3), the **validator now PASSES** (T56 landed:
3957 entries / 1013 files / 2591 warnings, zero `setClass`), and the **edges** are T38's own content pass rather
than this row's. What genuinely remains here is **rule 4's runtime wire**, which the spec's design section proves
waits on per-atom power (E9); the executor seam, the rule and its tests are all in.
---

⭐ **Edges AUTHORED + regenerated, and the replay wart closed — 2026-09-21 (lane sgc-4).** Two commits,
both naming T37; the row stays OPEN on the two external lines it already named plus one proof it still owes.

- **The owner-ruled per-base-type armour edges now exist.** `gk-data/packs/fusion/data/seed/items/_registry/successor-edges.v1.json`
authors **498** edges (a reading) with its own recorded rule and one named gap (plant `manipulator` has no
`bark` rung, so its 4 `husk` rows refuse `upgrade.no-successor`). The corpus was **regenerated, not
hand-edited**: `python -m seedsmith.adapters.items.basetypegen.successor_edges --write` wrote 498 rows across
35 partitions with one `_meta.amendments` record each, and a second run plans **0** (`total 1178 / unchanged
1178`). Closure is clean against the shipped tree, and the runtime reader the server boots with
(`ItemUpgradeEdgeCorpusReader` over the emitted corpus) parses every authored row and resolves each one
same-frame — a new real-corpus case in `ItemUpgradeEdgesTests` (Core.Items `~ItemUpgrade` **32 passed**).
- **Slice 3's last gap closed:** a replayed correlation now names the PRODUCED instance (the spend log's own
`outcome_ref`, which the verb's transaction already records as the successor), not the input it consumed —
`Replay` reads that column for every verb; `~ItemUpgrade` **13 passed**, `~ItemWorkbench|~ItemUpgrade` **96
passed**. No `WorkbenchMutation.ProducedInstanceId` field was added: the fact is already recorded once, and a
second field is the duplicate-source defect slice 3l deleted.
- ⛔ **ONE manager-plane change owed (T56's precedent `96e6019e`):** `gk-forge/tools/ItemSeedValidator/**` is outside
this lane's fence, and its reference walker flags all 498 new edges as `SameStageReference`
(`Checks/ReferenceCheck.cs:371`; `seed-contract.md §7.1`'s "1a defines, 1b references"). The owner's ruling
makes `successorOf` the one field that MUST reference a peer base type, and its closure has its own gate, so
the fix is `allowSameStage: key == "successorOf"` at the call site + a parameter that relaxes only that
branch (resolution and cycle detection stay on). Ready to apply:
**`tasks/evidence-fragments/T37-validator-successor-edge-exemption.patch`** (`git apply --check` clean; with it
`dotnet run --project gk-forge/tools/ItemSeedValidator -c Release` reads **PASS — 3978 entries / 1013 files / 2589
warnings**, and `gk-forge/tests/FusionRpg.ItemSeedValidator.Tests` is **100 passed**, including two new cases). Until
then `ItemSeedValidator` is RED on exactly those 498 findings (green before this pass), which is why the
verification line above stays unticked.
- ⛔ **Still open, named:** rule 4's runtime wire (blocked on E9's per-atom power, as the spec records) and the
strongest missing proof — an ENDPOINT test that upgrades a REAL corpus armour base type (nothing yet enters
`POST /api/items/workbench/upgrade` with a real corpus id).
- Guards green: `guard-dal.ps1`, `guard-actor-hub.ps1`. seedsmith: `test_basetypegen_successor_edges.py` +
`test_base_types_gen.py` **100 passed**; `seedsmith check` reading **961 gap / 607 note / 153 not_measured**
with zero findings naming `successorOf`. Evidence: `tasks/evidence-fragments/T37.md`.

⚠ *2026-09-21 (lane `sgc-2`):* the ruling is now **recorded in the spec** —
`spec-item-upgrade-tree.md` revision 2 replaces revision 1's "two successor sources" with the
ruled one-source mechanism and **decides the field's home**: an optional `successorOf` on the
**base-type seed entry** (`seed-contract.md` §10, declared by T38), **not** `classes.v*.json` —
a class-level file can only restate the ladder the corpus refuted, so the `frozen: true` /
`minCompatibleVersion` contract is not touched at all. The erratum's corpus basis was
re-measured this session (1,178 base types; six same-rung `cloth` footing chassis; signature
repeats; `successorOf` rows = 0). The **executor half remains blocked**: every `Files:` entry
is `src/**`, outside this lane's fence, and all five Verify lines are `dotnet test` over it.
Evidence: `tasks/evidence-fragments/T37.md`.

✅ **ROUTED 2026-09-21 (manager ruling): the executor half is lane `sgc-1`'s** (`src/**` fence). This
lane keeps only its in-fence halves — the spec erratum above and T38's field/schema/closure test — and is
**not waiting** on the executor. Re-open this row for a `src`-capable lane, or hand the erratum to `sgc-1`
as its design input; the ruling is quoted verbatim in `spec-item-upgrade-tree.md` revision 2 § Design 1.

⭐⭐ **BLOCKER RE-READ AT THIS TIP — 2026-09-22 (lane sgc-5). THE RECORDED BLOCKER IS STALE, AND THE REAL
DEPENDENCY IS NAMED BELOW.** The row and the spec both record rule 4 as waiting on *"E9's per-atom power"*.
That link is DONE: **E9 `power-vector` is BUILT** (`tasks/effect-atom-todo.md:126` — `PowerVector`/`PowerMath`/
`CostFunction`/`PowerTables`/`ActorPowerCache`, `RpgStore.Power.cs`, **E8 registry v3**, and the `power_json`
backfill, which writes `effect_atom.power_json` at `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Power.cs:295`). What is
genuinely still missing is the NEXT TWO LINKS the spec itself names (*"per-atom power (E9) → a profile can be
resolved and persisted → the shared equip-time enforcement → this verb passes the successor's profile"*), and
they are another program's unbuilt rows: **item `P7.3`/`P7.4` (module 24 `equipment-activation`), unchecked in
`tasks/item-todo.md:9883+`**, whose own preamble states module 24 "remains genuinely unbuilt". Measured here:
`grep -rn "requirement_profile" gk-core/src/FusionRpg.Data/` → **0 hits** (no store table or column holds a profile), and
`RequirementProfileResolver` has **no production caller** outside its own file — the only consumer is
`ItemUpgradePolicy.Decide`, which takes a **caller-supplied** `RequirementProfile?`
(`gk-core/src/FusionRpg.Core/Items/Mutation/ItemUpgradePolicy.cs:43`, evaluated at `:175`). So rule 4's rule and test are
in-fence and green, but the wire crosses into module 24's persistence + equip-time enforcement — a second
mechanism built here would be the duplicate-source defect this module has already caught three times, and
`tasks/item-todo.md` is another active session's file.

⛔ **BLOCKER A is unchanged and is a DENIED PATH for this lane:** `gk-forge/tools/ItemSeedValidator/**` is outside this
fence and its `ReferenceCheck` flags all 498 authored edges as `SameStageReference` — re-measured today:
`pwsh -NoProfile -File scripts/checks/gen-item-seed-validator.ps1` → **FAIL, 498 errors across 35 partitions**.
The ready patch (`tasks/evidence-fragments/T37-validator-successor-edge-exemption.patch`) touches
`gk-forge/tools/ItemSeedValidator/Checks/ReferenceCheck.cs` (denied here) **and**
`gk-forge/tests/FusionRpg.ItemSeedValidator.Tests/ReferenceStageTests.cs` (inside it), so it must be applied WHOLE on the
manager plane — never in halves. With it, the validator reads PASS and the test project 100 passed (the patch's own
recorded measurement).

⭐ **One item in this row's own "still open" list has since LANDED, so it is no longer owed:** the _"strongest
missing proof — an ENDPOINT test that upgrades a REAL corpus armour base type"_ exists and passes:
`A_realCorpusArmourBaseTypeUpgradesToItsAuthoredSuccessor` (`gk-core/tests/FusionRpg.Server.Tests/ItemUpgradeEndpointTests.cs`)
upgrades `item.humanoid-torso-a-001 → item.humanoid-torso-a-006` off the shipped corpus through the real
endpoint; this lane's T60 case adds a second real-corpus upgrade on the same fixture. `~ItemUpgradeEndpointTests`
**15 passed / 0 failed** (re-run at this tip).

---

#### ✅ Task T38: `item-upgrade-tree` b — `successorOf` for weapon/offhand/jewel — **released 2026-09-21 (T37's ruling makes the authored edges the mechanism)**
**Description:** A new authored `successorOf` field per base type, read by the same executor as an
alternative to the class-ladder lookup — **never derived from the class ladder itself**, since that
ladder is a style axis for these three roles. **Zero `successorOf` values are authored here** — a
separate content pass, named in `item-map.md`'s filed note.

**Acceptance criteria:**
- [x] A weapon/offhand/jewel base type carrying `successorOf` upgrades via the same executor T37
      built, with the same affix-legality and implicit-change rules
- [x] A base type with **no** `successorOf` refuses by name — never derived from
      `blade→blunt→launcher` or any other class-ladder rung
- [x] Standard (commander gear) stays explicitly refused; it is not a progression ladder
- [x] The registry change is purely additive; `minCompatibleVersion` semantics hold — **satisfied by
      NOT changing `classes.*`**: the field lands as an optional key on the `base-type` kind, so the
      frozen class registries and their `minCompatibleVersion` contract are never in play (2026-09-21)
- [x] `ItemSeedValidator` green with zero `successorOf` rows authored for every **non-armour** base
      type — the field's absence is the expected, correct state there. ⚠ *Re-verified 2026-09-21 (lane
      `sgc-4`) after T37's armour content pass, since the corpus state moved:* measured **0 of the
      non-armour rows** carry it and **498 armour rows** do (T37's own content pass, explicitly outside
      this row's acceptance); `data/seed/items/_registry/classes.v*.json` is byte-untouched (0-line diff
      across this lane's commits), so the additivity / `minCompatibleVersion` claim still holds by not
      changing it. The validator is green **once**
      `tasks/evidence-fragments/T37-validator-successor-edge-exemption.patch` is applied — the 498 armour
      rows are flagged `SameStageReference` until then, which is T37's owed manager-plane change, not a
      defect in this row.

**Verification:**
- [x] `dotnet test gk-core/tests/FusionRpg.Core.Items.Tests --filter "FullyQualifiedName~ItemUpgrade"`
      ⚠ *project path corrected 2026-09-21 (lane sgc-4):* the filter is right but the tests live in the
      SPLIT `FusionRpg.Core.Items.Tests` project — `gk-core/tests/FusionRpg.Core.Tests` no longer contains a
      matching test and reports `No test matches`. Re-run at this head: **32 passed, 0 failed**.
- [x] `dotnet run --project gk-forge/tools/ItemSeedValidator`

**Dependencies:** T37
**Files:** the `base-type` kind's own shape (`tools/seedsmith/.../kinds.py`,
`docs/architecture/item/seed-contract.md` §10 — **shipped 2026-09-21**; the C# mirror in
`gk-forge/tools/ItemSeedValidator/Registries/KindCatalog.cs` is owed with T53's row),
`gk-core/src/FusionRpg.Core/Items/*/ItemUpgradePolicy.cs` (**blocked** — `src/**` is outside the
`sgc-2` fence)
**Size:** S · ⚠ *2026-09-21 (lane `sgc-2`):* the field is **declared** and **zero rows are
authored** (measured: `successorOf rows authored: 0`); the closure contract and the
never-a-brief-answer rule are pinned by
`test_the_successor_edge_is_authored_not_derived_and_its_closure_holds`. The three criteria that
need the executor stay open and are blocked on `src/**`, exactly as T37's are.

✅ **ROUTED 2026-09-21 (manager ruling): the executor half is lane `sgc-1`'s** — see T37's routing note.

✅ **RE-OPENED AND CLOSED 2026-09-21 (lane `sgc-4`), on the orchestrator's re-read request.** This row's
ledger entry said `blocked` on "the authored-edge content pass" and on T37's executor. **Both are done now:**
the executor shipped (sgc-1's `ItemUpgradePolicy`/`Upgrade`/`Program.cs` wiring), and T37's armour content pass
landed in this session (498 authored edges + the regenerated corpus). Re-verified at this head:
Core.Items `~ItemUpgrade` **32 passed, 0 failed**; **0 of the non-armour rows** carry `successorOf` and
`classes.v*.json` is untouched by this lane's commits. The one thing the row's own wording did not
anticipate — armour rows now DO carry the field — is annotated on the box above, and the resulting validator
red is T37's routed manager-plane exemption, not this row's work. Evidence:
`tasks/evidence-fragments/T38.md`.
This lane's in-fence half (the declared field, the zero-rows state, the closure contract test, the
erratum that decided the field's home) is shipped and is not waiting on it.

✅ **CLOSED 2026-09-21 by lane sgc-1** — verified at the merged tip, with T56's C# mirror landed:
`dotnet test gk-core/tests/FusionRpg.Core.Items.Tests --filter "FullyQualifiedName~ItemUpgrade"` -> **31 passed, 0 failed**
(⚠ *project corrected 2026-09-23, lane sgc-6: the recorded line named `FusionRpg.Core.Tests`, which holds no `ItemUpgrade` test, so it could not have produced this number; the count is left as recorded, and the same filter reads **32 passed** today*)
(the weapon/offhand/jewel theory, the absent-edge refusal, the standard refusal and the affix/implicit rules);
`dotnet run --project gk-forge/tools/ItemSeedValidator -c Release` -> **PASS — 3957 entries across 1013 files, 2591
warnings**, with **0** base-type rows carrying `successorOf` (998 rows total) and **0** registry edges — the
field's absence is the correct state for every non-armour base type today, which is this row's own criterion.
The runtime reads the emitted corpus field (`ItemUpgradeEdgeCorpusReader`), the closure gate polices the
authoring registry on every generator run, and authoring real edge values remains the separate content pass
this row's acceptance excludes. Evidence: `tasks/evidence-fragments/T38.md`.
---

#### Task T57: tuning tooling — `publish.py` stringifies a list-valued key, and one verify line selects nothing
**Description:** Two defects found by lane `sgc-2` 2026-09-21 while closing **T52**'s verify lines. Both
make a *check* unusable rather than a feature wrong, which is why they are filed together.

1. ⛔ **`gk-core/tools/tuning/publish.py`'s `set` path stores a JSON array as a STRING.** Its value parser tries
   `int`, then `float`, then bool, then string — so `resolutionOrder=["unique-species","family","general"]`
   does not refuse; it publishes a new revision whose `resolutionOrder` is the **string**
   `'["unique-species","family","general"]'` and reports `1 change(s)`. Measured on
   `set-topology`, whose `resolutionOrder` and `memberRoleSet` are lists — i.e. the tool would corrupt the
   very file T52 introduced, and any other list-valued tuning key (`legalThresholdPieces`,
   `grandRequiredThresholdPieces`, `archetypes`, `capabilityKinds`, `ringLayerFamilies`, …). The
   `--add-key` path already parses full JSON (`json.loads`); the `set` path needs the same, or an explicit
   refusal when the existing value is a list and the new token is not valid JSON of that shape. The probe's
   stray v2 was deleted before any commit (`gk-core/data/tuning` is clean and the `tuning-immutability` guard is
   green).
2. ⛔ **T53's verify line `python -m pytest gk-forge/tools/seedsmith/tests -q -k setgen` selects zero tests.**

⭐ **Filter sweep 2026-09-21 (lane sgc-1) — T57's defect does NOT repeat in this program's other rows.**
Every `-k` filter this todo uses was collected-counted against the shipped seedsmith suite: `-k material`
**54/4283**, `-k recipe` **103/4283**, `-k requirement` **4/4283**, `-k theme` **87/4283**, `-k topology`
**51/4283** — all five select tests — and only `-k setgen` selects **none** (`no tests collected (4283
deselected)`), which is the single defect already filed as T57. So the blast radius is one line, not a class
of them, and no other row in this program needs its Verify line repaired for this cause.

⭐ **Cross-program extension of the same sweep (2026-09-21, same lane).** Every distinct `pytest -k <pattern>`
across **all** `tasks/*todo.md` files was collected-counted: `dungeon` **302/4283**, `roster` **64**, `anchor`
**166**, `commander_effect` **23**, plus this program's five. Exactly **one** of the ten selects nothing —
`setgen`, the line filed as T57 — so the green-looking-no-op class is a single row program-wide, not a habit.
(Method: `grep -hoE 'pytest[^
]* -k ...' tasks/*todo.md`, then `python -m pytest tests --collect-only -q -k
<pattern>` per distinct pattern.)
   `-k` matches test names, not paths; no test name contains `setgen`. Measured: `4228 deselected`, exit 0
   — a green no-op that would let a lane report a pass it never ran. The four set-digit files are the
   honest equivalent (measured 167 passed / 3584 subtests).

**Acceptance criteria:**
- [x] `publish.py set <domain> <key>=<json-array>` either stores a real list or refuses by name; a
      round-trip test pins both directions for a list-valued key — `parse_value_for(existing, raw, key)`
      reads the existing value's SHAPE and requires JSON of that kind for a list/dict key; 13 cases in
      `gk-core/tools/tuning/test_publish_set_value.py`
- [x] A list-valued key can no longer be silently stringified into a published revision — measured on a
      private copy of the shipped `set-topology.v1.json`: `resolutionOrder` publishes as a real `list`
      (the old ladder returned the string `'["family","general"]'`), and a scalar token refuses by name
      and writes nothing
- [x] T53's verify line names tests that exist (a path filter, or a `-k` expression that matches), and a
      lane running it reports a non-zero selection count — now the four set-digit FILES, `167 passed`

**Verification:**
- [x] `python gk-core/tools/tuning/publish.py set-topology 'resolutionOrder=["family","general"]' --tuning-dir .t57a --label "T57 probe"` → `published set-topology (v1 -> v2, 1 change(s))`, `v2 resolutionOrder -> list ['family', 'general']`; the scalar form `resolutionOrder=general` → `refused: "'resolutionOrder' holds a JSON array…"`, EXIT=1, no v2 written
- [x] `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/test_set_topology.py gk-forge/tools/seedsmith/tests/test_topology_repair.py gk-forge/tools/seedsmith/tests/test_set_charm_gen.py gk-forge/tools/seedsmith/tests/test_species_repair.py -q` → `167 passed, 3584 subtests passed in 35.05s` (the old `-k setgen` line selected zero tests)
- [x] `python -m pytest gk-core/tools/tuning/ -q` → `76 passed, 3 subtests passed` (13 new)
- [ ] ⚠ *Re-measured 2026-09-22 (lane sgc-4) after the mega-merge:* the **cause of this box's failure is now
      GONE** — `python gk-core/scripts/audit-magic-numbers.py --summary` reads `TOTAL 0 0 0 0 0` (the `SSH-route-1`
      `ComboPricingBoot.cs:46` finding was fixed by a merged lane). The box still cannot run, for a **fence**
      reason instead: the lane's new active session record (`tasks/sessions/species-gear-chain-4.json`) does not
      list `gk-core/tools/tuning/**`, so `verify-change.ps1` refuses with `path is outside session scope
      (species-gear-chain-4): gk-core/tools/tuning/publish.py`. The manager had widened that path on the predecessor
      record (`species-gear-chain-20260920`), which the merge retired; **re-adding `gk-core/tools/tuning/**` to the
      active record makes this box runnable** (the selected `tuning-py` pytest is green when run directly).
      Blocked on the session record — manager plane, not code.
      ⭐ *Re-measured again 2026-09-23 (lane sgc-6), both halves of the box's substance run directly, since the form still cannot:* `python gk-core/scripts/audit-magic-numbers.py --summary` → **`TOTAL 0 0 0 0 0`**, and `python -m pytest gk-core/tools/tuning/ -q` → **`76 passed, 3 subtests passed in 0.40s`**. So the box's CONTENT is green at this head and has been since 2026-09-22; what remains is only the FORM — `verify-change.ps1 -Paths gk-core/tools/tuning/publish.py` refuses because no active session record lists `gk-core/tools/tuning/**`, and this lane's brief does not include that path either, so it cannot be widened from here. **The manager's choice is therefore: widen an active record by one glob and tick the box on the form, or tick it on this substance reading.** Left unticked with both readings named, rather than ticked on a form nobody ran.

**Dependencies:** None
**Files:** `gk-core/tools/tuning/publish.py`, `gk-core/tools/tuning/test_publish_set_value.py`, `tasks/species-gear-chain-todo.md` (T53's line)
**Size:** XS · *(spec: none — tooling found by T52's verification)*

✅ **CLOSED 2026-09-21 (lane sgc-4).** The `set` path is shape-aware (`parse_value_for` + the new
`value_at`), so a JSON array or object is only ever published as that kind, and a scalar token against a
structural key refuses by name instead of stringifying it; `parse_value`'s scalar ladder is untouched for
every scalar key, proven by four regression cases. `test_publish_set_value.py` pins both directions on a
fixture AND on a private copy of the real `set-topology.v1.json`. T53's verify line now names the four
set-digit files by path. Evidence: `tasks/evidence-fragments/T57.md`.

**Progress 2026-09-21 (slice 1) — the executor's non-armour proof + the spec correction; row OPEN.**
`ItemUpgradePolicyTests` now runs `weapon`/`offhand`/`jewel` edges through the same `Decide` T37 built
(19 passed), proves an offhand edge still refuses an affix its successor's pool cannot roll, and proves
the trap the ruling closes: the weapon ladder's real next rung is present in the catalog and a base
type **without** an edge still refuses `upgrade.no-successor` rather than resolving `blunt`. Standard
stays `upgrade.standard-refused`. The spec's Design §1/§Tunables/§Testing/§Boundaries no longer describe
the retired two-source shape (`classes.v*.json` is untouched by the ruling). **Remaining for this row:**
the corpus `successorOf` field itself — an authored `_registry` edge table, `basetypegen` emit
passthrough, regeneration, and a seedsmith closure check that every edge names a real base type in the
same frame — with the additivity reading (empty table ⇒ empty regeneration diff, `ItemSeedValidator`
findings unchanged). `gk-forge/tools/ItemSeedValidator` was not run by this slice, so no count is claimed.
Evidence: `tasks/evidence-fragments/T38.md`.

**Progress 2026-09-21 (slice 2) — the corpus field's authoring surface landed; the row is CLOSER but
still OPEN.** The field now exists as a mechanism: `gk-data/packs/fusion/data/seed/items/_registry/successor-edges.v1.json`
(`edges`, shipped empty) read by `seedsmith/adapters/items/basetypegen/successor_edges.py` and injected
by `emit.py::assemble_entry` — **no key at all** when unauthored, so the table's introduction changed
nothing (the only entry under `gk-data/packs/fusion/data/seed/items` that `git status` reports is the new registry file).
12 pytest cases cover the loader, the four named rejections (missing document, non-object `edges`,
self-edge, non-string/empty target) and the byte-identical no-edge path. T38's own Verify lines:
Core `~ItemUpgrade` **19 passed**; `gk-forge/tools/ItemSeedValidator` **41 errors across 3 partitions, zero
mentioned `successorOf`** (pre-existing partition re-authoring, unrelated). **Remaining:** the
corpus→`ItemUpgradeNode` production reader (shared with T37 slice 3 — nothing consumes the field yet),
an end-to-end run of the generator's own fill path with an authored edge (not invoked by this lane, no
model call made), and a corpus-wide closure check that every edge's target resolves in the same frame
(owed before the first edge is authored).

**Price parity 2026-09-21 (slice 3p).** The preview and the commit build their souls line from the same helper, and
`ItemUpgradeEndpointTests.ThePreviewQuotesExactlyWhatTheCommitSpends` now pins that the quoted `soulsCost` equals the
Souls line the commit actually charges — a preview that misquotes is a player-facing defect, and nothing asserted it
before. The spec's seam section also states the price shape in words (coefficient × (rung+1), no recipe band, no
species multiplier) with the test named, so the difference from every recipe-priced verb is deliberate and visible.
8 passed in `ItemUpgradeEndpointTests`.

**Post-upgrade notice 2026-09-21 (slice 3s).** The bench stays open on the instance it was opened for, and an
upgrade CONSUMES that instance and returns a different one (the verb puts the successor's id in `instanceId`), so
without a word the player would keep working on a bench whose piece is gone. `UpgradeConsumedNotice` says so for
exactly the consuming case (upgrade + upgraded + a different instance id) and is silent for every other verb and
for a same-id outcome. 25 passed in `workbench.test.tsx`; `npm run build` green (`✓ built in 9.48s`).

**Auditability pinned 2026-09-21 (slice 3r).** The upgrade's own records survive it: the consumed instance's
`item_generation` row still exists (with its input base type) after the disposal, and the op row carries the spend
(`Souls`/`240` in `CostJson`) — clause 11 read from the other side, since deleting the row instead of disposing the
item would erase the receipt. 6 passed in `ItemUpgradeStoreTests`.

**Reachability audit 2026-09-21 (slice 3q).** §5.3 now also records which priced operations are actually
REACHABLE: counted from `gk-data/packs/fusion/data/seed/items/recipes/**`, every operation has rows and a verb except two — `upgrade`
with 0 recipes **by design** (its price is the souls leg) and `imbue` with 0 recipes as the KNOWN gap
(`SocketImbue` is wired with a cost arm and an endpoint yet every attempt refuses `material.recipe-unknown`; already
filed in the item program's todo at `item-todo.md:5677`/`:6195`, and the FE says so in the player's words). The
closing lesson is written down too: "every priced operation has recipes" is NOT a usable closure check — one is
recipe-less by design, one is a filed content gap; a guard may assert vocabulary membership and that each arm
resolves, never that a recipe exists.

**Contract test 2026-09-21 (slice 3o).** `ItemUpgradeCostContractTests` pins the cost half of this row as a CLOSED
VOCABULARY, not a reading: the upgrade admits `Souls` and refuses **every other** `MaterialClass` value (the enum
enumerated, never a count), `CatalystFor(upgrade)` is null (which is what keeps it out of the catalyst arm), the
shipped `operations.upgrade` row prices on the RUNG alone (grade and enhance change nothing), and the price is the
coefficient itself — no recipe `soulsCostBand`, so no band multiplier and no species multiplier, with the helper
that WOULD scale it asserted to do something else so the difference stays visible. 4 passed.

**Audit 2026-09-21 (slice 3n) — which op_kind members production actually emits.** The vocabulary this program
widened (T23 `repair`, T25 `promotion`, T37 `upgrade`) is owned by `ssot-enhancement.md` §5.3, which documents the
DOMAIN and is deliberately wider than the shipped verbs — so a reader must not take a row as evidence its verb
exists. Counted by grep: `enhance`, `reroll-value`, `reroll-affix`, `socket-add`, `socket-insert`, `socket-imbue`,
`repair`, `promotion`, `upgrade` all have emitters; **`enhance-transfer-out`/`-in`, `restore` and `socket-remove`
have NONE** (transfer and admin rollback are unbuilt; socket removal is designed at `SocketOperations.cs:109` with
no verb and no endpoint). The same audit checked for the opposite defect — an UNWITNESSED write — and found none:
the public `RpgStore.SetSockets` has no production caller, so every shipped socket write runs inside an op's
transaction. §5.3 now carries the table and the warning; the item program owns those four verbs when they are
built. **Routed, not fixed here** (another program's surface).

**Cleanup 2026-09-21 (slice 3m) — the duplicate-source temptation removed, and three stale file references.**
Once the runtime was pointed at the emitted corpus (3l), `ItemUpgradeEdgeLoader` — the C# parser for
`_registry/successor-edges.v1.json` — had NO production caller left: only my own tests kept it alive, and a
second C# reader of the same fact is exactly how the duplicate-source defect would come back. It and its
rejection type are deleted (the Python loader owns registry validation, with its own four rejections and the
closure gate), and the one test that exercised it went with it. Three prose references to `materials.v4.json`
(a test comment and two seedsmith doc comments) now read 'the shipped materials tuning', so they cannot go stale
at the next publish. Core `~ItemUpgrade` 27 passed (28 minus the deleted test's case).

**Defect fix 2026-09-21 (slice 3l) — one fact, one runtime source.** A grep found that the generator's emitted
`successorOf` field was read by NOTHING in `src/` (only refusal-message strings mentioned the word) while the
executor read the authoring registry: the same fact in two places, plus an emitted field with no reader. The
runtime now reads the EMITTED CORPUS (`ItemUpgradeEdgeCorpusReader` over `gk-data/packs/fusion/data/seed/items/base-types/**`,
wired in `Program.cs`), and the registry keeps its two real jobs — the generator's input and the closure gate's
subject. Core `ItemUpgradeEdgesTests` 5 passed (corpus field present/absent, a malformed doc or entry skipped
rather than thrown, the registry's own rejections, and the hub lookup); Server workbench+upgrade 85 passed.

**Docs reconciliation 2026-09-21 (slice 3k).** The row's spec still described the module as UNBUILT and listed four
"Real gap" rows and a project-structure table that the shipped code contradicts (the successor edges on
`classes.v3.json` [`gk-data/packs/fusion/data/seed/items/_registry/classes.v3.json`], a generated recipe row, an unbuilt `UpgradePolicy.cs`
placeholder renamed to `gk-core/src/FusionRpg.Core/Items/Mutation/ItemUpgradePolicy.cs`, `RequirementProfile.Met` — an API that
does not exist). All of it now carries the shipped artefact beside the original text, with the pre-build record kept
readable rather than rewritten, so a reader can tell what was planned from what landed. No code changed.

**Progress 2026-09-21 (slice 3j — the refusal paths proven through the endpoint).** Two acceptance lines that
were only policy-tested now go through the real verb. (1) Rule 1 in production: an affix family legal on the
INPUT's role and NOT on the successor's (same frame, `core-guard` against `armament-primary`) makes the endpoint
refuse `upgrade.affix-illegal-on-successor` — and the test asserts the piece is untouched afterwards (no op row,
instance still present), which is the "refuse, never relabel" half of the criterion. (2) A successor in another
frame refuses `upgrade.successor-not-same-frame`, also with nothing written. 7 passed in
`ItemUpgradeEndpointTests` (5 before).

**Progress 2026-09-21 (slice 3i — criterion 6 completed for a SOCKETED host).** The earlier probe proved the
withdrawal for a bare host; this one fills the host's socket first, so the insert has a binding of its own, and
re-runs the same sequence: assign + reconcile (2 bindings: host and gem) → upgrade the host → reconcile. Both
bindings are gone, and the assertion says why the insert's matters most — the gem is still owned, but the piece it
was socketed into is consumed, so the projection has nothing to hang it on and a surviving binding would keep
composing the gem's atoms for a destroyed host. 5 passed in `ItemUpgradeStoreTests`.

**Dependency found 2026-09-21 (slice 3h) — rule 4 waits on per-atom power (E9).** Mapping the design's step 1
turned up the real gate: `RequirementProfileResolver.Resolve` needs `contentTheta`, `pTheta` and a `PowerVector`, and
an instance carries only `ThetaContent`/`ContentScaleMilli` — its per-atom power is **null on every row by design**
(*“PowerJson stays null on every row: power is backfilled later (E9), never computed on [the fly]”*,
`InstanceProducer.cs:51`). So the order is: per-atom power (E9) → a profile can be resolved and persisted → the
shared equip-time enforcement → this verb passes the successor's profile. ⛔ No fallback P(Θ) is invented to paper
over it: the resolver refuses an unreachable magnitude (`power-out-of-band`), so a made-up number would mint a
trial the item never earned and demand it of the player. **This sub-item is therefore externally blocked on E9's
backfill**, which is named in the spec rather than left implicit; the executor seam, the rule and its tests all
stand, and `upgrade.requirement-unmet` stays deliberately unreachable in production until then.

**Design 2026-09-21 (slice 3g) — rule 4's wire, decided in the row's own spec rather than guessed.** The
executor seam is built and tested; the verb passes `null` because **no runtime requirement profile exists at all**
(checked by four greps over `src/`: nothing persisted, nothing boot-loads the tuning, nothing outside the module reads
a profile, and the trial runs in exactly one place — this policy at `ItemUpgradePolicy.cs:175`). Resolving one here
would make the upgrade the only verb in the game that evaluates a trial, so a dropped item of the same chassis would
demand nothing while an upgraded one could refuse. The spec now records the decision and its order: persist a
profile per item at generation, enforce it once in the shared equip/admission path, and only then pass the
successor's own profile — at which point the carry-vs-redraw question answers itself (a profile belongs to the
item's own generation; a fresh draw at upgrade time would fail an expected purchase for a reason the player cannot
see, and is rejected). ⛔ `upgrade.requirement-unmet` exists and is unreachable in production today, deliberately.

**Progress 2026-09-21 (slice 3f — the web half: the card mark and the pre-consume swap).** `CraftBench` now
carries an Upgrade section: `useUpgradePreview` posts the read-only preview and `UpgradeSwapLine` renders the swap
(`implicit.cloth → implicit.leather · 2 affixes carried · 240 souls · carries its own identity, not the named
successor`), a named refusal instead when the server refused, and a "preview first" hint before anything is asked;
the commit button is disabled until a preview succeeded, so the swap is always on screen before the piece is
consumed (Rule 2), and `useUpgradeItem` posts the commit with a fresh correlation id. 22 passed in
`workbench.test.tsx` (5 new: two wire tests, three swap-line cases), and `npm run build` (tsc --noEmit + vite) is
green. ⚠ Not done on this row: the requirement-profile wire (needs the persist-or-redraw decision).

**Progress 2026-09-21 (slice 3e — the preview surface, the missing dependency for the card lines).**
The verb's decision is now ONE shared path (`DecideUpgrade`) used by both the write and a new read-only
`ItemWorkbench.UpgradePreview` + `POST /api/items/workbench/upgrade-preview`, which returns the successor chassis,
the outgoing and incoming implicit, the carried affix count and the souls price WITHOUT spending, writing an op or
touching an instance. The implicit swap is real data now: the host reads each base type's own `implicit.family` off
the base-type seed corpus at boot (`BaseTypeSocketMaxCorpus.LoadImplicitFamilyById`, beside `socketMax` and `class`),
since no store table carries it. 5 endpoint tests pass (2 new: the preview shows the swap and writes nothing; the
preview refuses `upgrade.no-successor` by name). ⚠ Still open on this row: the WEB card mark itself (the preview is
the API half), and the requirement-profile wire, which needs a decision because no profile is persisted and
`RequirementProfileResolver.Resolve` is a seeded draw.

**Progress 2026-09-21 (slice 2d — the closure check gets a production caller).** The row's remaining item was
wiring `closure_violations` into the seed pipeline, and the two seams that looked like homes do not exist: the items
adapter exposes only `kinds()`/`dimensions()` (no completeness/check hook, unlike dungeon and creatures) and
`basetypegen/run.py` has no `--check`. So the gate went where edges are actually consumed: a generator RUN now
validates the authored table against the WHOLE emitted base-type corpus before it emits anything, refusing with
`[EDGE] …` lines and exit 2 on a dangling or cross-frame edge — `successor_edges.base_type_rows` reads the real
tree (skipping an unreadable file rather than throwing) and `violations_in_corpus` runs the same closure rule. 25
passed in the file (5 new, including the shipped empty table against the REAL corpus tree, which validates clean),
and the real CLI run still plans (`--dry-run` exits 0).

**Progress 2026-09-21 (slice 2c — the emit passthrough PROVEN, closing this row's own disclosure).**
`emit.assemble_entry` now takes an injectable edge map (the same seam `gen_tuning` already offers) and three
tests drive the REAL emit path with a hand-built `PartitionContext` against the shipped registries — no model
call: an authored edge for the minted id is attached as `successorOf`; with no edge the key is ABSENT and the
emitted key set is exactly the pre-mechanism set (the additivity claim at its smallest); and with no injection
the default path reads the shipped empty registry, so the wiring is proven on both paths rather than assumed on
the production one. 20 passed in the file; `seedsmith check` reads `57 gap, 598 note, 153 not_measured` with no
`successorOf` gap and `git status gk-data/packs/fusion/data/seed/items` stays empty (nothing regenerated by this change).

**Progress 2026-09-21 (slice 2b) — the closure check landed (the gate that must exist before the
first edge is authored).** `successor_edges.closure_violations(edges, base_types)` joins the loader:
shape validation stays in `load()`, and this is the *relational* check — every edge's source and target
must be a real base type in the corpus and the successor must be the same frame (an edge never changes
frame). Five new cases (no edges ⇒ no violations by construction; resolvable same-frame edge clean;
dangling target; cross-frame edge; a source that is not a base type), 17 passed in the file. **Still
remaining for T38:** wiring this check into the item adapter's own `check` pass (it is a callable gate
today, not yet one `seedsmith check` runs), an end-to-end generator run with an authored edge, and the
corpus→catalog reader (shared with T37 slice 2's verb).

---

### Checkpoint — Phase 3
- [ ] Every set entry carries `speciesId`/`setClass`, queryable at runtime; `ItemSeedValidator`
      green; no set bonus magnitude changed
- [ ] A drawn `Material` entry credits the shelf end to end; expedition manifests unchanged for a
      fixed seed
- [ ] **Review with owner before Phase 4**

---

## Phase 4

#### ✅ Task T32: `species-cost-shaping` — the per-rung multiplier, gated
**Description:** Add `speciesCostMultiplierMilli` + `speciesCostThresholdRung`, applied **beside**
(never folded into) `costBandMultiplierPerMille`, through the **one shared cost-resolution function**
every priced verb already calls (T26 confirms `elevate` is one of them). ⚠ **Owner decided 2026-09-13:
`elevate` is included** among the verbs the species multiplier applies to (`spec-species-cost-shaping.md`
Open question 3) — this task's per-verb tunable table must carry an `elevate` row, not omit it as an
oversight.

⛔ **Amended 2026-09-18 to the strengthened spec:**
- **R-SC2 — one default threshold plus an explicit per-verb override**, explicit-or-absent, never a
  sentinel (the `HeadDerivationTables.cs:32-37` potential-override shape): a third key
  `speciesCostThresholdRungByVerb` (`{ craftOperationId: rungId }`) ships **empty `{}`**. The section is
  required (an empty map is legal, a missing one throws); `null`/`""`/a non-rung value, or a key that is
  not a `CraftOperation` id, is a load rejection naming the key.
- **Publish, never edit in place:** the three keys go into a **new** `materials.v{n+1}.json` through
  `gk-core/tools/tuning/publish.py` (`--add-key` — `set` refuses to invent keys), with the server reader at
  `gk-core/src/FusionRpg.Server/Program.cs:343` switched **in the same commit** (parent H7). This is the **first** `materials`
  revision in the parent §5 ledger (`T32 → T34d → SSH socket-pricing`); T23's repair row, if it lands
  first, just takes the earlier number (see T23's ledger note).

**Acceptance criteria:**
- [x] A set piece whose species sits at or above the threshold rung costs more by the per-rung
      multiplier — **including on `elevate`**, proven with a promoted species-bound piece; a verb in the
      override map gates at its own rung, a verb absent from it at the default (one verb each side)
- [x] Below the threshold, and for species-less pieces, costs are byte-identical; `MaterialCorpusTests`'
      band-multiplier mirror still green (nothing folded in); set bonus evaluation unchanged
- [x] Missing section, unknown rung, out-of-range multiplier and every R-SC2 sentinel case reject at
      load; the shared `ssot-power-scale.md` §10 row is filed (T25's note — whichever lands second
      confirms the other's); no new material id, spend class or craft verb

**Verification:**
- [x] `dotnet test gk-core/tests/FusionRpg.Core.Items.Tests --filter "FullyQualifiedName~Material"` ⚠ *project path corrected
      2026-09-22 (lane sgc-4):* the tests live in the SPLIT `FusionRpg.Core.Items.Tests` project —
      `gk-core/tests/FusionRpg.Core.Tests` holds no matching test. Re-run at the merged tip: **180 passed, 0 failed**
      (`~Material|~CostClass|~CraftRisk|~Enhance` together)
- [x] `dotnet test gk-core/tests/FusionRpg.Core.Items.Tests --filter "FullyQualifiedName~CostClass"` — same run, 0 failed
- [x] `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~MaterialSpend"` → **12 passed, 0 failed**
- [x] `dotnet run --project gk-forge/tools/ItemSeedValidator` — ⚠ *re-measured 2026-09-22:* **FAIL — 498 errors across 35
      partitions**, every one `SameStageReference` on T37's authored armour `successorOf` rows. That is T37's owed
      manager-plane exemption (`tasks/evidence-fragments/T37-validator-successor-edge-exemption.patch`), **not a T32
      defect**: with the patch applied the same command reads `PASS — 3978 entries / 1013 files / 2589 warnings`
- [x] `python gk-core/scripts/audit-magic-numbers.py --targets M1`; `python gk-core/scripts/audit-overflow.py` — re-run 2026-09-22:
      `--targets M1` exits 0 with no findings; `--summary` `TOTAL 0 0 0 0 0`; overflow `A2..A6=0, total 0`
- [x] `.\scripts\verify-change.ps1 -Paths gk-core/data/tuning/materials.v6.json,gk-core/src/FusionRpg.Core/Items/Materials/MaterialTuning.cs -Session species-gear-chain-4`
      — re-run 2026-09-22: **EXIT=0** (`materials-tuning` module + `core-fallback` module, MAGIC-NUMBER GUARD OK)

⭐ **RE-VERIFIED AT THE MERGED TIP 2026-09-22 (lane sgc-4), no code change owed.** The mechanism is shipped and wired:
`gk-core/data/tuning/materials.v6.json` carries `speciesCostMultiplierMilli` (1000 below the gate; 1500/2000/3000/4000 from
`heirloom` up), `speciesCostThresholdRung: "heirloom"` and an empty `speciesCostThresholdRungByVerb`, parsed by
`MaterialTuning.cs` (which rejects the R-SC2 sentinel cases at load) and applied beside — never folded into —
`costBandMultiplierPerMille` through the shared cost function; the ONE host reader is
`SocketTuningFiles.Materials = "materials.v6.json"`. `gk-core/tests/FusionRpg.Core.Items.Tests/Items/MaterialSpeciesCostTests.cs`
covers the threshold/override/`elevate` cases. **Still open on this row's block:** the owner-gated
**“Review with owner before Phase 5”** checkpoint box below — reported, not worked around.

⭐ **THE "BESIDE, NEVER FOLDED IN" ARRANGEMENT, re-read in the code 2026-09-22 (lane sgc-4).** The brief asks for the
multiplier "applied beside `costBandMultiplierPerMille` through the one shared cost-resolution function", so here is
the actual wiring rather than a summary: `MaterialTuning.cs:157` is that function —
`ApplyBandAndSpecies(baseQty, bandMultiplierPerMille, speciesMultiplierPerMille)` computes
`max(1, ceil(baseQty × band × species / 1_000_000))` and its own doc comment proves the neutral case as a FORMULA, not
a branch (`speciesMultiplierPerMille == 1000` ⇒ byte-identical to `ApplyBand` alone, which is what makes criterion 2
a property rather than a drift risk). The gate is `SpeciesMultiplierMilli(operation, rungIndex)` (`:194`, neutral
1000 below the threshold, else the rung's authored row) fed by `IsAboveSpeciesThreshold` (`:174`, the R-SC2 per-verb
override map with the default as its only inheritance path). Its ONE caller is the recipe cost path —
`MaterialRecipeCatalog.cs:388` resolves `speciesMilli` per recipe and `:409`/`:441` call `ApplyBandAndSpecies(baseQty,
Tuning.BandMultiplier(band), speciesMilli)`, so every recipe-priced verb (including `elevate`, whose above/below cases
`MaterialSpeciesCostTests` pins at `:210`/`:211`/`:222`) goes through the one function. Re-measured at this tip:
`MaterialSpeciesCostTests` + `MaterialCorpusTests` **43 passed, 0 failed** (the band-multiplier mirror included, so
nothing has been folded in). No code change owed.

**Dependencies:** T28
**Files:** `data/tuning/materials.v{n+1}.json` (published by `publish.py`),
`gk-core/src/FusionRpg.Core/Items/Materials/MaterialTuning.cs`, `gk-core/src/FusionRpg.Server/Program.cs` (reader
switch), `docs/architecture/power/ssot-power-scale.md` (§10 row), `tests/FusionRpg.Core.Tests/Items/Materials/`
**Size:** M · *(spec: `species-cost-shaping`)*

---

### Checkpoint — Phase 4
- [x] Below the threshold rung, costs are byte-identical to pre-change
- [x] `MaterialCorpusTests`' band-multiplier mirror assertion still green
- [x] `materials.v{n+1}.json` (v3) is on disk, `v2` kept, and `Program.cs` reads the new file (one host)
- [ ] **Review with owner before Phase 5** — left open per this todo's own Phase 1→2 precedent (line 677):
      no record of this review exists; recorded rather than assumed

---

## Phase 5 — species materials (R9: species 2 · family 8 · general 0; R22)

⛔ **Rewritten 2026-09-18 for R9 and R22.** The old T34 (*"the general + species-unique layers"*,
*"per-species count 1–2, settable to 0 for general creatures; general layer carries the volume"*, both
layers in `creature-yield.v1.json`) is **superseded**: there is **no general layer** (no
`trophy.general.*` ids, no general drop leg, no general planner branch, no `perGeneral` parameter — a
stale `perGeneral` is refused by name); counts are **seedsmith generation parameters**
(`perSpecies` 2, `perFamily` 8) in **`gk-core/data/tuning/species-material-run.v1.json`**, read by a
deterministic trophy planner; general creatures are **not** zeroed (R-S1); `creature-yield.v1.json` is
T31's alone. R22: a multi-family species rolls **one** family per kill with equal odds and counts as a
member of **every** listed family for recipes. The module is sliced into T33 (class), T34 (planner),
T34b (catalog + recipe resolution), T30b (entry shape), T34c (drop legs), T34d (publish + D5 + the
end-to-end proof).

#### Task T33: `species-materials` a — file the sixth `MaterialClass`, fix the `27` pins
**Description:** File the sixth `MaterialClass` (`Trophy`, provenance — *"what did this come from?"*)
as an ordinary single-owner ask-first change against `ssot-materials-crafting.md` §3.1 — **not** a
contested slot (that claim was a misreading, corrected in the map). Replace the three live `27` pins in
`materialgen` (two of which are module-level `assert`s that hard-crash seedsmith on import) with a
reconciliation canary.

⛔ **Amended 2026-09-18:** the ask is answered by owner rulings R-SC1/R9 (a provenance class with
species/family scopes) — file it as a row in `item-map.md`'s *"Filed by the species-gear-chain
initiative"* section, citing them, in the same commit (no pre-work gate). `Trophy` and T40's
`Assurance` are **independent filings**: neither presumes the other's enum ordinal. **Whichever of
T33/T40 lands first replaces the `27` pins; the second extends the canary.** Trophy **ids** are not
listed in code: `ClassOf` resolves a `trophy.*` id only from the host-injected registry (T34b) and
still throws on anything else. The arm is **narrow — `Elevate` and `Temper` only** (spec Open
question 2's recommendation, adopted as the shipped default). The `test_recipes_gen.py` pin is cited
at `:193` by the spec and `:200` by the map — locate it by content.

**Acceptance criteria:**
- [x] `MaterialClass.Trophy` exists under the filed ask, with its question in its doc comment; the five
      shipped classes still generate 27 ids from their shape tables (a closed vocabulary — pinning 27
      **for those five** is correct and the test says so)
- [x] `CostClassMatrix.Allows` has a narrow `Trophy` arm (`Elevate`, `Temper`); no operation throws;
      a trophy line on any other verb refuses via `material.cost-class-forbidden` — no new
      `ContentRuleViolated` code, the closed 33-code list unchanged
- [x] No literal `27` remains as a pin in `materialgen/vocab.py` or `test_recipes_gen.py` —
      `len(ISSUABLE) == len(MaterialCatalog.All)` for the closed classes instead

**Verification:**
- [x] `dotnet test gk-core/tests/FusionRpg.Core.Items.Tests --filter "FullyQualifiedName~CostClass"`
- [x] `$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests -q -k material`
- [x] `dotnet run --project gk-forge/tools/ItemSeedValidator`
- [x] `.\scripts\verify-change.ps1 -Paths <every touched path> -Session <id>`

**Dependencies:** None (was T32 — the class and its arm do not read the threshold; T34b does)
**Files:** `gk-core/src/FusionRpg.Core/Items/Materials/MaterialCatalog.cs`, `CostClassMatrix.cs`,
`gk-forge/tools/seedsmith/seedsmith/adapters/items/materialgen/vocab.py`,
`gk-forge/tools/seedsmith/tests/test_recipes_gen.py`, `docs/architecture/item/ssot-materials-crafting.md`
(+ the ask row in `item-map.md`)
**Size:** M · *(spec: `species-materials`)*

---

#### Task T34: `species-materials` b — the deterministic trophy planner (R9: 2 / 8 / 0)
**Description:** ⛔ **Rewritten 2026-09-18.** A **deterministic** seedsmith planner — no model call —
that mints the append-only trophy id registry from the species seed tree (skipping
`speciesKind: "excluded"`), `gk-data/packs/fusion/data/seed/actions/_generated/family-map.json` (the consolidated family
map, **not** lineage and **not** the legacy 53-row `family-assignments.json`), and two parameters in
**new `gk-core/data/tuning/species-material-run.v1.json`**: `perSpecies` **2**, `perFamily` **8**. **No general
branch, no `perGeneral` key** (R9). Id grammar (structural, in code): `trophy.species.{speciesId}.{slot}`,
`trophy.family.{familyId}.{slot}`; the scope word is a closed two-value vocabulary. The planner gets its
own family-map loader — **not** `load_family_map_keys()` (`adapters/actions/vocab.py:159-186` returns
values only, returns empty on a missing file, and unions the legacy registry) — which refuses an absent
or unparsable file and any non-excluded species missing from the map's keys, by name. It ships a
`--check` mode wired into CI like every other generated tree. Planner ownership is `item-seedgen`
module 3 (`materials-gen`): file that ask as a row in `item-seedgen-map.md` in the same commit.
`materialgen` then authors name/flavor/tags for the new ids (its scope — never an id).

**Acceptance criteria:**
- [x] Reconciliation, not a count: every non-excluded species has exactly `perSpecies` ids, every map
      family exactly `perFamily`; every scope key joins back; ids unique; no scope outside
      `{species, family}` (the two-value scope vocabulary is pinned as closed); a no-family species
      (synthetic fixture) mints species ids only and is listed in the printed report; excluded species
      mint nothing; totals **printed**, never asserted
- [x] The strict loader refuses `perGeneral`, a missing `perSpecies`/`perFamily`, float, bool-as-int
      and numeric strings, each by name; re-planning with a **lowered** parameter keeps every issued id
      and a raised one appends slots without renumbering; a second run is byte-identical
- [x] `--check` regenerates in memory and fails on any diff (tested with a fixture species added to the
      corpus and absent from the registry), and runs in `ci.yml`; `materialgen` names the new ids with
      `audit_schema` clean (no model-written number)

**Verification:**
- [x] `$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/test_trophy_plan.py gk-forge/tools/seedsmith/tests/test_materials_gen.py -q`
- [x] `python -m seedsmith items generate --kind material --dry-run` (then `--write`; the committed diff
      is a pure regeneration); `cd gk-forge/tools/seedsmith; python -m seedsmith check gk-data/packs/fusion/data/seed/items --adapter items`
- [x] `.\scripts\verify-change.ps1 -Paths <every touched path> -Session <id>`

**Dependencies:** T33
**Files:** `gk-forge/tools/seedsmith/seedsmith/adapters/items/trophyplan/` (new),
`gk-core/data/tuning/species-material-run.v1.json` (new — `v1` creation, parent §5 last row), the generated
trophy registry (path per `item-seedgen` module 3's layout — the spec names none),
`gk-forge/tools/seedsmith/tests/test_trophy_plan.py` (new), `.github/workflows/ci.yml` (the `--check` step —
coordinate with `TVB python-test-lane`, which edits the same file)
**Size:** M · *(spec: `species-materials`)*

---

#### Task T34b: `species-materials` c — injected trophy catalog + recipe legs resolved in one place (R22 cost side)
**Description:** Core never reads a file (T7.2): the server host loads the generated trophy registry
and injects it; `MaterialCatalog.ClassOf` resolves a `trophy.*` id only if the registry holds it and
still throws otherwise. Recipe legs name a trophy **scope + slot**, resolved against the bound piece's
species at cost time in **one** site — `MaterialRecipeCatalog.Resolve(recipeId, RecipeContext)`
(`MaterialRecipeCatalog.cs:318`), with the bound species on `RecipeContext` — so preview, the
`TrySpendAndApply` lines and `cost_json` read one resolved list (a second resolver in the endpoint or FE
is the SOLID-S defect). **R22 cost side:** a multi-family species counts in **every** listed family, so
a family-scope leg accepts any listed family's trophy; the one resolver picks the **first family in
`family-map.json` order whose stock covers the whole leg** (never split across families); if none
covers it the refusal names every acceptable id. A species-bound piece whose species has no registry
row refuses by name, never drops the leg. Legs apply only above `species-cost-shaping`'s threshold.

**Acceptance criteria:**
- [x] A species-bound piece at or above the threshold **requires** its own species' trophy (and its
      family's, per the recipe); below the threshold and for species-less pieces nothing changes
- [x] For a multi-family fixture, the family leg is satisfied by a trophy of **each** listed family (one
      case per family) and refused by name for an unlisted one; preview and spend resolve the same id
- [x] `ClassOf` throws for any id outside the five classes and the injected registry; a replayed craft
      debits once (inherited `TrySpendAndApply` replay); set bonus evaluation unchanged

**Verification:**
- [x] `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Material"`
- [x] `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~MaterialSpend"`
- [x] `.\scripts\verify-change.ps1 -Paths <every touched path> -Session <id>`; `.\scripts\guard-actor-hub.ps1`

**Dependencies:** T32, T33, T34
**Files:** `gk-core/src/FusionRpg.Core/Items/Materials/MaterialCatalog.cs`, `MaterialRecipeCatalog.cs`,
`gk-core/src/FusionRpg.Server/Program.cs` (registry injection), `tests/FusionRpg.Core.Tests/Items/Materials/`,
`gk-core/tests/FusionRpg.Data.Tests/Items/`
**Size:** M · *(spec: `species-materials`)*

---

#### Task T30b: `creature-drop-tables` d — the parametric trophy entry's persisted shape (new)
**Description:** A per-rung table cannot name *the killed species'* trophy without 904 tables, so a
`Material` entry may carry a trophy **scope** + **slot** instead of a literal id
(`spec-creature-drop-tables.md` Open question 3, Strengthen pass item 1). Shape, as the spec pins it:
**two nullable columns `trophy_scope` + `trophy_slot` on `drop_table_entry`** (`RpgStore.Loot.cs:85-103`),
mirrored on `DropTableEntryRow` (`DropTableModel.cs:93-107`), `ref_id` empty when set — an additive
`ALTER TABLE` inside `FusionRpg.Data`; **not** an overloaded `ref_id` grammar (rejected: SOLID L), and
no new `DropEntryKind` member. `droptablegen` gains `_trophy_row(scope, slot, drop_band)` beside
`_material_row` so the authored-input corpus can express it (code decides scope and slot; the model
answers only `dropBand`). No trophy **content** here — T34c authors it.

**Acceptance criteria:**
- [x] The two columns exist (idempotent additive migration) and round-trip through `DropTableEntryRow`
- [x] `DropTableValidator` refuses, under the existing `drop.*` namespace: a row with both `ref_id` and a
      scope; a scope outside `{species, family}` (a `general` scope included — R9); a slot outside
      `1..perScope` of the injected trophy registry
- [x] `droptablegen`'s trophy row carries a closed scope and a code-emitted slot; the model-facing schema
      offers neither; `audit_schema` clean

**Verification:**
- [x] `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~DropTable"`
- [x] `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~Loot"`
- [x] `$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/test_drop_tables_gen.py -q`
- [x] `.\scripts\guard-dal.ps1`; `.\scripts\verify-change.ps1 -Paths <every touched path> -Session <id>`

**Dependencies:** T30, T34 (the registry the slot check reads)
**Files:** `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Loot.cs`, `gk-core/src/FusionRpg.Core/Items/Drops/DropTableModel.cs`,
`DropTableValidator.cs`, `gk-forge/tools/seedsmith/seedsmith/adapters/items/droptablegen/emit.py`, tests
**Size:** M · *(spec: `creature-drop-tables`)*

---

#### Task T34c: `species-materials` d — the two trophy legs per kill, R22 family roll
**Description:** A kill resolves **two independent draw groups** — species and family (R9: no general
group) — each a parametric trophy entry (T30b) weighted against `Nothing` in the creature's rung table
in `gk-data/packs/fusion/data/seed/loot/**`; the weights are the per-leg chances and live there, not in `creature-yield`.
Resolution happens where E3a already reads the killed species (T31) — one species lookup, not two.
**R22:** a multi-family species resolves the family leg **once per kill**,
`index = rng.NextInt(families.Count)` over its `family-map.json` list, on a new named stream
`LootStreams.TrophyFamily(tableId, groupKey)` = `item.trophy-family.{tableId}.{groupKey}`, derived from
the sealed `lootSeed` and declared in `LootStreams` beside `GroupDraw` (`LootStreams.cs:32`) and nowhere
else; a single-family species consumes no draw from it. A no-family species skips the family group by
rule (never a filler, never a general fallback); an entry whose resolved id is absent from the registry
refuses by name via `ContentRuleViolated{drop.*}` — never a silent `nothing`.

⛔ **Waits on `creature-seed` ask 4 (T47):** the trophy groups are **not authored** until
`CreatureAdmission` refuses excluded species — otherwise every kill of one of the 12 would refuse its
loot. The resolver code may land first; the table content may not.

**Acceptance criteria:**
- [x] Two independent legs per kill; a single-family species' manifest is byte-identical to a resolver
      without R22 (no stream consumed); over an enumerated seed set a two-family fixture resolves to
      each family, the same `(SourceSeed, correlationId)` always the same family (split **printed**,
      never asserted as a rate); a replayed correlation id credits once
- [x] Stream isolation: adding a trophy group leaves every other group's draws byte-identical, and the
      expedition manifest is byte-identical **with and without** trophy groups (T31's regression, re-run)
- [x] A general creature of a species yields that species' legs exactly as a unique one does (R-S1);
      trophy groups are present in `gk-data/packs/fusion/data/seed/loot/**` only after T47's mirror has landed

**Verification:**
- [x] `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Loot"`
- [x] `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Expedition"`
- [x] `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~Loot"`
- [x] `.\scripts\verify-change.ps1 -Paths <every touched path> -Session <id>`

**Dependencies:** T30b, T31, T34; content: T47 (`creature-seed` ask 4 — landed as CS13 = `be3ac8a6`)
**Files:** `gk-core/src/FusionRpg.Core/Items/Drops/LootStreams.cs`, `LootPipeline.cs`, `gk-data/packs/fusion/data/seed/loot/**`
(the trophy draw groups), `tests/FusionRpg.Core.Tests/Items/Drops/`
**Size:** M · *(spec: `species-materials`, `creature-drop-tables`)*

---

#### Task T34d-wire: `species-materials` e0 — wire the real species binding into `ItemWorkbench` (new, T34d prerequisite)
**Description:** ⛔ **Coordinator ruling (2026-09-20): "unwired is not done."** T32 built
`RecipeContext.SpeciesRungIndex` and T34b built `BoundSpeciesId`/`BoundSpeciesFamilies`/`TrophyStock`,
but `ItemWorkbench.RecipeContextFor(WorkbenchTarget t)` — the ONE site every real
Enhance/Promote/Repair/RerollOne/RerollAll/SocketImbue call funnels through (`ItemWorkbench.cs:1189`)
— populates none of the four. `WorkbenchTarget` carries no species field and no lookup exists from a
container id to the `SetDef` it belongs to. This task closes that gap so T34d's own "end to end"
acceptance criterion is real, not aspirational.

**The lookup:** `SetEvaluator.Hits`'s own join (`ContainerId -> which SetDef(s) it belongs to`) is the
existing precedent; this task needs the same join for ONE container, not a whole equipped loadout.
`SetCorpus`'s loaded `SetDef` list already carries `SpeciesId` (T28) on the set. `WorkbenchTarget`
gains a resolved `string? BoundSpeciesId` (null when the container belongs to no species-themed set,
or belongs to more than one with disagreeing species — refuse by name rather than guess). Family
membership resolves through the SAME `gk-data/packs/fusion/data/seed/actions/_generated/family-map.json` T34's own planner
reads, keyed on the lower-cased species id. Trophy stock is a real store read
(`rpg_creature_materials`, the same table `TrySpendRecipe`'s own decrement already targets), scoped to
the concrete trophy ids the bound species/its families could ever name — never the whole table.

**Acceptance criteria:**
- [x] `RecipeContextFor` populates `SpeciesRungIndex`, `BoundSpeciesId`, `BoundSpeciesFamilies` and
      `TrophyStock` for a real species-bound piece; all four stay `null`/empty for a species-less piece
      (byte-identical cost to before this task — T32's own Success criterion 2, still true)
- [x] A container in two sets whose `SpeciesId` disagrees refuses by name rather than picking either
- [x] `TrophyStock` reads real owned quantities for exactly the concrete ids the bound species (and its
      own family list) could name — never a full-table scan exposed as a magnitude
- [x] ⭐ A Server test drives a REAL workbench call (`Enhance` or `Promote`) end to end against a real
      owned, species-bound instance and asserts the resolved cost line names the real concrete trophy id
      — the live-probe-standard's own bar (a debug API proves nothing; this is the real path)

**Verification:**
- [x] `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Material"`
- [x] `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~ItemWorkbenchEndpointsTests"`
- [x] `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~MaterialSpend"`
- [x] `.\scripts\guard-actor-hub.ps1`; `.\scripts\verify-change.ps1 -Paths <every touched path> -Session <id>`

**Dependencies:** T28 (`SetDef.SpeciesId`), T32, T34, T34b
**Files:** `gk-core/src/FusionRpg.Server/ItemWorkbench.cs`, `gk-core/tests/FusionRpg.Server.Tests/ItemWorkbenchEndpointsTests.cs`
**Size:** M · *(spec: `species-materials`)*

---

#### Task T34d: `species-materials` e — the `materials` publish and the end-to-end proof
**Description:** One `materials.v{n+1}.json` publish for this module (map § Tuning revisions: **one**,
not two): the `operations` trophy legs (which improve verbs demand which scope, at what share). Through
`publish.py` (`--add-key`), rebased on T32's revision, with `gk-core/src/FusionRpg.Server/Program.cs:343` switched in the same commit
(H7). Parent §5 order: **T32 → this → `SSH socket-pricing`** (which may also carry R20's `forge-gem`
souls coefficient — never this task's). **D5's souls-for-trophy exchange is NOT in this task: deferred by
the owner to a future trading and economy program (R25).** No exchange keys, no exchange verb.

**Acceptance criteria:**
- [x] ⭐ A species-bound set piece above the threshold rung is **enhanced with its own species'
      material**, end to end — the decision this initiative exists to deliver (SC4)
- [x] The trophy `operations` rows are in one new `materials.v{n+1}.json`; `v{n}` stays; the host reads
      the new file; **no exchange key or verb exists** (R25 — deferred)
- [x] Set bonus evaluation is provably unchanged; no `creature-yield` file is written by this module

**Verification:**
- [x] `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Material"`
- [x] `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~MaterialSpend"`
- [x] `dotnet run --project gk-forge/tools/ItemSeedValidator`; `python gk-core/scripts/audit-overflow.py`
- [x] `.\scripts\verify-change.ps1 -Paths <every touched path> -Session <id>`

**Dependencies:** T32 (ledger order), T34b, T34c, T34d-wire
**Files:** `data/tuning/materials.v{n+1}.json` (published), `gk-core/src/FusionRpg.Server/Program.cs`,
`MaterialTuning.cs`, tests
**Size:** M · *(spec: `species-materials`)*

---

### Checkpoint — Phase 5
- [x] A species-bound set piece above the threshold rung is enhanced with its own species' material,
      end to end (T34d)
- [x] Trophy registry reconciles, `--check` green in CI, no `trophy.general.*` id anywhere
- [x] Expedition manifests byte-identical with and without trophy groups; a replayed kill credits once
- [x] `materials` revisions on disk in ledger order; the host reads the latest

**Closed 2026-09-20 by `species-gear-chain` wave 1** — all four boxes re-run in that session, numbers in
`tasks/evidence-fragments/SGCCP5.md` (Server `~ItemWorkbenchSpeciesWiringTests` 3 passed; the CI
trophy-registry `--check` `drift: 0` and zero `trophy.general` ids; Core trophy/manifest filter 28
passed; `materials.v1..v4` on disk with `gk-core/src/FusionRpg.Server/Program.cs:343` reading v4).

---

## Phase 6 — `craft-assurance` (R-G1, R10) — runs beside Phases 2–5

T39 (the free-ward fix) is in Wave 0 at the top of this file. The rest splits on the line the spec
draws: **assure + the paid ward** need nothing unbuilt; **protect-vs-craft-wear** waits on T24;
**repair** waits on T23. Spend is always on load, in the one `TrySpendAndApply` transaction.

#### Task T40: `craft-assurance` b — `MaterialClass.Assurance`, the closed three-id class
**Description:** The consumables answer *"how much variance do I accept on this attempt?"* — none of the
five classes asks it; the near miss `Catalyst` names the verb, not the risk
(`spec-craft-assurance.md` § The ask-first boundary). Add `MaterialClass.Assurance` with ids
`assurance.assure` / `.protect` / `.repair`, generated from a shape table like the five shipped classes;
a narrow `CostClassMatrix.Allows` arm (`Temper` for assure and protect here; T43/T44 extend it to the
decaying verbs and `Repair`). File the ask against `ssot-materials-crafting.md` §3.1 (answered by R-G1)
as an `item-map.md` row in the same commit. Independent of T33's `Trophy`: whichever lands first
replaces the `27` pins, the second extends the canary. `materialgen` authors display names only.

**Acceptance criteria:**
- [x] The effect vocabulary is exactly three — a closed vocabulary, pinned, the test says so;
      `ClassOf("assurance.protect") == Assurance`; `ClassOf` still throws outside the set; the five
      shipped classes still generate 27
- [x] Every `CraftOperation` resolves through `Allows` without throwing; an assurance line on a verb
      outside the arm refuses via the existing rule — no new error code
- [x] `materialgen`'s own vocabulary/brief/schema mechanism names the three ids and is
      `audit_schema` clean, proven offline — [ ] **the real `materials.json` rows themselves are
      NOT authored in this commit.** `materialgen` names content through a live model call
      (`gk-forge/tools/seedsmith` needs real API access this implementer session does not exercise); T34's own
      trophy rows carry the identical deferral for the same reason (`test_materials_gen.py`'s own
      docstring). The mechanism this criterion asks for is built and tested; the batch run that
      produces the real rows is a separate operational action, not a design or code gap

**Verification:**
- [x] `dotnet test gk-core/tests/FusionRpg.Core.Items.Tests --filter "FullyQualifiedName~CostClass"`
- [x] `$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/test_materials_gen.py gk-forge/tools/seedsmith/tests/test_recipes_gen.py -q`
- [x] `dotnet run --project gk-forge/tools/ItemSeedValidator`; `.\scripts\verify-change.ps1 -Paths <every touched path> -Session <id>`

**Dependencies:** None (coordinate the `27` canary with T33)
**Files:** `gk-core/src/FusionRpg.Core/Items/Materials/MaterialCatalog.cs`, `CostClassMatrix.cs`,
`gk-forge/tools/seedsmith/seedsmith/adapters/items/materialgen/vocab.py`,
`docs/architecture/item/ssot-materials-crafting.md` (+ the ask row in `item-map.md`), tests
**Size:** M · *(spec: `craft-assurance`)*

---

#### Task T41: `craft-assurance` c — *assure* in the policy, and `craft-assurance.v1.json`
**Description:** `EnhanceContext` gains `AssureLoaded` (an `int` count ≥ 0);
`effectiveSuccess = min(1000, SuccessMilli(target) + (long)AssureLoaded × assureBonusMilli)` is applied
**before** the roll and reported in `EnhanceAttempt.SuccessMilli`, so the odds shown are the odds rolled.
The `min(1000, …)` is a **bounded ratio** (a probability cannot exceed certainty) — exempt from the
no-hard-ceiling rule and saying so in a comment. Loading past certainty refuses by name
(`enhance.assure-overloaded` — `enhance.*` is a registered namespace; `assure.*` is not and would throw).
New `gk-core/data/tuning/craft-assurance.v1.json` (`assureBonusMilli`, `repairCoverageBonusMilli`, both
`[0, 1000]`, `schemaVersion` + `version`; every key required), a strict loader
`CraftAssuranceTuning.cs`, injected by the server host (Core never reads a file). Protect's effect is
structural (a `const`, commented), not tunable. No §10 row is owed (no number is level-derived).

**Acceptance criteria:**
- [x] Effective success = band chance + load × bonus, computed in `long` widened before multiplying;
      enough loads reach exactly 1000 and the attempt always succeeds; a load past certainty is refused
- [x] A missing key throws; a ratio outside `[0, 1000]` is a load rejection naming the key
- [x] The host loads `craft-assurance.v1.json` in the same commit that creates it

**Verification:**
- [x] `dotnet test gk-core/tests/FusionRpg.Core.Items.Tests --filter "FullyQualifiedName~Enhance"`
- [x] `python gk-core/scripts/audit-magic-numbers.py --targets M1`; `python gk-core/scripts/audit-overflow.py`
- [x] `.\scripts\verify-change.ps1 -Paths <every touched path> -Session <id>`

**Dependencies:** None
**Files:** `gk-core/src/FusionRpg.Core/Items/Mutation/EnhancePolicy.cs`,
`gk-core/src/FusionRpg.Core/Items/Mutation/CraftAssuranceTuning.cs` (new), `gk-core/data/tuning/craft-assurance.v1.json`
(new — `v1` creation, parent §5 last row), `gk-core/src/FusionRpg.Server/Program.cs`, tests
**Size:** M · *(spec: `craft-assurance`)*

---

#### Task T42: `craft-assurance` d — paid ward and assure: lines, not flags, in one transaction
**Description:** The enhance request carries **assurance lines** (ids + counts). The workbench coalesces
them to one line per id, appends them to the recipe's `MaterialCostLine` list, and passes the union to
the **one** `TrySpendAndApply` call — so insurance debits with the craft, replays idempotently on the
same `correlation_id`, and an insufficient stack refuses the whole attempt through the shipped
shortfall path. `EnhanceContext.WardLoaded`/`AssureLoaded` are **derived from that same list** — never
a separate request count (two inputs is the exact shape of the original defect). **Spent on load,
whatever the outcome** (§ Design 4). An `assure` line on a verb that does not roll a success die
(today: anything but `Enhance`) refuses by name. File the `ssot-enhancement.md` §7.6 amendment
(odds-raising protection; `ward.enhance` → `assurance.protect`, answered by R-G1) as an `item-map.md`
row in the same commit.

**Acceptance criteria:**
- [x] ⭐ A player with enough `assurance.assure` reaches 100% on an enhance through the endpoint, stack
      debited; a protect-loaded peril failure keeps the level, one unit debited in the same transaction
- [x] No stock ⇒ the whole attempt refuses (no level change, no recipe debit, no op row); a protected
      attempt that succeeds still debits; a replay with a **different** load on the same
      `correlation_id` returns the recorded outcome and debits nothing
- [x] The policy's loaded counts equal the debited line counts — enforced by construction (there is no
      second input to forge: `AssureLoaded`/`WardLoaded` are derived from the SAME coalesced lines that
      get debited); a duplicated id sums into one debited line

**Verification:**
- [x] `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~Workbench"` (0 tests match —
      no Data.Tests class is named `*Workbench*`; the real `TrySpendAndApply` transaction this task
      wires is instead exercised end to end by the new Server.Tests below)
- [x] `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~Workbench"`
- [x] `.\scripts\guard-dal.ps1`; `.\scripts\verify-change.ps1 -Paths <every touched path> -Session <id>`

**Dependencies:** T39, T40, T41
**Files:** `gk-core/src/FusionRpg.Server/ItemWorkbench.cs`, `WorkbenchEndpoints.cs`,
`docs/architecture/item/ssot-enhancement.md` (+ the ask row in `item-map.md`), Data + Server tests
**Size:** M · *(spec: `craft-assurance`)*

---

#### Task T43: `craft-assurance` e — *protect* covers craft wear past exhaustion
**Description:** One effect, one id, two call sites — never a second "craft ward". Past potential
exhaustion (T24), an attempt with a debited `assurance.protect` line applies **no** craft-wear
decrement; an unprotected one decrements as T24 built. Extend the `Allows` arm to the verbs T24 makes
decaying, and let those verbs accept assurance lines through the same coalesce-and-append path T42
built for `Enhance`.

**Acceptance criteria:**
- [x] Past exhaustion, a protected attempt leaves `durability_current` unchanged; an unprotected one
      decrements by the craft-wear formula
- [x] Protect is debited in the one transaction on every decaying verb; replay decrements and debits
      nothing twice
- [x] No destroy outcome on the craft path; no new `CraftOperation`/`MutationOpKind`

**Verification:**
- [x] `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~InstanceOp"`
- [x] `dotnet test gk-core/tests/FusionRpg.Core.Items.Tests --filter "FullyQualifiedName~CraftRisk"`
- [x] `.\scripts\verify-change.ps1 -Paths <every touched path> -Session <id>`

**Dependencies:** T24, T42
**Files:** `gk-core/src/FusionRpg.Core/Items/Materials/CraftRiskPolicy.cs`, `CostClassMatrix.cs`,
`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.InstanceOps.cs`, `gk-core/src/FusionRpg.Server/ItemWorkbench.cs`, tests
**Size:** S · *(spec: `craft-assurance`)*

---

#### Task T44: `craft-assurance` f — *repair* coverage leg; *protect* refused on repair (R10)
**Description:** `assurance.repair` is an optional leg on T23's workbench repair: each loaded unit adds
`repairCoverageBonusMilli` to `RepairPolicy.Resolve`'s material coverage. **R10:** the repair destroy
chance stands as the durability sink — no assurance effect suppresses or reduces it, and an
`assurance.protect` line on a repair attempt is **refused by name**. No new verb, `CraftOperation` or
`MutationOpKind`.

**Acceptance criteria:**
- [x] Each loaded `assurance.repair` raises coverage by `repairCoverageBonusMilli`; the destruction
      chance is byte-identical with and without it
- [x] `assurance.protect` (and `assure`) on a repair attempt refuse by name, debiting nothing
- [x] The repair leg debits in the one transaction; replay is idempotent

**Verification:**
- [x] `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~InstanceOp"`
- [x] `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~Workbench"`
- [x] `.\scripts\verify-change.ps1 -Paths <every touched path> -Session <id>`

**Dependencies:** T23, T40, T41
**Files:** `gk-core/src/FusionRpg.Core/Items/*/RepairPolicy.cs`, `CostClassMatrix.cs`,
`gk-core/src/FusionRpg.Server/ItemWorkbench.cs`, tests
**Size:** S · *(spec: `craft-assurance`)*

---

#### Task T45: `craft-assurance` g — boss-only sourcing: the validator rule and the first boss entries
**Description:** `DropTableValidator` refuses an `assurance.*` material entry not on the boss channel
(`AffixChannels.Boss`, `DropTableModel.cs:46-50`) as `drop.assurance-non-boss` under the existing
`ContentRuleViolated{drop.*}` namespace — never a new code. Closed through `Table` recursion: an
`assurance.*` entry in a sub-table is legal only if **every** `Table` entry reaching it is itself on
the boss channel; otherwise refused naming the referencing table. A mislabelled trash table is not
detectable — T46's report covers that as visibility, not proof. Author the first boss-channel
`assurance.*` entries in `gk-data/packs/fusion/data/seed/loot/**` (authored corpus, module 11) so the consumables are
farmable; their weights are first values, tuned in T49.

**Acceptance criteria:**
- [x] Off-channel `assurance.*` entry refused with `drop.assurance-non-boss`; on-channel accepted
- [x] A sub-table `assurance.*` entry reached through a `drop`-channel `Table` entry is refused, naming
      the referencing table; no new error code
- [x] Each of the three ids drops from at least one boss-channel entry and credits the shelf (T29's path)

**Verification:**
- [x] `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~DropTable"`
- [x] `dotnet run --project gk-forge/tools/ItemSeedValidator`
- [x] `.\scripts\verify-change.ps1 -Paths <every touched path> -Session <id>`

**Dependencies:** T40, T29
**Files:** `gk-core/src/FusionRpg.Core/Items/Drops/DropTableValidator.cs`, `gk-data/packs/fusion/data/seed/loot/**` (boss tables),
`tests/FusionRpg.Core.Tests/Items/Drops/`
**Size:** S · *(spec: `craft-assurance`)*

---

#### Task T46: `craft-assurance` h — the gamble-vs-assurance report
**Description:** Beside `CraftingHorizonReport` (`Items/Mutation/CraftingHorizonReport.cs`), computed
from shipped tuning only: per enhance level, the **expected** material cost of gambling to the next
level (success chance, downgrade risk, craft wear) against the cost of certainty (consumables needed ×
their expected farming cost from boss drop rates); plus assurance yield **per `LootSourceRow`**
(`source_kind:source_id`) so a boss-only consumable dropping from a trash source is visible. Printed,
**never asserted** — the right ratio is a balance judgement (R-G1's two failure modes).

**Acceptance criteria:**
- [x] The report prints per level from shipped tuning and the loot corpus, with no authored input
- [x] It prints per-source assurance yield
- [x] No test asserts a ratio, a drop count or a stock level — the test only proves it runs on the real
      tuning

**Verification:**
- [x] `dotnet test gk-core/tests/FusionRpg.Core.Items.Tests --filter "FullyQualifiedName~EnhancePolicy"` (where `CraftingHorizonReport` is exercised today) plus the new report's own test
- [x] `.\scripts\verify-change.ps1 -Paths <every touched path> -Session <id>`

**Dependencies:** T24, T41, T45
**Files:** `gk-core/src/FusionRpg.Core/Items/Mutation/` (new report beside `CraftingHorizonReport.cs`), its test
**Size:** S · *(spec: `craft-assurance`)*

---

#### ✅ Task T49: `craft-risk-ladder` + `craft-assurance` — the one-pass balance (R-G1)
**Description:** R-G1: `craftWearPerAttemptMilli`, the enhance bands, `assureBonusMilli` and the boss
drop weights are **one balance problem, tuned together**, reading T46's report — never one after the
other. Shipping first values was sanctioned; this is the pass that sets real ones. Each changed file
publishes `v{n+1}` through `publish.py`, host reader switched in the same commit (H7):
`deployment-hierarchy` **v3** (unless T24 already took it), `craft-assurance` **v2**, and — only if the
bands move — `enhancement` **v2** (⚠ not in the parent §5 ledger, which lists no `enhancement` publish
from this map; flagged in this revision's report). Boss weights are authored rows in `gk-data/packs/fusion/data/seed/loot/**`.

**Acceptance criteria:**
- [x] Every changed value cites the report line it was read from, in the commit body
- [x] Each publish is a new file with `v{n}` kept and the host reading the new one — no in-place edit
      (the loot corpus is the one substantive change and is the live, non-versioned file T45 already
      established the convention for; `deployment-hierarchy`/`craft-assurance` are deliberately left
      unpublished — see evidence fragment Findings 2/3, no report-backed reason to move either)
- [x] No test pins a tuned value or a ratio (validation-ssot)

**Verification:**
- [x] The T46 report re-run after the publishes, printed in the commit body — ⭐ *re-verified 2026-09-22 (lane sgc-4):*
      `CraftAssuranceHorizonReportTests` **5 passed** (the report renders from shipped tuning + the real corpus, the
      per-source yield covers every shipped source and all three assurance ids, and the boss table yields > 0 for all
      three after T45); the corpus change the pass made is still in place (`drop.exp.warpath-20h` carries the three
      `assurance-assure`/`-protect`/`-repair` groups, `gk-data/packs/fusion/data/seed/loot/tables.v1.json:755+`); the two tunings the pass
      deliberately did NOT move are still unmoved — `deployment-hierarchy.v4 → v5` differs **only** by
      `potentialCostPerVerb.upgrade` (T37's publish, `craftWearPerAttemptMilli` untouched), and `craft-assurance` is
      still **v1**
- [x] `dotnet test gk-core/tests/FusionRpg.Core.Items.Tests --filter "FullyQualifiedName~Enhance|FullyQualifiedName~CraftRisk"`
      ⚠ *project path corrected 2026-09-22 (lane sgc-4):* the tests live in the SPLIT `FusionRpg.Core.Items.Tests`
      project, not `gk-core/tests/FusionRpg.Core.Tests`. Re-run at the merged tip: **180 passed, 0 failed** (with
      `~Material|~CostClass`)
- [x] `.\scripts\verify-change.ps1 -Paths gk-data/packs/fusion/data/seed/loot/tables.v1.json,gk-core/data/tuning/deployment-hierarchy.v5.json,gk-core/data/tuning/craft-assurance.v1.json -Session species-gear-chain-4`
      — re-run 2026-09-22: **EXIT=0** (`drop-table-validator` + `seed-loot-data-seam` + `craft-assurance-tuning` +
      `deployment-hierarchy-tuning`, MAGIC-NUMBER GUARD OK)

⭐ **RE-VERIFIED AT THE MERGED TIP 2026-09-22 (lane sgc-4), no publish owed.** The pass's own conclusion still holds
under the rows that landed after it: nothing in the wear / enhance-band / assurance-bonus surface has a report-backed
reason to move (the report emits no wear number — Finding 2 — and the enhance bands and `assureBonusMilli` are
unchanged), so H7 has nothing new to publish. `craft-assurance` and `enhancement` stay at v1, `deployment-hierarchy`
at v5 (T37's `upgrade` potential row only), and the loot corpus carries the pass's one substantive change.

⭐ **THE PASS RE-EXECUTED AS A READING 2026-09-22 (lane sgc-4, on the manager's third request).** The report was
re-rendered from shipped tuning + the real corpus at this tip (`+9: 950‰ / 1 charge / 3.3 boss kills ... +25:
200‰ / 16 / 53.3 ... +30: unchanged`, the plateau being the peril band's soft floor; per-source lines now show
exactly the two boss sources nonzero, so Finding 1's fix holds). Every knob was re-read against the report:
`craftWearPerAttemptMilli` **50** (no report column exists), enhance bands (`safe`/`risk`/`peril`) and
`assureBonusMilli` **50** (the report derives from them; it asserts nothing — spec § Design 7), boss weights (6
boss-channel entries @300‰, 2 bosses × 3 ids, and 0‰ everywhere else — the intended boss-only shape). **Zero knobs
move, and none can honestly move on this evidence.**

⛔ **ERRATUM REQUESTED (manager).** The resumed instruction asked for `deployment-hierarchy` **v3**,
`craft-assurance` **v2** and `enhancement` **v2**. Those are this row's *original* targets and are stale:
`deployment-hierarchy` is at **v5** (v3 = T24, v4 = T26, v5 = T37 — a "v3" publish is a rollback, and `publish.py`
refuses an occupied version), and the other two have no report-backed reason to move. A publish needs target
numbers the spec deliberately leaves to a balance judgement (§ Tunables: *"Shipping first values is sanctioned;
calling them balance is not"*; § Design 7: the ratio *"asserts nothing"*). Either the owner supplies a target for a
named knob — then the next revision of that file publishes through `gk-core/tools/tuning/publish.py` with its host reader
switched in the same commit (**v6**/**v2**/**v2**, not v3) — or the manager records "no publish" as the pass's
outcome. Until then the row stays closed on the reading, and **no tuned value is touched**. Evidence:
`tasks/evidence-fragments/T49-pass-20260922.md`.

⭐ **THE INSTRUMENT WAS INCOMPLETE, AND IS NOW COMPLETE — 2026-09-22 (lane sgc-4, second pass on the same request).**
Spec § Design 7 requires the gamble column to carry **downgrade risk** and **craft wear**; the shipped report
computed neither (its own doc comment admitted the lower bound), so Finding 2's "no report line speaks to wear" was
a property of the INSTRUMENT, not of the balance. `CraftAssuranceHorizonReport` now adds
`gambleAttemptsWithDowngradeMilli` (the expectation under `EnhancePolicy.Resolve`'s own
`canDowngrade && level >= downgradeFromLevel` rule, unwarded: `E = 1/p` below the floor, `E = (1 + q·E(prev))/p`
above) and `craftWearPerMilleOfMaxGambling`/`…Certainty` (the same per-mille-of-max unit
`CraftRiskPolicy.WearFor` uses; no rate passed ⇒ no columns, so every pre-existing caller's output is unchanged).
5 new contract tests (`gk-core/tests/FusionRpg.Core.Items.Tests` **1407 passed**, `verify-change` **EXIT 0**).

⭐ **AND IT NOW SHOWS R-G1's FIRST FAILURE MODE WHERE THE LOWER BOUND COULD NOT.** From +17 up
(`downgradeFromLevel`, on the peril band's `successEndMilli: 200` soft floor) the downgrade-aware expectation
compounds: +17 **4979**‰ vs the naive 2272‰, +20 **36837** vs 2857, +24 **1 949 043** vs 4347 (448×), +30
**7 990 103 080** vs 5000. The wear column follows (at +24 the gamble route costs ~97 item-maxima of durability
against the certainty route's 50‰). *"A guarantee reachable only in theory"* — measured. Full artefact:
`tasks/evidence-fragments/t49-report-20260922.txt`; write-up `tasks/evidence-fragments/T49-instrument-20260922.md`.

⛔ **STILL NO PUBLISH, now for a decidable reason.** The completed instrument reduces the pass's open question to
two OWNER calls: (1) is the +24-and-above explosion intended (those levels are beyond shipped `ilvl_cap`, so
unreachable today) or a band shape to fix — either answer changes `enhancement.v2` and neither is an implementer's
pick; (2) the wear column now exists, so a stated target ("certainty should cost at most N item-maxima") makes a
`deployment-hierarchy.v6` publish citable. The publish path is proven ready for all three (**v6**/**v2**/**v2**
— not the briefed v3, which v5 already occupies). Absent those numbers, "instrument completed, no publish" is the
pass's outcome.

**Dependencies:** T43, T44, T46
**Files:** `data/tuning/deployment-hierarchy.v{n+1}.json`, `craft-assurance.v2.json`,
`enhancement.v2.json` (only if bands move), `gk-core/src/FusionRpg.Server/Program.cs`, `gk-data/packs/fusion/data/seed/loot/**`
**Size:** M · *(spec: `craft-risk-ladder`, `craft-assurance`)*

---
#### ✅ Task T52: set-planning — the topology classes as versioned data
**Description:** `S1` (`be608027`) revised `docs/architecture/species-gear-chain/spec-set-species-binding.md`
to the owner's ruling: `setClass` is a set's **declared topology class**, resolved deterministically from
the set's own declared topology, out of class templates that live in versioned tuning. This row builds
the data half. Three classes, with **no number in code**: `unique-species` (10 or 15 distinct roles,
bonus-tier ceiling exactly 2), `family` (>= 5 roles, ceiling 3), `general` (>= 2 roles, ceiling 4); the
ladder is tried most-restrictive-first in `resolutionOrder`. The universal "every set has a threshold at
2" rule is **read from `set-charm-gen.v1.json`'s `setShape.mandatoryThresholdPieces`**, never copied
(`tunables-ssot.md` section 2: that number belongs to whichever domain owns it).

**Acceptance criteria:**
- [x] `gk-core/data/tuning/set-topology.v1.json` carries the three classes as rows (member-role policy,
      bonus-tier ceiling, threshold template, `resolutionOrder`) — **shipped by `S2` (`5209971e`)**.
      ⛔ The `through gk-core/tools/tuning/publish.py - never hand-written` clause **cannot hold for a v1**: the
      tool exits 2 (`no existing set-topology.v*.json`) because it revises a domain and cannot create
      one, so the file was authored directly, as every domain's v1 in `gk-core/data/tuning/` was. Its values are
      already the tool's fixed point (a no-op publish exits 1), and `_meta.rebalance` names the publish
      path for every later change. **Erratum requested — filed as T57** with the measured exits.
- [x] `setgen/topology.py` loads it and exposes `resolve_class(entry)` exactly as the spec's ladder
      reads it: universal threshold invariants checked first (first at `mandatoryThresholdPieces`,
      strictly increasing, top <= distinct role count), then the first admitting class, and a shape no
      class admits **raises `SetTopologyError` naming the entry - no default, no fallback to `general`** —
      the function was named `resolve_entry` when `S2` landed and is **renamed in this commit** (14
      occurrences, 0 remaining) so the code reads exactly as the spec's ladder does; `-k topology` runs
      51 passed.
- [x] `memberRoleCount` counts **DISTINCT ROLES**, never raw member rows (a role shipping one row per
      frame contributes one point) - proven by a test, not by prose
- [x] The new `gk-core/data/tuning/**` file carries its `boundaries[]` owner row in the same commit (`TVB-F8`;
      `gk-core/data/tuning/**` is an `EnforcedRoots` member) — ⛔ **BLOCKED, denied path.**
      `python gk-core/scripts/guard-verification-boundaries.py` prints
      `VERIFICATION BOUNDARY GUARD FAILED / unmapped enforced-root file: gk-core/data/tuning/set-topology.v1.json`,
      so the row is owed and the guard is right — but `gk-core/scripts/verification-boundaries.v1.json` is outside
      this lane's fence and is pipeline-guarded. Filed as **T55**, which points at `TVB-F8`
      (`tasks/test-verification-boundary-todo.md:550`), the row that already owns this defect class.
- [x] No magic number: no threshold, role count or ceiling appears in `.py`/`.cs`; the tuning file is
      their only home — `python gk-core/scripts/audit-magic-numbers.py --summary` → `TOTAL 0 0 0 0 0`

**Verification:**
- [x] `python -m pytest gk-forge/tools/seedsmith/tests -q -k topology` (new tests) — **51 passed, 4177 deselected**
- [x] `python gk-core/scripts/guard-verification-boundaries.py` and
      `python gk-core/tools/tuning/resource_ownership.py --check` — re-measured 2026-09-21 by lane sgc-1 at the
      merged tip: **VERIFICATION BOUNDARY GUARD OK** (the manager placed the row the earlier note asked for)
      and **OK -- 166 generated edges match `aptitudes.v10.json`'s 166 resource edges exactly**
- [x] `python gk-core/scripts/anchor-ledger.py tasks/species-gear-chain-ledger.jsonl check` — `LEDGER OK`, exit 0

**Dependencies:** T27 (`S1` only, committed `be608027`)
**Files:** `gk-core/data/tuning/set-topology.v1.json`, `gk-forge/tools/seedsmith/seedsmith/adapters/items/setgen/topology.py`
**Size:** M · *(spec: `set-species-binding` "The set-planning system"; lane `sgc-2`)*

✅ **CLOSED 2026-09-21 — the gate is green.** The KindCatalog mirror landed at the manager plane
(`006dcd7b`, merged here as `5d79eeab`) and `dotnet run --project gk-forge/tools/ItemSeedValidator` now reads
**PASS — 3957 entries across 1013 files, 2591 warnings, 0 errors**. The boundaries criterion closed the
same day when the manager placed the `tuning-set-topology` row at its own plane. Final line readings at
this tip: `-k topology` 51 passed; boundary guard OK; `resource_ownership.py --check` OK (166 edges).
Evidence: `tasks/evidence-fragments/T52.md`.
Lane sgc-1's own re-measurement the same day: `ledger check` **LEDGER OK**, `-k topology` **51 passed, 4232 deselected**, boundary guard **OK**, `resource_ownership.py --check` **166 edges match**.

---

#### ✅ Task T53: set-planning — `set-charm-gen` emits `setClass` forward — **backed by `b7463f6d` (`S3`) + `tasks/evidence-fragments/T53.md`**
**Description:** With the classes as data (`T52`), `set-charm-gen` emits `setClass` for every newly
generated set entry, resolved through the ladder - never assigned by the model, never defaulted. A shape
the ladder refuses fails the generation with the entry named, exactly as an unresolvable `creature.*`
`themeKey` already fails.

**Acceptance criteria:**
- [x] Every newly generated set entry carries `setClass`, plus `speciesId` (a real id or an explicit
      absent, already built) — `test_set_charm_gen.py` 104 passed / 2677 subtests
- [x] The emitted class is the ladder's decision for that entry's declared topology, and a test proves a
      refused shape fails generation rather than emitting `general` —
      `test_the_emitted_class_is_the_one_the_emitted_entry_resolves_to` (re-resolving the emitted entry
      agrees) and `test_an_unclassifiable_shape_refuses_at_emission_rather_than_shipping`
- [x] The generator is the only author: no shipped set entry is hand-edited to gain the field — `S4`'s
      corpus diff is a pure insertion (`884 files, 910 added, 0 deleted`, 0 lines that are not
      `setClass`) produced by `items repair-set-class --write`; a second run reports 0 changes, and the
      field is neither a brief field nor in the answer schema

**Verification:**
- [x] `dotnet run --project gk-forge/tools/ItemSeedValidator` (must stay green: 41 -> 0 on this line) — **NOW PASS: 0 errors**, 3957 entries / 1013 files / 2591 warnings, after the manager applied the KindCatalog mirror (head `006dcd7b`, merged as `5d79eeab`). Measured before that:
      2026-09-21 after the merge: **910 errors, every one `unknown key 'setClass'`** across 884
      partitions. The 41 pre-existing `combinations/**` errors are **gone** (a merged lane fixed them),
      so on this line 41 -> 0 **holds**, and the only remaining red is the one-field C# mirror filed as
      T56.
      ✅ **Re-measured 2026-09-21 by lane sgc-1 after T56 landed:** `PASS — 3957 entries across 1013 files,
      2591 warnings`, zero `setClass` findings. The line is green, not merely annotated.
- [x] `python -m pytest gk-forge/tools/seedsmith/tests/test_set_topology.py gk-forge/tools/seedsmith/tests/test_topology_repair.py gk-forge/tools/seedsmith/tests/test_set_charm_gen.py gk-forge/tools/seedsmith/tests/test_species_repair.py -q` - report the numbers printed — ✅ **the filter was defective** (`-k setgen` matched test NAMES; no test carries it: `4228 deselected`, exit 0, a green-looking no-op). **Fixed by T57**: the line now names the four set-digit files by PATH — **167 passed, 3584 subtests passed in 35.05s**. Fix the line rather than trusting it (filed in T57).
      ✅ **Re-measured 2026-09-21 by lane sgc-1** on the same four files plus topology/species-repair:
      `169 passed, 4114 deselected, 1 warning, 3584 subtests passed in 21.82s`. The filter defect was filed
      as T57 and **closed 2026-09-21 by lane sgc-4** — this line now names the files by path.
- [x] `pwsh -NoProfile -File scripts/run-guards.ps1 -Tier ci` — measured: **21 guard(s) run, 0 red**,
      exit 0 — the two lines above are annotated with their measured outcomes rather than ticked blindly:
      the ItemSeedValidator line is red **for T56's cause only** (the C# mirror), and the `-k setgen`
      line is defective (T57). Evidence: `tasks/evidence-fragments/T53.md`.

**Dependencies:** T52
**Files:** `gk-forge/tools/seedsmith/seedsmith/adapters/items/setgen/**`
**Size:** M · *(spec: `set-species-binding`; lane `sgc-2`)*

✅ **CLOSED 2026-09-21 — the gate is green.** The validator reads PASS (0 errors) on the merged tree,
and the row's own lines hold: the four set-digit files **167 passed / 3584 subtests** (the row's literal
`-k setgen` line selects zero tests — a defective filter, filed as T57 — so the equivalent was run), and
`run-guards -Tier ci` is red only on `doc-citations`, whose 21 HIGH findings are in seven *other*
programs' documents. Evidence: `tasks/evidence-fragments/T53.md`.

---

#### ✅ Task T54: set-planning — the shipped corpus brought onto the ladder, deterministically — **backed by `ca790b44` (`S4`) + `tasks/evidence-fragments/T54.md`**
**Description:** Re-plane the shipped sets onto the classes by **running the generator**, never by
editing seed JSON. `S1`'s measurement over `gk-data/packs/fusion/data/seed/items/sets/**` (910 entries in 885 files) reads
`general` 906 · `family` 4 · `unique-species` 0 · refused 0, and `unique-species` stays empty until a kit
is authored (`species-craft-ideal.md:125`: "no 10- or 15-role set exists"). **That tally is a reading,
never asserted**: the test asserts the closure property instead - every shipped entry resolves to exactly
one class, and every resolved entry satisfies its own class template.

⚠ *2026-09-21 (lane `sgc-2`), one honest deviation from the prose above:* the mechanism is a
**deterministic repair pass over the emitted corpus** (`setgen/topology_repair.py` — the same shape `T28`
used for `speciesId`), not a `set-charm-gen` re-run: a re-run would call a model for ~910 sets and rewrite
their authored identity (names, flavour), which is a content pass, not a re-plan. The criteria are met
exactly as written — code produced the corpus, never a hand edit.

**Acceptance criteria:**
- [x] Regenerated corpus: every shipped set entry carries `speciesId` and `setClass`, committed as code's
      diff (never a hand edit) — census `910/910` carry `setClass`, the 844 creature entries carry a real
      `speciesId`, the 66 `build.*`/`theme.*` entries carry it explicitly absent; the diff is
      **884 files, 910 added, 0 deleted, 0 lines that are not `setClass`**
- [x] The closure property is asserted (every entry resolves to exactly one class and satisfies its
      template); no test pins 906/4/0 or any other population count — `test_topology_repair.py` 16 passed;
      the tally only ever prints
- [x] The repair report prints the class tally as a reading —
      `{"entries": 910, "changedEntries": 910, "changedFiles": 884, "resolvedByClass": {"family": 4, "general": 906}}`
- [x] `decisions.md`'s **Set topology classes (2026-09-10)** row and `item/ssot-sets.md` section 3.4 stay
      the authorities for the class definitions the data encodes — neither file is touched; the tuning
      file's `_meta.owner`/`sources` cite them

**Verification:**
- [x] `dotnet run --project gk-forge/tools/ItemSeedValidator` green; `python -m pytest gk-forge/tools/seedsmith/tests -q`
      — **both now green/PASS**: validator **PASS — 3957 entries / 1013 files / 2591 warnings, 0 errors**
      after the manager applied the KindCatalog mirror; `verify-change` on this lane's paths
      **21 failed / 4259 passed / 3 skipped / 5003 subtests in 700.50 s** against the recorded baseline's
      22 / 4109 / 4994 (one fewer failure, +150 passes). The `<every changed path>` form of the next line
      still cannot select the corpus tree — `gk-data/packs/fusion/data/seed/items/sets/**` has no owner mapping (**T55**) — so the
      mapped subset above is the strongest achievable run. Original line, for the record:
      compared against the recorded pre-existing baseline (`tasks/reports/seedsmith-baseline-e0f1375d.json`)
      — the suite is **19 failed / 4206 passed / 5003 subtests** vs the recorded **22 / 4109 / 4994**:
      **0 new failures and 3 baseline failures gone** (`test_publish_is_idempotent` was this lane's T51
      fix; two item-adapter failures were a merged lane's). `ItemSeedValidator` is **910 errors, all 910
      `unknown key 'setClass'`**, 1:1 with the 910 entries and caused solely by the C# mirror — **T56**;
      regenerating cannot clear a C# schema rejection. A full run also leaves `git status --porcelain`
      **empty**
      ✅ **Re-measured 2026-09-21 by lane sgc-1:** `ItemSeedValidator` -> **PASS — 3957 entries / 1013 files /
      2591 warnings, zero `setClass`** (the gate the manager named). The suite reads **23 failed / 4257 passed /
      3 skipped / 5003 subtests in 643s** against the recorded base **22 / 4109 / 4994** — one more failure and 148
      more passes on a corpus grown ~150 tests since base sha `e0f1375d`. ⚠ The +1 is NOT attributed: naming it needs
      the failure-list diff against that stale baseline, i.e. another full ~11-minute run, which this closure did not
      spend. Reported as a reading, never as "0 new failures".
- [x] `.\scripts\verify-change.ps1 -Paths <every changed path> -Session species-gear-chain-20260920` —
      the corpus tree has **no boundary mapping** (re-confirmed by this lane 2026-09-21: it still throws `VERIFICATION BOUNDARY MISSING`; the mapped half of this row's files runs and reports `2 failed, 1085 passed, 1 warning, 3789 subtests`, both failures being the head's foreign actions-corpus gap and SSH5.12 chassis-subset check, so the strongest achievable check WAS run): `verify-change.ps1 -Paths gk-data/packs/fusion/data/seed/items/sets/abyssswordstar.json`
      throws `VERIFICATION BOUNDARY MISSING`. Filed as **T55** (`scripts/**`, outside this lane's fence);
      the mapped paths' runs are recorded in `sgc-2-S3.md` / `sgc-2-S4.md`
- [x] `pwsh -NoProfile -File scripts/run-guards.ps1 -Tier ci` — **`GUARDS OK - 21 guard(s) run, 0 red`**,
      exit 0. Evidence: `tasks/evidence-fragments/T54.md`

**Dependencies:** T52, T53
**Files:** `gk-data/packs/fusion/data/seed/items/sets/**`, the set generator, its tests
**Size:** L · *(spec: `set-species-binding`; lane `sgc-2`)*

✅ **CLOSED 2026-09-21 — the gate is green.** The merged tree reads `PASS` on the corpus gate and the
row's substance is unchanged: 910/910 entries carry `setClass`, the 844 creature entries carry a real
`speciesId`, the 66 `build.*`/`theme.*` entries carry it explicitly absent, the diff is 884 files / 910
added / 0 deleted / 0 non-`setClass` lines, the closure property is asserted with the tally only printed,
and `decisions.md` / `ssot-sets.md` §3.4 stay untouched authorities. Evidence:
`tasks/evidence-fragments/T54.md`.

⛔ - [ ] Every `decisions.md:132` citation naming the set-topology row cites it by **row name**
      (*"Set topology classes (2026-09-10)"*), or by the correct line, in both files
- [ ] `powershell -NoProfile -File scripts/guard-doc-citations.ps1 -Strict` still exits 0

**Verification:**
- [ ] `grep -rn "decisions.md:132" docs/architecture/species-craft-ideal.md docs/architecture/tier-system-ideal.md`
      returns nothing, or every hit names the row it means

**Dependencies:** None
**Files:** `docs/architecture/species-craft-ideal.md`, `docs/architecture/tier-system-ideal.md`
**Size:** XS · *(spec: `set-species-binding`)*

---

#### ✅ Task T51: seedsmith — the creature theme writers emit the OS line ending, dirtying a committed corpus file on every test run
**Description:** Filed by lane `sgc-2` 2026-09-21, found while running this lane's own test baseline:
a full `python -m pytest gk-forge/tools/seedsmith/tests -q` leaves
`gk-data/packs/fusion/data/seed/creatures/_registry/themes.v2.json` **modified in the working tree** — 17,491 CRLF line
endings against `HEAD`'s 17,491 LF (511,942 vs 494,451 bytes; the *parsed JSON is identical*, so the
diff shows nothing and only the bytes differ). Cause read directly: **three writers open the file for
text without `newline="\n"`, so `\n` becomes `os.linesep` (CRLF) on Windows** —
`gk-forge/tools/seedsmith/seedsmith/adapters/creatures/generate_themes.py:164` and `:250`
(`Path.write_text`, unpatched translation) and
`gk-forge/tools/seedsmith/seedsmith/adapters/creatures/theme_enrich.py:148`
(`os.fdopen(handle, "w", encoding="utf-8")`). The reachable caller is
`gk-forge/tools/seedsmith/tests/test_themes_v2.py:49-52` (`test_publish_is_idempotent`), which calls
`publish_v2(write=True)` against the **default `CREATURES_ROOT`** — the production registry — and
asserts the bytes are unchanged: on a Windows LF checkout it both rewrites the file and makes its own
assertion platform-dependent. Two sibling writers already shipped the fix and documented this exact
bug class (`name_repair._atomic_json`, `species_repair.py`'s inline writer, *"item-seed-regen cause
3"*). This is the same defect class one adapter over. Fix is one `newline="\n"` per writer plus a
`write=False`/temp-root sandbox for the idempotency assertion.

**Owning program (manager ruling, 2026-09-21): `seed-corpus`.** The fix belongs to the seedsmith
**creatures** adapter and the creature theme registry, both on that program's surface, and the
failing assertion is already one of the 15 pre-existing reds its
`tasks/seedsmith-generated-seed-repair-todo.md` row names
(`test_themes_v2.py::test_publish_is_idempotent`). The manager copied this row's cause read into
that row; this row stays as the finding's origin and closes when the owning row closes.

⚠ *2026-09-21 (lane `sgc-2`) — the fix landed **before** that ruling arrived.* `gk-forge/tools/seedsmith/**` is
inside this lane's fence, so the lane that filed the row fixed it in the same session (commit
`92674925`, evidence `tasks/evidence-fragments/T51.md`), and the fix is therefore **already in the
merged tree**: three writer sites pin `newline="\n"`, the idempotence test publishes into a private
corpus copy, and a read-only closure check compares a fresh publication against the committed registry.
`seed-corpus`'s owning row can close against that fragment; **nothing further is owed on this row**.

⚠ **Measured 2026-09-21 by lane `sgc-2`, the failure was ORDER-DEPENDENT and the `sgc-2` baseline run
hid it.** With `themes.v2.json` restored to the committed LF bytes,
`python -m pytest gk-forge/tools/seedsmith/tests/test_themes_v2.py -q` reported `1 failed, 3 passed`
(`test_publish_is_idempotent`) — the test read `first` as LF, `publish_v2(write=True)` wrote CRLF,
and the byte-identity assertion failed. In the lane's pre-change full-suite baseline it PASSED, because
an earlier test in that same run had already converted the file to CRLF, so `first` was already CRLF.
A red test that a fresh checkout fails and a polluted one passes is worse than either: it makes a
full-suite comparison between two lanes meaningless on line endings alone. After the fix: **5 passed**,
full suite **21 failed / 4176 passed** (the pre-lane baseline is exactly 21), and a full run leaves
`git status --porcelain` empty.

**Acceptance criteria:**
- [x] The three writer sites pin `newline="\n"`; each carries a comment naming why (the
      `name_repair._atomic_json` precedent)
- [x] `test_publish_is_idempotent` writes through a private copy of the registry, not the production
      path, and its byte-identity assertion passes on both an LF and a CRLF checkout — `.gitattributes`
      pins `* text=auto eol=lf` (its own comment: *"byte-exact test comparisons must not depend on host
      git config"*), so every checkout is LF by construction
- [x] A full seedsmith pytest run leaves `git status --porcelain` clean for
      `gk-data/packs/fusion/data/seed/creatures/_registry/**` — measured **21 failed, 4176 passed, 3 skipped, 5003 subtests
      in 579.13s**, then **0** dirty files under `gk-data/packs/fusion/data/seed/creatures` and 0 anywhere else in the tree
      (the same run before this fix left `themes.v2.json` at 17,491 CRLF line endings); the suite's
      failure set is back to the pre-lane **21, no new, none fixed**, so the spurious extra failure
      S4's comparison had to explain is gone

**Verification:**
- [x] `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/test_themes_v2.py -q` → **5 passed**
- [x] `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests -q; git status --porcelain gk-data/packs/fusion/data/seed/creatures`
      prints nothing
- [x] `.\scripts\verify-change.ps1 -Paths gk-forge/tools/seedsmith/seedsmith/adapters/creatures/generate_themes.py,gk-forge/tools/seedsmith/seedsmith/adapters/creatures/theme_enrich.py,gk-forge/tools/seedsmith/tests/test_themes_v2.py -Session sgc-2`
      → 8 failed / 919 passed, all eight being baseline names

**Dependencies:** None
**Files:** `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/generate_themes.py`,
`gk-forge/tools/seedsmith/seedsmith/adapters/creatures/theme_enrich.py`,
`gk-forge/tools/seedsmith/tests/test_themes_v2.py`
**Size:** XS · *(spec: `set-species-binding` — found by its lane's verification)*

---

#### Task T55: verification-boundaries — the seedsmith boundary cannot pass, and a new `gk-core/data/tuning` domain is unmapped
⚠ **Renumbered from T52 on the 2026-09-21 merge:** the manager's re-seeded planning rows took T52/T53/T54
for this lane's S2/S3/S4, so this finding row moved to **T55** and the `ItemSeedValidator` mirror below to
**T56**. Every cross-reference in this lane's evidence fragments was updated in the same commit.
**Description:** Filed by lane `sgc-2` 2026-09-21, found by running the verification this lane's own brief
mandates. Two defects in `gk-core/scripts/verification-boundaries.v1.json` (outside this lane's fence — the fix
is a registry owner's, and the file is pipeline-guarded):

1. **`gk-core/data/tuning/set-topology.v1.json` has no owner mapping.** `verify-change.ps1` throws
   `VERIFICATION BOUNDARY MISSING: gk-core/data/tuning/set-topology.v1.json` and stops. `gk-core/data/tuning/**` has a
   per-domain entry for essentially every published domain and **no glob fallback**, so *every new
   tuning domain* is unmapped on the day it is published and its lane has no path-owned verification
   until someone notices. Fix: an owner row for the new domain, or a `kind: "owner"` fallback on
   `gk-core/data/tuning/*.v*.json` (the anti-pattern the registry's own per-domain shape exists to avoid, so
   the owner row is probably right — the point is that the omission must not be silent).
   ⚠ **Precedent:** T31 hit this exact gap for `creature-yield.v1.json` and closed it with a one-row
   owner mapping named `creature-yield-tuning` — the same remedy applies here.
2. **The seedsmith boundary selects three tests that fail pre-existing on a clean HEAD and are not in
   `knownRed`.** `verify-change.ps1` for any `gk-forge/tools/seedsmith/**` path runs the seedsmith project and
   reports `UNEXPECTED FAILURE` for
   `tests/test_cli.py::test_actions_check_uses_domain_loader_and_excludes_round_scratch`,
   `tests/test_items_adapter.py::RegistryVersionTests::test_versions_are_read_not_a_single_hardcoded_constant`
   and `tests/test_items_adapter.py::LiveCorpusIntegrationTests::test_authored_item_names_are_unique_across_kinds`.
   All three are in the pre-change full-suite baseline (21 failed, 4115 passed — recorded in
   `tasks/evidence-fragments/sgc-2-S1.md`'s lane), so a lane that changes one seedsmith file cannot get
   a green `verify-change` no matter what it does. `knownRed` carries five `seedsmith` rows today, all
   `test_actions_description_completeness`; these three need rows (with their owning debt id) or
   disposition.

**Acceptance criteria:**
- [ ] `verify-change.ps1 -Paths gk-core/data/tuning/set-topology.v1.json -Session <id>` resolves a boundary
      instead of throwing, and a newly published `gk-core/data/tuning/<domain>.v1.json` is mapped on day one —
      ⭐ *measured 2026-09-22 (lane sgc-4):* **the first half is MET** — the command now plans
      `gk-core/data/tuning/set-topology.v1.json -> tuning-set-topology (module)` (the manager placed the row), no
      `VERIFICATION BOUNDARY MISSING`. ⛔ The second half is **not** met: there is still **no glob fallback**,
      so a new `gk-core/data/tuning/<domain>.v1.json` is unmapped on the day it is published unless its lane adds the
      row. The selected run then fails on the seedsmith suite (next line)
- [ ] `verify-change.ps1 -Paths gk-data/packs/fusion/data/seed/items/sets/abyssswordstar.json -Session <id>` resolves a
      boundary too — the item corpus's own tree is unmapped (`VERIFICATION BOUNDARY MISSING`), so the
      884-file path this lane's S4 rewrote has no path-owned verification command at all —
      ⭐ *measured 2026-09-22 (lane sgc-4):* **the mapping half is MET** — the command plans
      `seed-items-corpus (module)` **and** `seed-items-validator-seam (seam)`, plus the `generated-seed` guard
      and the `gen-item-seed-validator`/`gen-items-gate` scripts. The selected run then fails with
      `item seed corpus failed validation` — that is **T37's 498 authored armour `successorOf` rows** being
      flagged `SameStageReference`, i.e. T37's owed manager-plane exemption, **not** an unmapped tree
- [ ] `knownRed` names the pre-existing seedsmith failures (or they are fixed), so a seedsmith lane's
      selected run is green unless the lane's own change broke it — ⛔ *re-measured 2026-09-22 (lane sgc-4):*
      **still open, and the failing SET has moved.** The boundary's run reports **17 `UNEXPECTED FAILURE`s**
      (`test_cli::test_actions_check_uses_domain_loader_and_excludes_round_scratch` — the only one of the three
      this row named that is still red; `test_audit_doc_citations.RealTreeTests::test_the_real_scan_runs_and_produces_a_report`
      — this row's own cwd item; `test_general_propose` ×5; `test_guard_population_pin` ×2; `test_preflight`;
      `test_tree_plan_emit`; `test_usage_stats`; `test_corpus_loader`; `test_fusion_recipe`; `test_affix_authoring`;
      `test_channel_weight_backfill`; `adapters.trees.test_nodegen_vocab`), against **5 `KNOWN RED`** rows
      (`test_actions_description_completeness`, `SR-25`). The two other names the row listed
      (`test_versions_are_read_not_a_single_hardcoded_constant`, `test_authored_item_names_are_unique_across_kinds`)
      are **no longer red** — a merged lane fixed them. TVB owns the registry and this disposition.
      ⭐ *Re-measured 2026-09-22 (lane sgc-5), 12-file subset:* **14 failed / 310 passed → 12 failed / 312 passed**
      after this lane fixed `test_fusion_recipe` (a real defect) and `test_channel_weight_backfill` (a stale
      revision pin). ⭐ *Third pass, same lane, same date:* **→ 9 failed / 315 passed / 0 skipped** after three more —
      `test_tree_plan_emit` (a population pin; the cause is SE1.5's `325191c05` "remove the retired channel from
      code and publish the catalog", 55 → 54 entries, so the axis now asserts it MIRRORS the injected catalog),
      `test_nodegen_vocab` (three per-tag population pins; the cause is the tag-axis exclusivity repair
      `e1d9103ee`, `utility` 19 → 17, so it now asserts the closed tag vocabulary, one tag minimum per family,
      the generators' own exclusivity rule and both branches non-empty) and `test_affix_authoring` (a
      hand-listed 5-family population that grew to 9 when four more `atom.aura-*` families shipped all six
      element variants; the five the rule was built for are now a subset assertion, the derivation contract
      stays in its sibling test). ⛔ Still open, owner TVB: the 9 remaining are cross-program drift — six are
      SGC5-F1 (a gitignored runtime directory), two are SGC5-F2 (the removed family `atom.fx-overlay-damage`),
      and one is SGC5-F3 (the committed creature dump). Full classification, per-fix causes and the exact
      file:line: `tasks/reports/T55-evidence.md`. `test_guard_population_pin` did **not** fail in this lane's
      subset.
      ⭐ *Whole suite, measured in four chunks the same evening (each under ~16 min, none wrapped in the local
      `timeout` — see that fragment's hazard note: the wrapper replaces the child PATH with 10 entries and
      hides `dotnet`, which alone "fails" six rows that pass without it):* adapters+pipeline+workflow **586 / 0**;
      `test_[a-c]*` 10 failed / 863 passed; `test_[d-l]*` 8 failed / 1272 passed; `test_[m-z]*` 2 failed /
      1612 passed / 1 skipped → **14 failed, of which 5 are the five REGISTERED `knownRed`
      `test_actions_description_completeness` rows**, leaving exactly the 9 above. That is the program-wide
      figure this row has been owed since sgc-4 (17), re-measured.
      ⭐ *12-file subset re-measured 2026-09-23 (lane sgc-6), same files sgc-5 used:* **3 failed / 326 passed /
      1 skipped** (was 9 failed / 315 passed) — the six SGC5-F1 rows (`test_general_propose` ×5,
      `test_usage_stats` ×1) are green after that row's tracked fixture, so the subset moved **-6 failed,
      +11 passed**. The 3 that remain are exactly **SGC5-F2's two** (`test_cli::test_actions_check_uses_domain_loader_and_excludes_round_scratch`,
      `test_corpus_loader::ConfigFilesSurviveTests::test_loading_the_live_corpus_raises_no_findings_today`) and
      **SGC5-F3's one** (`test_preflight::test_hash_matches_the_real_committed_dump`) — all three already rows in
      this todo with their causes named, and all three needing an out-of-fence decision (an erratum for F2, a
      `gk-forge/tools/CreatureCorpusDump` mode for F3). Nothing is left unfiled, so this box's remaining work is the
      `knownRed` disposition for those rows, not a hunt. Also swept here: every live `-k` verify line in this todo
      still selects tests (`recipe` 107/4632, `requirement` 4, `theme` 87, `material` 54, `topology` 51 — re-measured
      at the end against a suite this lane's own cases grew from 4616) and every
      referenced `tools/*` project and `scripts/guard-*.ps1` resolves. Evidence:
      `tasks/species-gear-chain-sgc6-t55-redset.md`.
      ⭐ *PROGRAM-WIDE, measured 2026-09-23 (lane sgc-6) in three chunks that provably cover the tree (177
      top-level `test_*.py` files + the `adapters`/`pipeline`/`workflow` subdirectories), in the sanctioned
      environment:* `test_[a-l]*.py` **7 failed / 2227 passed / 3 skipped** (✅ *the derived form published in `11977b375` is now replaced by direct runs, 2026-09-23: `test_[a-c]*` 7 failed / 892 passed / 2 skipped + `test_[d-f]*` 865 passed / 1 skipped + `test_[g-i]*`+`test_[j-l]*` 470 passed — a single run exceeds the harness segment cap under contention*); `test_[m-z]*.py` **1 failed / 1778
      passed / 1 skipped**; `adapters`+`pipeline`+`workflow` **612 passed**. **Program-wide: 8 failed / 4617
      passed / 4 skipped**, and all 8 trace to **three** causes — the hand-authored `authored-basics.json` row
      (3: SGC5-F2's two plus `test_load_committed_reports_zero_loader_findings`), `committed-round-1.json`'s
      `action.family.academic.004` having no inline `description` (4, filed as SGC5-F4 — the one of 181 action-seed
      entries missing it), and the stale creature-dump manifest (1: SGC5-F3). ⚠ *Corrected 2026-09-23: this note
      first said two causes and attributed all 5 `knownRed` rows to the authored row; `--tb=line` disproves it, and
      the same lane then corrected the over-broad test contract behind one of those attributions (see SGC5-F4), which
      moved one more row from SGC5-F2 to SGC5-F4.* So there is no unfiled seedsmith debt left. Two environment factors were measured and are now diagnosed
      rather than opaque: `dotnet` off `PATH` adds 6 rows (`test_[a-l]` reads 13 instead of 7; fixed in
      `a41d5d152`) and a missing `workflow` extra adds 2 (`test_[m-z]` reads 3 instead of 1; `open_checkpointer`
      now raises `WorkflowEngineMissing` naming the extra — still a failure, never a skip).
- [ ] The seedsmith boundary's selected run is **cwd-portable**: it runs the project from
      `gk-forge/tools/seedsmith`, where `docs/` does not exist, so
      `tests/test_audit_doc_citations.py::RealTreeTests::test_the_real_scan_runs_and_produces_a_report`
      fails there (`assert 0 > 0`, `doc_count == 0`) and passes from the repo root — measured
      2026-09-21 both ways for the same file, 1.20s vs 6.18s. A repo-root-relative test may not be run
      from a directory the repo root is not
      ✅ **MET 2026-09-22 (lane sgc-5).** The test now chdir's to `REPO_ROOT` before the real scan (the pattern
      `DocCitationFixture.scan` already used, because the checker shells out to `git ls-files` against the
      PROCESS cwd). Measured both ways: `gk-forge/tools/seedsmith` **1 failed → 23 passed**; repo root **23 passed**;
      the boundary's own invocation from `gk-forge/tools/seedsmith` exits **0**. File:
      `gk-forge/tools/seedsmith/tests/test_audit_doc_citations.py`.
- [ ] A lane's `verify-change` outcome is attributable to that lane's diff
      ⭐ *Partial, measured 2026-09-23 (lane sgc-6).* One whole class of unattributable red is closed: six
      rows (`test_combogen` ×3, `test_item_name_repair` ×3) reported `FAILED` with a bare
      `FileNotFoundError: [WinError 2]` when `dotnet` was not on `PATH` — a failure that looks exactly like a
      content defect and is not attributable to anyone's diff. All six pass with `dotnet` present, so they were
      environment artifacts; `seedsmith.tooling.run_tool` now raises each module's own documented refusal naming
      the executable, and a missing tool is still a FAILURE (no `Skip` added). The remaining half of this box is
      the `knownRed` disposition on the line above. Evidence: `tasks/species-gear-chain-sgc6-tool-refusal.md`.

**Verification:**
- [ ] `.\scripts\verify-change.ps1 -Paths gk-core/data/tuning/set-topology.v1.json -Session sgc-2`
- [ ] `.\scripts\verify-change.ps1 -Paths gk-data/packs/fusion/data/seed/items/sets/abyssswordstar.json -Session sgc-2`
- [ ] `.\scripts\verify-change.ps1 -Paths gk-forge/tools/seedsmith/seedsmith/adapters/items/setgen/topology.py,gk-forge/tools/seedsmith/tests/test_set_topology.py -Session sgc-2`

**Dependencies:** None
**Files:** `gk-core/scripts/verification-boundaries.v1.json`
**Size:** XS · *(spec: `set-species-binding` — found by its lane's verification)*

---

#### ✅ Task T56: `ItemSeedValidator` — mirror `setClass` into the C# `set` kind catalog (one row)
⚠ **Renumbered from T53 on the 2026-09-21 merge** — see T55's note.

✅ **APPLIED BY THE MANAGER 2026-09-21.** `KindCatalog.cs:112` now lists `setClass` and `:79` lists `successorOf`; the validator reads `PASS — 3957 entries / 1013 files / 2591 warnings, 0 errors`. The artifact below is kept for the record.

⭐ **READY-TO-APPLY PATCH (2026-09-21, lane `sgc-2`):** `tasks/species-gear-chain-T56-kind-catalog-mirror.patch`
— two array elements, `"setClass"` on the `set` row and `"successorOf"` on the `base-type` row (the
second is owed before sgc-1's successor-edge content pass authors its first row; measured: one injected
edge reports `UnknownKey 'successorOf' on kind 'base-type'`). Verified three ways: `git apply --check` is
clean; a temp copy of the whole tool with the patch applied prints **`PASS — 3957 entries across 1013
files, 2591 warnings`, 0 errors** on the real corpus; and the repository's own
`gk-forge/tools/ItemSeedValidator/**` is untouched (this lane's fence excludes it). One command for whichever plane
holds the fence: `git apply tasks/species-gear-chain-T56-kind-catalog-mirror.patch`.
**Description:** ⛔ **Filed by lane `sgc-2` 2026-09-21 as the ONE unmet acceptance line of its S4.** The
Python schema (`gk-forge/tools/seedsmith/seedsmith/adapters/items/kinds.py:69-80`) accepts `setClass` as an
optional field on kind `set`, and all 910 shipped set entries now carry one. The C# validator's own
hand-transcribed twin of that field list does not:

```
gk-forge/tools/ItemSeedValidator/Registries/KindCatalog.cs:112
-            extra: new[] { "themeKey", "theme", "members", "thresholds", "speciesId" }),
+            extra: new[] { "themeKey", "theme", "members", "thresholds", "speciesId", "setClass" }),
```

Until that lands, `dotnet run --project gk-forge/tools/ItemSeedValidator` reports **951 errors instead of 41** —
**exactly 910 new, every one** `UnknownKey [seed-contract.md §9] unknown key 'setClass' on kind 'set'`
(measured: `41 -> 951`, `910` occurrences of that string, 887 partitions touched). The 41 pre-existing
errors are all in `combinations/**` and unrelated. This is NOT a data defect and NOT a schema defect:
`item/entry-shapes.md` §11 states the kind→directory→namespace mapping "lives today only in
`KindCatalog.cs`, which exists precisely because nothing else does", and `seedsmith check`
(`63 gap, 580 note, 153 not_measured`, zero mentioning `setClass`) is the SSOT-side gate and is
unharmed. **`KindCatalog.cs` is outside lane `sgc-2`'s fence**, so the lane applies the corpus and
files this row rather than editing it — the alternative was withholding the whole re-plan over one
array element.

**Acceptance criteria:**
- [x] `KindCatalog.cs`'s `set` row lists `setClass` alongside `speciesId`
- [x] `dotnet run --project gk-forge/tools/ItemSeedValidator` returns to its pre-change error count (41 at
      2026-09-21, all in `combinations/**`) with zero `setClass` mentions
- [x] No entry's `members`/`thresholds` changed — the repair's own raw-diff proof stands

**Verification:**
- [ ] `dotnet run --project gk-forge/tools/ItemSeedValidator`
- [x] `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/test_topology_repair.py -q`

**Dependencies:** None (the corpus is already written; this is the reader)
**Files:** `gk-forge/tools/ItemSeedValidator/Registries/KindCatalog.cs`
**Size:** XS · *(spec: `set-species-binding`)*

---

### Checkpoint — Phase 6 (`craft-assurance`)
- [x] The free ward is gone: `wardLoaded: true` refused; protection only when stock is debited (T39, T42)
- [x] 100% enhance reachable through the endpoint with enough `assurance.assure` (T42)
- [x] Protected craft past exhaustion does not wear; repair coverage rises; protect refused on repair and
      the destroy chance untouched (T43, T44 — R10)
- [x] `assurance.*` drops only from boss-channel entries (T45); the report prints (T46)
- [x] No new error code, no new `CraftOperation`/`MutationOpKind`, no destroy outcome on the craft path

---

#### ✅ Task T58: `setClass`'s RUNTIME consumer is module 25's planned contract, not a missing reader (filed, then corrected, by lane sgc-1 2026-09-21)
**What the audit found (measured):** `grep -rn "setClass" --include=*.cs src/` and the same over
`gk-web/web/fusion-rpg-web/src` return **zero** hits; the only readers are the generator
(`gk-forge/tools/seedsmith/seedsmith/adapters/items/setgen/{seedfile,topology,topology_repair}.py`, `kinds.py`) and the
validator's registry row (`gk-forge/tools/ItemSeedValidator/Registries/KindCatalog.cs`).

**⚠ And what the specs say about that — which is why this row is TRACKING, not a defect.** I first filed this as
"emitted and unread", then checked the designs before leaving it:
- the **authoring-side consumer exists and reads it** — `setgen/topology.py:376` resolves each entry's class and
  writes it as `setClass`, which is the consumer `spec-set-species-binding.md` §"What the class does *not*
  decide" designates (the class is "the shape the planner resolves a template *into*");
- the **runtime-side consumer is module 25's planned contract**, not an oversight: `spec-set-requirement-
  reconciliation.md:27-33` declares `SetIdentityRequirement { setId, setClass, requiredFamilyId?, … }` from the
  "deterministic Set Topology Plan", and that module is specced-but-unbuilt;
- the sibling comparison that made the gap look suspicious (`speciesId` read at runtime via
  `Items/Thresholds/SetCorpus.cs`) does not apply: `SetCorpus` carries `speciesId` because the *set binding*
  needed it then, while `setClass`'s runtime reader is the module that has not been built yet.

**So the shipped T52/T53/T54 work is not defective** — the field is read by its designated authoring consumer,
and the parent's "a row nothing reads is a lie in a table" rule is satisfied on that side. This row exists so
the runtime half is not forgotten: when module 25 lands, its `SetIdentityRequirement` contract must read the
class through the normal path.
**Acceptance:** module 25's reconciliation reads `setClass` for a real set and proves it with a test that enters
through that host; or the class is declared authoring-time-only in `ssot-sets.md` §3.4 with the reason recorded.
**Files:** the module 25 build (`spec-set-requirement-reconciliation.md`), `docs/architecture/item/ssot-sets.md`.
**Size:** S (tracking) · *(spec: `set-species-binding` §"What the class does not decide"; route to whoever owns module 25)*

✅ **CLOSED 2026-09-21 (lane sgc-4) via the second branch.** `ssot-sets.md` §3.4 now declares the class
**authoring-time-only in v1 — a declaration, not a gap**: the generator resolves it and `ItemSeedValidator`
checks it, its runtime reader is module 25's `SetIdentityRequirement` (`spec-set-requirement-reconciliation.md`),
which is still UNBUILT, so nothing may infer a template/threshold/bonus/family from the class and it is not a
persisted field until that module proves its reader through its own host. The edit is **line-count neutral**
(the two §3.4 paragraphs were compressed into the same eleven lines) so the six `ssot-sets.md:<line>` citations
pointing past it (`:187`, `:287`, `:345`, `:370`, `:829`) keep their line numbers — re-anchoring `:829` would have
needed `docs/architecture/species-craft-ideal.md`, outside this lane's fence. `guard-doc-citations.ps1 -Strict`:
same pre-existing HIGH set, no `ssot-sets.md` finding. Evidence: `tasks/evidence-fragments/T58.md`.

---

**Bounding sweeps 2026-09-21 (same lane), both NEGATIVE — recorded so nobody re-runs them expecting findings:**
1. **Every `.json` name `src/` references exists on disk.** 89 distinct names appear as literals in `src/**/*.cs`;
   the 12 that are not under `gk-core/data/tuning/` all resolve in the seed tree (`gk-data/packs/fusion/data/seed/dungeon/_registry/*`,
   `gk-data/packs/fusion/data/seed/commanders/_registry/…`, `gk-data/packs/fusion/data/seed/saves/_registry/…`, `gk-data/packs/fusion/data/seed/external-reference/…`,
   `gk-data/packs/fusion/data/seed/items/_tuning/tier-bands.v1.json`). So there is no missing-tuning boot crash at this head.
2. **The seed tree has NO dark file, and the reason is structural.** 77 registry/tuning domains under
   `gk-data/packs/fusion/data/seed/**` were checked the same way; 41 looked dark by name, but every one of those is read through a
   DIRECTORY (a glob or a dir literal — `passive-tree/plan/*.json`, `items/_seed/*.json` and friends), so the
   individual filename never appears in code. Excluding directory-read trees leaves **0**. ⭐ That is exactly why
   this register's ten findings are real: `gk-core/data/tuning/**` is read **by name** (every host names its file), so an
   unread name there means an unread file — while a seed-tree name being absent from code means nothing.

#### Task T59: routed register — nine more tuning domains whose LATEST revision no code reads (filed by lane sgc-1, 2026-09-21)
**Why this row exists:** while auditing hubs and tunings for this program's own surfaces, a sweep found that of
111 tuning domains, the latest revision of **ten** is named nowhere in any code (checked across `src/`, `tools/`,
`gk-web/web/fusion-rpg-web/src/` and `scripts/`). One of them belongs to the power program and is filed there
(`tasks/power-todo.md` AUDIT-1: `power-predicate.v1.json`, never loaded while its hub silently defaults). The
other nine are listed here because this lane cannot tell which program owns each — the manager routes them:

| Latest revision, read by nothing | Likely owner |
|---|---|
| `achievement-titles.v1.json`, `achievement-titles-catalog.v1.json` | the achievements/titles program |
| `action-duration.v1.json`, `action-shares.v1.json` | the actions program |
| `actor-hud.v2.json` | ✅ **RESOLVED 2026-09-21 — an H7 violation, filed as `tasks/actor-hud-todo.md` AUDIT-1:** the Injector still loads `actor-hud.v1.json` (`RpgHost.cs:203`) while v2 differs in `worldYOffset` (0.08 vs -0.35), so the published change never took effect |
| `creature-pipeline-health-targets.v1.json`, `creature-variant-count.v1.json` | the creature/seed-corpus program |
| `movement-payload.v1.json` | the movement/board program |
| `items.v1.json` | the item program |

**Method (so it can be re-run):** for each `gk-core/data/tuning/<domain>.v<n>.json`, take the highest `n` and grep the
filename across `src/**/*.cs`, `tools/**/*.{cs,py}`, `gk-web/web/fusion-rpg-web/src/**/*.{ts,tsx}` and `scripts/**` —
excluding `bin`/`obj`/`__pycache__`. The v{n-1} files that still exist are *expected* to be unread (publish.py
keeps them for revert); only a domain's LATEST revision being unread is a finding.
**Acceptance:** each listed file either gains a reader in the same commit that publishes it (H7) or is deleted
with the decision recorded by its owner.

⭐ **Re-measured, corrected, and one domain CLOSED — 2026-09-21 (lane sgc-4).** Re-ran the row's own method on
this head (111 domains; latest revision per domain; filename grepped over `src tools gk-web/web/fusion-rpg-web/src
scripts`) → **10 dark, the same ten**. But the method over-reports: it greps the FILENAME, and a reader may BUILD
it (`f"<domain>.v{int(version)}.json"`). A second pass over every consumer of each domain classified all ten:

| Latest revision | Verdict on this head (evidence) |
|---|---|
| `creature-pipeline-health-targets.v1.json` | ✅ **READ — false positive.** `gk-forge/tools/seedsmith/seedsmith/metrics/pipeline_health.py:24` reads it (`TUNING_DIR / f"creature-pipeline-health-targets.v{int(version)}.json"`) |
| `creature-variant-count.v1.json` | ✅ **READ — false positive.** `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/anchor/derive.py:241` reads it (`VARIANT_COUNT_TUNING_DIR / f"creature-variant-count.v{int(version)}.json"`) |
| `items.v1.json` | ✅ **CLOSED by this lane (in fence), RE-LANDED 2026-09-22.** `ItemsTuningHub` had **no production `Configure` at all** — only test bootstraps (`gk-core/tests/FusionRpg.Core.Tests.Shared/ContractTuningTestBootstrap.cs:128`, `gk-core/tests/FusionRpg.Data.Tests/…:166`, `gk-core/tests/FusionRpg.E2E.Tests/…:136`, `gk-core/tests/FusionRpg.Server.Tests/PowerAndAptitudeTuningTestBootstrap.cs:50`) — while `GET /api/items/{instanceId}/card` (`ItemCardEndpoints.cs:715`) reaches `ItemNameComposer.Compose`'s `RareNameThreshold` (`RpgStore.ItemCard.cs:329` → `ItemNameComposer.cs:32`), which THROWS with the hub unconfigured. `Program.cs` loads `items.v1.json` through `ItemsTuningLoader` into the hub, the same reader-in-the-host shape as SR-17's lawn-attrition line. ⛔ **The wiring was then silently DROPPED by the cross-lane merge resolution `8b81e395d`** (“Merge branch 'features/mega-merge' into cmdc/cai4”: the symbol appears twice before it, zero after), which restored the live defect; re-landed 2026-09-22 with the incident named in the source, and `ContentBootStartupWiringTests.The_server_boot_reads_the_latest_revision_of_the_domains_it_owns` now pins the latest-revision contract for this domain (and for `ai`, which the same resolution broke — see the filed row below) |
| `actor-hud.v2.json` | ⏸ **Already filed** — `tasks/actor-hud-todo.md:196` AUDIT-1 (the Injector loads `actor-hud.v1.json`; an H7 violation; owner: hud) |
| `power-predicate.v1.json` | ⏸ **Already filed** — `tasks/power-todo.md:1364` AUDIT-1 (owner: power) |
| `achievement-titles.v1.json`, `achievement-titles-catalog.v1.json` | ⛔ **DARK, routed** — achievements/titles program. `AchievementTitlesTuning.Parse` exists (`AchievementTitlesTuning.cs:27`) and no host reads the file; the catalog has no code at all. Its todo (`tasks/achievement-title-todo.md`) is outside this lane's fence |
| `action-duration.v1.json`, `action-shares.v1.json` | ⛔ **DARK, routed** — actions program. `DurationTuning.Parse` (`DurationTuning.cs:25`) is called by nothing; `action-shares` has no code at all. Its todo (`tasks/action-todo.md`) is outside this lane's fence |
| `movement-payload.v1.json` | ⛔ **DARK, routed** — movement/board program. `MovementPayloadTuningLoader.Parse` is called only by `gk-core/tests/FusionRpg.Core.Tests/Actions/Movement/MovementPayloadTests.cs`; no host builds one from the file |

**Method defect, for whoever re-runs this:** a filename-only grep cannot see a constructed reader name. The
second pass is `grep -rn "<domain>"` plus each hub/loader's own call sites (`*.TuningHub.Configure`,
`*Loader.Parse`) — which is what found the two false positives and the missing `items` reader.
**Files:** the owning programs' todos and `gk-core/data/tuning/**`.
**Size:** XS each (routing only, in this row).

---

#### ✅ Task T60: the upgrade launders wear and resets potential (filed by lane sgc-1, 2026-09-21)
**Found while auditing what the `Upgrade` write actually persists.** The transferred instance is a *new* one, and
`SaveInstanceUnlocked` writes neither `durability_current` nor `craft_potential_current/max`, so the successor's
pair is **derived fresh** from its own base type and rung — while the consumed instance's used fractions are
disposed with it. Measured:
- `gk-core/src/FusionRpg.Core/Effects/Atoms/Instantiator.cs`'s `InstanceRow` carries no durability and no potential field;
- `grep -n "craft_potential\|durability" gk-core/src/FusionRpg.Data/Sqlite/RpgStore.AtomInstances.cs` → **0 hits** in
  the insert that creates the successor;
- both pairs are **derived on first read** (`RpgStore.InstanceOps.cs:35,83` — `GetDurability`/`GetOrDerive`), so a
  successor starts at full durability and full potential by construction.

**Why it matters (two economy holes, one shape):**
1. **Durability is laundered.** A piece at 1% `durability_current` upgrades into a pristine successor — an upgrade
   is a strictly better repair than `Repair`, which is the verb that is supposed to own restoration (and whose own
   attempt can destroy the item, D1). "Upgrade to repair" is a free sink-free reset.
2. **Potential is reset.** This one the spec already anticipated and answered: `spec-item-upgrade-tree.md:543`
   (Open question 3) says the successor's potential should be derived afresh "with the *used fraction* carried
   across — otherwise upgrading becomes a potential-reset loop, which is the exact escape hatch the risk ladder
   exists to close". The shipped verb carries nothing, so the escape hatch is open.

**Fix — durability half DONE 2026-09-21 (lane sgc-1); potential half DONE 2026-09-22 (lane sgc-5).** `TryUpgradeAndApply` gained an
optional `successorDurabilityCurrent`, written on the SUCCESSOR's id inside the same transaction, and the verb
computes it from the two maxes the wear source already derives (input's stored pair, successor's derived max,
`checked`, divide last) and passes it; a bench with no wear source carries nothing rather than inventing a
number. Data test: a 25%-durability input upgraded with a 200-max successor lands at **50**, and with no carry
parameter the pair stays underived (`ItemUpgradeStoreTests` **7 passed**).
⭐ **The potential half's precondition landed with T61** (half A gave `CraftWearSource.PotentialMaxFor`; half B
made every craft spend the pair) — the blocker this row named ("no potential-max source") is gone.
`TryUpgradeAndApply` now takes `successorPotentialCurrent` and `ItemWorkbench.Upgrade` computes it off
`PotentialMaxFor` by the same rule (`checked`, multiply-first, divide-last, only `current` crosses, measured
against the input's DERIVED max exactly as durability does), writing only `craft_potential_current` on the
successor's id. **The carry IS the upgrade's potential consumption** — the successor's own max already absorbs
the input's spend, so a `potentialCostPerVerb[upgrade]` decrement beside it would charge one craft twice; none
is added. A caller with no ceiling carries nothing, leaving the pair underived rather than inventing a value.
⚠ **The durability half's own comment claimed its arithmetic was "pinned at the Server layer" and no such test
existed** (only the Data write was pinned); the new endpoint case pins both pairs' arithmetic.
**Both halves proven at BOTH layers:** the store tests (a 25%-of-400 input carrying 75 onto a 300-max successor;
no parameter ⇒ underived; both pairs in one transaction) and the real-endpoint test
(`item.humanoid-torso-a-001 → item.humanoid-torso-a-006` off the shipped corpus, both pairs at DIFFERENT
fractions — 1/4 durability, 1/2 potential — so a carry copied into the wrong pair cannot pass). Evidence:
`tasks/reports/T60-evidence.md`.

**Fix direction (design recorded in the spec, not implemented here):** carry the *used fraction* of both pairs into
the same transaction that saves the successor — `SetDurabilityCurrentUnlocked` for durability, the head-pair writer
for potential (`RpgStore.InstanceOps.cs:42`), both on the successor's id, inside `TryUpgradeAndApply`. The
alternative (refuse to upgrade a worn or potential-exhausted item) is a product decision and is NOT taken here.
**Acceptance:** a worn/decayed input yields a successor whose used fraction matches the input's, proven at the Data
layer through the real store; and `Repair` stops being dominated by `Upgrade` for restoration.
✅ **MET 2026-09-22 (lane sgc-5) for BOTH pairs, and the row CLOSES.** The Data-layer proof is
`ItemUpgradeStoreTests.The_successor_carries_the_used_potential_fraction_instead_of_a_fresh_max` (the potential
carry) and `Both_head_pairs_cross_in_the_same_upgrade`, beside T60's own durability case; `Repair` is no longer
dominated because neither pair resets on upgrade. `~ItemUpgradeStoreTests` **9 passed**; the endpoint case
carries the Server-side arithmetic.
**Files:** `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Workbench.cs`, `gk-core/src/FusionRpg.Server/ItemWorkbench.cs`,
`gk-core/tests/FusionRpg.Data.Tests/Items/ItemUpgradeStoreTests.cs`,
`gk-core/tests/FusionRpg.Server.Tests/ItemUpgradeEndpointTests.cs`,
`docs/architecture/species-gear-chain/spec-item-upgrade-tree.md`
**Size:** M · *(spec: `item-upgrade-tree`; owner: this program)*

---

#### ✅ Task T61: the potential pair was never derived or spent; both halves fixed (filed and closed by lane sgc-1, 2026-09-21)
**A whole shipped subsystem is inert, and the greps are unambiguous.** `CraftRiskPolicy` decides every craft's wear
from the item's **potential** pair:
`gk-core/src/FusionRpg.Server/ItemWorkbench.cs` `CraftWearFor` reads `_store.GetPotential(id).Current` (a RAW read), and
`CraftRiskPolicy.CanDecay(null) == false` by design — T10's own evidence line calls a not-yet-derived pair "Assured".
So with no pair ever written, **every craft returns null and nothing ever wears**.

**Nothing writes or derives it in production (measured 2026-09-21):**
- `grep -rn "SetPotential(\|GetOrDerivePotential\|craft_potential" --include=*.cs src/` excluding
  `RpgStore.InstanceOps.cs` → **0 hits** (the columns' only writer/deriver has no production caller);
- `grep -rn "HeadDerivationTables\.DeriveMax" src/ tests/ tools/` → **0 hits** — the derivation the spec's
  §Seedsmith/generator names (*"Potential and durability derive at load from the base-type registry's existing
  `class` field and the rung (`HeadDerivationTables.cs`)"*) is never called anywhere;
- `GetOrDerivePotential` is called only by a test (`gk-core/tests/FusionRpg.Data.Tests/Items/HeadPairTests.cs:66`);
- by contrast the SIBLING derivation is wired: `CraftWearFor` calls
  `_store.GetOrDeriveDurability(id, () => max)` with `max` from `CraftWearSource`, which is why T24's endpoint
  test passes.

**Why T24's own evidence did not catch it:** that test (`Enhance_pastPotentialExhaustion_decaysDurabilityThroughTheRealEndpoint`)
**sets the potential pair itself** before enhancing, so it proves the mechanism *given a pair* while production
never establishes one. The spec's `NULL is "not yet derived"` note is correct per-instance, but nothing derives.
**Consequence:** `craft-risk-ladder` Stages 2–3 (decay past exhaustion), T24's wear, the durability floor path and
T43's `assurance.protect` suppression are all unreachable in play; every craft is Assured forever.
**Half A — the DERIVATION — is DONE 2026-09-21 (lane sgc-1).** `CraftWearSource` gained `PotentialMaxFor` (built in `Program.cs` from the same base-type class + ladder rung as durability, through `PotentialTable.DeriveMax`, which honours the authored override first), and `CraftWearFor` now derives the pair when it is absent — **only** when absent, so a stored pair (a spend's own value) still decides the wear and a host without the source keeps its pre-T61 behaviour. Proven at the endpoint: a real enhance on a real base-type instance leaves the item with a DERIVED pair equal to `PotentialTable.DeriveMax(...)`, where it was NULL before; `~ItemWorkbench|~ItemUpgrade` **95 passed**. **Half B — the per-verb spend — remains.**

**Half B — the SPEND — is DONE 2026-09-21 (lane sgc-1), so T61 CLOSES.** `WorkbenchMutation` gained `PotentialCurrent` (written in the op's own transaction by a new `SetPotentialCurrentUnlocked`, mirroring the durability field beside it), and `PotentialAfter(target, operationId)` computes `max(0, current − potentialCostPerVerb[operationId])`. Five verbs spend: Enhance→`temper`, Promote→`elevate`, Reroll→the operation's own id, SocketImbue→`imbue`, Repair→`repair`. ⚠ The remaining priced verbs (`forge`, `forge-gem`, `upcycle`, `socket-add`, `socket-insert`) still do not spend, and `upgrade` cannot (its input is consumed) — named here rather than implied; each has a `potentialCostPerVerb` row waiting. **Proven at the endpoint, with the exhaustion produced by the SPEND itself:** one craft whose authored cost equals the derived ceiling takes `craft_potential_current` to 0 while durability is untouched, and the NEXT craft decays durability by `WearFor(max, rate)` — `~ItemWorkbench|~ItemUpgrade` **96 passed**.

⛔ **The defect has TWO unwired halves, not one (found while scoping the fix, same audit):**
1. nothing DERIVES the pair (above), and
2. nothing CONSUMES it — `grep -rn "PotentialCostPerVerb" --include=*.cs src/` returns **only the tuning
   record's own declaration** (`DeploymentHierarchyTuning.cs:23`), so `potential.byVerb`'s per-verb cost is
   parsed and never read: no craft ever spends a point, so even a derived pair would sit at its max and
   `CanDecay` would stay false. Both halves are needed before a single craft can wear, which is why the
   acceptance below forbids the test from setting a pair AND from faking the spend.

**Fix direction:** (a) derive on demand exactly like durability does — `_store.GetOrDerivePotential(id, () =>
HeadDerivationTables.DeriveMax(<base type class>, <rung>, <tuning>, <authored override>))` in `CraftWearFor`'s own
line, or persist at import. The spec's authored `potential.overrides` must keep precedence.
**Fix direction (b):** spend `potentialCostPerVerb[verb]` in the SAME transaction as the op, floored at 0, beside
the existing craft wear — the `WorkbenchMutation`/`SetPotentialCurrentUnlocked` shape the durability half
already uses (T60's fix is the template).

**Acceptance:** a real enhance past exhaustion decays `durability_current` through the endpoint **without the
test setting a pair first** (and therefore only after enough crafts have spent the derived potential down to
zero), and an authored override still wins over the derived max.
**Files:** `gk-core/src/FusionRpg.Server/ItemWorkbench.cs`, `gk-core/src/FusionRpg.Core/Items/Materials/HeadDerivationTables.cs`,
`gk-core/tests/FusionRpg.Server.Tests/ItemWorkbenchEndpointsTests.cs`.
**Size:** M · *(spec: `craft-risk-ladder` § Design 2; owner: this program)*

---

## Checkpoint — Complete
- [ ] A species-bound set piece above the threshold rung is enhanced with its own species' material,
      end to end
- [ ] An armour piece upgrades cleanly (T37); a weapon/offhand/jewel base type without an authored
      `successorOf` refuses by name, not by deriving from its class ladder (T38)
- [ ] All **20** modules green on their own spec's Success criteria (`socket-combat-wiring`'s arm 2 is
      `SSH combo-bind`'s, not counted here)
- [ ] Full regression at the parent's CC8 (the one full-suite point): Core/Data/Guard/Server/E2E +
      seedsmith pytest + `npm test`/`build`
- [ ] `deployment-hierarchy-map.md`'s and `item-map.md`'s filed notes are current, including the
      `Trophy`, `Assurance` and §7.6 ask rows
- [ ] **Ready for owner sign-off**

---

## Deferred

None. Both of this initiative's external blockers (`deployment-hierarchy` module 7 durability;
`item` module 23 `requirement-profiles`) were resolved by pulling a minimal, already-designed slice
of each forward — see T11/T23 and T35/T36. Remaining **content** gaps, named not built: authoring
`successorOf` values for ~800 non-armour base types (T38 builds the mechanism) — owed to whichever
program picks it up next; and `RaiseResolver.SpeciesFor`'s own selection fix (plan § Open questions 1).
**Not this program's:** combination-grant binding (arm 2) — `SSH combo-bind`.

---

## Filed by other lanes

- [ ] **SGC-F-dump-args — `CreatureCorpusDump` treats any unrecognised argument as a data directory, and its default path cannot run at all** · S · deps: — · *(filed by manager adjudication, 2026-09-27, from the leftover walk while adjudicating `corpus-bcu213`)*

  - **Defect 1 — no argument validation, and it writes.** `gk-forge/tools/CreatureCorpusDump/Program.cs`
    recognises exactly two forms: `--verify` (line 14) and `--base-stats` (line 39). Everything else
    falls through to the default run, where `args[0]` becomes a data directory (line 103,
    `new RpgStore(dataDir)`) and `RpgStore.Init()` **creates SQLite databases in it**. `--help` is
    therefore not a usage message; it is an instruction to create a server data directory named
    `--help`. **Measured, by this session's own mistake:** running `--help` produced **7.7 MB** at the
    repository root - `rpg-hot.sqlite` with `-wal`/`-shm`, `rpg-media.sqlite` with `-wal`/`-shm`, a
    `pre-save-identity` backup, and a 1-byte `archive`. All of it removed; the committed dump tree was
    never touched.
  - **The same footgun, ten days earlier.** A directory named `--check` sits at the repository root,
    dated 2026-09-17, holding the same shape (~1.7 MB: `rpg-hot.sqlite`, `rpg-media.sqlite`, `archive`).
    **Left in place on purpose** - it is untracked litter from this same tool bug, but it is not
    provably abandoned and deleting a live database is not recoverable, so it is surfaced rather than
    removed.
  - **Defect 2 — the default path can never succeed.** `CreatureCorpusDump` contains **zero**
    `LeadNames` mentions, so `LeadNamesHub.Configure(...)` never runs and the run dies with
    `System.InvalidOperationException: LeadNamesHub.Configure(...) has not run` at
    `RpgStore.Init() -> SeedPlayerIfEmpty -> OnboardingPlayerName`. **This is the same defect class
    already fixed for the seedsmith importer in `47c9d1f60`**, where read/parse/configure became one
    implementation (`LeadNamesHub.ConfigureFromFile`) with the server's `LeadNamesBoot` delegating to
    it. This tool was not included in that fix.
  - **Why CI is green and this is invisible.** `--verify` returns before any `RpgStore` is
    constructed, and `--verify` is the only form CI runs (`ci.yml:482`). Confirmed at this head:
    `dotnet run --project gk-forge/tools/CreatureCorpusDump -c Release -- --verify gk-data/packs/fusion/data/seed/creatures/_dump` →
    `is self-consistent (hash cc322647…)`, exit 0. So the tool's *verification* form is trustworthy and
    its *writing* form is unreachable.
  - **Why it matters here, concretely.** A corpus dump can be checked but never regenerated, by anyone,
    through the documented entry point. `corpus-bcu213` holds a **month-newer** capture
    (`capturedUtc 2026-09-17`, 5,480 lines, `spawn-baseline.json` +1663/-164 against integration) than
    the committed one (`2026-08-15`, 494 lines). Generated data is never hand-edited - the sanctioned
    path is to regenerate - so that capture **cannot be landed** until this row is closed. It is
    recorded as UNLANDED GENERATED DATA, *not verifiable as-is*, with the reason named rather than
    guessed at.
  - **Acceptance:**
    - An unrecognised argument is **refused with a usage message and a non-zero exit**, before any
      `RpgStore` is constructed. A refusal that creates a directory is not a refusal.
    - The default path configures the lead-names registry, by the same single implementation
      (`LeadNamesHub.ConfigureFromFile`) the seedsmith importer fix uses, so a regeneration run
      completes rather than throwing.
    - `dotnet run --project gk-forge/tools/CreatureCorpusDump -- <data dir> gk-data/packs/fusion/data/seed/creatures/_dump` then
      produces a dump, and `--verify` on it exits 0.
    - With regeneration working, decide the committed dump's disposition: re-record through the writer
      (which is what the `sgc-6` row above already asks for and marks not-achievable-in-fence), or state
      why the older capture is the one to keep. Either way the answer is recorded, because today the
      tree verifies and cannot be refreshed at the same time.
    - The stray `--check` directory at the repository root is removed, or its owner identified.


- [x] **T16-F1 — `test_publish_is_idempotent` mutates the production registry on its first run (CRLF)** · XS · *(filed by item-seed-gen ISG5, 2026-09-20)*
  - **Cause, read from the code.** `gk-forge/tools/seedsmith/tests/test_themes_v2.py:48-52` calls
    `themes_mod.publish_v2(write=True)` against the REAL `gk-data/packs/fusion/data/seed/creatures/_registry/` and then
    asserts byte-idempotence, so the test itself writes the production tree.
    `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/generate_themes.py:249`
    (`out.write_text(json.dumps(...) + "\n", encoding="utf-8")`) omits `newline=""`, so on Windows
    Python's text-mode newline translation rewrites the file LF -> CRLF. On a checkout whose working
    copy is LF the assertion then fails (`b'{\r\n...' != b'{\n...'`) AND the file is left changed;
    on a second run the file is already CRLF and the test passes — a stateful test that reports the
    environment, not a defect in the themes.
  - **Not fixed here:** this is the `themes.v2.json` migration's own program (T16); the fix is either
    `newline="\n"` on that write (matches `name_repair._atomic_json`'s own 2026-09-20 note) or
    pointing the idempotence assertion at a temp `root` so the test never writes production.
  - Acceptance: the test passes on a fresh LF checkout AND on a CRLF one, and leaves
    `gk-data/packs/fusion/data/seed/creatures/_registry/themes.v2.json` byte-identical (`git status` clean)
  - Verify: `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/test_themes_v2.py -q`
  - Files: `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/generate_themes.py`, `gk-forge/tools/seedsmith/tests/test_themes_v2.py`
  - ✅ **CLOSED 2026-09-21 (lane sgc-4), no code change owed.** T51's fix is in the merged tree and
    re-measured here: the three writers pin `newline="\n"`, `test_publish_is_idempotent` builds a
    PRIVATE corpus copy (`_private_corpus`, `tmp_path`) and asserts `b"\r\n" not in first`, and the
    sibling read-only closure test compares a fresh publication against the committed registry. Verify
    again on this head: `5 passed, 1 warning in 2.84s`, and `git status --porcelain gk-data/packs/fusion/data/seed/creatures`
    printed **nothing** both before and after the run. Evidence: `tasks/evidence-fragments/T16-F1.md`.

- [ ] **RECON-F6 — the "contract boxes" clause is invisible to a box counter** · XS · *(routed by the manager 2026-09-22 from `tasks/reports/backlog-reconciliation-20260921.md` §9, which lists it and deliberately does not file it: the lane's fence is `tasks/reports/**`.)*
  `tasks/species-gear-chain-todo.md:16-17`: the clause saying shipped tasks’ boxes are "the original contract" has no banner phrase, so any box-counting metric reads this file’s **240 unticked lines as open** (its real count is **6 open task blocks**). Either the clause gets a recognised banner or the metric learns it — this is the file whose apparent size drove a lane-count decision.
  - ⛔ **Examined 2026-09-22 (lane sgc-4): the banner option is NOT honest for this file, and the metric option is
    out of this lane's fence.** `RECONCILED_BANNER_RE = re.compile(r"closed by the header above", re.IGNORECASE)`
    (`gk-core/scripts/audit-program-pipeline.py:99`, per the reconciliation's §4.2) matches that phrase **anywhere in the
    first 15 lines**, so writing it into this header would declare the WHOLE file closed — false today, because
    T37, T55, T57 (one box) and T59 still have genuinely open rows. The clause at `:16-17` is scoped to *ticked*
    tasks only, which is exactly the distinction the counter cannot make. The honest fixes are (a) teach the metric
    the clause, in `gk-core/scripts/audit-program-pipeline.py` (**outside this lane's fence** — pipeline-guarded), or
    (b) add the banner only once this file has no open blocks. Not ticked, and not worked around.
  - ⭐ **RE-MEASURED 2026-09-23 (lane sgc-6) — the divergence is larger, and the lane brief that cited it was misled.**
    `python .claude/cmdc-agents/scripts/convergence-census.py` reads **`species-gear-chain 25 blocks 0 wip 240
    residue`** (its own header: "a block = one column-0 `- [ ]` row"), while this file's own block rule (heading
    marker → body `CLOSED <date>` phrase → column-0 `- [ ]`) finds **40 blocks carrying unticked column-0 boxes, of
    which 2 are OPEN: T37 (12 boxes) and T55 (8)** — T57 is closed by its body phrase and T59/T60 have no unticked
    column-0 boxes. ⚠ *Re-run at the end of this lane: the census reads **24** and T37 carries **8** unticked boxes,
    because this lane's `f41dd5e12` + `1561a9774` measured four of T37's five verify boxes. The figures above are
    the FIRST reading; the fragment carries both, and says the lane moved them.* So the census's 25 (and the lane brief's "26 open task blocks / 263 workable") is the line-level
    artifact this row names, and the block-level truth is **2**, both externally blocked. Full decomposition, with
    each block's exact external blocker: `tasks/species-gear-chain-sgc6-open-blocks.md`.

- [ ] **SG-ARTIFACT-1 — a cross-lane merge resolution silently reverted TWO `Program.cs` reader lines, one of
  which stopped the server booting** · S · *(filed 2026-09-22 by lane sgc-4; **owner: `empire-progression`** — I
  cannot write `tasks/empire-progression-todo.md`, it is outside this lane's fence, so this row lives here for the
  manager to route.)*
  - **Cause, read from the code.** `8b81e395d` (“Merge branch 'features/mega-merge' into cmdc/cai4”) resolved
    `gk-core/src/FusionRpg.Server/Program.cs` from a branch snapshot that predated three merged fixes. Two of them were
    reader lines, and the diff of that one merge commit is exactly: the `items` block removed (2 occurrences of
    `ItemsTuningHub` before, 0 after — species-gear-chain T59's fix), and `ai.v3.json` reverted to `ai.v2.json`
    (EP5.2 `2114445b6` had made the switch *in the same commit as the ai.v3 publish*).
  - **Impact, measured:** `WorldAiTuningLoader.Parse` requires the newest revision's `buildScorer` block
    (`gk-core/src/FusionRpg.Core/World/Ai/WorldAiTuning.cs:81`), which only `ai.v3.json` carries (`ai.v1`/`ai.v2` have none)
    — so the merged tip's server could not boot AT ALL: `gk-core/tests/FusionRpg.E2E.Tests` (`RpgApiFactory :
    WebApplicationFactory<Program>`) threw `WorldAiTuningRejection: ai tuning: missing or non-object 'buildScorer'`
    at `gk-core/src/FusionRpg.Server/Program.cs:294`. **2 E2E tests failed** there while T59's `items` defect stayed latent behind it.
  - **What this lane did:** restored BOTH lines (`ai.v3.json` for EP5.2, `ItemsTuningHub.Configure` for T59) with the
    incident named in the source, and pinned the H7 contract revision-agnostically in
    `ContentBootStartupWiringTests.The_server_boot_reads_the_latest_revision_of_the_domains_it_owns` (it reads the
    latest `items.vN`/`ai.vN` on disk and requires the boot to name it, so the next publish stays green and a
    reverted pin fails in a test rather than at boot).
  - **What `empire-progression` still owns:** nothing on the reader line (restored), but EP should know its publish
    was reverted in transit — if `ai.v3`'s values are ever revised again, the switch must be re-verified against the
    loader requirement, and the `buildScorer` thresholds (`continuityCooldownTurns: 3`, `*FitThreshold: 500`) are
    EP5.2's untuned starting values.
  - **Verify:** `dotnet test gk-core/tests/FusionRpg.E2E.Tests --filter "FullyQualifiedName~UnlockTuningActivation"` →
    **2 passed** (it was 2 failed before the restore); `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter
    "FullyQualifiedName~ContentBootStartupWiring"` → green; `verify-change.ps1 -Paths
    gk-core/src/FusionRpg.Server/Program.cs,gk-core/tests/FusionRpg.Server.Tests/ContentBootStartupWiringTests.cs -Session
    species-gear-chain-4` → EXIT 0, Server.Tests **797 passed**.
  - **Systemic note for the pipeline (out of this lane's fence):** the same single resolution dropped two
    independent lanes' lines, so this is a *merge-hazard on a shared hot file*, not two accidents. A generic H7 guard
    — for every `gk-core/data/tuning/<domain>.vN.json`, the host names the highest `N` — would cover the whole class; measured
    at this tip with the sweep in `tasks/evidence-fragments/T59-boot-regression-20260922.md`: **101 domains fine, 1
    stale (`actor-hud`, already filed as `actor-hud-todo.md:196`), 9 with no literal (constructed name or unread)**.

- [x] **SGC5-F1 — six seedsmith tests require a GITIGNORED runtime directory, so they can never pass in a fresh checkout** · XS · *(filed 2026-09-22 by lane sgc-5 out of T55's measurement; **owner: the actions program** (`gk-data/packs/fusion/data/seed/actions/**`), with the `knownRed` half in the verification-boundary registry — neither is in this lane's fence, so the row lives here for the manager to route, the way RECON-F6 and SG-ARTIFACT-1 do.)*
  - **Cause, read from the tree (not from a test name).** `.gitignore:113` ignores `/data/seed/actions/_candidates/`, so it is absent from every fresh checkout — measured here: `find data/seed/actions/_candidates -type f | wc -l` → **0**. T55's selected seedsmith run needs it in six places: `gk-forge/tools/seedsmith/tests/test_usage_stats.py::TestRealCorpusTests::test_the_real_corpus_loads_and_reports_without_error` (`assert report["acceptedCount"] > 0` → `assert 0 > 0`; `build_report(REPO_ROOT)` counts accepted action-candidate ROUNDS) and `gk-forge/tools/seedsmith/tests/test_general_propose.py::RealWorkedExampleTests` ×5 (`FileNotFoundError: data/seed/actions/_candidates/general/round-1.json`). The module docstring says it runs "against the real, live repo data (`data/seed/actions/_candidates/**` …)" — i.e. state only a machine that has run the actions pipeline has.
  - **Two dispositions, both the owner's:** (a) commit a minimal tracked fixture (or move the worked-example brief/answer pair to a tracked path) so the pair is reproducible on a clean checkout; or (b) `knownRed` rows with the owning debt id — that is T55 box 3's disposition and TVB owns the registry. ⛔ Not "fixed" by this lane: adding a skip for absent runtime state is what the audit flags as `Skip`, and moving the fixtures is a decision about authored content.
  - **Verify:** `python -m pytest gk-forge/tools/seedsmith/tests/test_usage_stats.py gk-forge/tools/seedsmith/tests/test_general_propose.py -q` → **6 failed** on this checkout (measured 2026-09-22).
    - **OWNER RULING (2026-09-23): disposition (a) -- TRACK A MINIMAL FIXTURE.** Commit the worked-example brief/answer pair (or a minimal fixture) to a **tracked** path so the pair is reproducible on a clean checkout, and the six tests stop depending on the gitignored runtime directory. NOT disposition (b): the `knownRed` route stays unused (the repo's standing rule against it), and NOT a skip -- a skip for absent runtime state is exactly what the audit flags as `Skip`. **Acceptance:** `python -m pytest gk-forge/tools/seedsmith/tests/test_usage_stats.py gk-forge/tools/seedsmith/tests/test_general_propose.py -q` passes on a fresh checkout, with the fixture committed in the same commit that removes the dependency.
    - ✅ **DONE 2026-09-23 (lane sgc-6).** `gk-data/packs/fusion/data/seed/actions/_fixtures/general/round-1.json` is the tracked fixture — the ONE pinned accepted candidate (`candidate.general.003`), copied verbatim from the real accepted draft, declared `exclude` in `gk-data/packs/fusion/data/seed/actions/_manifest.json`. `prompts._WORKED_EXAMPLE_CANDIDATES_PATH` and the test's own `REAL_GENERAL_CANDIDATES_PATH` now read it; `usage_stats.derive._round_corpus_root` reads the runtime `_candidates/` when it holds a real round file and falls back to the fixture when it does not, so a machine that ran the pipeline still measures the live corpus with no double-count. **Acceptance re-measured on this checkout, which has no `_candidates/`: `110 passed, 12 subtests passed` (was `6 failed, 98 passed`)** — the 104 the first pass measured plus the 6 cases this lane then added for the new fallback seam, which the first pass had left untested. Evidence: `tasks/species-gear-chain-sgc6-f1.md`.

- [ ] **SGC5-F2 — the generated actions corpus names an atom family that no longer exists** · S · *(filed 2026-09-22 by lane sgc-5 out of T55's measurement; **owner: the actions program** — `gk-data/packs/fusion/data/seed/actions/**` is outside this lane's fence.)*
  - **Cause, read from the loader's own refusal.** `gk-data/packs/fusion/data/seed/actions/authored-basics.json`'s `act.attack` carries `atomFamilies` including `atom.fx-overlay-damage`, and the domain loader refuses it by name: `[GAP] Actions/Loader — act.attack: act.attack: field 'atomFamilies' refused — unknown value 'atom.fx-overlay-damage'` — surfaced by `gk-forge/tools/seedsmith/tests/test_cli.py::test_actions_check_uses_domain_loader_and_excludes_round_scratch` and `gk-forge/tools/seedsmith/tests/test_corpus_loader.py::ConfigFilesSurviveTests::test_loading_the_live_corpus_raises_no_findings_today` (one cause, two red rows). The family id no longer exists in the shipped atom-family registry, so the corpus and the registry have drifted apart.
  - **Fix, in the owner's own terms:** regenerate the actions corpus from the current registry (generated content is never hand-edited) OR restore the family — a content decision, not a spelling fix. The generator half is `gk-forge/tools/seedsmith/seedsmith/adapters/actions/**` (in this fence); the corpus half is not.
  - **Verify:** `python -m pytest gk-forge/tools/seedsmith/tests/test_cli.py gk-forge/tools/seedsmith/tests/test_corpus_loader.py -q` → **2 failed** (measured 2026-09-22, after this lane's fixes to the same subset).
    - **OWNER RULING (2026-09-23): REGENERATE THE ACTIONS CORPUS FROM THE CURRENT REGISTRY.** Re-run the generator (`gk-forge/tools/seedsmith/seedsmith/adapters/actions/**`, inside this program's fence) so the corpus derives from the registry that exists now; the regenerated diff lands **with the reason** in the same commit, and generated content is never hand-edited. NOT "restore the family": `atom.fx-overlay-damage` was retired deliberately and nothing in the row argues for its return. **Acceptance:** `python -m pytest gk-forge/tools/seedsmith/tests/test_cli.py gk-forge/tools/seedsmith/tests/test_corpus_loader.py -q` green, and the regenerated corpus no longer names the retired family.
    - ⛔ **RULING PREMISE FALSE — BLOCKED ON AN ERRATUM, 2026-09-23 (lane sgc-6). NOT ticked, nothing regenerated.** Measured, not argued: (1) the ONLY `unknown-family` finding in the whole live tree is `authored-basics.json` / `act.attack`; every `atomFamilies` value in `committed-round-*.json` and `_rounds/**` is already a member of the 125 — **the generated corpus has nothing to fix.** (2) The offending file is not generator output: its own `_meta.authored` says "HAND-AUTHORED, not generator output. ... A generator must never write here, and a regeneration run must never overwrite it", and `grep -rn "authored-basics" gk-forge/tools/seedsmith/seedsmith/` finds **no writer**. (3) `atom.fx-overlay-damage` is not a retired affix family — it is a LIVE atom-registry family (`gk-data/packs/fusion/data/seed/atoms/fx-core.json`, `family: atom.fx-overlay-damage`, "Overlay HP delta"; one of 31 atom families, disjoint from the 125 affix families), and the owning spec names it on purpose (`docs/architecture/lawn-combat-wire/spec-basic-attack-seed.md:39` "atom family `atom.fx-overlay-damage`", `:95` "The authored brief's atom family resolves"). The C# importer is green on the real file (`ActionCorpusImporterTests.cs:159`, seeded from the real `fx-core.json`). **This row's cause accounts for 5 of the 8 program-wide red rows**: these 2 plus 3 of `test_actions_description_completeness.py`'s 5 (`test_every_real_committed_action_carries_provenance` — the row deliberately carries no `_provenance`; `test_load_committed_reports_zero_loader_findings`; `test_resumed_plan_is_empty_now_that_every_real_action_has_a_description`, which lists BOTH ids). ⚠ *Corrected 2026-09-23: the first pass said this row was the single root cause of all 7. `--tb=line` disproves it — the other 3 of the 5 name a SECOND cause, `committed-round-1.json`'s `action.family.academic.004` having no inline `description` (filed as SGC5-F4).*
    - **EXACTLY what blocks it:** an owner erratum ruling choosing one of two spec decisions — **(a)** `lawn-combat-wire` re-authors `act.attack`'s `atomFamilies` to a member of the 125 (a content decision: which affix family the basic attack spends); or **(b)** the actions program widens the `atomFamilies` contract and `vocab.load_family_ids`/`load.py:250` to the **UNION** of the 125 affix families and the atom-registry families the C# composer resolves against (`store.ListAtomsByFamily`, fed from `gk-data/packs/fusion/data/seed/atoms/*.json` **and** `gk-data/packs/fusion/data/seed/atoms/generated/*.json`). ⚠ *CORRECTED 2026-09-23 (same lane): the first form of (b) said "widen to the full atom-family corpus the C# composer resolves against", implying that set contains the 125. Measured, it does not — the two namespaces are largely disjoint. Sizes and what each candidate would refuse, over the committed corpus: today's 125 → **1 family / 1 row** (this one); the atom-registry set alone (105) → **60 families / 205 rows**, a silent regression; the UNION (169) → **0 families / 0 rows**. So the union is the only viable form of (b).* Neither option is a regeneration, and the second is a contract change, so neither is this lane's to make. This is the question `gk-forge/tools/seedsmith/tests/test_coverage_report.py:888` NOTED on 2026-09-15 and left open. **Owning programs: `lawn-combat-wire` (the file's own `_meta.owner`) and `action`.** Their todos (`tasks/lawn-combat-wire-todo.md`, `tasks/action-todo.md`) are outside this lane's fence, so this row carries the finding for the manager to route, as RECON-F6 and SG-ARTIFACT-1 do. Evidence: `tasks/species-gear-chain-sgc6-f2.md`.

- [ ] **SGC5-F3 — the committed creature dump has been self-inconsistent since it was first committed; both implementations agree, the DATA is stale** · XS · *(filed 2026-09-22 by lane sgc-5 out of T55's measurement; **owner: the creature corpus / creature-seed program** — `gk-data/packs/fusion/data/seed/creatures/_dump/**` is outside this lane's fence.)*
  - **Both sides measured, and they agree.** The C# author of the dump and the Python mirror report the SAME two hashes: `dotnet run --project gk-forge/tools/CreatureCorpusDump -- --verify gk-data/packs/fusion/data/seed/creatures/_dump` → `FAILED self-consistency — hash mismatch: manifest declares cc322647cd0118c72d2dc80826cfe7cea7d02077a59aedfb0bb167319d38a10d, files on disk hash to 6181dc2d5393e44653b4e7b688633bc3c79b97928183eee645bce15b31c05e0a` (exit 1), and `seedsmith.adapters.creatures.preflight.check_2_dump_is_current` reports the identical pair. So the seedsmith mirror has NOT drifted from `DumpWriter.ComputeContentHash` (both hash the same four payloads in the same order — `gk-forge/tools/CreatureCorpusDump/DumpWriter.cs:143` vs `adapters/creatures/preflight.py:79`): the committed DATA is stale. `_manifest.json`'s `contentHash` and `capturedUtc: 2026-08-23T10:09:17Z` describe bytes this repo has never contained, while all four payloads were FIRST committed in `740920d2e` (2026-09-12, 28,824 insertions, parent blob empty) and are byte-identical at HEAD (`almanac/plant.json`: 13541 LF / 0 CRLF).
  - **Why it matters:** every lane's `check_2_dump_is_current` reports stale/`ask` (so the preflight tells readers to re-dump), and `gk-forge/tools/seedsmith/tests/test_preflight.py::test_hash_matches_the_real_committed_dump` is red for this data reason — one of T55's nine. The test itself is CORRECT and is deliberately left red: it is the row that detects this.
  - **Fix, in the owner's terms:** re-record the dump through its own writer — `dotnet run --project gk-forge/tools/CreatureCorpusDump -- <server data dir> gk-data/packs/fusion/data/seed/creatures/_dump` — which rewrites `_manifest.json` from the payload bytes. ⛔ Never hand-edit `_manifest.json`: it is generated (the same rule that forbids hand-editing any generated tree).
  - **Verify:** `dotnet run --project gk-forge/tools/CreatureCorpusDump -- --verify gk-data/packs/fusion/data/seed/creatures/_dump` → the `is self-consistent` line and exit 0; `python -m pytest gk-forge/tools/seedsmith/tests/test_preflight.py -q` → green.
  - ⛔ **THE PROPOSED FIX IS NOT ACHIEVABLE IN-FENCE — BLOCKED, 2026-09-23 (lane sgc-6). NOT ticked, nothing re-recorded.** Reproduced and then measured further: (1) `--verify` fails exactly as recorded (`cc32…` declared vs `6181…` on disk, EXIT 1). (2) The manifest's **counts are NOT stale — only its hash is**: it declares `677/227/82/1295` and the four payload arrays hold exactly **677 / 227 / 82 / 1295**, so the manifest was written against a same-shaped payload with different bytes. (3) **No mode re-renders the manifest from the payloads on disk** — `BuildTree(payload, capturedUtc)` is the only manifest producer and it takes a DB payload; `VerifyCommittedTree` only compares. (4) **Re-recording from the live DB rewrites the corpus**: `--check` against a backup copy of `dist/FusionRpg.Server/data/rpg-hot.sqlite` reads `expected hash a71ff42e… plant=677 zombie=227 baselines=913 recipes=0` — baselines **82 → 913**, recipes **1295 → 0** — and the tool's own author already rules that out (`Program.cs`'s `--base-stats` comment: "re-emitting them from today's database would be a large, unrelated diff nobody asked for"). (5) The seedsmith mirror only READS; hand-editing `_manifest.json` is forbidden. **EXACTLY what blocks it:** a manifest-only rehash mode in `gk-forge/tools/CreatureCorpusDump/**` (**outside this lane's fence** — the fence has `gk-forge/tools/seedsmith/**` and `gk-core/src/FusionRpg.Core|Data/**`, not this tool), or an owner decision to re-snapshot the corpus. **Second, distinct finding the row does not name:** there are TWO stalenesses — manifest vs committed payloads (`cc32…` vs `6181…`) AND committed payloads vs the live game (`6181…` vs `a71f…`, different baseline/recipe populations); the second is the creature-seed program's deliberate 2026-08-23 snapshot, not a bug. Evidence: `tasks/species-gear-chain-sgc6-f3.md`.
  - **Register check (2026-09-23, lane sgc-6): NOT listed.** `docs/architecture/stub-register.md`'s 20 `SR-*` rows were read in full; none mentions the dump, `_dump`, or a stale manifest — this is genuinely unregistered, unlike SGC5-F4 (which is `SR-25`).

- [ ] **SGC5-F4 — one committed action row has no inline `description`, and it is the SECOND cause behind 3 of the 5 `knownRed` rows** · XS · *(filed 2026-09-23 by lane sgc-6 out of T55 box 2's program-wide measurement; **owner: the actions program** — the fix is a description backfill, i.e. a model call, and `data/seed/actions/committed-round-*.json` is generated content, so it is not a lane edit.)*
  - ⚠ **The GAP itself is already REGISTERED, dated and accurate — cite it, do not re-derive it.** `docs/architecture/stub-register.md:77`'s `SR-25` row (confirmed 2026-09-19) reads: *"`RealCommittedCorpusCleanPassTests` fails 5 of its 11 tests on the real, committed action corpus … **Two real actions (`act.attack`, `action.family.academic.004`) carry no content description**, and `act.attack`'s `atomFamilies` names an unregistered value (`atom.fx-overlay-damage`). The tests are right …"* — so the register already names BOTH rows and BOTH causes, which is exactly the split this lane re-measured. ⚠ *Corrected 2026-09-23 (same lane, after reading the register): this row's first form presented the second cause as newly found and asked for the registry disposition to be made “against both”. The register already said both.* **What this row genuinely adds:** the 1-of-181 figure (the register does not count the population), that the row is also the ONE generated action row absent from the backfill ledger's 179, and the exact 4-of-5 / 1-of-5 test split.
  - **Cause, measured.** `gk-data/packs/fusion/data/seed/actions/committed-round-1.json`'s `action.family.academic.004` carries `descriptionKey` (`action.family.academic.004.desc`) but **no inline `description`** — the ONE of **181** action-seed entries missing it (checked across all four `committed-round-*.json`; the other three have none missing). `test_actions_description_completeness.py`'s `RealCommittedCorpusCleanPassTests` reports exactly that: `Content/FieldMissing … 1 of 181 'action-seed' entries in domain 'actions' have no 'description' (action.family.academic.004)`.
  - **Four of the 5 registered `knownRed` rows name it**, and after the contract correction below all four name ONLY it: `test_content_field_missing_is_clean_on_the_real_corpus` (`Content/FieldMissing … 1 of 181`), `test_every_real_committed_action_carries_provenance` (`None is not true : action.family.academic.004` — the description), `test_resumed_plan_is_empty_now_that_every_real_action_has_a_description` (`['action.family.academic.004'] != []`) and `test_automatic_backfill_makes_zero_model_calls_and_writes_nothing_when_all_done`, whose name says "zero model calls" but which reaches a REAL model call **because that row still has work** (hence `RuntimeError: model call failed … <urlopen error timed out>` with no model running). The fifth, `test_load_committed_reports_zero_loader_findings`, names SGC5-F2's authored row. ⚠ *Before that correction the split read 3/3 with one test naming both ids — see the next bullet.*
  - ✅ **Fixed in the same pass — the backfill would have written into the AUTHORED file.** `plan()` targeted `act.attack` (measured: `['act.attack', 'action.family.academic.004']`), so a real `backfill` run would have stamped a generated `description` and a `_provenance` block into `authored-basics.json` — overwriting its authored prose and destroying the marker that tells authored content from generator output, which that file's own `_meta.authored` forbids outright ("A generator must never write here, and a regeneration run must never overwrite it"). `generate_action_descriptions.is_authored` now excludes such rows from `plan()`; the plan reads `['action.family.academic.004']`, and `test_the_backfill_plan_never_targets_authored_content` pins it.
  - ✅ **The test contract that inflated this row's count is corrected too.** `test_every_real_committed_action_carries_provenance` required a `description_backfill` `_provenance` on EVERY `action-seed` row, including the authored one whose file says it deliberately carries none — i.e. it demanded the hand-edit the authored-content rule forbids, and the backfill plan was the way to satisfy it. It now asserts the split contract (generated rows carry `description` + provenance; authored rows carry a description and **no** provenance), keeps its name so its `knownRed` entry stays valid, and still fails — now on THIS row's real gap.
  - **⚠ This row exists to carry a correction.** The first pass of T55's program-wide note (and of SGC5-F2's own note) attributed all 5 `knownRed` rows to SGC5-F2's authored row. `python -m pytest tests/test_actions_description_completeness.py -q --tb=line` disproves it: 3 of the 5 name this row instead. The `knownRed` block's debt id `SR-25` therefore covers at least **two distinct content causes**, and the registry disposition must be made against both.
  - **Fix, in the owner's terms:** run the description backfill (`gk-forge/tools/seedsmith/seedsmith/adapters/actions/description_backfill/**`; its ledger is `gk-data/packs/fusion/data/seed/actions/_runs/description-backfill.ledger.json`) — it needs a model endpoint, so it is an owner/model-run step. ⛔ Never hand-edit the row: `committed-round-*.json` is generator output.
  - **Verify:** `python -m pytest gk-forge/tools/seedsmith/tests/test_actions_description_completeness.py -q` → green (currently `5 failed`, of which 3 name this row), and a scan of the four `committed-round-*.json` reports **0** entries without a `description` (currently 1). Evidence: `tasks/species-gear-chain-sgc6-t55-redset.md`.

- [ ] **SGC5-F6 — the committed action corpus's atom-family gap, measured program-wide: 48 of 181 briefs name no family the atom catalog has, and the boot's importer result is discarded** · S · *(filed 2026-09-23 by lane sgc-6 while measuring the atom-family namespaces for SGC5-F2; **owner: the action program** — the corpus half is `gk-data/packs/fusion/data/seed/actions/**` plus the atom corpus, and the reporting half is `gk-core/src/FusionRpg.Server/Program.cs:765`, outside this lane's fence.)*
  - ⚠ **The PHENOMENON is already documented and already ruled — this row's job is the program-wide figure and the reporting gap, not the discovery.** Two independent records say so. (1) `gk-core/tests/FusionRpg.Data.Tests/Actions/ActionCorpusRealContentQualityTests.cs:18-26`, dated: "**Real, measured finding (2026-09-06), not assumed**: only 2 of the 30 unique `atomFamilies` the real corpus names … exist anywhere under `gk-data/packs/fusion/data/seed/atoms/` … Exactly 3 of 24 briefs … import; the other 21 correctly refuse, naming why. This is a real content-authoring gap in a sibling pipeline (the atom/family generator), **not a defect in A21's own import machinery — fixing it is out of this module's scope**." (2) The sealed spec `docs/architecture/action/spec-action-seeding.md:8-20` carries the owner's own ruling (2026-08-27): *"seedsmith is a tool for developing the game, not the running game … **Seedsmith measures a corpus this module produces — it cannot gate the feature that produces it, and it does not run in the game**"* — i.e. the committed corpus is a dev-tool artefact whose completeness is not a gate on the feature. ⚠ *Corrected twice, 2026-09-23 (same lane): the first form read as a fresh discovery; the second fixed the lever but still framed the gap as a defect to close.*
  - ✅ **THE OWNER, found by finishing the DESIGN-GATE read: effect-atom module E43 (`docs/architecture/effect-atom/spec-family-expand.md`), whose own §2 already names this exact gap.** "**What it owns: turning the 98 authored family definitions into atom rows**" (drafted 2026-09-03, after the spec-coverage audit found the rule *"specced nowhere after W7.9 replaced its module"*), and its §2 table reads: `SeedScanner.OwnedFolders` | **does not include `items`** | `SeedScanner.cs:14-15` — so the importer never sees them; **The expansion rule | ⛔ real gap — no file, no generator, no test**. Two more documents say the same from the catalog side: `atom-catalog-ssot.md` §0 ("**The vocabulary is closed and built. The POOL is empty. Do not confuse the two.** … **So the pool file exists and is read. What it lacks is rows.** The step that would fill it — emitting the family library from the registry, deterministically — is **model-free and unbuilt**") and `atom-family-library.md` §2's stage table (`families → atoms` | owner **effect-atom `E30`** | **Shipped? no — this is the unimplemented rule`). So the 95 refusals below are **E43's remaining work**, and `gk-forge/tools/FamilyExpandGen` is the partial implementation of it (11 partitions landed of 16) — not a tool whose scope is wrong, and not a "priceability table" to edit. **Owning program: effect-atom, row E43** — not the action program, whose corpus merely consumes it.
  - **DESIGN-GATE §1 rows 45 and 42 — what this lane read, this session, and what it did not.** ✅ **Read IN FULL:** `docs/architecture/action/spec-action-seeding.md` (212 lines) and **`docs/architecture/action-ideal.md` (902 lines, completed 2026-09-23)** — and that document's only two defects are the ones this lane filed (`SGC5-F7` at `:499`/`:137`, `SGC5-F8` at `:656`/`:657`); its §9 "what this supersedes" table tracks the drift it created in the *shipped action specs*, but not its own body's counts. Read in section: `action-corpus-ideal.md` §21; `effect-atom/atom-catalog-ssot.md` §0–§3; `effect-atom/atom-family-library.md` §1–§2; `effect-atom/spec-family-expand.md` §1–§3.1; `action-map.md` §4–§4.3 (the module list, build order and Phase 0); **`effect-atom/definitions.md` §0–§5** (the model, the id grammar, values/rolls, predicates, rarity, slots/affix bundles/RNG streams, instances and determinism). **Still NOT read in full, and the gap is bounded:** `action-map.md` §5–§10 (dependency direction, checkpoints, what is inherited from Chaos, owner decisions, resources, the readiness gate) and `effect-atom/definitions.md` §6–§14 (owner keys, power, content hash, runtime support, rejection codes, measurement, the defect log, the ICD key) — **both are atom/action-program internals with no bearing on this lane's item/gear/actions-corpus findings**, which is why the gap is stated rather than closed by reading them: the §5 checklist's own rule is "if you cannot tick a box, say so", and a gap whose risk is named is worth more than a tick nobody can defend.
  - **What that read adds, and what it does not change.** It contradicts nothing in this row. It sharpens two things: (a) the corpus is seedsmith's **by sealed decision** — `action-ideal.md` §0.1 decisions **4** ("Actions are seeded, never handcrafted") and **17** ("Seedsmith rolls the target spec") — and `action-map.md` §4.1 labels **A13 `action-seeding`** "the **runtime generator** … **Not seedsmith**", with §4.3's Phase 0 extending the atom effect layer **before** any action module builds; (b) the row E43 must emit is **grammar-free work**: `definitions.md` §1 pins `atom_id` as **derived, not authored** — `{family_id}[.{variant}].t{tier}` — over an `effect_atom` key of `UNIQUE (family_id, tier, variant)` (`variant` `''` for single-member families like `vitality`/`might`, the element for generated ones), and `spec-family-expand.md` §2 lists `AtomRow.DeriveId` and that constraint as already **built**. So E43's remaining 95 families need no new vocabulary, no new table and no new id rule — only rows.
  - **Cause, read from the code.** `ActionCorpusComposer.Compose` requires at least one of a brief's `atomFamilies` to resolve — `foreach (var family in brief.AtomFamilies) foreach (var atom in atomsInFamily(family))`, then `if (candidates.Count == 0) throw new ActionCorpusComposeRejection($"brief '{brief.Id}': none of its atomFamilies (…) resolved any atom")` (`gk-core/src/FusionRpg.Core/Actions/Corpus/ActionCorpusComposer.cs:83-89`). `atomsInFamily` is `store.ListAtomsByFamily`, and the store's atom rows come from `SeedImportRunner` sweeping `SeedScanner.AtomFolders`.
  - **NEW — the complete resolvable set, measured:** **105 families, all under `gk-data/packs/fusion/data/seed/atoms/**`** (7 hand-authored files → 31, 11 `generated/family-expand.*` → 74). Scanning every other swept folder (`containers`, `curves`, `rarity`, `elements`, `channel-policy`, `channel-pools`, `effects/affixes`, `power`, `creatures/species-effects`) for entries carrying a `family` field returns **zero** — so 105 is the whole set, and only **61** of the 125 item affix families are in it.
  - **NEW — the program-wide figure (the 2026-09-06 reading covered only `committed-round-{1,2}`, 24 rows):** of the **181** committed + authored action rows, **48 name ONLY families with no atom row** — a hard rejection regardless of the rung window — and 133 have at least one resolvable family. Most-named unresolvable families: `atom.elpw-surge` (11 rows), `atom.sust-husk` (6), then `atom.volley`, `atom.elpw-overflow`, `atom.searing-strike`, `atom.retribution`, `atom.deathblast` (4 each).
  - **NEW — why the 95 unexpanded families cannot be expanded, classed, and TWO layers not one.** `dotnet run --project gk-forge/tools/FamilyExpandGen -- --check` → **`--check: clean, 11 generated file(s) match`** (EXIT 0), and its header reads **"125 families read, 150 row(s) emitted across 8 family file(s), 95 family(ies) refused:"** with every refusal named. Classed: **69** `no referenceBaseGameUnits` (the family's channel/kind has no game-units reference), **21** `no opWeightPermille entry for op 'Replace'/'Flag'`, **3** bare status family template ("the concrete segment must be authored (`status.<family>.<category>`)"), **4** `no matching E30 channel pool`. Those are the **generator's own expansion gates** (`bands.v1.json`'s `familiesOutOfFourWaySplit`, the op weights, the E30 pools) — **a different layer from E9's atom pricing**, which per the sealed `action-corpus-ideal.md:694` *"has no concept of a family"* (its key is `(kindId, channel)`, and it can only price a concrete `AtomRow`). Conflating the two would send a reader after the wrong table; the gate read is what caught that.
  - **NEW — the boot prints nothing about it.** `gk-core/src/FusionRpg.Server/Program.cs:765` calls `ActionCorpusImporter.Import(store, actionBriefs, actionCostTemplate, RungPolicy.Table)` and **discards the returned `ImportResult`**: `ImportedCount`/`RejectedCount`/each `BriefOutcome.Rejection` are computed (`ActionCorpusImporter.cs:80-87`) and never printed, so the refusal is *documented in a test* but invisible in a boot log. The importer's own contract for a brief that composed before and refuses now is to upsert the stored action **DISABLED** (never deleted), so the visible catalog thins quietly. ⚠ This is the row's one part that is **not** covered by either ruling above — they rule the GAP out of scope, not the silence about it.
  - **Register check (2026-09-23, lane sgc-6): HALF listed.** `SR-25` covers the *corpus* half (the two rows without a description and `act.attack`'s unregistered family) but **not** the compose-join figure, the 105-family set, the classed `FamilyExpandGen` refusals, or `gk-core/src/FusionRpg.Server/Program.cs:765` discarding the `ImportResult` — none of the 20 `SR-*` rows mentions any of those. So the row's reporting half is genuinely unregistered.
  - **Verify:** a join, not a count — every committed brief's `atomFamilies` must intersect the set of families with atom rows, and the boot must report the importer's rejected ids. Today: **48 of 181 fail the join** and the call site prints nothing. ⚠ 48 is a LOWER bound: it counts only the zero-resolvable-families mode; the composer's second rejection mode (no resolvable atom inside the row's rung window, `ActionCorpusComposer.cs:92-95`) is not counted, because replicating the rung-table collapse in Python would be a second implementation of a C# rule.

- [ ] **SGC5-F7 — the SEALED `action-ideal.md` contradicts its own "0 open questions" in two places** · XS · *(filed 2026-09-23 by lane sgc-6 while doing the DESIGN-GATE read for §1 row 45; **owner: the action program** — `docs/architecture/action-ideal.md` is outside this lane's fence, and the fix is a one-line amendment or a ratification.)*
  - **Cause, read from the document.** Its own header (`:3`) reads "**Status: ✅ SEALED 2026-08-27 by the owner.** 26 decisions, **0 open questions**, 6 retractions", and `§0.2` (`:67`) is titled "**Open — none. This ideal is ready to seal**" — but the body still carries two items labelled as unresolved:
    - `:499` — "**⛔ Open (§0.2 A): a lawn actor has no turn**, so control duration has nothing to resolve against there." There is no `§0.2 A`: §0.2's only carried item is **Linkage (§8.5)** (`:77`), and the lawn-turn question is what decision **26** (`:61`) reclassifies as a **deferred measurement**, "not open design". So both the label and the cross-reference are stale, and a reader at §5.3 is told an open design question exists in a document that seals them all.
    - `:137` — §1.3's innate-action rung is "**Recommended, not yet ratified.**" while decision **1** seals "Three kinds of action" and §0.2 declares none open. Either the recommendation was ratified in the seal and the label is stale, or it was not and §0.2's "0 open questions" is over-broad.
  - **Why it matters beyond tidiness:** this document's own rule is *"do not reopen"* (§0.1), and the gate row points every reader at it. An "Open" marker inside a sealed ideal is exactly the kind of stale label that makes a later lane believe a decision is still pending — the failure mode the SEALED header exists to prevent.
  - **Fix, in the owner's terms:** amend `:499` to name decision 26's deferred-measurement status (and drop the dead `§0.2 A`), and either ratify §1.3 in §0.1 or move it to §0.2. Nothing else in the document needs to move.
  - **Verify:** `grep -nE "Open \\(|not yet ratified" docs/architecture/action-ideal.md` returns only lines whose own section says the item is a rule or a decision — today it returns `:499` and `:137`.

- [ ] **SGC5-F8 — the SEALED `action-ideal.md` carries a STALE closed-vocabulary count: `12 kinds / 7 triggers` where the registry says `18 / 13`** · XS · *(filed 2026-09-23 by lane sgc-6 while finishing the DESIGN-GATE read for §1 row 45; **owner: the action program** — `docs/architecture/action-ideal.md` is outside this lane's fence.)*
  - **Cause, read from both sides.** `action-ideal.md` §8.2a's dial table reads `| kind_id | what it does | **12** kinds |` (`:656`) and `| when_json → trigger | when it fires | **7** — OnSpawn OnDamageDealt OnDamageTaken OnDeath OnGranted OnRemoved OnTimer |` (`:657`). The registry at this head is `AtomKindRegistry.KindCount = 18` (`gk-core/src/FusionRpg.Core/Effects/Atoms/AtomKindRegistry.cs:43`), `AttachPointCount = 9` (`:27`) and `TriggerCount = 13` (`:48`), and the atom SSOT carries the correction with its own history — `effect-atom/definitions.md:37` ("closed set of ~~12~~ ~~16~~ **18**; not content. **Corrected 2026-09-19** … `DESIGN-GATE.md`'s atom row carries 9/18/13") and `effect-atom/atom-catalog-ssot.md:122` ("`AtomKindRegistry.TriggerCount = 13`").
  - **Why it matters beyond a typo.** `DESIGN-GATE.md` §1's atom row states the rule this document breaks: *"Because this file wins over any spec, a stale count here outranks every correct one downstream, so a module that widens the vocabulary is not finished until this line moves with it"* — and it records that the count has already gone stale four times. Here the stale count sits in a **sealed** ideal (`:3`) that the gate's action row points every reader at, so an implementer reading §8.2a would size the combinatorial surface ("twelve kinds × seven triggers") against a vocabulary that is 50% larger.
  - **Fix, in the owner's terms:** move `:656`/`:657` to `18` kinds and `13` triggers (the seven named plus `OnActivate`, `OnWave`, `OnMatchStart`, `OnMatchEnd`, `OnSunCollect`, `OnGridPlace` — `atom-catalog-ssot.md` §3's own table names them), or replace the numbers with a pointer to the registry constants so the two cannot drift again.
  - **Verify:** `grep -nE "\\*\\*12\\*\\* kinds|\\*\\*7\\*\\* —" docs/architecture/action-ideal.md` returns nothing, and any count the document states matches `AtomKindRegistry`'s three constants.

- [ ] **SGC5-F5 — test code starts FIVE executables by bare name, so a stripped `PATH` turns them into opaque `Win32Exception`s** · S · *(filed 2026-09-23 by lane sgc-6 while running T37's third verify box; **owner: cross-program** — the call sites span 10 test projects, none of them this program's, so it is filed here for the manager to route the way RECON-F6 and SG-ARTIFACT-1 are.)*
  - **The measured instance.** `gk-core/tests/FusionRpg.Server.Tests/RealRunCollectorTests.cs:154` sets `FileName = "powershell"` on a `ProcessStartInfo` and calls `Process.Start(psi)` — a bare name, resolved through `PATH` only. Same head, both ways: without `powershell` on `PATH` **Failed: 2, Passed: 857**; with it **Failed: 0, Passed: 859**. Every failure is `System.ComponentModel.Win32Exception : An error occurred trying to start process 'powershell' … The system cannot find the file specified`, which reads exactly like a content failure.
  - **The class, inventoried** (`grep`-equivalent scan of `tests/**/*.cs` for a bare `ProcessStartInfo.FileName` / `new ProcessStartInfo("…")`, `bin`/`obj` excluded): **5 distinct executables across 35 call-site files in 10 test projects** — `powershell` 24 files / `FusionRpg.Guard.Tests` + `FusionRpg.Server.Tests`; `dotnet` 5 files / `AtomImporter.Tests`, `Core.Tests.Shared`, `Data.Tests`, `SquadHarness.Tests`; `python` 3 files / `Core.ClassSystem.Tests`, `Guard.Tests`; `git` 2 files and `icacls` 1 file / `Guard.Tests`.
  - ⚠ **What that count does and does not mean — corrected 2026-09-23 (same lane, after a second pass):** it is a static count of the two LITERAL shapes only, and the `dotnet` fifth of it is **not the same risk as the rest**. Every `dotnet` site is an **apphost-preferred fallback** — `FileName = apphost` (the executable built beside the test dll by the `ProjectReference`, asserted to exist first) with `: new ProcessStartInfo { FileName = "dotnet", … }` behind it (`Core.Tests.Shared/TestSupport/ToolProcess.cs:29-45` is the shared form of it). So the REACHABLE bare-name risk is `powershell` (24 files, no resolver), `python` (3), `git` (2) and `icacls` (1) — 30 files, not 35. The variable-shaped `FileName = apphost`/`host` sites in ~7 further files are already resolved paths and were never part of the count.
  - **The fix pattern already exists in this repo, so name it rather than invent one.** `gk-core/tests/FusionRpg.Guard.Tests/TestContentRootGuardTests.cs:58` defines `ExecutableOnPath(name)` — it walks `PATH`, returns the first `<dir>\<name>.exe` that exists, and returns `null` so the call site can fall back (`:48` is `FileName = ExecutableOnPath("pwsh") ?? "powershell"`). That is exactly the "resolve deterministically, and if it cannot, say which is missing" shape this row asks for, and it is used in ONE place out of thirty. The fix is therefore: hoist that helper into the shared test support, use it at every site, and make the `null` branch a named assertion rather than a silent bare-name fallback.
  - **Second measured instance, and far the worse one — now counted exactly.** The two `python`-spawning guard classes (`DocCitationAuditTests`, `VocabRenameTests`) read **Failed: 39, Passed: 1, Total: 40 in 105ms** without `python` on `PATH`, and **Passed! Failed: 0, Passed: 40, Total: 40 in 6s** with it (`dotnet test gk-core/tests/FusionRpg.Guard.Tests --no-build --filter "FullyQualifiedName~DocCitationAudit|FullyQualifiedName~VocabRename"`). So a lane running the guard suite from a stripped shell does not see two odd failures — it sees **39 guard failures** that read as real citation/vocabulary violations, and the whole-project run they sit in takes **8m36s**, too long to diagnose and re-run inside one segment.
  - **Why it matters.** This is the C# twin of the seedsmith hazard fixed in `a41d5d152` (a missing `dotnet` surfacing as a bare `FileNotFoundError`): an environment-dependent dependency reported as an opaque exception. T37's own recorded Server.Tests reading (`Failed: 1, Passed: 766`) was taken where it resolved, so the failure appears only to a lane running from a stripped shell — which is exactly how an agent runs it, and the two classes were found on two different sides of the language boundary in the same session.
  - **Fix, in the owner's terms:** resolve each executable deterministically (prefer `PATH`, fall back to the well-known absolute location) and fail with a message naming what is missing if neither resolves — never a bare `Process.Start` on a PATH-only name. A shared helper already exists to build on: `gk-core/tests/FusionRpg.Core.Tests.Shared/TestSupport/ToolProcess.cs:45` spawns `dotnet` the same bare way.
  - **Verify:** in an environment WITHOUT `powershell`/`python` on `PATH`, `dotnet test gk-core/tests/FusionRpg.Server.Tests --no-build` and the two `python`-spawning guard classes are either green, or fail with a message naming the missing executable rather than `Win32Exception`. Today: **2 failed / 857** and **39 failed / 1 passed / 40**.
  - **Register check (2026-09-23, lane sgc-6): NOT listed.** All 20 `SR-*` rows were read; none mentions a bare process name, `powershell`, `python`, `icacls` or `git` as a spawned executable. Genuinely unregistered.

    **CORRECTION 2026-09-27 to SGC-F-dump-args — the named tool is not the one at fault, and the row
    under-reports its own blast radius.** Traced end to end by read-only investigation:

    - **The arguments and `LeadNamesHub` do not connect.** The path that throws is
      `RpgStore.Init` -> `SeedPlayerIfEmpty` -> `OnboardingPlayerName` -> `LeadNamesHub.Current`, and
      `gk-forge/tools/CreatureCorpusDump/Program.cs` contains **zero** `LeadNames` references. The row's
      `KS-F1` framing ("give the boot's discovery the same content-root awareness the test resolver has")
      describes a different seam; this is an unconfigured-hub throw, not a discovery gap.
    - **It fires only on a COLD data dir.** On a warm one the seeding path is not taken and the run
      succeeds, which is why this reads as intermittent.
    - **`--base-stats` (line 56) shares the defect** even though the row names only the default path, so
      the row's own scope is one argument short.

    **The `--check` directory at the repo root is confirmed litter — and `CreatureCorpusDump` could not
    have produced it.** It is an `RpgStore` data directory named after a CLI flag: `rpg-hot.sqlite`
    (1.72 MB) + `rpg-media.sqlite` + `archive/`, 175 tables, git-ignored. But `CreatureCorpusDump` filters
    `--check` at `Program.cs:88` and did so in its 2026-09-12 revision too — five days **before** the
    directory's 2026-09-17 timestamp — so a bare `--check` crashes before any `RpgStore` is constructed.
    **The live defect class is different: `CreatureCatalogGen:13` and `CreatureCorpusEmit:18` call
    `Path.GetFullPath(args[0])` with no flag guard at all.** A bare `--check` there yields
    `GetFullPath("--check")` and a data directory with that name — which is exactly the litter. The
    fix belongs to those two tools, not to the row's current target.
