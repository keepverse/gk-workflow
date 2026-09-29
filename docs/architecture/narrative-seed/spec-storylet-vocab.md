# Spec: `storylet-vocab`

**Program:** [narrative-seed](../narrative-seed-map.md) · **Module id:** `storylet-vocab` · **Map row:** 5 · **Wave:** 1
**Depends on:** none · **Model calls:** none
**Status:** spec phase, 2026-09-19. Map approved by the owner 2026-09-19; no build authorized.
**Shared with the runtime:** `npc-story-events`' `narrative-vocabulary` reads these files from C#
(`npc-story-events-map.md` row 1); one file per vocabulary, read by both sides.

---

## Objective

Author the closed registries a storylet is built from — host kinds, choice kinds, choice patterns, the
condition vocabulary, consequence kinds, role requirement tags and role kinds — plus the model-facing
notes for the vocabularies a storylet borrows from existing registries. Every value carries a
**description and a negative clause**, because the model picks from these lists and the most common enum
error is a plausible neighbouring value (`docs/research/ai-native-generation/README.md` §3).

These lists turn *"what kind of decision is this?"* into a planner fact: the model never decides the
shape of a choice (map §2 principle 6). They are also the seed-side half of the widening
`party-dungeon/spec-event-deck.md` §6 left as *"a seed-contract widening — ask first"*
(`docs/architecture/party-dungeon/spec-event-deck.md` line 210); the owner approved it with the map.

**Done means:** eight registry files (Alignment 2026-09-20: `teaches.v1.json`, §3.8; ~~Owner ruling 2026-09-20 (round 5): `sector-climates.v1.json`, §3.9~~ Owner ruling 2026-09-20 (round 6): R20 retired that ninth file) and one notes file exist under
`gk-data/packs/fusion/data/seed/narrative/_registry/`, each loads through one reader, every join to an existing registry
closes, and the structural rules below are proven by tests.

---

## Design

### 1. Principles applied here

- **Read, never transcribe.** Vocabularies another registry already owns are referenced, not copied:
  storylet kinds, outcome ordinals and repeat scopes are `gk-data/packs/fusion/data/seed/dungeon/_registry/bands.v1.json`'s
  `eventKind`, `outcomeOrdinal` and `repeatScope` (`:45`, `:52`, `:56`); drop bands are
  `gk-data/packs/fusion/data/seed/items/_registry/bands.v1.json`'s `dropBand` (`:451`); supply tags are
  `gk-data/packs/fusion/data/seed/dungeon/_registry/override-tags.v1.json`; disposition bands are
  `gk-data/packs/fusion/data/seed/dungeon/_registry/disposition.v1.json` (the one relation ladder, R4); elements are the six of
  `gk-core/src/FusionRpg.Core/Stats/Derived/ActorElementTypes.cs:3-11`.
- **`none` where a model chooses.** A value list the model sees as a JSON Schema `enum` carries a `none`
  row whose description says what `none` means for that list. Lists only the planner uses (host kinds,
  choice kinds, patterns) reach the model as `const` and carry no `none`, the same rule the dungeon
  schema already follows (`gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/schema.py:71-76`).
- **No number is a balance value.** The only numbers in these files are structural counts (slots and
  outcomes per pattern) — a count is structure, not balance (`docs/architecture/item/seed-contract.md`
  §2.1).

### 2. Common file shape

```json
{
  "schemaVersion": 1,
  "registryVersion": 1,
  "<vocabulary>": {
    "<value>": { "description": "<what it is>", "negative": "<what it is not>", "...attributes": "..." }
  }
}
```

`description` and `negative` are separate keys so a test can prove every negative clause exists. Unknown
keys are refused; forward compatibility comes from `schemaVersion`.

### 3. The registries

**3.1 `host-kinds.v1.json` — places that can show a storylet.** Seeded from the Delve's existing kind-fit
rule (`docs/architecture/party-dungeon/spec-event-deck.md` line 92).

