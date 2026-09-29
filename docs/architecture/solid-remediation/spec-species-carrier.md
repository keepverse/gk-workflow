# spec — `species-carrier`

**Module 12 of `solid-remediation`.** Register entries: **S4, S5, S6**. Depends on `species-empire-scope`.

The carrier is worth binding only once the scope it carries is right — hence the order.

## Objective

Layer 1 binds, and the fusion-picks feature stops being dark.

## The defects

| Id | Defect |
|---|---|
| **S4** | **Fusion picks are recorded and reach no stat** — orphan |
| **S5** | **The fusion-picks feature is dark in production** — `MaterialisePlayerSpecies` lost its only caller |
| **S6** | **Layer 1 binds nothing, and has two dark carriers rather than one** |

## This is the program's clearest "built and dark" case

Fusion picks are **built, validated, carry nine refusal codes, and are reachable from the FE** — and
render nothing, because one upstream writer has no caller.

**That is a wiring defect, not a stub.** It does not belong in the stub register, and misfiling it there
would hide a shipped feature behind a debt list. The distinction is the whole reason both registers exist:

- a **stub** refuses by design, waiting on a named finding
- a **dark feature** works and is unreached

S5 is literally one of the ideal doc's eleven wires: *"`MaterialisePlayerSpecies` lost its only caller."*

### ⚠️ S5's premise is wrong in one word: it never HAD a caller (verified 2026-09-17, T4.5)

`git log -S "MaterialisePlayerSpecies" --all -- src/` returns exactly two commits, and **both add**:
`018bc2b5` (2026-09-02) introduces the method itself. Every call site ever written in this repo's whole
history lives under `tests/`. Nothing was ever removed.

So it is a **dark feature, not a regression** — and the difference decided the work. "Restore the caller"
assumes a call site to recover and a cause to avoid repeating; there was neither. The seam had to be
**chosen from the spec** instead, and `spec-player-materialise.md` names it in its own Objective and §3:

> "At **profile creation**, roll every species container against that player's world seed"
> §3: "a later `catalog_revision` **adds** species — the new ones are rolled **on next load** and appended"

Two triggers, which is exactly why the method is append-only and idempotent by construction: one call
serves both. The wiring is therefore a single call in `Program.cs`, placed **after** `SeedImportRunner.
RunSelfHealing` — before it the container tables are empty, so the roll would silently write nothing,
report success, and not run again until the next launch. It is wrapped in try/catch on the same
reasoning the content boot beside it already documents: a save is still playable without newly-appended
rows.

**The task's own note was the right instruction for the wrong history.** "Find why it was lost before
restoring it, or it is re-lost the same way" — the honest answer to *why* is that it was never wired,
and the thing that makes it stay wired is the guard, not the cause. `PlayerSpeciesMaterialiseCallerGuardTests`
scans for a call site **outside `tests/`**, because a unit test cannot express this: it would call the
method itself and stay green forever while production called nothing. That is precisely why a fully green
suite never noticed. All three assertions were verified to fail when the caller is removed.

### Two more copies of the same write, found while wiring it

`MaterialisePlayerSpecies` is not the only implementation of "materialise a player's species rows":

| Where | Selection | Production caller |
|---|---|---|
| `MaterialisePlayerSpecies` | unowned only, append | **now** `Program.cs` (T4.5) |
| `ReforgePlayerSpecies` | all, re-roll | `POST /api/debug/reforge-world` — debug-only |
| `RpgStore.Fusion.cs:311-369` | the one fusion output species | the fusion flow |

The fusion copy states its own reason: calling the method "opens its own lock/connection and would
re-decide 'already owned' against a DIFFERENT snapshot than the one already proven inside this
transaction". That reason is real and transactional — the same constraint T4.4 hit with
`EffectiveSpeciesAllocation` — but it justifies a shared **`...Unlocked(db, tx, …)` core**, not three
copies of the write shape. Recorded here for **T4.6**, which owns the carrier de-duplication; not folded
into T4.5, whose acceptance is the caller.

