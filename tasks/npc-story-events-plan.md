# Plan: npc-story-events — the narrative runtime

**Status: approved 2026-09-22, ready for lanes.** Plan written 2026-09-20; owner approved implementation
2026-09-22. No task started, no build authorized. **One premise is rotted and is named in the
addendum below — A1 (HIGH): NR0.2's D2 rows fail the boundary guard's C8 rule as written. NR0.1 is
unblocked; NR0.2 waits on A1's answer.**
Task list: [npc-story-events-todo.md](npc-story-events-todo.md). Program id: `npc-story-events`.
Plan session record: `tasks/sessions/narrative-plan-20260920.json` (this file and the todo are in its `paths`).

Inputs, read in full this session and not reopened here:
[npc-story-events-map.md](../docs/architecture/npc-story-events-map.md) (approved 2026-09-19; module table rows
1–31, waves, build order, gates G0–G7, cross-program table, owner rulings rounds 3–6),
the 28 module specs under [docs/architecture/npc-story-events/](../docs/architecture/npc-story-events/) including
each spec's *Standards audit (2026-09-19)* and *Cross-lane alignment (2026-09-20)* sections,
[npc-story-events-ideal.md](../docs/architecture/npc-story-events-ideal.md) §10 (R1–R23) and §11,
[DESIGN-GATE.md](../docs/DESIGN-GATE.md) §1–§5, `AGENTS.md`/`CLAUDE.md` hard rules and the verification boundary,
[agent-git.md](../docs/contributing/agent-git.md), [session-boundary.md](../docs/contributing/session-boundary.md),
[testing-standard.md](../docs/contributing/testing-standard.md),
[live-probe-standard.md](../docs/contributing/live-probe-standard.md). Coordination sources:
[party-dungeon-todo.md](party-dungeon-todo.md) (transfer note at its top),
[world-continuity-map.md](../docs/architecture/world-continuity-map.md),
[narrative-seed-map.md](../docs/architecture/narrative-seed-map.md), [identity-rename-plan.md](identity-rename-plan.md),
[ip-censor-plan.md](ip-censor-plan.md).

Where a spec and this plan disagree, the spec wins, except for the eight plan decisions in §4, each of which names
the spec text it propagates to and the task that makes the propagation.

---

## 1. What the owner ruled — the input, not reopened here

| Ruling | Content | Where it lands |
|---|---|---|
| R1–R3 | Spine fully generated; the antagonist speaks; finite chapters keyed to a piece per world won, then endless | NR3.13–NR3.15 (scenes, antagonist `ActorId`), NR5.14–NR5.15 (spine), NRX.2 (world-won source) |
| R4 | One 4-band relation ladder for characters and factions | NR2.13–NR2.14 |
| R8–R12 | Names are tokens; lead names from the names registry; surface renames are identity-rename's | NR2.15–NR2.17; §4 D6 (one names reader) |
| R13 | No recurring antagonist; six anti-Nemesis rules | NR3.4 (rules 1–3, 5), NR6.1–NR6.5 (rules 1, 3, 4, 5, 6 at faction level) |
| R14 | Narrative rewards come out of the host's existing budget, never on top | NR4.6–NR4.7 (owed queue, take-a-line), NR2.30 (the world budget line) |
| R15 | The story is also the tutorial (`teaches`, `mechanic.first-seen`) | NR1.2 (`TeachesCatalog`), NR2.6 (`storylet.teaches`), NR3.12 (priority rule), NR3.14 and NR4.2 (the fact at ack and answer) |
| R16 | All 54 legacy Delve events regenerated clean and keyed; the four `story` tails stay dangling as named known defects | NR2.8 (known-defect list), NR2.26 (bridge reads the keyed legacy tree) |
| R17 | World claim loot is this program's (`world-claim-loot`) | NR2.28–NR2.30 |
| R18 | Counter-doctrine reads only what the Rotwright's faction observed | NR6.2 |
| R20 | World storylets read the sector's own `WorldSector.Climate` | NR5.5 |
| R21, R23 | Anomaly slots on `storm`/`nexus`/`barren`; guarded Vault slots in the same new template versions | NR2.31 (allow-list), NR2.32 (template versions; sector picks in §4 D8) |
| R22 | Mythic claim bonus seeds from `WorldSeed.DeriveRollSeed(worldSeed, "claim.mythic", sectorId)` | NR2.28 (plan gate PG3) |
| Round 3 | The Delve's live path is this program's (`delve-live-start`, `delve-live-rooms`) | NR2.20–NR2.27 |
| Round 4 | World-scoped story state is never deleted: live, dormant, frozen | NR1.1 (`WorldNarrativePhase`), NR2.9 (the one write gate), every world-scoped test |
| NS1–NS8 | Drafted `decisions.md` rows, appended by the change that lands each | NR2.2, NR2.13, NR2.9, NR3.2, NR2.17, NR6.3, NR2.8, NR5.4 |

---

## 2. Scope

**In scope.** Map rows 1–25 and 28–31: every Core, Data, Server and web-contract module of the runtime, plus the
Delve live path and the two world prerequisites.

**Blocked, with no build task.** Rows 26 `storylet-card` and 27 `quest-log-layer` (wave 6) wait on `/idea-ui`
(map principle 15, gate G7). **Addendum 2026-09-22:** Phase 7 now carries three `/idea-ui` entry tasks
(NR7.1–NR7.3, `tasks/npc-story-events-todo.md`) that produce the two ideals and then the G7 record; they are
entry points, not build tasks. No build task is written until each surface passes that gate. Their server
contracts (`quest-log-contract`, the offers route in NR5.8, `DelveEventDto`) are built here, so `/idea-ui` designs
against real DTOs. The stale `EventPanel.tsx` comment (map *Conflicts* item 3) stays with `storylet-card`.

**Out of scope, so no task drifts into it.** Seed generation and every file under `gk-data/packs/fusion/data/seed/narrative/**` except
the doctrine registry rows this program authors (narrative-seed); extraction, room clear and quest verdicts at
`CloseDelve` (party-dungeon); the turn loop, phase order, faction policies and clan needs (world-map-program);
surface renames and the title (identity-rename); the IP release gate (ip-censor); playback rows, inspector and rail
surfaces (world-stage, filed as asks); push delivery (notification-ssot); achievement evaluation (achievement-title).

---

## 3. Build order — the map's waves, sliced into tasks

The map's order is binding (`npc-story-events-map.md`, *Build order*). Each wave becomes one phase; the task order
inside a phase follows the map's dependency direction.

| Phase | Wave | Modules | Tasks |
|---|---|---|---|
| 0 | — | session record, verification boundaries | NR0.1–NR0.2 |
| 1 | 0 | `narrative-vocabulary` | NR1.1–NR1.6 |
| 2 | 1 | `storylet-reseam` → `storylet-contract` ∥ `story-ledger` → `relation-ledger` ∥ `narrative-text` ∥ `host-content-theta` → `delve-live-start` → `delve-live-rooms`; ∥ `world-claim-loot`; ∥ `world-anomaly-sites` | NR2.1–NR2.32 |
| 3 | 2 | `character-registry` → `cast-resolver` ∥ `narrative-predicates` → `storylet-selection`; `scene-script-loader` | NR3.1–NR3.16 |
| 4 | 3 | `choice-resolution` ∥ `quest-sources` → `outcome-routing` → `quest-log-contract` | NR4.1–NR4.9 |
| 5 | 4 | `delve-host`, `world-events-host` → `petition-host`, `expedition-lead-host`, `sanctum-hub-host`, `spine-progress`, `failure-branches` | NR5.1–NR5.17 |
| 6 | 5 | `counter-doctrine` ∥ `narrative-readings` | NR6.1–NR6.7 |
| 7 | 6 | `storylet-card`, `quest-log-layer` | NR7.1–NR7.3 (the two `/idea-ui` passes and the G7 record); no build task until each passes |
| X | — | follow-ups that wait on another program's module | NRX.1–NRX.3 |

**Ordering rules the phases keep.**

1. **The Delve's live path precedes its host.** `delve-live-start` (NR2.20–NR2.22) → `delve-live-rooms` (NR2.23–NR2.27)
   → `delve-host` (NR5.1–NR5.2). `delve-live-start` also follows `host-content-theta` (NR2.18), the one
   `ParentWorldTerms` producer. `delve-live-rooms`' text half (NR2.26–NR2.27) follows `narrative-text` and
   narrative-seed's `dungeon-generator-repair`.
2. **World prerequisites precede their hosts.** `world-claim-loot` (NR2.28–NR2.30) lands before `world-events-host`
   (NR5.3–NR5.8) and `petition-host` (NR5.9); `world-anomaly-sites` (NR2.31–NR2.32) before `world-events-host` and
   `counter-doctrine`. `world-claim-loot` depends on no module of this program, so it may run in parallel with the
   whole of Phase 2.
3. **World, expedition and homeworld hosts do not wait on the Delve.** NR5.3–NR5.17 depend on Phase 4 and their own
   prerequisites only. A slipped Delve task never blocks them.
