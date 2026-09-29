# Spec: counter-doctrine

Status: **DRAFT for owner review, 2026-09-19. Spec phase; no build authorized.** Every `file:line` below was
opened in this session.

Module `counter-doctrine`, row 24 of the [npc-story-events map](../npc-story-events-map.md) (`:229`), wave 5. Depends
on `world-events-host` (the `Events` phase seam and its post-Step pass), `story-ledger`, `scene-script-loader` and
`character-registry`. Consumed, as an **input**, by world-map-program's faction policy (filed ask; map `:317`).
Owner ruling **R13** (`npc-story-events-ideal.md` §10); draft decision row **NS6** (`npc-story-events-map.md:403`);
gate **G6** (`:301`). Session record: `tasks/sessions/narrative-programs-spec2-20260919.json`.

## Objective

The antagonist answers the player's **whole war**, never an individual encounter (R13). Per world:

1. **The reading** — the aggregate of the player's strategy **as the Rotwright's faction observed it** (Owner ruling
   2026-09-20 (round 5), R18): the element share of the creatures the player fields, the posture of the player's
   legions, the sector kinds the player takes — each counted only where his faction saw it;
2. **The study bar** — advanced each End Turn in the `Events` phase while one lean persists, visible to the player;
3. **The doctrine** — adopted from a closed, reviewed vocabulary when the bar fills, for a stated window, changing
   **what** the Rotwright's faction fields (species drawn, element mix, order weights) and **never how strong**;
4. **The voice** — a short scene through `scene.play`, reacting to the strategy;
5. **The counter-play** — change strategy to stall the study, keep a lean out of his sight (R18), or raid a study site
   at an `Anomaly` or `Vault` to set it back.

Plus the **registry rows and guard tests** for the six anti-Nemesis rules.

Success looks like (G6): with the game closed, a fixture world where the player fields mostly fire creatures for
several turns fills the study bar, adopts the fire-countering doctrine, changes the Rotwright's species and element
draws and order weights, and changes no magnitude; switching away from fire stops the bar; a won raid sets it back;
all six guards pass.

## Locked anchors

- **R13 and the six rules** (ideal §6.12, `npc-story-events-ideal.md`; map principle 17, `:127-130`): no enemy
  grows from meeting the player; no enemy hierarchy; no enemy remembers the player personally; no enemy base built from
  an enemy's traits; no sharing of enemy data between players; warlords grow by world rules only. *"A design choice,
  not legal advice; a counsel review precedes a commercial release"* (map locked assumption 7, `:150-152`).
- **The five parts and their bases** (ideal §6.12 table, `:572-579`), the loop page's *"Enemy counter-development
  (Vision): if you lean fire, the war grows fire-hard; if you lean summons, anti-summon shows up. Not 'enemy level =
  Dave's level.'"* (`docs/guide/the-loops.md:96`).
- **Never how strong**: *"magnitudes still read `P(Θ)` and contests `Θ`"* (ideal §6.12, `:576`; map principle 5).
- **The doctrine is an input to world-map's faction policy; this program never writes a doctrine into
  `FrontierRulesPolicy`** (map ownership table, `:317`). Policies are pure in `(belief, seed)`
  (`gk-core/src/FusionRpg.Core/World/Ai/IFactionPolicy.cs:29-40`); `FrontierRulesPolicy` reads its weights from world AI tuning
  (`gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs:19-46`); a raised legion's species is the sector's climate element
  (`RaiseResolver.SpeciesFor`, `gk-core/src/FusionRpg.Core/World/Growth/RaiseResolver.cs:144-170`).
- **Faction state is hashed**: `WorldFaction` carries per-mille modifiers *"hashed, replayed"*
  (`gk-core/src/FusionRpg.Core/World/WorldState.cs:70-95`), written by `WorldCanonical` (`gk-core/src/FusionRpg.Core/World/WorldCanonical.cs:18`).
- **The doctrine id list is this module's closed, reviewed vocabulary**; `narrative-vocabulary` ships its file shape
  (`gk-data/packs/fusion/data/seed/narrative/_registry/doctrines.v1.json` (new)) and an empty catalog (`spec-narrative-vocabulary.md` §3).
- **Every rule has a registry row** (DESIGN-GATE §5 last box); rules 1–3 are already guarded by `character-registry`
  (`spec-character-registry.md` §5: `ns6-no-enemy-growth`, `ns6-no-enemy-memory`, `ns6-no-enemy-hierarchy`).

## Design

