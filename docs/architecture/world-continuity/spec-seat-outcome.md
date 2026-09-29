# Spec: `seat-outcome`

**Status: written against shipped code 2026-09-19** on `features/mega-merge`. Module 3 of the
[world-continuity map](../world-continuity-map.md) (wave 1, no dependencies). Ideal:
[world-continuity-ideal.md](../world-continuity-ideal.md) §6.1, §6.5, W1, W4, W8. Owner decisions
**Q1** (`outcome` column) and **Q2** (losing the active world makes it `fallen`; the save never ends),
2026-09-19. House style: [../world-action-economy/spec-budget-debit.md](../world-action-economy/spec-budget-debit.md).

## Objective

One pure Core function over a committed `WorldState` answers two questions: **has the player taken the
seat of the world's dominant enemy empire** (→ `won`), and **has the player lost their own seat**
(→ `fallen`)? Victory and fall are two readings of one detector, so they cannot disagree, and a full
step and a coarse step that produce the same state produce the same reading.

## Scope and non-goals

**In scope:** the detector; the per-template declaration of the dominant enemy seat; a validation rule
that every continuity template declares exactly one; the reading for both step kinds.

**Not in scope:** writing `outcome` (`world-victory`, `world-fall`); anything that happens after the
reading; `world-reclaim`.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| Every map world has exactly one `Home` sector, owned by the player faction at creation | `gk-core/src/FusionRpg.Core/World/WorldValidation.cs:201-218` (`Rule4Homeworld`); flag `gk-core/src/FusionRpg.Core/World/SectorTypeCatalog.cs:9`, `:59-60` |
| `boss-lair` carries `SectorTypeFlags.Boss` | `SectorTypeCatalog.cs:12`, `:98-99` |
| Faction kinds are plural-ready (`Player`, `Zomboss`, `Clan`, `Rival`, `Wild`) | `gk-core/src/FusionRpg.Core/World/FactionKindCatalog.cs:7-18` |
| Sector ownership changes by capture (`ClaimResolver`) and by fade to unowned (`LoamPhases`) | `gk-core/src/FusionRpg.Core/World/Movement/ClaimResolver.cs:101`; `gk-core/src/FusionRpg.Core/World/Loam/LoamPhases.cs:219` |
| Validation runs only at creation (never on load), so a world whose `Home` is lost still loads | the only map callers are `WorldTemplateCatalog.cs:42-43` and `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:226` |

### Wiring gap

| Gap | Evidence |
|---|---|
| `SectorTypeFlags.Fortress` exists and no sector type sets it; only `DistrictLayout` reads it | `SectorTypeCatalog.cs:15`; `gk-core/src/FusionRpg.Core/World/District/DistrictLayout.cs:267` |

### Real gap — and a content finding

- Nothing in `gk-core/src/FusionRpg.Core/World` detects victory or seat loss.
- **No shipped template contains a `boss-lair` sector.** `first-light` uses `homeworld`, `stable`,
  `rich`, `barren`, … and has **no enemy-held sector at all** — its only enemy presence is a warband
  (`gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.cs:210`). `two-hearths`' enemy capital is `z-home`, a
  `warcamp` (`gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.TwoHearths.cs:236-243`), which carries no
  `Boss` flag. So the map's reading "the dominant enemy is whoever owns the `Boss`-flag seat"
  (map module 3) has no content to read today.
- **Found in the round-4 reconciliation (2026-09-19):** `first-light` does have a seat for its enemy — the
  unowned `nexus` sector `black-gate`, whose `Seat` slot sits behind a heavy guard
  (`gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.cs:98-108`), next to a `Zomboss` faction row that holds no
  ground (`:83`). `trade-network` `counterparties` already treats `black-gate` as that empire's seat
  (`trade-network/counterparties/spec-empire-roster.md` §1 rule 3). This spec's first draft missed it; §4 is
  corrected.

## Design

### 1. The dominant seat is a template declaration, not a sector flag

`WorldTemplateCatalog` gains one lookup:

```csharp
// The sector whose capture wins this template (W8: many empires; one is dominant).
public static string DominantSeatOf(string templateId) => templateId switch
{
    TwoHeartsId => "z-home",
    FirstLightId => "black-gate",   // unowned at creation, guarded seat (§4, round-4 reconciliation)
    _ => throw new ArgumentException(...)
};
```

