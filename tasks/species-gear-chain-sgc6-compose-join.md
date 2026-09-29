# 48 of the 181 committed action briefs cannot compose at boot — and the importer's result is discarded

⚠ Location note: the brief says fragments live under `tasks/evidence-fragments/`, outside this lane's
allowed paths (`tasks/species-gear-chain-*`); this file is named to stay inside the fence.

Found while measuring the atom-family namespaces for SGC5-F2; filed as **SGC5-F6**.

⚠ **The PHENOMENON is already documented and already ruled — this filing's value is the program-wide
figure, not the discovery.**

**Two independent records, and the DESIGN-GATE read that found the second.** The test docstring above is
the first. The second is the sealed spec `docs/architecture/action/spec-action-seeding.md:8-20`, whose
owner quote (2026-08-27) is: *"seedsmith is a tool for developing the game, not the running game … **Seedsmith
measures a corpus this module produces — it cannot gate the feature that produces it, and it does not run
in the game**"*. So the committed corpus is a dev-tool artefact and its completeness is not a gate on A13.
That spec was read IN FULL this session as part of DESIGN-GATE §1 row 45; `action-corpus-ideal.md` was
read in its §21 section (which is where the E9-has-no-family-concept citation below comes from);
`action-ideal.md`, `action-map.md` and §1 row 42's atom docs were **not** read in full — stated as a gap,
not ticked.

The gate read also caught a conflation in this fragment's own wording: the generator's refusal reasons
(`no referenceBaseGameUnits`, `no opWeightPermille`, bare status templates, missing E30 pools) are the
**generator's expansion gates**, a different layer from **E9's atom pricing** — which per
`action-corpus-ideal.md:694` "has no concept of a family" (its key is `(kindId, channel)` and it can only
price a concrete `AtomRow`). Calling both "priceability" would send a reader after the wrong table. `gk-core/tests/FusionRpg.Data.Tests/Actions/ActionCorpusRealContentQualityTests.cs:18-26`
records it, dated 2026-09-06: "only 2 of the 30 unique `atomFamilies` the real corpus names … exist
anywhere under `gk-data/packs/fusion/data/seed/atoms/` … Exactly 3 of 24 briefs … import; the other 21 correctly refuse,
naming why. This is a real content-authoring gap in a sibling pipeline (the atom/family generator),
**not a defect in A21's own import machinery — fixing it is out of this module's scope**." The first
form of this fragment read as a fresh discovery; that was wrong and is corrected here.