4. **`storylet-reseam` and party-dungeon's open event-deck work**: whichever lands second carries the other's call
   sites (map, *Dependency direction*). `keepverse-split` (direct mode) claims
   `gk-core/tests/FusionRpg.Core.Tests/Delve/Events/EventCatalogTests.cs`, one of the moved tests; the file was clean on
   2026-09-20, and if it is dirty when NR2.2 starts, NR2.2 waits for that edit to be committed (§7): a namespace move
   cannot skip one of its tests.

   **Plan audit 2026-09-20 — the rule above under-states the collision, so NR2.2 now carries a hand-off step.**
   `party-dungeon-todo.md`'s transfer note (`:8-14`) keeps **the resolver logic**, **the 256-seed sweep** and the deck
   goldens with party-dungeon, and its **D3.3 (`:1411`), D3.5 (`:1607`) and D3.9 (`:1818`) are still open**. All of
   that work lives in `gk-core/src/FusionRpg.Core/Delve/Events/**` — the exact 18 files NR2.2 moves out and deletes. "Carries
   the other's call sites" covers referrers; it does not cover an open task in another plan whose declared paths stop
   existing. So NR2.2 additionally: (a) lists, in its commit body, the old → new path of every moved file; (b) records
   the same table in `tasks/party-dungeon-todo.md`'s transfer note as a one-line pointer, under clean-or-skip, so
   party-dungeon's open D3.3/D3.5/D3.9 retarget instead of failing; and (c) states in its evidence line whether D3.3,
   D3.5 and D3.9 were open at the time. If any of them is **in progress in another live session**, NR2.2 defers — a
   move across live work is the one thing `session-boundary.md` will not merge.
5. **`world-events-host` needs only the catalog half of `world-anomaly-sites`.** NR5.3 follows NR2.31 (the
   allow-list). The template half (NR2.32) waits on world-continuity's `WorldCreation.Rebuild`; until it lands no
   world holds an anomaly, so `world.anomaly` storylets are simply ineligible (`spec-world-anomaly-sites.md` §3) and
   the host is otherwise complete.

**Parallel lanes.** Inside Phase 2, four lanes share no file: (a) reseam → contract; (b) ledger → relation;
(c) text; (d) theta → delve live path; plus the two world lanes (claim loot; anomaly sites). Phase 5's hosts are
parallel after NR5.3–NR5.7 except petitions (after the world host) and the Delve host (after the live path).

---

## 4. Plan decisions

### D1 — One task, one commit, one module slice

Each task is one commit: code, tests, the evidence line and the todo status line together, explicit paths, never
`git add -A`, never amend, never push (`agent-git.md`). A task touches at most about five files; the one exception is
NR2.2 (`storylet-reseam`), a pure move whose file count is mechanical and whose proof is the filtered test diff
(`spec-storylet-reseam.md` §5). No commit carries a watermark.

### D2 — Verification: focused boundaries first, the full suite at three named points only

Measured 2026-09-20 with `verify-change.ps1 -PlanOnly -AllowUnscoped`: `gk-core/src/FusionRpg.Core/**`,
`gk-core/src/FusionRpg.Data/**` and `gk-core/src/FusionRpg.Server/**` resolve to their project **fallbacks**, which run the whole test
project; `gk-core/data/tuning/expeditions.v1.json`, `gk-data/packs/fusion/data/seed/dungeon/**` and every `web/**` path throw
`VERIFICATION BOUNDARY MISSING` (`scripts/verify-change.ps1:118`). So NR0.2 adds focused rows before any code:

| Row (new) | Project | Paths |
|---|---|---|
| `core-narrative` | core, `VerificationId` `core.narrative` | `gk-core/src/FusionRpg.Core/Narrative/**`, `gk-core/tests/FusionRpg.Core.Tests/Narrative/**`, `src/FusionRpg.Core/Delve/StoryletHost/**`, `tests/FusionRpg.Core.Tests/Delve/StoryletHost/**`, `data/tuning/narrative.v*.json`, `data/tuning/narrative-cast-catalog.v*.json`, `gk-data/packs/fusion/data/seed/narrative/_registry/**`, `gk-core/tests/fixtures/narrative/**`, `data/seed/dungeon/events/_known-defects.json` |
| `data-narrative` | data, `data.narrative`, guards `dal`, `test-substrate` | `src/FusionRpg.Data/Sqlite/RpgStore.StoryLedger.cs`, `RpgStore.NarrativeCharacters.cs`, `RpgStore.ClaimLoot.cs`, `tests/FusionRpg.Data.Tests/Narrative/**`, `tests/FusionRpg.Data.Tests/World/ClaimLootPassTests.cs` |
| `server-narrative` | server, `server.narrative` | `gk-core/src/FusionRpg.Server/Narrative/**`, `src/FusionRpg.Server/StoryEndpoints.cs`, `tests/FusionRpg.Server.Tests/Narrative/**` |
| `contracts-narrative` | the `notify-contracts` precedent | `src/FusionRpg.Contracts/Narrative/**`, `gk-core/src/FusionRpg.Contracts/NarrativeTextDtos.cs`, `src/FusionRpg.Contracts/StorySceneDtos.cs`, `src/FusionRpg.Contracts/Delve/**` |
| `guard-narrative` | guard, `guard.narrative` | `gk-core/scripts/guard-narrative.py`, `tests/FusionRpg.Guard.Tests/Narrative*.cs`, `tests/FusionRpg.Guard.Tests/StoryletEngineSingleSourceTests.cs` |
| `data-delve-live` | data, `data.delve-live`, guards `dal`, `test-substrate` | `src/FusionRpg.Data/Seed/DungeonDomainImportRunner.cs`, `tests/FusionRpg.Data.Tests/Seed/DungeonDomainImportRunnerTests.cs` |
| `server-delve-live` | server, `server.delve-live` | `src/FusionRpg.Server/DelveEventEndpoints.cs`, `src/FusionRpg.Server/Delve/**`, `tests/FusionRpg.Server.Tests/DelveEventEndpointsTests.cs`, `tests/FusionRpg.Server.Tests/DelveQuestTrackerEndpointTests.cs` |
| `expeditions-tuning` | core, the expedition tuning tests' `VerificationId` | `data/tuning/expeditions.v*.json` |
| `narrative-readings-script` | the script's test | `scripts/narrative-readings.ps1` |

A path that does not exist yet is mapped by glob. If `guard-verification-boundaries.py` refuses a row that names a
single not-yet-existing file (`scripts/narrative-readings.ps1`), that row moves to the task that creates the file
(NR6.7) and the move is recorded in the NR0.2 evidence line — a default, not a gate.

> **Addendum 2026-09-22 (A1, HIGH) — the paragraph above is now load-bearing, and every exact path in the table
> below must be read as a glob until its file exists.** The guard added rule **C8**
> (`gk-core/scripts/guard-verification-boundaries.py:121-125`): a pattern that `Test-ExactPattern` calls exact
> (`scripts/lib/VerificationBoundaries.ps1:246-249` — no `/**`, no `*`) and that names no file fails as
> **`stale exact path`**. Sixteen of this table's entries are exact single-file paths whose files are unbuilt, and
> `expeditions-tuning` repeats the existing `tuning-expeditions` pattern string, which fails as
> **`ambiguous owner pattern`** (`:116-119`). NR0.2's acceptance in the todo carries the remedy (glob-shaped
> patterns only; exact paths added by the task that creates the file; the `expeditions-tuning` row dropped).
> Measured, not inferred: the guard is green at `15baa1454` (26.95s), and `Test-ExactPattern` returns `True` for
> `data/seed/dungeon/events/_known-defects.json`, `scripts/narrative-readings.ps1`,
> `src/FusionRpg.Server/StoryEndpoints.cs`, `gk-core/src/FusionRpg.Contracts/NarrativeTextDtos.cs` and
> `src/FusionRpg.Data/Sqlite/RpgStore.StoryLedger.cs`, none of which exists. The B1 audit's premise — “the guard
> does not check that a `paths` entry exists on disk” — was true on 2026-09-20 and is not true now.

**Plan audit 2026-09-20 — the refusal rule above was wrong, and the real one changes NR0.2's shape.** Read this
session: `guard-verification-boundaries.py` does **not** test whether a `paths` entry exists on disk (it only checks
the pattern shape, `:71-78`), so a row naming `scripts/narrative-readings.ps1` before NR6.7 writes it is legal and the
stated fallback is dead text kept only as a belt-and-braces default. What the guard **does** refuse is a row whose
`verificationId` has no matching `[Trait("VerificationId", "<id>")]` test anywhere in that row's project
(`:82-92`) — and NR0.2 runs **before any narrative test exists**, so all six of the rows above that carry a
`VerificationId` (`core.narrative`, `data.narrative`, `server.narrative`, `guard.narrative`, `data.delve-live`,
`server.delve-live`) would fail the guard the moment NR0.2 lands them. It also refuses a duplicated owner pattern as
*ambiguous* (`:74-77`), and a row must carry `level` ∈ {`focused`, `module`, `seam`} and no field outside
`{id, kind, paths, project, verificationId, guards, level}` (`:65`).