### 1. The reading — aggregates of what his faction observed

Owner ruling 2026-09-20 (round 5): **R18 — counter-doctrine is fog-correct.** The Rotwright reads **only what his
faction observed**: battles his faction took part in or saw, and sectors inside his faction's observation. A lean the
player keeps out of his sight is not studied. This replaces the round-1 "omniscient over committed state" world rule
(struck below).

`DoctrineReading.Of(WorldState world, IReadOnlyList<TurnReportEntry> turnBattles, string antagonistFactionId,
string playerFactionId)` (new, Core, pure) reads two observation sources and nothing else — never a battle **outcome**,
an enemy entity's identity or history, or a character:

1. **His faction's observation record.** The turn engine writes each faction's observation in its `Intel` phase, the
   **last** phase of the turn (`gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:150-156`, `:207`; `Observe` at `:384-403`,
   through `IntelRecorder.Observe`, `gk-core/src/FusionRpg.Core/World/Intel/IntelRecorder.cs:23-62`) into
   `WorldState.Intel` (`gk-core/src/FusionRpg.Core/World/WorldState.cs:353`), one `FactionIntel` per faction holding an
   `IntelSnapshot` per sector it has seen (`gk-core/src/FusionRpg.Core/World/Intel/FactionIntel.cs:89-156`). Because the study
   step runs in `Events`, before this turn's `Intel`, the **latest observation** is the one stamped
   `LastSeenTurn == turn − 1` — what he saw as the last turn ended. Record then drain: one turn late is correct.
2. **This turn's battles he took part in or saw.** `RunEvents` receives this turn's report (`spec-world-events-host.md`
   §1), whose `battle` entries carry the battle id and location sector (`gk-core/src/FusionRpg.Core/World/Turn/BattleReporting.cs:79-80`).
   The battle id names both sides' entities (`BattleKinds.IdFor`, `gk-core/src/FusionRpg.Core/World/Turn/BattleSeam.cs:29-30`).
   A battle counts when one side is an entity his faction owns (**took part**), or when its sector was in his latest
   observation (**saw**). A battle is a sighting, nothing more: its winner is never read (R13 rules 1 and 3).

| Lean key | Share (per-mille) | Counted over (the **observed** set only) |
|---|---|---|
| `element:{id}` (6, one per element) | observed player legion members whose species' primary element is `{id}`, over all observed player legion members | player-owned forces recorded **`Exact`** in his latest observation — he stood on the ground and counted (`IntelRecorder.cs:155`) — plus player entities on either side of a battle that counts. Members from `WorldEntity.Members` (`WorldState.cs:321`), species element from `CreatureSpeciesCatalog` |
| `posture:hold` | observed player legions in `hold` stance, over observed player legions | the same force set; `WorldEntity.Stance` (`WorldState.cs:312`) |
| `ground:{slotKind}` | observed player-held sectors holding that slot kind, over observed player-held sectors | sectors in his latest observation whose snapshot names the player as owner (`IntelSnapshot.OwnerFactionId`), slot kinds from the snapshot's `Slots` (`RememberedSlot.SlotTypeId`; slots are recorded on a full survey only, `IntelRecorder.cs:110-125`) |

**Why `Exact` and not a glimpse.** A glimpse from next door records a force as a strength band only
(`SectorSight.Glimpse`, `gk-core/src/FusionRpg.Core/World/Intel/Visibility.cs:11-12`; `RememberedForce.Exact`,
`FactionIntel.cs:37`) — he saw that something is there, not what it is made of — so a glimpsed force adds nothing
to an element or posture share. **Members are read from the entity as it stands**: `RememberedForce` carries no species
(`FactionIntel.cs:30-49`), and between his observation and this turn's `Events` phase a legion's roster is changed only by
this turn's earlier phases (fights, supply losses), never by a new raise, which settles in `Snapshot` after `Events`
(`TurnEngine.cs:428`) — so reading the live members of a force he counted is the smallest faithful read; adding a species
roster to intel would be a world-map intel change this module does not need.

A **lean** is the key with the highest share, if that share is at least `doctrine.leanThresholdMilli` and strictly
above every other key's; otherwise there is no lean this turn. **An empty observed set is no lean** (a zero
denominator reads as nothing seen, never as a share). The reading is recomputed every turn — it holds no memory of its
own — so the player's war is judged on what he **sees** of it, turn by turn.

