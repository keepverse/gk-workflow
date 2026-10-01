# Spec: `empire-level`

**Program:** [`empire-progression`](../empire-progression-map.md) · **Wave D** · depends on: external
`solid-enforcement` [`save-identity`](../solid-enforcement/spec-save-identity.md) (the `(SaveId, EmpireId)`
key and the re-keyed `TryApplyXpUnlocked`); `ai-empire-species` for Zomboss's feed only.
**Rulings honoured:** R19 of [spec-rulings-2026-09-18.md](../spec-rulings-2026-09-18.md): *"A new
empire-level track, fed by the empire's species level-ups. Each empire level grants free empire respecs
now, and is the hook reserved for later world-stage rewards. Zomboss's empire gets the same track."* R18
supplies what the grant is (free **empire** respecs, spent by [`respec-free-counter`](spec-respec-free-counter.md)).
**Status:** spec, not reviewed, no build authorized.

## Objective

An empire should grow as its species grow, and that growth should pay out something the player can use.
Today nothing sums an empire's progress. Each species has its own level, and there is no empire-wide
number. This module adds one: a level per empire, fed only by that empire's species levelling up. Each
new empire level pays out a grant. The first grant kind is free empire respecs. The grant list is the
place later world-stage rewards plug in.

What ships today, read in code:

