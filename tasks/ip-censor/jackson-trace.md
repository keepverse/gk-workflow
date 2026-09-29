# T17 — every entry point and player-visible surface of the `Jackson*` family

**Program:** `ip-censor` · **Task:** T17 · **Lane:** `ip-censor-2` · **Date:** 2026-09-23
**Evidence:** every citation below was read in this session at the lane's head; the row's own
citations were re-measured and three of them had drifted (see §5).
**Route this trace feeds:** T18 (the authored rename map) → T19 (apply it, regenerate) → T19b (re-key
the species ids) → T22 (the owner admits the `real-person` row).

Measured blast radius: **74 tracked files carry a `jackson` token** (`git grep -Iil jackson | wc -l`),
of which **19 have it in their path** (`git ls-files | grep -i jackson`). The two numbers differ
because most carrying files reference an id, not their own name.

---

## 1. Where the real person's name enters our tree

There is exactly **one** place in the tracked tree where the person's full name appears in Latin
letters, and one where it appears in Chinese. Both are upstream, read-only captures.

| # | Site | What it holds | Evidence |
|---|---|---|---|
| E1 | `gk-data/packs/fusion/data/seed/creatures/_dump/almanac/zombie.json:134` | `flavorIntroduce` — "现在与**Michael Jackson**合作的流行乐《Just Brains》正在爆火。" | read |
| E2 | `gk-data/packs/fusion/data/seed/creatures/_dump/almanac/zombie.json:218` | `flavorIntroduce` — "你可以叫他**Michael Jackson**。" | read |
| E3 | `gk-data/packs/fusion/data/seed/creatures/_dump/almanac/zombie.json:217` | `flavorInfo` — "向传奇舞王**迈克尔·杰克逊**致敬！经典太空步入场。" (the Chinese transliteration, same entry) | read |
| E4 | `gk-data/packs/fusion/data/seed/creatures/_dump/almanac/zombie.json:225,1299,2528,2642,2927,3668,3820,3839,3858` | the nine host `typeName`s: `JacksonZombie`, `SandJackson`, `JacksonDriver`, `QuickJacksonZombie`, `UltimateJacksonDriver`, `JacksonDriverBoss`, `Jackson_a`, `Jackson_b`, `Jackson_c` | read |
| E5 | `gk-data/packs/fusion/data/seed/creatures/_dump/type-base-stats.json:4867,5245,5686,5728,5833,6106,…` | the same names, once as `typeName` and once inside `statsJson` | read |
| E6 | `gk-data/packs/fusion/data/seed/external-reference/almanac-enrichment/pvz-fusion-almanac-3.6.1.json:5247,5472,5677,5887,5892,5897,5957,5962,5967` | the English display names `Michael Zombie`, `Beach Michael Zombie`, `Michael Zomboni`, `Sergeant/Commander/General Michael Zombie`, `Plated/Armored/Colossus Michael Zomboni` — the **first name only**, no surname | read |
| E7 | same file, `:5474,5679,5959,5964,5969` + `:5774` | the `weaknesses` prose that names those display names ("spawns a Michael Zombie upon death") and `"name": "Jackson Worldwide"` at `:5772` | read |
| E8 | same file, 781 rows, keys `{name, side, typeClass}` | **`Michael Jackson` (the full name) does not appear in the export at all** | `python` field scan, 16 field-level hits, all `Michael …`/`Jackson Worldwide` |

**The dump is itself a committed capture, not the origin.** `gk-data/packs/fusion/data/seed/creatures/_dump/**` is emitted
by `gk-forge/tools/CreatureCorpusDump` from the store: `CorpusReader.cs:52` maps the almanac DTO to a dump row
and `:69-71` carries `Enrichment.{Qualities,UnlockCondition,TypeClass,WeaknessesText,DamageVsText,
Description,Source}` through; `DumpWriter.cs:51,70` writes them. So the game's own tables are the
origin, the dump is our snapshot of them, and **the dump is never hand-edited**.

## 2. Every derived artifact, classified

Classification vocabulary is the spec's: **player-visible name**, **player-visible prose**,
**identifier**. "Owned" is the column that decides T19's route.

### 2a. Player-visible **prose**

