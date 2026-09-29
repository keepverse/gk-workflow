# Spec: Creature drop tables (`creature-drop-tables`)

**Initiative:** `species-gear-chain` ([map](../species-gear-chain-map.md)) · **Module:** `creature-drop-tables`
**Owning program:** `drop-tables`
**Depends on:** `species-magnitude-synth`, and at least one of `wave-species-roll` / `wild-species-spawn` / `delve-species-wiring`
**Status:** spec, 2026-09-13. Awaiting owner approval. No build authorized. ⚠ *2026-09-18: approved through `tasks/species-gear-chain-plan.md`; build state — unbuilt (T29–T31).*
**Source ideal:** [tier-system-ideal.md](../tier-system-ideal.md) § The shape 2 — edges E1, E2, E3a

> **Amended 2026-09-18 for owner ruling R-SC1 (2026-09-17)** — only Open question 3 and a new
> § Seedsmith / generator section change. R-SC1 made a kill yield **species, family and general** (R9 removed the general leg — next note)
> trophies (`spec-species-materials.md` § Design 5), and a per-rung table cannot name *the killed
> species'* trophy id without either 904 tables or a parametric entry. This module owns that entry
> shape. **Build state:** unbuilt (T29–T31, Phase 3).
>
> **Amended again 2026-09-18 for owner ruling R9** ([spec-rulings-2026-09-18.md](../spec-rulings-2026-09-18.md)):
> the general layer is removed (general = 0, family 8, species 2). A kill now yields **species and
> family** trophies only — two draw groups, not three — and the parametric entry's scope vocabulary is
> two values. A species with no family yields its species leg only; there is no general fallback.
>
> **Amended 2026-09-18 for owner ruling R22** ([spec-rulings-2026-09-18.md](../spec-rulings-2026-09-18.md)):
> *"Rolled per kill, equal odds, among its families; the species counts as a member of **every** listed family for recipes, so it can supply any of them."*
> The family entry's mint-time resolution is pinned below (Open question 3, Strengthen pass item 3);
> the recipe side lives in `spec-species-materials.md` § Strengthen pass item 4.

---

## Objective

**Make killing a creature yield material that reflects what it was.**

This closes the middle of the spine: the player can now reach a species, and this is where the species
starts producing something. Three edges, in increasing order of honesty about cost.

| Edge | What it is |
|---|---|
| **E2** | A drawn `Material` entry actually credits the material shelf |
| **E1** | A creature kill is a loot **source** with its own tables |
| **E3a** | The shard a creature yields keys on **its own rung**, not a hardcoded pair |

⚠ **E3b — the layered species/family trophy model (the tier ideal's "general/species-unique"; R9
removed its general layer) — is NOT in this module.** It is
`species-materials`, and it is the vocabulary-widening ask-first change.

---

## What exists today — verified against code

### Built

- **`DropEntryKind` is a closed ten-member enum** — `Equipment, Material, Currency, Insert, Charm,
  Consumable, Unique, Relic, Table, Nothing` (`Items/Drops/DropTableModel.cs:20-32`; `Relic` was added by
  empire-development after this spec was written — re-verified 2026-09-18). **`Material` is already
  drawable**; E2 is not about making it drawable.
- **`LootSourceRow(SourceKind, SourceId, TableId, ContentLevel)`** is already the generic carrier —
  `source_kind` is a `TEXT` column, not an enum, so adding a ninth kind is **content and vocabulary,
  not a schema migration**.
- ~~`decisions.md` — 'Battle death attribution (2026-09-08)' already puts `KillerActorKey` / `killerPtr` on the `die` occurrence, so *"who
  killed this"* is already on the wire.~~ ⛔ **STRUCK — overstated, and the ideal had already said so.**
  `tier-system-ideal.md:148-150`: *"**`decisions.md` — 'Battle death attribution (2026-09-08)' was overstated.** `KillerActorKey` is scoped
  to *'web/standalone battles where the server owns HP and resolution'*; **on the lawn it carries
  nothing** — which contradicts E1's 'what exists'."* This spec quoted the pre-correction claim for
  its own headline edge. **Kill attribution exists for server-resolved battles only; the lawn path is
  a real gap**, and gameless-first means E1 must work without it.