| Piece | Where |
|---|---|
| A species level is an `rpg_actor_progression` row with `kind = 'species'`, keyed by `CreatureTypeId` | `gk-core/src/FusionRpg.Core/Progression/RpgProgression.cs:9-15`; table `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs:511-524` |
| Every XP write, for every kind, goes through one function, which reads state, applies the delta, writes the ledger row with `INSERT OR IGNORE`, and updates the row only if the ledger insert landed | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Progression.cs:169-244` (dedupe at `:206-207`) |
| Species XP reaches that function by exactly two paths: the per-placement award and the run-completion award | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Progression.cs:46-48` and `:116-119`. Expeditions level the specimen only, never the species (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Expeditions.cs:325-327`) |
| `RpgXpApply` emits one `LevelChangeEvent` per level crossed, `Direction` `up` or `down`, and keeps `HighestLevel` | `gk-core/src/FusionRpg.Core/Progression/RpgProgression.cs:170-248` |
| A species can **demote** (a negative award walks it down a level) | `gk-core/src/FusionRpg.Core/Progression/RpgProgression.cs:216-239` |
| The ledger is unique on `(player_id, kind, type_id, reason, dedupe_key)` | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs:545` |
| `ProgressionPipeline` is a static, **empty** handler list, and it runs **before** the ledger dedupe | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Progression.cs:18`, `:179-180` versus `:206` |
| The one shared cost curve, `first + (L−1)·step`, dispatched per kind | `gk-core/src/FusionRpg.Core/Progression/RpgProgression.cs:62-89` |
| A changed progression row is broadcast as `RpgProgressionUpdated { playerId, kind, typeId, revision }` | `gk-core/src/FusionRpg.Server/Program.cs:1779-1782` |

## Design

### The empire level is one more progression row, not a new store

The empire level is a row in `rpg_actor_progression` with a new kind, `RpgActorKinds.Empire = "empire"`
(new), and `type_id = 0`. One row per empire.

This is the same decision `species-xp` made for species (`gk-core/src/FusionRpg.Core/Progression/SpeciesProgression.cs:13-21`,
*"never a second store forking the ledger/retention/compaction/`LevelChangePipeline` that already exist"*).
The row gets the ledger, the dedupe, the level-change events, the revision counter, the REST reads and
the `RpgProgressionUpdated` broadcast for free.

The key comes from `save-identity`, which rebuilds this table with the primary key
`(save_id, empire_id, kind, type_id)` (`spec-save-identity.md` §"The classification", Tier A row). So
the empire row is keyed `(SaveId, EmpireId)` from its first build, as R3 requires. Nothing here keys an
empire by a player row.

`RpgActorKinds` is a closed vocabulary (`IsKnown`, `gk-core/src/FusionRpg.Core/Progression/RpgProgression.cs:24-25`).
Adding `Empire` makes six members. That is a reviewed change, and its pinned-membership test says why.

### What feeds it: one credit per species level, once ever

Inside `TryApplyXpUnlocked`, after the species row update has landed (`:221-241`), and only for
`kind == Species`:

```csharp
// gk-core/src/FusionRpg.Data/Sqlite/RpgStore.EmpireLevel.cs (new)
void CreditEmpireForSpeciesLevelsUnlocked(SqliteConnection db, EmpireRef owner, int speciesTypeId,
    long highestBefore, long highestAfter, long runId, string t, long? factId,
    List<RpgProgressionDirty> sideEffects)
{
    if (!SpeciesCreditsOwner(owner, speciesTypeId)) return;      // R1 side rule, below
    for (var level = highestBefore + 1; level <= highestAfter; level++)
    {
        var d = TryApplyXpUnlocked(db, owner, RpgActorKinds.Empire, 0, runId, t,
            delta: RpgXpAwards.SpeciesLevelUp,                        // (new) tunable
            reason: RpgXpReasons.EmpireSpeciesLevelUp,                // (new) "empire_species_level_up"
            dedupeKey: $"sp:{speciesTypeId}:L{level}",
            factId, payloadJson: null);
        if (d is { } item) sideEffects.Add(item);
    }
}
```

- **One place covers both XP paths.** Both species paths call `TryApplyXpUnlocked` (`:46`, `:116`), so
  the hook sits in the one function they share. A third path added later is covered without a change.
- **Once per (species, level), ever — keyed on `highest_level`, not on the ledger.** The credit pays
  exactly the levels in `(highestBefore, highestAfter]`, where both are the species row's own
  `HighestLevel` before and after `RpgXpApply.Apply` (`gk-core/src/FusionRpg.Core/Progression/RpgProgression.cs:170-248`
  keeps it; the row persists it as `highest_level`). A species that demotes from 5 to 4 and climbs back to 5
  never raises `highest_level` past 5, so it credits nothing the second time. **The ledger dedupe is not
  enough on its own, and this is why** (found by the strengthen pass): `rpg_xp_ledger` is tail-trimmed per
  actor by compaction (`TrimXpTailsCore`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Compaction.cs:541-560`, delete
  at `:674`, retain count `SealedCompactionPolicy.XpRetainTailPerActor`). The empire row is one actor that
  gains a ledger row per species level, so its oldest `sp:{id}:L{n}` keys are exactly the ones compaction
  removes, after which a demote-and-reclimb would pay again. `highest_level` lives on the species row and is
  never trimmed. The dedupe key stays as the replay guard inside one transaction, and it keeps the ledger
  readable (`sp:{id}:L{n}` says what was paid).
- **A replay credits nothing.** A replayed species award is dropped by the species ledger's own
  `INSERT OR IGNORE`, and `TryApplyXpUnlocked` returns before the row update (`:206-207`), so the credit is
  never reached.
- **Side effects travel with the caller.** The nested empire call returns its own `RpgProgressionDirty`.
  `TryApplyXpUnlocked` gains an optional collector that the credit appends to, and both species callers
  (`:46-53`, `:116-120`) add the collected dirties to their `dirty` list and to `_progressionNotifyBatch`
  exactly as they add their own. `EmpireLevelUp` events (below) are queued the same way and broadcast by the
  host **after commit**, never from inside the transaction (record-then-drain).
- **R1 side rule.** `SpeciesCreditsOwner(owner, typeId)` is true only when the species' side maps to that
  empire through the one existing mapping, `KillAttribution.EmpireOf(side)`
  (`gk-core/src/FusionRpg.Core/Battle/KillAttribution.cs:58-59`). Ruling R1 gives zombie species to Zomboss's
  empire and plant species to the player's. So the human's pre-R1 zombie species rows, which
  `ai-empire-species` leaves as history on the human empire, never raise the human's empire level, live
  or by backfill; and the order in which `empire-level` and `ai-empire-species` land stops mattering.
