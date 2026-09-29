# SE3.8 — Doc backlog: `docs/architecture/*.md` root

Method per the owner's standing instruction: bulk deterministic first
(`gk-core/scripts/fix-doc-citations.py`, already run in a prior commit), then hand-fix the residue this
tool cannot resolve — never guess a citation target; an unresolvable one gets the spec's own
disposition (repoint after verifying, `citations-historical` marker, prose correction, or `(new)`),
never an invented path.

## Scope measured before the edit

`docs/architecture/*.md` root files only (2 path segments: `docs/architecture/<name>.md`), excluding
every `docs/architecture/<program>/` subdirectory (SE3.9–3.11's job).

| Code | Total | HIGH |
|---|---|---|
| D1 | 113 | 56 |
| D2 | 14 | 14 |
| D3 | 62 | 60 |
| D4 | 12 (post SE3.7 hedge-regex fixes, see below) | 12 |

## Scope measured after the edit

| Code | Total | HIGH |
|---|---|---|
| D1 | 56 | **0** |
| D2 | 0 | **0** |
| D3 | 0 | **0** |
| D4 | 0 | **0** |

`0 HIGH / 0 D3 / 0 D4` — meets SE3.8's acceptance. The 56 remaining D1 are LOW: genuinely
forward-looking proposals in ideal/audit docs (a `gk-core/data/tuning/*.v1.json` file a not-yet-built
program names for later, correctly marked `(new)`/`hypothetical`/`rejected`) or citations already
honest about the file being gone — never a claim that something exists when it doesn't.

## Two tool precision bugs found and fixed while measuring this batch (not merely worked around)

1. **D4's shipped-status regex was a bare substring match.** `MAP_STATUS_SHIPPED_RE` fired on "No
   build **AUTHORIZED**", "once this map is **APPROVED**", "Plan (when **approved**)", and (via an
   unbounded `complete`) on "cache triggers **completed**"/"…**completeness** is in scope" — i.e. it
   flagged 8 of the original 20 D4 hits as false positives. Fixed across two follow-up commits:
   `map_positively_claims_shipped()` rejects a match hedged by `no/not/never/once/until/pending/
   after/when/if` within ~40 chars, and `complete` is now word-bounded
   (`\bcomplete\b`, never `completed`/`completing`/`incomplete`). D4: 20 → 11 genuine, each
   hand-verified by reading the real map text. All 11 got a `Status line vs. what shipped` banner in
   this same batch (the 12th, `strain-splice-host`, dropped out as a genuine non-finding — its map
   agrees with its ideal that nothing is built).
2. **`PRIOR_ART_HEADING`'s `sources?` term was far too broad**, matching engineering headings that
   use "source" in its ordinary sense ("D2's fourth acquisition **source** has no carrier", "the
   `CreatureType` budget **source** inverts a locked ordering") and silently demoting two genuinely
   ambiguous `AptitudeTuning.cs` D3 citations to LOW. A repo-wide grep found 15+ such false-positive
   headings and zero real prior-art headings that need `sources?` specifically (every real one
   already also says "prior art"/"genre"/"research"). Removed `sources?` from the pattern; re-ran the
   full falsifier suite clean.

## Every CORRECTED (not merely repointed) claim in this batch

- `tier-system-ideal.md`: the `materialgen/vocab.py`/`droptablegen/tuning.py` "broken cite" bullet
  had already drifted TWICE (its own "corrected" line numbers were themselves stale against the
  live, actively-generated file) — rewritten to cite by path only, no line number, with a note that
  this generator is under active edit. The `len(ISSUABLE) == 27` "foreseeable guard breakage" this
  doc warned about is **already fixed** (now `_EXPECTED_ISSUABLE_COUNT`, a computed reconciliation)
  — noted inline. The `CreaturesPage.tsx`/`rosterSplit.ts` rarity-sort defect is **fixed** (both now
  import from the shared `rarityLadder.ts`, ladder-consistency-repair/species-gear-chain T17);
  `patronView.ts` is **not** fixed (still keys the retired four-value vocabulary) — both facts
  verified by reading the current code, not assumed from the old finding.
- `battle-tempo-map.md` D9: the "two independent poise stacks" fork this row named is **gone** —
  `Combat/Guard/PoiseRuntime.cs` was deleted; only `PoiseLedger.cs` remains. D8 (which cited the now-
  deleted `PoiseRuntime.Riposte`) is flagged as possibly-stale rather than silently left contradicting
  D9 — whether Riposte moved, was reimplemented, or was lost was explicitly **not** investigated in
  this pass (out of scope for a citation-gate batch) and is named as needing its own check.
- `passive-tree-ideal.md`: the "841st species, `zombie/_needs-review.json`" duplicate finding is
  **stale** — that quarantine file doesn't exist and a direct grep finds exactly one `SnorkleZombie`
  row today, not two; the duplicate was resolved separately from this doc.
- `debug-mcp-ideal.md`: `scripts/commit-tool/mcp_server.py` was deleted 2026-09-19 (git gate
  retirement) — the row is corrected to say so while keeping the precedent it was making (a stdio MCP
  server is a proven shape here).
- `game-gui-principles.md`: `features/world/LaneEdge.tsx` no longer exists under that path; the world
  render layer moved to `stages/world/render/` — a grep of the plausible successor (`Lane.tsx`) finds
  none of the three hardcoded hex literals this row named, but that was not independently verified as
  proof of a fix, only that the old citation is dead.
- `base-defense-ideal.md`: `stages/world/camera.ts` and `stages/world/cameraGestures.ts` (the latter
  already flagged in its own row as dead code with zero importers) are both gone under those names;
  a plausible-but-unverified successor (`game/world/systems/worldCameraMath.ts`/`worldCameraSystem.ts`)
  is named for `camera.ts`, and `cameraGestures.ts`'s `wheelZoom` export is not found anywhere in
  `web/` — most likely removed as the dead code the row itself already said it was.
- `lawn-tuning-profile-ideal.md`: the "second full `aptitudes-lawn.v1.json`" citation in the Rejected
  table was a hypothetical never actually created — marked so explicitly.

## Repointed after verifying (representative, not exhaustive — ~90 individual citations across 66 files)

Every repoint below was checked by opening the target file and reading the cited content, per the
spec's fix-preference order; several caught real drift (a "corrected" line number that had drifted
again) and were re-anchored to the true current line rather than the doc's own stale correction:

- `CommanderId.cs` (9 sites, 5 docs), `BattleStatComposer.cs`/`PlaceholderBattleResolver.cs` (13
  sites, 9 docs), `PatronAuraOverlay.cs` (4 sites, 2 docs), `RiftMenuOverlay(Layout)?.cs` + its
  deleted test (6 sites, 2 docs), `RiftPrologueDialog.tsx` (2 sites, 2 docs) — all `citations-
  historical` markers, one per governing heading section, naming the real successor
  (`BattleHubCompose.cs`, `ICommanderDirectory`, `StorySceneHost.tsx`, atom-backed patron aura).
- `Program.cs` (21 sites, 14 docs) — qualified to `gk-core/src/FusionRpg.Server/Program.cs` (the only
  `Program.cs` shaped like an ASP.NET startup wiring dozens of `*Policy.Configure` calls; every
  other `Program.cs` in the repo is a small CLI tool entry point) and reanchored via a same-doc
  distinctive-token search; 8 of the 21 had no safe reanchor token and kept a bare path instead of a
  guessed line.
- Seedsmith adapter files disambiguated by reading real content against the citing claim: `combogen`
  (`emit.py`/`tuning.py`/`schema.py`, strain-splice-host, 9 sites), `dungeon` (`schema.py`/
  `pipelines.py`/`briefs.py`, narrative-seed, 6 sites), `creatures/anchor` (`schema.py`, 7 sites),
  plus singles: `structures/planner.py`, `effects/affix/prompts.py`, `creatures/anchor/derive.py`,
  `items/kinds.py`, `items/basetypegen/brief.py`, `items/droptablegen/schema.py`,
  `report/cli.py` (line drifted 1156→1816, re-anchored by grepping the exact quoted comment).
- C#/data singles: `CapPolicy.cs` (3 sites, disambiguated `Actions/Grants` vs `Match` by content),
  `AptitudeTuning.cs` (3 sites, `Core/Stats/Aptitudes` vs `gk-core/tools/CombatSim`), `TwoHearths.cs` →
  `WorldTemplateCatalog.TwoHearths.cs`, `Core.Tests.csproj` → its real
  `gk-core/tests/FusionRpg.Core.Tests/FusionRpg.Core.Tests.csproj` name, `gk-core/data/tuning/power-scale.v2.json`
  (was bare `v2.json`), `gk-data/packs/fusion/data/seed/items/_registry/bands.v1.json` (2 sites, line drift 59→59/78→81
  verified), `gk-web/web/fusion-rpg-web/src/contract/types.ts` (`SlotView`, line drift 871→886).
- `action-playability-ideal.md`: `committed-round-909/2000.json` / `committed-round-1/2.json` were a
  wrong slash-separated naming pattern; the real files are `data/seed/actions/committed-round-{N}.json`
  (dash-separated, one file per number).
- `element-fire.json` (achievement-title-ui-ideal.md) qualified to the doc's own stated canonical
  source, `docs/design/gui-lego/themes/packs/` (the web copy is described as a mirror of it).
- `weapon.json` (base-defense-ideal.md): not a repo citation at all — a third-party
  `cohstats/coh3-data` GitHub file; de-backtick'd so it no longer parses as a path citation.
- `launcher.json` (game-versioning.md), `storyContract.ts` (story-scene-map.md): both are genuine,
  correctly-named references to something that is not a tracked repo file — a per-machine runtime
  settings file, and (for storyContract) a name with no current file at all, with the closest live
  candidates named but not verified as the same claim.

## Falsifier and guard evidence

| Check | Command | Result |
|---|---|---|
| Falsifier suite | `python -m pytest gk-forge/tools/seedsmith/tests/test_audit_doc_citations.py -q` | **23/23**, twice in a row (once after each tool fix) |
| C# narrow falsifier (EXEMPT 1) + registry schema | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~DocCitationAuditTests\|FullyQualifiedName~EnforcementRegistryGuardTests"` | **23/23** |
| SE3.8 scope, quoted after the edit | `python scripts/audit-doc-citations.py --scope docs/architecture/` (filtered to 2-segment docs) | D1 56 (0 HIGH), D2 0, D3 0, D4 0 |
| Repo-wide summary | `python scripts/audit-doc-citations.py --summary` | D1 1109 (163 HIGH), D2 47 (41 HIGH), D3 204 (148 HIGH), D4 0 — all outside this batch's scope, SE3.9–3.12's job |
| CI guard tier unaffected | `.\scripts\run-guards.ps1 -Tier ci` | **18/18, 0 red** — `doc-citations` correctly absent (still `backlog`, gates at SE3.13) |
| `guard-doc-citations.ps1` (repo-wide, non-gating) | `.\scripts\guard-doc-citations.ps1` | exit 1 as expected — reports the real remaining backlog outside this batch, not a regression |

No `gk-core/data/tuning/**` file touched; no golden test affected (docs-only + one Python tool file).