- **`gk-core/data/tuning/drop-rate-floor.v1.json`** ships with `minRatePerMillion: 1`, read by
  `Items/Drops/DropRateFloor.cs`. ⚠ **Consume it; do not re-introduce a floor.** An earlier draft of
  the ideal proposed one before finding it already shipped.
- ⭐ **There are TWO drop-table corpora and neither replaces the other.** `gk-data/packs/fusion/data/seed/loot/README.md`
  says so in its own section heading (*"Why this is not `gk-data/packs/fusion/data/seed/items/drop-tables/`"*):

  | Corpus | Owner | Read by |
  |---|---|---|
  | `gk-data/packs/fusion/data/seed/loot/` (5 files) | item module 11 `drop-volume` | `LootCorpusReader` (`Items/Drops/LootCorpus.cs`), judged by `DropTableValidator`, drawn by `LootPipeline` — **the runtime corpus** |
  | `gk-data/packs/fusion/data/seed/items/drop-tables/` (4 files) | item-seedgen module 10 `drop-tables-gen` | `droptablegen` **writes here** (`droptablegen/tuning.py:30 DROP_TABLES_DIR`), `_meta.model` present |

  ⚠ **Two corrections at once.** `tier-system-ideal.md:216-217` claims *"`gk-data/packs/fusion/data/seed/loot/**` does not
  exist"* — **it does.** And an earlier draft of this spec called `gk-data/packs/fusion/data/seed/loot/**` *"droptablegen
  output"* — **it is not**; droptablegen writes the other one. **E1's runtime tables go in
  `gk-data/packs/fusion/data/seed/loot/`; the generator's output tree is `gk-data/packs/fusion/data/seed/items/drop-tables/`.**

- `droptablegen` already loads rarity ids
  from tuning (`load_rarity_ids`, `droptablegen/tuning.py:159-163`) — the T-1 pattern.

### Wiring gap

- **E2:** a `Material` entry can be drawn and the grant is emitted, but the shelf is not credited.
  ⚠ **Sizing corrected.** An earlier draft called this *"one arm"*; `tier-system-ideal.md:172-176` had
  already struck that: *"⛔ **E2 is not 'one arm'.** … Plus a player-id type mismatch
  (`PersistLootUnlocked` keys on `string`, the credit helpers on `long`). Honest size: **2–3 Data files
  + tests**, not one call."* The type mismatch is the part that makes it more than a wiring edit.

### ⛔ Real gap — and E3a is NOT "one read"

The ideal's § The shape 2 describes E3a as *"one read"* — replacing hardcoded shard ids at
`ExpeditionResolver.cs:172-173`. **That is wrong, and the ideal's own audit already struck it.** The
verified state:

`ExpeditionResolver.cs:94-98`, inside the battle-plan loop:

```csharp
// Shards drop at plan time, win or lose — the resolver never sees battle outcomes
// (they resolve later at collect), and win-gating here would break the manifest's determinism.
materials.TryGetValue(isBoss ? ShardRare : ShardCommon, out var have);
materials[isBoss ? ShardRare : ShardCommon] = have + 1;
```

Three facts make this more than a read:

1. **The shard is chosen by `isBoss`, not by species** — a two-value ternary over two consts.
2. **It mints at *plan* time**, and the comment records why: *"the resolver never sees battle
   outcomes… win-gating here would break the manifest's determinism."*
3. **There is no species in scope** at that line. `setup.Wave` holds the enemy list; the mint is
   per-tick, not per-enemy.

**So E3a needs the species threaded to the mint point, and it must preserve plan-time determinism.**
That is a real change to what the manifest is computed from — not a substitution.

⭐ **This is the honest sequencing consequence:** E2 and E1 are small. **E3a is the one that needs
design**, and it should be specced after the selection modules land, when there is a real species at
that point to thread.