| Value | `place` | `roomKind` | `admits` (storylet kinds) | `climateNeutral` | `climateSource` · `climates` (Owner ruling 2026-09-20 (round 5), R19; Owner ruling 2026-09-20 (round 6), R20: world rows read the sector's own climate) |
|---|---|---|---|---|---|
| `delve.curio` | delve | curio | curio | no | `room` (the room's climate, today's path) |
| `delve.shrine` | delve | shrine | shrine | no | `room` |
| `delve.trap` | delve | trap | trap | no | `room` |
| `delve.merchant` | delve | merchant | bargain | yes | `none` |
| `delve.wild` | delve | wild | story | no | `room` |
| `delve.rest` | delve | rest | encounter-event | yes | `none` |
| `delve.unknown` | delve | unknown | all six | yes | `none` |
| `sanctum.hub` | homeworld | `none` | story | yes | `none` |
| `world.shrine` | world | `none` | shrine, story | ~~yes~~ no | ~~`sector-type` · `none`~~ `sector` · all seven |
| `world.anomaly` | world | `none` | curio, trap, encounter-event, story | ~~yes~~ no | ~~`sector-type` · *(empty: no sector type allows an `anomaly` slot today)*~~ `sector` · all seven |
| `world.tear` | world | `none` | encounter-event, trap | ~~yes~~ no | ~~`sector-type` · `air`, `fire`~~ `sector` · all seven |
| `world.vault` | world | `none` | curio, trap, story | ~~yes~~ no | ~~`sector-type` · `none`, `dark`~~ `sector` · all seven |
| `world.market` | world | `none` | bargain | ~~yes~~ no | ~~`sector-type` · `none`~~ `sector` · all seven |
| `world.wildland` | world | `none` | story, encounter-event | ~~yes~~ no | ~~`sector-type` · `none`, `earth`, `air`, `fire`, `dark`~~ `sector` · all seven |
| `world.petition` | world | `none` | story, bargain | ~~yes~~ no | ~~`sector-type` · `none`, `earth`, `air`, `fire`, `dark`~~ `sector` · all seven |
| `expedition.return` | expedition | `none` | story, curio | yes | `none` |

`roomKind` joins `gk-data/packs/fusion/data/seed/dungeon/_registry/room-kinds.v1.json`, and `climateNeutral` must equal that
row's own flag; a non-Delve row carries `roomKind: none` and no room-kind join. World, expedition and homeworld hosts are added as rows when their runtime defines them
(map §9); until then they do not exist and no cell is computed for them.

Alignment 2026-09-20: `sanctum.hub` is added because its runtime now defines it
(`npc-story-events/spec-narrative-vocabulary.md` §2, `spec-sanctum-hub-host.md`). A **hub conversation with
choices** is an ordinary storylet whose `hosts` include `sanctum.hub`, with one required role `speaker` (the
character at home the runtime binds, `spec-sanctum-hub-host.md` §3) and a talk-verb pattern that fits `story`
(`pattern.interact-leave`, `pattern.persuade-leave`, `pattern.threaten-leave`) — no new seed kind. The
**reaction to how the outing went** is not a storylet: it is the character's own homecoming line,
`character-vocab` §5's `return-*` contexts, which the runtime plays as a one-line scene. That is the smallest
change that meets ideal §6.6 ("one conversation per character per return, reacting to the outing") with the
two seed kinds that already exist. ~~The runtime's eight `world.*`/`expedition.return` host rows are still owed
here.~~ Alignment 2026-09-20: the eight rows are added above, one per host kind the runtime defines
(`npc-story-events/spec-narrative-vocabulary.md` §2): the six world slots (`gk-core/src/FusionRpg.Core/World/SlotTypeCatalog.cs:7-24`),
`world.petition` and `expedition.return`, which `spec-world-events-host.md`, `spec-petition-host.md` and
`spec-expedition-lead-host.md` read. `admits` is decided by the patterns each host needs: the study-site raids of
`spec-counter-doctrine.md` §5 need a `fight` pattern on `world.anomaly` and `world.vault` (`fight` patterns fit
`encounter-event`, `trap`, `story`, §3.3); a petition is a `quest.offer`/`offer:souls`/`leave` storylet
(`pattern.persuade-leave-offer` fits `bargain`, `story`); an expedition lead is auto-answered with no `fight` and no
`offer` (`spec-expedition-lead-host.md` §3, §5), which `interact`/`persuade` patterns on `story` and `curio` allow.
~~Every non-Delve row is **climate-neutral**: no world sector or expedition carries a climate the runtime passes to
selection today, so a storylet naming one of these hosts carries `climate: none` (§5 rule of `narrative-contract`); a
world climate is a reviewed change when world-map gives sectors one.~~ Owner ruling 2026-09-20 (round 5): **R19 — a
world storylet's climate is derived from the sector type.** The seven `world.*` rows are no longer climate-neutral:
their site climate is the sector type's row in the closed registry `sector-climates.v1.json` (§3.9), and `climates`
lists the climates each host can actually present — the registry's image over the sector types whose
`AllowedSlotTypes` hold that slot (`gk-core/src/FusionRpg.Core/World/SectorTypeCatalog.cs:55-102`; a petition can come from a
held sector of any type). `climates` is authored here because the planner cannot read C#; the runtime's
`narrative-vocabulary` join test proves it equals the image (`npc-story-events/spec-narrative-vocabulary.md` §1), so
it can never drift. A storylet's `climate` must be in `climates` for every world host it names; an empty `climates`
(`world.anomaly`) means the host fires nowhere today and the planner declares no cell for it. `sanctum.hub` stays
neutral (the homeworld is untouched ground). **Expedition hosts stay climate-neutral** because an expedition carries no
destination sector (`ExpeditionRow` holds a tier, a squad and a seed, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Expeditions.cs:10-12`);
if one ever does, `expedition.return` becomes `sector-type` over that sector through the same registry, a reviewed
change. The Delve keeps its own per-room climate (`climateSource: room`). `roomKind` is `none` on every non-Delve row.
Owner ruling 2026-09-20 (round 6): **R20 — world storylets read the sector's own climate.** The type-derived registry
above (§3.9) is **retired**: a world sector already carries its own era climate, `WorldSector.Climate`
(`gk-core/src/FusionRpg.Core/World/WorldState.cs:153-154`, authored per sector in the templates, e.g.
`gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.cs:90`, persisted with the world at
`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:311`), and the world already reads it for wild spawns
(`gk-core/src/FusionRpg.Core/World/Loam/WildSpawnRoller.cs:77`), raised species (`gk-core/src/FusionRpg.Core/World/Growth/RaiseResolver.cs:136`)
and ley-lane cost (`gk-core/src/FusionRpg.Core/World/Ai/MarchGraph.cs:44-45`). That field is the **one source of truth**; no
narrative registry mirrors it. The `world.*` rows' `climateSource` is `sector` and their `climates` are all seven
values (any element, or `none` — the homeworld's null climate), exactly like the Delve's `room` rows, because which
climates a map presents is template content, a population the seed side does not pin. The expedition and homeworld
rules above are unchanged, with "the same registry" read as "that sector's own climate". Negative clause for the family:
*a host kind is where a storylet can be shown, not which storylet is chosen or what it pays.*

**Ownership note.** `npc-story-events-map.md` row 1 lists host kinds among its *runtime-only*
vocabularies, while `narrative-seed-map.md` row 5 puts them here. A storylet names its hosts, and the
planner computes cells from them before any runtime host exists, so the file must exist on the seed side
first. It is authored here and the runtime reads the same file (the one-file-per-vocabulary rule both maps
state). The runtime map's row 1 needs a one-line correction; that propagation is owed to its owner. Reconciled 2026-09-19: `npc-story-events-map.md` row 1 now lists host kinds among the shared files this module authors.

**3.2 `choice-kinds.v1.json` — what the player can do.** Each maps to machinery that exists.

| Value | `gate` | `argFamily` | Resolves by | Negative clause |
|---|---|---|---|---|
| `interact` | none | none | a draw among the choice's own outcomes (`OutcomeResolver`) | not a fight and not a trade; nothing is spent |
| `leave` | none | none | nothing; a chain may continue later | not a failure, not a penalty; every storylet has exactly one |
| `use` | intrinsic | `supplyTag` | the supply is spent, then this choice's outcomes | not `bring`: a supply is consumed, a party member is not |
| `offer` | intrinsic | `stock` | a cost priced by the runtime (`gk-core/src/FusionRpg.Core/Delve/Wild/OfferPricing.cs:26`) | not a bargain kind; the price is never written in the seed |
| `fight` | none | none | a battle through the existing builder (`gk-core/src/FusionRpg.Core/Delve/Encounter/Encounter.cs:91`) | not `threaten`; a fight is the battle itself |
| `bring` | intrinsic | `element` | this choice's outcomes, usually the best (FTL's requirement-gated options) | not `use`; nothing is spent, a party member qualifies |
| `persuade` | none | none | a contest on a Θ difference (`gk-core/src/FusionRpg.Core/Combat/CombatProbability.cs:8`) or the shipped flat coin | not an offer; nothing is paid |
| `threaten` | none | none | the same contest | not a fight; no battle starts from the threat itself |

Argument families, all closed: `supplyTag` → the override-tag registry; `stock` → `souls · spirit ·
supply`, declared here, matching the shipped verbs (`gk-core/src/FusionRpg.Core/Delve/Wild/TalkTree.cs:10-12`);
`element` → the six elements. A trait or species argument for `bring` is a later reviewed widening.

The **intrinsic gates** compile as: `use` → the built `HoldsStock` leaf
(`gk-core/src/FusionRpg.Core/Effects/Atoms/PredicateNode.cs:41`); `offer` → the runtime's affordability check on
the priced cost, not a predicate leaf; `bring` → the party-composition leaf `PartyCarriesTag` (Alignment
2026-09-20: named), which does not exist yet and is `npc-story-events`' `narrative-predicates` (map §3.3;
`npc-story-events-map.md` row 9).

**3.3 `choice-patterns.v1.json` — the authored shapes the planner allocates.** The default follows FTL's
measured distribution: two unconditioned options (one of them `leave`) plus zero to two conditioned ones
(`narrative-seed-ideal.md` §5.3). Each pattern fixes its slots in order; each slot names its choice kind
and a fixed outcome count, so every slot's fields are votable by position (the fix for
`gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/briefs.py:227-235`). Slot order is the vote position, not a
display order — presentation belongs to the runtime.

| Pattern | Slots (outcomes per slot) | `fitsKinds` |
|---|---|---|
| `pattern.interact-leave` | interact (2), leave (1) | curio, shrine, trap, story |
| `pattern.fight-leave` | fight (2), leave (1) | encounter-event, trap, story |
| `pattern.persuade-leave` | persuade (2), leave (1) | story, bargain |
| `pattern.threaten-leave` | threaten (2), leave (1) | story, bargain |
| `pattern.interact-leave-use` | interact (2), leave (1), use (1) | curio, shrine, trap |
| `pattern.interact-leave-offer` | interact (2), leave (1), offer (1) | shrine, bargain |
| `pattern.interact-leave-bring` | interact (2), leave (1), bring (1) | curio, shrine |
| `pattern.fight-leave-use` | fight (2), leave (1), use (1) | encounter-event, trap |
| `pattern.fight-leave-bring` | fight (2), leave (1), bring (1) | encounter-event |
| `pattern.persuade-leave-offer` | persuade (2), leave (1), offer (1) | bargain, story |
| `pattern.persuade-leave-bring` | persuade (2), leave (1), bring (1) | story |
| `pattern.threaten-leave-bring` | threaten (2), leave (1), bring (1) | story, encounter-event |
| `pattern.interact-leave-use-bring` | interact (2), leave (1), use (1), bring (1) | curio |

Structural rules, each a test: 2–4 slots; exactly one `leave`, with exactly one outcome; exactly two
slots whose kind has `gate: none`; zero to two slots with `gate: intrinsic`; no kind twice; outcomes per
slot 1–3; every choice kind appears in at least one pattern; every storylet kind has at least one fitting
pattern. The ideal's example `[offer, leave] + use + bring` has one unconditioned option and three
conditioned ones, which breaks its own two-unconditioned rule; the rule wins and that example is not a
pattern.

**3.4 `conditions.v1.json` — an extra gate on a conditioned slot.** An unconditioned slot's condition is
always `none`, which keeps two options open in every storylet. A conditioned slot carries its kind's
intrinsic gate plus, optionally, one condition from this list:

| Value | `argFamily` | `usableIn` | `compilesTo` | Negative clause |
|---|---|---|---|---|
| `none` | none | slot | nothing | not "unknown": the slot has no gate beyond its kind's own |
| `danger-band-is` | `dangerBand` (bands registry `:5`) | slot | leaf `BandIs` (built, `gk-core/src/FusionRpg.Core/Effects/Atoms/PredicateNode.cs:42`) | not a difficulty scale; a named band, never a number |
| `disposition-is` | `disposition` (the R4 ladder) | slot | leaf `RelationBandAtMost` — **proposed**, owned by `narrative-predicates` | not a loyalty rank; disposition belongs to a creature that has not joined |
| `character-state-is` | `characterState` (`unmet · met · joined · departed · fallen`, the runtime's `CharacterState` wire ids, `npc-story-events/spec-narrative-vocabulary.md` §3) | slot | leaf `CharacterStateIs` — **proposed**, owned by `narrative-predicates` | not a relation band; says whether the character was met, joined, left or fell, never how warm it is |
| `story-flag-set` | `storyFlag` (declared by the arc shape) | slot, eligibility | leaf `StoryFlagSet` — **proposed**, owned by `narrative-predicates` | not a counter; a flag is set or it is not |
| `lead-level-at-least` | `levelGate` (a named gate id from `data/tuning/narrative.v{n}.json` `gates.leadLevel`, `npc-story-events/spec-narrative-vocabulary.md` §4) | slot | leaf `LeadLevelAtLeast` — **proposed**, owned by `narrative-predicates` | not a level and not a band: a named gate whose threshold lives in tuning; the seed never carries the number |
| `doctrine-studying` | none (`arg: none`) | eligibility | leaf `DoctrineStudying` — **proposed**, owned by `narrative-predicates` | not a doctrine id and not a fight; true while the host world's antagonist studies or holds a doctrine (`npc-story-events/spec-counter-doctrine.md` §5) |
| `role-cast` | `roleId` (an optional role declared by the same storylet) | slot | a role requirement, resolved by casting | not a leaf; casting decides it before eligibility is evaluated |

Arguments are named values, never ordinals or numbers: resolving a name to an ordinal is the importer's
job (`gk-core/src/FusionRpg.Core/Effects/Atoms/PredicateNode.cs:19-26`). The file carries a `proposedLeaves`
block naming each proposed leaf and its owning runtime module. A test parses the `LeafId` enum from
`gk-core/src/FusionRpg.Core/Effects/Atoms/PredicateNode.cs:28-46` and asserts every named leaf is either built or
listed as proposed, and that none is both — so the day the runtime lands a leaf, this file is told to
move it.

Alignment 2026-09-20 (cross-lane leaf names). The condition ids above are the **authored surface**; the leaf
names are the runtime's (`npc-story-events/spec-narrative-predicates.md` §5 holds the one mapping table, and
the runtime owns `LeafId`, `narrative-seed-map.md` §7). The proposed names now follow it: `RelationBandIs` →
`RelationBandAtMost`, `StoryFlagIs` → `StoryFlagSet`. Three ids are added so no runtime leaf exists on one side
only: `character-state-is` (`CharacterStateIs`; the leaf `storylet-selection` §4 reads for consequences),
`lead-level-at-least` (`LeadLevelAtLeast`, the id `narrative-predicates` filed here; a gate list that is empty
at first ship means the planner never offers the condition until a gate exists) and `doctrine-studying`
(`DoctrineStudying`, the gate `counter-doctrine` §5 filed for study-site raids). `proposedLeaves` therefore
names `RelationBandAtMost`, `CharacterStateIs`, `StoryFlagSet`, `LeadLevelAtLeast`, `DoctrineStudying` and
`PartyCarriesTag` (the `bring` intrinsic gate, §3.2). The runtime's former `SectorKindIs` is withdrawn on its
side, because a storylet's place is its host kind (§3.1).

**Which role a relation or state condition reads (Alignment 2026-09-20).** `disposition-is` and
`character-state-is` carry one argument, so their subject is fixed by rule, not written: the slot's
`role-cast` role cannot also be present (one condition per slot), so the subject is the storylet's first
declared role whose `kind` is not `forbidden` — the same declaration-order rule `narrative-contract` §5 uses to
fill `consequence.ref`. A storylet with no such role cannot carry either condition (`validate_entry` refuses it).

**`usableIn`** (Alignment 2026-09-20). `slot` conditions sit on a conditioned slot (above); `eligibility`
conditions sit in the storylet's `eligibility` list (`narrative-contract` §5). `story-flag-set` is both: an arc
link's `flagsRead` and a slot gate.

**3.5 `consequence-kinds.v1.json` — what an outcome does beyond its effects.** The existing four
(`gk-core/src/FusionRpg.Core/Delve/Events/EventCatalog.cs:204`) plus the seven runtime outcomes the storylet engine
routes (`npc-story-events-ideal.md` §6.2; `npc-story-events-map.md` row 15; `doctrine.setback` from row 24 —
Alignment 2026-09-20):

Owner ruling 2026-09-19 (round 3): an outcome's consequence is one object, `{kind, ref, param}`
(`spec-narrative-contract.md` §5). This registry declares, per kind, whether `ref` is required and in which prefixed
forms (`refForms`), and which closed `param` values it allows (`params`). The old single `argFamily` column (and the
`direction` family `warmer · colder`) is retired: a target is a `ref`, a modifier is a `param`.

| Value | `refForms` (`ref` required?) | `params` | `routesTo` | Negative clause |
|---|---|---|---|---|
| `none` | — (`ref: null`) | `none` | nothing | not "no effect": the outcome's `effects` still apply |
| `loot` | — (`ref: null`) | `none` | the host's loot draw at this outcome's drop band | not a named item; the runtime rolls it |
| `encounter` | — (`ref: null`) | `none` | a delve-room fight (`gk-core/src/FusionRpg.Core/Delve/Encounter/Encounter.cs:91`) | Delve hosts only; not `battle.start` |
| `scout` | — (`ref: null`) | `none` | the party's sight radius for the room | not a map reveal outside the room |
| `quest.offer` | **required**: `quest:<questId>` — a narrative quest anchor (`spec-quest-vocab.md`) | `none` | the quest engine's offer (`npc-story-events/spec-quest-sources.md` §4) | not a quest definition; the storylet names a quest anchor, it never writes one |
| `relation.shift` | **required**: `role:<roleId>` (a declared role) or `character:<characterId>` (a named character seed or a lead token id) | **required, not `none`**: `met · helped · refused · betrayed · spared` — the relation fact kinds `npc-story-events/spec-relation-ledger.md` §2 derives bands from | the relation ledger: one fact of that kind about the target; tuning owns each kind's band step | not a number of steps and not a direction; never about an enemy-side role (R13 rule 3) |
| `story.flag` | **required**: `flag:<flagId>` (declared by the arc shape) | `none` | the story ledger (`flag.set`, subject = `ref`) | not a relation change |
| `recruit` | **required**: `role:<roleId>` (a cast character) or `host:wild` (the host's unnamed wild creature) | `none` | ownership transfer of the cast character, or the wild-join intake (`gk-core/src/FusionRpg.Core/Delve/Wild/RecruitMint.cs:27`) | never an enemy-side role (R13); enforced by `narrative-validators`' `enemy-consequence` rule (Audit 2026-09-19: no validator named it before) |
| `scene.play` | **required**: `scene:<sceneId>` (a spine scene id, planned) | `none` | the scene player via the scene trigger | not a dialogue tree |
| `battle.start` | — (`ref: null`) | `none` | a battle request into an existing battle mode, for non-Delve hosts | not `encounter`; never a Delve room fight |
| `doctrine.setback` | — (`ref: null`) | `none` | `counter-doctrine`'s study setback, applied inside the world `Events` phase when the choice resolves (`npc-story-events/spec-counter-doctrine.md` §5, `spec-outcome-routing.md` §2); legal on `world.*` hosts only | not a relation change and not an amount: how far the study falls back is tuning (`doctrine.raidSetbackMilli`, `doctrine.raidShortenTurns`) |

Alignment 2026-09-20: `doctrine.setback` is added because the runtime routes it (`spec-outcome-routing.md` §2 row,
`spec-counter-doctrine.md` §5 "added to narrative-seed's vocabulary (filed)"); a seed could not otherwise name the
raid's consequence. The registry is now the existing four plus seven.

The `params` lists are closed and pinned with their reason (a declaration). A kind whose `refForms` is empty
refuses any non-null `ref`; a kind with a required `ref` refuses `null`. `ref` values are DERIVED (filled by the
pipeline's deterministic resolve step, `spec-narrative-contract.md` §5, never the model — Alignment 2026-09-20: this
line said PLANNED after the contract had moved `ref` to DERIVED), so the model-facing enum is `kind` and, for
`relation.shift`, `param` — both carry a `none` row per §1.

`battle.start` is not in `narrative-seed-map.md` row 5's list; it is in the consumer's routing table
(`npc-story-events-map.md` row 15) and ideal (`npc-story-events-ideal.md` §6.2). The contract follows the
consumer so a seed never names a kind the runtime cannot route, or lacks one it can. A new consequence
kind is a reviewed vocabulary change.

**3.6 `role-tags.v1.json` — who can fill a storylet role.** Two blocks:

- `roleKinds`: `required` (cannot cast → the storylet is removed from the pool), `optional` (cast if
  possible), `forbidden` (a character matching the tags must not be present), and `none` (*no role kind
  fits; the structure draft is refused and re-asked* — Audit 2026-09-19: the structure call picks a role
  kind, so the list is model-facing and must admit `none`, map §2 principle 4). Negative clause: *not a
  score; scoring over the save's facts is the runtime's casting.*
- `requireFamilies`, closed: `source` (`party · named · wild · any`), `side` (`plant · zombie`),
  `element` (the six), and `characterRole` whose values are the roles of `character-vocab`
  (`valuesFrom: "roles.v1.json"`; the join is proven where both load, in `narrative-contract`). On disk and
  in every schema a requirement is one string `<family>:<value>` (for example `characterRole:trader`) and a
  role's `requires` is an array of them, empty for "no requirement" — one shape for storylet roles, arc-shape
  roles (`spec-arc-shapes.md` §2) and the runtime's string array (Audit 2026-09-19: the three specs used an
  object, an array and a prefixed string). The item enum carries `none` for the audit rule; a `none` item
  beside any other item is refused by `validate_entry`, and `["none"]` means the same as `[]`.

Role ids themselves are storylet-local names in the token grammar's role form (`token-grammar`), not a
vocabulary here.

**3.7 `value-notes.v1.json` — model-facing notes for borrowed vocabularies.** Descriptions and negative
clauses, keyed `<source>.<value>`, for the borrowed lists a model sees: `outcomeOrdinal` (`good · mixed ·
bad · nothing`, plus `none` = *you cannot tell whether this outcome helps or harms; the draft is refused
and re-asked*), `dropBand` (the five bands — *how often this outcome is drawn among its choice's
outcomes; not a loot quality* — plus `none` = *a certain outcome, legal only when the choice has exactly
one*), and `eventKind` (brief context only). Audit 2026-09-19: the structure call also picks from the
grantable atom families and power bands (`effects[]`) and from the condition argument families
(`dangerBand`, `disposition`), so those lists get notes too, each with a `none` row (*no effect of this kind
fits; the outcome carries fewer effects* for the atom family, *refused and re-asked* for the others). Every
borrowed list any narrative call schema shows is covered; a test proves it against the call schemas, so a
new borrowed list cannot reach a model without its notes and its `none`. A test proves the note keys equal the source members plus
`none` exactly, so the notes can never drift from the lists they describe.

**3.8 `teaches.v1.json` — what a piece of story teaches (Owner ruling 2026-09-20: story is also the
tutorial).** A closed list of the mechanics and loops a player learns from story. A storylet or a spine scene
may name what it teaches; the runtime gives such content its first showing early and once
(`npc-story-events/spec-storylet-selection.md` §4, `spec-spine-progress.md` §3). Each value names the loop of
`docs/guide/the-loops.md` it belongs to, the carriers that can teach it, and one **authored** teaching sentence —
written in this registry, reviewed like code, keyed by the §4 rule of `narrative-contract` with the namespace
`ns.teaches.<value>.teachingLine.<h8>`; the model never writes a teaching sentence (it would be a rules claim the
model can get wrong).

| Value (in teaching order) | `loop` (`the-loops.md`) | `carriers` | `requires` on a storylet carrier | Negative clause |
|---|---|---|---|---|
| `expedition-dispatch` | 2. Idle expeditions — core forever | spine, storylet | host `expedition.return` | not the expedition tiers' numbers; how to send, wait and collect |
| `talk-verbs` | 7. Quests and events | spine, storylet | a `persuade` or `threaten` slot | not a promise that talking wins; what the talk choices are |
| `offer-cost` | 7. Quests and events | storylet | an `offer` slot | not a price; that an offer spends a stock the runtime prices |
| `bring-option` | 7. Quests and events | storylet | a `bring` slot | not a party-building guide; that the right companion opens a choice |
| `relation-bands` | 7. Quests and events | spine, storylet | a `relation.shift` consequence | not a loyalty number; that choices move a character along the one ladder |
| `quest-log` | 7. Quests and events | spine, storylet | a `quest.offer` consequence | not a quest's goal; where offered quests are kept and how to drop one for free |
| `delve-extract` | 6. Dungeon crawler — the Delve | spine, storylet | a `delve.*` host | not a difficulty warning; that extracting banks the haul and a wipe loses it |
| `world-command` | 4. World map — adventure | spine | — | not a strategy; that End Turn commits every order at once |
| `fusion` | B. Creature summon and fusion | spine | — | not a recipe list; that duplicates and essence fuse into stronger forms |
| `counter-doctrine` | 3. Farming, hunting, and defending the empire | spine, storylet | a `doctrine.setback` consequence or a `doctrine-studying` eligibility | not a threat level; that the antagonist adapts to how you fight and a raid sets it back |

The list is a declaration, pinned with its reason; a new value is a reviewed change. It is **planner-only**
(`teaches` reaches a model as `const`, §1), so it carries no `none` — an empty `teaches` list means the content
teaches nothing. The array order of the file is the **teaching order**, which `arc-shapes` §5 uses to order the
spine's chapters.

**Boundary with the first-session sequence.** `docs/architecture/standalone/spec-first-session-progression.md`
owns the first-session checkpoints (first lawn win and Dave's sheet, species XP at level 3, Dave's first item at
level 4). No `teaches` value names one of those mechanics, and no teaching storylet or scene grants, reveals or
waits on a checkpoint: that spec owns the checkpoints, the story supplies the scenes that teach the loops around
them. **Tutorial content never gates play**: `teaches` is read by selection priority only — never by an
eligibility, an unlock or a checkpoint — every teaching storylet keeps its `leave` (NS7), and every teaching scene
keeps story-scene's unconditional skip.

**Superseded — Owner ruling 2026-09-20 (round 6): R20.** World storylets read the sector's own `WorldSector.Climate`
(§3.1); this registry is never authored. The text below is kept as the trail of R19.

~~**3.9 `sector-climates.v1.json` — the climate a world sector type presents to storylets (Owner ruling 2026-09-20
(round 5), R19).**~~ A closed mapping from each of the eight sector types of `gk-core/src/FusionRpg.Core/World/SectorTypeCatalog.cs:55-102`
(read, never edited) to one of the six elements (`gk-core/src/FusionRpg.Core/Stats/Derived/ActorElementTypes.cs:3-11`) or
`none`. Owned by narrative-seed, authored and reviewed like every registry here, so changing a sector's storylet
climate is a registry edit, never code. **The principle, applied to every row:** a type gets an element only when its
name or its defining slot or flag names an elemental phenomenon; a type defined by structure, safety or absence gets
`none`. `none` means storylets there are weighed climate-blind (`EventDraw.WeightMilliFor`'s `none` arm,
`gk-core/src/FusionRpg.Core/Delve/Events/EventDraw.cs:30-35`).

| Sector type | `climate` | Reason (the row's `description`) | Negative clause |
|---|---|---|---|
| `homeworld` | `none` | the one sector the Fracture never touched (`SectorTypeFlags.Home`, `SectorTypeCatalog.cs:8-9`); its era climate is also null (`gk-core/src/FusionRpg.Core/World/WorldState.cs:153-154`) | not "unknown": untouched ground has no elemental identity |
| `stable` | `none` | ordinary ground, named for its steadiness; its slots are plain resources and a Seat | not a weak element: stability is not a phenomenon |
| `rich` | `earth` | defined by what the ground yields — essence deposits, shard veins, material seams, a rootbed (`SectorTypeCatalog.cs:71`) | not wealth: the element is the living soil, not the loot |
| `barren` | `none` | defined by what it lacks: no Seat ever (`SectorTypeFlags.NoBase`), a hazard and a seam | not earth: barrenness is an absence, not a phenomenon |
| `storm` | `air` | the Rift Storm is weather (`Name = "Rift Storm"`, `SectorTypeCatalog.cs:81`) | not dark: the storm is the rift's wind, not its rot |
| `warcamp` | `fire` | a war-forge where the antagonist's armies are made; forging and burning ground are fire | not a threat level: danger stays the danger band |
| `nexus` | `none` | a structural type: a chokepoint joining clusters (`SectorTypeFlags.Nexus`, `SectorTypeCatalog.cs:13-14`) with a spire and a market | not light: a crossing of roads is not an element |
| `boss-lair` | `dark` | the antagonist's own seat (`SectorTypeFlags.Boss`), and the antagonist is a maker of rot (R11, `npc-story-events-ideal.md` §10) | not a doctrine: the lair's climate never changes with the antagonist's study |

The image of the mapping is `none`, `earth`, `air`, `fire`, `dark`: `ice` and `light` are presented by no world type
today. That is a reading of the principle, not a target — no row is bent to cover an element — and a new sector type
gets its row by the same principle. The **member set is the world catalog's**: the file carries exactly one row per
`SectorTypeCatalog` id, which the runtime's join test proves (`npc-story-events/spec-narrative-vocabulary.md` §1), so
the count is never pinned here. Negative clause for the family: *a sector's storylet climate says which storylets suit
the place, never how dangerous it is or what it pays.*

**Known divergence, stated so no reader mistakes it for a bug.** World sectors already carry an authored per-sector era
climate (`WorldSector.Climate`, `WorldState.cs:153-154`) that world-map uses for wild spawns, raised species and ley-lane
costs (`gk-core/src/FusionRpg.Core/World/Growth/RaiseResolver.cs:136`, `gk-core/src/FusionRpg.Core/World/Loam/WildSpawnRoller.cs:77`,
`gk-core/src/FusionRpg.Core/World/Ai/MarchGraph.cs:44-45`), and it varies within one type: the shipped templates give
`barren` sectors `earth`, `dark` and `fire` (`gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.cs:90`,
`gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.TwoHearths.cs:97`, `:158`). R19 derives the storylet climate from the
**type**, so a sector's storylets and its wild creatures can disagree. That follows the ruling as given; whether the
storylet climate should instead read the sector's own `Climate` is the one question this pass leaves for the owner.

### 4. The reader

`adapters/narrative/storylet_vocab.py` (new) loads every file fresh on each call and returns frozen
views. Paths resolve through `gk-forge/tools/seedsmith/seedsmith/workspace_roots.py:47`. The C# reader is
`npc-story-events`' job; both sides load the same committed files, so drift is impossible by construction
(the precedent is `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/registries.py:1-10`).

### 5. `decisions.md` row

No row of its own: these registries are the vocabulary of row 1 (the storylet contract), drafted in
`narrative-contract`.

---

## Commands

```powershell
$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/test_narrative_storylet_vocab.py -q
```

## Project structure

```text
gk-data/packs/fusion/data/seed/narrative/_registry/host-kinds.v1.json          (new)
gk-data/packs/fusion/data/seed/narrative/_registry/choice-kinds.v1.json        (new)
gk-data/packs/fusion/data/seed/narrative/_registry/choice-patterns.v1.json     (new)
gk-data/packs/fusion/data/seed/narrative/_registry/conditions.v1.json          (new)
gk-data/packs/fusion/data/seed/narrative/_registry/consequence-kinds.v1.json   (new)
gk-data/packs/fusion/data/seed/narrative/_registry/role-tags.v1.json           (new)
gk-data/packs/fusion/data/seed/narrative/_registry/value-notes.v1.json         (new)
gk-data/packs/fusion/data/seed/narrative/_registry/teaches.v1.json             (new) Alignment 2026-09-20 (owner ruling: story is also the tutorial)
~~data/seed/narrative/_registry/sector-climates.v1.json     (new) Owner ruling 2026-09-20 (round 5), R19~~ (retired by R20, Owner ruling 2026-09-20 (round 6))
gk-forge/tools/seedsmith/seedsmith/adapters/narrative/__init__.py   (new) package marker only; the adapter class is narrative-contract's
gk-forge/tools/seedsmith/seedsmith/adapters/narrative/storylet_vocab.py   (new)
gk-forge/tools/seedsmith/tests/test_narrative_storylet_vocab.py     (new)
```

The files are authored registries under `_registry/` — hand-written and reviewed, never generated.

## Code style

Match `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/registries.py`: one reader, read fresh, frozen return
values, refusals that name the file and the key.

## Testing strategy

| Test | Asserts |
|---|---|
| `every_value_has_description_and_negative` | both keys non-empty in every file |
| `model_facing_lists_have_none` | `conditions`, `consequence-kinds` and the notes for `outcomeOrdinal`/`dropBand` carry a `none` row; planner-only lists carry none |
| `host_kinds_join_room_kinds` | every `roomKind` exists; `climateNeutral` equals the room-kind flag; every `admits` value is an `eventKind` member |
| ~~`sector_climates_close`~~ | ~~(round 5, R19)~~ Owner ruling 2026-09-20 (round 6): retired with the registry (R20) |
| `world_rows_read_sector_climate` | Owner ruling 2026-09-20 (round 6), R20: every `world.*` row has `climateSource: sector` and `climates` equal to the six elements plus `none`; no file under `_registry/` maps a sector or sector type to a climate |
| `patterns_obey_the_shape_rules` | the §3.3 rules, one assertion each |
| `every_choice_kind_and_storylet_kind_is_covered_by_a_pattern` | coverage of both lists |
| `arg_families_close` | supply tags, disposition bands, danger bands and elements resolve to their source registries |
| `leaves_are_built_or_proposed_never_both` | parsed `LeafId` members vs `proposedLeaves` |
| `condition_usable_in_closes` | every condition declares `usableIn`; only `usableIn: eligibility` ids may appear in a storylet `eligibility` list (Alignment 2026-09-20) |
| `teaches_close_and_order` | every `teaches` value has description, negative, a `loop` naming a `docs/guide/the-loops.md` heading, `carriers`, a storylet `requires` that joins this file's kinds/hosts, and an authored `teachingLine` with no digit; no value names a first-session checkpoint mechanic; the member list and order are pinned as a declaration (Alignment 2026-09-20) |
| `value_notes_match_their_sources` | note keys = source members + `none` |
| `every_borrowed_model_facing_list_has_notes` | every borrowed enum in any narrative call schema (built by `narrative-contract`) has a notes block with a `none` row (Audit 2026-09-19) |
| `role_kinds_admit_none` | `roleKinds` carries `none` with its description and negative clause |
| `requires_is_one_string_shape` | every `requires` item parses as `<family>:<value>` with a known family and member; `none` mixed with another item is refused |
| `consequence_kinds_cover_the_legacy_four` | `none · loot · encounter · scout` present (the loader's existing list) |
| `consequence_ref_and_param_rules_close` | every kind declares `refForms` and `params`; `relation.shift`'s `params` equal the relation fact kinds of `spec-relation-ledger.md` §2 exactly; no kind keeps an `argFamily` (Owner ruling 2026-09-19 (round 3)) |
| `closed_member_lists_are_pinned` | each registry's member list is pinned with a comment: a declaration, so a new member is a reviewed change |
| `unknown_key_is_refused` | fixture file with an extra key fails naming it |

No test counts seeds, cells or a corpus.

## Boundaries

- **Always:** description plus negative clause per value; reference borrowed lists by path; keep the
  model-facing/planner-only split.
- **Ask first:** a new consequence kind, choice kind or condition (each needs runtime machinery); a host
  kind outside the Delve before its runtime exists.
- **Never:** copy a vocabulary another registry owns; put a weight, probability or price in any file;
  add a predicate leaf (runtime-owned).

## Success criteria

- [ ] Eight registries and the notes file exist and load; every join closes (Alignment 2026-09-20: `teaches`; Owner ruling 2026-09-20 (round 6): R20 retired round 5's `sector-climates`).
- [ ] Every value has a description and a negative clause; model-facing lists admit `none`.
- [ ] Every pattern has exactly one `leave` and exactly two unconditioned slots; every kind is covered.
- [ ] Every compile target is a built leaf, a proposed leaf with a named owner, a role requirement or a
      runtime check.
- [ ] Member lists are pinned as declarations with their reasons.

## Open questions

None.

---

## Standards audit (2026-09-19)

Independent adversarial review against `docs/research/ai-native-generation/README.md` §10, seedsmith P1–P5,
`seedsmith/spec-pipeline.md` §3, `spec-quality-gates.md`, `spec-workflow-runtime.md`, `validation-ssot.md`,
`tunables-ssot.md`, `item/seed-contract.md` §2–§7, `DESIGN-GATE.md` §3/§5, owner rulings R1–R13 and IC-3, and
the runtime contracts (`npc-story-events/spec-storylet-contract.md`, `spec-narrative-text.md`). Every change
in the body is marked "Audit 2026-09-19" (or "Owner ruling 2026-09-19 (round 4)" where the owner ruled).

| # | Severity | Finding | Status |
|---|---|---|---|
| 1 | medium | `roleKinds` is picked by the structure call but had no `none` row (principle 4) | fixed (§3.6) |
| 2 | medium | `requires` was an object in `arc-shapes`, an array here and a prefixed string at runtime | fixed (one `<family>:<value>` string array) |
| 3 | medium | Value notes covered three borrowed lists; atom family, power band and condition-argument lists reached the model without notes or `none` | fixed (§3.7 + test over the call schemas) |
| 4 | low | R13 negatives for `recruit`/`relation.shift` named no enforcing validator | fixed (`enemy-consequence`, `spec-narrative-validators.md` §2) |
| 5 | low | Map row 5 said `bring:{tag}`; the closed argument family here is the six elements | fixed in the map |
| 6 | low | Citations sampled: `PredicateNode.cs:28-46`, `EventCatalog.cs:204`, `bands.v1.json:45/:52/:56`, `items/_registry/bands.v1.json:451` — resolve | verified |

## Cross-lane alignment (2026-09-20)

Alignment 2026-09-20: final alignment between this seed contract and `npc-story-events`' runtime readers, plus two
owner rulings of 2026-09-20.

| # | Change | Where |
|---|---|---|
| 1 | Condition leaf names follow the runtime (`RelationBandAtMost`, `StoryFlagSet`); `character-state-is`, `lead-level-at-least`, `doctrine-studying` added so no leaf exists on one side only; `usableIn` column; subject rule for relation/state conditions. The one seed-id → `LeafId` table lives in `npc-story-events/spec-narrative-predicates.md` §5 | §3.4 |
| 2 | `doctrine.setback` consequence kind, routed by the runtime | §3.5 |
| 3 | `ref` is DERIVED, matching `narrative-contract` §5 | §3.5 |
| 4 | `sanctum.hub` host row; hub conversations are storylets on that host plus `character-vocab`'s `return-*` lines — no new seed kind | §3.1 |
| 5 | Owner ruling 2026-09-20 (story is also the tutorial): the closed `teaches` registry and its first-session boundary | §3.8 |
| 6 | Owner ruling 2026-09-20 (round 5), R19: world host rows take their climate from the sector type through the closed `sector-climates.v1.json`; `climateSource` and `climates` columns; expedition stays neutral (no destination sector); the Delve keeps its room climate | §3.1, §3.9 |
| 7 | Owner ruling 2026-09-20 (round 6), R20: the sector-type registry is retired; world rows read the sector's own `WorldSector.Climate` (`climateSource: sector`, all seven climates) | §3.1, §3.9 (superseded) |

~~Open: the eight `world.*`/`expedition.return` host rows the runtime defines are not yet rows here (§3.1).~~ (They
were added in the 2026-09-20 alignment pass, §3.1.) ~~Open for the owner: the storylet climate follows the sector
**type** per R19, while world-map's per-sector era climate can differ within a type (§3.9 "Known divergence").~~ Closed
by R20 (Owner ruling 2026-09-20 (round 6)): the storylet climate is the sector's own.
