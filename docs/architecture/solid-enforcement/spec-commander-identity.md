# Spec: `commander-identity`

**Program:** [`solid-enforcement`](../solid-enforcement-map.md) · **Wave 4** · depends on:
`debt-ledger` (row SR-20). Moved here from `empire-progression` by the "one program" ruling (map D5).
**Status:** spec, 2026-09-18; strengthened the same day against code and rulings R3/R17; no build
authorized. [`save-identity`](spec-save-identity.md) builds directly after it.

## Objective

<!-- citations-historical: CommanderId.cs was deleted (commander-identity SE4.2/SE4.3); the faction is EmpireId, the unit is CommanderRef, and every display name/scope key/empire/default comes from data through ICommanderDirectory -->


The owner, 2026-09-17: *"commander is not a enum. it is a unique creature with named and play a role
like another unique actor"* and *"a commander literally a unique demon, it only carry more role."*
Today the type is:

```csharp
// gk-core/src/FusionRpg.Core/Commanders/CommanderId.cs:20
public enum CommanderId { Dave, Zomboss }
```

A population encoded as a closed enum is an **Open/Closed** defect. Every new commander means
editing the four `switch` expressions that map the enum to strings (`CommanderId.cs:34-35`,
`:70-71`; `PlayerEmpireCommanders.cs:14-15`; `SpeciesAllocation.cs:44-45`), the string `switch` that
parses it back (`CommanderId.cs:46-51`), the closed list `CommanderIds.All` (`CommanderId.cs:39`), and
every `== CommanderId.Dave` branch (ten, listed under "Migration").

### The deeper defect this module found: one enum, two responsibilities

<!-- citations-historical: CommanderId.cs was deleted (commander-identity SE4.2/SE4.3); the faction is EmpireId, the unit is CommanderRef, and every display name/scope key/empire/default comes from data through ICommanderDirectory -->


Reading the call sites shows `CommanderId` is used for **two different concepts**:

| Concept | Where it's used as `CommanderId` | What it actually is |
|---|---|---|
| **Empire / side** | species-allocation key (`SpeciesAllocation.cs:44` → `"dave"`/`"zomboss"`, solid-remediation T4.1: *"the empire is now part of the species key"*); `AllocationScopeKey` (`CommanderId.cs:66-72`); kill attribution (`KillAttribution.cs`); `RpgStore.Aptitudes.cs:232` (`empire != CommanderId.Dave`) | **which faction** a species' progression, a kill or an allocation belongs to |
| **Commander** | `rpg_player_commander.default_lawn_commander_id`; `CommanderEndpoints`; `MatchCommanderSessionCache`; `CommanderResourcePools` | **the unit leading the side**, the thing the owner ruled is a unique creature |

That is a **Single-Responsibility** defect underneath the Open/Closed one. Opening the enum without
splitting it would produce an open type that still means two things, and the first real
creature-commander would then silently re-key every species' progression (the "empire" meaning
would follow the creature). **This module splits the concept first and opens it second.**

The code already knows the id spaces must stay apart. `CommanderIds.ToStableId`'s own comment:
*"neither `WorldFaction.FactionId` (bare `"dave"`/`"zomboss"`) nor any `BattleActorSetup.Key` …
ever carries this prefix, so the three id spaces can never collide."* This module makes that
separation a **type**, instead of a naming convention.

## Design

### Two value types, both open

```csharp
namespace FusionRpg.Core.Commanders;

/// <summary>A faction — the side a species' progression, a kill and an allocation belong to. Open:
/// the world map's factions are data (`WorldFaction.FactionId`), and this is the same id space
/// ("dave", "zomboss"). Never a commander: a commander LEADS an empire; it is not one.</summary>
public readonly record struct EmpireId(string Value)
{
    public static readonly EmpireId Dave = new("dave");       // well-known rows, not enum members
    public static readonly EmpireId Zomboss = new("zomboss");
}

/// <summary>The unit holding the commander role. Open by the owner's ruling (2026-09-17): a commander
/// is a unique creature carrying one more role. Stable string form keeps the load-bearing
/// `commander:` prefix, so it can never collide with a faction id or a battle key.</summary>
public readonly record struct CommanderRef(string StableId);
```

- **No `switch` over either type anywhere in `src/`.** Display names, allocation scope keys and
  species-key strings come from **data**, through `ICommanderDirectory` below.
- `EmpireId.Dave` / `.Zomboss` are well-known *values* for the two factions every save has today,
  exactly as `ElementIds` names well-known elements. They are not a closed set, and nothing
  enumerates them as "all empires". **Which empires one save has** is data, owned by
  [`save-identity`](spec-save-identity.md) (`rpg_save_empires`, per save). It is not an enumeration of
  this type.