So **NR0.2 lands every row at `level: module` with no `verificationId`** — the shipped `notify-core-domain` /
`notify-contracts` shape, which is exactly a row written before its focused tests. The row still selects its own
project instead of a whole-tree run, which is the whole point. Each row's `verificationId` (and `level: focused`) is
then added **by the first task that lands a test carrying that trait** — `core.narrative` at NR1.1, `guard.narrative`
at NR1.4, `data.narrative` at NR2.9, `server.narrative` at NR2.14, `data.delve-live` at NR2.20, `server.delve-live` at
NR2.24 — in that task's own commit, with `guard-verification-boundaries.py` in its verify line. That is the same
"the row lands with the thing that makes it true" rule D3 applies to enforcement rows.

**`web/**` has no verification lane** (`test-verification-boundary` owns adding one; filed ask). Web tasks run their
named `npx vitest run …`, `npm run build`, `npm run extract` and `npm run check:bundle` commands and list the web
paths as unmapped in their evidence line. `gk-forge/tools/seedsmith/**` is not edited here.

**The full suite** (`.\scripts\test-fast.ps1 -AllDefault`) runs only at the three points AGENTS.md names:
(1) the end of a phase that finishes a large feature — Checkpoint 4 (G3, the engine) and Checkpoint 6 (program
close); (2) a task that crosses module boundaries, named in its own todo entry — NR2.2, NR2.30, NR2.32, NR3.16, NR5.7,
NR6.3; (3) immediately before a live probe — Checkpoints 2 and 5. Every other task runs
`verify-change.ps1 -Paths <every changed path> -Session <sid>` and nothing broader. A focused failure is diagnosed at
its boundary, never retried as a broad run.

### D3 — Registry rows land with their guard, through one catalogued guard script

`gk-core/scripts/enforcement-registry.v1.json` accepts an invariant row with guard ids from its `guards` catalog **xor** an
`unguardableReason` (`EnforcementRegistryGuardTests` R6), and every catalog guard is a `scripts/guard-*.ps1` that
some invariant names (R1, R8). A test class is not a catalog guard. So:

- NR1.4 adds **one** catalog guard, `narrative` → `gk-core/scripts/guard-narrative.py` (`tier: ci`, `status: gating`), which
  runs `dotnet test` with `--filter "Guard=narrative"` over the Core, Data, Server and Guard test projects and, for
  the three web-backed rows, `npx vitest run` over the named files. It lands in the same commit as the first row
  (`narrative-tuning-no-default`), so R8 never sees an unnamed guard.
- Every test that backs a row carries `[Trait("Guard", "narrative")]`. Each later row lands in the **same commit** as
  the test that makes it true, lists `["narrative"]` (plus `dal` where it is a SQL rule), and its `source` cites the
  spec section. A row whose rule no scan can see carries an `unguardableReason` instead.

The rows, with the task that lands each:

| Row id | Guard / reason | Task |
|---|---|---|
| `narrative-tuning-no-default` | narrative (`NarrativeVocabularyTests` missing-key loop) | NR1.4 |
| `ns1-one-storylet-engine` | narrative (`StoryletEngineSingleSourceTests`) | NR2.2 |
| `ns-storylet-preflight-at-load` | narrative (`StoryletContractTests`, one red fixture per rule) | NR2.5 |
| `ns3-story-ledger-append-only` | narrative (`StoryLedgerStoreTests` text scan) | NR2.9 |
| `ns3-story-sql-in-data` | dal | NR2.9 |
| `ns-world-scope-never-deleted` | narrative (append-only scan + per-edge lifecycle test) | NR2.9 |
| `ns2-one-relation-ladder` | narrative (`NarrativeRelationLadderGuardTests`) | NR2.13 |
| `ns2-relations-access-not-stats` | narrative (`RelationLedgerTests` loyalty contract test) | NR2.13 |
| `ns-one-narrative-text-dto` | narrative (Contracts reflection test) | NR2.15 |
| `ns5-names-are-tokens` | narrative (two-name-set render test, C# and web) | NR2.17 |
| `ns-one-content-theta-producer` | narrative (`HostContentThetaTests` source scan) | NR2.18 |
| `ns-delve-boot-import-never-throws` | `unguardableReason`: a behavioural property of one runner (`DungeonDomainImportRunnerTests`) | NR2.20 |
| `ns-delve-one-answer-path` | narrative (Server route-table test) | NR2.25 |
| `ns-no-blank-event-text` | narrative (`DelveEventEndpointsTests` unkeyed refusal + web adapter test) | NR2.27 |
| `ns-world-claim-loot-once` | narrative (`ClaimLootPassTests`) | NR2.30 |
| `ns6-no-enemy-growth`, `ns6-no-enemy-memory`, `ns6-no-enemy-hierarchy` | narrative (`NarrativeNoEnemyGrowthTests`) | NR3.4 |
| `ns6-no-enemy-data-sharing` (R13 rule 5) | `unguardableReason` at NR3.4 (no upload path exists to scan); **upgraded** to guard narrative (`NarrativeNoNetworkTests`) at NR6.5, per `spec-counter-doctrine.md` §7 | NR3.4, NR6.5 |
| `ns-narrative-streams-named` | narrative (stream-prefix scan over `gk-core/src/FusionRpg.Core/Narrative/**`, in Guard.Tests) | NR3.5 |
| `ns-narrative-leaf-context` | narrative (`NarrativeLeafTests` context test) | NR3.9 |
| `ns-no-per-host-selection` | narrative (`StoryletEngineSingleSourceTests` extended to `*Selector`) | NR3.12 |
| `ns-one-scene-player` | narrative (web test: `StorySceneHost` is the only beat renderer) | NR3.16 |
| `ns-choice-stream-literal` | narrative (`ChoiceResolverTests` stream-literal scan) | NR4.1 |
| `ns-quest-no-lawn-only-objective` | narrative (`QuestObjectiveRegistryTests`) | NR4.3 |
| `ns-outcome-host-budget` | narrative (`EventDeckPreflightTests` + `OutcomeRouterTests`) | NR4.6 |
| `ns-quest-log-dto-vocabulary` | narrative (`QuestLogDto` reflection test) | NR4.8 |
| `ns-world-story-seam-null` | narrative (world golden suite with the seam over an empty input) | NR5.3 |
| `ns-petition-no-loam-payment` | narrative (`petition.pays-loam` red fixture) | NR5.9 |
| `ns-expedition-lead-disjoint-stream` | narrative (tier-hash tests at `encounter.* = 0` and `1000`) | NR5.10 |
| `ns-failure-no-second-penalty`, `ns-failure-enemy-personal` | narrative (`EventDeckPreflightTests` red fixtures) | NR5.16 |
| `ns6-doctrine-no-magnitude` | narrative (`DoctrineMagnitudeKeyTests`) | NR6.1 |
| `ns6-reading-aggregate-only` | narrative (`DoctrineReadingAggregateTests`) | NR6.2 |
| `ns6-doctrine-same-rung` | narrative (`DoctrineSameRungTests`) | NR6.4 |
| `ns6-no-trait-base`, `ns6-warlord-world-rules-only` | narrative (`NarrativeNoTraitBaseTests`, `NarrativeNoWarlordWriteTests`) | NR6.5 |
| `ns-readings-no-decision-reader` | narrative (`NarrativeReadings` reference scan) | NR6.6 |

Thirty-seven distinct rows (one, `ns6-no-enemy-data-sharing`, lands twice: as a reason, then upgraded to a guard), one catalog guard. Each row's test also has a falsifier: a probe source string or fixture built in
memory that the test must reject, never written under `src/`.

**Plan audit 2026-09-20 — one catalog guard makes a vacuous pass easy, so the guard refuses one.** The enforcement
meta-test proves R1 (the script exists and every `scripts/guard-*.ps1` on disk is catalogued), R6 (guards **xor**
reason) and R8 (a catalogued guard is named by some invariant). **None of them looks inside the script**, and a
`--filter "Guard=narrative"` run that matches nothing exits 0. So with 37 rows riding one filter, a row whose test
forgot `[Trait("Guard", "narrative")]` — or a row added with no test at all — is green and enforces nothing. Two
additions close it, both landing with the guard in NR1.4:

1. `gk-core/scripts/guard-narrative.py` carries a committed **row → test-class map**, derives from
   `gk-core/scripts/enforcement-registry.v1.json` the set of invariant ids whose `guards` contains `narrative`, and exits
   non-zero naming any row absent from the map (and any map entry naming no row). Every later row task appends its
   line in the same commit as its test — the sibling program's `guard-narrative-seed.ps1` does the same (its plan D4).
2. The guard exits non-zero if the trait filter selects **zero** tests in any project it names, and prints the
   selected count per project so a silent collapse is visible.

Falsifier, run in NR1.4's verify: add a throwaway row with `guards: ["narrative"]` and no map line, confirm the guard
names it, remove it; then strip the trait from one real test and confirm the count drops and the guard fails.

### D4 — Every narrative tuning key is declared in `narrative.v1.json` at wave 0

The loader requires every key and has no default (`spec-narrative-vocabulary.md` §4–§5; T5). Seven later specs say
their keys are "added to `narrative.v1.json` in this module's build change" (`quest-sources` §Data shapes,
`quest-log-contract` §2, `world-events-host` §Data shapes, `failure-branches` §Data shapes, `counter-doctrine` §6,
`narrative-readings` §Data shapes, `delve-host` §Data shapes). Once v1 is committed, a hand edit is forbidden and every
change is a published `v{n+1}` (tunables-ssot T4). So NR1.4 creates v1 with the **union** of every key those specs
declare, at the starting values each spec already chose by principle: `selection.*`, `firing.*` for all 16 host kinds,
`cooldown.*`, `fairness.*`, `relation.*`, `casting.*` (including `saveCastPerRole` and `delveResidentsPerRole`),
`gates.leadLevel`, `quest.expiry.*`, `questLog.recentClosed.*` (one per `HostClockKind`), `world.offerLifetimeTurns`,
`failure.priorityWindow.*`, `doctrine.*` (six keys) and `readings.*` (three keys). A key discovered later is a
`gk-core/tools/tuning/publish.py narrative --add-key` publish to `v2` whose readers switch in the same commit
(`implementer-hard`). NR1.6 propagates this decision into the seven specs' text (evidence rule 6).

The same rule applies to two other files: `data/tuning/narrative-cast-catalog.v1.json` is created at NR3.7 with both
`residentRolesBySlot` (`cast-resolver`) and `residentRolesByRoomKind` (`delve-host`); `expeditions.v2.json` is published
once at NR2.19 with both `tiers.*.dangerBand` (`host-content-theta` §4) and `encounter.*` (`expedition-lead-host` §6),
so `expedition-lead-host` needs no second publish.

### D5 — `ConditionCompiler` is split across two waves

`storylet-contract` (wave 1) compiles every widened `{id, arg}` condition through `ConditionCompiler`
(`spec-storylet-contract.md` §3), which `narrative-predicates` (wave 2) owns (`spec-narrative-predicates.md` §5). The
shell and the arms that reach **built** targets — `none`, `danger-band-is` (`BandIs`), `role-cast` (a `RoleGate`),
the `use` intrinsic gate (`HoldsStock`) and the `offer` affordability marker — land with the loader in NR2.4. The arms
for the six new leaves land with those leaves in NR3.10. Until then a condition id whose leaf is not built is refused at
load with `storylet.condition-unknown`. No real narrative corpus exists before narrative-seed's wave 5, so nothing real
is refused; the wave-1 fixture corpus uses only built-target conditions.

### D6 — One names registry reader, shared with identity-rename

identity-rename's T1 builds `gk-core/src/FusionRpg.Core/Narrative/LeadNames.cs` (new) and its T3 builds
`gk-web/web/fusion-rpg-web/src/i18n/leadNames.ts` (new) over `gk-data/packs/fusion/data/seed/narrative/_registry/names.en.v1.json`
(`identity-rename-todo.md` T1, T3). `narrative-text` needs the same two readers for lead tokens. So NR2.15 and NR2.17
**use** those files if identity-rename has landed them, and otherwise **create them at those exact paths and names**
with identity-rename's acceptance criteria, which identity-rename's tasks then adopt. `narrative-text`'s
`namesRegistry.ts` (its spec's Structure) is not created: character names resolve through lingui keys, lead names
through `leadNames.ts`. One reader per language, whichever program writes it first. The same rule covers the Server
copy rule for `gk-data/packs/fusion/data/seed/narrative/_registry/**` (identity-rename T2 and NR1.5).

### D7 — World lifecycle through one seam until world-continuity lands

The round-4 lifecycle (`Live`, `Dormant`, `Frozen`) is derived from `rpg_worlds` attention and outcome, but the
`outcome` column and the `hibernating`/`idle` values do not exist until world-continuity's `world-state-vocabulary`
(`world-continuity-map.md` module 1). NR2.9 therefore reads the phase through one Data method,
`WorldNarrativePhaseOf(db, tx, worldId)`, whose production body today returns `Live` for the only state any world
holds, and whose lifecycle tests drive a fixture reader through every edge. NRX.1 replaces the body with the real
column read when `world-state-vocabulary` lands. No host, selector or caster reads world state directly; every one
takes the phase from this method or from `RelationRead.Phase`.

### D8 — R23: which sectors get the guarded Vault slots

R23 asks the plan to pick the sectors by §1's fit-and-spread rule and to test reachability (`spec-world-anomaly-sites.md`
Objective). **Fit:** a vault is sealed history on settled ground, and only `stable` and `boss-lair` allow `vault`
(`gk-core/src/FusionRpg.Core/World/SectorTypeCatalog.cs:66`, `:100`), so no allow-list changes. Neither shipped template has a
`boss-lair` sector, so the picks are `stable`. **Spread:** one site per side of each template, so study sites sit on the
player's reachable ground and, where the template has one, on the Rotwright's.

| Template (new version) | Sector | Slot | Why this sector |
|---|---|---|---|
| `first-light` | `frost-mire` (stable, ice, band 1, `WorldTemplateCatalog.cs:124`) | `vault` at index 3, `guard-medium`, `Intact` | one lane from the start sector (`l-home-frost`, `:177`); its sibling `ember-hollow` already carries a `lair`, so the vault spreads the guarded sites |
| `two-hearths` | `d-flank-2` (stable, earth, band 1, `WorldTemplateCatalog.TwoHearths.cs:65`) | `vault` at index 3, `guard-medium`, `Intact` | the player's side, one lane from `d-home` (`l-dh-df2`, `:254`) |
| `two-hearths` | `z-flank-2` (stable, fire, band 1, `WorldTemplateCatalog.TwoHearths.cs:207`) | `vault` at index 3, `guard-medium`, `Intact` | the Rotwright's side, so a raid on his ground is a contested choice (`spec-counter-doctrine.md` §5) |

`guard-medium` is the guard the templates already give a material-bearing site of middle value (`material-seam`,
`WorldTemplateCatalog.TwoHearths.cs:125`); the build task confirms the wave id against the guard catalog and records
it. The acceptance test is R23's own: each new template version places at least one `vault` reachable over lanes from
the start sector.

**Plan audit 2026-09-20 — R23 has not reached the map or the spec body, so NR2.32 propagates it.** R23 is in
`npc-story-events-ideal.md` §10 and in `spec-world-anomaly-sites.md`'s R-note, but the approved
`npc-story-events-map.md` records rounds 3–6 with **R20–R22 only** and its row 31 still reads that no template places
a `vault` and the question is *"still open"*; `spec-world-anomaly-sites.md` §4 and §6 still carry the pre-R23 text
and contradict the spec's own R23 note. Code beats docs, but a stale map row and a self-contradicting spec are
exactly what the next session reads and re-derives. NR2.32 therefore lands, in the same commit as the template
versions: the map row 31 correction, and `spec-world-anomaly-sites.md` §4/§6 rewritten to D8's three picks. This is
propagation of an owner ruling, not a new decision — no gate.

---

## 5. Agent types

Execution by any agent needs the owner charter first — runtimes, exact models, budget, stop rule
(`CLAUDE.md` *Multi-agent runs start with the owner's charter*; the `project-manager` skill). Within an approved charter:

| Agent type | Tasks |
|---|---|
| `refactorer` | NR2.2 (the re-seam: a cross-module move of the engine behind a new seam) |
| `implementer-hard` | NR2.9 and NR2.11 (new tables; the event-seen migration and drop), NR2.19 (tuning publish with its readers in the same commit), NR2.28–NR2.30 (claim commit path; R22 seed; replay), NR2.32 (template versions and their golden re-bless), NR3.2–NR3.3 (the character table; specimen ownership transfer), NR5.3, NR5.6, NR5.7 (the turn-engine seam; the `story_input_json` turn-log column; `RulesetVersion` and the golden re-bless), NR5.11 (the `leads_json` expedition column), NR6.3 (hashed faction state and its goldens) |
| `implementer` | every other build task |
| `test-engineer` or the implementing session | the live probes NR-LP1 and NR-LP2 |
| `locator` | any file search inside a task, instead of spending an implementer's context |

Every golden that moves is **measured, not assumed**: the task runs the golden suite before and after, lists each
moved hash, and re-blesses only in the same commit and only under the reviewing program named in its entry.

---

## 6. Gates

Plan gates are named PG1–PG3 so they never collide with the map's gates G0–G7. A gate blocks only an irreversible action; each has a resolver and a default (`planning-and-task-breakdown`
*Gates vs. checkpoints*). Every other decision is a tracked ask (§9) or a checkpoint.

| Gate | Blocks | Why irreversible | Resolver | Default if unanswered when reached |
|---|---|---|---|---|
| **PG1** Drop `rpg_delve_event_seen` after copying it into the ledger | NR2.11's `DROP TABLE` only | A drop on the owner's real save cannot be undone without a backup | Owner | Proceed: the migration copies, re-reads the copied facts and compares them with the old rows **inside one transaction**, drops only on equality, and takes a file backup of the save first (the ip-censor T19b precedent). A mismatch rolls back and fails the boot loudly |
| **PG2** A `RulesetVersion` bump and a world golden re-bless with story content on (NR5.7), and the hashed `WorldFaction.Doctrine` field once any world holds a non-null value (NR6.3) | Committing turns under the new behaviour on real saves | Turns committed under a ruleset replay only under it; re-blessed goldens replace the old truth | world-map-program (the owner as its reviewer) | Follow the version rule written at `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:125` and its history above it: bump when the same command log yields a different state, re-bless in the same commit, list every moved hash. The seam-off and empty-input paths stay byte-identical either way (NR5.3) |
| **PG3** R22's mythic-seed edit when a stored `claim.mythic:` report line exists | NR2.28's commit only | A seed change re-derives a different bonus on replay of a stored report | Owner | The task scans a real server data directory's `rpg_world_turn_log.report_json` first. Zero rows (the expected case, no production caller sets the rate): proceed. Rows found: the edit is built and tested, the commit waits, and the task reports the world ids; every other task continues |

No other task is gated. In particular the NS7 leave rule was approved with the map, the party-dungeon transfer is
recorded, and every external dependency in §8 is a dependency with an owner, not a gate.

---

## 7. Shared files — active sessions and the clean-or-skip rule

Read from `tasks/sessions/*.json` on 2026-09-20, **active records only**. A **worktree** lane meets this program at its
merge; a **direct** session shares this working tree.

| File(s) this plan edits | Also claimed by | Mode |
|---|---|---|
| `gk-core/scripts/verification-boundaries.v1.json` (NR0.2, NR6.7) | `keepverse-split`; summoner-convergence lanes A2, B, C, D, D2, D3 | direct; worktrees |
| `gk-core/scripts/enforcement-registry.v1.json` (NR1.4 and every row task in D3) | lanes B, D2 | worktrees |
| `docs/architecture/decisions.md` (NS1–NS8 rows) | `keepverse-split`, `trade-network-idea-20260919` | direct |
| `gk-core/tests/FusionRpg.Core.Tests/Delve/Events/EventCatalogTests.cs` (NR2.2 using lines) | `keepverse-split` (clean on 2026-09-20) | direct |
| `docs/architecture/party-dungeon/spec-event-deck.md` (NR2.8, NS7) | `narrative-seed-idea-20260919` | direct |
| `gk-core/src/FusionRpg.Server/Program.cs` (NR1.5, NR2.20, NR2.24) | lanes A2, C, D3 | worktrees |
| `gk-core/src/FusionRpg.Server/WorldEndpoints.cs` (NR2.30) | lane D3; lane B (`gk-core/src/FusionRpg.Server/**`) | worktrees |
| `gk-core/src/FusionRpg.Data/Sqlite/**` (ledger, characters, claim loot, delve, world turns, expeditions) | lanes B, C (`Sqlite/**`); D3 (`RpgStore.cs`) | worktrees |
| `gk-core/src/FusionRpg.Core/Expeditions/**`, `gk-core/data/tuning/**` (NR2.19) | lane C | worktree |
| `gk-core/src/FusionRpg.Core/**`, `gk-core/src/FusionRpg.Server/**`, `gk-core/src/FusionRpg.Contracts/**`, `tests/**` (most tasks) | lanes B, D (broad globs); D2 (`gk-core/tests/FusionRpg.Core.Tests/**`, `gk-core/tests/FusionRpg.Guard.Tests/**`) | worktrees |
| `gk-web/web/fusion-rpg-web/src/i18n/locales/**` (NR2.16–NR2.17 extract) | lanes A2, D3 | worktrees |
| `gk-web/web/fusion-rpg-web/src/lib/bus/**` (NR3.16) | lane D3 (`hub-provider.tsx`, `playerRouting.ts`) | worktree |
| `docs/architecture/effect-atom/**`, `docs/architecture/story-scene-map.md` (NR3.8, NR3.15) | lanes B, D (`docs/**`) | worktrees |
| `tasks/npc-story-events-plan.md`, `tasks/npc-story-events-todo.md` | `narrative-plan-20260920` (this plan's author) | direct; the implementing session claims them at NR0.1 |

**Mode for the implementing session.** Lanes B and D claim `src/**`, `tests/**` and `docs/**` in worktree mode, and
`session-boundary.md` §5 reports a direct session whose paths fall under an active worktree's globs as drift even when
the regions differ. So NR0.1 recommends **worktree mode** to the owner (the owner decides); in direct mode the session
proceeds only while `session-boundary-check.py --session <sid>` is clean.

**Clean-or-skip, for every shared file, before the edit** (the ip-censor plan §8 rule, restated):

1. `git status --porcelain -- <file>` is empty. If the file is dirty with another direct session's uncommitted work,
   **skip it**: commit the task's other files only if they stand alone, otherwise defer the whole task, and record the
   skip in the todo's evidence line. Exception: NR2.2 cannot skip a moved test, so if `EventCatalogTests.cs` is dirty
   it waits for that edit to be committed.
2. For each worktree lane that claims the file, `git diff $(git merge-base HEAD <branch>)..<branch> -- <file>` does not
   touch the region being edited (`session-boundary.md` §5). A region overlap is resolved with the owner; a different
   region merges cleanly. Boundary and registry rows go in one contiguous block at the end of their arrays (the
   identity-rename plan §5 precedent).
3. **Never** `git stash`, `git checkout -- <file>` or `git reset` around another session's work, and never `git add -A`.

**Keepverse split.** `keepverse-split` may move this tree into sub-repos (`tasks/keepverse-split-plan.md`). Unfinished
tasks then retarget their paths; no task depends on a path the move renames.

---

## 8. Cross-program dependencies

### 8.1 narrative-seed — which seed module unblocks which runtime task

| narrative-seed module (wave) | Unblocks | Before it lands |
|---|---|---|
| `storylet-vocab` (1) | NR1.2 (storylet registries: choice kinds, consequence kinds with `refForms`/`params`, conditions with `usableIn`, role tags, `teaches`, host kinds) | NR1.2 is built and tested against fixture registry files under `gk-core/tests/fixtures/narrative/_registry/`; the task's commit that reads the real files waits |
| `character-vocab` (1) | NR1.3 (roles, line contexts, voice registers) | same fixture rule |
| `token-grammar`, `names-registry` (1) | NR2.15–NR2.17 real grammar and lead rows | fixtures; lead rows per identity-rename D1 if it lands first (§4 D6) |
| `narrative-contract` (2) | NR2.3–NR2.7 (the seed side's own `validate_entry` green fixtures), NR3.1 (character schema), NR5.14 (spine chapter schema) | fixtures written from the spec text |
| `quest-vocab` (2) | NR4.3 (anchor → `QuestRow` mapping, objective registry) | fixtures |
| `arc-shapes` (1) | NR5.14–NR5.15 (the spine frame, fragments) | fixtures |
| `dungeon-generator-repair` (0, including its regeneration run after `gloss-fill`) | NR2.26 (the bridge reads keyed legacy events), NR2.27 (Delve text on the wire), the known-defect list in NR2.8 | NR2.26–NR2.27 wait; NR2.20–NR2.25 do not |
| pipelines (5), `delve-event-regen` (6) | real content in every host; `delve-event-regen` itself waits on this program's NR2.3–NR2.8 | hosts run on fixture corpora; content volume is a reading (NR6.6), never a test |

### 8.2 Other programs

| Program · module | This plan reads or asks | Blocks | State (2026-09-20) |
|---|---|---|---|
| party-dungeon | Transferred here: D4.16 boot caller, D4.22 five `/start` delegates, D4.14 offer and tracker, D3.9 answer route and store callers, D3.3/D3.5 live call site (`party-dungeon-todo.md` transfer note, `:8-14`). Stays there: the import arm, D4.19 display delegates, D4.17/D4.30 content, extraction, room clear, `CloseDelve` verdicts, deck goldens, **the resolver logic and the 256-seed sweep** (**Plan audit 2026-09-20:** this row previously dropped those last two, and they are exactly the ones living in the files NR2.2 moves — see §3 rule 4) | NR2.20–NR2.27 build only the transferred clauses. `delve.wiped` (NR5.17) and the Delve quest verdict mirror (NR4.5) stay inert until `CloseDelve` has a production caller — a wiring gap owned by party-dungeon | Plan approved; extraction open |
| world-continuity · `world-state-vocabulary` | the `state`/`outcome` columns | NRX.1 (production phase reader, §4 D7) | Map approved; no plan yet |
| world-continuity · `world-victory` | `rpg_world_won_facts` | NRX.2 (production `IWorldOutcomeSource`); the spine past chapter 1 | Map approved |
| world-continuity · `world-fall`, `coarse-step` | the fall edge; per-loss digest facts | NRX.3 (quest fail-by-fall trigger; coarse-step losses opening branches) | Map approved |
| world-continuity · `world-creation` | `WorldCreation.Rebuild` (versioned replay) | NR2.32 (template half) | Map approved; not built |
| world-continuity · `world-event-budget` | its row says hibernating events resolve inside `CoarseStep` from the same deck; this program's specs say a dormant world is never drawn | nothing here; reported at map level (`spec-world-events-host.md` §4) | open between the maps |
| world-map-program | review of the claim seam, the story seam, `event.choose`, `story_input_json`, `RulesetVersion`, the doctrine field; guard-fight simulation; `ai-commander` clan policy and needs; doctrine consumption in `FrontierRulesPolicy`, `RaiseResolver.SpeciesFor` and wild spawns (filed asks) | reviews at NR2.28–NR2.30, NR5.3–NR5.7, NR6.3; clan requests (NR5.9) fire only once needs are real; a storylet `fight` resolves as a refused no-op until guard fights simulate; a doctrine is visible and inert until consumed | — |
| world-stage | playback rows for `story.*` and `doctrine.*` kinds; inspector petition block; rail item (filed asks) | nothing here | — |
| achievement-title · `achievement-evaluator` | hosting the evaluator | quest completion is durable evidence meanwhile (NR4.4) | open |
| notification-ssot | player-routed push | the turn report and rail meanwhile | lane D3 building |
| trade-network · `counterparties` | reads `RelationReader.FactionBand` (NR2.14) | nothing here | ideal only |
| story-scene | reviews the widening in NR3.15 (`SceneId`, speaker union, antagonist `ActorId`, optional props) | NR3.15 lands under that review | approved program |
| identity-rename | names registry file and readers (§4 D6); the antagonist `ActorId` member id follows its identifier allow-list (its plan §2 keeps `"dave"`/`"penny"`). **Plan audit 2026-09-20 — one uncoordinated collision:** its **T13** (`identity-rename-todo.md:221-222`) edits `WorldTemplateCatalog.cs` / `WorldTemplateCatalog.TwoHearths.cs` and re-blesses any world golden a renamed faction moves, and **NR2.32** publishes new versions of the same two files and re-blesses their goldens. Neither plan's §7/§5 names the other for these paths, and two independent re-blesses of one golden set is how a hash silently stops meaning anything | **NR2.32**: clean-or-skip against T13 before editing; whichever lands second re-runs the golden suite **after** the first and lists the full moved set, never only its own delta; if both are in flight, the owner sequences them (default: identity-rename T13 first — a rename is cheaper to redo than a template version) | plan awaiting approval |
| ip-censor | scans character names and storylet titles at release (IC-3) | nothing | plan awaiting approval |
| first-session-progression | the "first character met" slot (filed ask, NR5.13) | nothing; the hub runs without the special case | — |
| item program | derived base price for the Delve merchant; `offer:supply` stays unpriced | nothing; the choice shows ineligible with its reason | — |
| test-verification-boundary | a web lane for `web/**`; the python lane | nothing; named npm commands meanwhile | lane D2 building |
| power | `ssot-power-scale.md` §8 row 6 wording (expedition content as a danger band composed through `ContentExplain`) | nothing; propagation owed outside this program | open |

---

## 9. Tracked asks (non-blocking), each with a resolver and a default

| Ask | Resolver | Default when the task is reached |
|---|---|---|
| **A1** `petition-host` files a `sector.need` leaf; `narrative-predicates` fixes six new leaves and lists "a seventh narrative leaf" under *Ask first* (`spec-narrative-predicates.md` Boundaries; `spec-petition-host.md` §2) | Owner | NR5.9 adds `SectorNeedIs` as a reviewed seventh narrative leaf (`LeafId` 22 → 23, the leaf-count test and `spec-predicate-tree.md` updated in the same commit, the seed condition id filed on `storylet-vocab`). Reversible: leaf ordinals are compiled at load, never stored |
| **A2** The antagonist's `ActorId` member id | identity-rename (its identifier allow-list) | NR3.15 uses the id identity-rename's allow-list names; if it names none, `"rotwright"`, recorded as an identifier identity-rename keeps |
| **A3** World-stage playback rows for the six new report kinds; inspector petition block; rail item | world-stage | Filed in NR5.4, NR5.9, NR6.3; the raw prefix never reaches a player because world-stage's translation table refuses unknown kinds |
| **A4** Doctrine consumption by world-map's policy and species draw | world-map-program | Filed in NR6.3; the doctrine is adopted, reported and inert until then (`spec-counter-doctrine.md` §3) |
| **A5** `ssot-power-scale.md` §8 row 6 wording | power program | Filed in NR2.18 |
| **A6** Hosting `AchievementEvaluator` | achievement-title | Evidence is durable; a later evaluator backfills by fact id (`spec-quest-sources.md` §7) |
| **A7** A web verification lane | test-verification-boundary | Named npm commands per task (§4 D2) |

---

## 10. Checkpoints

| Checkpoint | After | Proves | Full suite |
|---|---|---|---|
| CP1 — vocabulary | NR1.6 | every registry and tuning key loads or rejects by name; one guard catalogued | no |
| CP2 — one engine, the Delve starts (G1, G2) | NR2.32 (NR2.26–NR2.27 and NR2.32 may trail on their external dependencies; the checkpoint records which) | G1 and G2 of the map; the Delve starts and its rooms play through real routes (NR-LP1) | yes, point 3 (before NR-LP1) |
| CP3 — cast and select | NR3.16 | casting, predicates, selection and scenes over fixture corpora, game closed | no (NR3.16 already ran it, point 2) |
| CP4 — a storylet resolves (G3) | NR4.9 | G3 end to end on a fixture host, deterministic on replay | yes, point 1 |
| CP5 — places play (G4, G5) | NR5.17 | G4 world, expedition and hub halves; G5 through real routes (NR-LP2) | yes, point 3 (before NR-LP2) |
| CP6 — doctrine and program close (G6) | NR6.7 | G6; every registry row in D3 green; G7 recorded as blocked on `/idea-ui` | yes, point 1 |

Every checkpoint is a review of finished work, never a pre-work gate.

**Live probes** (`live-probe-standard.md`). NR-LP1 (after CP2's full suite) proves `delve-live-start` and
`delve-live-rooms`; NR-LP2 (after CP5's full suite) proves G5 and the world host. Both are **RPG Server scope only**:
the server is started as its own process (`Start-Process dist\FusionRpg.Server\FusionRpg.Server.exe`, never
`deploy-play.ps1` with a server restart from an agent call); every subject is created through a real route a player's
flow uses; every result is read back through the normal query route; no `debug.*` command, no hand-inserted row. The
Injector half is not claimed (the Delve and the world run with the game closed).

---

## 11. Risks

| Risk | Impact | Mitigation |
|---|---|---|
| The re-seam and party-dungeon's open event-deck work both edit the engine | High: a lost call site | Whichever lands second carries the other's call sites (map rule); NR2.1's stream-identity fixture is recorded before the move and must stay byte-equal |
| A focused boundary is missing and a task falls back to a whole-project run | Medium: minutes per task, and the temptation to run everything | NR0.2 lands the rows first; an unmapped production path is a boundary defect to fix, never a reason to run the full suite |
| The world story seam moves a golden unnoticed | High | NR5.3 proves seam-off and empty-input byte-identical before any content; NR5.7 measures every moved hash (PG2) |
| World payouts add rolls instead of taking them (R14) | High: a new faucet | NR2.30 and NR4.7 test that the item-roll count equals the claim-line count across a fixture with more owed payouts than lines |
| A doctrine smuggles strength through a species draw | High: breaks "never how strong" | NR6.4's rung and rarity histogram test (`ns6-doctrine-same-rung`) |
| A legacy Delve event reaches the wire unkeyed or blank | High: breaks the round-4 ruling | NR2.26 refuses an unkeyed legacy row at generation; NR2.27's DTO and web tests; `ns-no-blank-event-text` |
| The implementing session in direct mode crosses a worktree lane's broad globs | Medium: boundary drift | §7 recommends worktree mode; clean-or-skip at every shared file |
| An external module (world-continuity, dungeon-generator-repair) is late | Medium | Only NR2.26–NR2.27, NR2.32 and NRX.1–NRX.3 wait; every other task builds against fixtures or a documented seam |

---

## 12. DESIGN-GATE §5 checklist

```
[x] Subsystems: product loops 2-7 and B; the Delve; world map and stage; expeditions; homeworld; quests;
    achievements (evidence); story-scene; economy (host budgets, claim loot); power (Θ); tunables; effect atoms
    (predicate leaves); battle (handoffs); actor layer (read-only); UI contracts; standalone; live probe.
[x] Session boundary: tasks/sessions/narrative-plan-20260920.json lists both files (direct, features/mega-merge).
    The implementing session records its own at NR0.1.
[x] Read this session: the map in full, all 28 specs in full (audit and alignment sections included), ideal §10
    and §11, DESIGN-GATE §1-§5, agent-git, session-boundary, testing-standard, live-probe-standard, the planning
    skill and /plan command, party-dungeon-todo transfer note, world-continuity-map modules, narrative-seed-map
    §4-§8, identity-rename plan §1-§6 and todo T1-T3, ip-censor plan §8.
[x] decisions.md: NS1-NS8 are drafted in the map and appended by the tasks named in §1; no lock contradicted.
[x] Every factual claim cites file:line or a spec section; the line citations were re-checked this session.
[x] audit-doc-citations.py --scope run on this file and the todo (result in the hand-off).
[x] Claims verified against code: the verification mappings (verify-change -PlanOnly, 2026-09-20), the
    enforcement-registry contract (EnforcementRegistryGuardTests R1, R6, R8), SectorTypeCatalog vault rows,
    template sectors and lanes, RulesetVersion, active session records.
[x] No constraint assumed: golden movement is measured per task (§5); plan gates PG1-PG3 are irreversible actions only (§6).
[x] Nothing contradicts a §2 invariant.
[x] Corrections propagate: D4's key union to seven specs (NR1.6); D5 and D6 recorded in the tasks that use them.
[x] No assertion pins a population: tests assert contracts, closed vocabularies with reasons, joins, determinism
    and structural bounds; corpus sizes, cast sizes and pick rates are readings (NR6.6).
[x] Edge-refreshed caches: the scene-rows cache (NR3.16, five triggers) and the quest-log query (NR4.9, twelve
    triggers) each test every trigger, key-set edges included.
[x] Orderings that vary are tested both ways (draw vs wipe, join vs fall, pin vs corpus bump, fight report vs
    commit, dispatch vs later facts, outing vs entry).
[x] Actor numbers: no task writes one; relationships grant access; doctrines change selection and weights only.
[x] No SOLID-violating parallel path: one engine, one selector, one quest engine, one ladder, one scene player,
    one story store, one names reader per language, one loot roller.
[x] Registry rows: 37, each landing with its guard or reason (§4 D3).
```

---

## Plan audit (2026-09-20)

Independent adversarial standards audit of this plan and [npc-story-events-todo.md](npc-story-events-todo.md),
fix-in-place. Standards read this session: `.claude/skills/planning-and-task-breakdown/SKILL.md`,
`.claude/commands/plan.md`, AGENTS.md *Verification boundary*, `docs/contributing/agent-git.md`,
`session-boundary.md`, `testing-standard.md`, `live-probe-standard.md`,
`docs/architecture/validation-ssot.md`, `tunables-ssot.md`, `gk-core/scripts/enforcement-registry.v1.json` with
`gk-core/tests/FusionRpg.Guard.Tests/EnforcementRegistryGuardTests.cs`, `gk-core/scripts/guard-verification-boundaries.py`,
`DESIGN-GATE.md` §5. Boundary claims were **re-measured**, not re-read.

| # | Sev | Finding | Status |
|---|---|---|---|
| B1 | High | **NR0.2 would have landed six rows the boundary guard refuses on the day it runs.** `guard-verification-boundaries.py:82-92` rejects a `verificationId` with no matching `[Trait("VerificationId", "<id>")]` test in that row's project, and NR0.2 runs before any narrative test exists. The plan's stated refusal rule was also simply wrong: the guard does **not** check that a `paths` entry exists on disk (`:71-78`), so the `scripts/narrative-readings.ps1` fallback was guarding a failure mode that cannot happen | **Fixed** — §4 D2 rewritten; NR0.2 lands every row at `level: module` with no `verificationId` (the shipped `notify-core-domain` shape), and each `verificationId` is added by the first task landing a trait-carrying test (NR1.1, NR1.4, NR2.9, NR2.14, NR2.20, NR2.24) |
| B2 | High | **One catalogued guard over 37 rows makes a vacuous pass easy.** The enforcement meta-test proves R1/R6/R8 only; none looks inside the script, and `dotnet test --filter "Guard=narrative"` matching nothing exits 0. A row whose test forgot the trait, or a row with no test at all, would be green | **Fixed** — §4 D3 and NR1.4: `guard-narrative.py` carries a committed row → test-class map, derives its required rows from the registry, fails on any row not in the map (or map entry not a row), fails when the filter selects zero tests in any project, and NR1.4 runs both falsifiers |
| B3 | High | **NR2.2 moves the 18 files party-dungeon's still-open D3.3/D3.5/D3.9 live in**, and the transfer note keeps *the resolver logic* and *the 256-seed sweep* there. §3 rule 4's "whichever lands second carries the other's call sites" covers referrers, not another plan's open tasks whose declared paths cease to exist | **Fixed** — §3 rule 4 and NR2.2 gain a hand-off step: old → new path table in the commit body and pointed at from `party-dungeon-todo.md`'s transfer note, D3.3/D3.5/D3.9 open-state recorded, and the task **defers** if any of the three is live in another session |
| B4 | High | **Two uncoordinated golden re-blesses of the same world templates.** identity-rename **T13** edits `WorldTemplateCatalog.cs` / `.TwoHearths.cs` and re-blesses any golden a renamed faction moves; **NR2.32** publishes new versions of the same files and re-blesses theirs. Neither plan's shared-file table named the other, and its §8.2 row said identity-rename blocks "nothing" | **Fixed** — §8.2 identity-rename row and NR2.32: clean-or-skip, whichever lands second re-runs the suite after the first and lists the **full** moved set, owner sequences if both are in flight (default: T13 first) |
| B5 | Medium | **§8.2's party-dungeon "stays there" list dropped two clauses** the transfer note names (`party-dungeon-todo.md:14`) — the resolver logic and the 256-seed sweep — and those are precisely the two that B3's move touches | **Fixed** — both restored to the §8.2 row |
| B6 | Medium | **NR2.15's *Files* list omitted `gk-core/src/FusionRpg.Core/Narrative/LeadNames.cs`**, though §4 D6 makes that task create it when identity-rename T1 has not landed. The file would have been written outside the task's declared fence and outside its `-Paths` | **Fixed** — added to NR2.15's *Files* with D6's use-or-create rule |
| B7 | Medium | **R23 has reached neither the map nor the spec body.** The approved map records R20–R22 only and its row 31 still calls the vault question *"still open"*; `spec-world-anomaly-sites.md` §4/§6 still carry pre-R23 text that contradicts the spec's own R23 note. D8 decides the picks against a source the next reader will find saying the opposite | **Fixed** — D8 and NR2.32: the map row and the two spec sections are corrected in the same commit as the template versions (propagation of an owner ruling, so no gate) |
| B8 | Low | **`data/seed/dungeon/events/_known-defects.json` (NR2.8, authored) sits inside the tree narrative-seed's cutover deletes.** Correct and intended, but unsaid — a later reader would "restore" it | **Fixed** — NR2.8 states the list is born to shrink to zero and be removed with the tree at NSG3/NS69 |

**Checked and found correct** (no change needed): every map module has at least one task except rows 26
`storylet-card` and 27 `quest-log-layer`, which §2 blocks on `/idea-ui` with no task and no spec — the
correct treatment, since their server contracts are still built here; no task invents a module; the wave
order, the Delve live-path-before-host rule and the world-prerequisite rule match the map; all five
transferred party-dungeon clauses have a task (D4.16→NR2.20, D4.22→NR2.21, D4.14→NR2.22, D3.9→NR2.23+NR2.25,
D3.3/D3.5→NR2.24) and no task claims a "stays" clause; PG1–PG3 are genuinely irreversible with a resolver
and a default and nothing else is gated (the seven §9 asks are asks, each with a default); every
hard-edge task is marked `implementer-hard` or `refactorer` in §5 and every golden that can move is
**measured before and after**, never assumed; store tests are in memory with one tagged `DiskSemantics`
exception (NR2.11); both live probes are RPG-Server-scope, create subjects through real routes, read back
through the normal query path and claim no Injector half; no acceptance criterion pins a population
(corpus, cast and pick rates are readings, NR6.6); `narrative.v1.json` is created once at wave 0 and every
later key is a `publish.py --add-key` to v2 with its readers in the same commit; the enforcement-registry,
`SectorTypeCatalog` vault-row, template-sector and `notify-contracts`-precedent citations all check out;
`gk-core/src/FusionRpg.Core|Data|Server/**` do resolve to project fallbacks and `gk-core/data/tuning/expeditions.v1.json`,
`gk-data/packs/fusion/data/seed/dungeon/**` and `web/**` do throw `VERIFICATION BOUNDARY MISSING`, exactly as §4 D2 states.

`python scripts/audit-doc-citations.py --scope tasks/npc-story-events-plan.md` — **0 HIGH** (23 resolvable
citations).

**Owner decisions that genuinely remain:** none introduced by this audit. B4 adds one *default* the owner
may override — if identity-rename T13 and NR2.32 are in flight together, T13 goes first.

---

## Addendum (2026-09-22) — premise verification against the convergence head

Verified at `15baa1454` (worktree `cmdc-arch-d`, session `arch-d-20260922`) before the status line moved to
"approved, ready for lanes". Read at this head: `gk-core/scripts/guard-verification-boundaries.py`,
`scripts/lib/VerificationBoundaries.ps1`, `gk-core/scripts/verification-boundaries.v1.json` (read, never edited),
`tasks/party-dungeon-todo.md`, `tasks/narrative-seed-todo.md`, `tasks/test-verification-boundary-todo.md`.

### A1 (HIGH) — NR0.2 as written fails its own guard, and the Plan audit B1 fix is why

The 2026-09-20 audit rewrote D2 and NR0.2 on the finding that the guard **does not** check whether a `paths`
entry exists on disk, so a row naming a not-yet-existing file was "legal now" and the old glob fallback was
"dead text kept only as a belt-and-braces default". **That is no longer true.** Rule **C8** was added to the
guard with the seam-coverage work:

- `gk-core/scripts/guard-verification-boundaries.py:121-125` — for every boundary pattern, if
  `Test-ExactPattern` is true and the path names no file, the guard appends
  **`stale exact path: <id>: <pattern>`** and fails.
- `scripts/lib/VerificationBoundaries.ps1:246-249` — `Test-ExactPattern` returns true when the pattern
  neither ends in `/**` nor contains `*`. An exact single-file path is *exactly* the case C8 rejects while
  that file is unbuilt.

Measured this session, not inferred:

```
VERIFICATION BOUNDARY GUARD OK          # guard-verification-boundaries.py, 26.95s, at 15baa1454
pattern=data/seed/dungeon/events/_known-defects.json       exact=True  existsOnDisk=False
pattern=scripts/narrative-readings.ps1                     exact=True  existsOnDisk=False
pattern=src/FusionRpg.Server/StoryEndpoints.cs             exact=True  existsOnDisk=False
pattern=gk-core/src/FusionRpg.Contracts/NarrativeTextDtos.cs       exact=True  existsOnDisk=False
pattern=src/FusionRpg.Data/Sqlite/RpgStore.StoryLedger.cs  exact=True  existsOnDisk=False
pattern=tests/FusionRpg.Core.Tests/Delve/StoryletHost/**   exact=False existsOnDisk=False
pattern=tests/FusionRpg.Guard.Tests/Narrative*.cs          exact=False existsOnDisk=False
```

(`Test-ExactPattern` called directly against `scripts/lib/VerificationBoundaries.ps1`; the guard is green
**today**, so every failure below is one D2 would introduce.)

**Every exact single-file pattern in D2 is a `stale exact path` while its file is unbuilt** — sixteen of
them: `data/seed/dungeon/events/_known-defects.json` (`core-narrative`); `RpgStore.StoryLedger.cs`,
`RpgStore.NarrativeCharacters.cs`, `RpgStore.ClaimLoot.cs`, `tests/.../World/ClaimLootPassTests.cs`
(`data-narrative`); `src/FusionRpg.Server/StoryEndpoints.cs` (`server-narrative`);
`gk-core/src/FusionRpg.Contracts/NarrativeTextDtos.cs`, `StorySceneDtos.cs` (`contracts-narrative`);
`gk-core/scripts/guard-narrative.py`, `tests/FusionRpg.Guard.Tests/StoryletEngineSingleSourceTests.cs`
(`guard-narrative`); `src/FusionRpg.Data/Seed/DungeonDomainImportRunner.cs` and its test
(`data-delve-live`); `src/FusionRpg.Server/DelveEventEndpoints.cs` and two test files
(`server-delve-live`); `scripts/narrative-readings.ps1` (`narrative-readings-script`).

**And one row is a duplicate of a row that now exists.** `data/tuning/expeditions.v*.json` is already the
pattern of `tuning-expeditions` in the registry, so D2's `expeditions-tuning` row would trip
`ambiguous owner pattern` (`gk-core/scripts/guard-verification-boundaries.py:116-119`) — the check keys on the
pattern string, and the string is identical.

**Remedy (mechanical, inside NR0.2 — no plan reopen needed).**

1. Drop the `expeditions-tuning` row; `tuning-expeditions` already owns that path
   (`gk-core/scripts/verification-boundaries.v1.json`, owner `tuning-expeditions`, module).
2. Give every other row **glob-shaped** patterns only: `**` for a directory, a final-segment `*` for a
   family (`src/FusionRpg.Data/Sqlite/RpgStore.Story*.cs`), or the directory glob plus the exact file added
   **by the task that creates it** (NR2.9 for the ledger store, NR1.1/NR1.4 for the guard, NR6.7 for the
   readings script). The plan's original "a path that does not exist yet is mapped by glob" rule was right
   for this rule; the B1 audit removed it for a reason that does not cover C8.
3. Re-run `python gk-core/scripts/guard-verification-boundaries.py` as NR0.2's own gate — it already is the verify line,
   which is why this is caught by the task rather than after it.

The B1 audit's *other* half stands and is still correct: the `verificationId` rule
(`gk-core/scripts/guard-verification-boundaries.py:151-161`) does refuse a row whose id has no trait-carrying test,
so every row still lands at `level: module` with no `verificationId`, and each id is added by its first
trait-carrying task. Two grown constraints the plan does not mention and NR0.2 will meet: a `verificationId`
is now also refused on a `pytest` or `script` project (`:173-174`), and the legal boundary field set is nine
(`id, kind, paths, project, verificationId, guards, level, testFiles, selfSelect` — `:108`), so the plan's
six-field list is a legal subset rather than the whole set.

### Verified clean — no task changes

| Premise | Evidence at this head |
|---|---|
| No narrative code exists; the program is unstarted | `gk-core/src/FusionRpg.Core/Narrative/` absent; `gk-core/src/FusionRpg.Server/Narrative/` absent; `gk-data/packs/fusion/data/seed/narrative/` absent; `data/tuning/narrative*` absent; `scripts/narrative-readings.ps1` absent; `data/seed/dungeon/events/_known-defects.json` absent |
| The two server contracts are still to be written, so `/idea-ui` designs against real DTOs only later | `grep -rn DelveEventDto\|QuestLogDto -- src/` → no match |
| `EventPanel.tsx`'s placeholder comment is still stale (map *Conflicts* item 3, `storylet-card`'s) | `gk-web/web/fusion-rpg-web/src/stages/delve/layers/EventPanel.tsx:8-20` describes the six `EventView` fields as `Pending` because "No adapter exists", and renders three italic fallbacks |
| party-dungeon's still-open tasks sit in the files NR2.2 moves | transfer note `tasks/party-dungeon-todo.md:3-15`; **D3.3 `:1411`, D3.5 `:1607`, D3.9 `:1818` are all still `[ ]`** — B3's hand-off step is still required |
| NS2 (the narrative corpus boundary) is still open, so NR0.2's `core-narrative` row is that path's first owner | `tasks/narrative-seed-todo.md:61` `[ ]`; no `gk-data/packs/fusion/data/seed/narrative/**` pattern exists in the registry |
| The `notify-core-domain` / `notify-contracts` shape NR0.2 copies | `gk-core/scripts/verification-boundaries.v1.json:3913` and `:3935` |
| Task count and phase table | 94 tasks counted (`NR0` 2, `NR1` 6, `NR2` 32, `NR3` 16, `NR4` 9, `NR5` 17, `NR6` 7, `NRX` 3, + NR-LP1/NR-LP2) — matches the header |
| Map gate G7 | `docs/architecture/npc-story-events-map.md:312` |
| `web/**` still has no verification lane | `verify-change.ps1 -PlanOnly` on `gk-web/web/fusion-rpg-web/src/app/TitleScreen.tsx` → `VERIFICATION BOUNDARY MISSING` |

### Drift — citations only

| Cited as | At this head | Effect |
|---|---|---|
| `scripts/verify-change.ps1:118` (D2, todo) | `:114` | cosmetic; re-pointed |
| `guard-verification-boundaries.py:71-78` (no path-existence check) and `:82-92` (the `verificationId` trait rule) | the rules now live at `:114-126` (C8 exact-path, `:118` ambiguous pattern) and `:151-161` (trait rule), in a file that grew with schemaVersion 4/5 | **substantive** — see A1 |
| `party-dungeon-todo.md:8-14`, B5's `:14` for the "stays here" clauses | note spans `:3-15`; the resolver/256-seed clauses are on `:13` | cosmetic |
| `gk-core/data/tuning/expeditions.v1.json` and `gk-data/packs/fusion/data/seed/dungeon/**` "throw `VERIFICATION BOUNDARY MISSING`" | both **now resolve** — `tuning-expeditions` (module) and `seed-dungeon-corpus` (module) + `seed-dungeon-core-seam` + `seed-dungeon-data-seam` (TVB4.7 landed 2026-09-21, `tasks/test-verification-boundary-todo.md:212`) | favourable; **it is also why A1's duplicate-pattern failure exists** |

### Not re-measured here

NR2.32's template goldens, T13's faction-name goldens and the two live probes are each that task's own
first step. The `--write` precondition of `trees generate` belongs to ip-censor's T16.

### Verdict

The plan's structure, order and scope hold: the map's waves, the Delve-live-path-before-host rule, the
world-prerequisite rule, the PG1-PG3 gates and the party-dungeon hand-off are all still required and still
correct. **One HIGH premise is rotted and is named, not papered over: NR0.2's D2 rows fail the guard's C8
rule as written (A1), with a mechanical remedy inside NR0.2.** The owner is asked to confirm that remedy
rather than a plan reopen. **Status set to "approved 2026-09-22, ready for lanes"** — NR0.1 is unblocked,
and NR0.2 waits on A1's answer.