| Artifact | Evidence | Owned by |
|---|---|---|
| `gk-data/packs/fusion/data/seed/creatures/creature/zombie/epic.json:110` — `flavorIntroduce` carries E1 **verbatim** | read | `gk-forge/tools/CreatureCorpusEmit` (`Program.cs:79,110-115`) — **generator**, but see §6a: the guard cannot see it |
| `gk-data/packs/fusion/data/seed/creatures/species/**` briefs and motif/theme inputs | `family/extract.py:59-66` (name + flavorInfo + flavorIntroduce into the brief), `generate_motifs.py:41-46`, `generate_themes.py:86-96`, `dump_ctx.py:57` | seedsmith creature adapters — **generator** |
| `data/seed/creatures/_registry/themes.v{1,2}.json` motif labels `杰克逊` / `迈克尔` (`themes.v1.json:7450,7522-7523`) | read; the file carries per-row `model` + `promptVersion: "theme-enrich/1"` at `:1134-1135` | **generator-owned** (theme-enrich) |
| `gk-data/packs/fusion/data/seed/creatures/_generated/motif-assignments.json:4583,4627-4628` | read | seedsmith motif generator — **generator** |
| `gk-data/packs/fusion/data/seed/actions/_briefs/round-1.json` (20 hits, e.g. `:57081`), `round-2.json` (15), `_generated/role-lean.json` (3), `_rounds/round-1/accepted.json` (5) | read | seedsmith actions pipeline — **generator** |
| `gk-data/packs/fusion/data/seed/actions/species-innate.json`, `type-weights.json` | grep | seedsmith actions pipeline — **generator** |

### 2b. Player-visible **name**

**None carries the real person's name.** Every creature display name a player reads comes from the
host game's own `types` table: `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.AlmanacSeed.cs:474-486` selects
`type_name, display_name FROM types` and overrides the stored snapshot with it. The RPG writes no
name for these creatures. The corpus `name` fields are the game's Chinese names, and the derived
registries name the *motif/theme*, not the person, in their `displayName` (e.g.
`themes.v2.json`'s `"displayName": "究极剑仙杨桃"`).

**Corollary, and it is the important one for the release gate:** on today's shipped
`scope-policy.v1.json`, `michael`, `jackson` and `迈克尔`/`杰克逊` produce **zero enforced findings**
(measured: `git grep -Iic` over `docs/guide`, `gk-data/packs/fusion/data/seed/passive-tree`, `gk-data/packs/fusion/data/seed/commanders` → 0).
The real-person text sits under `gk-data/packs/fusion/data/seed/creatures/**`, which the classifier sends to its authored
`code-identifier` default (report-only). IC-4.2 is therefore closed by the map's own import-output
test, exactly as `ip-censor-map.md:132` says — **not** by the scan. See §6b for the open question.

### 2c. **Identifiers** (the compound `Jackson*` ids and everything derived from them)

| Artifact | Evidence | Owned by |
|---|---|---|
| `gk-data/packs/fusion/data/seed/creatures/species/_index.json:382-387,552,560,841` — `speciesId → file` map | read | seedsmith `anchor/emit.py` (`build_index`) — **generator** |
| the 7 species files carrying a `speciesId` — `species/zombie/undead.json:2342,3542`, `performer-undead.json:75`, `performer-zombie.json:169,256`, `undead-performer.json:73`, `motorized-undead.json:73`, `mechanical-undead.json:602`, `theatrical-construct.json:76` | read | **generator**; each row carries `_provenance.dumpHash` + `gameTypeId` (e.g. `Jackson_a` → `gameTypeId: 307`) |
| the derived trait `moonwalking` (`performer-undead.json:80`) plus `family`, `posture`, `reason`, `_derived.family` | read | **generator** |
| `gk-data/packs/fusion/data/generated/creatures/<id>.json` — 9 files whose **filename** is the id (`JacksonZombie.json` …); the content is stat-only (`gameTypeId`, `magnitudes`, …), no name | read | `gk-forge/tools/CreatureSpeciesGen` (`Program.cs:15-16,61-62,133-136`) — **generator** |
| `gk-data/packs/fusion/data/generated/creatures/_species-build-plan.json`, `_fusion-recipes.json` | grep | `gk-forge/tools/CreatureBuildPlanGen`, fusion-recipe generator — **generator** |
| `gk-data/packs/fusion/data/seed/items/sets/*.json` — 9 sets (`jackson-a.json` … `ultimatejacksondriver.json`) whose ids/`nameKey`/`themeKey` embed the species id (`"id": "set.jacksonzombie-001"`, `"themeKey": "creature.jacksonzombie"`) and whose `_meta.batch` is `set-gen-jacksonzombie` | read | **generator** (`set-charm-gen`, `_meta.model` + `promptVersion` present) |
| `gk-data/packs/fusion/data/seed/items/charms/{econ,off-ctrl,surv-util}.json`, `materials/trophy-registry.json`, the two `set-charm-gen.ledger.json` | grep | **generator** |
| `gk-data/packs/fusion/data/seed/actions/_generated/family-map.json` (`"jackson_a": ["undead","zombie"]`), `_reports/coverage-round-*.json` | read | **generator** |
| `gk-data/packs/fusion/data/seed/creatures/_registry/motifs.v1.json:835,848` — the motif vocabulary verbs `杰克逊`, `迈克尔` | read; **no** provenance key in the file | **authored** registry (direct edit lawful) |
| `gk-core/tools/CombatSim/archetypes/creatures/JacksonZombie.json`, `gk-forge/tools/seedsmith/run_checkpoint8a_claude_propose.py`, `tools/seedsmith/.../_registry_snapshot/allocated_partitions.json` | grep | `code-identifier` — **code change**, never a content edit |
| `gk-core/tests/FusionRpg.Core.Tests/Creatures/CreatureRecipeCatalogTests.cs` | grep | `code-identifier` |
| `docs/research/game-meta/{datamodel,enums,index}.json`, `docs/research/pvz-engine-surface/…`, `docs/architecture/{creature-seed-map,action-corpus/spec-characteristic-pool,creature-seed/spec-fusion-recipe-generator}.md`, `tasks/**` | grep | report-only (`docs-prose-citation` / `deliberate-identity`) |

**The name alludes through the motif vocabulary, not the id.** The `杰克逊` motif is why the trait
`moonwalking` exists; `moonwalk`/`moonwalking` itself is an allusion to the person's signature move,
not a spelling of the name. The registry's `real-person` category is about *names*, so `moonwalking`
is **not** a mark alias today — the owner may widen the alias set (§7, decision D2).

## 3. Four tracked trees, four routes

| Tree | Written by | Provenance | T19's route |
|---|---|---|---|
| `gk-data/packs/fusion/data/seed/creatures/_dump/**` | `gk-forge/tools/CreatureCorpusDump` (from the store) | none in the file | read-only; regenerate only from a captured store |
| `gk-data/packs/fusion/data/seed/creatures/species/**` + `_index.json` | seedsmith `creatures/anchor/emit.py` | per-row `_provenance` (`dumpHash`, `promptVersions`) | generator + regenerate |
| `gk-data/packs/fusion/data/seed/creatures/creature/**` | `gk-forge/tools/CreatureCorpusEmit` | **`_meta` carries `partition` only** | regeneration needs a captured store; §6a |
| `gk-data/packs/fusion/data/generated/creatures/**` | `gk-forge/tools/CreatureSpeciesGen` (+ build-plan/fusion generators) | none in the file; `gk-data/packs/fusion/data/generated/` is in the guard's tree table with `^tools/` as its source | generator `--check` + regenerate |

## 4. T20's decision line: **skip, with a reason**

T20 asks whether any upstream name reaches a player **through the server import path**. Verified:

- The only server route for the export is `POST /api/almanac/seed/enrich`
  (`gk-core/src/FusionRpg.Server/Program.cs:1720-1742`), which calls
  `RpgStore.ImportAlmanacEnrichment` (`RpgStore.AlmanacSeedEnrichment.cs:36`).
- The export's `name` field is read **only as a match key**: the importer builds
  `byNormName` from `almanac_seed`'s own `type_name`/`display_name` (`:47-65`) and never stores the
  incoming name. The stored fields are `Qualities`, `UnlockCondition`, `TypeClass`, `WeaknessesText`,
  `DamageVsText`, `Description` (`:20-30`).
- Of those, only `weaknesses` contains the name, in 6 rows (`Michael Zombie`/`Michael Zomboni`).
  It reaches the committed dump (`CorpusReader.cs:69-71` → `DumpWriter.cs:51,70`) and stops there:
  the player-visible corpus fields are `name`/`flavorInfo`/`flavorIntroduce`, and no surface reads
  the dump's `enrichment` node (`git grep weaknessesText -- web/` → nothing; the almanac DTO is served
  only by the seed endpoints, which the web does not call).
