# Spec: composer-tier-window (ST1)

**Status: proposed 2026-09-18.** Module **ST1** of [action-skill-tiers-map.md](../action-skill-tiers-map.md).
No dependencies. Not approved; no build authorized.

## Objective

**Make the rung's tier window reach the one roll actions actually get.**

Ruling 1 says a skill tier *is* the atom-tier window a rung selects, the way rarity selects it for an
item. The sealed action ideal says the same: *"Rarity (on the container) selects the `pool_rolls` count
and the `min_tier`/`max_tier` window … An unlocked action is a container roll, and the rung is its
rarity"* (`action-ideal.md:271-276`), and so does A13 (`spec-action-seeding.md` §1).

**Today only half of it happens.** Traced in code:

| Step | What it does | Evidence |
|---|---|---|
| The rung row carries a tier window | `MinTier`, `MaxTier` on every row | `RungRow.cs:22-23`; `action-rungs.v2.json` rows (`1-1,1-1,2-2,2-2,3-3,3-3,4-4,4-4,5-5,5-5`) |
| The composer picks the rung row | `rung = rungBand.Collapse()`, then `rungTable.TryGet(rung, …)` | `ActionCorpusComposer.cs:57-60` |
| It builds the pool from **every atom of every named family**, all tiers | `foreach (var atom in atomsInFamily(family))` | `ActionCorpusComposer.cs:76` |
| It uses the row's `PoolRolls` | yes | `ActionCorpusComposer.cs:118-119` |
| It uses the row's `MinTier`/`MaxTier` | **no** — the draft container never sets them | `ActionCorpusComposer.cs:114-121` |
| `Instantiator.Draw` filters by tier | **no** — group exclusion and weights only | `Instantiator.cs:207` onward |
| `ContainerValidator` would check the window | only for **pool** refs, and only when the container has a window | `ContainerValidator.cs:139-144` |

`grep` for readers of the action rung row's `MinTier`/`MaxTier` in `src/` finds none. **So a rung-1
general action can hold a t5 atom today**, and the window is data nothing reads.

**Which roll this is.** An action is rolled **once, at import**, from its brief's stable id — never per
player (`spec-action-instance-and-grant.md` §Objective 3; `ActionCorpusComposer.cs:125-127`). So the
window applied here is the **authored** rung's window. This is the reading A-U1 already assigns to
content properties (`spec-rung-semantics.md` §3.1: the authored rung *"fixes the structure budget,
because structure is a property of the action"*). A fixed atom set is also a property of the action.
The holder's progress shows through the effective rung in cost and `qPower` — see ST2.

**Player-visible result:** a general action carries tier-2 atoms, a family action tier 4, a signature
action tier 5, at the shipped windows (general ceiling rung 4 → `[2,2]`, family rung 7 → `[4,4]`,
signature rung 10 → `[5,5]`). "Some skills are rarer shapes" (ideal §What this is) becomes true of the
content instead of only of the prose.

## Contract

1. **Filter.** In `ActionCorpusComposer.Compose`, after resolving `rungRow`, drop every candidate atom
   whose `Tier` is outside `[rungRow.MinTier, rungRow.MaxTier]`. Each dropped atom is recorded as a
   `DroppedAtomCandidate` (the type already exists, `ActionCorpusComposer.cs:15`) with the reason
   `tier {t} outside rung {r} window [{min},{max}]`. Measured and reported, never silent — the same
   posture as the existing roll-class drop.
2. **Empty pool.** If no candidate survives, the brief is refused through the existing
   `ActionCorpusComposeRejection` path, and the message names the families and the window. Never widen
   the window to find an atom — widening is a balance decision, not an import decision.

   **A refused brief that was imported before this module** (added 2026-09-18, strengthen pass). The
   importer records a refusal and `continue`s (`ActionCorpusImporter.cs:45-49`), leaving the brief's
   previously stored action and pre-window container untouched — so an out-of-window action would stay
   in every battle catalog. `ActionRow.Enabled` cannot switch it off today: it is copied
   (`ActionCompiler.cs:64`) and persisted (`RpgStore.Actions.cs:263`) but **nothing filters on it**. So:
   the importer upserts the stored row with `Enabled = false` (a revision bump, never a delete — grants
   may reference the id) and reports it as its own outcome, and `BuildActionCatalog` skips a disabled
   row. That is `Enabled`'s first reader; it is a skip, not a new `ActionRejectionReason` member (that
   enum is closed).
3. **Stamp.** Both the draft and the final container carry `MinTier`/`MaxTier = rungRow`'s window. The
   fields exist (`ContainerRow.cs:169-170`) and are persisted and compared (`RpgStore.Containers.cs:103-104`),
   so a re-import updates stored content through the existing revision bump.
4. **Post-condition.** Every atom in the final fixed core lies inside the stamped window, asserted in
   the composer and throwing if not. `ContainerValidator` does not check the fixed core
   (`ContainerValidator.cs:70-86` checks core atoms for existence and overrides only), so the composer
   must.
5. **Multi-tier window is refused, not defaulted.** Every shipped window is one tier wide, so weights
   inside a window have no effect today. The item rule for them (`W_tier 1000/600/300/120/35`,
   `ssot-affixes.md` §4.8) has **no code home** — it is described in `gk-data/packs/fusion/data/seed/items/_registry/bands.v1.json:487`
   and implemented nowhere in `src/` (grep). If a published rung row ever has `MinTier < MaxTier`, the
   composer refuses the brief naming the missing weight source. That is tunables rule T5: *"A missing
   tunable is a load rejection naming it. Never a built-in default."* Pool weight stays `1`
   (`W_family = 1`).

