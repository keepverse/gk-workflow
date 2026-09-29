# Spec: `lawn-commander-seat`

**Program:** [`empire-progression`](../empire-progression-map.md) · **Wave C** · depends on:
[`commander-roster`](spec-commander-roster.md); `decisions.md` rows **P1** and **P2** from the map.
**Rulings honoured:** R-C1 (*"to enter the lawn run, the commander must on any base"*; exclusivity is the
deployment hierarchy's), R-C4 (duration XP on the lawn run only), and the place rule (*"only outside the
combat in lawn run"*). **Status:** spec, not reviewed, no build authorized.

## Objective

When a creature commander leads a lawn run, it should stand outside the board, earn the lawn's
duration XP and nothing else, and be unable to be anywhere else for that run.

The ideal said the XP mechanism *"already works"*. Read in code, it works for a **Bound** specimen only:

| Fact | Where |
|---|---|
| Duration XP reads `bound_active_ms` from the specimen's lawn session and pays `(ended − started) / interval × xp` | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.UniqueActors.cs:944-970` |
| The receipt is `INSERT OR IGNORE` + re-read + assert the same delta | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.UniqueActors.cs:973-996` |
| Run end pays every `ActiveBound` row of the match, then recovers it to `Roster` | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.UniqueActors.cs:1008-1035` (`TryRecoverActiveByMatchKey`) |
| A commander is never Bound: it has no board tile and no ptr | the lawn's own constraint; `commander-surface`'s "commander never on a tile" |
| The frozen leading commander never reaches the server; it is only a debug fold | `gk-core/src/FusionRpg.Core/Commanders/MatchCommanderSnapshotHolder.cs:35-45` |
| The deploy path's refusal branch is named and missing | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.UniqueActors.cs:177-185`, test canary `gk-core/tests/FusionRpg.Data.Tests/CreatureLawnDeployCommanderRefusalTests.cs:9-14` |

So the gap is a **seat**, not a new faucet.

## Design

### The seat is a deployment child (map D5, `decisions.md` P1)

A seated commander is one more child in the deployment tree, beside lawn Bound, delve slot, siege
combatant and expedition seat:

```
parent                                   child
roster / home                  ─────►    lawn commander seat (new)   no tile, no ptr, no kill credit
legion stationed in a sector   ─────►    lawn commander seat (new)   (after legion-commander)
```

Seating moves the specimen `Roster → ActiveBound` with the run's `match_key`, skipping `Deploying`
because there is no engine spawn to wait for. That single phase change buys every property R-C1 wants
from machinery that already ships:

- **One place at a time.** Delve, expedition and lawn-deploy admission already refuse a non-`Roster`
  specimen (`RpgStore.UniqueActors.cs:189-190` for the lawn). A seated commander cannot be sent anywhere
  else for the run.
- **Run end settles it.** `TryRecoverActiveByMatchKey` already pays duration XP and recovers every
  `ActiveBound` row of the match (`:1028-1031`). The seat needs no settlement code of its own.
- **No kill XP, automatically.** Kill credit requires the proven attacker ptr (`decisions.md` "Unique
  lawn XP receipts"). A seat has none, so R-C4's "duration only" is a consequence, not a rule to enforce.
- **It cannot die on the lawn.** Lawn death is keyed on ptr. A commander standing outside the board is
  never a board casualty.

### The seat session

A row in the existing `rpg_unique_lawn_sessions` with a new column `seat = 'commander'` (board Bound
rows get `'board'`, the default), `bound_active_ms = 0`, and no ptr. The receipt writer is reused
unchanged. The column is additive through the schema's existing `EnsureColumn` pattern
(`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs:778-780`), and it makes "is this a seat" an explicit fact rather
than an inference from a null ptr.

### Who is seated, and when (record-then-drain)

The injector freezes the leader at `board.start` from its session cache (never awaiting HTTP,
`gk-core/src/FusionRpg.Core/Commanders/MatchCommanderSessionCache.cs:5-7`). The server learns it from the
**MatchStarted fact**, which gains `leadingCommanderId` (additive payload field). On draining that fact
the server seats the specimen if the id resolves to a creature commander (`commander-roster`) and:

| Check | On failure |
|---|---|
| holds the role | seat refused, reason `seat.notCommander` |
| phase `Roster`, or a member of a legion that is stationed, not on a lane (the second after `legion-commander`) | `seat.notAtBase` |
| is not the active Patron | `seat.isPatron`: one creature does not run two aura economies at once, the same reasoning that refuses the Patron a lawn deploy (`RpgStore.UniqueActors.cs:172-175`) |

A refused seat is **recorded on the run, never a gate**: the run proceeds (commander-surface: *"no
pre-run web gate"*), the injector's frozen aura still applies for this match (it never reads live state
mid-run), and no duration XP is paid. Two async systems degrade to *"delayed or missing XP"*, never to
blocking the lawn. The default-commander picker (`commander-surface`) lists only creatures that would
pass these checks, so the gap between the cache and the seat is small.

### The canary branch

`TryBeginUniqueDeploy` (`RpgStore.UniqueActors.cs:150`) gains the branch its own comment asked for,
symmetric with the Patron one: a specimen holding this run's seat is refused with
`commander.cannot-deploy`, **before** the phase check, so the reason names the rule rather than a
phase. `CreatureLawnDeployCommanderRefusalTests` gets the case its header says it is waiting for.

A creature that holds the role but is **not** leading this run deploys like any unique. The restriction
belongs to the place and the run, not the role (the ideal's shape item 7).

### Cache triggers — §2.16

| # | Trigger | What moves | Refresh |
|---|---|---|---|
| T1 | `board.start` (key-set edge) | the seat enters `ActiveBound` | the MatchStarted drain itself; the seat is created there |
| T2 | Match end | the seat leaves | existing `TryRecoverActiveByMatchKey` |
| T3 | Default commander changed mid-run | nothing for this run | the frozen snapshot is the contract; tested that the seat does not move |
| T4 | Role revoked mid-run | nothing for this run | same; the seat settles normally at run end |

The injector's commander cache is global and refreshes as today. No per-entity cache is keyed by the
seat, because the seat has no ptr to key a lawn entity by.

## Seedsmith / generator

**None.** Runtime seating and XP.

## Tunables

None new. Duration XP rate and interval are the existing `progression.v{n}.json` values
(`RpgXpAwards.SpecimenBoundIntervalMs`/`SpecimenBoundIntervalXp`, read at
`RpgStore.UniqueActors.cs:952-953`). R-C4: *"no new tunable and no new faucet"*.

## ActorHub gate

**Consumes Hub only.** A seated commander's numbers are its specimen's, composed as any unique's. It
contributes to the side through its aura (`aura-skill`), and through nothing seat-shaped.

## Integer widths and the power ladder

XP is `long` and `checked`, inherited (`RpgStore.UniqueActors.cs:969-970`). No magnitude is added.

## Commands

```powershell
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~CommanderSeat|FullyQualifiedName~CreatureLawnDeployCommanderRefusal|FullyQualifiedName~UniqueLawn"
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~PvzActivity"
.\scripts\verify-change.ps1 -Paths <every touched path> -Session <session-id>
```

A live probe, if one is run, allocates and seats through the real `/api/commanders` and match path and
reads XP back through the `/api/unique` routes (`gk-core/src/FusionRpg.Server/UniqueActorEndpoints.cs:10`),
never through a debug bind (live-probe standard).

## Project structure

| Path | Change |
|---|---|
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CommanderSeat.cs` (new) | seat on MatchStarted drain, checks, refusal record |
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.UniqueActors.cs` | canary refusal branch |
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs` | `seat` column via `EnsureColumn` |
| `gk-fusion/src/FusionRpg.Injector/Match/MatchHost.cs` | MatchStarted payload carries the frozen `leadingCommanderId` |
| `gk-core/tests/FusionRpg.Data.Tests/CommanderSeatTests.cs` (new) | below |
| `gk-core/tests/FusionRpg.Data.Tests/CreatureLawnDeployCommanderRefusalTests.cs` | the commander case |

## Code style

```csharp
// Seat = the ordinary ActiveBound transition with no spawn to wait for. Same row, same settle path.
cmd.CommandText = """
    UPDATE rpg_unique_actors
       SET phase = $active, match_key = $mk, revision = revision + 1
     WHERE instance_id = $id AND phase = $roster;
    """;
```

## Testing strategy

1. **Seated and paid.** A seated commander at run end receives exactly one duration receipt and
   returns to `Roster`; a replayed MatchEnded pays nothing more.
2. **Never kill credit.** A run with kills attributes none to the seat.
3. **One place.** A seated commander is refused by expedition dispatch and delve admission for the run.
4. **Canary.** Deploying this run's seated commander as a lawn Bound is refused with
   `commander.cannot-deploy`; a role-holder not leading this run deploys normally.
5. **Refusals don't block the run.** Each seat check failing leaves the run playable and records its
   reason.
6. **Order-independent:** grant-role-then-set-default and set-default-then-grant-role both seat at the
   next `board.start`.
7. **T3/T4:** changing the default or revoking the role mid-run leaves the seat and its XP unchanged.

## Boundaries

- **Always:** reuse the receipt writer and run-end settle; record every refused seat.
- **Ask first:** the `seat` column and the MatchStarted payload field (schema and wire); letting a
  refused seat block a run.
- **Never:** a second XP path; a board tile for a commander; kill credit for a seat.

## Success criteria

- [x] `decisions.md` P1 and P2 landed 2026-09-18 (rows "Deployment hierarchy SSOT" and "Unique lawn XP receipts", amended).
- [ ] A creature commander leading a run earns duration XP only and is refused as a lawn Bound.
- [ ] The canary comment and test are replaced by the real branch and its case.

## Open questions

None.

## Self-audit — the debate

- **"`ActiveBound` for something not on the board is a lie in the phase name."** The phase means
  "deployed in a live child", and the seat is one. The alternative, a sixth phase, would need every
  admission path, the run-end settle and the FE to learn it, for no behavioural difference.
- **"Could the seat happen at default-selection time instead?"** No: the default is a preference for the
  *next* run and can change freely; only `board.start` commits a leader, which is why commander-surface
  freezes there.