- **Not a `LevelChangePipeline` handler.** The pipeline runs before the ledger dedupe (`:180` versus
  `:206`), so a handler would fire again on a replayed fact. The credit is written after the species
  ledger row is known to have landed, in the same connection and transaction. The pipeline stays
  empty; this module does not register anything in it.
- **Same owner as the species.** `owner` is the species row's own `EmpireRef`. A plant species credits
  the player's empire, a zombie species credits Zomboss's (ruling R1, delivered by `ai-empire-species`).
- **The empire row never demotes.** Every credit is positive. Its `DemotionCount` stays 0.

### The level curve: the one shared cost ladder, row 6's function

The empire level reads `RpgXpCurve.XpToNext(RpgActorKinds.Empire, level)`
(`gk-core/src/FusionRpg.Core/Progression/RpgProgression.cs:82-89`), with its own `(first, step)` pair added to
`ParamsFor` (`:62-74`). **No new `f(level)` is written.**

This is `ssot-power-scale.md` §10.1 **row 6**'s function: the arithmetic *cost* ladder `first + (L−1)·step`,
kept because only its ratio against `P(Θ)` matters (§10.5). Rows 26 (species) and 27 (specimen) are
the precedent: each is row 6's function with its own tunable pair, recorded as its own row. This
module owes the same: a **§10.1 row for the empire level, at the next free ordinal when it lands**
(37 is the highest today, so 38 unless another lands first). The row says:

| Scale | Shape | Location | Verdict |
|---|---|---|---|
| Empire level, `kind = 'empire'` on `rpg_actor_progression` | arithmetic, identical shape to row 6 | `RpgXpCurve.ParamsFor` (`xpCurve.empire` in `progression.v{n}.json`) | A *cost* ladder whose unit is species level-ups. **It never feeds `Θ` or `P(Θ)`**: an empire level grants respecs (and later world-stage rewards), never a magnitude. If a later grant ever reaches a magnitude, it does so through an existing row, never through this level |

**PS-5x holds trivially.** The award (`speciesLevelUp`) and the curve are both flat. Neither is scaled
by content. If one is ever scaled, the other moves with it (§10.5).

### Level-up grants: a closed list, the world-stage hook

When the empire row itself crosses a level, the store asks one pure function what that level pays:

```csharp
// gk-core/src/FusionRpg.Core/Progression/EmpireLevelGrants.cs (new)
public enum EmpireLevelGrantKind { FreeEmpireRespec }       // closed; one member today

public readonly record struct EmpireLevelGrant(EmpireLevelGrantKind Kind, long Amount);

public static class EmpireLevelGrants
{
    /// What reaching `levelAfter` grants. Pure, no I/O, deterministic.
    public static IReadOnlyList<EmpireLevelGrant> For(long levelAfter, EmpireLevelTuning tuning) =>
        tuning.FreeRespecsPerEmpireLevel > 0
            ? [new EmpireLevelGrant(EmpireLevelGrantKind.FreeEmpireRespec, tuning.FreeRespecsPerEmpireLevel)]
            : [];
}
```

The hook is the mirror of the species one: inside `TryApplyXpUnlocked`, after the row update has landed,
for `kind == Empire` only, each `LevelChangeEvent` with `Direction == "up"` calls
`EmpireLevelGrants.For(e.LevelAfter, …)` and applies each grant. The empire row never demotes, so every
empire level is crossed once. The Data layer applies each grant in the same transaction as the empire
level change, with the dedupe key `L{levelAfter}`:

| Grant kind | Applied by | Where it lands |
|---|---|---|
| `FreeEmpireRespec` | `respec-free-counter` | `rpg_empire_free_respec_ledger` (new there), `+Amount`, reason `empire-level` |

