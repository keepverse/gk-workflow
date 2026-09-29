# SE3.9 — Doc backlog: `world-stage/`, `world-map-runtime/`, `story-scene/`, `rift-gate/`

Same method as SE3.8: never guess a citation target; repoint after opening and verifying, a
`citations-historical` marker for wholesale-replaced code, a prose correction where the claim is
now false, or leave a genuine forward-looking proposal (spec docs, no line cited) alone.

## Scope measured before the edit (module specs under each of the four directories)

| Program | D1 | D2 | D3 | Docs |
|---|---|---|---|---|
| world-stage | 26 (25 HIGH) | 1 (1 HIGH) | 1 (1 HIGH) | 15 |
| world-map-runtime | 19 (18 HIGH) | 0 | 0 | 3 |
| story-scene | 4 (4 HIGH) | 16 (16 HIGH) | 9 (9 HIGH) | 21 |
| rift-gate | 4 (0 HIGH) | 1 (1 HIGH) | 4 (4 HIGH) | 5 |
| **Total** | **53 (47 HIGH)** | **18 (18 HIGH)** | **14 (14 HIGH)** | 44 |

## Scope measured after the edit

| Program | D1 | D2 | D3 |
|---|---|---|---|
| world-stage | 1 (LOW: `componentSplit.ts`, forward-looking spec proposal, no line cited) | 0 | 0 |
| world-map-runtime | 0 | 0 | 0 |
| story-scene | 0 | 0 | 0 |
| rift-gate | 4 (LOW: `FlowerClickable.cs`/`MenuPresenceHook.cs` x2 each, forward-looking spec proposals) | 0 | 0 |

**0 HIGH / 0 D3 / 0 D4** across all four directories.

## The one dominant pattern: two shared components rewritten wholesale mid-program

Almost the entire batch (66 of 79 required fixes) traces to two known cutovers, each already
partly documented elsewhere in the repo, now marked consistently everywhere they're cited:

1. **`RiftPrologueDialog.tsx` went 203 → 39 lines at the S6 cutover** (17 D2 sites across 15 spec
   files under `story-scene/` and `rift-gate/`). It is now a thin wrapper; the beat/guard/
   acknowledgement/completion logic these specs cite by old line number lives in the shared
   `StorySceneHost.tsx`. One `citations-historical` marker per governing heading section, naming the
   successor.
2. **The old `features/world/` page was deleted 2026-09-05** when `world-shell`'s route flip landed
   (`world-stage-map.md`'s own words: *"the `worldTypes.ts` re-export shim and `features/world/`
   itself are both gone"*) — `WorldPage.tsx` (8 sites), `camera.ts`/`cameraGestures.ts` (12 sites,
   same file this session already found dead in `base-defense-ideal.md`, SE3.8), `LaneEdge.tsx`
   (3 sites), `SectorFog.test.tsx`/`SectorPanel.test.tsx`/`e2e/world.spec.ts` (5 sites, all from one
   `spec-world-wire.md:245` line), `WorldScene.tsx`/`WorldScene.test.tsx`/`render/WorldScene.tsx`
   (7 sites), `worldTypes.ts` (3 sites), `LoamGauge.tsx` (2 sites), `world.spec.ts` (3 sites) — 43
   D1 sites across 12 spec files. One `citations-historical` marker per governing heading section,
   naming the real successor location (`stages/world/`, `stages/world/render/`) without claiming a
   1:1 rewrite (the components were rebuilt under new names, not moved verbatim).

## Repointed after verifying (the rest)

- `Program.cs` (3 sites, `rift-gate/spec-overlay-hide.md`) — qualified to
  `gk-core/src/FusionRpg.Server/Program.cs`; `SendInjectorCommand` confirmed at the exact cited line 1617.
- `condition-console.json`/`derived-console.json` (7 sites, `story-scene/spec-recipe-wire.md` +
  `spec-story-scene-fold.md`) — both exist identically under `docs/design/gui-lego/recipes/` and
  `gk-web/web/fusion-rpg-web/src/ui/gui-lego/recipes/` (byte-identical `diff`); qualified to the
  `docs/design/` copy per this doc's own established canonical-source convention (matches SE3.8's
  `element-fire.json` disposition). All cited lines verified exact, zero drift.
- `types.ts:104-109` (`spec-recipe-wire.md`) — not `contract/types.ts` (unrelated content at that
  range); the real `$bindArray` type lives in `features/gui-lego/types.ts:127`, verified by content.
- `types.ts:266-267` (`world-stage/spec-world-contract.md`) — `SectorView` is real, but at
  `contract/types.ts:763` today, not 266-267 (drifted); reanchored by grepping the exact type name.
- `Dtos.cs:45` (`rift-gate/spec-first-open-signal.md`) — 3 files share this basename; `HealthDto.
  InjectorConnected` verified at `gk-core/src/FusionRpg.Contracts/Dtos.cs:46` (off by one, corrected).
- `SectorNode.tsx:104` (`world-stage/spec-world-render.md`) — the `"◆".repeat(n)` danger-diamond
  pattern this D2 finding named is not in the file at all (97 lines total); marked as gone rather
  than guessing a replacement line, since whether it was fixed or just moved wasn't checked here.
- `riftAssets.ts` (3 sites, `story-scene/spec-actor-cast.md`) — genuinely gone; `features/onboarding/`
  today holds only `RiftPrologueDialog.tsx`/`.test.tsx` and two PNGs, no manifest file or
  `RIFT_ASSET_VERSION` anywhere in `web/`.
- `storyContract.ts` (2 sites, `story-scene/spec-story-scene-host.md` + `-map.md` from SE3.8) —
  confirmed not to exist under that name anywhere; the closest live candidates
  (`contract/types.ts`, `sceneTrigger.ts`) were named but not verified as the same claim.

## Falsifier and guard evidence

| Check | Command | Result |
|---|---|---|
| Falsifier suite | `python -m pytest gk-forge/tools/seedsmith/tests/test_audit_doc_citations.py -q` | **23/23** |
| C# narrow falsifier + registry schema | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~DocCitationAuditTests\|FullyQualifiedName~EnforcementRegistryGuardTests"` | **23/23** |
| CI guard tier | `.\scripts\run-guards.ps1 -Tier ci` | **18/18, 0 red** |

No `scripts/audit-doc-citations.py` change in this task — pure doc-content fixes, no tool
precision bugs found this batch (unlike SE3.7/SE3.8). No `gk-core/data/tuning/**` touched; no golden
affected.