### One directory (the D in SOLID): `ICommanderDirectory`

```csharp
public interface ICommanderDirectory
{
    bool TryResolve(string stableId, out CommanderRef commander);   // replaces TryParseStableId
    EmpireId EmpireOf(CommanderRef commander);                       // which side it leads
    string DisplayName(CommanderRef commander, long playerId);       // replaces PlayerEmpireCommanders' switch;
                                                                     // the player's default commander = the player's name
    string AllocationScopeKey(CommanderRef commander, long playerId);// replaces the CommanderId.cs:66 switch
    CommanderRef DefaultFor(EmpireId empire);                        // today's two defaults
}
```

**`long playerId` above is the save's id** (`players.id`; ruling R17: the player row **is** the save).
`save-identity` (the module after this one) types it `SaveId`, and passes an `EmpireRef` wherever the
question is about one empire of a save. It changes no string this directory produces.
`AllocationScopeKey` becomes the **one** encoder of the commander pool key; `save-identity` X9 routes
the three other encoders of `player:{id}` through it (`AptitudeEndpoints.cs:123`,
`RpgStore.AptitudePresets.cs:432`, `RpgStore.WorldTurns.cs:575`).

**The shipped implementation is data-backed, and byte-identical to today except for one ruled
change.** It holds two rows: `commander:dave` → empire `dave`, display **the player's own name** (the
one change, owner ruling 2026-09-18, see the section below), scope `player:{id}`; and
`commander:zomboss` → empire `zomboss`, display "Dr. Zomboss", scope `zomboss:{id}`. The rows live in
a small authored registry (`gk-data/packs/fusion/data/seed/commanders/_registry/default-commanders.v1.json`: authored,
never generated). **Save compatibility is preserved to the string:** stored
`default_lawn_commander_id` values and allocation scope keys are unchanged, so **this module** migrates
no data. The schema migration that ruling R3 requires (empires keyed `(SaveId, EmpireId)`) belongs to
[`save-identity`](spec-save-identity.md), and it keeps every string this module preserves.

`empire-progression` then makes a unique creature a commander by **adding a directory row, or a
directory source backed by `rpg_unique_actor`**. That extends the directory. It never edits it. That
was the whole point of the ruling, and it stays that program's feature work (map D5).

### Migration, by call-site kind (measured 2026-09-18; re-measure at build)

| Kind | Count | Change |
|---|---|---|
| Files referencing the enum | 39 in `src/` (re-measured 2026-09-18 in the strengthen pass; the first draft read 37). World files that only use `string CommanderId` properties are unaffected | per file below |
| `CommanderId.Dave/.Zomboss` literals | 43 in `src/`, 111 in `tests/` (re-measured; readings, never pinned) | the **empire** meaning → `EmpireId.Dave/.Zomboss`; the **commander** meaning → `directory.DefaultFor(EmpireId.Dave)` |
| Enum-typed parameters / fields | 14 | typed `EmpireId` or `CommanderRef` **by meaning**, decided per site, never by find-and-replace |
| `switch` expressions over the enum | 4 (`CommanderId.cs` ×2, `PlayerEmpireCommanders.cs`, `SpeciesAllocation.cs`) | deleted; replaced by directory lookups |
| `switch` over the stable-id strings | 1 (`TryParseStableId`, `CommanderId.cs:46-51`) | deleted; `ICommanderDirectory.TryResolve` reads the directory rows. Guard I2 cannot see a string switch, so the Open/Closed test below is what catches a new one |
| The closed list `CommanderIds.All` | `CommanderId.cs:39`; pinned by `gk-core/tests/FusionRpg.Core.Commanders.Tests/Commanders/CommanderIdTests.cs:25` (`Assert.Equal(2, CommanderIds.All.Count)`) and used as a membership set in `gk-core/tests/FusionRpg.Core.Tests/Battle/KillAttributionTests.cs:36`, `:173`, `:180`, `:234` | deleted. The count pin goes with it: once commanders are a population, "two" is a reading. The kill tests assert membership in the directory's rows instead; which empires a save has is `save-identity`'s `EmpiresOf(save)` |
| `== CommanderId.X` branches | ten: `CommanderEndpoints.cs:78`, `:93`; `ItemEquipEndpoints.cs:307`; `PlayerEmpireCommanders.cs:19`; `SpeciesAllocation.cs:29`; `SpeciesAllocationSource.cs:114`; `RpgStore.Aptitudes.cs:232`, `:266`; `RpgStore.WorldTurns.cs:573`; `CheatState.cs:183` | compare `EmpireId` (for the empire rule) or ask the directory. Nine of them mean **"the save's human empire"**, a third meaning this module cannot type yet: they become `== EmpireId.Dave` here and `save-identity` re-types them to `HumanEmpireOf(save)` (its X9 table). `SpeciesAllocation.cs:29` keeps `EmpireId.Dave` for good, because it chooses a persisted string shape |

