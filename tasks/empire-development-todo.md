# Task list: empire-development

Companion checklist to `tasks/empire-development-plan.md` — see that file for full reasoning,
acceptance criteria, verification commands, and file lists per task. Built 2026-09-13 in worktree
`worktree-empire-development-20260915-b7e2` (session `empire-development-20260915-b7e2`).

## Phase 0: External prerequisite — `deployment-hierarchy`'s `corpse-cache` trio

*(Skip check performed: no `rpg_corpse_cache` in `gk-core/src/FusionRpg.Data`, no
`tasks/deployment-hierarchy-plan.md` — built here, no duplication.)*

- [x] 0.1 `corpse-cache` — schema + death/wipe move (core mechanism now; anti-fraud phase-gate guarantee
  BLOCKED on an item-program ask, tracked not blocking; wipe path BLOCKED on `loot-pack` §7 ask)
- [x] 0.2 `cache-decay-void` — clock, amended for durable world-map places (never voids `world_sector`/`world_lane`)
- [x] 0.3 `cache-field-access` — reachability, amended for `world_sector`/`world_lane`
- [x] 0.3b `cache-field-access` — claim into legion cargo (`ClaimCorpseCacheIntoCargoUnlocked`,
  `spec-cache-field-access.md` §2a; needs Task 1.1, landed)

### Checkpoint: Phase 0 complete
- [x] Combined test run green (CorpseCache 9+1 skip / CacheDecay 15 / CacheFieldAccess 19)
- [x] `guard-dal.ps1` / `guard-actor-hub.ps1` green
- [x] `grep -rn "rpg_corpse_cache" gk-core/src/FusionRpg.Data` wired end-to-end

## Phase 1: Wave 1 — four independent modules (parallelizable)

- [x] 1.1 `legion-cargo` — slot+weight cargo overlay, all-members capacity (Core 7 + Data 28)
- [x] 1.2a `sector-storage` — `StructureKind.ItemStorage` + capacity axis
- [x] 1.2b `sector-storage` — table + capture hook (no-op capture transfer + tx atomicity proof)
- [x] 1.3a `relic-item-kind` — KindSpec + enum + mint arm
- [x] 1.3b `relic-item-kind` — seedsmith `droptablegen` gains `relic` entryKind + append operation
  (+ `_write_document` `newline=""` fix, root repair — CRLF rewrite broke byte-identity)
- [x] 1.3c `relic-item-kind` — content authoring (3 anchors + 7 appended groups, regenerate-only;
  runtime-corpus rows are a filed item-program ask, `spec-relic-item-kind.md` §Design 4b)
- [x] 1.4 `wonder-structure` — vocabulary + `StructureDef` facet + `Validate`

### Checkpoint: Phase 1 complete
- [x] All four modules' tests pass independently
- [x] `guard-dal.ps1` / `guard-actor-hub.ps1` / `guard-single-writer.ps1` green (Phase 3 run: 6/6)
- [x] `audit-overflow.py`: 0 new; `audit-magic-numbers.py`: 5 HIGH + 2 LOW new in
  `RpgStore.CacheDecay.cs` — spec-§Tunables starting values pending the sibling program's
  `gk-core/data/tuning/deployment-hierarchy.v1.json` domain file (accepted deviation, documented in code)
- [x] ContainerKind 11→12 pins bumped (`UniqueTests`, `DropVolumeCorpusTests`) for Task 1.3a's
  reviewed `Relic` addition

## Phase 2: Wave 2 — four modules

- [x] 2.1 `cargo-transfer` — deposit/withdraw/legion-to-legion, corrected weight resolution (20/20)
- [x] 2.2 `cargo-fate` — legion-death cargo cache (sector + lane cases; fixed real
  `INSERT OR REPLACE` cascade wipe on entity rewrite via `ON CONFLICT DO UPDATE`)
- [x] 2.3a `wonder-effect-empire` — faction-input plumbing + SUM (30/30)
- [x] 2.3b `wonder-effect-empire` — SQL persistence + 3 secondary call sites (16/16)
- [x] 2.3c `wonder-effect-empire` — upkeep term (38/38; `loam.v5.json` ships rate 50;
  all `loam.v4.json` functional readers flipped to v5)
- [x] 2.4 `wonder-build-flow` Core-side — fields, cap scan, admission check, **rubble/ironwork wiring fix**

