# spec — `zomboss-commander-clock`

**Module 7 of `species-progression`** ([map](../species-progression-map.md)). Depends on external
`solid-enforcement` `save-identity` (R3). **Q3 is answered by R3**
([spec-rulings-2026-09-18.md](../spec-rulings-2026-09-18.md)): neither one global row nor one row per
human player — Zomboss's level lives on **Zomboss's empire of the save**, keyed `(SaveId, EmpireId)`.
Status: spec, 2026-09-18, R3 applied the same day, strengthened the same day (seam names aligned with
`save-identity`, tuning version sequenced, R19 distinguished); **R23** applied the same day (session
`rulings-r20-r24-20260918`): the level this clock raises also sizes **Zomboss's commander pool**, whose
assign-ladder default applies side-wide to his members — built by `empire-progression`
[`ai-empire-species`](../empire-progression/spec-ai-empire-species.md), read through this module's seam. No build authorized until the map is
reviewed and `save-identity` has landed.

## Objective

R-S2 part 1, in the owner's words: *"for now, only lawn run can ship, so in lawn run, the zomboss
commander (current is him) will level up by play the game, we already define player win/lose the run,
number of run."* And the ideal's reading of it: *"This program wires Zomboss's commander level to the
run outcome; it does not author a scale."*

So: every **resolved** lawn run advances Zomboss's commander level through the **existing** XP machinery
— one award when Zomboss wins the run (the human's defeat), a different one when he loses (the human's
victory) — and that level becomes readable as the `zombossLevel` input `Θ_content` already declares.

**What already exists and is reused, not rebuilt:**

| Piece | Where |
|---|---|
| The axis | `Θ_content = Wz·zombossLevel + …`, `Wz = 1000` (`ssot-power-scale.md` §5, §5.3); composed at `PowerIndexComposer.cs:71` from `ContentContext.ZombossLevel` (`ContentContext.cs:16`) |
| The run outcome | `PvzActivityKinds.NormalizeMatchResult` → `victory` / `defeat` (`PvzActivityKinds.cs:55-65`), already read for the human at `RpgXpAwardMap.cs:57-61` |
| The XP writer and its cost ladder | `TryApplyXpUnlocked` (`RpgStore.Progression.cs:169`), the `player`-kind `RpgXpCurve` row (`ssot-power-scale.md` §10.1 row 6 — a cost ladder, not a power ladder) |
| Zomboss's identity | **today** a `players` row found or created **by name** (`RpgStore.ZombossDeploy.cs:13`, `:25-29`), shared by every save. R3 retires that: Zomboss becomes an empire of each save, `(SaveId, EmpireId.Zomboss)`, and stops being a player row. This module is written against the R3 identity, never the by-name row |

**What does not exist, and is honestly out of reach here:** no production code constructs a
`ContentContext` or `ParentWorldTerms` from live state (`DelveStart.cs:48-52` names the gap;
`RoomTheta.cs:12` is the only reader and is fed test literals). This module makes the level **exist and
be readable**; wiring a consumer is the delve program's (`ParentWorldTerms`) and `lawn-tuning-profile`'s
(lawn zombie Θ). ~~Until one of them reads it, Zomboss levelling changes nothing a player sees~~ —
**R23 (2026-09-18) adds a consumer:** Zomboss's commander pool `zomboss:{save}` — keyed
`(SaveId, EmpireId.Zomboss)` per `save-identity` — gets the assign-ladder's computed default at the budget
his commander level implies, and applies **side-wide to his members** exactly as the player's pool does
under R4 (symmetric empires). So once `ai-empire-species` lands, each level this clock awards strengthens
every Zomboss-side actor's `Commander` layer (resolved alone, R16; scaled by the commander layer weight,
R21). This module still writes only the level; it reads no allocation and writes none.

## Where the level lives — Zomboss's empire of the save (R3)

The owner, asked "one global row or one per save", answered neither: *"did we count empire as player?
If true we need to escalate a new save identity instead of overlapping the role of player."* Confirmed
in code: an empire **is** a player row today, and Zomboss is a second player row found by name
(`RpgStore.ZombossDeploy.cs:25-29`) that every save shares. The ruling: **a Save owns its empires**
(Dave's, Zomboss's, later AI), each keyed `(SaveId, EmpireId)`.

