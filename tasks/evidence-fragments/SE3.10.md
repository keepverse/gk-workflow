# SE3.10 — Doc backlog: `item/`, `seedsmith/`, `passive-tree/`

Same method as SE3.8/SE3.9.

## Scope measured before the edit

| Program | D1 | D2 | D3 | Docs |
|---|---|---|---|---|
| item | 23 (15 HIGH) | 1 (1 HIGH) | 7 (7 HIGH) | 70 |
| seedsmith | 25 (20 HIGH) | 0 | 0 | 28 |
| passive-tree | 14 (2 HIGH) | 0 | 14 (14 HIGH) | 14 |
| **Total** | **62 (37 HIGH)** | **1 (1 HIGH)** | **21 (21 HIGH)** | 112 |

## Scope measured after the edit

| Program | D1 | D2 | D3 |
|---|---|---|---|
| item | 8 (0 HIGH) | 0 | 0 |
| seedsmith | 5 (0 HIGH) | 0 | 0 |
| passive-tree | 12 (0 HIGH) | 0 | 0 |

**0 HIGH / 0 D3 / 0 D4** across all three directories. The 25 remaining D1 are LOW: real
forward-looking proposals (spec files naming a tuning file or CLI arg not yet built, no line cited)
— e.g. `i18n_translate.py`/`motif_translate.py` in `spec-pipeline.md`.

## The dominant pattern: `tools/seed_graph/*` and a never-built `seedsmith.py` script

19 of the 59 required fixes trace to one fact, already recorded in `.github/workflows/ci.yml`'s own
comments but not propagated to the docs that predate it: **`tasks/seedsmith-todo.md` S10
(2026-08-23) cut CI over from `tools/seed_graph/*` to the real `gk-forge/tools/seedsmith` package** — "the
seven Linkage/Registration metrics ported from `seed_graph` were promoted to `gates=True`
(`seedsmith/metrics/linkage.py`)". `docs/architecture/seedsmith/review/audit-buildability.md`,
`audit-grounding.md`, `audit-gaps.md`, `spec-foundation.md`, and `item/enrichment-plan.md` all
predate this cutover and cite `seedsmith.py` (a top-level CLI script that was never built — the
shipped invocation is `python -m seedsmith`) and `tools/seed_graph/{corpus,checks,
test_reachability,check_reachability}.py` (absorbed, not left in place). One `citations-historical`
marker per governing heading section, naming the real cutover and successor. One heading whose own
TEXT cited `seedsmith.py` (`### N3`) couldn't take a marker (the CITATION regex fires on the heading
line itself, before the marker-scope logic runs) — reworded in place instead: *"the unbuilt
`seedsmith.py`"*.

## Repointed after verifying (representative)

- `AptitudeTuning.cs` (6 sites, `passive-tree/spec-species-tree.md`, `-tree-plan.md`,
  `-tree-state.md`) — `gk-core/src/FusionRpg.Core/Stats/Aptitudes/AptitudeTuning.cs`; three separate drifted
  line numbers reanchored by content (`record AptitudeGrant` at :14 not :13,
  `SkillPointsPerThetaMilli` parse at :179 not :158, the UniqueCreature tuning row at :229 not :204).
- `schemas.py`/`gates.py`/`model.py`/`provenance.py`/`cli.py` (5 sites, `passive-tree/
  spec-tree-language.md` + `item/spec-set-charm-gen.md`) — every one is a seedsmith **core pipeline**
  file the tree-content generator shares with every other adapter
  (`pipeline/model.py`, `pipeline/provenance.py`, `report/cli.py`,
  `adapters/actions/validate_heal/{gates,schemas}.py`), not a tree-specific module; disambiguated by
  grepping the exact quoted function/phrase in each candidate (`audit_schema`'s enum-is-allowed
  paragraph at `pipeline/model.py:121`, `run_g2` at `validate_heal/gates.py:114` — exact match,
  `should_generate` at `pipeline/provenance.py:77` — exact match, the tree-generate dry-run "someone
  eventually forgets" sentence at `report/cli.py:1688-1691` — exact match, reused verbatim by two
  different passive-tree specs).