### Checkpoint: Phase 2 complete
- [x] All Phase 2 tests pass
- [x] `guard-dal.ps1` / `guard-actor-hub.ps1` green
- [x] Integration: legion cargo load→transfer→death-cache proven (`CargoFateTests` via real
  `DiffCommitForTest` + `CargoTransferTests` 20/20 + claim-back via `ClaimCorpseCacheIntoCargo`)
- [x] Integration: Sector-scope Wonder boosts yield with zero engine change
  (`WonderCatalogTests`); Empire-scope sums into `ScopeModifierMilli`, persists across save/load
  (`WorldGraphScopeModifierTests`), and costs upkeep (`WonderUpkeepTests`)

## Phase 3: Final integration

- [x] 3.1 `wonder-build-flow` Data-side — relic reachability pre-check + spend, same-transaction (5/5;
  neighbor regression 212/212)

### Checkpoint: Phase 3 complete — full program integration
- [x] End-to-end: mint (real `MintRelic`) → carry/deposit → spend → build → observe production +
  upkeep effect (`WonderBuildTests` 5/5; live-drop source rows are the §Design 4b item-program ask)
- [x] Full suite: Core 13691 (3 pre-existing/foreign fails: 2 stale ContainerKind pins — FIXED this
  pass — plus dungeon CRLF + 2 creature-drift, all outside empire files), Data 1421 (same 2
  creature-drift), Guard 314/314
- [x] All boundary guards green (6/6)
- [x] `audit-overflow.py` / `audit-magic-numbers.py` — see Phase 1 checkpoint note for the one
  accepted deviation
- [x] Ready for owner review / live deploy-play smoke test

## Deferred, named future work (not a task — carried for a future notification-consumer session)

- [ ] `spec-sector-storage.md` — sector storage reachability flip on capture, silent to the player
- [ ] `spec-cargo-fate.md` — legion-death cargo cache, silent to the player
- [ ] `spec-wonder-build-flow.md` — Wonder completion + `wonder.cap-reached` refusal, silent to the player

## Open, non-blocking content/balance decisions

- [ ] Relic drop weight/rate per `SourceKind` table (Task 1.3c) — ship a low default, flag for balance pass
- [ ] `EmpireWonderUpkeepRateMilli` real value (Task 2.3c) — ship provisional `50`, flag for balance pass
- [ ] ~~Item program (`drop-volume`): runtime-corpus relic rows in `gk-data/packs/fusion/data/seed/loot/*.json`~~ → tracked
  at this file's own **4B.3** (line 152, `backlog-clean-up` `paperwork-reconcile` P7, rule 3 — same ask
  duplicated at the task and the open-decision level; 4B.3 is the owner)

## Phase 4: Live-wire — player-triggerable surface (9-audit verdict: 2 dead-code, 7 wired-but-untriggerable, 0 playable)

- [x] 4D.0 idea-ui phase: `empire-inventory-surfaces-ideal.md` + `empire-wonder-surfaces-ideal.md` (LANDED, strengthened, answers recorded)
- [x] 4A.1 cargo WorldCommands + admission + resolver (D1 HELPERS locked no-code-change; D2
  playerId RECORD; D3 server-side weightEach + loud refusal; weightEachFor lookup is implementation's
  first task; merge-additive with 4A.2)
  - [x] Per-kind resolve moves-never-copies; refusals verbatim, zero writes; claim skip-not-refuse +
    idempotent `cache.claimed:<c>+<s>`; claim-before-decay; no-bump proof (goldens green + old-log
    replay hash unchanged, RulesetVersion 10); weight-probe extension + helper-reuse guard; admission
    matrix; seam-shape + debit-after-refill-order only (numbers/body in 4A.6/4A.7/4A.8)
  - [x] Files: WorldCommand.cs + WorldCommandAdmission.cs + RpgStore.WorldTurns.cs +
    RpgStore.CargoCommands.cs NEW + WorldDtos.cs + WorldEndpoints.cs + CargoCommands/ tests NEW
