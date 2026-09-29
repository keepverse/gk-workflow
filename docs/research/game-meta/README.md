# Game type model — mined from `Assembly-CSharp.dll`

**Captured 2026-09-17** against the MelonLoader 3.9 pack's `MelonLoader/Il2CppAssemblies/Assembly-CSharp.dll`
(8,405,504 bytes). Regenerate with:

```powershell
dotnet run --project gk-fusion/tools/GameMetaDump -- `
  --assembly "<game-dir>\MelonLoader\Il2CppAssemblies\Assembly-CSharp.dll" `
  --metadata "<game-dir>\PlantsVsZombiesRH_Data\il2cpp_data\Metadata\global-metadata.dat" `
  --out docs/research/game-meta
```

`--metadata` is not optional in practice — see *Recovering the names the interop assembly destroyed*
below. Without it the dump is still correct, but 628 members across the 18 most interesting enums carry
an unusable placeholder instead of a name.

`gk-fusion/tools/GameMetaDump` is a **read-only metadata walk** (`PEReader` + `MetadataReader`). It never loads or
executes the assembly, never reads game memory, and never needs the game running. It emits names and
shapes only — no IL, no constants, no assets. It records no filesystem path, so nothing here leaks a
machine-local game directory.

**Not in CI.** The input is the owner's own legally-installed game, which CI does not have, so there is no
`--check` drift gate — it would fail on every machine but one. Re-run by hand after a game version bump
and commit the diff.

| File | Rows | What it answers |
|---|---|---|
| `index.json` | 3,767 types | *Does the game have a `X`?* — namespace, name, field/method counts |
| `datamodel.json` | 274 types | *What can I call on it?* — full field and method detail for the data-bearing types |
| `enums.json` | 194 enums, 4,186 members | *What is the closed vocabulary?* — every enum and its members, names recovered |
| `full.json` | — | Everything, via `--full`. **Not committed** — regenerate in one command |

`datamodel.json` selects on the game's own naming (`*DataManager`, `*DataLoader`, `*Data`, `*Config`,
`*Info`, `*Manager`, `*Table`, `*Tree`, `*Type`). A shape heuristic was rejected because it drags in every
UI window that happens to hold an int.

---

## Why this was mined

The creature corpus bakes every species' magnitudes from `pTheta × k`, and the resulting roster is
homogeneous: 88 distinct `resource.max.hp` values across 904 species, 189 distinct magnitude vectors, and
Peashooter and GatlingPea baking byte-identically.

The cause is not the bake — it is that **there was almost nothing real to bake from.** The only stat
capture path reads fields off a **live spawned entity** (`GameHooks.cs:1678` → `GameDumps.Zombie`, reading
`z.theAttackDamage` / `z.theFirstArmorHealth`), so a type that was never spawned has no observed stats.
Measured against `gk-data/packs/fusion/data/seed/creatures/_dump/` as captured 2026-08-23:

| | rows | `statsObserved` | hp / attack | armor |
|---|---|---|---|---|
| plant | 677 | **64** (9.5%) | 64 | **0** |
| zombie | 227 | **18** (7.9%) | 18 | 18 |

**82 of 904 species (9%) have real game stats, and plant armour was never captured at all.**

So the question was whether the game exposes its stats any other way. It does.

---

## What the mine found

### 1. Base stats are static, per type, and need no spawn

```
PlantDataManager.GetPlantData(PlantType)          -> PlantData
PlantDataManager.GetPlantOriginalData(PlantType)  -> PlantData      // unmodified base
    maxHealth · attackDamage · attackInterval · produceInterval · cd · cost

ZombieDataManager.GetZombieData(ZombieType)       -> ZombieData
    theMaxHealth · theAttackDamage · armor
    theFirstArmorMaxHealth · theSecondArmorMaxHealth
    cost · cd · summonLevel · summonWeight