---

## Design

### 1. E2 — credit the shelf

~~One arm in `LootMintAt.Mint` for `DropEntryKind.Material`~~ ⛔ *Corrected 2026-09-18 (strengthen
pass): `LootMintAt.Mint` is the wrong site.* Its own doc comment (`LootMintAt.cs:44-51`) records that
`Material`/`Currency` grants are added to `manifest.Grants` directly and **never reach `Mint`**. The
credit belongs in **`PersistLootUnlocked`** (`RpgStore.Loot.cs:567`) alone, and its position is
load-bearing:

- **After** the `(player_id, correlation_id)` early return (`RpgStore.Loot.cs:576-584`), so a retried
  loot resolution credits **nothing twice** — the idempotency the drop log already has is inherited,
  not re-built.
- **Inside** the caller's transaction (`db`, `tx`), so the drop-log row and the shelf credit commit
  together or not at all — including the Delve path, where `CloseDelve` owns the transaction
  (`RpgStore.Delve.cs:707`).
- The `string` player id the drop log keys on and the `long` the credit helpers take is converted
  **once, checked** — a non-numeric id refuses the whole persist by name, never credits a default row.

Tested: a replayed correlation id leaves the shelf unchanged; a thrown credit rolls the drop-log row
back with it.

### 2. E1 — a ninth `source_kind`, and the paired arm nobody mentioned

`source_kind` is `TEXT`, so the change is: a new id in the closed source-kind vocabulary, its
authored tables, and kill attribution wired to resolve a species.

⛔ **And a paired change the earlier draft missed.** `Items/Drops/DropTableValidator.cs:52-59` lists
the eight shipped kinds (`web-wave`, `expedition-tier`, `world-sector`, `pvz-run`, `dungeon-room`,
`dungeon-clear`, `dungeon-quest`, `siege-assault`) with its own warning:

> *"Each also gains a `LootCorrelation.Derive` arm (`LootPipeline.cs`) — **neither list is complete
> without the other**."*

**A ninth kind without its `Derive` arm is a self-documented incompleteness.** Both, in one change.

⚠ **And kill attribution is only half-built** (see the struck bullet above): it exists for
server-resolved battles, not the lawn. E1 must therefore key on a source the **expedition / delve /
wild** paths can supply, not on a lawn kill.

**Table shape to start from:** *1 generic + 3 commons + 1 rare gate*, with weights and gate rates in
per-million, matching the unit `drop-rate-floor.v1.json` already uses.

### 3. E3a — the species' own rung selects the shard

Replace `isBoss ? ShardRare : ShardCommon` with a lookup on the **killed species' rarity rung**, which
already has a minted id (`shard.{rarity}`). This is MH re-tiering **with ids that already exist** —
no vocabulary change.

⚠ **Determinism is the constraint, not a nicety.** The manifest is computed at plan time and its
determinism is load-bearing. Two shapes are possible:

| Shape | Note |
|---|---|
| **Plan-time, from the planned wave** | The wave's species are known at plan time, so the rung is derivable without seeing outcomes. **Preserves the existing contract exactly.** ✅ Recommended |
| Collect-time, from actual kills | More accurate, but moves the mint out of the manifest and changes what determinism means |

**Recommendation: plan-time, from the planned wave's species.** It keeps the comment at `:94-96`
true.

---

## Tech stack

C# .NET 8 (`FusionRpg.Core/Items/Drops`, `FusionRpg.Core/Expeditions`, `FusionRpg.Data`),
Python 3 (`droptablegen`), xUnit + pytest.

## Commands

```powershell
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Drop"
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Expedition"
dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~Loot"
$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests -q -k droptable
python gk-core/scripts/guard-dal.py
python gk-core/scripts/audit-overflow.py
```

## Seedsmith / generator

**Generator involved: only at the authoring-input side, and not for the runtime tables.** The E1
tables this module ships live in `gk-data/packs/fusion/data/seed/loot/**` — the **authored** runtime corpus owned by item
module 11 (`gk-data/packs/fusion/data/seed/loot/README.md`: *"the band→row generator … does not exist yet"*). They are
authored, not generated, so the no-hand-edit rule does not bind them; `DropTableValidator` does.

