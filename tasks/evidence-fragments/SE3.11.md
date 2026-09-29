# SE3.11 — Doc backlog: every remaining `docs/architecture/<program>/`

Same method as SE3.8–SE3.10. This batch covers every directory-scoped program not already closed by
SE3.9 (`world-stage/`, `world-map-runtime/`, `story-scene/`, `rift-gate/`) or SE3.10 (`item/`,
`seedsmith/`, `passive-tree/`) — 78 program directories, 949 documents.

## Scope measured before the edit

| Code | Total | HIGH |
|---|---|---|
| D1 | 805 | 76 |
| D2 | 22 | 22 |
| D3 | 110 | 109 |

## Scope measured after the edit

| Code | Total | HIGH |
|---|---|---|
| D1 | 727 | **0** |
| D2 | 0 | **0** |
| D3 | 1 | **0** |

**0 HIGH / 0 D3 / 0 D4** across all 78 directories. The one remaining D3 (LOW) and 727 remaining D1
are all forward-looking proposals or already-honest dead citations, none HIGH.

## Recurring patterns (this batch is where the whole repo's backlog concentrated)

The same handful of known cutovers, already established in SE3.7–SE3.10, account for the majority
of this batch's 207 required fixes — each closed with one `citations-historical` marker per
governing heading section, reused across every doc that cites it, never a guessed line:

- **`BattleStatComposer.cs`** (deleted 2026-09-13, 69ba6a7b3, battle-hub-fuse T6) + **`Combat/Guard/
  PoiseRuntime.cs`** (the losing side of the poise fork, superseded by `PoiseLedger.cs`) — 23 sites
  across 14 spec files (`actor-hub-and-combat-power-solid-fixing`, `aura-skill`, `base-defense`,
  `battle-tempo`, `class-system`, `party-dungeon`, `power`, `action`).
- **`CommanderId.cs`** (deleted, commander-identity SE4.2/SE4.3; `EmpireId`/`CommanderRef`/
  `ICommanderDirectory` are the successors) — 17 sites across 8 spec files.
- **`scripts/commit-tool/`** (deleted 2026-09-19, git gate retired) — 9 sites across 3 spec files,
  including two headings whose own text named the tool (a citation on a heading line can't take a
  `citations-historical` marker — the audit checks the heading line before the marker-scope logic
  runs — so those two were reworded in place instead of marked).