| | Before R3 (both options the map offered) | This module, under R3 |
|---|---|---|
| Key | `players.id` of the by-name row (A), or a Zomboss `players` row per human (B) | `(SaveId, EmpireId.Zomboss)` |
| Storage | `rpg_actor_progression(player_id, kind = 'player', type_id = 0)` | the empire-keyed commander-level store `save-identity` provides. The player's commander level is an empire's level too, so it moves with the same migration; this module adds **no** table of its own |
| Read seam | `GetZombossLevel()` / `GetZombossLevel(humanPlayerId)` | `CommanderLevelOf(SaveId save, EmpireId empire)` — the consumer asks for Zomboss's empire of its own save |
| Which save a run belongs to | implicit: the human's `playerId` | resolved from the run through `save-identity`. A run whose save cannot be resolved awards nothing and is reported, never credited to a guessed save |

The read seam takes both keys and uses both — a parameter that is accepted and ignored is exactly the
defect T4.4 found in `SpeciesBaselineAllocation` (`spec-species-empire-scope.md` §"A fourth seam").
T4.1's interim key, Zomboss's allocations under the **human** player id (`SpeciesAllocation.cs:28-31`),
is also re-keyed by `save-identity`, not by this module.

## Commands

```powershell
dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~ZombossCommanderClock|FullyQualifiedName~Progression"
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~ProgressionTuning|FullyQualifiedName~PowerIndexComposer"
python gk-core/tools/tuning/publish.py progression --add-key "awards:zombossRunVictoryXp=100" --add-key "awards:zombossRunDefeatXp=25" --label "zomboss-commander-clock working values"
python gk-core/scripts/guard-dal.py
.\scripts\verify-change.ps1 -Paths <every changed file> -Session <session-id>
```

(`--add-key` is repeatable — `action="append"`, `gk-core/tools/tuning/publish.py:453` — so one call publishes both
keys as one new version, verified 2026-09-18.)

## Project Structure

| Path | Change |
|---|---|
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Progression.cs` | after the run-completion block (`:57-64`), in the same transaction: the Zomboss award |
| `gk-core/src/FusionRpg.Core/Progression/RpgProgression.cs` | `RpgXpReasons.ZombossRunVictory = "zomboss_run_victory"`, `ZombossRunDefeat = "zomboss_run_defeat"`; `RpgXpAwards` reads the two new tunables |
| `gk-core/src/FusionRpg.Core/Progression/ProgressionTuning.cs` | loads the two keys; a missing key is a load rejection naming it (`tunables-ssot.md` T5) |
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.ZombossDeploy.cs` | none by this module. `EnsureZombossPlayer`'s retirement is `save-identity`'s |
| the `save-identity` empire-progression seam (path owned by that spec) | the award writes through its re-typed `TryApplyXpUnlocked(db, EmpireRef owner, kind, typeId, …)`; the level is read through `CommanderLevelOf(SaveId, EmpireId)` |
| `data/tuning/progression.v{n+1}.json` | **published by the tool**, never hand-written. `n` is whatever `progression` version is current at build: `empire-progression` `empire-level` (R19) and `creature-lawn-deploy` `lawn-deploy-progression` also publish into this domain, so no spec pins a version number — each publish is `publish.py`'s next version, and the three are never merged into one hand-assembled file |
| `gk-core/tests/FusionRpg.Data.Tests/ZombossCommanderClockTests.cs` | **(new)** |

## Behaviour