- [x] 4A.2 Wonder REST entry (`RelicInstanceIds` + mapping + FE mirror; NO early pass — admission owns
  refusals; unknown structureId never reaches a Get)
  - [x] Mapping round-trip order-preserved; admission-over-HTTP per-command; FE null-vs-`[]`;
    no-silent-cleaning; 5-step live proof (file → `build.started:` → `consumed` + overlays gone →
    completes after BuildTurns, RPG-server-debug scope, normal-path readback)
  - [x] Files: WorldDtos.cs + WorldEndpoints.cs + bus/world.ts + worldSelection.ts + Server World/
    tests + worldSelection.test.ts
- [x] 4A.3 cache discovery + claim endpoints + read-back DTOs (passes NO weight, resolves none;
  Depends: 4A.1)
  - [x] 10-bullet Testing: presence-gating; hidden-until-found body assert; unknown-vs-empty;
    foreign-legion entity.not-yours; filer idempotency; filer-never-resolves; one-scope reads;
    refusals verbatim; no-weight-on-wire schema; stored-detail-not-replay
  - [x] Files: WorldDtos.cs (5 DTOs) + WorldEndpoints.cs (4 routes + filer) + types.ts + adapt.ts +
    WorldClaimEndpoints/ tests NEW — Estimated L (split Server-vs-FE-mirror if unwieldy)
- [x] 4A.4 Wonder catalog/slot wire (6/6 Data + 7/7 HTTP + 48/48 mirror suites; tsc clean) (strengthen-pass orphan fix; Depends: 4B.1 rows)
  - [x] 4 catalog fields (WonderScope/WonderRarity/RelicCost/ExistenceCap) + 2 slot-facet fields
    (fog-parity) + 4 sector fields (2 live counts owner-only, Common absent; WonderUpkeep inside
    breakdown; WonderProductionContribution) + WorldRelicReachabilityDto + GET route + TS
    mirror/adapter lines in the same diff + upkeep Total reconciliation
  - [x] Files: WorldDtos.cs + WorldEndpoints.cs + RpgStore.WonderReach.cs NEW + bus/world.ts +
    types.ts + adapt.ts
- [x] 4A.5 act-price-table (6 tuning rows camelCase: claimCostMilli 250 / depositCostMilli 100 /
  withdrawCostMilli 100 / loadCostMilli 50 / unloadCostMilli 50 / holdAllowanceMilli 250; reserved
  clear/sustain NOT accepted; publish-via-tool + _meta note + old version stays; 3 bootstrap updates)
  - [x] Missing-key-per-key rejection; non-integer rejects; round-trip; no-golden-moves
- [x] 4A.6 budget-debit (debit-after-refill, `entity.spent`, attempt-pays/refusal-free, replay-once,
  re-hash, RulesetVersion 10→11; AFTER 4A.1; Depends: 4A.5, 4A.1)
  - [x] 7 Testing bullets: debit-after-refill; flat per-act; spent-refusal; attempt-pays/refusal-free;
    replay-once + post-trim convergence; old-log hash (fixed-point + priced divergence); hold-zero interim
- [x] 4A.7 hold-allowance (refill arm + ReachMap stance-gate + Move-only gate lock + AI single-slot +
  comment/fixture; Depends: 4A.5; rides 11)
  - [x] 7 Testing bullets: allowance refill; no-march; reach-empty; act-admitted-not-held-dropped;
    heal-consumes-slot; upkeep-agnostic; golden re-bless table (dig-in + wild-pack move, rest green)
- [x] 4A.8 claim-pricing (5 verbs wired, transfer charged-0; §Named gap ALREADY FIXED in spec — no
  plan action; Depends: 4A.6)
  - [x] 8 Testing bullets + deposit-pipe proof (5 round trips, exact strings + budgets) + per-verb
    golden deltas (zero-kind + transfer-only identical, priced diverge by exactly the debit)
- [x] 4B.1 Wonder seed rows (`standing-stones` Sector/Common relicCost 1 + `sunspire-throne`
  Empire/Unique relicCost 3, hand-authored under `gk-data/packs/fusion/data/seed/structures/wonder/`)
  - [x] Validate acceptance: pairing holds; reserved probes (World scope, DefensePower/AuraGrant/
    EmpireBuff) refused loud naming the member; exact-case spellings; valueMilli placeholder;
    cap-literal ban (ExistenceCapFor tunable-read proof; Common = long.MaxValue)