~~Audit 2026-09-19: the reading is **omniscient over committed state**, not fog-limited — it reads every player legion,
including ones the antagonist's intel has not seen. That is a world rule … Whether the reading should instead be
fog-limited (hiding a lean as counter-play) is filed on world-map-program's review of this module.~~ Owner ruling
2026-09-20 (round 5): the reading is fog-limited (above), and hiding a lean is now **counter-play**: fight him where he
cannot see your fire, and the study stalls. The **consumer** side was already belief-bound and is unchanged:
`FrontierRulesPolicy` reads `IWorldView` and nothing else (`gk-core/src/FusionRpg.Core/World/Ai/IFactionPolicy.cs:24-27`), so
the adopted doctrine reaches it as the antagonist's **own** faction record exposed through `IWorldView` (§3), never as
a `WorldState` read. Both halves of the doctrine now see only what the antagonist believes.

Deploy modes and action tags (named in ideal §6.12) are not in world state today; they join as further lean keys when
a world battle report carrying them is persisted (a reading source added under review, not a design change).

### 2. The study bar — hashed faction state

The study is state the Rotwright's policy will read, so it lives where the engine can replay it: a new hashed field on
the antagonist's `WorldFaction` (a world-map schema change, reviewed jointly):

```csharp
public sealed record DoctrineState
{
    public string? StudyingLean { get; init; }           // the lean being studied, or null
    public long StudyMilli { get; init; }                // 0..1000: a progress ratio (bounded, structural)
    public string? ActiveDoctrineId { get; init; }        // a DoctrinesCatalog id, or null
    public int ActiveUntilTurn { get; init; }             // the doctrine's window end (inclusive)
    public int CooldownUntilTurn { get; init; }           // no new study completes before this turn
}
```