### ⚠️ S6 is stale: the second carrier is live, so it must NOT be deleted (verified 2026-09-17, T4.6)

S6 reads "Layer 1 binds nothing, and has **two dark carriers** rather than one", and the shape step says
the second is deleted once zero readers are proved. **Zero readers is disproved.** The attempt to prove it
is the evidence:

| | `species-passive.{id}` | `trait.species-magnitude-{id}` |
|---|---|---|
| Producer | `SpeciesMaterialiser` via `MaterialisePlayerSpecies` — a production caller as of T4.5 | `SynthesizeMagnitudeContainerUnlocked`, called from the species import at `RpgStore.Species.cs:114/150/197/214` |
| Content | 3 authored containers | **904 of 906** species carry non-empty `magnitudes` in `gk-data/packs/fusion/data/generated/creatures/*.json` |
| Consumer | **none — no `effect_binding` row is ever written for it** | `ReconcileCreatureMagnitudeBindingsUnlocked`, on every unique-actor deploy |
| Tests | `PlayerMaterialiseTests`, `FusionInheritancePicksTests` | `SpeciesMagnitudeSynthTests`, `CreatureLawnDeployMagnitudeTests` |

The source of the "dark" claim is `species-progression-ideal.md` R2, which states
*"`CreatureSpeciesDef.Magnitudes` is empty for every species"*. That was true when it was written and is
**no longer true**: `species-gear-chain` T18 shipped the synthesizer, and the runtime catalog is loaded
from the imported store rows — `gk-core/src/FusionRpg.Server/Program.cs` calls
`CreatureSpeciesCatalog.Configure(store.BuildCreatureSpeciesSnapshot())`, and
`RpgStore.Species.cs:436` (re-anchored 2026-09-20; the file has since shrunk) returns `head with { Magnitudes = magnitudes }`. The binder's
`species.Magnitudes.Count > 0` gate therefore passes in a real install.

**So the deletion does not happen, and the Boundaries rule is what says so** — *"Always: prove zero
readers before deleting the second carrier."* The proof failed, so the rule is satisfied by refusing,
not by proceeding. Deleting it would break a live `species-gear-chain` pipeline that this program does
not own.

**What S6 should have said**, and what is actually still true: layer 1 has **one live carrier and one
unbound one**, and the unbound one is `species-passive.{id}` — the carrier fusion picks land in. That is
the same defect as S4, seen from the carrier end, which is why they share a task. The remaining work is
binding `species-passive`, not deleting anything.

## Shape

1. **Restore the caller** (S5). Find why it was lost — a refactor that moved the call site, or a
   deliberate disable — before restoring it, so it is not re-lost the same way.
2. **Bind the carrier** (S6). Two dark carriers become one bound one; the second is deleted only after
   zero readers are proved.
3. **Let picks reach a stat** (S4), through `ActorHub`.

**Do not rebuild the feature.** It is built. The ideal doc's whole thesis applies here most sharply: the
work is wiring, and wiring is fixed without breaking a build.

### S4 closed: the join that was missing (T4.6, 2026-09-17)

Everything upstream of the composer was already live. `GetSpecimenMaterialisedRoll` reads a source
specimen's roll (`RpgStore.Fusion.cs:253/258`, `FusionEndpoints.cs:192`), picks are forced into the
output species' instance through `InstanceProducer.Compose`, `player_species` is written, and the FE
reads it back. **The missing step was the last one**: no composer ever read the instance, so a recorded
pick was durable, visible on the sheet, and arithmetically inert.

`UniqueActorHubCompose` now adds the rolled instance's atoms beside the two sources already there:

```
list.AddRange(EquippedBoundAtoms.DerivedFromStore(store, specimenId));   // equipment
list.AddRange(TreeBoundAtoms.ForPlayer(store, powerIndex, actor.PlayerId)); // passive tree
list.AddRange(SpeciesPassiveAtomSource.DerivedAtomsFor(...));           // the species roll  ← T4.6
```