```

Both accessors are `public static` and keyed by the enum, so a sweep is the same loop
`GameHooks.EnqueueFullAlmanacText` already runs for *text*.

`GetPlantOriginalData` returns the **unmodified** base, which is the correct input — it is immune to
whatever the current run has mutated (`PlantDataManager` also exposes `ModifyPlant` / `ApplyModify` and
holds both `PlantData_Default` and `PlantData_Modified`).

**Enum sizes cap the sweep:** `PlantType` has **698** members, `ZombieType` **229**. That is ~925 types
reachable, against 82 observed today.

**Neither manager is referenced anywhere in `src/`.** Grep returns zero hits. This is a wiring gap, not a
limit.

### 2. `ZombieData` carries a game-authored tier ladder

`summonLevel` and `summonWeight` are per-type fields the game already uses to decide what may appear and
how often. That is a difficulty/tier signal authored by the game's own designers — no LLM, no derivation.

### 3. The fusion tree is a second, independent tier ladder

`PlantMixTreeManager` exposes `PlantMixTrees`, `ChildToParents`, `IsInitialized` and `Statistics`. Only
`ChildToParents` is consumed today (`GameHooks.EnqueueRecipes`, which produced the committed 1,295-recipe
`gk-data/packs/fusion/data/seed/creatures/_dump/recipes.json`). Fusion depth over that DAG:

| depth | 0 (base) | 1 | 2 | 3 | 4 | 5 | cyclic |
|---|---|---|---|---|---|---|---|
| types | 78 | 347 | 86 | 54 | 39 | 15 | 86 |

`WallNut + WallNut = BigWallNut`; `ObsidianSpike + WallNut = ObsidianWallNut`. The 86 "cyclic" entries are
recipes whose output is also an input (`WallNut + TallNut = TallNut`), so a depth pass must handle cycles
rather than assume a DAG.

`PlantMixTrees` and `Statistics` are unread and may carry more.

---

## Recovering the names the interop assembly destroyed

Il2CppInterop regenerates the managed assembly from `global-metadata.dat`, and on this game it **fails for
every enum whose members are named in Chinese**. Instead of the member name it writes the literal string
`EnumValueAsmResolver.DotNet.Serialized.SerializedConstant` — a `ToString()` of its own internal object —
into the field name. The enum *values* survive intact (`0..N`, in declaration order); only the names die.

Measured on the 3.9 pack: **18 enums, 628 members**, and they are the most interesting enums in the game.

| enum | members | what it is |
|---|---|---|
| `AdvBuff` | 177 | advanced buffs — 撒豆成兵, 核能威慑, 百步穿杨, 量子护盾 … |
| `TravelDebuff` | 142 | per-zombie travel modifiers — 黑橄榄禁疗, 基洛夫加速 … |
| `UltiBuff` | 56 | ultimate buffs — 嗜血如命, 世纪之盾, 永动机 … |
| `TalentType` | 47 | a talent tree, with explicit I/II/III rungs |
| `FruitBuffType` | 25 | 力大砖飞, 有丝分裂, 冰封千里 … |
| `SynergyType` | 19 + 25 | squad synergies — 前院守卫, 蘑菇岛, 战术小队, 泰坦之躯 … |

`global-metadata.dat` still holds the originals, so nothing was lost by the *game* — only by the
regeneration step. `Il2CppMetadata.cs` reads three tables back (string blob, field table, type-definition
table) and re-attaches the names **positionally**, guarded by an exact field-count match between the two
sources: a length mismatch means the lists are not the same list, and grafting by position would silently
mislabel every member, which is the one failure that would be hardest to notice downstream.

Verified: `628 recovered, 0 still lost`, and `enums.json` contains no remaining placeholder.

The parser refuses any metadata version other than **v31** rather than guessing — the table offsets move
between versions, so parsing anyway would produce confident nonsense instead of an error. It reads names
only: no IL, no constants, and deliberately never the `stringLiteral` tables, which hold the game's
user-facing text.

---

## The effect vocabulary

The game carries a large, closed effect/status vocabulary — the same shape as this repo's atoms. Intact
without recovery:

| enum | members | sample |
|---|---|---|
| `EffectType` | 21 | Cold, Jala, Freeze, Ember, Poison, Portal, Butter, Kelp, Immune, Fragile, Love, Curse, Recover, FireCover |
| `ZombieStatus` | 49 | Dying, Flying, Miner_digging, Gargantuar_withImp, WithSnowShield, Boss … |
| `PlantStatus` | 44 | Chomper_bite, Blover_blow, Kelp_grab, Prism_shoot, DoomTorch_active … |
| `PlayerWeaponBuff` | 45 | Pea_damage, Fume_length, Gloom_range, Laser_loadSpeed … |
| `PlayerBuff` | 29 | Defence, Invincible, BulletTime, StrikeDamage … |
| `BulletStatus` | 11 | Melon_cannon, Endoflame_sun, Doom_big, Water_cold … |
| `DamageEffect` | 9 | SetCold, SetFreeze, SetJalaed, AddPoisonLevel, AddFreezeLevel … |

`EffectType` overlaps this repo's own status vocabulary almost one-for-one (Cold / Freeze / Poison /
Butter / Kelp / Immune / Curse), which is the strongest available evidence that the two systems are
describing the same mechanics under different names.

**This is identity-mapping work, and identity is the one thing an LLM is permitted to author here.** The
recovered names are Chinese labels that must be mapped onto the repo's closed atom and channel
vocabularies; the repo's standing rule (`anchor/schema.py:69`, `innate_picker/derive.py:7-9`) is that a
model may author the label and never the magnitude. Mapping 4,186 members onto a closed vocabulary is
exactly that shape. Nothing in this capture authorises a model to emit a number.

---

## What this does not settle

The mine says the data **exists and is reachable**. It does not say what the bake should do with it —
whether observed hp replaces `pTheta × k`, informs it, or only validates it, is a balance decision that
belongs with `species-flavour-lawn` and the build favour pipeline
(`docs/architecture/empire-progression-ideal.md` §4a), not with this capture.

One caution carried forward from `AGENTS.md`: whatever consumes this must go through a generator. The
species corpus is generated output, so a stat that disagrees with the game is a generator or capture
defect, never a prompt to hand-edit `gk-data/packs/fusion/data/generated/creatures/*.json`.
