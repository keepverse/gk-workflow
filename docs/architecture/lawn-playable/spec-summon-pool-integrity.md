# Spec: `summon-pool-integrity` (lawn-playable module 4)

**Program:** [lawn-playable](../lawn-playable-map.md) · **Depends on:** nothing ·
**Closes:** live-probe Task 22
**Status:** spec, 2026-09-16. Not built.

## Objective

A player spends 100 souls, gets a specimen, deploys it, and nothing happens. No refusal, no message —
the deploy sits in `Deploying` until the ack times out and the specimen falls back to `Roster`. The
souls are gone.

Measured 2026-09-16 on real pulls with real souls: **3 of 5** rolled a species this build cannot plant —
`typeId 261` (`Synergy_蘑菇岛`), `264` (`Synergy_爆破王`), `265` (`Synergy_磁力科技`). The injector logs

```
[UNITY] 不存在该类型的植物Synergy_磁力科技
[FusionRpg] [cheat] ERR pvz.spawn.extra plant: System.NullReferenceException
  at CreatePlant.SetPlant (…)
```

and the server never hears about it.

Two independent defects, both owned here:

**(a) The pool contains species that cannot be planted.** Synergy plants are fusion *results* in PvZ
Fusion — nothing plants them directly. The catalog offers 871 summonable species over 783 distinct
`gameTypeId`s, 68 of them in the 200–299 band the low-rarity bands draw from heavily
(`GET /api/creatures/catalog`).

**(b) An engine-side spawn failure is never reported.** The injector catches the exception and logs it;
the deploy correlation is never answered, so the server cannot tell "the engine refused" from "the ack
is late". `POST /api/unique/actors/{id}/fail-deploy` already exists and nothing calls it from here.

## Tech stack

The species generator that emits acquisition flags (`tools/DemonSpeciesGen`, `data/generated/demons/**`),
a corpus guard, and `FusionRpg.Injector` (`CheatActions` spawn path) + `FusionRpg.Server`
(`UniqueActorService`). No new dependency.

## Commands

```powershell
dotnet run --project tools/DemonSpeciesGen -- --check     # CI's own drift gate
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Summon|SpeciesAcquisition"
dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~Deploy"
.\scripts\verify-change.ps1 -Paths <changed files> -Session <session id>
```

## Project structure

| What | Where |
|---|---|
| The flag's source | the generator that emits `acquisition` — **never the emitted JSON** |
| The corpus guard | `gk-core/tests/FusionRpg.Core.Tests/Creatures/SummonPoolPlantabilityTests.cs` (new) |
| The plantable vocabulary | `gk-core/data/tuning/` or a registry the generator reads — see The shape |
| Failure reporting | injector spawn catch → `fail-deploy`; server records a reason |

## The shape

**(a) is a generator fix, not a data edit.** `data/generated/demons/**` carries generator provenance, so
editing a row by hand forks the corpus from its generator and the next run reverts it
(`AGENTS.md`, hard rule). The generator needs an input that says which `gameTypeId`s this game build can
actually plant. That input is **authored**, because it is a fact about the host game, not a roll:

- a registry file listing the plantable id ranges / exclusions, with its reason per entry
  (`Synergy_*` = fusion result, not plantable), and
- a generator rule: a species whose `gameTypeId` is not plantable **cannot carry
  `CreatureAcquisition.Summonable`**. It may still be capture-only, fusion-only, or codex-only — this
  module removes it from the *summon* pool, it does not delete content.

**(b) is a two-line contract.** The injector's existing catch already has the correlation id
(`pvz.spawn.extra id=<correlationId>` is in the log). It answers `fail-deploy` with the engine's own
message; the server records the reason on the actor and returns the souls' worth of honesty — the
specimen goes back to `Roster` with a **stated reason** instead of a timeout.

⚠️ Refunding the souls is **not** in this module. A refund is an economy decision and belongs to whoever
owns the soul ledger; naming the failure is what makes that decision possible.

## Testing strategy

- ✅ Every species flagged `Summonable` has a `gameTypeId` in the plantable registry — asserted over the
  whole corpus, as a **join that must close**, never as a count (`validation-ssot.md`).
- ✅ The plantable registry's own entries are a closed, authored vocabulary — pin its shape, not its
  size.
- ✅ A generator run against a corpus containing a fusion-only species emits it without `Summonable`.
- ✅ Server: a `fail-deploy` answer moves the actor to `Roster` **with a reason**, and the reason
  reaches `GET /api/unique/actors/{id}`.
- ❌ Never assert how many species are summonable. That is a population reading and it grows with
  content.

## Boundaries

- **Always:** fix the generator and regenerate; keep the registry authored and commented per entry.
- **Ask first:** whether a failed deploy refunds souls — that is the ledger owner's call, not this
  module's.
- **Never:** hand-edit `data/generated/demons/**`; delete species (a fusion-only species is legitimate
  content, it is simply not summonable); silently swallow an engine exception again.

## Numeric types

None introduced.

## ActorHub gate

Not an actor-magnitude module. It touches acquisition flags and a deploy refusal path only.

## Success criteria

1. A corpus guard fails if any summonable species is not plantable, and it passes after the regen.
2. Ten consecutive real pulls deploy without a single `不存在该类型的植物` in the injector log.
3. A deliberately unplantable deploy answers within the ack window with a named reason, not a timeout.
4. `DemonSpeciesGen --check` green in CI (no drift).

## Open questions

One, and it is the owner's: **does a failed deploy refund the souls?** Default until answered: no
refund, but the failure is named on the actor, which is strictly better than today's silence.