- The name a player actually reads is the host game's `types.type_name`/`display_name`, injected by
  the game, not by this import.

**Decision: T20 is skipped** by its own default. The full name never passes through the server import
path, and the first-name-only prose it does pass is not player-visible. *Caveat, recorded:* the
`weaknesses` text does enter the committed dump, so if the owner ever decides the dump needs the map
too, T20's route is real — the importer's row construction is the seam.

## 5. The row's citations that had drifted (measured this session)

| Row said | At this head | Note |
|---|---|---|
| `_dump/almanac/zombie.json:134,218` | correct | the two `Michael Jackson` lines |
| `adapters/creatures/family/extract.py:61-65` | `:59-66` | the brief builder |
| `generate_motifs.py:45` | `:41-46` | motif inputs |
| `generate_themes.py:94` | `:86-96` | theme inputs; also `dump_ctx.py:57` reads `flavorInfo` |
| export `:5247,5677,5772` | `:5247,5677` are `Michael Zombie`/`Michael Zomboni`; `:5772` is **`Jackson Worldwide`**, a place/boss label, **not** the person | the export holds **no** full name |
| `gk-core/src/FusionRpg.Server/Program.cs:1423-1445` | **now the PvzActivity section**; the almanac seed enrich endpoint is `:1720-1742` | re-anchored |
| `RpgStore.AlmanacSeed.cs:474` | `:474-486` | the `types` naming read |
| `species/zombie/undead.json:2290` | `:2342` | `speciesId: "JacksonZombie"` |
| `performer-undead.json:75,80` | correct (`speciesId` at `:75`, `moonwalking` at `:80`) | |
| `species/_index.json:382-387` | correct | |
| "about 900 lines under `data/**`" (plan D7) | **74 files carry a token; 854 token occurrences under `gk-data/packs/fusion/data/seed/items`, `gk-data/packs/fusion/data/seed/actions`, `gk-data/packs/fusion/data/generated` alone** | the population is much wider than the nine species the row reasoned about |