- [x] 4B.2 ItemStorage seed row (`relic-vault` bonus 20 at `gk-data/packs/fusion/data/seed/structures/store/relic-vault.json`,
  hand-authored AUTHORED, NO generator fix)
  - [x] write_corpus survival proof + corpus assert; EffectiveCapacity==20 / under-construction-0 /
    wrong-slot tests; granary contributes 0 to the item axis
- [ ] 4B.3 runtime-corpus relic rows (item-program ask §4b)
- [x] 4B.4 live probe (real server :5099, scratch DB: file-commit-started-consumed-completed-persisted all via GET readback; yield correctly 0 on placeholder rows): build → yield + upkeep + persistence via real paths
- [x] 4C.1 lawn-death producer (explicit lawn-Retire trigger; recover rule preserved) (design first: injury-tiers vs lawn→Retire trigger)
- [ ] 4C.2 wipe path (gated on loot-pack §7)
- [ ] 4C.3 anti-fraud Roster gate (item-program ask)
- [x] 4C.4 delve claim verb (12/12; SPILL decided with PackArranger evidence; module 6 separate) §2 + retrieval-mission module 6
- [x] 4D.1 legion-sheet build (drafts built, acceptance pending owner; shared pieces frozen) (drafts accept checkpoint → mount; Depends: 4A.1, 4A.3)
  - [x] Overview tab + per-legion reset; unknown-vs-empty; one-scope probe; file-vs-resolve;
    no-weightEach bus schema; closed-vocab fold; GG-55 (no silent-disable)
- [x] 4D.2a storage-panel build (BLOCK_ORDER +1 vault, never reorder; Depends: 4A.1, 4A.3, 4B.2)
  - [x] Locked-vs-phase-empty naming relic-vault; fog prohibition; winner-no-toast; one-scope probe;
    fits/left-behind fold; Never list (StoragePage + Relics tab never the vault host)
- [x] 4D.2b cache-claim + notify build (AP slot binds server-sent ClaimCostMilli (follow-up closed 2026-09-16: list DTO carries tuning value; const deleted)) (Depends: 4A.1, 4A.3, 4A.6; Estimated L — split pin-vs-toast
  if unwieldy)
  - [x] Pin presence == response presence; claimCostMilli AP display slot (number owned by 4A.5);
    capture header + exactly one loser toast; fog prohibition; one-scope probe; Never list as in 4D.2a
- [x] 4D.3 wonder-composer build (packs owned by 4D.4; Depends: 4A.2, 4A.4, 4B.1, 4D.1; Estimated L —
  split composer-vs-refusal-fold if unwieldy; drafts-accept is an in-task checkpoint, not a phase gate)
  - [x] Slot tree; fold 6 readings + prohibitions; bus 6 events; cost-plate 5 lines; refusal 4 rows;
    themeRefs/catalog owed; 6 draft states + owner-accept gate before any TSX
- [x] 4D.4 wonder-display build (packs + catalog built once here; Depends: 4B.1, 4A.4, 4D.1 meter/row
  twins risk — consume by name, never fork)
  - [x] Pending-state rule (pre-wire cap lines pending, never guessed/hidden); fifth ledger ROW lands
    here; unknown-id placeholder; GG-55-class behaviors per plan

### Checkpoint: inventory UI
- [x] Sheet + vault + claim mountable against 4A routes, zero test-constructed commands
- [x] Build + landmark tests green; bundle budget held
- [x] Re-hash proof (post-debit hash describes committed state); AP display bound to claimCostMilli;
  capture header + loser toast proven (winner: no toast)
- [ ] Reviewed with human (shared pieces freeze here)

### Checkpoint: wonder UI
- [x] Composer + display bind live 4A.4 fields, zero placeholders
- [x] Live N-of-cap proven (Unique "N of cap raised" from tuning; Common buildable-on-cap-grounds)
- [x] Build green; packs never forked
- [ ] Reviewed with human

### Checkpoint: Phase 4 complete
- [x] Every Phase 0-3 verb HTTP-reachable or named-tracked otherwise
- [x] RulesetVersion 11 + per-verb golden deltas (zero-kind + transfer-only identical)
- [x] Live probe: earn → carry → build → observe, zero test-constructed commands
- [x] Full suite + all guards green; audits clean of new findings (no Phase 0–3 re-litigation)
- [x] Scope-creep check clean: no World/Multiverse buildable tier, no cross-faction spend, no second pool