**The projection lives in Core, not beside the caller.** It is the fourth place that would parse a
`stat.derived` atom into channel/op/amount, and the other three already sit in Core. A fourth copy in
the Server is exactly the parallel-path shape this program removes. The op goes through
`AtomDerivedSubsystem.TryParseOp`, whose contract is that an unknown op is a content error to **skip**,
never to coerce into a plausible `flat`.

**Instance values first, definition second** — `ItemCard` already establishes that order, and it matters
more here: a pick *is* a rolled value, so if the definition won, every player's species would compose the
same number and the feature would stay inert while looking wired. A fixed core atom with no rolled value
still falls back to its definition.

Three refusals are asserted rather than assumed, each a defect if it were a coercion: a non-`stat.derived`
atom, an unknown op, and a **ValueSpec object** `amount` — that last one because `TryGetInt64` *throws*
on an object rather than returning false, which took a whole compose down once at the equip seam. This
seam has no ValueSpec resolver either, so it skips rather than evaluating a second, divergent copy.

GG-49: every contribution carries `species-passive:{speciesId}` — a distinct prefix from
`equip:`/`insert:`/`tree:`, so a sheet can name which roll a number came from. Attributing a species roll
to equipment would be the wrong-but-plausible attribution the `Insert` arm exists to prevent one layer up.

> **Retired 2026-09-19 (`species-progression` SP3.1/SP3.6, module 3's own map C3).** `species-passive:
> {speciesId}` was minted here OUTSIDE the `ContributionSourceIds` grammar and had no `FictionLabel` arm
> — it could not tell layer 1a (the species-passive core) from layer 1b (a player's own roll), which is
> exactly the ambiguity `species-layer-projector` exists to close. `SpeciesPassiveAtomSource.cs` (gone —
> the file this section describes) is deleted; the sheet join it served now goes through
> `SpeciesLayerProjector.ProjectBase`/`.ProjectPlayerMod`, minting `species-base:{speciesId}` (1a) and
> `species-player:{speciesId}:{mechanism}` (1b) instead — two ids, not one, so the ambiguity this
> section's own GG-49 note names cannot recur. This module's `solid-remediation` register entries
> (S4/S5/S6, closed) are historical and unaffected: the fix they describe still happened, this section
> just no longer names the current SourceId.

**The nine refusal codes are pinned** as a closed vocabulary, count included. That is the correct use of a
literal count under `validation-ssot.md`: a refusal code is a declaration the code owns and a human edits,
so a tenth should fail the test and be re-read — the opposite of a population count, where the "fix" is to
bump the number.

## ActorHub

S4 makes picks **reach a stat**. That contribution is an `IActorStatSubsystem` or a registered atom
reader with a non-empty GG-49 `ContributionSourceIds` grammar id, or it consumes Hub output. Never a
private fold.

## Tests to rewrite

Any test asserting `MaterialisePlayerSpecies` is uncalled, or that picks reach nothing, is pinning S4/S5.
Restate: a recorded pick reaches the actor's composed stats.

Assert the **contract** — a pick is recorded, materialised, and composed — never the number of picks,
species or carriers, which are populations.

The nine refusal codes are a **closed vocabulary**: pin them, and say why.

## Boundaries

- **Always:** prove zero readers before deleting the second carrier
- **Ask first:** changing what a pick grants — that is content, not wiring
- **Never:** file a dark feature in the stub register

## Verification

```powershell
.\scripts\verify-change.ps1 -Paths <carrier> <materialise> <tests> -Session solid-remediation-<date>
```

- [ ] `MaterialisePlayerSpecies` has a production caller, and a test that fails if it loses one again
- [ ] One carrier; the second deleted with zero readers proved
- [ ] A recorded fusion pick changes a composed stat — asserted end to end
- [ ] `guard-actor-hub.py` green

## Register

Appends to the **stub register** only if something here turns out to be a genuine stub — waiting on a
named external finding — rather than dark. State which it was, either way; that judgement is the row's
value.

## Success criteria

A player's fusion picks change their actors. Today they are recorded and discarded.
