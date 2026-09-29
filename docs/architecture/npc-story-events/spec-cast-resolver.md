# Spec: cast-resolver

Status: **DRAFT for owner review, 2026-09-19. Spec phase; no build authorized.** Every `file:line` below was
opened in this session.

Module `cast-resolver`, row 8 of the [npc-story-events map](../npc-story-events-map.md) (`:214`), wave 2. Depends on
`character-registry` (characters and the cast operation), `storylet-contract` (roles, role gates, placeholders) and
`relation-ledger` (bands for scoring). Consumed by `storylet-selection` (a required role that cannot be cast removes
the storylet), `narrative-text` (who each token names), `choice-resolution` and the hosts. Session record:
`tasks/sessions/narrative-programs-spec2-20260919.json`.

## Objective

Decide **who** is in each place and **who** plays each role, seeded and reproducible per save:

1. **World and save casting.** When a world is created, place characters from the seed corpus into homes (the
   sector slots that host storylets), seeded by the world; when a save first needs them, cast its save-scoped
   companions. Two saves meet different people.
2. **Role casting per storylet.** For each role a storylet declares (required, optional, forbidden, each with
   closed-tag requirements and a score over the save's facts), pick the best character or party creature. A
   required role that cannot be cast removes the storylet; a forbidden role that can be cast removes it too.
3. **Arc casting.** Cast an arc's roles once when it starts; every later link reads that cast.
4. **Resource binding** of the placeholders `{place}` and `{supply}` from the host and world state; `{reward}` and
   `{cost}` are declared here and bound by `choice-resolution` from resolved magnitudes.

Success looks like: the same world seed, ledger and corpus revision produce the same cast every time; a storylet
with an uncastable required role never reaches the pool; an arc's second link names the same character as its first.

## Locked anchors

- **Casting beats authoring volume** (ideal §4.5 item 1; Wildermyth's role scoring, `npc-story-events-ideal.md:235`):
  *"a role takes the highest-scoring hero … a required role that cannot be cast removes the event"*.
- **Roles and casting** (ideal §6.2, `:338-341`); **arcs cast once, reused** (`narrative-seed-ideal.md:383`).
- **Seed to concrete; named streams** (map principle 12, `:111-114`): `WorldSeed.DeriveRollSeed(worldSeed,
  streamName, targetId)` (`gk-core/src/FusionRpg.Core/Effects/Atoms/WorldSeed.cs:24-30`) or `SeededRng.DeriveStream`
  (`gk-core/src/FusionRpg.Core/Battle/SeededRng.cs:26`), one stream per purpose, never a combat stream.
- **Resource binding** (Kreminski; ideal §6.10, `:512-516`): *"[creature] asks for [supply] in [sector]"*.
- A character is one seed per species (`narrative-seed-ideal.md:348-350`); casting chooses which characters a save
  meets and where, never re-species a character (see `spec-character-registry.md` Contradictions 2).

## Design

### 1. World cast (at world creation)

For each sector slot whose kind is a storylet host (`Shrine`, `Anomaly`, `Tear`, `Vault`, `Market`, `Wildland` —
`gk-core/src/FusionRpg.Core/World/SlotTypeCatalog.cs:7-24`):

1. roll `casting.residentChanceMilliBySlot.{slotKind}` (`spec-narrative-vocabulary.md` §4) on
   `WorldSeed.DeriveRollSeed(world.Seed, "narrative:cast:resident", "{sectorId}:{slotIndex}")`
   (`WorldState.Seed`, `gk-core/src/FusionRpg.Core/World/WorldState.cs:336`);
2. on a hit, draw one character from the corpus whose role is in `residentRolesBySlot[slotKind]` and who is not
   yet cast in this world, on the stream `narrative:cast:resident-pick` with the same target id, as a uniform
   seeded draw over candidates in ordinal id order through `WeightedChoice.Pick`
   (`gk-core/src/FusionRpg.Core/Actions/Seeding/WeightedChoice.cs:25`);
3. call `CastCreatureCharacter` (`spec-character-registry.md` §4) with home `sector-slot:{sectorId}:{slotIndex}`.

`residentRolesBySlot` is a **catalog**, not a balance number, so it lives in its own file,
`data/tuning/narrative-cast-catalog.v1.json` (new) — tunables-ssot keeps runtime catalogs beside, never inside, the
number file (DESIGN-GATE §1 "Any tunable number" row). Starting content by the ideal's place table (§6.6):
`Market → [trader]`, `Shrine → [chronicler]`, `Vault → [chronicler]`, `Wildland → [hermit, wanderer]`,
`Anomaly → [hermit, wanderer]`, `Tear → [wanderer]`. Warlords are cast onto world-graph's roaming powers by
`world-events-host` (map row 18, `:224`) through the same operation; clan elders onto clan factions when clans have
a policy (`npc-story-events-map.md:186`).

**When.** World creation is `RpgStore.CreateWorld` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:219`). The world
cast runs as a post-create step in the Server's world-creation route (it needs the corpus, which Data does not
load), and is idempotent through each cast fact's dedupe key, so a retried creation casts nobody twice.

### 2. Save cast (companions)

Save-scoped companions are cast on the save's first world creation: `casting.saveCastPerRole.companion` characters
(tuning, starting 2, declared in `spec-narrative-vocabulary.md` §4 — Audit 2026-09-19) drawn from `companion`-role seeds on the save stream (§5), home `homeworld`. The three lead rows
are ensured at the same time (`EnsureLeadCharacters`).

### 3. Role casting per storylet

Input: a storylet's `roles[]` (`StoryletRole(RoleId, Kind, Requires)`, `spec-storylet-contract.md` §2), the host
site, the party, and the ledger. For each role, in declaration order:

**Candidates.** Characters whose derived fate is `Present`, whose world's `WorldNarrativePhase` is `Live` (save-scoped
characters always are; Owner ruling 2026-09-19 (round 4): a dormant or frozen world's cast is never cast) and whose
home is this host site, the cast of the arc the storylet belongs to (if any), and — only when the role's `source`
requirement admits `party` — the party's creatures.

**Filter by `requires`**, the closed `requireFamilies` of `role-tags.v1.json` (`narrative-seed/spec-storylet-vocab.md`
§3.6, read through `RoleTagCatalog`, `spec-narrative-vocabulary.md` §1): `source` (`party · named · wild · any`),
`side` (`plant · zombie`), `element` (the six) and `characterRole` (the `roles.v1.json` members). Every requirement must
match. Audit 2026-09-19: this list previously read `role:`, `side:`, `element:`, `species:`, `state:`, `party` — two
families (`species`, `state`) the seed vocabulary does not declare and one (`source`) it does that was missing; a
seed could not have written the former, and the runtime could not have read the latter.

**Score** (additive, Wildermyth-style, weights from `casting.score.*`):

```text
score = metBefore           × [a met fact exists]
      + perBandFriendlier   × (hostileOrdinal − bandOrdinal)        # relation-ledger band; 0 for party creatures
      + notCastRecentlyPulses × min(pulsesSinceLastCast, cap)       # cap: structural, the host's cooldown window
```

The `min` bounds a recency bonus to one cooldown window — a bounded ratio of a window, not a magnitude cap — and says
so in a comment. The best score wins; ties break by a seeded draw on
`"narrative:cast:role"`, target `"{storyletId}:{roleId}:{hostKind}:{hostClock}"`, never by list order.

**Kinds.**
- `required`: no candidate → the storylet is **removed** from this pulse's pool (`CastOutcome.Uncastable`).
- `optional`: no candidate → the role is unbound; any choice whose `RoleGate` or an outcome's `consequence.ref`
  names it (`role:<roleId>`; Owner ruling 2026-09-19 (round 3): the one `{kind, ref, param}` consequence object,
  `spec-storylet-contract.md` §1) is ineligible. The storylet's `name` and `situation` may reference only required roles; that load rule,
  `storylet.optional-role-in-situation`, joins `EventDeckPreflight.Run` with this module.
- `forbidden`: a candidate exists → the storylet is removed (a scene that must not play while that character is here).

A character is cast into at most one role per storylet.

### 4. Arc casting

When the first link of an arc is selected, its roles are cast by §3 and the result is written into the
`arc.started` fact's attributes (`{roleId: characterId}`) together with the arc's pins (`spec-story-ledger.md` §4).
Every later link reads its cast from that fact and never recasts. If a cast character's fate is no longer `Present`,
a link that requires it is ineligible; the arc stalls rather than recasting a stranger (a stalled arc is a reading
for `narrative-readings`, not an error).

### 5. Streams and seeds

| Purpose | Root seed | Stream name | Target id |
|---|---|---|---|
| resident roll / pick | `WorldState.Seed` | `narrative:cast:resident`, `narrative:cast:resident-pick` | `{sectorId}:{slotIndex}` |
| save cast | the save seed below | `narrative:cast:save` | `{role}:{index}` |
| role tie-break | world seed, or the save seed for sanctum and expedition hosts | `narrative:cast:role` | `{storyletId}:{roleId}:{hostKind}:{hostClock}` |

**The save seed.** A save has no seed column today. It is `SeededRng.DeriveStream(0UL, "narrative:save:{playerId}")`
's first `NextULong()` — the same fixed-root derivation `ContractPolicy.PersonalityFor` uses for a specimen
(`gk-core/src/FusionRpg.Core/Creatures/Contracts/ContractPolicy.cs:195-196`). It is stable for a save forever and never
shared with a combat stream (every name above starts `narrative:`).

### 6. Resource binding

```csharp
namespace FusionRpg.Core.Narrative.Casting;

public abstract record EntityRef
{
    public sealed record Character(string CharacterId) : EntityRef;
    public sealed record PartyCreature(string InstanceId) : EntityRef;
    public sealed record SectorSlot(string WorldId, string SectorId, int SlotIndex) : EntityRef;
    public sealed record DelveDomain(string DomainId) : EntityRef;
    public sealed record Homeworld : EntityRef;
    public sealed record Supply(string ItemId) : EntityRef;
    public sealed record Pending(string Placeholder) : EntityRef;      // {reward}, {cost}: bound by choice-resolution
}

public sealed record StoryletCast(
    string StoryletId, long Revision,
    IReadOnlyDictionary<string, EntityRef> Roles,          // roleId -> who
    IReadOnlyDictionary<string, EntityRef> Placeholders);  // "place" | "supply" | "reward" | "cost" -> what

public abstract record CastOutcome
{
    public sealed record Cast(StoryletCast Value) : CastOutcome;
    public sealed record Uncastable(string StoryletId, string RoleId) : CastOutcome;
    public sealed record Forbidden(string StoryletId, string RoleId) : CastOutcome;
}
```

- `{place}` → the host site (`SectorSlot`, `DelveDomain` or `Homeworld`).
- `{supply}` → for a `use:{tag}` choice, the first supply in the party's pack carrying the tag, in item id order; for
  a petition (wave 4), the host passes the sector's need. Missing → the choice is ineligible, never a blank.
- `{reward}` / `{cost}` → `Pending`; `choice-resolution` replaces them with resolved magnitudes.

A cast is **never** a display string: `narrative-text` turns each `EntityRef` into a token value.

## Data shapes

- `data/tuning/narrative-cast-catalog.v1.json` (new): `{ "residentRolesBySlot": { "<SlotKind>": ["<role>", ...] } }`.
- Tuning keys `casting.*` in `narrative.v1.json` (`spec-narrative-vocabulary.md` §4), including
  `casting.saveCastPerRole.companion` (Audit 2026-09-19: declared there now, since the loader requires every key).
- No new table: world and save casts are rows in `rpg_narrative_character`; arc casts are `arc.started` attributes.

## Numeric types

| Quantity | Type | Why |
|---|---|---|
| scores | `long`, `checked` | additive over weights and counts; an overflow throws |
| resident chance | `long` per-mille, compared with an `int` roll widened | the tuning type (`spec-narrative-vocabulary.md` Numeric types) |
| seeds | `ulong` / `long` as `WorldSeed` and `SeededRng` return them | no conversion beyond theirs |

## SOLID notes

- **S:** one resolver for every cast (world, save, storylet, arc); hosts never pick characters.
- **O:** a new requirement tag is a vocabulary row plus one matcher arm; a new host passes its site.
- **D:** depends on `ICharacterReader`/`RelationLedger`/`StoryFact` reads, never on tables.
- One roll SDK: `WeightedChoice.Pick` and the named-stream derivations, no private RNG.

## Commands

```powershell
.\scripts\verify-change.ps1 -Paths @('src/FusionRpg.Core/Narrative/Casting/CastResolver.cs','tests/FusionRpg.Core.Tests/Narrative/Casting/CastResolverTests.cs') -Session <session-id>
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~Narrative.Casting"
dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~WorldCast"
python scripts\audit-magic-numbers.py --domain narrative
```

## Structure

```
src/FusionRpg.Core/Narrative/Casting/CastResolver.cs        (new: role casting, arc reuse, binding)
src/FusionRpg.Core/Narrative/Casting/WorldCast.cs           (new: resident and save casting plans, pure)
src/FusionRpg.Core/Narrative/Casting/EntityRef.cs           (new)
src/FusionRpg.Server/Narrative/WorldCastStep.cs             (new: runs the plan after CreateWorld)
data/tuning/narrative-cast-catalog.v1.json                  (new)
tests/FusionRpg.Core.Tests/Narrative/Casting/CastResolverTests.cs   (new)
tests/FusionRpg.Server.Tests/Narrative/WorldCastTests.cs            (new)
```

## Testing strategy

- **Determinism:** the same world seed, ledger and corpus give the same world cast and the same role casts across
  two runs; the cast plan is a pure function (the Core half runs with no store).
- **Seed sensitivity:** over 64 fixed world seeds the resident casts are not all identical (a property over a
  fixed seed list, deterministic, not a population count).
- **Required uncastable:** a storylet with a required role no candidate satisfies returns `Uncastable`.
- **Forbidden:** a castable forbidden role returns `Forbidden`.
- **Optional unbound:** choices gated on it are ineligible; the preflight rejects an optional role in `situation`.
- **Scoring:** a met, friendlier candidate beats an unmet one; a tie breaks the same way on every run and differs
  across two host clock values (it is seeded, not list-ordered).
- **Arc reuse:** link 2 names link 1's character; a fallen character makes link 2 ineligible without recasting.
- **Idempotent world cast:** running the world-cast step twice for one world adds no row.
- **Streams isolated:** every stream name starts `narrative:`; a scan fails on a narrative call into a
  `battle:`/`dungeon:` stream.
- **No population:** tests use a fixture corpus; no test counts the committed corpus.

## Success criteria

1. Every cast is reproducible from seeds and the ledger. 2. Required and forbidden roles remove storylets. 3. Arcs
keep their cast. 4. Placeholders bind to entity refs, never strings. 5. The resident catalog is data, not code.

## Boundaries

- **Always:** seed every draw on a `narrative:` stream; cast from existing characters; bind refs, not text.
- **Ask first:** minting a new character on demand to fill a role (today only world and save casting mint).
- **Never:** change a character's species; pick by list order; share a combat stream; read the wall clock.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `CastResolver.CastStorylet(...)` → `CastOutcome` | `storylet-selection` |
| `StoryletCast`, `EntityRef` | `narrative-text`, `choice-resolution`, `outcome-routing` |
| `WorldCast.Plan(world, corpus, tuning)` + `WorldCastStep` | world creation (Server), `world-events-host` |
| arc cast in `arc.started` attrs | every later link, `quest-log-contract` (the cast you have met) |

## Contradictions found (report; not fixed here)

1. **Casting templates onto species.** See `spec-character-registry.md` Contradictions 2: this module casts
   characters (each with its seed's species) into homes, following `narrative-seed-ideal.md:348-350,563`, not
   `npc-story-events-ideal.md:399-401`. Reconciled 2026-09-19: the npc ideal §6.3 and map row 8 now match.

## Open questions

None for the owner.

## Design-gate checklist

```
[x] Subsystems: narrative casting, world creation (post-step), relation ladder (reader), roll SDK.
[x] Session boundary recorded (narrative-programs-spec2-20260919).
[x] Read this session: map row 8; ideal §4.2 (Wildermyth), §6.2, §6.3, §6.10; narrative-seed §6.2-§6.4;
    WorldSeed, SeededRng, WeightedChoice, SlotTypeCatalog, WorldState.Seed, CreateWorld, PersonalityFor.
[x] Every claim cites file:line.
[x] Determinism: named streams, seeded tie-breaks, fixed-root save seed.
[x] No cache. No population pinned. No actor number.
[x] No parallel path: one resolver; the mint and character store are character-registry's.
[ ] Registry row: the stream-prefix scan is local; no enforcement-registry row proposed. (Audit 2026-09-19: row
    proposed below.)
```

## Standards audit (2026-09-19)

| # | Severity | Finding | Status |
|---|---|---|---|
| 1 | high | The `requires` tag list did not match the seed vocabulary it filters (`storylet-vocab` §3.6): `species:`/`state:` are not declared families, `source` was missing. Casting would have refused or ignored real seed requirements | **Fixed:** the four `requireFamilies`, read through `RoleTagCatalog` |
| 2 | high | Round-4 owner ruling: casting had no world-lifecycle input, so a hibernating (dormant) or fallen (frozen) world's characters stayed castable | **Fixed:** candidates require `WorldNarrativePhase.Live`; a test per phase below |
| 3 | medium | `casting.saveCastPerRole.companion` was to be added "in the build change" to a table whose loader requires every key | **Fixed:** declared in `spec-narrative-vocabulary.md` §4 |
| 4 | low | Map citations one line early (`:213`, `:223`) | **Fixed** |

Test added by this audit: a character whose world is `Dormant` or `Frozen` is never a candidate; the same character
is castable again after its world returns to `Live` (both orders).

Checked and clean: named `narrative:` streams (never a combat stream, never `System.Random` or the wall clock),
`WorldSeed.DeriveRollSeed` and `WeightedChoice.Pick` signatures verified (`WorldSeed.cs:24-30`, `WeightedChoice.cs:25`),
scores `long` `checked`, the recency `min` commented as a bounded window, the resident catalog is a runtime catalog in
its own file (tunables T7/T8), no population pin.

**Proposed enforcement-registry row:** `ns-narrative-streams-named` — every narrative roll uses a `narrative:` named
stream, never a combat stream; guard: the stream-prefix scan in `CastResolverTests` (promote to Guard.Tests covering
`gk-core/src/FusionRpg.Core/Narrative/**`).