1. **Only a resolved lawn run counts.** `factKind == MatchEnded`, `runId != 0`, `pvzGame == true`
   (the method's own flag, `RpgStore.Progression.cs:20-22`), and the normalised result is `victory` or
   `defeat`. Anything else — no result, an unrecognised string, a web-mode match — awards nothing. R-S2:
   *"only lawn run can ship"*.
2. **Victory for Zomboss is defeat for the human.** Human `defeat` → `awards.zombossRunVictoryXp`;
   human `victory` → `awards.zombossRunDefeatXp`. Both positive: losing still advances the antagonist's
   clock (*"number of run"*), winning advances it faster.
3. **Exactly once per run.** Dedupe key `zomboss-run:{runId}`; a replayed `MatchEnded` fact writes nothing
   (the ledger's existing dedupe, as `run-complete:{runId}:{speciesId}` already does at `:115`).
4. **Same cost ladder as Dave.** Zomboss's `player`-kind row levels on `RpgXpCurve`'s `player` row. No new
   curve, no new kind — `empire-progression-ideal.md` forbids adding a commander member to
   `RpgActorKinds`, and this needs none.
5. **Not rubber-banding.** The clock reads run outcome and count only, never the human's power — R-S2
   part 2 puts any player-scaled "cheat" in its own program, and the RimWorld wealth-scaling failure the
   ideal records is exactly what this avoids.

## Code Style

```csharp
// RpgStore.Progression.cs, after the run-completion block
if (factKind == PvzActivityKinds.MatchEnded && pvzGame && runId is { } zr && zr != 0)
{
    var outcome = PvzActivityKinds.NormalizeMatchResult(result);
    var (delta, reason) = outcome switch
    {
        "defeat"  => (RpgXpAwards.ZombossRunVictoryXp, RpgXpReasons.ZombossRunVictory),
        "victory" => (RpgXpAwards.ZombossRunDefeatXp,  RpgXpReasons.ZombossRunDefeat),
        _ => (0L, null),                                   // unresolved run: the clock does not move
    };
    if (reason is not null)
    {
        // R3: the run's save, then Zomboss's empire of that save. Never a player row.
        // `save` is this method's own first parameter once save-identity re-types it; that module
        // asserts save == SaveOfRunUnlocked(runId) whenever runId is set, so no second lookup here.
        var owner = new EmpireRef(save, EmpireId.Zomboss);
        if (EmpiresOf(save).Any(e => e.Empire == owner.Empire))       // the save owns a Zomboss empire
        {
            var d = TryApplyXpUnlocked(db, owner, RpgActorKinds.Player, typeId: 0, zr, t,
                delta, reason, $"zomboss-run:{zr}", factId);          // same ledger + dedupe semantics
            if (d is { } item) { dirty.Add(item); _progressionNotifyBatch?.Add(item); }
        }
        else ReportMissingEmpire(save, owner.Empire);                 // never a guessed empire
    }
}
```

## Testing Strategy

- **Each outcome, one test:** human defeat → Zomboss gains `zombossRunVictoryXp`; human victory →
  `zombossRunDefeatXp`; no/unknown result → nothing; web-mode (`pvzGame == false`) → nothing.
- **Idempotence:** the same `MatchEnded` fact twice → one award.
- **Identity (R3):** the award lands on `(SaveId, EmpireId.Zomboss)` of the run's save — never on the
  human's row, never on the by-name `players` row, never on a literal id. Two saves' runs advance two
  different Zomboss levels; a run in save A leaves save B's Zomboss unchanged.
- **Unresolved save:** a fact whose run resolves to no save awards nothing and reports (`save-identity`'s
  rule for every award; asserted here for this award).
- **Missing empire:** a save with no Zomboss empire row awards nothing and reports — never a row created
  on the fly (save empires are created only at save creation and migration, `save-identity` T4).
- **Level-up through the existing curve:** enough runs raise the level by the `player` row's
  `first + (L−1)·step`, asserted against the curve function, not a literal level.
- **Read seam:** `CommanderLevelOf(save, EmpireId.Zomboss)` returns that empire's level; the narrowing into `ContentContext`'s `int`
  field is `checked` (a level past `int` throws, never clamps).
- **R23 consumer contract:** the same seam is the only level `ai-empire-species`' Zomboss commander pool
  reads — a guard test asserts no second Zomboss commander-level reader (the pool's side-wide tests live
  in `ai-empire-species`, tests 10–14).
- **Tunables:** a `progression` file missing either key is rejected at load, naming the key.

## Numeric

XP and level are `long` end to end (`ssot-power-scale.md` §10.1 row 6). `ContentContext.ZombossLevel` is
`int` (`ContentContext.cs:16`); the narrowing at the read seam is `checked` and reported, never silent.
`Θ_content`'s arithmetic is the power program's (`PowerIndexComposer.cs:71`), unchanged.

## Tunables

| Key | File | Unit | Working value | Why this value |
|---|---|---|---|---|
| `awards.zombossRunVictoryXp` | `data/tuning/progression.v{n+1}.json` | XP per resolved run | 100 | equals `species-progression.v1.json` `awards.runCompletion`, the repo's existing per-run award |
| `awards.zombossRunDefeatXp` | same | XP per resolved run | 25 | a quarter of the win award, so the count of runs still moves the clock |

**Working values, not a balance decision** — the same standing `ssot-power-scale.md` §5.3 gives the
ladder weights (*"pick numbers now, tune from play"*). They live in `progression` rather than
`species-progression` (as the ideal's Tunables table suggested) because they are `player`-kind XP
awards, and `progression.v1.json` `awards` owns that concept — `tunables-ssot.md` §2: a number belongs to
*"whichever owns the concept"* (map C8).

**Not the empire level (R19).** R19 adds an **empire-level** track (`empire-progression` `empire-level`,
`kind = 'empire'`), fed by the empire's species level-ups and granting free respecs, and gives Zomboss's
empire the same track. That is a different row and a different feed from this clock: this module levels
Zomboss's **commander** (`kind = 'player'`, type 0) from run outcomes, which is what `Θ_content`'s
`zombossLevel` reads (R-S2). Neither writes the other's row; neither module reads the other's level.

## Seedsmith / generator

No generator involved.

## ActorHub gate

No actor contribution **from this module**. The level is a `Θ_content` input and, by R23, the source of
Zomboss's commander budget; the resulting `Commander`-scope contribution is composed by `rpg.aptitude`
from `ai-empire-species`' read (one ActorHub compose), and any magnitude derived from the level goes
through `P(Θ)` in its consumer's program, never here.

## Boundaries

- **Always:** reuse the XP ledger's dedupe semantics and the `player` cost curve; resolve Zomboss as an
  empire of the run's save; publish tunables through `gk-core/tools/tuning/publish.py`.
- **Ask first:** any consumer wiring (delve, lawn) — those are other programs'.
- **Never:** scale the clock by the human's power; award from a web-mode match; key on a literal id, a
  player row or the by-name Zomboss row; add an empire-level table beside `save-identity`'s; hand-edit a
  tuning file.

## Success Criteria

- [x] Q3 answered: R3, `(SaveId, EmpireId)` ([spec-rulings-2026-09-18.md](../spec-rulings-2026-09-18.md)).
- [ ] Every resolved lawn run advances its save's Zomboss commander level exactly once, by outcome.
- [ ] The level is readable through one seam keyed `(SaveId, EmpireId)`.
- [ ] Two new tunables, published, loaded with rejection on absence.

## Open Questions

None for the owner. One dependency: the empire-keyed commander-level store and the run→save mapping are
`save-identity`'s to specify; this module consumes both and blocks on them.

## Rulings applied 2026-09-18

Source: [spec-rulings-2026-09-18.md](../spec-rulings-2026-09-18.md). Not reopened here.

- **R3 (was OWNER Q3):** neither option (A) nor (B). Zomboss's commander level lives on Zomboss's empire
  of each save, `(SaveId, EmpireId)`, supplied by `solid-enforcement` `save-identity`; Zomboss stops being
  a player row. The award writes through `save-identity`'s re-typed `TryApplyXpUnlocked(EmpireRef …)`, the
  same writer every other award uses — no Zomboss-specific writer.
- **R19 (strengthen pass):** the empire-level track is a separate row and feed; see "Not the empire level".
- **R23 (was `empire-progression` map Q-S1):** yes, mirror the player — Zomboss's pool `zomboss:{save}`,
  keyed `(SaveId, EmpireId.Zomboss)`, gets the assign-ladder computed default at his level's budget and
  applies side-wide to his members (R4 mirrored). Built by `ai-empire-species`; this module supplies the
  level through `CommanderLevelOf` and nothing else. Golden impact is stated there: Zomboss-side actors
  with a non-zero budget gain a new commander layer, listed as a new layer delivered, never a re-bless.