| Stage | Adapter | Change | Tuning | New seed fields |
|---|---|---|---|---|
| Authored input tables (`gk-data/packs/fusion/data/seed/items/drop-tables/`) | `gk-forge/tools/seedsmith/seedsmith/adapters/items/droptablegen/emit.py` — `RowPlan` (`:75-83`), `_material_row` (`:99-105`) | **(new)** a `_trophy_row(scope, slot, drop_band)` beside `_material_row`, so the authored-input corpus can express R-SC1's parametric entry the runtime corpus uses. Code decides `scope` and `slot`; the model still answers only `dropBand` (a closed band enum — P1) | `droptablegen/tuning.py` (the existing curve/band ids; nothing new) | `trophyScope` (closed enum `species`/`family` — R9 removed `general`), `slot` (an ordinal index emitted by code). No number a model writes; `audit_schema` (`pipeline/model.py:113`) stays clean |
| Runtime tables (`gk-data/packs/fusion/data/seed/loot/**`) | none — authored | Creature tables per rung; the two trophy legs (species, family — R9) are two independent draw groups (`DropTableModel.cs:76-85`), each a parametric trophy entry weighted against `Nothing`. No general draw group | the weights live in these tables (module 11's corpus) — `creature-yield.v1.json` keeps only the rung→grade map | the same two fields, validated by `DropTableValidator` |

```powershell
$env:PYTHONPATH = "gk-forge/tools/seedsmith"
python -m seedsmith items generate --kind drop-table --dry-run
cd gk-forge/tools/seedsmith; python -m seedsmith check gk-data/packs/fusion/data/seed/items --adapter items
```

**pytest:** `gk-forge/tools/seedsmith/tests/test_drop_tables_gen.py` — a trophy row carries a closed scope and a
code-emitted slot, and the model-facing schema offers neither; a `general` scope is refused (R9).

## Project structure

| Path | Role |
|---|---|
| `gk-core/src/FusionRpg.Core/Items/Drops/` | `LootMintAt.Mint`, `DropRateFloor` |
| `gk-core/src/FusionRpg.Data/Sqlite/` | `PersistLootUnlocked`, the `source_kind` row |
| `gk-core/src/FusionRpg.Core/Expeditions/ExpeditionResolver.cs:94-98` | E3a |
| `tools/seedsmith/.../droptablegen/` | The table generator |
| `gk-data/packs/fusion/data/seed/loot/**` | The **runtime** corpus (item module 11 `drop-volume`) — where E1's tables land |
| `gk-data/packs/fusion/data/seed/items/drop-tables/**` | `droptablegen` **output** — regenerated, never hand-edited |
| `gk-core/src/FusionRpg.Core/Items/Drops/LootPipeline.cs` | ⛔ The paired `LootCorrelation.Derive` arm — see below |

## Code style

```csharp
// E3a: the shard keys on the KILLED SPECIES' OWN RUNG, from the planned wave — not on isBoss.
// Plan-time by necessity: the manifest's determinism depends on the resolver never seeing battle
// outcomes (see the comment above), so the rung is derived from the PLANNED enemies, which are
// known here, rather than from actual kills, which are not.
var shardId = MaterialIds.ShardFor(PlannedRungFor(setup.Wave));
```

---

## Tunables

| Number | Meaning | Owner |
|---|---|---|
| Per-species-kind drop weights (`weightPerMillion`) | E1's tables; the *1 generic + 3 commons + 1 rare gate* shape | `gk-data/packs/fusion/data/seed/loot/**` (runtime corpus, module 11) |
| Rare-gate rates (`gateRatePerMillion`) | How often the gated entry fires | Same |
| Species-tier → material grade/rung map | Which shard rung a creature of rung *n* yields (MH's `Scale` → `Scale+` → `Shard`) — E3a's `ShardFor` reads it; a ten-row identity map is a legal first value, a missing rung is a load rejection (T5) | New `gk-core/data/tuning/creature-yield.v1.json` — ⭐ **owned by this module alone** (strengthen pass 2026-09-18: "shared with `species-materials`, whoever creates it first" was two owners for one file, and `species-materials` reads nothing from it) |
| ~~A drop-rate floor~~ | ⛔ **Already ships.** `drop-rate-floor.v1.json` `minRatePerMillion: 1` | *(shipped — consume it)* |

**Structural (stays `const`, with a comment saying why):** the `DropEntryKind` enum and the
source-kind vocabulary — closed lists the code owns.

## Numeric types

- Weights and gate rates are **per-million `int`s** — bounded ratios, exempt and commented as such.
  ⚠ Note the unit is **per-million**, matching `drop-rate-floor.v1.json`, **not** per-mille like the
  socket and cost tables. Mixing the two is the most likely bug in this module.
- Yield **quantities** are `long`. They are magnitudes that scale with content.
- **Widen before multiplying; divide last, exactly once; integer overflow throws.** Floating-point is allowed (owner ruling 2026-09-15).

## ActorHub gate

**N/A and checked.** A drop table produces materials, not actor combat / derived / AppliedCombat
magnitudes. Nothing composes, contributes, or folds. `guard-actor-hub.py` stays green.

## Testing strategy

| Level | What it asserts |
|---|---|
| Unit | E2 — a drawn `Material` entry **credits the shelf**, end to end |
| Unit | E1 — a creature kill resolves to its source row and draws from its table |
| Unit | E3a — the shard id follows the **species' rung**, across several rungs |
| Unit | ⭐ **Plan-time determinism is preserved** — the same expedition seed yields a byte-identical manifest, before and after E3a |
| Unit | The shipped drop-rate floor is **consumed**, not re-implemented — a sub-floor weight still draws |
| Unit | Per-million and per-mille units are not mixed — a table asserting a known rate against a hand-computed expectation |
| Contract | Every `source_kind` is in the closed vocabulary; every table id resolves |
| pytest | `droptablegen` emits tables whose weights sum as declared and whose literal material ids resolve in the material vocabulary (`materialgen/vocab.py` `ISSUABLE`) — not "in the closed 27": `species-materials` widens that set with generated trophy ids, a population. A trophy entry carries scope + slot, never a literal id |
| Unit | ⭐ **R22 single-family:** a one-family species' family entry resolves to that family with no `item.trophy-family.*` draw |
| Unit | ⭐ **R22 multi-family by seed:** over an enumerated seed set, a two-family fixture resolves to each listed family, the same `(SourceSeed, correlationId)` always resolves the same family, and a replayed correlation id credits once (`RpgStore.Loot.cs:580-584`) |
| Unit | ⭐ **R22 stream isolation:** adding a trophy group with a multi-family species leaves every other group's draws byte-identical (the `item.trophy-family.*` stream shifts nothing) |
| Report | Per-species yield distribution — **a reading, printed, never asserted** (the per-family split of multi-family species included) |

⛔ **No test asserts a drop rate as a balance outcome or a table count.** Assert the **draw contract**
and **closure**; print the distribution.

## Boundaries

**Always**
- ~~**Fix the generator and regenerate.** `gk-data/packs/fusion/data/seed/loot/**` is `droptablegen` output.~~ ⛔ *Corrected
  2026-09-18 — this contradicted the spec's own § What exists:* `gk-data/packs/fusion/data/seed/loot/**` is **authored** (item
  module 11's runtime corpus); `droptablegen` writes `gk-data/packs/fusion/data/seed/items/drop-tables/**`. Fix the generator
  and regenerate **that** tree; author and validate the runtime tables.
- Consume the shipped drop-rate floor.
- Preserve plan-time manifest determinism.
- Keep per-million and per-mille units straight, and say which in every comment.
- Commit with plain `git` (explicit paths).

**Ask first**
- ⛔ **The ninth `source_kind` id.** It is a closed vocabulary.
- Moving the shard mint out of plan time — that changes what the manifest's determinism means.
- Creating `creature-yield.v1.json` — this module is its **sole owner** (strengthen pass 2026-09-18); `species-materials` does not write it.

**Never**
- ⛔ Widen the closed 27-id material vocabulary here. That is `species-materials`', and it is
  ask-first against `ssot-materials-crafting.md` §3.1.
- ⛔ Introduce source-tagged material ids. §3.4 bans them, and MH's own `itemData` sprawl (IDs
  0–2315) is the documented failure mode.
- Re-introduce a drop-rate floor.
- Hand-edit a generated loot table.
- Let one species' yield **strictly dominate** — see below.
- Assert a population count.

## ⛔ The guard this module makes load-bearing

**No single species' rewards may strictly dominate.**

`wild-species-spawn` records this obligation; **this is the module that creates the risk.** A map full
of creatures whose drops are strictly ordered will be farmed at exactly one sector — the documented
Wilds/Arkveld outcome, where monoculture followed **reward dominance, not the UI**.

The discipline is `roster-metrics` (creature-seed module 14) pointed at yields. It is a **report,
never a test assertion**. The design lever is **overlap**: a higher-rung creature should yield *better
odds*, never a strictly superior set — the same overlap principle `rarityGrant`'s windows already use
deliberately (*"adjacent windows OVERLAP by design… so socket count never becomes a strict ladder"*).

## Success criteria

1. A drawn `Material` entry credits the shelf, proven end to end.
2. A creature kill resolves to a loot source and draws from its own table.
3. The shard a creature yields follows **its rung**, not `isBoss`.
3a. ⭐ An `Equipment`-kind entry in a creature-authored table mints a real, saved equipment instance
    through the existing `LootMintAt.cs:77-87` arm, with `thetaContent` derived from the killed
    species' own rung — the same input E3a establishes for the shard. No new equipment-roll mechanism
    is built; this criterion proves the existing arm is reachable from a creature source.
4. ⭐ Expedition manifests remain byte-identical for a given seed — plan-time determinism intact.
5. The shipped drop-rate floor is consumed; no second floor exists.
6. No new material id; the 27-id vocabulary is untouched.
7. A per-species yield **distribution report exists and is printed**.
   ⚠ **Split from what this module cannot close.** *"No species' yield strictly dominates another's"*
   needs `roster-metrics` (creature-seed module 14) pointed at yields — which is **not one of the
   nineteen**, and which this initiative's own map defers with the hunt interaction. **The dominance
   guard is a named obligation on the world-stage hunt module, not a criterion this module can meet.**
8. `guard-dal.py`, `guard-actor-hub.py` green; Core, Data and pytest suites green.

## Strengthen pass 2026-09-18 — representation, ordering and dependency gaps

1. **The parametric trophy entry needs a persisted shape — named here so T30 does not invent one.**
   `drop_table_entry` (`RpgStore.Loot.cs:85-103`) carries `entry_kind`, `ref_id` and no scope column,
   and `DropTableEntryRow` (`DropTableModel.cs:93-107`) mirrors it. Two shapes were weighed:
   - *Overload `ref_id`* with a grammar such as `trophy:species:1` under `Kind = Material` — no schema
     change, but `RefId` would then mean "a material id **or** a rule" inside one kind, and every reader
     of a `Material` entry (validator, pipeline, report) would have to re-parse it. Rejected (SOLID L: a
     `Material` entry would no longer be substitutable for a `Material` entry).
   - ✅ **Two nullable columns, `trophy_scope` + `trophy_slot`, on `drop_table_entry`, mirrored on
     `DropTableEntryRow`**, with `ref_id` empty when they are set. An additive `ALTER TABLE` inside
     `FusionRpg.Data` (the DAL guard holds), no new `DropEntryKind` member (the ten-member enum stays
     closed). `DropTableValidator` refuses a row carrying both a `ref_id` and a scope, a scope outside the
     closed two-value vocabulary, and a slot outside `1..perScope` of the injected trophy registry — all
     under the existing `drop.*` namespace.
2. ⛔ **Dependency: trophy entries do not ship before `CreatureAdmission` refuses excluded species**
   (`creature-seed` map ask 4). The 12 `speciesKind: "excluded"` species still spawn in every context
   (`CreatureAdmission.cs:14-24`), have no trophy registry row, and so would hit Open question 3's
   by-name refusal on every kill. E1/E2/E3a are unaffected — only the parametric trophy entries (T30's
   `species-materials` half) wait.
3. **Order-independence of the two resolutions on one kill.** E3a's shard and the trophy legs read the
   same planned species once (Open question 3). The trophy family draw (R22: one family per kill, equal
   odds) uses the kill's own seeded stream, **domain-separated** from the shard's and the equipment
   roll's: **`LootStreams.TrophyFamily(tableId, groupKey)` = `item.trophy-family.{tableId}.{groupKey}`**,
   derived from the sealed `lootSeed` (`LootPipeline.cs:233`), declared in `LootStreams` beside
   `GroupDraw` (`LootStreams.cs:31-32`) and nowhere else. A single-family species consumes no draw from
   it. So adding a trophy group never shifts an existing table's rolls — and
   Success criterion 4's byte-identical expedition manifest is asserted **with and without** trophy
   groups present.
4. **`creature-yield.v1.json` has one owner — this module.** See § Tunables.

## Open questions

1. ⭐ **Plan-time or collect-time for E3a?** **Recommendation: plan-time, from the planned wave.** It
   preserves the manifest contract exactly, and the planned species are known where the mint happens.
2. ⭐ **DECIDED 2026-09-13 (owner) — equipment drops too, in v1**, overriding this spec's own
   recommendation of materials-only. **This does not open a new rarity/affix-roll design:**
   `DropEntryKind.Equipment` is already a **built** arm — `LootMintAt.cs:77-87` already mints a real
   equipment instance via `EquipmentContainerBuild.From` + `Instantiator.TryInstantiate`, driven by
   `grant.RollSeed` and a `thetaContent` input, and other drop sources already use it. **The only new
   design surface is what `thetaContent` a creature-authored `Equipment` entry rolls at** — resolved
   the same way E3a resolves the shard: **the killed species' own rung**, at plan time, from the
   planned wave (Open question 1's answer applies identically here — one `theta` input, two entry
   kinds). No new rarity/affix mechanism, no set-roll design; this module supplies the input, the
   existing arm does the rest.
3. **One table per species, per rung, or per species-kind?** **Recommendation: per rung, with a
   per-species override slot left empty.** 904 authored tables is the MH sprawl failure; a rung table
   plus a thin override is the bounded shape.
   ⚠ *Amended 2026-09-18:* this line ended *"the same 1–2-per-species discipline `species-materials`
   uses"*. R-SC1 replaced that discipline with generated per-scope counts, revised by R9 to 2 per
   species and 8 per family with **no general scope**. The
   per-rung recommendation survives it **only with a scope-parametric trophy entry (new)**: an entry of
   kind `Material` that names a trophy **scope** (`species` | `family`) and a **slot**
   rather than a literal id, resolved at mint time against the killed species — its `speciesId`, or
   (R22) one of its families with **equal odds** by `NextInt(count)` over its `family-map.json` list on
   the `item.trophy-family.{tableId}.{groupKey}` stream (Strengthen pass item 3); the species still
   counts toward every listed family for recipes (`spec-species-materials.md` § Design 5.2). A killed species with **no family**
   resolves the family entry to nothing by rule (the group is skipped, never a filler and never a
   general fallback — `spec-species-materials.md` § Design 5.3); that is distinct from an entry
   whose resolved id is missing, which is refused below. Resolution happens
   where E3a already reads the killed species' rung, so there is one species lookup, not two. An
   entry whose resolved id is absent from the injected trophy registry is refused by name through the
   existing `ContentRuleViolated{drop.*}` namespace — never a silent `nothing`.