The **per-site meaning decision** is the real work and the real risk. Each file's commit states which
meaning each use carried, so a reviewer can check the split rather than trust it.

### The regression guard

A small new `guard-open-identity.py`. It is not an extension of `guard-class-system`, whose
invariant is aptitude and channel wiring, not identity:

- **I1:** no `enum` named `*Id` or `*Ids` under `gk-core/src/FusionRpg.Core/Commanders/` or
  `gk-core/src/FusionRpg.Core/World/`, the two namespaces the owner's ruling covers.
- **I2:** no `switch` on `EmpireId` or `CommanderRef` values anywhere in `src/`.

It is deliberately narrow. A repo-wide "no enum ending in Id" rule would hit legitimate closed
vocabularies (`AtomKind` ids and the like), which is the contract-vs-population distinction again.

## Commands

```powershell
dotnet build src\FusionRpg.Server
python gk-core/scripts/guard-open-identity.py
.\scripts\run-guards.ps1 -Tier ci
.\scripts\verify-change.ps1 -Paths <touched> -Session <id>
# cross-module (Core + Data + Server + Injector + Contracts): full suite once at module end (AGENTS.md point 2)
```

## Project structure

| Path | Change |
|---|---|
| `gk-core/src/FusionRpg.Core/Commanders/CommanderId.cs` | enum deleted → `EmpireId`, `CommanderRef` |
| `gk-core/src/FusionRpg.Core/Commanders/ICommanderDirectory.cs`, `DataCommanderDirectory.cs` | **new** |
| `gk-data/packs/fusion/data/seed/commanders/_registry/default-commanders.v1.json` | **new**, authored |
| 37 `src/` files, 67+ test files | per-site migration |
| `gk-core/scripts/guard-open-identity.py`, Guard.Tests falsifiers | **new** |
| `docs/architecture/empire-progression-ideal.md` | the `CommanderId` section marked **moved to `solid-enforcement` `commander-identity`**, with a link |
| `docs/architecture/stub-register.md` | SR-20 struck through with the SHA at close |

## Testing strategy

- **Byte-identical behaviour is the acceptance bar.** Every existing test keeps passing, except those
  whose *only* change is a type rename in their own setup.
- **Goldens:** persistence stores the same strings and hashing does not read the enum's ordinal (the
  world canonical form uses the string id: confirm at build). So no golden is expected to move. **A
  moved golden stops the module** until it is explained, because it would mean an ordinal leaked into
  a hash.
- **A new test proves Open/Closed:** register a third commander row in an in-memory directory
  (`commander:test-creature` → empire `dave`), and run a lawn allocation resolve and a kill
  attribution through it **without editing any production file**. That test is the ruling, made
  executable.
- **Falsifiers for I1/I2.**
- **Commands:** `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~Commander|FullyQualifiedName~KillAttribution|FullyQualifiedName~SpeciesAllocation"`,
  then the Guard.Tests falsifiers for `guard-open-identity`, then `verify-change.py` with every touched
  path.

## Boundaries

- **Always:** decide empire vs commander **per site**, and record it.
- **Ask first:** changing any persisted string or scope key. The design keeps them identical, and any
  deviation is a save migration.
- **Never:** reintroduce a `switch` over these types. Never make a creature-commander re-key species
  progression. That is exactly the conflation this split removes.

## Success criteria

- [ ] No `enum CommanderId`. `EmpireId` and `CommanderRef` in use, each by its meaning.
- [ ] `ICommanderDirectory` is the only place commander display names, scope keys and empires are
      decided.
- [ ] The third-commander Open/Closed test passes with zero production edits.
- [ ] Full suite green at module end; no golden moved, or every move explained.
- [ ] `guard-open-identity` gating.
- [ ] The player's first commander displays the player's name (`/api/commanders/{id}`), and an
      empty-save boot names the player "Crazy Dave". Neutral fallback when the player is unknown.

## The first commander's name — owner ruling 2026-09-18, and an orphan it absorbs

