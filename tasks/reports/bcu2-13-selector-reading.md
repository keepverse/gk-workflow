# BCU2.13 — the `elementSecondary` selector and `doublecherry attackTempo`, read model-free

Lane `cmdc/bcu8-4`, head `9541f1f2c`. Owner of the row: `tasks/combat-unification-todo.md` F2b +
`tasks/species-build-todo.md` (the `attackTempo` half), via register BCU2.13. The row is a manager-run
model job (board: launched, "108 species"; `2004b5a42`) whose outputs are `gk-data/packs/fusion/data/seed/creatures/**` —
outside this lane's fence. This is the reading those outputs will move, recorded with no model calls:

```
python tasks/reports/bcu2-13-selector-reading.py --out tasks/reports/bcu2-13-selector-reading.json
```

## The selector

Definition, the manager's own (`2004b5a42`): species whose `elementSecondary` is `none` **and** that no
fusion recipe names as an output. Read at this head:

| reading | value |
|---|---:|
| species in `_index.json` | 904 |
| fusion recipes (`gk-data/packs/fusion/data/generated/creatures/_fusion-recipes.json`) | 759 |
| species with `elementSecondary: none` | **450** |
| **A** — none **and not a recipe output** (the stated rule) | **138** |
| B — also not a recipe *input* | **108** |
| C — A restricted to `pure` species | 126 |
| register's 2026-09-07 reading | 127 |
| board's 2026-09-23 reading | 108 |

**Two id-space traps, both real, both reproducible.** (1) `_index.json` keys are CamelCase
(`AcientSunNut`) while the recipes name outputs in lower case (`acientsunnut`); comparing them raw made
every `none` species look unnamed, which is the wrong attempt `2004b5a42` describes and rejects. (2)
**The one this lane fell into and then fixed:** the anchors live in FAMILY files holding many rows
(`zombie/undead.json` holds 63) and `_index.json` maps a species to its family, *not* to a row — so
`rows[0]` reads the family's base species for every key that is not first, which was **355 of the 904**
keys. Both scripts now resolve by exact `speciesId` (every key matches exactly; no file repeats one) and
*refuse* rather than read a neighbour's anchor. The counts on this page are the corrected ones; the
numbers this lane first published (487 `none` / 122 / 96 / 111) were the `rows[0]` reading and are
superseded.

**This also reconciles the board's figure.** With rows resolved correctly, variant **B = 108**, exactly
`2004b5a42`'s reading — so the board's 108 is reproducible under the *also-excluding-recipe-inputs*
rule, while the rule as literally written in that commit (which names only outputs) reads 138. The
definition, not the arithmetic, is what differs.

The JSON carries the **full member lists** (`selectorMembers` 138, `selectorMembersVariantB` 108,
`selectorMembersVariantC` 126, `noneSecondaryMembers` 450), so the post-run delta is a set difference
rather than a count — which is what a row with no fixed acceptance bar needs, since "which of these
should get a second element" cannot be read off a number.

So at this head the stated rule reads 138, against the board's 108 and the register's 127; B and C are
recorded because the register's own wording ("species with no fusion recipe at all") is closer to B than
to A. Which definition the row wants is a call for its owner — the same call F2b already reserved to
content/balance judgement (`combat-unification-todo.md` F2b: *"which of these should get a second
element is itself a content/balance judgment call"*). The count will move again when the in-flight run
writes anchors; re-run the command for the delta.

### Where the gap sits (same command, `selectorDistribution` in the JSON)

| cut | the 138 | the wider `none` set (450) |
|---|---|---|
| side | zombie 67 · plant 71 | — |
| `pure` | **true 126** · false 12 | — |
| rarity | `sprout` 43 · `chaff` 34 · `grafted` 33 · `almanac` 12 · `cultivated` 7 · others 9 | — |
| family | `unclassified` 13 · `undead+reanimated` 4 · `metallophyte` 2 | — |

So the gap is overwhelmingly `pure`, low-rarity species (sprout/chaff/grafted) with no fusion lineage —
which is why the selector rule cannot resolve it arithmetically and why the row leaves it to content
judgement: a classifiable answer may legitimately stay `none` for most of these, exactly as F2b's own
note says of the first pass.

### The vocabulary the answer must live in (same command, `elementVocabulary`)

The six elements are **read** from the adapter (`anchor/prompts.py`'s `ELEMENTS`, whose own source note
pins them to `gk-core/src/FusionRpg.Core/Combat/Element/ElementTable.cs:125-130`), never transcribed here, and
tallied against the corrected anchors: primary `earth` 399 · `fire` 149 · `light` 108 · `ice` 102 ·
`dark` 86 · `air` 60, secondary `earth` 168 · `fire` 76 · `air` 59 · `ice` 58 · `light` 58 · `dark` 35 ·
`none` **450** — with **`outsideVocabulary: []`** and **`speciesMissingPrimary: []`**. So F2b's gap is a
*presence* gap inside a closed vocabulary that the corpus already respects (every species has a primary;
no secondary is an illegal value); a classify pass cannot be blocked by vocabulary here.

## `doublecherry`'s `attackTempo`

| field | value |
|---|---|
| `attackTempo` | `"quick"` |
| `_provenance.confidence.attackTempo` | **`deterministic-fallback`** |
| `_provenance.promptVersions` | eight stages at v1, `element-secondary` among them |

So the field is present and honestly stamped as the deterministic fallback. **Correction (same lane,
next commit): that is not work the in-flight run owes.** `tasks/species-build-todo.md` records the
closure itself — *"Follow-up, 2026-09-07 (closed same day): `doublecherry` resolved, owner-directed
manual pick, never a model call"* — the owner set `attackTempo: "quick"` from the anchor's own emitted
evidence and stamped `deterministic-fallback` on purpose ("the same tag Phase I's aptitude/rarity/
threat-band fallbacks use — never disguised as a real model judgment"), with the chain re-run
end to end (`CreatureSpeciesGen` 903 → 904, `CreatureSpeciesImport` 1 written, `CreatureBuildPlanGen`
84/84). The residual is only the *tag*, which that row keeps deliberately, so if BCU2.13 is meant to
replace it with a real vote that is a new requirement the owning row does not carry — an owner call.

Sized across the whole roster, the tag is one species, not a population
(`python tasks/reports/bcu2-13-attacktempo-census.py --out tasks/reports/bcu2-13-attacktempo-census.json`):

| `_provenance.confidence.attackTempo` | species |
|---|---:|
| `high` | 727 |
| `split` | 173 |
| **`deterministic-fallback`** | **1** — `DoubleCherry` (`quick`) |
| absent | 3 |

and the value distribution is `steady` 304 · `slow` 191 · `flurry` 179 · `ponderous` 160 · `quick` 70.
(These are the corrected post-`speciesId`-resolution figures; the tag count is unchanged at one species,
which is the conclusion the sizing exists for.)