- `verdict.py:83-96` (`passive-tree/spec-tree-review.md`) — `setgen/verdict.py`, "a held partition
  alone is enough to deny a pass" verified at its real lines 86-88 (kept the doc's own range,
  approximately right).
- `RosterPage.tsx` (6 sites, 4 `item/` SSOT docs) — genuinely gone; `EQUIP_SLOTS` not found under
  any name in `web/`. Whether it was renamed, folded into another component, or removed outright was
  not investigated — `citations-historical` markers record only that the citation is dead.
- `Fusion.cs` (4 sites, `item/ssot-materials-crafting.md`) — `gk-core/src/FusionRpg.Data/Sqlite/
  RpgStore.Fusion.cs` (a partial-class file cited by its short name, same pattern as
  `WorldTemplateCatalog.TwoHearths.cs` in SE3.8); all four claims verified by content
  (`IsKnown`, the `qty >= $q` conditional update, the fusion-log dedupe-collision throw) and
  reanchored to their real lines.
- `registries.py` (3 sites, `item/spec-slot-roles.md` + `spec-threshold-grants.md`) —
  `adapters/items/registries.py`; `HYBRID_FRAME_CITATION` verified at its real line 155, not the
  cited 105/111.
- `BindGate.cs` (2 sites, one flagged D2 one already in-range but wrong content) —
  `gk-core/src/FusionRpg.Core/Effects/Atoms/BindGate.cs`; the "Sector/Slot world-host check" is really at
  line 49 (the originally-cited :188-190 was in range but the wrong content — caught while verifying
  the flagged neighbor, corrected too rather than left silently wrong beside a freshly-fixed line);
  the `defense`-at-`match`-scope rejection is at :158-166, not the cited :239-252 (past EOF, file is
  209 lines).
- `Program.cs` (2 sites, `item/spec-action-wiring-closure.md` + `spec-armoury.md`) — qualified to
  `gk-core/src/FusionRpg.Server/Program.cs`; `ActionCorpusImporter.Import` verified at :543-545. The armoury
  keyset-pagination claim (`:369`, "returns `{items, nextAfterId}`") could not be verified —
  `nextAfterId` is not found anywhere in `Program.cs` or the co-cited `RpgStore.Progression.cs` —
  but the citation was already structurally in-range (not a required fix); qualified the path only,
  left the line and the unverified semantic claim as found.
- `kinds.py:104` (`item/spec-strain-splice-gen.md`) — `adapters/items/kinds.py`; the `KINDS` tuple
  starts at line 48, not 104.

## Two hypothetical/proposed citations marked explicitly (not repointed, never built)

`axes.v1.json` (`item/entry-shapes.md`, "Recommend a small `axes.v1.json`") and `zh.json`
(`item/ssot-presentation.md`, "if a second language ships, it becomes `en.json` + `zh.json`") are
both genuine proposals in non-spec SSOT docs (so EXEMPT 6's forward-looking rule doesn't apply
automatically) — marked `(new, hypothetical)` inline.

## Falsifier and guard evidence

| Check | Command | Result |
|---|---|---|
| Falsifier suite | `python -m pytest gk-forge/tools/seedsmith/tests/test_audit_doc_citations.py -q` | **23/23** |
| C# narrow falsifier + registry schema | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~DocCitationAuditTests\|FullyQualifiedName~EnforcementRegistryGuardTests"` | **23/23** |
| CI guard tier | `.\scripts\run-guards.ps1 -Tier ci` | **18/18, 0 red** |

No `scripts/audit-doc-citations.py` change this batch (pure doc content). No `gk-core/data/tuning/**`
touched; no golden affected.