**The world-stage hook is this enum.** A world-stage reward is a new `EmpireLevelGrantKind` member plus
its applier, added by the program that specs it. That is a reviewed change to a closed vocabulary with a
pinned-membership test, like `RpgActorKinds`. This module names the extension point and builds only the
one member R19 asks for now. It does not invent a placeholder member.

**Grants are keyed by level, not by time.** A level already paid is never paid again (`L{n}` dedupe),
and a grant is never taken back. Lowering `freeRespecsPerEmpireLevel` changes only future levels.

### Existing saves: a backfill through the same credit

A save that already has species levels would otherwise start at empire level 1 while its species sit
at level 30. At store start, before the host serves a request, a catch-up pass runs **for each empire
that has no `kind = 'empire'` row yet**. In one transaction per empire it walks that empire's species
rows and calls the same `CreditEmpireForSpeciesLevelsUnlocked` with `highestBefore = 1` and
`highestAfter = highest_level`, so the same side rule and the same dedupe keys apply. So:

- the result equals what live play would have produced, level for level;
- **it is idempotent by construction, not by the ledger.** The first credit creates the empire row, so
  once the pass has committed for an empire, the "no row yet" test is false and the pass never runs
  there again, even after compaction has trimmed the ledger. A crash mid-pass rolls the whole empire's
  transaction back, so the next start re-runs it from clean;
- it cannot collide with live credits: it runs before any request, and every later live credit pays only
  levels above the species' `highest_level`, which the pass has already covered;
- an empire whose species are all at level 1 gets no row and no work; its first live level-up creates
  the row, and there was nothing to catch up;
- the empire's grants for those levels are paid by the same grant path.

`highest_level` is the right input, not `level`: a demoted species has still earned its highest level
once, and live play would have credited it.

### Zomboss parity (R19)

Zomboss's empire gets the same row, curve, credit and grants, because the credit reads the species row's
own `EmpireRef`. Two saves hold two independent Zomboss empire levels (R3).

**What Zomboss's grants buy.** Nothing yet. An AI empire has no respec surface
(`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.SpeciesRespec.cs:155-159`; `spec-ai-empire-species.md`). Its
free respec stock accrues and is readable, and it is where `ai-build-scorer` could draw from later.
Nothing here spends it.

**Until `ai-empire-species` lands,** zombie species XP still credits the human's rows. The side rule
keeps those levels off the human's empire level, and Zomboss's empire level stays at 1. That is correct
for that interval, and it moves when R1's routing lands. Nothing is migrated then: Zomboss's zombie
species start their own rows at level 1, and his empire level follows them live.

### Contracts: REST and SignalR

| Surface | Shape | Notes |
|---|---|---|
| `GET /api/players/{playerId}/empires/{empireId}/level` (new) | `{ empireId, level, xp, xpToNext, highestLevel, freeRespecStock, freeRespecsPerLevel }` | `playerId` is the `SaveId` (R17). `freeRespecStock` is read from `respec-free-counter`'s ledger |
| `GET /api/rpg/progression/{playerId}/empire/0` (existing route, `gk-core/src/FusionRpg.Server/Program.cs:1104`) | the raw progression row | works once `IsKnown` accepts `empire` |
| `RpgProgressionUpdated` (existing, `gk-core/src/FusionRpg.Server/Program.cs:1779-1782`) | `kind: "empire"` | fires on every credit, like any row |
| `EmpireLevelUp` (new) | `{ playerId, empireId, levelBefore, levelAfter, grants: [{ kind, amount }], freeRespecStock }` | once per empire level crossed. A player-facing notice for it is `notification-ssot`'s to render (R14); this module only emits |

**The unfiltered progression list gains a row.** `ListRpgProgression` with no `kind` returns every kind
(`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Progression.cs:414`, `:819`). Any FE list that assumes only
`player`/`plant`/`zombie`/`species`/`specimen` must filter by kind. The build greps the FE for unfiltered
reads and filters them; a test covers the list.