| Criterion | Command / read | Result |
|---|---|---|
| what the composer requires | `gk-core/src/FusionRpg.Core/Actions/Corpus/ActionCorpusComposer.cs:83-89` | `foreach (var family in brief.AtomFamilies) foreach (var atom in atomsInFamily(family)) …` then `if (candidates.Count == 0) throw new ActionCorpusComposeRejection("… none of its atomFamilies (…) resolved any atom")` — one resolvable family is enough; ZERO is a hard rejection |
| what `atomsInFamily` resolves against | `ActionCorpusImporter.cs:107` | `store.ListAtomsByFamily` — the store's atom rows, populated by `SeedImportRunner` sweeping `SeedScanner.AtomFolders` |
| the complete set of families with atom rows | scan of every swept folder for entries carrying a `family` field | `atoms` 18 files → **105 families** (7 hand-authored → 31; 11 `generated/family-expand.*` → 74). `containers`, `curves`, `rarity`, `elements`, `channel-policy`, `channel-pools`, `effects/affixes`, `power`, `creatures/species-effects` → **zero families each**. So 105 is the whole set, and 61 of the 125 item affix families are in it |
| the consequence, measured | scan of the 4 `committed-round-*.json` + `authored-basics.json` | of **181** rows, **48 name ONLY families with no atom row** (hard rejection) and 133 have at least one resolvable family. Most-named unresolvable families: `atom.elpw-surge` 11 rows, `atom.sust-husk` 6, then `atom.volley`, `atom.elpw-overflow`, `atom.searing-strike`, `atom.retribution`, `atom.deathblast` 4 each |
| why it is invisible | `gk-core/src/FusionRpg.Server/Program.cs:765` | `ActionCorpusImporter.Import(store, actionBriefs, actionCostTemplate, RungPolicy.Table);` — the returned `ImportResult` is **discarded**. `ImportedCount`/`RejectedCount`/`BriefOutcome.Rejection` are computed (`ActionCorpusImporter.cs:80-87`) and never printed, so 27% of the corpus can fail to import with nothing in the boot log saying so |
| and it thins the catalog | `ActionCorpusImporter.cs`'s rejection branch | a brief that composed before and refuses now upserts the stored action **DISABLED**, never deletes it — so the visible catalog shrinks while grants may still reference the id |
| the generator is NOT the defect | `dotnet run --project gk-forge/tools/FamilyExpandGen -- --check` | **`--check: clean, 11 generated file(s) match`**, EXIT 0 — and its header reads **"125 families read, 150 row(s) emitted across 8 family file(s), 95 family(ies) refused:"**, each refusal named |
| why 95 families cannot be expanded | classification of the generator's own refusal lines | **69** `no referenceBaseGameUnits` (the family's channel/kind cannot be priced — no game-units reference), **21** `no opWeightPermille entry for op 'Replace'/'Flag'`, **3** bare status family template ("the concrete segment must be authored (`status.<family>.<category>`)"), **4** `no matching E30 channel pool` |
| the lever, corrected | read | the **priceability rules and tables** (`bands.v1.json`'s `familiesOutOfFourWaySplit`, the op weights, the status-category authoring) — NOT `FamilyExpandGen`'s scope, which T12 already widened and which is green. ⚠ The first form of this row named the 6 unexpanded partitions as the lever; that would have sent the owner after the generator |

**Verify (the join, not a count):** every committed brief's `atomFamilies` must intersect the set of
families with atom rows, and the boot must report the importer's rejected ids. Today **48 of 181 fail
the join** and the call site prints nothing.

**Owner, found by finishing the DESIGN-GATE read: effect-atom module E43**
(`docs/architecture/effect-atom/spec-family-expand.md`). Its §2 table already reads:
`SeedScanner.OwnedFolders` | **does not include `items`** | `SeedScanner.cs:14-15` — so the importer
never sees them; **The expansion rule | ⛔ real gap — no file, no generator, no test**. The catalog
side agrees twice over: `atom-catalog-ssot.md` §0 ("**The vocabulary is closed and built. The POOL is
empty.** … **So the pool file exists and is read. What it lacks is rows.** The step that would fill it
— emitting the family library from the registry, deterministically — is **model-free and unbuilt**")
and `atom-family-library.md` §2's stage table (`families → atoms` | owner **effect-atom `E30`** |
Shipped? **no**). So the 95 refusals are **E43's remaining work** and `gk-forge/tools/FamilyExpandGen` is its
partial implementation (11 partitions of 16) — not a mis-scoped tool and not a table to edit.

The action program owns the other half: `gk-data/packs/fusion/data/seed/actions/**` consumes the atom corpus, and
`gk-core/src/FusionRpg.Server/Program.cs:765` discards the importer's `ImportResult` (outside this fence).
Filed rather than fixed.

**DESIGN-GATE §1 read, this session:** `action/spec-action-seeding.md` in full; `action-corpus-ideal.md`
§21, `effect-atom/atom-catalog-ssot.md` §0–§3, `effect-atom/atom-family-library.md` §1–§2,
`effect-atom/spec-family-expand.md` §1–§3.1, `action-ideal.md` §0–§1, `action-map.md` §4–§4.3 and
`effect-atom/definitions.md` §0–§2 in section. The remainder of those last three is still unread —
stated as a gap, not ticked.

**What the read adds (it contradicts nothing here).** (a) The corpus is seedsmith's by SEALED decision:
`action-ideal.md` §0.1 decisions **4** and **17**; `action-map.md` §4.1 labels A13 `action-seeding`
"the **runtime generator** … **Not seedsmith**", and §4.3's Phase 0 extends the atom effect layer
before any action module builds. (b) E43's work is grammar-free: `definitions.md` §1 pins `atom_id` as
**derived, not authored** — `{family_id}[.{variant}].t{tier}` — over `UNIQUE (family_id, tier, variant)`
(`variant` `''` for single-member families, the element for generated ones), and `spec-family-expand.md`
§2 lists `AtomRow.DeriveId` and that constraint as already built. So the 95 refused families need no new
vocabulary, no new table and no new id rule — only rows.