## Tunables

None new. Reads `rows[].minTier`, `rows[].maxTier`, `rows[].poolRolls` from the loaded
`data/tuning/action-rungs.v{n}.json` (`RungPolicy.Table`, passed in by `ActionCorpusImporter`,
`gk-core/src/FusionRpg.Server/Program.cs`).

## Numeric types

Tiers and rungs are small structural indices bounded by the rung table (`1..cap`) and `TierCount = 5`
(`Effects/Atoms/Generation/FamilyExpansion.cs:28`). `int` holds them; no magnitude is computed here.

## Seedsmith / generator

**No generator change.** The tier window is applied at C# import time. The seed keeps carrying only
`rungBand` (an index pair) and `atomFamilies` (ids) — `gk-forge/tools/seedsmith/seedsmith/adapters/actions/kinds.py:24` `ACTION_SEED_REQUIRED` — and
`audit_schema` (`pipeline/model.py:113`) keeps any magnitude out. `data/seed/actions/committed-round-*.json`
is not touched and is not regenerated.

## Commands

```powershell
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~ActionCorpusComposer"
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~ActionCorpusImport"
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden"
.\scripts\verify-change.ps1 -Paths <every changed file> -Session <session-id>
```

## Project structure

```
gk-core/src/FusionRpg.Core/Actions/Corpus/ActionCorpusComposer.cs     (filter, stamp, post-condition, refusal)
gk-core/src/FusionRpg.Data/Sqlite/ActionCorpusImporter.cs             (disable a stored action whose brief now refuses)
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.ActionCatalog.cs           (skip a disabled row)
gk-core/tests/FusionRpg.Core.Tests/Actions/Corpus/…ComposerTierWindowTests.cs
```

## Code style

```csharp
// ST1: the rung's tier window is the action's rarity (action-ideal.md:271-276). An atom outside it is
// dropped and reported, never silently kept -- and never widened to find one.
if (atom.Tier < rungRow.MinTier || atom.Tier > rungRow.MaxTier)
{
    dropped.Add(new DroppedAtomCandidate(family, atom.AtomId,
        $"tier {atom.Tier} outside rung {rung} window [{rungRow.MinTier},{rungRow.MaxTier}]"));
    continue;
}
```

## Testing strategy

Contract tests. No test asserts how many actions the corpus holds, how many were dropped, or which
atom a real brief drew.

| # | Test | Proves |
|---|---|---|
| 1 | A brief whose families hold atoms at t1..t5 composes to atoms all inside its rung's window, and the container carries that window | Contract 1, 3 |
| 2 | Out-of-window atoms appear in `Dropped` with the tier reason | Contract 1 |
| 3 | A brief whose families have **no** atom in the window is refused, naming the window | Contract 2 |
| 4 | **Planted violation:** a composer path that keeps an out-of-window atom trips the post-condition | Contract 4 |
| 5 | A rung table with a two-tier window refuses the brief naming the missing weight source | Contract 5 |
| 6 | Same brief, same catalog, composed twice → byte-identical container | Determinism unchanged |
| 7 | Re-import over a store holding the pre-window container bumps its revision (not a no-op, not a failure) | Contract 3 |
| 8 | Re-import where a previously imported brief now refuses: the stored action is disabled (revision bumped, not deleted), reported, and absent from `BuildActionCatalog`'s output | Contract 2 |

**Goldens.** A battle golden that holds a corpus action whose drawn atom changes will move. That is a
content change. Re-bless it in a **separate commit** that says why (tunables T7 — a golden move must be
attributable to one cause), **second** in the cross-program order ST2 → ST1 → `action-enrich`
`action-base` (map §7).

## Boundaries

- **Always:** report every dropped atom; refuse rather than widen; keep the roll content-seeded.
- **Ask first:** widening any rung row's window (a balance decision, and it needs a tier-weight source
  first — contract 5).
- **Never:** roll per player (`spec-action-instance-and-grant.md` Boundaries); add a `tier` field or
  column (ruling 1); hand-edit `gk-data/packs/fusion/data/seed/actions/**`; read the holder's effective rung here (that is
  ST2's reading, and it is not a content property).

## Success criteria

1. After import, every action's fixed atoms lie inside its authored rung's `[MinTier, MaxTier]`.
2. The composed container carries that window.
3. No brief is silently widened; an empty window is a named refusal.
4. A multi-tier window cannot ship without a tier-weight source.

## Self-audit (debate pass)

- *"Should the window follow the band's floor, not its ceiling?"* No. The composer already collapses the
  band to its ceiling for the structure budget (`ActionRow.cs:118`), and A-U1 fixed that as the content
  reading. Using a different rung for the atom window than for the structure budget would give one action
  two content rungs.
- *"Signature actions now all carry t5 atoms from a holder's first unlock — too strong?"* That follows
  from rung = rarity with a fixed, import-time roll (C-5 in the map). The holder's effective rung still
  scales cost and `qPower`, so a first-unlock holder pays and scales as rung 1. Whether a first unlock
  should *see* t5 content is a balance question on the rung table's windows, which ST3 makes tunable.
  Not an owner question for this module.
- *"Does this change the budget check's result?"* Yes, and in the safe direction for general and family
  actions (lower tiers). That is why ST4 runs after this module.

## Open questions

None.