Why a declaration and not the `Boss` flag: retyping `z-home` to `boss-lair` changes its danger band
(`SectorTypeCatalog.cs:98`, band 6 vs `warcamp` band 4, `:87`) and so the world's hash and every
golden that builds `two-hearths`; a declaration keyed by template id changes nothing in `WorldState`
and nothing in the hash. When `world-generator` produces templates as data, the declaration becomes a
field of the template record; the detector's input shape does not change. The **dominant enemy empire**
is, by definition, the template's one faction of kind `Zomboss` — the definition `trade-network`
`counterparties` `empire-roster` rule 1 already validates (*"exactly one faction of kind `Zomboss`"*); one
definition, not two. The rule validated here: exactly one declared seat, which at creation is either held
by that faction or unowned (a guarded seat the enemy has not garrisoned), and never held by `Player`,
`Wild`, `Clan` or `Rival`.

### 2. The detector

```csharp
// src/FusionRpg.Core/World/Continuity/SeatOutcome.cs — pure: no store, no clock, no RNG.
public enum SeatReading { Contested, SeatTaken, SeatLost }

public static SeatReading Read(WorldState world, string dominantSeatSectorId)
{
    var player = world.Factions.Single(f => f.Kind == WorldFactionKind.Player).FactionId;
    var home   = world.Sectors.Single(s => SectorTypeCatalog.Get(s.TypeId).Flags.HasFlag(SectorTypeFlags.Home));
    if (!string.Equals(home.OwnerFactionId, player, StringComparison.Ordinal)) return SeatReading.SeatLost;
    var seat   = world.Sectors.Single(s => s.SectorId == dominantSeatSectorId);
    return string.Equals(seat.OwnerFactionId, player, StringComparison.Ordinal)
        ? SeatReading.SeatTaken : SeatReading.Contested;
}
```

- **Seat lost wins over seat taken** in the same state: a player who took the enemy capital and lost
  their own `Home` in the same turn has lost their seat. Stated, tested, not an accident of `if` order.
- **Lost means "not owned by the player", whatever the cause** — capture (`ClaimResolver.cs:101`) or
  fade to unowned (`LoamPhases.cs:219`). Q2's words are "enemy empires take your seat"; the cause is
  the digest's to say, not a second predicate. One predicate is what makes victory and fall unable to
  disagree.
- The reading is a **level**, not an edge: the caller (`world-victory`, `world-fall`) owns the
  transition and its idempotency. Retaking the enemy seat after it was re-taken does not "win again"
  (`won` is sticky, `world-victory`), and `fallen` is terminal for this program (`world-fall`).

### 3. Validation — continuity templates declare exactly one seat

A new pure check `SeatOutcome.ValidateDeclaration(world, templateId)`: the declared seat exists, is
not the `Home` sector, and at creation is either owned by the template's `Zomboss` faction or unowned —
never owned by a `Player`, `Wild`, `Clan` or `Rival` faction (a clan's seat, now on both templates after
round-4 Q5, can therefore never be mistaken for the win condition).
It is called by the production creation service (`world-creation`) before `CreateWorld`
(`RpgStore.World.cs:219`), **not** inside `WorldTemplateCatalog.Build` (`WorldTemplateCatalog.cs:39-45`):
putting it in `Build` would fail every existing test that builds `first-light` the moment this module
lands. A template with no declaration is refused by the production path, never created silently
"unwinnable".

### 4. `first-light`'s winnable seat — `black-gate` (corrected in the round-4 reconciliation)

`first-light` is the default template for a new save (`WorldTemplateCatalog.cs:35-38` comment) and holds
no enemy ground, but its `black-gate` sector carries an unowned, heavily guarded `Seat` slot. Options:

- **Chosen (2026-09-19 reconciliation):** declare `black-gate` as `first-light`'s dominant seat. Taking it
  (clearing its guard and owning the sector) is the win. **No template content changes**, so no template
  version, no golden moves, and nothing collides with `counterparties`' `first-light` v2, which adds the
  round-4 clan (`trade-network/counterparties/spec-clan-seeding.md` §4). It matches the sibling cluster's
  reading of the same sector (`spec-empire-roster.md` rule 3).
- Withdrawn: the first draft's authored enemy capital owned by `Zomboss`. It would have edited
  `first-light` for the same purpose `black-gate` already serves, given a teaching map a landed enemy that
  pays upkeep and expands, and taken the `v2` template version the clan now uses.