Each End Turn, in the `Events` phase (through `world-events-host`'s `IWorldStoryHost` seam, after the calendar roll):

```text
lean = DoctrineReading.Of(world, player).Lean
if lean is null or lean != StudyingLean:  StudyingLean = lean; StudyMilli = 0          # a changed strategy restarts the study
else:                                     StudyMilli = min(1000, StudyMilli + doctrine.studyRatePerTurnMilli)
if StudyMilli == 1000 and ActiveDoctrineId is null and turn >= CooldownUntilTurn:
    ActiveDoctrineId  = DoctrinesCatalog.Countering(lean)
    ActiveUntilTurn   = turn + doctrine.windowTurns
    CooldownUntilTurn = ActiveUntilTurn + doctrine.cooldownTurns
    StudyMilli = 0; StudyingLean = null
if ActiveDoctrineId is not null and turn > ActiveUntilTurn: ActiveDoctrineId = null
```

- The `min(1000, …)` bounds a **progress ratio**, not a magnitude, and says so in a comment (map principle 7).
- Audit 2026-09-19 — **no encounter moves the bar up** (R13 rule 1, made explicit): the only inputs to the study are
  the reading (an aggregate) and `doctrine.setback` (a player win lowers it). No battle outcome, won or lost by
  either side, and no storylet consequence can raise `StudyMilli` or adopt a doctrine. A lost raid changes nothing.
  Owner ruling 2026-09-20 (round 5): under R18 a battle his faction fought or saw is a **sighting** of the player's
  forces in it (§1), counted exactly as seeing the same forces on watched ground would count; its winner, and which of
  his entities fought, are never read, so the rule above still holds: winning or losing moves nothing.
- Audit 2026-09-19 — **dormant worlds** (Owner ruling 2026-09-19 (round 4)): the study runs only in a full `Step`'s
  `Events` phase. A hibernating or idle world is advanced by world-continuity's `coarse-step`, which runs no narrative
  phase, so the doctrine state is frozen while the world is dormant and a fallen world keeps it as read-only history.
- **Restart on change** is the "slow the study by changing strategy" counter-play: holding a lean is what lets the
  enemy learn it.
- Report entries (typed, fog-free because they are about the player's own war): `doctrine.studying`
  (`Detail = {lean}:{studyMilli}`), `doctrine.adopted` (`{doctrineId}:{untilTurn}`), `doctrine.ended`, each
  `Audience = playerFactionId`. Three new `TurnReportKinds` members with playback rows filed on world-stage's
  `world-playback` (the same rule as `spec-world-events-host.md` §5).

### 3. The doctrine — what the faction fields, never how strong

`gk-data/packs/fusion/data/seed/narrative/_registry/doctrines.v1.json` (new) (authored, reviewed; the vocabulary is closed):

| Doctrine id | Counters | Changes (inputs to world-map's policy and species draw) |
|---|---|---|
| `ward.{element}` (6) | `element:{element}` | **species draw**: raised and spawned zombie-side species biased to elements the ring says resist `{element}` (`ElementRingMatrix.GetRelation`, `gk-core/src/FusionRpg.Core/Combat/Element/ElementRingMatrix.cs:20`); **element mix** of legions |
| `siegecraft` | `posture:hold` | **order weights**: assault and siege orders weighted up against held, stationary positions |
| `raiders` | `ground:market`, `ground:vault` | **order weights**: raids on economic slots weighted up |

A doctrine row may contain only these effect keys: `speciesElementBiasMilli.{element}`, `orderWeightMilli.{orderKind}`.
**No key can name a magnitude** (hp, attack, level, damage, defense, rarity rung, count of units): the catalog loader
refuses any other key (`doctrine.magnitude-key`), which is the guard for "never how strong". Magnitudes of every
Rotwright unit still come from `P(Θ)` and contests from `Θ`, unchanged.

Audit 2026-09-19 — **a species draw can smuggle strength.** A species carries a threat rung whose `thetaOffset` is
added into `Θ` before `P(Θ)` (`docs/architecture/power/ssot-power-scale.md` §5.3, `thetaOffset` row), and species
differ in base rarity. An element bias that re-weighted across rungs would make the doctrine field *stronger* units,
not only *different* ones. So `speciesElementBiasMilli` re-weights only **within the candidate set the undoctrined
draw would use at the same threat rung and rarity** — it changes which element fills the slot, never the rung, the
rarity or the count. The consumer ask on world-map-program carries this constraint, and the test is §Testing's
"never how strong". A doctrine also biases **new** draws only: it never rewrites the members of an existing entity,
warlords included (R13 rule 6).

**Consumption is world-map's.** This module exposes `DoctrineView.For(world, factionId)` (pure) returning the active
doctrine's biases; the policy-side read goes through the faction's own record on `IWorldView` (Audit 2026-09-19, §1),
so `DoctrineView` is the engine-side and test-side reader, not a second input channel for a policy. The filed asks on world-map-program: `FrontierRulesPolicy.Decide` multiplies its order weights by
`orderWeightMilli` when a doctrine is active; `RaiseResolver.SpeciesFor` and the wild spawn draw weight candidate
species by `speciesElementBiasMilli`. Until those land, a doctrine is adopted, announced and visible, and changes
nothing in the field — an inert wiring gap with a named owner, not a claim that it works.

### 4. The voice

On `doctrine.adopted`, the post-Step pass (`spec-world-events-host.md` §6) appends `flag.set scene.due.doctrine.{doctrineId}`
(`spec-outcome-routing.md` §5): the Rotwright's short scene plays at the next Sanctum return
(`spec-sanctum-hub-host.md` §3), or as a world-hosted spine beat where the spine frame places one
(`spec-spine-progress.md` §3). Its lines are keyed by **doctrine and lean**, never by an encounter: the scene script's
eligibility may read the lean and the doctrine, and the scene-script loader refuses a doctrine scene whose eligibility
names a battle, a character fact about the antagonist or a warlord (`doctrine.scene-personal`, added to
`scene-script-loader`'s validation, filed) — R13 rule 3 at the content boundary.

### 5. The counter-play — raiding a study site

(Owner ruling 2026-09-20 (round 6): R21 — anomaly study sites exist only in new worlds, placed by `world-anomaly-sites`, `spec-world-anomaly-sites.md`; no template places a vault yet.) While `StudyMilli > 0` or a doctrine is active, storylets on `world.anomaly` and `world.vault` whose eligibility reads
the study (the `DoctrineStudying` leaf, `spec-narrative-predicates.md` §1; seed condition `doctrine-studying` in the storylet's `eligibility`, `narrative-seed/spec-storylet-vocab.md` §3.4 — Alignment 2026-09-20) may offer a raid: a `fight` choice (a guard
battle at the site, `spec-choice-resolution.md` §6) or an `interact`/`persuade` choice. A **won** raid (or a
successful contest) carries the consequence `doctrine.setback`, applied **in the engine** during `event.choose`
resolution, because it changes hashed state: `StudyMilli = max(0, StudyMilli − doctrine.raidSetbackMilli)`, or — with a
doctrine active — `ActiveUntilTurn = max(turn, ActiveUntilTurn − doctrine.raidShortenTurns)`. `doctrine.setback` is a
consequence kind in narrative-seed's vocabulary (`narrative-seed/spec-storylet-vocab.md` §3.5, Alignment 2026-09-20: added there); it is legal only on `world.*` hosts (preflight).

### 6. Tunables

**Declared in `narrative.v1.json` at wave 0 (plan §4 D4; current version `v2`)**, not added in this module's build
change (every key required; starting values by principle and the
ideal's prior art, §7 of the ideal and §4.1 *Stellaris Situations*):

| Key | Unit | Starting value and reason |
|---|---|---|
| `doctrine.leanThresholdMilli` | per-mille | 400: with six elements, a uniform war is ~167‰ each; 400‰ is a clear lean (2.4× uniform) that a mixed roster does not hit by accident |
| `doctrine.studyRatePerTurnMilli` | per-mille per turn | 125: eight turns of a held lean fill the bar — about one threat cycle (~7 turns, ideal §7) plus one turn to see it coming |
| `doctrine.windowTurns` | turns | 10: long enough to force a rebuild, short enough that the rebuild pays off |
| `doctrine.cooldownTurns` | turns | 10: the next doctrine cannot land while the player is still answering the last one |
| `doctrine.raidSetbackMilli` | per-mille | 375: a raid undoes three turns of study |
| `doctrine.raidShortenTurns` | turns | 3 |

### 7. The six rules — guards and registry rows

| Rule | Guard | Registry row (`gk-core/scripts/enforcement-registry.v1.json`) |
|---|---|---|
| 1. No enemy grows from meeting you | `character-registry`'s source scan, plus `DoctrineMagnitudeKeyTests`: the doctrine catalog refuses any magnitude key; `DoctrineSameRungTests` (Audit 2026-09-19): a doctrined species draw never moves threat rung or rarity | `ns6-no-enemy-growth` (character-registry), `ns6-doctrine-no-magnitude` (new), `ns6-doctrine-same-rung` (new, proposed) |
| 2. No enemy hierarchy | `character-registry`'s type-name scan | `ns6-no-enemy-hierarchy` (character-registry) |
| 3. No enemy remembers you personally | `character-registry`'s ledger refusal; `DoctrineReadingAggregateTests`: `DoctrineReading.Of` takes only `WorldState`, this turn's battle entries and two faction ids (reflection over its signature); its output is identical for two worlds that differ only in battle **outcomes** or in **which** antagonist entity fought (Owner ruling 2026-09-20 (round 5): was "only in battle history" — under R18 a battle he saw is a sighting, never a memory), and identical to a world where he saw the same player forces without a battle | `ns6-no-enemy-memory` (character-registry), `ns6-reading-aggregate-only` (new) |
| 4. No enemy base built from an enemy's traits | `NarrativeNoTraitBaseTests`: no type under `gk-core/src/FusionRpg.Core/Narrative/**` references structure, district-layout or siege-construction types | `ns6-no-trait-base` (new) |
| 5. No sharing of enemy data between players | `NarrativeNoNetworkTests`: no file under `gk-core/src/FusionRpg.Core/Narrative/**` or `gk-core/src/FusionRpg.Server/Narrative/**` references `HttpClient`, sockets or an upload API; `narrative-readings` is local-only | `ns6-no-enemy-data-sharing` (new) |
| 6. Warlords grow by world rules only | `NarrativeNoWarlordWriteTests`: no narrative code writes a `WorldEntity` of kind `Warlord` (level, members, lairs); the doctrine state lives on the faction, not on an entity | `ns6-warlord-world-rules-only` (new) |

The scans run in `gk-core/tests/FusionRpg.Guard.Tests/` beside `character-registry`'s, and each row lands in the same change as
its guard.

## Data shapes

- `WorldFaction.Doctrine : DoctrineState?` (hashed through `WorldCanonical`; null for every faction but the
  antagonist's and for every world before this module) — a world-map schema change, reviewed jointly.
- `gk-data/packs/fusion/data/seed/narrative/_registry/doctrines.v1.json` (new) — the closed doctrine vocabulary (authored).
- Three `TurnReportKinds` members; tunables in §6.

## Numeric types

| Quantity | Type | Why |
|---|---|---|
| shares, `StudyMilli`, thresholds, biases | `long` per-mille, `checked` | ratios computed from counts; the product before the divide stays in range (divide by 1000 last) |
| member and sector counts | `long` | a large empire's counts are unbounded in principle |
| turns | `int` | `TurnEngine`'s own turn type |

## SOLID notes

- **S:** reading, study and adoption are this module's; consumption is world-map's policy; voice is the scene path.
- **O:** a new doctrine is a catalog row; a new lean key is a reading row.
- **L:** a world with no antagonist doctrine state behaves exactly as before (`Doctrine` null, no study entries).
- **D:** world-map depends on `DoctrineView`, a pure read of hashed state, never on narrative internals.
- No recurring antagonist, no per-enemy memory, no second policy.

## Commands

```powershell
.\scripts\verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/Narrative/Doctrine/DoctrineReading.cs','src/FusionRpg.Core/Narrative/Doctrine/DoctrineStudy.cs','gk-core/src/FusionRpg.Core/World/WorldState.cs','gk-core/src/FusionRpg.Core/World/WorldCanonical.cs','tests/FusionRpg.Core.Tests/Narrative/Doctrine/DoctrineTests.cs','tests/FusionRpg.Guard.Tests/NarrativeAntiNemesisTests.cs') -Session <session-id>
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~Narrative.Doctrine|FullyQualifiedName~World"
dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~NarrativeAntiNemesis|FullyQualifiedName~NarrativeNoEnemy"
```

The change touches hashed world state, so the build task runs the full suite once at its end and re-blesses any
golden only under world-map-program review.

## Structure

```
gk-core/src/FusionRpg.Core/Narrative/Doctrine/DoctrineReading.cs      (new: aggregate reading, pure)
src/FusionRpg.Core/Narrative/Doctrine/DoctrineStudy.cs        (new: per-turn study update, adoption, setback)
gk-core/src/FusionRpg.Core/Narrative/Doctrine/DoctrinesCatalog.cs     (new: loader refusing magnitude keys)
gk-core/src/FusionRpg.Core/Narrative/Doctrine/DoctrineView.cs         (new: what world-map's policy reads)
src/FusionRpg.Core/Narrative/Hosts/WorldStoryPhase.cs         (edited: study step, setback consequence)
gk-core/src/FusionRpg.Core/World/WorldState.cs                        (edited: WorldFaction.Doctrine)
gk-core/src/FusionRpg.Core/World/WorldCanonical.cs                    (edited: hash the doctrine state)
gk-core/src/FusionRpg.Core/World/Turn/TurnReport.cs                   (edited: three doctrine kinds)
gk-data/packs/fusion/data/seed/narrative/_registry/doctrines.v1.json               (new)
tests/FusionRpg.Core.Tests/Narrative/Doctrine/DoctrineTests.cs          (new)
tests/FusionRpg.Guard.Tests/NarrativeAntiNemesisTests.cs                (new: rules 4-6 scans, magnitude keys, aggregate-only)
gk-core/scripts/enforcement-registry.v1.json                          (edited: five ns6 rows)
```

## Testing strategy

Game closed; fixture worlds; no store needed for Core (pure), in-memory store for the post-Step voice flag.

- **Lean:** a fixture world with 60% fire members, all counted by his intel, reads `element:fire`; 30% fire and 30%
  ice reads no lean (not strictly above).
- **Fog-correct (Owner ruling 2026-09-20 (round 5), R18):** a fire lean the player keeps out of his sight — every fire
  legion on ground his latest observation does not hold at `Exact`, and in no battle he fought or saw — reads no
  lean and does **not** advance the study bar over eight turns; the same lean on ground he observes does. A force he
  only glimpsed adds nothing. A battle his faction fought against the fire legion out of his sight makes it count.
  Nothing observed reads no lean (no zero-denominator share).
- **Study fills and resets:** eight turns of a held fire lean fill the bar; switching to ice on turn 5 resets it (Owner ruling 2026-09-20 (round 5) pass: `water` is not one of the six elements, `gk-core/src/FusionRpg.Core/Stats/Derived/ActorElementTypes.cs:3-11`; the Lean test above was corrected the same way); no
  lean holds it at zero.
- **Adoption:** a full bar adopts `ward.fire`, sets the window and cooldown, reports `doctrine.adopted`; no second
  doctrine lands during the cooldown.
- **Never how strong (G6):** with `ward.fire` active, `DoctrineView` exposes only element biases and order weights; a
  catalog row with an `hp`/`attack`/`level` key fails load; for the **same species and `Θ`**, every fixture Rotwright
  unit's magnitude is identical with and without the doctrine (the magnitude path never reads the doctrine); and over a
  fixed seed list the doctrined draw's threat-rung and rarity histogram equals the undoctrined draw's (Audit
  2026-09-19: a species change must not be a strength change).
- **No encounter raises the study:** a fixture turn with a lost player battle against the antagonist and one with a
  won one produce the same `StudyMilli` as a turn with no battle (R13 rule 1).
- **Dormant:** a fixture world that hibernates for N turns keeps its `DoctrineState` byte-identical until it is active
  again (Owner ruling 2026-09-19 (round 4)).
- **Setback:** a won raid lowers `StudyMilli` by the tuned amount, never below 0; a lost raid changes nothing.
- **Deterministic and hashed:** the same command log replays to the same `DoctrineState` and state hash; a world
  without the antagonist's doctrine state hashes as before (goldens byte-identical with the field null).
- **Aggregate only:** two fixture turns identical except for battle winners, or for which antagonist entity fought,
  produce identical readings (Owner ruling 2026-09-20 (round 5): battles are sightings, never outcomes).
- **Voice is strategic:** adoption writes one `scene.due.doctrine.{id}` flag; a doctrine scene fixture naming an
  encounter fails the loader.
- **Six guards:** each scan in §7 fails on a probe source string and passes on the tree.
- **No population:** fixtures only; the doctrine list is a declared closed vocabulary.

## Success criteria

1. A sustained lean advances a visible study bar; a changed strategy resets it; a raid sets it back. 2. A doctrine
changes species and element draws and order weights only — never a magnitude — proven by the catalog guard and a
magnitude-equality test. 3. The voice reacts to strategy, never to an encounter. 4. The six anti-Nemesis rules each
have a guard and a registry row. 5. The doctrine is consumed by world-map's policy as an input it owns. (G6.)

## Boundaries

- **Always:** read aggregates of what the antagonist's faction observed (Owner ruling 2026-09-20 (round 5), R18: was
  "of committed state"); hash the study; route consumption through world-map's policy.
- **Ask first (world-map-program):** the `WorldFaction.Doctrine` field, the policy and species-draw consumption, any
  golden re-bless.
- **Never:** a per-enemy memory, rank or growth; a magnitude key in a doctrine; write a doctrine into
  `FrontierRulesPolicy` from here; upload or share a reading.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `DoctrineView.For(world, factionId)` | world-map-program: `FrontierRulesPolicy`, `RaiseResolver.SpeciesFor`, wild spawn draw (filed asks) |
| `doctrine.*` report kinds | world-stage `world-playback` (rows filed), `narrative-readings` |
| `scene.due.doctrine.*` flags | `sanctum-hub-host`, `spine-progress` |
| `DoctrineStudying` leaf input (Alignment 2026-09-20: added, `spec-narrative-predicates.md` §1) | `narrative-predicates` |

## Contradictions found (report; not fixed here)

1. **Study state as a hashed faction field versus "the story ledger" in the ideal.** Ideal §6.12's table bases the study
   on *"the `Events` phase of the turn engine, the story ledger"* (`npc-story-events-ideal.md` §6.12, study row). The study changes
   what the antagonist's policy decides, and policies are pure in world belief and seed (`IFactionPolicy.cs:34-39`), so
   the state must be replayable world state, not a ledger fact the engine cannot read. The ledger still records the
   voice (scene flags) and readings; the bar itself is faction state. Reconciled 2026-09-19: ideal §6.12's study row
   now names the hashed `WorldFaction` field.
2. **"Summons" and "action tags" leans have no world-state source.** Ideal §6.12 names deploy modes and action tags in
   the reading; world state today carries neither. v1 ships the three lean families above and names the missing
   sources.

## Open questions

None for the owner. Starting values are decided by principle in §6; the counsel review before a commercial release is a
release gate already stated by R13, not a spec question.

## Design-gate checklist

```
[x] Subsystems: world map (faction state, policy input, species draw), AI (consumer, filed), elements (ring reader),
    power (magnitudes untouched), scenes, R13 guards.
[x] Session boundary recorded (narrative-programs-spec2-20260919).
[x] Read this session: map row 24, G6, principle 17, NS6, ownership table; ideal §6.12, §7, §10 R13; the-loops.md :96;
    DESIGN-GATE §1 World map, Stats/Actor rows, §2, §5; sibling specs narrative-vocabulary, character-registry,
    world-events-host, outcome-routing; code: IFactionPolicy, FrontierRulesPolicy, FactionPolicies, RaiseResolver,
    WorldState (faction, entity stance and members), WorldCanonical, ElementRingMatrix, TurnReport.
[x] Every claim cites file:line.
[x] Goldens: byte-identical with the field null is a test; re-bless only under world-map review.
[x] No population pinned.
[x] No cache; the reading is recomputed each turn.
[x] Order: a changed lean restarts the study regardless of which element came first (tested both ways).
[x] Actor numbers: none; a magnitude-equality test proves it.
[x] No parallel path: one policy (world-map's), one scene path, one storylet engine.
[x] Registry rows: ns6-doctrine-no-magnitude, ns6-reading-aggregate-only, ns6-no-trait-base, ns6-no-enemy-data-sharing,
    ns6-warlord-world-rules-only (plus character-registry's three).
```

## Standards audit (2026-09-19)

Independent adversarial review against DESIGN-GATE §1 (World map, Power, Battle, Caps, Tunables, Standalone rows),
§2 (1, 2, 9, 12, 13, 14, 15), §3, §5; `ssot-power-scale.md` §2/§5; `IFactionPolicy.cs`; ideal §6.12 and **R13's six
rules** (each checked); round-3 and round-4 owner rulings.

| # | Severity | Finding | Status |
|---|---|---|---|
| 1 | HIGH | "Never how strong" was guarded only against magnitude **keys**. An element bias over species can pick a higher threat rung (`thetaOffset` enters `Θ`) or rarity, so the doctrine could field stronger units without naming a magnitude. The G6 test ("every unit's magnitude identical") was also ill-defined, because a different species legitimately has different stats | **Fixed**: bias constrained to the same rung/rarity candidate set (§3); test restated per species and `Θ`, plus a rung/rarity histogram test; proposed guard row `ns6-doctrine-same-rung` |
| 2 | MEDIUM | Consumption named `DoctrineView.For(world, …)`, but a faction policy reads `IWorldView` and nothing else (`IFactionPolicy.cs:24-27`); a `WorldState` read from a policy would breach the policy contract | **Fixed** (§1, §3): the policy reads the faction's own record through `IWorldView` |
| 3 | MEDIUM | The reading is omniscient over committed state (reads legions the antagonist has not seen), unstated | ~~**Fixed** as a stated world rule (§1); fog-limited reading **deferred** to world-map-program review (it changes counter-play)~~ **Resolved — Owner ruling 2026-09-20 (round 5), R18:** the reading is fog-correct (§1), with tests (§Testing "Fog-correct") |
| 4 | MEDIUM | R13 rule 1 was implied, not stated: nothing said a battle outcome cannot raise the study | **Fixed** (§2 bullet, test) |
| 5 | LOW | R13 rule 6: doctrine could be read as rewriting an existing warlord's members | **Fixed** (§3: new draws only) |
| 6 | LOW | Round-4: doctrine behaviour while a world is dormant or fallen was unstated | **Fixed** (§2 bullet, test) |
| 7 | LOW | `ground:{Market}` did not match the reading's key grammar | **Fixed** (`ground:market`) |
| 8 | LOW | Ideal line citations had drifted (the ideal is being edited) | **Fixed**: cited by section |

R13 rule-by-rule: 1 — no encounter input (fixed #4); 2 — no ranks, the doctrine is faction state (holds); 3 — voice
keyed by strategy, loader refusal `doctrine.scene-personal` (holds); 4 — `ns6-no-trait-base` (holds); 5 —
`ns6-no-enemy-data-sharing` (holds); 6 — new draws only, warlord entities untouched (fixed #5).

**Deferred:** ~~fog-limited reading (#3) — world-map-program's call;~~ (resolved by R18, Owner ruling 2026-09-20 (round 5)) the three `TurnReportKinds` members and the
`WorldFaction.Doctrine` field stay joint-review asks. **Registry rows proposed** (not written — shared file):
`ns6-doctrine-same-rung` → `DoctrineSameRungTests`; the five rows in §7 stand.

## Owner ruling 2026-09-20 (round 5)

**R18 — counter-doctrine is fog-correct.** §1 now reads only what the Rotwright's faction observed: its latest `Intel`
record (forces counted `Exact`, player-held sectors in view) and this turn's battles it fought or saw, never a battle's
outcome. A lean kept out of his sight does not advance the study bar; one he observes does (§Testing). R13's six rules
are unchanged: battles are sightings, not memories (rule 3), and no outcome raises the bar (rule 1, §2). Hiding a lean
joins changing it and raiding a study site as counter-play. Checklist addition: `[x]` read `TurnEngine` (`Observe`,
phase order), `IntelRecorder`, `FactionIntel`, `Visibility`, `BattleSeam.IdFor`, `BattleReporting` this session.