**Ruled:** *"change to player name for first commander."* This is not new. It is rift-gate
decision 7 (2026-09-15): *"Dave remains the first commander, but his display name becomes the
player's name — no second identity, no new actor."* Rift-gate decision 10 assigned it to
`commander-surface`. **It was never built, and nothing owns it:** `CommanderEndpoints.cs:87` still
emits `PlayerEmpireCommanders.DisplayName(commander)`, the constant `"Crazy Dave"`, and
`commander-surface`'s map and todo carry no task for it (they use `"Crazy Dave"` only as an example
value). Under the one-program ruling it lands here, because this module's directory is where display
names are decided.

**How:** `ICommanderDirectory.DisplayName` takes the player it is answering for. The player's
empire's **default commander** resolves to **the player's own name** (`PlayerDto.Name`, the name the
player types at "Choose a summoner", `SaveSelect.tsx`), read at the seam that already holds
`playerId` (`CommanderEndpoints.ProjectList`). `Dr. Zomboss` keeps its authored name. The
"we don't know the player" fallbacks (`MatchCommanderSessionCache.cs:14,43`, `RpgClient.cs`) use a
**neutral** label, never another person's name, as rift-gate's own analysis specified.

**A mismatch between the owner's description and the code, flagged rather than assumed.** The owner:
*"my onboarding idea already create crazy dave as first player when it is empty [boot] and play
prologue story."* The code does not do that yet. On an empty save, `SeedPlayerIfEmpty`
(`RpgStore.cs:4018`) inserts a player named **`'Player 1'`**. The two rulings compose cleanly once
that seed says what the owner intends:

| Save | Player name | First commander shows |
|---|---|---|
| Fresh boot, empty save (prologue path) | **"Crazy Dave"** (seed changed from `'Player 1'`) | "Crazy Dave" |
| Player-created save | whatever the player typed | that name |

So this module **also changes the empty-save seed name to "Crazy Dave"**. No test or FE file depends
on `'Player 1'` (grep, 2026-09-18: `RpgStore.cs` is its only occurrence). The string is player-facing
content, so it is declared once with a comment naming the owner's onboarding idea, never repeated.
`save-identity` edits the same seed function for a different line: the seed also creates the save's
empires (a human one and Zomboss's AI one). The name belongs to this module, the empires to that one.

**Still not changed:** the *empire* is labelled by the directory's empire rows, and whether the UI
should one day read "<player>'s empire, led by <creature>" is `empire-progression`'s feature.

## Self-audit — the debate

**Objection: "Just replace the enum with a string. Splitting into two types is over-engineering."**
A plain string keeps the conflation. The same `"commander:dave"` value would flow into species
allocation (an empire concept) and into the commander slot (a unit concept). The first time a
creature became a commander, species progression would re-key to it and every player's species
levels would appear to reset. Two types turn that bug into a compile error. That is the cheapest
place a bug can ever be caught.

**Objection: "EmpireId is also a closed set in practice (plants vs zombies)."** The *lawn* has two
sides structurally, but empires are the world map's factions, and those are data
(`WorldFaction.FactionId`). Closing `EmpireId` would repeat the defect one level up. Its well-known
values give the convenience of an enum without the closedness.

**Objection: "37 files and 112 test literals is a big bang."** It is sequenced as one compile-driven
pass. Delete the enum, and the compiler lists every site. The per-site meaning decision is the work
and cannot be skipped. `srp-file-budget` runs after this module, so it never splits a file while this
one is editing it.

## Gaps found and closed while writing

- **The ideal doc framed this as "make the enum open".** Reading the call sites found the two
  meanings. Opening without splitting would have shipped a latent re-keying bug. The split is now the
  first half of the design.
- **Save compatibility** was unexamined in the ideal. Checked: the persisted columns are already
  `TEXT` (`rpg_player_commander.default_lawn_commander_id`, `rpg_world_commands.commander_id`). The
  directory preserves every stored string, so there is no migration.
- **Strengthen pass (2026-09-18).** The migration counts drifted (37 → 39 files, 45 → 43 and
  112 → 111 literals); the first draft missed the string switch in `TryParseStableId`, the closed list
  `CommanderIds.All` and its count-pinning test, and six of the ten `== CommanderId.Dave` sites. Nine
  of those sites mean "the save's human empire", which is `save-identity`'s type, so the hand-off is
  now explicit instead of each module assuming the other re-types them.
- **The regression guard** was a repo-wide "no *Id enums" rule in the first draft. It would have hit
  legitimate closed vocabularies, so it was narrowed to the two namespaces the ruling covers.