- Rejected: leaving `first-light` unwinnable. A new player's first world could then never reach `won`, so
  the full carry limit and the won-fact (`world-victory`) would be unreachable from the tutorial.

`first-light`'s enemy empire therefore never loses a seat it holds, and `world-fall` for the enemy is not a
concept this module has; the player's `Home` rule is unchanged.

### 5. Full step and coarse step read the same function

`world-victory` and `world-fall` call `Read` after a committed full step (`CommitWorldTurn`) and after
every `coarse-step` record. Because the input is only `WorldState` + the declaration, the same state
gives the same reading whichever engine produced it.

## Built / wiring gap / real gap (summary)

| Bucket | Item | Closed by |
|---|---|---|
| Built | `Home` flag, one-home rule, capture, fade | reused |
| Wiring gap | `Fortress` flag unused | left alone — the declaration (§1) is the dominant-seat SSOT; `Fortress` stays `DistrictLayout`'s |
| Real gap | detector; seat declaration; validation | §1–§3 |
| Content gap | `first-light` had no declared seat | §4 — `black-gate` declared; no content change |

## Acceptance (contract)

1. `Read` is pure: identical inputs give identical output; the file holds no store, clock or RNG
   reference (the world determinism guard covers `gk-core/src/FusionRpg.Core/World`,
   `gk-core/tests/FusionRpg.Guard.Tests/WorldDeterminismGuardTests.cs:253-266`).
2. For every continuity template: taking the declared seat reads `SeatTaken`; losing `Home` reads
   `SeatLost` (both causes: capture and fade); both at once reads `SeatLost`.
3. `ValidateDeclaration` refuses, with a named reason, a template with no declared seat, an unknown seat
   id, a seat equal to `Home`, or a seat owned at creation by a `Player`, `Wild`, `Clan` or `Rival`
   faction; an unowned declared seat (`first-light`'s `black-gate`) passes; `Build` itself is unchanged.
4. The reading is identical for a world produced by `TurnEngine.Step` and by `CoarseStep` when the
   resulting `WorldState`s are equal (tested by constructing both).

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/Continuity/SeatOutcomeTests.cs` (new): acceptance 1–4 on
  `two-hearths` built through `WorldTemplateCatalog.Build`, mutated by `with` expressions.
- No Data or Server change.

```powershell
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <id>
dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~WorldDeterminismGuard"
```

## Hard edges

- **`rpg_worlds` schema:** none.
- **Replay / hash:** none — no `WorldState` field and no template change (the `first-light` seat is a
  declaration of an existing sector, §4).
- **Corpse-cache tick key:** none.

## Dependencies

None. Consumed by `world-victory`, `world-fall`, `coarse-step` (the per-record reading), `away-digest`.

## Boundaries

- **Always:** one detector for both readings; seat lost beats seat taken.
- **Ask first:** a win condition other than the seat (for example a share of territory) — that
  reopens W1.
- **Never:** reading the store or a clock; a second predicate for fall or victory; retyping a shipped
  sector to carry the `Boss` flag as a side effect of this module.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `SeatOutcome.Read(world, seatId)` → `SeatReading` | `world-victory`, `world-fall`, `coarse-step` |
| `WorldTemplateCatalog.DominantSeatOf(templateId)` | `world-creation` (validation), `multiverse-surface` (show the target) |

## DESIGN-GATE §5 checklist

```
[x] Subsystems: world model (Core), template catalog, validation.
[~] Session boundary: covered by tasks/sessions/trade-network-idea-20260919.json; check not re-run.
[x] Read this session: see spec-world-state-vocabulary.md checklist.
[x] decisions.md checked: no lock on win detection.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run on this file; no HIGH.
[x] Verified against code: template sector types (no boss-lair in either template), z-home's type,
    Rule4Homeworld, the fade ownership write.
[x] Surrounding sections read (WorldTemplateCatalog.Build's first-light comment).
[x] Constraint tested by reading, not assumed: "retyping z-home moves goldens" follows from the hashed
    sector row carrying the type and band (WorldCanonical.cs:42-46); not measured by a suite run.
[x] No §2 invariant contradicted.
[x] Corrections propagated: the map's "Boss-flag seat" reading is corrected in the map's decisions
    section.
[x] No population pinned.
[x] No cache.
[x] No ordering-fixed criterion (both-at-once case is specified).
[x] No actor magnitude.
[x] No SOLID fork: one detector.
[x] No new cross-cutting rule needing a registry row.
```
