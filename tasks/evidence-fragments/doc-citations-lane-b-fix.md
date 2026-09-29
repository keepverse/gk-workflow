# doc-citations gate — lane B's own findings closed

Ran `python scripts/audit-doc-citations.py --strict` after merging `features/mega-merge` per the
coordinator's instruction, to get the full list rather than work from a partial recollection.

## Before

13 HIGH findings total. Traced each to the git commit that shrank/deleted the cited file, not
assumed:

| File cited | Commits that shrank/deleted it | Program |
|---|---|---|
| `SpeciesPassiveAtomSource.cs` (4 docs) | `a74aaa2c` "SP3.6 — retire SpeciesPassiveAtomSource" | species-progression (mine) |
| `RpgStore.Species.cs` (1 doc) | `13ef61c8` "SP3.3 — move the synthetic stat.derived atom builder into Core" | species-progression (mine) |
| `RpgStore.PlayerSpecies.cs` (1 doc) | `80559a75` "SP0.6 — player_species has no reader or writer left" | species-progression (mine) |
| `RpgStore.ZombossDeploy.cs` (2 docs) | `101bcad7`/`5e1fbdd8` "SE4.12"/"SE4.22 save-identity" | solid-enforcement (mine — lane B's own SE wave 4) |
| `CombinationEvaluator.cs` (5 docs) | not investigated — outside `gk-core/src/FusionRpg.Data`/species-progression entirely | species-gear-chain / strain-splice-host (**lane C**, confirmed still actively changing per this session's own `tasks/evidence-fragments/CC6.md`) |

**8 of 13 findings trace to lane B's own commits** (species-progression + solid-enforcement, both
this lane's mandate per the master plan's own lane diagram) — more than the 4 first estimated, found
by running the full `--strict` list as instructed rather than stopping at the first few.

## Fixed (8/8, all lane B's own)

Every fix either re-anchors the citation to the code's real current location, or marks it gone on the
SAME PHYSICAL LINE the audit reads (Markdown soft-wrap meant several "gone" explanations already
existed one line below the citation, which the exemption regex does not credit — moving the word
onto the citing line itself, never deleting the line number, per the instruction):

| Doc | Fix |
|---|---|
| `actor-hub-ssot.md:821` | added "retired by SP3.6 — the file is gone; its work moved into `SpeciesLayerProjector.cs`" on the citing line |
| `solid-remediation/spec-species-carrier.md:157` | added "(gone —" on the citing line (the "is deleted" explanation was one line below) |
| `solid-remediation/spec-species-carrier.md:94` | re-anchored `RpgStore.Species.cs:460` → `:436` (real current line of the same code, `head with { Magnitudes = magnitudes }`) |
| `species-progression-map.md:150` | added "(retired by SP3.6 — file gone, superseded by `SpeciesLayerProjector`)" to the C3 table cell |
| `species-progression/spec-species-layer-projector.md:25` | added ", gone — retired by SP3.6" on the citing line |
| `species-progression-ideal.md:200` | added ", retired by SP0.4/SP0.6 — the method is gone" on the citing line |
| `npc-story-events/spec-character-registry.md:63` | re-anchored `RpgStore.ZombossDeploy.cs:57` → `:41` (real current line of `Origin = "zomboss"`) |
| `solid-enforcement/spec-save-identity.md:361` | re-anchored `RpgStore.ZombossDeploy.cs:57` → `:41`, same fix |

## After

```
python scripts/audit-doc-citations.py --strict
```
0 HIGH findings in any doc this lane touched (verified: none of the 8 above appear in the re-run).
**5 HIGH findings remain, all `CombinationEvaluator.cs`**, cited from `species-gear-chain/spec-gem-tier.md`,
`strain-splice-host-ideal.md` (×2), `strain-splice-host-map.md`, `strain-splice-host/spec-host-gate.md`
— confirmed these are `species-gear-chain`/`strain-splice-host`'s own files (lane C), not touched by
any lane B commit, and per this session's own `tasks/evidence-fragments/CC6.md`, that program is
**actively in progress** right now (its own closing checkpoints are unticked). Fixing another lane's
active citations without being asked risks colliding with work already underway there.

**`--strict` exit code is 1, not 0** — honestly reported rather than claimed otherwise: the remaining
5 findings are lane C's, not lane B's. If the coordinator wants a global exit 0 before merging, that
needs routing to whichever session owns `species-gear-chain`/`strain-splice-host` (the same relationship
already established for CC6's own `combo-budget` gap).

## Reviewed-vocabulary / closed-form note

No population-count or generated-text assertion is added by this fix.