- **`PatronAuraOverlay.cs`** (deleted, patron aura atom-backed since 2026-09-06) — 4 sites.
- **The old `features/world/` page** (`WorldPage.tsx` and its components, deleted 2026-09-05 per
  `world-stage-map.md`'s own record) — 6 sites in one doc (`loam/spec-loam-fe-2.md`).
- **`Program.cs`** (29 sites, 20 docs) — qualified to `gk-core/src/FusionRpg.Server/Program.cs`; a same-line
  distinctive-token reanchor resolved 5 of the 29 precisely, the rest kept a bare path rather than a
  guessed line. One genuine tool bug found and fixed while doing this: two of the 29 sites were
  inside `spec-doc-citation-gate.md`'s own illustrative prose ("a bare `Program.cs` fails D3"), not
  real citations — the auto-reanchor script wrongly resolved one to a fabricated specific line
  (`:162`, a random unrelated match); both were caught and corrected to keep the illustration
  abstract instead of citing a real file.

## Repointed after verifying (representative — ~60 individual citations)

- **`RpgStore.CacheFieldAccess.cs`/`RpgStore.CargoTransfer.cs`/`RpgStore.LegionCargo.cs`** (18 sites,
  `empire-inventory-surfaces`, `world-action-economy`) — all three are partial-class `RpgStore` files
  cited by their short suffix; a spot-check (`IsCargoClaimReachableUnlocked` at the exact cited line)
  found zero drift, so the rest were bulk path-qualified on that confidence.
- **`AptitudeTuning.cs`** (8 sites total across SE3.10+SE3.11) — `gk-core/src/FusionRpg.Core/Stats/
  Aptitudes/AptitudeTuning.cs`; every cited line reanchored by content
  (`record AptitudeGrant` at :14 not :13, `retire-atk`'s `familyRead` skip at :200-214 not :241-262,
  the `SkillPointsPerThetaMilliByScope` doc comment at :43-58, `UniqueCreature`'s own tuning row at
  :229 not :204).
- **Seedsmith adapter files disambiguated by content, not by domain guess**: `distribution_planner/
  derive.py:747` (`refuse_full_run_if_ungated`, exact def-line match), `structures/planner.py:92`
  (the density formula, exact match) and `:146` (`check_plan`), `adapters/base.py:31-37`
  (`reference_fields`, the abstract interface attribute — a genuinely different file from the
  concrete `dungeon/__init__.py:40` that implements `legal_combinations` for the SAME doc's sibling
  citation, both confirmed by reading the actual logic), `pipeline/model.py` (`audit_schema` and its
  enum-is-allowed rule, four separate citations reanchored to :113-115/:121), `creatures/anchor/
  vote.py:19-23` (`VoteResult.confidence`, reused by every actions-domain adapter per
  `validate_heal/derive.py`'s own comment "reused from creatures.anchor.vote, never reimplemented"),
  `items/uniques/audit.py`/`items/uniques/briefs.py` vs `dungeon/audit.py` vs `creatures/anchor/
  audit.py` (three different `numeric_audit`/`MAGNITUDE_DENY_NAMES` implementations, disambiguated
  by the specific vocabulary each citing doc's own claim named — "source-locked"/rarity for uniques,
  "weightBand"/"manifestCost" for dungeon, "MAGNITUDE_DENY_NAMES" for creatures).
- **Renamed classes/interfaces found by searching for the described behavior, not the file name**:
  `IProgressionPowerProvider.cs` → `gk-core/src/FusionRpg.Core/Power/IPowerIndexProvider.cs` (the interface
  itself was renamed); `ConcreteSpeciesMapper.cs` → the class lives inside `ConcreteSpeciesSeedReader.cs`,
  never its own file; `IsRelicSpendableUnlocked.cs` → a private method inside
  `RpgStore.WonderBuild.cs`, same story; `LaneTypeDef.cs` → the `record LaneTypeDef` is declared
  inside `LaneTypeCatalog.cs`; `ResourcePoolState.cs:93-106` → the cited method (`Add`) is on a
  different class, `ActorResourcePools.cs`, at the exact same line number (93) — a genuinely wrong
  filename from the start, not drift; `zombie.hypno`'s Harmony postfix moved from
  `CreateZombieHooks.cs` (now 28 lines, no longer touches mind control) to
  `GameCaptureHooks.cs:296-301`, class `ZombieMindControl`.
- Small standalone fixes verified by exact content match: `command.json` (passive-tree nodes,
  1298 lines, cited line in range), `gk-web/web/fusion-rpg-web/package.json:12` (`"test": "vitest run"`,
  exact), `gk-data/packs/fusion/data/seed/items/_registry/themes.v1.json:11` (`elementAffinity`, exact),
  `gk-data/packs/fusion/data/seed/aptitudes/roster.json:19-22` (the `bastion` posture rows, exact),
  `CreaturesLayer.tsx:94` (the exact empty-state hint string).

## Genuinely gone, marked honestly rather than guessed

`DerivedStatsTab.tsx`, `LoamGauge.tsx`, `ChannelCacheSeamTests.cs`, `ConcreteSpeciesMapper.cs` (fixed
above; a plausible-but-unverified successor was named where one existed and the claim was not
independently re-verified), and the renamed `DemonSpeciesLegacyTraitPoolOverlap.Generated.cs` →
`CreatureSpeciesLegacyTraitPoolOverlap.Generated.cs` (the demon→creature rename convention) and
`DamageFxOverlay.cs`/`OverlayWorldFx.cs` (already documented in `CLAUDE.md` as a known, accepted VFX
migration state) were all corrected in place rather than silently repointed on a guess.

## Falsifier and guard evidence

| Check | Command | Result |
|---|---|---|
| Falsifier suite | `python -m pytest gk-forge/tools/seedsmith/tests/test_audit_doc_citations.py -q` | **23/23** |
| C# narrow falsifier + registry schema | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~DocCitationAuditTests\|FullyQualifiedName~EnforcementRegistryGuardTests"` | **23/23** |
| CI guard tier | `.\scripts\run-guards.ps1 -Tier ci` | **18/18, 0 red** |
| Repo-wide summary (all SE3.7–SE3.11 batches combined) | `python scripts/audit-doc-citations.py --summary` | D1 946 (3 HIGH), D2 6 (0 HIGH), D3 60 (4 HIGH), D4 0 — only SE3.12's own scope (D3 outside `docs/architecture/`) and a handful of stray HIGH findings remain repo-wide |

No `scripts/audit-doc-citations.py` change this batch (pure doc content, one auto-fixer-adjacent
bug caught and fixed by hand in `spec-doc-citation-gate.md`'s own prose, not the tool). No
`gk-core/data/tuning/**` touched; no golden affected.