The injector needs nothing. An empire level is not an actor number and never reaches Unity.

## Tunables

`data/tuning/progression.v{n+1}.json`, published, never hand-edited:

```powershell
python gk-core/tools/tuning/publish.py progression --label "R19 empire level" `
  --add-key 'xpCurve:empire={"first":10,"step":5}' `
  --add-key 'awards:speciesLevelUp=1'
```

- `xpCurve.empire.first`, `.step`: species level-ups (the XP unit of this row is one species level).
  Working values: level 2 at 10 species level-ups, then 15, 20 and so on. Not a balance decision.
- `awards.speciesLevelUp`: empire XP per species level reached, `long`, ≥ 1.
- `ProgressionTuningLoader` (`gk-core/src/FusionRpg.Core/Progression/ProgressionTuning.cs:59-72`) reads both. A
  missing key is a load rejection naming it (tunables-ssot T5), so after this change **v1 no longer
  loads** and every pin of the old version must move in the same change. The pins are found by search,
  not by a list in this spec: `rg -l "progression\.v1\.json" src tools tests --glob "*.cs"`. On
  2026-09-18 that search hits `gk-core/src/FusionRpg.Server/Program.cs:137`, `gk-forge/tools/ProveHubCombat/Program.cs:94`,
  `gk-forge/tools/_TempSeedSpecies/Program.cs:112` (its owner decides move or delete) and the Server test fixtures
  (for example `gk-core/tests/FusionRpg.Server.Tests/AptitudeEndpointsTests.cs:42`); a doc comment naming v1 is
  not a pin.
- **Version.** One version, one publisher. `species-progression` `zomboss-commander-clock` and
  `creature-lawn-deploy` `lawn-deploy-progression` also publish into `progression`; none of the three pins
  a number. Each takes the next free version at landing and lands its keys on top of the previous file
  through the tool. The map's "Tuning version sequence" table is the record.
- `freeRespecsPerEmpireLevel` is **not** here. It prices the respec economy and is published by
  `respec-free-counter` into `species-build.v{n+1}.json`. `EmpireLevelTuning` is the small record the
  grant function reads, assembled at host wiring from that key.

**Landed 2026-09-21 (Core half, `empire-progression-3`) — one recorded deviation, closed the same day.** The Core half ships:
`RpgActorKinds.Empire`, `RpgXpReasons.EmpireSpeciesLevelUp`, the `ParamsFor` arm, `RpgXpAwards.SpeciesLevelUp`,
`EmpireLevelGrants`/`EmpireLevelGrantKind`/`EmpireLevelTuning`, and a `ProgressionTuning` that reads both keys.
In EP4.1 the two keys were **presence-tolerant at parse and refused by name at first use**
(`RpgXpCurve.ParamsFor(RpgActorKinds.Empire)`, `RpgXpAwards.SpeciesLevelUp`), **not** a parse-time requirement as
the paragraph above says. Reason, checked against code: `progression` is a multi-publisher domain whose pins are
literal version paths with **no "find latest" resolver** — the live host was `gk-core/src/FusionRpg.Server/Program.cs`
reading `progression.v2.json`, and ~30 test fixtures pinned `progression.v1.json`. A parse-time requirement in
EP4.1 would therefore have made the shipped server unloadable in the commit that added the key, before the publish
moved the pins. It was the discipline `XpAwardsTuning.ZombossRunVictoryXp` already uses in `ProgressionTuning.cs`,
and nothing was silently defaulted (absent stayed `null`; the read threw naming the key).

**EP4.2 closed the deviation, so the paragraph above is now the shipped behaviour.** That commit published
`progression.v3.json` with `xpCurve.empire` and `awards.speciesLevelUp`, moved every pin of the previous version in
the same commit (`gk-core/src/FusionRpg.Server/Program.cs`, `gk-forge/tools/ProveHubCombat`, `gk-forge/tools/_TempSeedSpecies` and every test
fixture — H7), and **made both keys REQUIRED at parse** (tunables-ssot.md T5: a missing tunable is a load rejection
naming it). `progression.v1.json` and `progression.v2.json` therefore no longer load as documents; they stay on disk
so a revert is a file restore, never a re-publish. The first-use refusal survives only for an in-code
`ProgressionTuning` a test bootstrap built without the keys, which is still refused by name rather than read as 0.