## 6. Findings routed

### 6a. `gk-data/packs/fusion/data/seed/creatures/creature/**` is generator output the generated-seed guard cannot see

- `guard-generated-seed.py:66-67` lists `^gk-data/packs/fusion/data/seed/creatures/` with
  `Sources = @('^gk-forge/tools/seedsmith/seedsmith/adapters/creatures/')` — **`gk-forge/tools/CreatureCorpusEmit/` is
  not a listed source**, although `CreatureCorpusEmit/Program.cs:79` writes that subtree.
- The block only reports a file when `Test-HasGeneratorProvenance` (`:117-128`) finds
  `_meta.model` / `_meta.promptVersion` / `_meta.batch`. `creature/zombie/epic.json`'s `_meta` carries
  **`partition` only** (`CreatureCorpusEmit/Program.cs:110-115`), so the guard returns false.
- Together: a hand edit to `creature/zombie/epic.json:110` — the exact file that carries the
  real-person prose — passes both checks, while the file is regenerated output.

**Owning program: `ip-censor`** (its own T19 runs into this). Two candidate fixes, neither this
task's to take: add `^gk-forge/tools/CreatureCorpusEmit/` to that tree's `Sources`, and/or teach the guard the
`_meta.partition`-only shape. The same `_meta`-only defect is already recorded against
`guard-generated-seed.py` in T4's row (plan D8/§5), where `command.json` and the species rows use
`_provenance` shapes the guard also misses — this is a third instance of one cause.

### 6b. Open question for the owner/manager: is `gk-data/packs/fusion/data/seed/creatures/creature/**` a player surface?

The corpus fields `name` and `flavorIntroduce` are prose a player can read, but the shipped
`scope-policy.v1.json` sends `gk-data/packs/fusion/data/seed/creatures/**` to its `code-identifier` default, so every hit
there is report-only. That is why IC-4.2 never appears in the release-gate reading. Either answer is
defensible and both are authored-data changes:

- **Leave it** (today's state): IC-4.2 is proven by T19's import-output test, per `ip-censor-map.md:132`.
- **Make `gk-data/packs/fusion/data/seed/creatures/creature/**` a `player-prose` surface**: IC-4.2 becomes gate-visible —
  and so does every other generated name/flavor hit in that tree, which is why this must be the owner's
  call at T22 with the readings in hand, not a lane's.

Per `spec-registry.md` §Categories ("any disagreement becomes a scope-policy row change later
(authored data, reversible)"), this is deferred to T22 rather than decided here.

## 7. Owner decisions this trace puts to T22

| # | Decision | Proposal in the candidate file | Consequence if accepted |
|---|---|---|---|
| D1 | Admit a `real-person` group for the person | `michael-jackson`, aliases `michael-jackson`, `michael jackson`, `michael`, `remediation: upstream-imported`, scope left `null` for the owner | The map (T18) gets its row; T19's import-output test gets its done-when |
| D2 | Widen to `jackson` / `杰克逊` / `迈克尔`? | **not proposed** — `jackson` alone collides with the genre of derived keys (`creature.jackson_a`, `set.jacksonzombie-001`, `trophy.species.jackson_a.1`) and the Chinese spellings need their own scope under IC-6 | Report-only noise today; re-measure at T22 with the census |
| D3 | Replace the `杰克逊`/`迈克尔` **motif** vocabulary, or only the person's name? | The vocabulary is generator-owned (`themes.v*` per-row `promptVersion`) plus one authored registry (`motifs.v1.json`) | Changing it re-rolls motifs/themes/actions — a generator change with a corpus diff, not a JSON edit |
| D4 | `moonwalking` / `moonwalk-legend` (allusions, not names) | **not proposed** as aliases | Owner may add them; they would be new alias rows, not part of D1 |

An enforced finding with no owner is what CP3's audit calls a classifier defect. Nothing in this
trace produces one: with the current scope policy the whole family is report-only, and that is stated
rather than papered over.
