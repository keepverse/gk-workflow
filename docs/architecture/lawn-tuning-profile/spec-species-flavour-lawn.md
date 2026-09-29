# Spec: `species-flavour-lawn` (lawn-tuning-profile module 8)

**Program:** [lawn-tuning-profile](../lawn-tuning-profile-map.md) ·
**Depends on:** `mode-profile`, `base-relative-read` · **Feeds:** `lawn-scale-live-proof`
**Owner ruling carried in (2026-09-16):** *"keep the specie favour in specie seed, seem like it never
wire"* — and, on the base question: *"the specie seed have power ladder and generate base on almanac in
game, maybe inconsistent some where but in principle should correct."*
**Status:** spec, 2026-09-16. Not built.

## Objective

Make a species feel like itself on the lawn, from the seed that already describes it — and fix the bake
first, because the bake does not currently describe it.

## The bake is a constant wearing a species' name — measured, all 904 files

`gk-data/packs/fusion/data/generated/creatures/*.json` is the species SSOT and it is generated. Corpus-wide:

| Reading | Value |
|---|---|
| Distinct `theta` | **730 of 904 are `13`**; 136 are `0`; the remaining 38 scattered over 8 values |
| `combat.power.omni` present | **457 of 904 (50%)** — half the corpus has no attack identity |
| Distinct `resource.max.hp` | 42 values, but **450 of 904 are exactly `2712`**, 95 are `14464` |
| Peashooter vs GatlingPea | identical `hp 2712`, identical `power 362` — the two plants vanilla separates most are identical in the bake |
| Carried well | `rangeCells` (1/3/5), `attackIntervalMs` (500–3000, 5 values), rarity, elements, `traitPool` |

So a "species flavour" wired to the lawn today would carry, for most species, **one Θ, one hp tier, and
half the time no attack at all**. Wiring that first and fixing it later would ship a feature whose
observable effect is a constant — and would make every downstream tuning pass chase a number the
generator, not the balance, decided.

⚠️ Note the scale too: `resource.max.hp 2712` is ladder-sized, against vanilla's 300. The seed is not a
drop-in replacement for the vanilla base — see `base-relative-read`, which anchors on the actor's own
vanilla value for exactly this reason.

## Two halves, in order

### Half 1 — fix the generator (this is the deliverable that matters)

Per the hard rule, `gk-data/packs/fusion/data/generated/creatures/**` is output: the fix is in the generator and its inputs,
never in the emitted JSON.

1. **Θ becomes a species property.** A species' rung should follow its rarity and role, not sit at 13
   for four fifths of the corpus. Rarity is already per-species (`Cultivated`, `Fused`, `Grafted`,
   `Sprout`, …) and the ladder is already the SSOT — this is a mapping, not a new curve
   (`ssot-power-scale.md` §10 stays closed).
2. **Attack coverage.** A plant that attacks gets `combat.power.omni`; one that does not
   (Sunflower, Wall-nut) legitimately has none. Today's 50% is not that distinction — Threepeater and
   KelpPuff both attack and both read `None`. The generator must derive it from the almanac role it
   already reads, and the guard below makes the absence deliberate rather than silent.
3. **Reconcile against the almanac.** The owner's own framing: the base is generated from the in-game
   almanac. Where the bake and the almanac disagree on whether a plant attacks, at what cadence and at
   what range, the almanac wins and the disagreement is reported, not smoothed over.

### Half 2 — wire it (small, once half 1 is real)

- The species lookup moves onto the `EmpireGeneral` claim — `spec-general-empire-fallback.md` forbids
  type-id inference, and the lawn currently infers.
- The bake is re-run against the **shipped** aptitude tuning: it reads `aptitudes.v2.json` while hosts
  load `v8`, so even the values it does carry were fitted against a retired table.
- **One registered species contributor** carries the baked values into the lawn Hub, for the RPG-only
  channels vanilla has no field for (`rangeCells`, cadence, trait-driven channels). Contribute through
  `IActorStatSubsystem`; never a second fold.

## Tunables

| Key | Where | v1 |
|---|---|---|
| species Θ mapping by rarity | the generator's own tuning input | derived from the existing rarity ladder |
| `modes.lawn.families.species.*` scale | `mode-profiles.v{n}.json` | `UNMEASURED` |

No per-species number is ever authored in `gk-core/data/tuning` — the ruling is that species flavour lives in
the species seed. The lawn row holds mode-level dials only.

## Commands

```powershell
dotnet run --project tools/DemonSpeciesGen            # regenerate
dotnet run --project tools/DemonSpeciesGen -- --check # CI's drift gate
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Species|CreatureSpecies"
.\scripts\verify-change.ps1 -Paths <changed files> -Session <session id>
```

## Testing strategy

Contract and closure, never a population count (`validation-ssot.md`):

- ✅ **Θ is not a constant**: the corpus's distinct-Θ count is greater than one *and* Θ correlates with
  rarity — asserted as a relationship, never as "how many species have Θ=13".
- ✅ **Attack coverage is deliberate**: every species with an attacking role carries
  `combat.power.omni`, and every species without one has a non-attacking role. A join that must close,
  in both directions.
- ✅ Peashooter and GatlingPea do not resolve to identical magnitudes (a named regression case for the
  exact symptom this spec was written from).
- ✅ The bake reads the same aptitude tuning version the hosts load — asserted, because it does not
  today.
- ✅ The lawn contributor registers through `IActorStatSubsystem`; `guard-actor-hub.py` green.
- ❌ Never assert the species count, the number carrying power, or any single species' hp.

## Boundaries

- **Always:** fix the generator and regenerate; keep species flavour in the species seed (owner ruling).
- **Ask first:** nothing in half 1. Half 2's dial values are `UNMEASURED` and sized by the live proof.
- **Never:** hand-edit `gk-data/packs/fusion/data/generated/creatures/**`; author per-species numbers in `gk-core/data/tuning`;
  anchor the lawn's base on the seed's ladder-sized magnitudes (that is M1 again — `base-relative-read`
  owns where the base comes from).

## Numeric types

Baked magnitudes are `long`. Θ is an index (`int`). Cadence is milliseconds (`int`).

## ActorHub gate

**Contributes** through one registered species subsystem; consumes Hub output elsewhere. No second fold.

## Success criteria

1. Θ varies by species and follows rarity; the 730-at-13 cluster is gone.
2. Attack coverage is a closed join in both directions, not 50%.
3. Peashooter and GatlingPea differ in the bake.
4. The bake and the hosts read the same aptitude tuning version.
5. A lawn actor's species-only channels (range, cadence, traits) reach the Hub through one registered
   contributor, observable in `lawn-scale-live-proof`'s run files.

## Open questions

None. The Θ-by-rarity mapping is derived from the existing ladder, not chosen.