## ActorHub gate

**Not applicable.** The empire level is not an actor magnitude and has no Hub contributor. A grant that
someday affects combat does so through an existing layer and its own SourceId, never through this row.

## Integer widths

`long` for level, XP and award, as for every progression kind (`gk-core/src/FusionRpg.Core/Progression/RpgProgression.cs:132-140`).
`checked` arithmetic is already in `XpToNext` and `Apply` (`:87`, `:188`). The empire's XP total is at
most `speciesLevelUp` times the sum of all species levels, far below `long` range.

## Seedsmith / generator

**None.** Runtime attribution over existing rows.

## Commands

```powershell
python gk-core/tools/tuning/publish.py progression --add-key 'xpCurve:empire={"first":10,"step":5}' --add-key 'awards:speciesLevelUp=1'
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~EmpireLevelGrants|FullyQualifiedName~RpgActorKinds|FullyQualifiedName~ProgressionTuning"
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~EmpireLevel"
python gk-core/scripts/guard-power.py
.\scripts\verify-change.ps1 -Paths <every touched path> -Session <session-id>
```

## Project structure

| Path | Change |
|---|---|
| `data/tuning/progression.v{n+1}.json` (new) | published |
| `gk-core/src/FusionRpg.Core/Progression/RpgProgression.cs` | `RpgActorKinds.Empire`, `RpgXpReasons.EmpireSpeciesLevelUp`, `ParamsFor` arm, `RpgXpAwards.SpeciesLevelUp` |
| `gk-core/src/FusionRpg.Core/Progression/ProgressionTuning.cs` | `EmpireCurve`, `Awards.SpeciesLevelUp` |
| `gk-core/src/FusionRpg.Core/Progression/EmpireLevelGrants.cs` (new) | the grant enum and pure function |
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.EmpireLevel.cs` (new) | the credit, the grant application, the backfill |
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Progression.cs` | one call to the credit inside `TryApplyXpUnlocked` for `kind == Species` |
| `gk-core/src/FusionRpg.Server/EmpireEndpoints.cs` (new, or `save-identity`'s empires route file if it exists) | the level read, the `EmpireLevelUp` broadcast |
| `gk-core/src/FusionRpg.Server/Program.cs`, `gk-forge/tools/ProveHubCombat/Program.cs` | `progression` pin moved |
| `docs/architecture/power/ssot-power-scale.md` | the §10.1 row, in the same change |
| `gk-core/tests/FusionRpg.Core.Progression.Tests/Progression/EmpireLevelGrantsTests.cs` (new), `gk-core/tests/FusionRpg.Data.Tests/EmpireLevelTests.cs` (new) | below |

## Code style

The credit snippet above is the style: the existing XP function reused with a new kind, dedupe keys that
say what they deduplicate, and the Data layer doing the write inside the caller's transaction.

## Testing strategy

Every assertion reads the curve and award from the loaded tuning, never a literal.

1. **Both paths credit.** A placement award and a run-completion award that each level a species once
   produce one empire credit each, with the expected dedupe keys.
2. **Once per level, ever.** Level a species to `n`, demote it, re-level it to `n`: the empire XP is the
   same as a single climb to `n`. **Run the same case again after deleting the empire's `sp:*` ledger rows**
   (what compaction does): still no second credit, because the rule reads `highest_level`.
2b. **Side rule (R1).** A zombie species row owned by the human empire levels up: the human's empire row
   does not move. A plant species on the human empire and a zombie species on Zomboss's each credit their
   own empire.
2c. **Side effects are drained after commit.** One award that levels a species and the empire returns
   both dirties to the caller and queues one `EmpireLevelUp`; a rolled-back transaction broadcasts none.
3. **Replay is harmless.** Replaying the same activity fact changes neither the species nor the empire row.
4. **Multi-level awards.** One award that crosses `k` species levels credits `k` times.
5. **The curve is the shared one.** The empire levels exactly when `RpgXpCurve.XpToNext(Empire, L)` says,
   for `L` in a range read from tuning; no other curve function exists (a `guard-power` run, and a
   reflection test that `EmpireLevelGrants` declares no level-shaped method).
6. **Grants.** Crossing `k` empire levels writes `k` `FreeEmpireRespec` grants of
   `freeRespecsPerEmpireLevel` each, keyed `L{n}`. `freeRespecsPerEmpireLevel = 0` writes none.
7. **Closed enums.** `RpgActorKinds` has 6 members and `EmpireLevelGrantKind` has 1. Both are pinned, with
   the reason in the test: each is a code-owned vocabulary whose growth is a reviewed change.
8. **Zomboss parity.** Once `ai-empire-species` routes zombie species XP, a zombie species level-up
   credits `EmpireRef(save, zomboss)`, never the human's empire; two saves hold independent Zomboss
   empire levels.
9. **Backfill equals live play.** For a store seeded with species at assorted highest levels, the backfill
   produces the same empire row and grants as crediting those levels live. A second start changes nothing,
   including after the empire's ledger rows are deleted (compaction). A pass that throws midway leaves no
   empire row, and the next start completes it.
10. **Unfiltered lists.** The unfiltered progression list includes the empire row, and every FE reader
    that must not show it filters by kind (a vitest over the fold).

No test asserts a count of species, a count of empire levels in a real save, or a grant total over the
corpus.

## Boundaries

- **Always:** credit through `TryApplyXpUnlocked`; key by `EmpireRef`; one curve function; grants from the
  closed enum.
- **Ask first:** feeding the empire level from anything other than species level-ups; a grant kind that
  is not a free empire respec.
- **Never:** a new `f(level)`; a `LevelChangePipeline` handler for the credit; let the empire level reach
  `Θ` or `P(Θ)`; take a grant back.

## Success criteria

- [ ] `progression.v{n+1}.json` published and every pin moved.
- [ ] A species level-up on either path raises its own empire's level on the shared curve.
- [ ] Each empire level-up writes its grants once.
- [ ] Zomboss's empire has its own track in every save.
- [ ] The §10.1 row landed in `ssot-power-scale.md`.
- [ ] `verify-change.py` and `guard-power.py` green.

## Open questions

None. R19 fixed the feed, the grant and Zomboss's parity.

## Self-audit — the debate

- **"Sum the species levels at read instead of storing an empire row."** Then a level-up has no moment:
  nothing could pay a grant exactly once, and the dedupe that stops demotion farming would have nothing
  to key on. A stored row with a ledger is what makes "one grant per level-up" true.
- **"Use per-level dedupe keys alone; `highest_level` is a second rule."** The first draft did exactly
  that, and it is wrong in this repo: the ledger is tail-trimmed by compaction, so a key the rule depends
  on can disappear. `highest_level` is already read (`ReadActorStateUnlocked`) and never trimmed, so it
  costs nothing and survives compaction. The dedupe key stays as the in-transaction replay guard.
- **"Weight a species level by the species' rarity or threat rung."** R19 says fed by level-ups, not by
  whose. A weight is a balance idea, and a later tuning publish can add one without a schema change. It
  is not built now.
- **"A new table would be cleaner than a sixth progression kind."** It would be a second store for the same
  shape (level, XP, ledger, dedupe, broadcast), which is what `species-xp` refused for the same reason.
- **"The backfill hands veterans a pile of free respecs at once."** It hands them what live play would
  have handed them. Not backfilling would mean an empire level that disagrees with the species levels on
  the same screen.
