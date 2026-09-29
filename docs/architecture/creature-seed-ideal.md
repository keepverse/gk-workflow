# Ideal: `creature-seed` — the species anchor, classified from lore and expanded by arithmetic

**Program:** `creature-seed` · **Phase:** idea. **No spec, no plan, no code follows from this document.**
Written 2026-09-01.

> **Updated 2026-09-17.** The capture this document designed for **landed**: 892 of 904 species now carry
> measured game stats, up from 82, and **170 stop being LLM judgements**. **4 owner rulings**
> (R-CS1–R-CS4): re-derive now, mimic-not-enforcement, mark-not-delete, and `SPECIES_KIND` as a closed
> enum. See the enrichment immediately below — **two scarcity claims in the body are superseded**.
>
> **Partly built 2026-09-18 — this header said "Built" and "the rulings are implemented", and an
> audit falsified that.** What did ship: the capture is exported as a committed dump file, and every
> anchor's `basis` is re-derived from it (892 `observed`). What did **not**: `speciesKind: "excluded"`
> exists only in the seedsmith seed tree — **zero C# consumers** — and all 12 phantoms still ship as
> full playable species in the runtime corpus (`gk-data/packs/fusion/data/generated/creatures/Pit.json` carries
> `"acquisition": "Summonable"`, a complete `magnitudes` block, and no `speciesKind` at all).
> **R-CS3 property 1 and R-CS4 both say in terms that a mark nothing consumes is decoration** — so by
> the rulings' own test the mark is not yet implemented. The C# mirror is left to a spec, and until it
> lands this clause is a seed-tree fact, not a runtime one. **One clause did not ship** — the `threatBand` re-score behind "170 stop
> being LLM judgements" needs a `creature-threat.v2.json` re-fit first. **Measured 2026-09-18: the defect
> is the SCORE, not the thresholds** — 154 species are one number to it, and adding `cost` as a third
> weight fixes it (every rung occupied, none over 20%). One owner decision remains: the weight. With
> hand. See *"What R-CS1..R-CS4 actually cost, measured"* below.

**Predecessor:** [seedsmith-creatures-ideal.md](seedsmith-creatures-ideal.md) explored generating *content
about* 84 species that already existed. This explores generating **the species themselves**, and
replaces that document's assumption that the roster arrives pre-made.

---

## ⚡ Enrichment 2026-09-17 — the capture this document was waiting for has happened

**Status of this section:** idea phase. Not a spec. No build authorized. It records a measurement, not a
plan.

This document's central scarcity premise is **obsolete**. It was written when 82 of 904 species had
observed stats and 822 had none, and it designed a four-value `basis` ordinal precisely so a later
capture could upgrade rows without rebuilding the corpus:

> *"a later capture upgrades a species from `inferred` → `stated` → `observed`, and provenance says
> exactly which rows to re-derive. **Nothing is ever rebuilt wholesale.**"*

**That later capture landed on 2026-09-17.** `GameHooks.EnqueueBaseStats` sweeps both game enums and
reads `PlantDataManager.GetPlantOriginalData` / `ZombieDataManager.GetZombieData` — the game's own static
tables — with no board, no spawn and no almanac window. Result: **911 rows** in `type_base_stats`
(684 plant, 227 zombie), against 82 observed before.

### What it does to the basis ladder — measured, not projected

Joined by `(side, gameTypeId)` against the committed corpus:

| basis | count | now backed by a real game stat row |
|---|---|---|
| `stated` (韧性/伤害 regex over almanac text) | 637 | **637 — all of them** |
| `inferred` (**the LLM judged `powerBand` from lore**) | 170 | **170 — all of them** |
| `observed` (was `spawn_stats`) | 82 | 82 |
| `blocked` (no text at all) | 15 | 3 |

**892 of 904 species — 98.7% — now have a real number from the game itself.** The ladder does not climb
one rung; it collapses to its top.

**The most consequential row is `inferred`.** Those 170 species had their power judged by a model reading
flavour text, because nothing else existed. **They now have measured stats, so the model stops judging
power for 19% of the roster.** That is not a quality improvement to an LLM output — it is the removal of
an LLM call, which is the outcome this repo prefers wherever it is available
(`innate_picker/derive.py:7-9`: *"Model calls: none — permanently, not provisionally"*).

**A cross-validation worth recording, because two independent sources agreeing is rare.** This document
measured `韧性` (toughness, parsed out of almanac prose) spanning **200 → 640,000**. The static table
measured independently on 2026-09-17 gives plant `hpBase` spanning **300 → 640,000**. Same ceiling,
different extraction paths, no shared code. The regex was reading the real number.

### The capture also found a corpus defect: 12 species that are not creatures

The 12 species left without base stats are not a coverage gap. They are:

```
Pit (257)   Refrash (258)   Extract_single (259)   Extract_ten (260)
EnumValue261 … EnumValue268
```

**`PlantType` values 257–268 have no enum member at all** — verified by reading the enum's own constants
out of `global-metadata.dat`, where every one of those twelve values returns no member. `EnumValue261`
is literally the fallback naming pattern for *"a value with no name"*, and `Pit` / `Refrash` (refresh) /
`Extract_single` / `Extract_ten` are **UI and gacha actions**, not plants.

So twelve corpus rows were generated from values the game does not define. The sweep exposed them as a
side effect: **every real type got stats, and the only rows that did not are the rows that are not
types.**

> **The base-stat sweep is therefore also a corpus validator**, and that is worth keeping rather than
> treating as a one-off. A species that the game's own `PlantType`/`ZombieType` cannot resolve is a
> species that should not exist. This is a *contract* check — "every species resolves to a real game
> type" — not a population count, so it is exactly the kind of assertion `validation-ssot.md` permits and
> the kind the repo's guardrail rule asks for.

### Three buckets

**Built.**
- `type_base_stats` (side, type_id, type_name, stats_json, captured_utc), 911 rows —
  `RpgStore.TypeBaseStats.cs`.
- The sweep itself, both enums, no board required — `GameHooks.EnqueueBaseStats` (`GameHooks.cs:430+`),
  reachable as cheat action `basestats`.
- The baseline overlay: `LoadCombatBaselinesUnlocked` already prefers the static table over a spawn
  sample and falls back to the sample, so a pre-capture database still works
  (`RpgStore.AlmanacSeed.cs`).
- The `basis` four-value ordinal and its upgrade semantics — this document, already designed for this.

**Wiring gap.**
- ~~**Nothing re-derives the corpus from the new table yet.**~~ ✅ **Closed 2026-09-18** — see
  *"What R-CS1..R-CS4 actually cost, measured"* below.
- ⚠️ `CreatureSpeciesGenerator.cs:39` filters `.Where(c => c.HpBase > 0 && …)`. **The claim that
  followed this line was wrong, and it is corrected here rather than deleted, because the mistake is
  instructive: it conflated two different tables.** That filter reads `CapturedTypeSeed.HpBase`, which
  `CreatureCatalogGen/Program.cs:47` fills from **`types.hp_base`** — the spawn-sampled capture. The
  2026-09-17 sweep landed in **`type_base_stats`**, a different table that this generator never reads.
  So the filter's meaning did not change at all: measured on the owner's machine 2026-09-18,
  `types` holds **42** rows of which **40** have `hp_base > 0`, so the filter drops 2 and the legacy
  catalog is bounded by `types` coverage, not by the filter. This generator is also not the corpus
  path — it emits the shipped compiled `CreatureSpeciesCatalog.Generated.cs` (84 species), while the
  anchor -> `CreatureSpeciesGen` -> `gk-data/packs/fusion/data/generated/creatures/**` path (904 species) is the one CI
  gates. Two generators, two tables; "the same line, a different meaning" was true of neither.

**Real gap.**
- **No contract check that a species resolves to a real game type.** Nothing today would have caught the
  twelve phantom rows; they were found by joining against a table that did not exist until this capture.
- **No provenance on the upgrade.** `basis` says *how* a species' power was derived, but nothing records
  *which capture* supplied an `observed` value, so a later re-capture cannot tell a 2026-08-23 spawn
  sample from a 2026-09-17 static read. `type_base_stats.captured_utc` exists; the corpus does not carry
  it forward.

### What R-CS1..R-CS4 actually cost, measured — 2026-09-18

**Status:** built. This section records what the four rulings did when executed, including the one
part of R-CS1 that stopped at a boundary and why. It adds no new ruling.

**The precondition nobody named, and the pattern that resolved it.** The measured stats lived only in
`dist/FusionRpg.Server/data/rpg-hot.sqlite`, which is **not committed**, while
`gk-data/packs/fusion/data/generated/creatures/**` **is** and CI byte-compares it. A generator reading the live database
would have made a committed artifact depend on uncommitted local state. Resolved with the pattern this
directory already established: `gk-forge/tools/CreatureCorpusDump --base-stats <data dir>` exports the table to
`gk-data/packs/fusion/data/seed/creatures/_dump/type-base-stats.json`, a committed, deterministically ordered, self-hashing
file, and the generator reads that. It is kept **out of** the four-file manifest hash on purpose — the
almanac/baseline/recipe files are a 2026-08-23 snapshot and this is an independent 2026-09-17 sweep, so
folding them together would force regenerating four unrelated files, and would invalidate every
anchor's recorded `dumpHash` for a change none of those anchors were derived from. `--verify` checks
both.

**What the re-derivation moved** (`seedsmith creatures run rederive-measured`, deterministic, no model
calls, idempotent):

| Field | Before | After |
|---|---|---|
| `basis` | 637 stated · 170 inferred · 82 observed · 15 blocked | **892 observed · 12 blocked** |
| `speciesKind` | (did not exist) | **892 creature · 12 excluded** |

The 12 `excluded` are exactly the phantom rows, and they are exactly the 12 anchors that fail to join
`type_base_stats` — the two lists were derived independently and agree. **`gk-data/packs/fusion/data/generated/creatures/**`
did not change by one byte**, and `CreatureSpeciesGen --check` is clean: `basis` and `speciesKind` are
not fields of `ConcreteSpecies`, so this is entirely a seed/provenance upgrade. That is the expected
outcome, not a missed regeneration.

**⛔ The one part of R-CS1 that did NOT ship, and the measurement behind it.** R-CS1's summary expects
170 species to "stop being LLM judgements", which means re-scoring their `threatBand` from the measured
stats instead of from lore. Measured before deciding: re-scoring every species against the **shipped**
`creature-threat.v1.json` moves **498 of 904** rows and collapses the ladder — `raider` and `warden`
take 476 between them, while `marauder` and `pest` fall to **one occupant each**.

The cause is not the measurement; it is the thresholds. v1's rung boundaries are, by its own `_note`,
*"the real p10..p90 deciles of the (toughness×600+damage×400)/1000 score over the 719 non-blocked
species"* — deciles of the **old, almanac-parsed** distribution, in which ~280 `stated` species had no
parsed `韧性` at all (so scored on damage alone) and the game's universal **300-hp plant floor** was
invisible. Applying better inputs to thresholds fitted on worse ones empties the rungs that file
explicitly exists to keep occupied.

Re-fitting them is a `creature-threat.v2.json` publish through `gk-core/tools/tuning/publish.py`. That moves
every species' `Θ`, therefore every magnitude in `gk-data/packs/fusion/data/generated/creatures/**`, therefore the build
plans and fusion eligibility downstream — a balance change with a cascade, not a mechanical
re-derivation. **So the boundary is: the data upgrade shipped, the re-tune is an owner call with the
measurement now in hand.** This is consistent with R-CS1's own principle rather than a deferral of it:
the measurement is made, the corpus is no longer known-wrong, and what remains is genuinely the
"tune later by deterministic engine and data" half.

---

### The `threatBand` re-fit, measured — the defect is the SCORE, not the thresholds

Idea phase, 2026-09-18. Extends the section above, which correctly identified that v1's boundaries were
fitted on worse inputs. **Measuring the re-fit itself shows the problem is one layer deeper: no choice of
thresholds fixes this, because the score cannot tell hundreds of species apart.**

#### Re-fitting alone provably fails

Two honest re-fits over the committed capture (`gk-data/packs/fusion/data/seed/creatures/_dump/type-base-stats.json`, 911
rows), score `(hp×600 + attack×400)/1000` exactly as shipped:

| Fit | Worst rung | Empty |
|---|---|---|
| **v1 as shipped**, re-scored | `raider` **282**, `warden` **210** | **`nuisance` — 0 occupants** |
| **Log-spaced**, 2.68× per rung | `marauder` **483 (53.0%)** | none |
| **Deciles over distinct score values** | `nuisance` **412 (45.2%)** | none |

Every scheme piles roughly half the roster into one rung. That is not three bad choices — it is the same
result three times, which is the signature of a cause upstream of the choice.

> **Measured cause.** The score reads two fields, and **the roster is not distinct in those two fields**:
>
> | | distinct values | biggest tie |
> |---|---|---|
> | `(hp, attack)` — what the score sees | **145** over 911 species | **154 species** |
> | `(hp, attack, cost)` | **446** over 911 species | 22 species |
>
> **154 species are the same number to this score** (`hp 300, attack 0` → 180). A ladder cannot rank
> creatures it cannot distinguish; a threshold placed inside that tie is arbitrary, and one placed
> outside it leaves the whole block in one rung. Re-fitting only chooses *which* rung holds the block.

This is also why v1's low end looks so wrong now. Its bottom three rungs cap at **12, 24 and 120**, while
the cheapest real creature scores **180** — the universal 300-hp plant floor. Those rungs were fitted to
~280 species whose `韧性` never parsed and therefore scored on damage alone: **v1's low end is a fit to
missing-data-as-zero.**

#### Cost is the missing term, and it is the game's own statement of value

`cost` is authored per type, already captured, and **differs 24 ways inside the single largest tie group**.
It is the signal this document's own §"what it does to the basis ladder" already stumbled on: **Peashooter
and GatlingPea share `hp 300 / attack 20` and cost 100 against 400.** The shipped score cannot separate
them; the game says one is four times the other.

Prototyped as a third weight beside the existing `toughnessMilli 600` / `damageMilli 400` — **no new
mechanism, one more row in `scoreWeights`** — with boundaries re-fitted over distinct score values:

| `costMilli` | Worst rung | Empty |
|---|---|---|
| 0 *(today)* | 45.2% | none |
| 400 | 23.5% | none |
| 1000 | 21.7% | none |
| 2000 | 20.9% | none |
| **4000** | **19.8%** | **none** |
| 8000 | 17.2% | none |

At `costMilli = 4000`, cuts `[700, 1004, 1292, 1640, 1980, 2580, 3308, 5120, 10300]`:

```
nuisance 180 · pest 139 · marauder 90 · raider 91 · warden  87
scourge   64 · tyrant  92 · harbinger 67 · cataclysm 55 · calamity 46
```

**Every rung occupied, none above 20%** — against v1's re-score, which empties `nuisance` outright. Full
occupancy is what keeps `UnoccupiedRung` quiet, the guard `bands.py` ships precisely because *"a fitted
curve puts most of the roster in two rungs"*.

#### Two facts the prototype settled, and one it deliberately did not

- **Negative cost is a non-issue — but not for the reason first given here.** Exactly **2** species
  have one: `ZombieEndoFlame` (`-125`) and `PresentZombie` (`-100`). This bullet originally said *"they
  are sun producers, so the prototype floors cost at 0 rather than treating production as negative
  threat."* **That reason is false**, and an audit caught it: both rows carry `attackBase 0` **and
  `produceIntervalMs 0`** — neither produces anything. The decision to floor at 0 still stands, now on
  an honest footing: a negative price is the game's own bookkeeping for a type that refunds or is
  granted, and refunding sun is not a statement about how dangerous the creature is. Flooring keeps the
  score monotone in price without inventing a meaning for values below zero. Cheap to state, cheap to
  revisit — but it must be stated, not left implicit, and the reason must be checked, not assumed.
- **116 species have `cost` 0**, so cost does not separate those — `hp`/`attack` still does. The terms are
  complementary, which is why the blend beats either alone and why cost **adds** a term rather than
  replacing one.
- **`costMilli = 4000` is not a recommendation.** The curve is still improving at 8000; 4000 is a plateau
  I stopped on, not an optimum. **Choosing the weight is the balance judgement**, and it is a statement
  about meaning rather than fit: a high weight makes threat mostly *"what the game charged for this"*, a
  low one keeps it mostly *"how much it survives and hits for"*. Fit quality cannot decide that.

#### What this does not change

- **It stays on the one power ladder.** `thetaOffset` is untouched; this re-fits *which rung* a species
  lands on, never what a rung is worth. A private `f(score)` would be the defect `ssot-power-scale.md`
  §10 exists to prevent.
- **It is a tuning publish, not a generator change.** `creature-threat.v2.json` through
  `gk-core/tools/tuning/publish.py`, never a hand-edit — and the cascade the section above names is unchanged:
  every `Θ`, therefore every magnitude, therefore build plans and fusion eligibility.
- **It does not re-open R-CS1.** The data upgrade shipped and the corpus is no longer known-wrong; this is
  the "tune later by deterministic engine and data" half, now with the data.

#### Prior art — D&D Challenge Rating, and the blind spot it documents

**D&D 5e computes Challenge Rating from both defensive and offensive statistics** — the same two-axis
blend as `toughnessMilli 600` / `damageMilli 400`. Two things it has learned are worth taking.

**1. A two-axis score still needed extra resolution at the bottom.** CR runs 0–30 **and adds fractional
rungs — 1/8, 1/4, 1/2 — below 1.** Weak creatures cluster, and D&D's answer was not to re-fit the
boundaries but to **add resolution where the roster is dense**. Our 10 rungs are a closed vocabulary and
should not grow, so the equivalent move is what the prototype above does: **add a term that separates the
dense band**, rather than re-cutting thresholds through the middle of it.

**2. CR's documented failure is exactly our remaining one.** CR is *"a loose approximation"*, and the
named reason is that **legendary actions, lair actions and powerful special traits push a monster's real
difficulty well beyond what the math says**. Stats alone underrate creatures whose threat lives in
abilities.

> ⚠️ **That failure applies to this proposal unchanged, and the prototype does not fix it.** The score
> reads `hp`, `attack` and (proposed) `cost`. It does not read `traitPool`, which every species carries,
> and it does not read granted atoms. A species whose danger is *"reflects damage"* or *"immune to
> slowing"* scores as its raw stats and nothing else — the same blind spot, from the same cause.
>
> **`cost` partially compensates by accident**, which is worth naming so nobody mistakes it for a fix: the
> game priced abilities into cost, so a trait-heavy creature tends to cost more. That is a proxy, not a
> reading, and it fails wherever the game's own pricing was loose.

Sources: [What Does Challenge Rating Mean in D&D 5e — SlyFlourish](https://slyflourish.com/what_does_cr_mean.html) ·
[What is Challenge Rating in 5e + How to Calculate It — Black Citadel](https://blackcitadelrpg.com/challenge-rating-5e/) ·
[What is Challenge Rating (CR) in DnD 5e](https://dungeonsanddragonsfan.com/what-is-challenge-rating-cr-dnd-5e/)

#### Three buckets

**Built.**
- The score, its weights and the ten-rung table — `gk-core/data/tuning/creature-threat.v1.json` (`scoreWeights`,
  `thresholds`, `thetaOffset` 0→40, `inferredDefaultRung` 4).
- The banding pass and its own occupancy guard —
  `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/power/bands.py`, which ships `UnoccupiedRung`
  (*"a histogram request found a rung with zero occupants — reported, not hidden"*) and states why the
  ladder is a table: *"a fitted curve puts most of the roster in two rungs."*
- The measured inputs this proposal needs — `gk-data/packs/fusion/data/seed/creatures/_dump/type-base-stats.json`, 911 rows,
  committed 2026-09-18, carrying `hpBase`, `attackBase`, `cost`, `armorMaxBase`, `summonLevel`.
- The publish path a re-fit must use — `gk-core/tools/tuning/publish.py` (`v{n+1}`, never a hand-edit).

**Wiring gap.**
- **`cost` is captured and unread.** It is in every one of the 911 rows and no scorer consumes it. The
  weight vector has two entries where the data supports three — inert data, not a missing capability.

**Real gap.**
- **No trait or atom term in the score, and no proxy that is honest about being one.** This is the D&D
  failure above. Adding one is not a re-fit; it needs a way to price an ability, which the corpus does not
  have today — `traitPool` is a list of ids with no magnitude attached.
- **No occupancy assertion in CI for the shipped ladder.** `UnoccupiedRung` exists in the banding pass, but
  nothing fails a build when a *published* `creature-threat.v{n}.json` would empty a rung against the
  current corpus. That is precisely the defect this whole section found by hand, and it is a **contract**
  check (every rung has an occupant) rather than a population count, so it is the kind
  `validation-ssot.md` permits.

#### R-CS5 — RULED 2026-09-18: `costMilli = 400`

**Ruled: 400.** `creature-threat.v2.json` is published, and the scorer reads the term.

**Why the measurement could not choose, and what did.** The fit flattens almost immediately. Worst-rung
occupancy against the 911-row capture, deciles over distinct score values:

| `costMilli` | cost's share of the blend | worst rung | empty rungs |
|---|---|---|---|
| 0 *(v1)* | 0% | **44.0%** | none |
| 200 | 16.7% | 26.8% | none |
| **400** | **28.6%** | **22.7%** | **none** |
| 800 | 44.4% | 21.1% | none |
| 2000 | 66.7% | 19.2% | none |
| 8000 | 88.9% | 17.1% | none |

Twenty times the weight buys 5.6 further points. **400 captures 79% of the total achievable
improvement**, and everything past it is inside the noise of a corpus nobody has played against.

So the design statement decides, as the open question said it would: **threat is what a creature does
in a fight, with price as a corrector.** At 400, cost is 28.6% of the blend — a real tie-breaker and an
honest proxy for the abilities the score cannot see, without becoming the score. A cost-dominant weight
would make `threatBand` mostly *"what the game charged for this"*, which is a different claim about a
different thing, and not the one the encounter builder, `SlotFilter` and `DomainPreflight` are asking.

The prior-art note above applies unchanged and is the reason 400 is a **proxy, not a fix**: D&D 5e's
documented CR blind spot is that legendary and lair actions push real difficulty past what stats say.
Cost partially compensates because the game priced abilities in. That is still not reading `traitPool`,
and the real gap below stands.

**Cuts** `[256, 326, 414, 572, 850, 1320, 2480, 4840, 9760]`, every rung occupied:

```
nuisance 207 · pest 140 · marauder 84 · raider 74 · warden  59
scourge  101 · tyrant 88 · harbinger 66 · cataclysm 48 · calamity 44
```

**What shipped with the ruling.** `scoreWeights.costMilli` is read by
`power/bands.py`'s `score()` — it defaults to **0** when absent, so v1 scores exactly as it always did
and no caller still on v1 changes behaviour. `MeasuredBaseStats` now surfaces `cost`, `PowerSeed`
carries it as a defaulted final field, and `parse_power_seed` takes `measured_cost` the same way it
already took `measured_hp`. Cost is floored at 0 **in the scorer**, never at load, so the two negative
prices stay visible to anything else that wants them.

**What did NOT ship, and is the next step.** Re-deriving `threatBand` across the 904 committed anchors,
and regenerating `gk-data/packs/fusion/data/generated/creatures/**` behind it. The tuning and the scorer are in; the corpus
still carries v1 bands. Until that pass runs, **`gk-data/packs/fusion/data/seed/creatures/species/**`'s `threatBand` values
are v1's**, and the cascade this section already names — every `Θ`, therefore every magnitude,
therefore build plans and fusion eligibility — has not moved yet.

#### The question this replaced — kept because it says why 400 is a judgement, not a fit

**What should `costMilli` be, and what does that choice mean?** (The trait blind spot above is a
**separate, later** question — it needs a way to price an ability that the corpus does not have yet, and
it must not block this re-fit.) Not a fit question — every value from 400
up beats today's score and none empties a rung, so the measurement cannot pick for you. It is a design
statement about what "threat" names: the price the game put on a creature, or what the creature does in a
fight. The prototype's numbers are above; the ratio is yours.


**Two cross-validations worth keeping.** Of the 82 species that already carried a spawn-sampled
`observed` basis, **zero** changed rung under the measured stats — the sample and the static table
agree. And of the 357 `stated` species with a parsed `韧性`, **354 matched `hpBase` exactly**; the three
that differ (`HolographicPlant`, `DoomZombie`, `EndoFlameZombie`) are recorded as disagreements by
`PowerSeed`, not resolved.

**One finding this produced that the enrichment did not anticipate:** the sweep carries **19 rows that
no anchor claims** — plant type ids **1444–1450, 1452–1461, 5003–5004**. (This wrote the range as
"1444–1461" until 2026-09-18, which reads as 18 consecutive ids and would make the total 20;
**1451 is claimed**, by `species/plant/explosive-fungi.json`. The count of 19 was right, the notation
was not — and a contiguous range is exactly the shape a later session would re-derive from rather
than re-measure.) Those are game types newer than the
2026-08-23 almanac snapshot the corpus was classified from — a coverage gap in the *dump*, not in the
corpus, and closing it means re-running `CreatureCorpusDump` for real and classifying the new species.

### Prior art — an honest note

The web search for this specific question (replacing inferred values with measured ground truth in a
content pipeline, and what regresses) returned **no game-design numbers worth citing**, and inventing
relevance would be worse than saying so. The one transferable idea is **field-level lineage**: a data
pipeline where *"every relevant imported value can be traced back to its external source."* This
document already has that mechanism — `basis` is a lineage field — which is why the upgrade is cheap and
why the missing piece named above (which capture supplied the value) is the natural next field rather
than a new system.

Source: [field-level provenance/lineage in a data-ingestion pipeline](https://github.com/michelecoppi/guess_the_player_from_the_path/pull/62)

### What this enrichment deliberately does not decide

- **Whether measured stats should replace, inform, or merely validate the bake.** The species bake is
  `pTheta × k`; the real table says plant hp spans 300 → 640,000 against the bake's 480 → 46,080, roughly
  **22× more compressed**. Closing that is a balance decision owned by `species-flavour-lawn`, not a
  mechanical re-derivation, and this section does not assume the answer.
- ~~**What happens to the twelve phantom rows.**~~ Ruled by **R-CS3** (mark, never delete) and
  implemented 2026-09-18: they carry `speciesKind: "excluded"` and every downstream join
  (`type-weights.json`, build plans, family memberships) is left intact and correct.
- **Whether `stated` should be retained as a distinct basis** once `observed` covers the same species.
  Keeping it costs nothing and preserves the reasoning trail; collapsing it loses the evidence that two
  sources agreed.

### Owner rulings on this enrichment — 2026-09-17

#### R-CS1 — re-derive now; tune later with the deterministic engine and collected data

**Ruled:** *"option 1, then we will tuning later by deterministic engine and data collecting instead of
defer, that is our principle."*

Re-derive the corpus from `type_base_stats` immediately. 892 species move to `observed`, and **170 stop
being LLM judgements**. Do not hold the upgrade behind the balance decision.

**The principle stated in the ruling is the durable part, and it generalises past this question:**
*tune later with a deterministic engine and collected data, rather than deferring the mechanical step
until the balance answer exists.* Deferring keeps a known-wrong corpus in place to protect an unmade
decision. Re-deriving makes the real distance visible — the game's plant `hpBase` spans 300 → 640,000
against the bake's 480 → 46,080, roughly **22× more compressed** — so the balance pass gets a measured
gap in generated output instead of a claim in an audit.

This is the same discipline the repo already applies elsewhere: ship the measurement, let the
deterministic pass consume it, and price it afterwards with data rather than guessing first and
measuring never.

#### R-CS2 — do NOT enforce native type resolution; check the mimic fallback instead

**Ruled:** *"the specie have special one that don't have make from the lawn game, so do not strictly it,
it can cause we cannot make more special, only check is mimic fallback, that special should copy a id
from the lawn instead of enforce it."*

> ⚠️ **This overturns the recommendation I gave, and the reason is worth recording, because I proposed
> the exact defect this repo spent 2026-09-17 fixing.** A check asserting *"every species resolves to a
> real `PlantType`/`ZombieType` member"* would make the species corpus **closed to extension** — a new
> special species, authored rather than mined from the lawn, would fail a gate for the crime of being
> new content. That is `CommanderId`'s Open/Closed violation in a second place: a **population** fenced
> by a rule that only admits what already exists.

**The ruled shape keeps it open.** A species is valid when **either**:

1. it resolves to a real game type (the 892 mined from the lawn), **or**
2. it declares a **mimic** — a deliberately borrowed lawn type id that it presents as, rather than owns.

The check is that a species has a **resolvable id by one of those two routes**, never that the id is
natively its own. A special species copies an id from the lawn instead of being refused for lacking one.

**Why a mimic rather than a null.** A species with no type at all cannot spawn, render, or be dumped —
every downstream join keys on the type. Borrowing an id keeps every one of those paths working, and
makes the borrowing **explicit and inspectable** rather than an absence somebody later reads as a bug.
It is the same reasoning `AGENTS.md` applies to the override rule in `gear-climb` R-G1: *explicit or
absent, never a sentinel* — here the mimic is the explicit form.

**What this means for the 12 phantoms:** they are not mimics. A mimic is a deliberate declaration; these
are rows generated from enum values that do not exist, with no declaration behind them. The mimic check
does not launder them, which is why R-CS3 still applies.

#### R-CS3 — mark the 12, do not delete: marking is tracking, deleting is untracking

**Ruled:** *"mark instead of delete, the mark help me avoid to spawn it in other feature, because we
cannot sure something will happen in the future, instead of delete and untrack, we mark to track."*

The distinction is the reasoning and must not be lost in a spec: **a deleted id is untracked, and an
untracked id can be silently re-used or re-derived.** A marked row stays visible, so any future feature
that iterates species sees the mark and skips it deliberately rather than never knowing the id was
claimed.

So `Pit`, `Refrash`, `Extract_single`, `Extract_ten` and `EnumValue261`–`268` stay in the corpus carrying
an explicit mark that means **"not a creature — never spawn, never draw, never count as roster."** The
mark is a positive statement about what the row is, not an absence of data.

**Two properties this must have, both following from the ruling's own reasoning:**

1. **The mark is read by anything that spawns or draws a species**, or it does nothing. The owner's
   stated purpose is *"avoid to spawn it in other feature"* — a mark nothing consumes is decoration.
2. **A marked row is excluded from roster readings, not from the corpus.** Coverage and distribution
   measurements should report 892 real species, not 904; but the 12 rows remain present and joinable so
   nothing that already references them breaks.

**This also avoids the multi-artifact regeneration deletion would have forced** — `type-weights.json`,
`_species-build-plan.json` and family memberships all carry these ids today. Marking leaves those joins
intact and correct.

**✅ Answered by R-CS4 below:** the mark is its own closed enum, `SPECIES_KIND`, separate from `basis`
for exactly the reason this paragraph anticipated.

#### R-CS4 — the mark is its own closed enum, `SPECIES_KIND`

**Ruled:** *"just make closed enum for it."*

This is the correct tool and it is the **mirror** of the defect this repo spent 2026-09-17 fixing. A
commander **roster** is a population and must never be an enum; a **mark vocabulary** is a closed set the
code owns and a human changes by review, which is exactly what an enum is for. The two cases look
similar and are opposite:

| | Closed vocabulary — enum is correct | Derived population — enum is the defect |
|---|---|---|
| Changes when | a developer edits a declaration | content ships |
| Example | `BASIS`, `POSTURES`, `DEPLOY_MODE`, and this new mark | species roster, commander roster |

**Proposed shape**, matching the vocabularies already sitting in
`gk-forge/tools/seedsmith/seedsmith/adapters/creatures/anchor/schema.py:44-53`:

```python
SPECIES_KIND = ("creature", "mimic", "excluded")
```

| Value | Means | Applies to today |
|---|---|---|
| `creature` | A real creature whose `gameTypeId` resolves to a real `PlantType`/`ZombieType` member | the 892 mined from the lawn |
| `mimic` | A real creature that **deliberately borrows** a lawn type id it does not natively own (R-CS2) | none yet — this is the door special species walk through |
| `excluded` | **Not a creature.** Never spawn, never draw, never count as roster | the 12: `Pit`, `Refrash`, `Extract_single`, `Extract_ten`, `EnumValue261`–`268` |

**Why one enum and not two.** R-CS2 (id provenance) and R-CS3 (what the row is) looked like separate
axes, and this document warned against exactly that kind of conflation one ruling earlier — so it is
worth saying why they are genuinely one here. **`mimic` implies `creature`**: a mimic *is* a real
creature that borrowed an id. There is no meaningful `excluded` mimic, because a mimic is a deliberate
declaration and an excluded row has none. The axes collapse because one value is a subtype of another,
not because they were forced together.

The derived check falls out of the enum rather than needing its own rule: **a row is playable when
`kind != "excluded"`**, and **an id is legitimate when `kind == "creature"` resolves natively or
`kind == "mimic"` names the id it borrows.** Neither is a population count; both are closure checks over
a closed vocabulary, which is what `validation-ssot.md` permits.

**Why `excluded` and not `notACreature`.** The ruling requires the mark to be *"a positive statement
about what the row is, not an absence of data"* — the whole reason marking beats deleting is that an
untracked id can be silently re-used. `excluded` says what the row **is for** (nothing, deliberately);
`notACreature` says only what it failed to be, which reads as a missing value and invites someone to
"fix" it later.

**Ownership: `DERIVED`.** It belongs in `schema.py`'s `OWNERSHIP` map beside `posture` and `pure`, which
are also `DERIVED`. **A model must never author it** — `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/anchor/schema.py:93` already forbids the model
authoring `posture`/`pure`/`basis` for the same reason, and "is this row a real creature" is a fact about
the corpus, not a judgement about a creature.

**It is a separate field from `basis`, deliberately.** `basis` answers *"how was this species' power
derived"* (`observed` → `stated` → `inferred` → `blocked`). `SPECIES_KIND` answers *"what is this row"*.
`basis: blocked` means *"no text to derive power from"* — a real creature can legitimately be `blocked`
— which is a different statement from *"not a creature"*. Collapsing them would lose precisely the
distinction R-CS3 exists to preserve, and would make every future `blocked` creature unspawnable.

**The one property that makes it work, restated from R-CS3 because it is the failure mode:** the mark
must be **read** by anything that spawns, draws, or counts a species. A mark nothing consumes is
decoration, and the owner's stated purpose was *"avoid to spawn it in other feature."*

**Left to a spec, honestly:** the C# mirror. `schema.py` owns the seedsmith side, and no C# counterpart
to `BASIS` exists today — so whether `SPECIES_KIND` needs one depends on whether the runtime reads it,
which depends on which consumers enforce the playable check. That is a wiring question, not a
vocabulary one.

---

### Open questions — ruled 2026-09-17

All three were ruled the same day they were raised; the originals are kept below each ruling above.
All four are ruled. The mark's field name and shape — the one residue R-CS3 left — was ruled the same
evening as **R-CS4** (`SPECIES_KIND`, a closed three-value enum). What remains is genuinely spec-level:
whether a mimic is declared per species or per family (R-CS2), and whether `SPECIES_KIND` needs a C#
mirror, which depends on which consumers enforce the playable check (R-CS4).

<details><summary>Original questions, for the trail</summary>

1. **Re-derive the corpus from `type_base_stats` now, or wait for the balance decision?** The upgrade is
   mechanical and the document already specifies it, but the moment 892 species carry measured stats,
   the 22× compression gap becomes visible in the generated output rather than in an audit. Running the
   upgrade first makes the balance problem concrete; waiting keeps one change in flight at a time.
2. **Should "every species resolves to a real game type" become a contract check?** It would have caught
   the twelve phantom rows, it asserts a contract rather than a count, and it is cheap. The cost is that
   it can only run where the game's enums are readable — which is the owner's machine, not CI, the same
   constraint `GameMetaDump` already carries.
3. **Do the twelve phantom rows get deleted, or marked?** Deletion is cleaner; marking them
   (`basis: blocked` plus an explicit `notACreature` flag) preserves the record that the ids were once
   claimed, which matters if anything downstream already references them.

</details>

---

## 0. The principles this is built on, restated inline

A downstream session reads this document, not its links. So the load-bearing rules are written out
here rather than cited.

**1. Every RPG feature lives in the RPG layer. It is never built by changing what PvZ is.** PvZ owns
the board, vanilla damage, spawn/die, and the sun bank. We observe its events and contribute signed
deltas back. We never rewrite it, never read its current state, and never make a feature depend on it
representing a concept. *"Can the lawn express X"* is almost always the wrong question; *"does the RPG
layer have a channel/atom/runtime for X, and is that path wired or inert"* is the right one. An inert
path is a **wiring gap**, never an architectural wall.

**2. Two async systems.** The RPG and PvZ share no clock. Hooks record and return; decisions happen in
a later budgeted drain. Delay is the designed degradation mode, not a failure to engineer around.

**3. One power ladder.** Every magnitude derived from a level goes through a single index `Θ` and a
single function `P(Θ) = C + A·Θ + B·Θ(Θ−1)/2`. **Contests read `Θ` (linear, difference-based);
magnitudes read `P(Θ)` (triangular).** Never the other way round. The inventory of power-shaped
scales is **closed** — a curve not in it has no permission to exist, and writing a private `f(level)`
in a subsystem is the exact defect that let three incompatible curves ship at once.

**4. Rarity never touches a magnitude.** A rarity rung sets a **count band** and a **tier window** —
how many affixes, and how far below the top the pool may reach. That is all. A multiplier on the rung
makes rarity dominant and destroys the overlap between rungs that makes a long ladder legible.

**5. No hard progression ceilings.** A cap on a magnitude is a progression ceiling until proven
otherwise: remove it, or make it a configurable soft cap. Absolute bounds are derived from the
arithmetic and **throw, never clamp silently** — a clamp turns *"your gear stopped mattering"* into a
bug with no symptom.

**6. The balance surface is config, not code.** Any number a balance pass would change lives in
`gk-core/data/tuning/<domain>.v{n}.json`. A number in code costs an edit, a rebuild and a test run; a number
in config costs a file save.

**7. Integer magnitudes are `long`.** Per-mille `int` exceeds its range at `Θ` = 3,213. Floating-point is
allowed (owner ruling 2026-09-15 — precision is not overflow). Widen before multiplying, divide by 1000
last, let integer overflow throw.

**8. The vocabularies are closed on purpose.** 9 attach points · 18 atom kinds · 13 triggers ·
6 elements + `omni` · 6 resources · 12 aptitudes · 10 item rarity rungs. (Read "5 · 12 · 7" until
2026-09-18. ⚠️ **Re-measured 2026-09-18: `AtomKindRegistry.cs:27,43,48` — **9** attach points, **18** atom kinds, **13** triggers.** These are the closed vocabulary, so the count *is* the contract and a stale one is worse than none. The growth since: `Ui`/`ui.present`, `Siege`/`structure.place` (2026-09-06) and `Element`/`element.convert` (D56, 2026-09-07), plus E34's trigger expansion 8→13 and E35–E37 adding kinds on existing attach points.) Adding one is a reviewed
change, not a convenience.

**9. Never invent a second classification of something already classified.** Two classifications of a
stat channel already exist and are verified against consumers; inventing a third is a named, repeated
failure in this repo. This document already made that mistake once during the conversation that
produced it — see §5 Q1.

---

## 1. What the owner asked for

Verbatim, 2026-09-01:

> *"extend seedsmith generator, don't use in game C# generator it useless … make multiple pipelines
> that LLM read almanac data for each plant/zombie. each pipeline answer a question like what family
> classify, power scale (not a real number, a open or closed enum), aspect and some other …
> a creature specie data (json) is an anchor it have multiple closed/open enum. we will use this anchor
> to generate other gameplay mechanism for creature — like deterministic power scale generator base on
> closed/open set power scale enum that define on creature specie seed."*

Three claims, and all three are architecturally correct:

1. **The LLM classifies; it never computes.** Every answer is an enum drawn from a closed (or
   deliberately open) vocabulary.
2. **The species JSON is an anchor** — a record of those enums and nothing else.
3. **Deterministic generators read the anchor** and produce every real mechanic, including magnitudes.

This resolves a tension the predecessor document could not. seedsmith's schemas **mechanically reject
any numeric field** (`gk-forge/tools/seedsmith/seedsmith/pipeline/model.py:8-9`: *"a schema carrying a numeric
magnitude field is rejected by `audit_schema`, not by review"*). That reads as a limitation only while
you expect the model to produce mechanics. Under the anchor model it becomes the **load-bearing
guarantee**: the model is structurally incapable of inventing a number, so every number in the game
still comes from one ladder.

---

## 2. Findings — built · wiring gap · real gap

### BUILT

**B1 — The anchor shape already exists, and is already almost pure enums.**
`CreatureSpeciesCatalog.cs:9-23` carries `SpeciesId`, `Name`, `Side`, `GameTypeId`, `CreatureTypeId`,
`ElementPrimary`, `ElementSecondary`, `BaseRarity`, `DeployMode`, `Acquisition`, `Variants[]`,
`TraitPool[]`. Only the two ids are numbers, and they are identity, not magnitude. **This feature does
not invent a shape; it changes where the enum values come from.**

**B2 — The power ladder is built, exact, and callable.** `Power/PowerLadder.cs:26`, with
`ValueMilli(int index)` at `:34` documented as *"P(Θ) in per-mille, before the single end rounding.
Exact — no float anywhere."* A `powerBand → Θ` lookup has a real consumer the day it is written.

**B3 — The twelve aptitudes are a 3 × 4 matrix with a counter-cycle, not a flat list.**
`Stats/Aptitudes/Aptitude.cs:28-53` — three postures (Force · Finesse · Bastion) × four each, with
`Count` computed as `PostureCount * PerPosture` so a thirteenth changes by construction. From
`gk-data/packs/fusion/data/seed/aptitudes/roster.json`'s own `role` column, the breaks form a cycle:

| Posture | Its defence | Its breaks | Therefore counters |
|---|---|---|---|
| Force | Fortitude (mitigation) · Vigor (shield) | Onslaught (guard + reflect) | **Bastion** |
| Finesse | Agility (dodge) · Composure (crit-denial) | Pierce (mitigation + shield) | **Force** |
| Bastion | Bulwark (guard) · Retribution (reflect) | Precision (dodge) · Ferocity (crit-denial) | **Finesse** |

Might (universal offence) and Focus (utility — qi, cooldowns) are the two non-cyclic slots.

**B4 — Nine measured aptitude allocations already exist.** `Battle/Ai/ZombossPatterns.cs` ships 9
patterns — 3 pure, whose shares are *ported from `gk-core/tools/CombatSim`'s own measured archetypes*, and 6
mixed, each a (defence-posture, breaks-posture) pair chosen because it is not self-cancelling. Each
pattern **is** a 12-way per-mille allocation. Any `aptitude → allocation` expansion table has a
calibration reference instead of inventing shares.

**B5 — Six resources, not five.** `Stats/Derived/DerivedStatChannels.cs:510`:
`{ "hp", "stamina", "hunger", "spirit", "qi", "poise" }`. `resource-hub-ssot.md:128` calls this a
closed set — *"adding one is an ADR (`poise` added 2026-08-26)"*. `poise` is the guard pool: a flat
commit cost to raise a guard plus a drain proportional to what it absorbed; empty means guard broken,
never death (`gk-core/src/FusionRpg.Core/Actions/Defence/PoiseLedger.cs` (this cited a nonexistent `Combat/Guard/PoiseRuntime.cs` until 2026-09-18)).

**B6 — A ten-rung rarity ladder exists, and was built for growth.**
`gk-data/packs/fusion/data/seed/items/_registry/core.v1.json` → `rarity.ladder`: chaff 10 · sprout 20 · grafted 30 ·
cultivated 40 · fused 50 · chimeric 60 · heirloom 70 · firstseed 80 · sunwoven 90 · almanac 100.
Ordinals are *"pre-spaced by 10 precisely so a future rung can be inserted without renumbering."*
Rungs 70 and 90 are pity-guarded; 100 is deliberately unguarded but must have a deterministic source.

**B7 — Creature gacha is shipped and tuned to four rungs.** `Creatures/SummonRoller.cs`: common 74% / rare
20% / epic 5% / legendary 1%; epic hard pity 25; legendary soft ramp +6%/pull from 41, hard 55; a
10-pull rare floor.

**B8 — seedsmith's generation runtime is built and proven.** Constrained decoding via LM Studio
(`response_format: json_schema`), a LangGraph workflow with three independent stop conditions, six
deterministic validators, provenance recording what each entry was generated from, and skip-existing
idempotency. 497 tests green; 84 commander effects generated end to end against a local Gemma-26B.

**B9 — The closed vocabularies an anchor would draw from are all real.** **9** attach points
(the five original — stat · resource · status · shield · board — plus `Match`, `Ui`, `Siege`, `Element`),
**18** atom kinds, **13** triggers of which **5 are authorable**
(`OnSpawn` · `OnDamageDealt` · `OnDamageTaken` · `OnDeath` · `OnTimer`; `OnGranted`/`OnRemoved` are
runtime lifecycle no atom may author), 6 concrete elements plus `omni` — and `omni` **may not appear
in a primary or secondary slot** (`element-hub-ssot.md:128`).

**B10 — The two number systems stay SEPARATE. Only a progression delta crosses.**

An earlier draft of this finding claimed *"the RPG's magnitudes must be commensurate with PvZ's own"*
and treated the `韧性` corpus as a calibration anchor between the two ladders. **That was wrong, and
the owner corrected it:**

> *"we don't really need to know in game stats exactly — we only need to send delta for creature
> progression level and power. the base stats keep on our rpg engine, so our rpg database don't need
> same as pvz database. our base stats will use for web battle area features."*

The correct model, and it follows directly from the standalone-first decision (*the web RPG is the
core game; PvZ is extension gameplay*):

| | Owns the base | What crosses |
|---|---|---|
| **Web battle** (the core game) | the RPG's own creature base stats — server-authoritative | nothing; it is all RPG-side |
| **PvZ lawn** (extension) | PvZ owns the entity's own base (`EntityBaseline` Y0, captured at spawn) | **only the creature's progression/power delta** |

So a creature's base HP is never sent to the lawn and never needs to resemble a gargantuar's 640,000.
What is contributed is *what this creature has earned* — its progression — and that is a smaller,
independent quantity. **`P(Θ)` is not being asked to match PvZ's scale**, which is why no
cross-calibration table is needed.

**What survives from the original worry:** the progression delta still has to be *felt* on the lawn,
and `EntityBaseline` (`Stats/EntityBaseline.cs:3`, *"Immutable game baseline Y0 for one entity
instance"*) plus `DerivedModifierOp.Increased` (`Stats/Derived/DerivedModifier.cs:13`) mean a percent
contribution is available if a flat one reads as noise. That is a tuning choice inside the RPG, not an
architectural bridge between two ladders.

**And the `韧性` corpus keeps its real job** — it seeds `powerBand`, which says how strong a species
*is relative to other species*. It was never needed as a unit conversion.

### WIRING GAP

**W1 — `stat.derived` atoms are quarantined everywhere.** The kind exists and is one of the twelve,
but has *no opcode, no bag branch, no sink arm*, and battle reads channel mods only from
`TraitBattleCatalog`, never from a grant. This is the kind an aspect would most naturally use to write
a derived channel. It re-opens per runtime as consumers ship — **a wiring gap on a scheduled path, not
a wall.**

**W2 — seedsmith declares an `aspect` kind that nothing writes.**
`gk-forge/tools/seedsmith/seedsmith/adapters/creatures/kinds.py` declares `creature`, `aspect`, `commander-effect`,
`environment`; only `commander-effect` has a generator. `data/seed/creatures/aspect/` does not exist.

**W3 — `Distribution/MotifSharing` is inert.** It reports *"no creature entry carries motif data yet"*
against a corpus where `motif-assignments.json` holds 135 motifs for all 84 creatures, because nothing
merges the generated file back onto the corpus entries `Corpus.load` reads.

**W4 — Both terminal outputs are unread by the game.** `themes.v1.json` publishes 84 theme keys and
**zero items reference one**; `commander-effect/all.json` holds 84 name+doctrine pairs and no lawn
code opens the file. The pipeline is internally consistent and connects to gameplay at neither end.

### REAL GAP

**R1 — Nothing derives a species from lore.** `CreatureSpeciesGenerator.cs:57` assigns rarity by HP rank
(`RarityForRank(rank, pool.Count)`), `:81` assigns traits by `TraitsFor(rarity, row.TypeId)`, and
element by round-robin coverage. **No code path reads almanac prose to decide anything.** The
LLM-reads-the-almanac step is `power-estimate` (D5) — decided 2026-08-31, never specced, never built.

**R2 — Capture coverage, not code, now bounds the roster.** Measured against
`dist/FusionRpg.Server/data/rpg-hot.sqlite` on 2026-09-01: **904** `almanac_seed` rows (677 plant /
227 zombie), **889** carrying flavour text — but only **82** with observed HP — ⚠️ **this scarcity is
superseded; 892 of 904 now carry a measured stat, see the 2026-09-17 enrichment at the top** —
(`stats_observed = 1`); **822** have none. `CreatureSpeciesGenerator.cs:39` requires `HpBase > 0`, so
889 rows of usable lore are invisible to a roster of 84. **The old 24-species cap is gone and this
replaced it.**

**R3 — `aspect-scope` is approved and unbuilt, and it moves two of the anchor's fields.**
`creatures/spec-aspect-scope.md` is *"APPROVED by the owner 2026-08-31. Authorized to build"* and moves
`ElementPrimary`/`ElementSecondary`/`TraitPool` **off the species onto an aspect tier**, so one species
can have many elements. Verified unbuilt: those fields are still on the species at
`CreatureSpeciesCatalog.cs:17,23`, and no `Aspect` type exists anywhere under `src/`.

> **⚠️ SUPERSEDED by §5 Q9 (owner, 2026-09-01): `aspect-scope` is to be REVERTED.** This finding
> originally concluded that an anchor keeping element on the species contradicts an approved spec.
> With the revert, keeping element and traits **on the species is correct**, and one creature has exactly
> one aspect — its own. The finding is left in place because the *fact* it verified is still true
> (the spec is approved and unbuilt); only its conclusion changed.

**R4 — There is no `powerBand` axis anywhere.** No `PowerBand`/`PowerTier` enum exists in `src/`.
This is the one axis in the whole design that is genuinely free — nothing consumes it, so its length
and semantics can be chosen without migrating a single consumer.

**R5 — ⛔ A locked decision blocks the headline change.** `decisions.md:95` records the species
catalog as *"generated deterministically from captured game data (types/almanac/icons/spawn_stats),
output checked in."* Replacing that generator with LLM classification is an amendment to a locked
row, and this repo's rule is that architecture changes which lock behaviour need `decisions.md`
changed **first**. This is procedural, not a refusal — but it is not a silent swap.

---

## 3. The shape this suggests

### 3.1 Two stages, and the boundary between them is the whole idea

```
   almanac row (Chinese prose, 889 of 904 have it)
              │
              ▼   LLM — one pipeline per question, every answer an ENUM
   ┌──────────────────────────────────────────┐
   │  THE ANCHOR — enums only, no magnitudes  │
   └──────────────────────────────────────────┘
              │
              ▼   deterministic — tables and the one power ladder
   magnitudes · allocations · atoms · matchups · drop tables
```

The model never sees a number and never emits one. Every number in the game continues to come from
`P(Θ)` and the tuning tables. The `audit_schema` numeric ban stops being a limitation and becomes the
enforcement mechanism for principle 3.

### 3.2 What the anchor carries

**Identity — carried, not classified.** `speciesId` · `nativeName` · `side` · `gameTypeId` ·
`creatureTypeId` · `sourceText` (the exact almanac fields it was classified from) · `basis`
(`text` | `name` | `blocked`) · `provisional`.

**Classified — one pipeline per question.**

| Field | Openness | Draws from | Note |
|---|---|---|---|
| `family` | **open** | grows; 19 today | already built |
| `aptitudePrimary` | closed, 12 | `AptitudeCatalog` | replaces the "archetype" idea — see §5 Q1 |
| `aptitudeSecondary` | closed, 12 or null | `AptitudeCatalog` | posture derived, never asked |
| `powerBand` | closed ordinal | **new, and free** (R4) | the magnitude axis |
| `rarity` | closed, 4 | `CreatureRarity` | the breadth axis — count + tier window only |
| `deployMode` | closed, 2 | `PlantAvatar` · `HypnoAlly` | exists |
| `acquisition` | closed flags | Summonable · CaptureOnly · EventOnly | exists |
| `variants` | closed, 7 | normal · ancient · mutated · corrupted · blessed · cursed · shiny | exists |
| `resourceProfile` | closed subset, 6 | hp · stamina · hunger · spirit · qi · **poise** | may be derivable from posture |

| `elementPrimary` | closed, 6 | fire · ice · air · earth · light · dark — **`omni` is illegal in a slot** | stays on the species per Q9 |
| `elementSecondary` | closed, 6 or null | same; **0..2 concrete types total** | stays on the species per Q9 |
| `traits` | **open** | `TraitPool` | stays on the species per Q9 |

**Element and traits stay on the species** (§5 Q9). The earlier draft of this document moved them to
an aspect tier on the strength of an approved spec; the owner reverted that spec, so one creature has
exactly one aspect — its own — and its typing lives on the anchor.

**Still not on the anchor:** any magnitude. Not one field above is a number.

### 3.3 What deterministic generators derive from it

| Input | Generator | Output | Constraint it must respect |
|---|---|---|---|
| `powerBand` | lookup table → `Θ` → `P(Θ)` | hp · atk · defense | **A table, never a formula.** A `f(band)` is a private curve; the inventory is closed (principle 3) |
| `aptitudePrimary` + `Secondary` | expansion table calibrated on `ZombossPatterns` (B4) | 12-way per-mille allocation | Feeds the creature-type allocation scope that already exists and has no supplier |
| `aptitudePrimary` | direct read | posture → counter-cycle position | Derived, so it can never contradict the aptitude |
| `rarity` | count band + tier window | how many aspects/atoms, which tiers | **Never a magnitude** (principle 4) |
| `resourceProfile` | pool registration | which of the six pools exist | |

### 3.4 The two axes are orthogonal, and that is the point

`powerBand` answers *how strong*; `rarity` answers *how many*. This is the item model exactly — ilvl
decides how strong an affix may be, rarity decides how many affixes and how far below the top the
pool reaches. Keeping them separate is what makes a long ladder legible rather than dominant, and it
is why a top-rung drop from the tutorial lawn is structurally impossible rather than merely
discouraged.

### 3.5 Provenance is the upgrade path, not bookkeeping

The predecessor document established this and it matters more here: with **822 of 904** types
carrying lore but no stats (R2), and enrichment a planned later pipeline, the corpus must be able to
answer *"which species were classified from a name only, under which prompt version, from which
source text"* — or it can only be rebuilt wholesale rather than improved incrementally. `basis`,
`provisional` and `sourceText` are load-bearing.

---

## 4. Prior art — eight research passes, 2026-09-01

> **Raw material: [../research/game-design/](../research/game-design/)** — the full data tables,
> verbatim designer quotes with attribution, documented failure modes, and
> **[06-unsourced.md](../research/game-design/06-unsourced.md), which records what does not exist.**
> Read that before commissioning any further research on unit design; several hundred searches were
> spent here and the negative findings are as valuable as the positive ones.

Nine game families surveyed from **shipped data**, not wiki prose: Pokémon (PokéAPI + Showdown dex and
ladder stats), StarCraft I/II (OpenBW, BWAPI, Blizzard's own `.sc2mod` catalogs), Warcraft III and
AoE II (Blizzard's `classic.battle.net`, genieutils), Command & Conquer (EA's GPL release), Company of
Heroes and Total War (Relic Essence exports, RPFM schemas), Genshin / HSR / Arknights / FGO / FEH /
Summoners War (game data tables and official APIs), D&D 5e and PF2e (Open5e's 3,207 creatures,
Archives of Nethys' 4,748), Diablo II (1.13 data files), Ragnarok Online (`mob_db.yml`).

### 4.1 ⭐ The ratio that decides roster design

Units per **grid cell** — the product of a game's primary categorical axes — against documented
power-creep severity:

| Units/cell | Games | Creep |
|---|---|---|
| **~1** | Summoners War 1.02 · HSR 1.8 · Arknights 1.97 | Low, structurally constrained |
| **~3** | Genshin 3.4 · FGO 3.2 | Low — FGO's base stats have not moved in ten years |
| ~7 (median 4) | Pokémon | Managed by a **second vocabulary** (abilities) |
| **~15, max 129** | **Fire Emblem Heroes** | **The worst-documented case in the genre** |

FEH is causal, not coincidental: 1,410 heroes into 96 cells, **129 Red Sword Infantry in one cell**,
and a BST ceiling that moved from ~147–169 at launch to **216**. Its Arena scoring buckets BST into
bins of 5 *before* weapons and merges, converting stat creep directly into revenue.

**Our own number, computed the same way** (element-combination × aptitudePrimary; rarity excluded,
as the method excludes it):

| Design | Cells | Units/cell at 904 species | Lands in |
|---|---|---|---|
| Single element × 12 aptitudes | 6 × 12 = **72** | **12.6** | **FEH's failure zone** |
| **Dual element × 12 aptitudes** | 21 × 12 = **252** | **3.59** | **The Genshin/FGO safe band** |

**This is the strongest quantitative result of the round, and it settles hybrid typing on evidence
rather than taste.**

The three ways games hold ~1–3 per cell, in ascending order of fit for a generated roster:

1. **Grow the vocabulary with the roster.** Arknights runs 425 operators at a median of 2 per
   (subclass × rarity) cell by treating the subclass enum as a **content stream** — 72 branches and
   counting, five of which exist on CN but not Global.
2. **Make the grid the primary key.** Summoners War's `family_id × element` is filled 821/870 with
   **median exactly 1 and max exactly 1** — no two obtainable monsters share a cell.
3. **⭐ Orthogonal axes beat a long flat list.** **Ragnarok Online: 27 authored values across four axes
   (Race 10 × Element 10 × ElementLevel 4 × Size 3) produce 417 realised mechanical identities for
   2,675 monsters.** A flat list would need 417 maintained entries for the same expressiveness.

Point 3 answers the `family` sizing question and dissolves it. A rarefaction test — resample *n*
creatures from a full corpus, count distinct categories, 200 draws — shows **type vocabularies
saturate at n≈300 and never grow again**: D&D 5e uses **14 types for 322 SRD creatures and for all
3,207**. A flat model at 900 would want ~270 families; a multiplicative one wants a few small axes,
which is what this design already has. **`family` does not need to grow toward 270.**

### 4.2 ⭐ Distinctness is not carried by stats. It is carried by abilities.

Measured over full rosters:

- **63%** of 3,207 D&D 5e creatures share their exact `(CR, AC, HP)` triple with another. PF2e: **83%**.
- Adding **type + speed modes + resistances** lifts uniqueness to **93%**.
- **71%** of 5e's 2,472 distinct trait names appear on exactly **one** creature. PF2e: 8,429 ability
  names across 4,748 creatures, **66% used once**.
- Pokémon, the same finding from the other direction: type combination alone gives 154 cells, median
  3 species. Type **+ ability set** gives **730 cells, median 1, 68% singletons**. True near-duplicate
  rate **0.5%** — 18 pairs in 1,025 species, every one a deliberate designed twin. Carried by ~310
  abilities and 934 moves, not by 18 types.
- Genshin makes it literal: 119 characters share only **72 distinct HP values** and **68 distinct ATK
  values**. Diluc (v1.0, 2020) and Odette (v7.0, 2026) have **identical HP 12,980 / ATK 334**.

**A 900-unit roster needs roughly 1,500–3,500 named ability instances.** That is the real cost of this
program, and it is a generation problem of its own — almost certainly the shape of the
passive-skill-graph work named in §5 Q9.

### 4.3 The genre abandoned N×N matrices, and said why

**Four AAA franchises independently dropped the table, and none went back.** SC2 replaced a universal
3×3 with 22 sparse per-weapon bonuses; AoE4 replaced 38 armour classes with 4 damage types; Total War
went from 5 bonus categories to **2**; Company of Heroes shipped no matrix at all. **42 cells
(Warcraft III) is the largest fixed matrix any of them shipped.**

Dustin Browder, on the SC1 → SC2 change, verbatim:

> *"We wanted to make that system a lot more transparent and obvious. **Before, you had to be a
> hardcore player or surf the web to understand how the system worked.** … So instead of doing 50 or
> 75 or 100 percent damage, we added a single damage bonus against certain unit types."*

**In that very quote he mis-states SC1's own numbers** — he says 100/75/50; the real table is
100/50/25 and 50/75/100. The lead designer of the sequel got the source system wrong in an interview
about how confusing it was. That is evidence, not anecdote.

**Legibility is inferrability, not size.** No researcher or designer has published a threshold *N* at
which a matrix stops being learnable. The argument for the other axis comes from a **strategy critic,
not a developer** — Brandon Casteel, writing on Game Developer — and it names Warcraft III's **18**
non-neutral cells as unlearnable while Pokémon's **120** are not: *"Why one unit takes triple damage
from a sword versus the unit next to it taking 25% damage from the same sword is a matter of
memorizing tables and playing over and over — **there's no good visual indicator for the player to
use.**"* Attribution matters here: **no Blizzard developer has ever conceded the WC3 matrix was hard
to learn.**

**Blizzard's stated rule:** *"Units' attacks always do at least 100% of the damage value shown on the
screen."* They removed **penalty** cells because the printed number stopped being trustworthy.
`ElementRingMatrix` currently has penalty cells (`Weak => −k`).

### 4.3a ⭐ A counter matrix removed, then re-added — with reasons on both sides

Fire Emblem is the only natural experiment in the survey: the series **dropped** its weapon triangle in
*Three Houses* (2019) and a sister studio **restored** it in *Three Hopes* (2022). Both decisions have
designer statements, and they disagree in a useful way.

**Why it was removed** — Toshiyuki Kusakihara, director, Intelligent Systems:

> *"We think that the weapon triangle is somewhat of a stylized system, **it isn't really realistic**.
> If you have a situation where a novice axe user takes down an advanced lance user, well, that makes
> sense? Probably not. So, we wanted to make something that comes across as more realistic to warfare
> and have players develop their weapons skills individually."*

The objection is that a **categorical counter overrides accumulated investment** — a novice beats an
expert because of a category. That is exactly what a strong matchup multiplier does.

**Why it was restored** — Hayato Iwata, director, Omega Force / Koei Tecmo, on *Three Hopes*:

> *"**We thought that simple visual cues make for better choices and gameplay.** … we thought players
> should be able to understand the concept fairly easily as it is not an entirely new concept to
> them."*
> *"We originally gave each class a single weapon and decided what weapons would be effective against
> what based on that, but **we ultimately went with the weapon triangles**."*

And his colleague Hayashi, on playing without it: *"We didn't use that system in the beginning and
**felt that the gameplay wasn't as interesting**."*

**The two positions are both right, about different games.** A counter matrix buys *legibility and
decision texture* and costs *investment mattering*. Nintendo's own editorial framing in Ask the
Developer treats the triangle as **series identity** — *"a gameplay feature passed down from past
games as one of the characteristics of the Fire Emblem series"* — not as an optimum.

**For this design the tension is live**: a creature roster is built on accumulated investment (levels,
rarity, aptitudes), which is the axis Kusakihara says a triangle overrides. That is an argument for
keeping matchup *soft* — which our ±25% already is — or for moving the counter's payload out of the
damage formula entirely, as Engage did by replacing the modifier with a **Break** status.

⚠️ Both quotes are verified only against their English republishers; GameSpot and Jeuxvideo returned
403 to direct retrieval.

### 4.4 Reactions vs matrices — the cost argument, with counts

| | Pokémon (matrix) | Genshin (reactions) |
|---|---|---|
| Types / elements | 18 | 7 |
| Live interactions | 306 ordered cells · **120 non-neutral (37%)** | 26 productive of 30 · 17 of 21 pairs |
| **Facts to learn** | **120**, each an independent authored cell | **~22** — 16 named reactions + 4 direction cases + 2 inertness rules |
| Facts per element | 6.7 | **3.1** |
| Cost growth | **O(n²)** | **O(named reactions)** — the designer chooses |
| Composes? | No — a cell is terminal | **Yes** — a reaction produces an object (Dendro Core, Quicken aura, Frozen aura) that feeds the next |
| Depth | One depth, 120 cells, for everybody | **Two, set independently** — 16 names for players, gauge / aura-tax / decay / ICD for optimisers |

**~5.5× fewer facts despite 2.6× more elements.** And the cheapness has a named source:

> *"The reaction system's cheapness comes from deliberately leaving pairs empty. Genshin's 4 dead
> pairs and DOS2's 5 non-blessable surfaces are not gaps — they are the budget."*

When Genshin added Dendro, pairs went 15 → 21 but they shipped only **6** new reactions, leaving 4 of
the 6 new pairs inert.

**Pokémon's own depth engine is the dual-type product rule**, not the type count: 120 authored facts
become **1,589 non-neutral interactions** — a 13× expansion at zero authoring cost. The design space
is already **94.7% exhausted** (162 of 171 combos used), and the nine holes are declined on *flavour*
grounds, several being strong typings. **More types would not have helped.** Gen IX's answer was
Terastallization — a 19th type name adding essentially **zero** matrix cells.

**⛔ The Geo warning, and it applies here by construction.** Geo was acknowledged broken in December
2020 and was still ranked **worst of 7** in August 2024, through two dedicated characters that did not
fix it. The stated reason: *"Geo has a single elemental reaction, Crystallize, whereas most other
elements have three or four."* The eventual fix was the **Lunar reaction family** — an orthogonal layer
giving *every* element a new reaction slot. **Extend by adding a reaction family, not by adding
elements.**

`light` and `dark` are neutral against the entire ring and interact only with each other. In a matrix
that is merely sparse; in a reaction model it is **Geo's shape, worse** — one interaction each against
the ring four's two apiece.

### 4.5 ⭐ Rarity buys breadth and ceiling. In every game studied, never power.

| Game | Tiers | What rarity actually controls |
|---|---|---|
| **Arknights** | 6 | **skills 0/0/1/2/2/3 · talents 1→2 · max level 30/30/55/70/80/90 · elite ceiling · modules 4★+ · mastery 4★+** |
| Genshin | 2 | Ceiling only — same 3 talents, 3 passives, 6 constellations at both tiers |
| HSR | 2 | Ceiling only — same 5 skills, 6 Eidolons, 18-node trace tree |
| FGO | 6 | Party cost 3/4/7/12/16 and max level — **every Servant has exactly 3 actives and 5 Appends** |
| FEH | 5 | **~5 BST across the entire range**, plus skill *access*. And it is **mutable** — 46 heroes demoted a tier in one day |
| Summoners War | 5 | Almost pure acquisition rate — **SPD is flat at ~100 at every natural star** |

Arknights is the cleanest model: **rarity moves median deployment cost by 3 points across five tiers;
class moves it by 11.** That ratio is the whole mechanism behind low-rarity viability.

And the recurring refusal: **every game that kept low rarity viable did so by refusing to let rarity
buy the thing that matters most in its own combat model** — SPD in Summoners War and HSR (4★ mean SPD
*exceeds* 5★), deployment economy in Arknights, NP level in FGO (raised only by duplicates, while 3★
Servants drop from a free currency).

This validates principle 4 and §5 Q4: adopting the ten-rung ladder is safe **because count-band and
tier-window are exactly breadth**.

### 4.6 Cap the magnitude field; creep the effect vocabulary

**FGO's median 5★ ATK moved 32 points in ten years across ~450 Servants**, and the all-time highest
belongs to an early-middle release. Everything that got stronger got stronger in *effect text* — 50%
NP charge became 80%, single-target became party-wide, 3-turn became 5-turn.

**Epic Seven goes further and does not author per-unit statlines at all**: base stats come from a
216-cell (rarity × class × zodiac) template, so heroes sharing all three are *numerically identical*.
*"E7 cannot creep statlines without moving a cell a dozen heroes share."* **That is a defensive
property a derived-stat generator gets for free**, and it reframes the Warzone 2100 tradeoff in §2:
losing per-unit hand-tuning also buys structural immunity to per-unit inflation.

**⚠️ One finding that challenges the single-curve rule.** Every surveyed system inflates **durability
far faster than lethality**:

| System | HP growth | Damage growth |
|---|---|---|
| Diablo II Normal → Hell (L85) | 6.2× | 1.85× |
| Path of Exile level 1 → 100 | 2,989× | 352× |
| **Diablo III Torment I → XVI** | **16,958×** | **163×** — HP grows **104× faster** |

PoE's map-tier table sets boss damage to **+0% at every tier from 66 to 90**. Principle 3 has all
magnitudes read one `P(Θ)`, so HP and ATK grow identically — a choice **no surveyed game made**. It
may still be right, but it should be deliberate. See §5 Q19.

### 4.7 Enum selection is the most bias-prone LLM task shape there is

Every pipeline in this design is discrete choice over a labelled set — precisely the shape with the
largest documented non-semantic failure modes.

- **Selection bias splits into label bias** (an uncontextual preference for certain label *names*)
  **and position bias.**
- **Position bias is severe:** shuffling option order has been reported to change GPT-4 accuracy by
  **up to 75%**.
- **Mitigations are cheap and measured:** permutation with majority voting and multi-evidence
  calibration recover up to **8 percentage points**; `PriDe` is a label-free inference-time debiasing
  method with demonstrated cross-domain transferability.
- **Conformance is not quality.** An audit of public structured-output benchmarks found *"every public
  benchmark examined was full of erroneous and inconsistent ground-truth outputs."* Reported
  reliability is usually schema validity (e.g. 98.0% JSON validity), which is orthogonal to whether the
  content is right — a lesson this program already paid for twice, at 8/8 on shoehorned content and
  83/83 same-named effects.

### 4.8 Failure modes, with corpses

**⛔ A data table picked the winning build.** Diablo II Hell immunities across 703 monsters:
**137 cold · 131 poison · 113 fire · 105 lightning — and 11 magic.**
*"which is why Hammerdin won Hell — a data table picked the winning build, not a designer."*
**This is the sharpest warning of the round for a generated roster**: an uneven element/resistance
distribution across 900 creatures silently selects the meta, and selection bias (§4.7) guarantees
unevenness unless it is measured. It converts §5 Q8 from a quality nicety into the control that
prevents this outcome.

**⛔ A single wrong cell broke a metagame for a console generation.** Pokémon Gen I shipped
Ghost → Psychic at **0×** when it should have been 2×. Nintendo's own guides, two anime episodes, and
**an NPC inside the game** all said otherwise. Psychic's only functional weakness became Bug, and Gen I
had no strong Bug moves. The lesson: *"anyone shipping a matrix needs a test that asserts the table
against declared intent."*

**⛔ Gates converge every build, and Larian retracted one after nine years.** DOS2's armour had to reach
0 before any status could land. Swen Vincke on their own AI: *"it focused on one character, made sure to
destroy their physical and magical armour, and then would start to control it, then kill it… **it was a
dominant tactic.**"* Removed in 2026; Pechenin's replacement criterion is *"you will not have to wait
before you can use your fun skills on enemies."* **General rule: if a mechanic's rule is "nothing
interesting happens until X", optimal play is always "make X happen first" and every build converges.**
`PoiseRuntime` has that shape; the riposte rule (spent poise converts to damage) is a real mitigation
Larian did not have, but the shape is worth watching.

**⛔ Tag absence is a stat.** SC2's Archon, Ghost, Ravager, Baneling and Queen carry **neither** Light
nor Armored, making them immune to a large share of every bonus-damage term in the game. **Omitting a
tag is not neutral — it is a defensive buff.** Hence §6's explicit-`none` rule.

**⛔ Closed vocabularies leak under pressure.** SC2 patch 5.0.13 removed the Sentry's Light tag *and in
the same line* added `+4 vs Shields`, an ad-hoc pseudo-attribute outside the closed eight. `Psionic` was
dead vocabulary for an entire expansion cycle before Interference Matrix revived it. Four live attribute
swaps shipped **with no designer note**. A closed contract stays closed only if it has a designated
escape hatch; otherwise one gets improvised.

**⛔ Taxonomy accretion.** AoE2's 38 armour classes include one named *"All Buildings (except Port)"* for
a building that never shipped, one named *"Unique Units (except Turtle Ship)"* that **contains Turtle
Ships**, a class created and decommissioned in place, and a Mosque with **no armour class at all**, so
every attack against it does exactly 1 damage. Hidden from players for ~20 years.

**⛔ "A faster Banshee is still a Banshee."** Browder on SC2's pre-release redundancy crisis:
*"You'd play as the Zerg with something called a Spore Beast and we'd say, 'Oh my god, this is just a
Banshee, isn't it?' We'd try to tune it as like a really fast Banshee, and it was like, 'Okay, dude, but
that's still a Banshee.' **It hadn't fundamentally changed its role.**"* And the rule: *"You don't want a
'Marine 1' and 'Marine 2' scenario… you'd just end up picking the 'best' one."*
**A pure magnitude axis does not make a different unit.** `powerBand` and `rarity` both fail that test;
only element, aptitude, and the §6.2 tempo/reach variables pass it.

**⛔ Integer ceilings are real.** WoW's Ra-den shipped at **~1.5 billion HP — 70% of the signed 32-bit
ceiling** — forcing four game-wide stat squishes. Principle 7 with a corpse attached.

**The dead tail, measured.** Pokémon: **177 species (36% of everything tiered) sit in the bottom tier**,
and **18 species fill 50% of all competitive team slots**; of 1,025 species, 762 appear at all and only
82 reach 1% usage. Genshin: among players who **own** the character, eight sit under 4% usage while
Kazuha sits at 95.7% — a **~319× spread** — and Klee shows a **69% vacancy rate** (levelled past 71,
never fielded).

**And the industry's answer to power creep was retroactive rewrites, not restraint.** All three
HoYoverse titles converged independently — Novaflare (HSR), Hexerei (Genshin), ZZZ v2.5 — periodic named
batches that rewrite old kits wholesale, including scaling stats and Eidolon/Constellation effects.
HSR's are **toggleable**; Genshin's are **gated behind quest content** and attach a party-synergy tag.
**Each of those is a content program. For a generated roster it is a pipeline re-run** — a structural
advantage this design has and they do not, and the reason provenance must stay load-bearing.

### 4.9 What nobody has published

- **No quantified counter-strength target.** No studio states "a counter should win by X%". Blizzard's
  statements are entirely qualitative and always name micro or terrain as the override. A number for
  how much element matchup should matter must be derived here, not borrowed.
- **No threshold at which a matrix becomes unlearnable.**
- **No designer statement capping Pokémon at 18 types** — only evidence of per-addition cost.
- **No industry-standard closed role taxonomy.** Blizzard's two official "unit types" pages both
  explicitly disclaim completeness. Role is a per-unit editorial judgement used to detect redundancy,
  never an enum a unit is assigned from.
- **Almost no designer commentary on roster or grid design at all.** Genshin's official "Developers
  Discussion" series, enumerated across 18 entries from 2023-09 to 2025-07, is **entirely
  quality-of-life**; not one entry discusses roster growth, duplicate avoidance, grid coverage, or
  power creep.

---

## 5. Open questions

**ALL CLEARED — Q2 through Q22, by the owner 2026-09-01. Nothing in this document is waiting on a
decision.** Q21 and Q22 were raised by the prior-art round and answered the same day; both answers
corrected the question rather than picking an option.

Q9's answer named two unbuilt programs the full `aspect` vision depends on, and Q18's answer
retracted the premise of finding B10, which is corrected in place rather than deleted.

### Q1 — `archetype`: superseded before it was written, recorded so it is not re-proposed

During the conversation that produced this document, an eight-value `archetype` enum
(bruiser/tank/swarm/artillery/controller/support/assassin/summoner) was proposed and then withdrawn:
it is a **second classification of what the twelve aptitudes already classify**, which is the named
failure principle 9 exists to prevent. The owner's correction — *"we have 12 primary stats mean 12
base class"* — is the shape carried into §3.2. **Not an open question; a recorded correction.**

### ✅ Q2 — `aptitudeSecondary`: **different posture by default; SAME posture allowed and flagged `pure`.** *(owner)*

A same-posture pair is a deliberate specialist, not an accident — which is exactly what the three
pure `ZombossPatterns` already are (`force-pure`, `finesse-pure`, `bastion-pure`). Flagging it makes
the distinction readable in data instead of inferred from the pair.

Different-posture pairs reproduce the six shipped mixed patterns and cannot self-cancel. The `pure`
flag marks the ones that deliberately double down, so a balance pass can find them in one query.

### ✅ Q3 — `powerBand`: **a `Θ` OFFSET, ~10 rungs.** *(owner)*

The band shifts the species' index on the single ladder; `P(Θ)` does the rest. A stronger species is
*further along*, which composes with world depth and player level without double-counting, because
there is still exactly one curve. A multiplier was rejected for the reason principle 5 exists: it
compounds with `contentScale` at depth and would need a cap on a magnitude.

**The lookup lives in `gk-core/data/tuning/`, never as a formula** — a private `f(band)` is precisely the
defect the closed power inventory was written to end.

### ✅ Q4 — creature rarity: **ADOPT THE FULL 10-RUNG ITEM LADDER.** *(owner)*

Owner override, taken with the migration cost stated. Creatures leave `CreatureRarity`'s four values and
join `chaff`·10 → `almanac`·100 — one vocabulary, one set of colours and pips, one sort order across
items and creatures.

**This is an amendment to [item/ssot-rarity.md](item/ssot-rarity.md) §4.1 and §4.3**, whose current
text says *"Creatures keep their own ladder"* and rejects exactly this. The amendment must be written
before the change is built, and it carries five verified consumers:

| Consumer | What breaks |
|---|---|
| `SummonRoller` rates | 74/20/5/1 is a four-rung distribution; ten rungs needs a new curve |
| `SummonRoller` pity | epic hard 25 / legendary soft 41 / hard 55 all key on four-rung names |
| `FusionRoller.SlotsFor` | slot counts keyed by rarity |
| `SoulEarnPolicy.DiscoveryDelta` | soul yield keyed by rarity |
| `shard.{rarity}` material ids | id strings embed the four names |

**The item ladder already answers the pity concern the genre raises** (§4.3): it guards only rungs
**70** and **90**, and requires rung **100** to have a deterministic (quest/boss) source. Creatures can
adopt that same two-guard shape rather than inventing ten thresholds.

### ✅ Q5 — `resourceProfile`: **ALWAYS A PIPELINE. The LLM picks the pools.** *(owner)*

Owner override of the measure-first option. Lore about a starving plant or a spirit-eating zombie
reaches the right pool directly, rather than being flattened into whatever the posture implied.

**The cost this accepts, stated plainly:** the pipeline can contradict the posture — a Bastion creature
that never gets `poise`, or a Focus creature with no `qi`. That contradiction is invisible to every
tier-2 validator in seedsmith today, because each answer is individually legal. It needs a
**cross-field validator**, and what that validator does on a conflict is Q12.

### ✅ Q6 — the 822: **DROP THE HP GATE. Parse HP from almanac text as an optional seed.** *(owner)*

Owner: *"drop hp gate, but hp still exist in zombie description in almanac, can use it as optional
seed."*

**Verified, and it is larger than the question assumed — it is in plant descriptions too.** Measured
2026-09-01 against `rpg-hot.sqlite`, parsing `韧性` (toughness) and `伤害` (damage) out of
`flavor_info`/`flavor_introduce`:

| Basis | Count | Where the power signal comes from |
|---|---|---|
| `observed` | **82** | `spawn_stats` — met in-game — ⚠️ **superseded 2026-09-17: 892 of 904 are now backed by the game's own static tables; see the enrichment at the top of this document** |
| `stated` | **637** | `韧性`/`伤害` in the almanac text — **deterministic regex, no model call** |
| `inferred` | **170** | prose only; the LLM judges `powerBand` from lore |
| `blocked` | **15** | no text at all |

**719 of 904 types carry a numeric power seed, up from 82.** The great majority of the roster is
therefore *not* an LLM judgement at all — it is parsing a number the game already printed.

`韧性` spans **200 → 640,000** (n=381, median 3000). Across 10 rungs that log-spaces to ≈**2.24× per
rung**, which is a natural fit for Q3's ten-rung offset ladder and is evidence the two decisions
agree rather than merely coexist.

**This makes `basis` a four-value ordinal, and it is the feature's precision ladder**: a later capture
upgrades a species from `inferred` → `stated` → `observed`, and provenance says exactly which rows to
re-derive. Nothing is ever rebuilt wholesale.

### ✅ Q7 — C# path: **KEEP CAPTURE. MOVE EVERY GENERATOR TO SEEDSMITH.** *(owner)*

Owner: *"keep capture because it is pvz fusion source of truth but we move every generator to
seedsmith so we can support AI native generator."*

Sharper than the option offered. The dividing line is **observation vs derivation**, not C# vs Python:

| Stays in C# | Moves to seedsmith |
|---|---|
| The injector capturing the live game | `CreatureSpeciesGenerator`'s rarity / element / trait rules |
| `almanac_seed`, `spawn_stats`, `recipes` — PvZ Fusion's own facts | The species roster itself |
| The DAL that owns those tables | Corpus emission |

**Rationale, in the owner's frame:** capture is the source of truth *because PvZ produced it*; every
step that *derives* something belongs where derivation is cheap to iterate and AI-native. This also
amends `decisions.md:95` more broadly than option 1 would have — the row's *"generated
deterministically from captured game data"* becomes *"captured deterministically; derived in
seedsmith"*.

⚠️ **This answer created Q10** — seedsmith is Python in `tools/`, and the captured facts live in
SQLite. See below.

### ✅ Q8 — bias control: **PERMUTE EVERYWHERE; majority-vote the load-bearing fields.** *(owner)*

Option order is seeded from `speciesId` — deterministic, but not constant across subjects — which
removes the systematic ordering artifact at zero extra cost. Majority voting across permutations is
spent only where the answer drives mechanics: **`powerBand` and `aptitudePrimary`**.

**Disagreement rate across permutations becomes a reported quality metric**, in the same place `basis`
and coverage are reported. This is the first quality signal in this program that can see a defect
*no per-item validator can*, which is the exact class of failure that produced 87% code-switching and
83-of-83 duplicate names — both individually legal, both invisible to tier 2.

### ✅ Q9 — `aspect`: **REVERT `aspect-scope`. One creature, one original aspect. No element/status variants.** *(owner)*

Owner: *"revert aspect feature, original creature need original aspect, no element/status — that is
better than make a bundle of aspect, they will become chaos and hard to rebalance, so we have a
playable game first."*

This is the largest decision in this document, and it moves in the opposite direction from every
option offered. **`element` and `traits` stay on the species.** A creature has exactly one aspect: its
own. There is no fire-Peashooter / ice-Peashooter fan-out.

**Consequences, stated rather than discovered later:**

| | Effect |
|---|---|
| [creatures/spec-aspect-scope.md](creatures/spec-aspect-scope.md) | **APPROVED 2026-08-31 — now to be reverted.** Reverting an approved spec is itself a `decisions.md`-level change, exactly like R5's |
| §2 finding **R3** | **Superseded.** It said an anchor keeping element on the species contradicts an approved spec. With the revert, keeping it there is now correct |
| §3.2 anchor | `elementPrimary`, `elementSecondary`, `traits` **return to the species** |
| class-system `point-economy` | Its third allocation scope survives, but **collapses to 1:1 with the species** — degenerate, not missing. `decisions.md:101`'s four scopes still hold |
| `CreatureSpeciesGenerator`'s element round-robin | Still deleted — element becomes an **LLM classification from lore**, which is what a Pokemon-style typing wants anyway |

**The rebalance argument is the load-bearing one.** N aspects per species multiplies the balance
surface by N before a single creature is playable. This program's own history supports it: the
class-system's dominance matrix is *"red by design today"* at one aspect per actor.

### ⚠️ Q9 also named two unbuilt programs the full aspect vision depends on

Recorded here because they are the reason the revert is sequencing, not cancellation:

1. **Creature hybrid element typing** — Pokemon-style. The element hub already carries the substrate:
   6 concrete elements, a matchup ring plus `light ⇄ dark` mutual counter, per-component hybrid and
   a dual-type product rule, `MatchupShareK = 0.25`. **Hybrid typing is closer to a wiring question
   than a design one** — but the *creature-facing* design does not exist.
2. **A passive skill graph** — 12 primary stats × 2 build paths (offensive / defensive) × each
   element type × each status type, in the Path of Exile / Last Epoch tradition. **The owner expects
   seedsmith to build it**, which makes it a second, much larger generation program — and the real
   reason *"aspect feature is very huge"*.

Neither is designed. Both belong in their own idea phase, and `aspect` should not be specced until at
least the first exists.

### ✅ Q10 — data access: **EXPORT A DUMP. It is the development-phase source of truth.** *(owner)*

Owner: *"seedsmith is just a dev tool, it not work in the game runtime, so we need to dump data game
data and use it as SOT in our development phase, not player who play the game."*

Sharper than the option as posed. The dump is **not a cache of the database** — it is the SOT *for the
development phase*, and that phase distinction is what makes it correct:

| | Runtime (players) | Development (this pipeline) |
|---|---|---|
| Source of truth | the live game + the server's DB | the committed dump |
| seedsmith | **does not exist** — it never ships | reads only the dump |
| SQL | inside `FusionRpg.Data`, as the rule says | **none anywhere** |

This removes the DAL tension completely rather than negotiating an exemption: no SQL enters `tools/`,
so `guard-dal.py`'s `tools/` blind spot stops mattering for this feature instead of being relied on.

It also has direct precedent — `gk-data/packs/fusion/data/seed/creatures/**` is already exactly this shape: a committed dump
emitted from the DB, read by seedsmith with no database access.

**Follow-on, now Q13:** what the dump contains, and how staleness against a newer capture is detected.

### ✅ Q11 — two ladders: **BOTH TEN RUNGS, with vocabularies that cannot be confused.** *(owner)*

Rarity keeps its botanical ladder — `chaff` · `sprout` · `grafted` · `cultivated` · `fused` ·
`chimeric` · `heirloom` · `firstseed` · `sunwoven` · `almanac`. `powerBand` takes a **threat vocabulary
from a different world entirely**, so the two can never read as the same kind of thing even at a
glance, while the 1:1 tuning symmetry is kept.

**The `powerBand` vocabulary itself is not chosen — that is Q14.** The constraint it must satisfy: no
word may plausibly belong to a botanical rarity ladder, and the ordinal direction must be obvious
from the words alone.

### ✅ Q12 — posture/resource conflict: **REJECT AND REPAIR, naming the conflict.** *(owner)*

A draft whose `resourceProfile` contradicts its posture — Bastion without `poise`, Focus without `qi`
— is rejected, and the repair prompt states the exact conflict. Same shape as the shipped anti-motif
validator, and it keeps the corpus internally consistent by construction rather than by review.

This is a **cross-field** validator, a shape seedsmith does not have yet: every validator today reads
one field. It is the same lesson `name_collision` taught one level out — a property no single field
can express needs a check that sees more than one field.

### ✅ Q14 — `powerBand` vocabulary: **THREAT-SCALE NOUNS.** *(owner)*

`nuisance` · `pest` · `menace` · `threat` · `scourge` · `terror` · `horror` · `nightmare` ·
`cataclysm` · `calamity` — ten rungs, direction legible without a legend, and no word could belong to
a botanical rarity ladder. Exact wording is a content pass; the register is decided.

### ✅ Q13 — the dump: **full tables + capture stamp + content hash**, plus a **preflight skill**. *(owner)*

`almanac_seed`, `spawn_stats` and `recipes` dumped whole, with the capture timestamp and a **content
hash** in `_meta`. Every generated file records that hash in its provenance, so *"was this derived
from the current dump?"* is a comparison rather than a guess — the same mechanism that caught the
stale theme registry on 2026-09-01.

**New requirement, owner-added:** a **preflight skill that runs before seedsmith** — an agent that
checks the requirements are present (dump exists, hash current, model reachable, venv installed) and
**asks the human to supply anything missing** rather than proceeding on a silent default. This is the
class of defect this program keeps paying for: the 2026-08-31 "real run" used scratch scripts that
lived nowhere, and a falsifier attempt on 2026-09-01 silently failed to plant and reported green. A
preflight that refuses is cheaper than a run that quietly used the wrong input.

### ✅ Q15 — rarity rungs: **ALL TEN, two pity guards at 70 and 90.** *(owner)*

Mirrors the item ladder exactly: the same ten rungs, the same two-guard shape, and rung **100
(`almanac`) deliberately unguarded by pity, requiring a deterministic quest/boss source**. One rarity
philosophy across items and creatures, and the shipped two-counter `PityState` shape ports over with its
thresholds retuned rather than its structure rewritten.

### ✅ Q16 — `powerBand`: **NUMBER WINS, and the LLM AUDITS the result.** *(owner)*

Where a parsed `韧性`/`伤害` or an observed HP exists (719 species), a tuning table maps it to a rung
**deterministically** — no model call decides the band. The LLM then **reviews** the assigned band
against the lore and **flags disagreements without overriding them**. For the 170 prose-only species
the LLM assigns the band directly.

The most expensive of the three options, chosen for signal: **the disagreements are the product.** They
say where the almanac's own numbers misrepresent what a creature is — information no other mechanism
here can produce — and no model ever silently moves a magnitude.

### ✅ Q17 — `deployMode` / `variants` / `acquisition`: **all three classified from lore.** *(owner)*

The almanac usually says outright whether a zombie is driven or hypnotised. `variants` still must
never be a number the model emits: the model names *which* variants exist; **how many** a rung permits
stays rarity's count band.

Chosen for a reason much larger than these three fields — see finding **B10**, which constrains the
whole power ladder.

### ✅ Q18 — contribution: **the two number systems stay separate; only a progression delta crosses.** *(owner)*

Not one of the three options — the owner dissolved the question. The RPG keeps its own base stats for
creatures and uses them fully in **web battle**; on the **lawn**, PvZ owns the entity's base and receives
only the creature's **progression/power delta**. The RPG database does not need to resemble PvZ's.

**This retracts the premise of B10 as first written**, which claimed the two ladders had to be
commensurate. They do not. See B10 for the corrected finding.

Left as a tuning choice, not an architecture one: whether that delta is `Flat` or `Increased`
(percent). Both ops exist; the percent form is available if a flat delta reads as noise on a
640,000-HP entity.

### ✅ Q19 — the existing 84: **RE-DERIVE EVERYTHING ONCE, then append-only from there.** *(owner)*

One clean rebuild against the new anchor, so all ~900 species are classified by identical rules and
there is no two-generation seam for a balance pass to reason about.

**The cost, stated plainly:** the 84 committed commander effects and 84 themes are regenerated
stochastically — today's names and doctrines will not survive verbatim. The append-only window is
already closed (G4 wrote its first row), so this is a **deliberate reviewed correction**, exactly the
category `generate_families.py`'s refusal guard was built to force a human to confirm.

**Sequencing that falls out of it:** the rebuild happens *once*, before the roster grows — re-deriving
84 rows is cheap, re-deriving 900 is not.

### ✅ Q20 — run scope: **FULL RUN, behind a state machine with pause / resume / cancel / rerun / overwrite-all.** *(owner)*

Owner: *"so we will generate what we want and stop when we want."*

**This is a real feature, not a run mode.** seedsmith today has per-subject checkpointing
(`SqliteSaver`, thread-id per subject) and skip-existing idempotency, but **no run-level control** —
a run is started and either finishes or is killed. What is asked for is a *job* with observable state:

| Control | What it must mean |
|---|---|
| pause / resume | stop between subjects without losing completed work — the checkpointer already supports the per-subject half |
| cancel | stop and leave the corpus in a consistent state, never half-written |
| rerun | regenerate a named subset — `--only` and `--stale` already exist as the primitive |
| overwrite-all | the deliberate full re-derivation Q19 calls for, and it must refuse without an explicit acknowledgement |

The existing `--only` / `--stale` / `--force` flags plus the append-only refusal guard are the raw
material; the gap is a **run record** that survives the process, so a resumed run knows what the
previous one finished.

### ✅ Q21 — HP vs damage: **ONE CURVE. The primary stats already carry the divergence.** *(owner)*

Owner: *"no, we use primary stats, hp and damage system already cover it, don't add more mechanism,
imbalance."*

**The prior-art finding was real but the conclusion was wrong.** Every surveyed system does inflate
durability faster than lethality (D2 6.2× vs 1.85×, PoE 2,989× vs 352×, D3 **16,958× vs 163×**) — but
those games have no aptitude layer, so the only place they *can* express the divergence is the curve.
This design has somewhere better to put it.

**Where the divergence actually lives.** `gk-core/data/tuning/aptitudes.v2.json`'s `familyRead` classifies
`combat.power` and `combat.defense` **both as `magnitude`** — so both read `P(Θ)`, one curve, PS-3
intact. What differs is the **share** each channel receives, and share is the aptitude system's job:

| Aptitude | Its channel family (roster.json `role`) |
|---|---|
| Might | universal offence — power |
| Fortitude | mitigation — defense · absorption · reduction |
| Vigor | shield — capacity / regen / toughness |

Two creatures at the same `Θ` with different `aptitudePrimary` already produce different effective HP and
different damage. **A per-channel growth rate would be a second mechanism computing the same thing,
and two mechanisms for one outcome is how imbalance gets in.**

**So the rule stands unchanged: one index, one function, magnitudes read `P(Θ)`.** The HP-vs-damage
question is answered upstream, by allocation.

### ✅ Q22 — the contract: **a well-defined JSON STRUCTURE with per-attribute descriptions — not a frozen enum list.** *(owner)*

Owner: *"closed contract is not closed enum, it is well defined structure json, so LLM know how to
generate each attribute in json because it understand the description of each attribute. each pipeline
must cover 1 or some attributes."*

**This reframes the question rather than answering it, and dissolves the Arknights tension.** The
options offered assumed "closed" meant "frozen vocabulary". It does not. Reliability comes from three
things, none of which is enum immutability:

1. **A defined JSON structure** — the schema shape, enforced by constrained decoding, so a malformed
   answer is unsampleable rather than merely detected.
2. **A description per attribute** — the model generates the right value because it *understands what
   the field means*, not because the value list is short. This is what JSON Schema `description` is
   for, and it is the part a frozen-enum framing ignores entirely.
3. **Narrow pipelines** — *"each pipeline must cover 1 or some attributes."* One question per call.
   A pipeline answering one well-described attribute is reliable in a way that a pipeline answering
   fifteen at once is not.

**Consequence for §6.2 ④, which was written against the wrong frame.** The freeze/grow split it
proposed is still *useful* — knowing which axis is cheap to widen remains true, and `element` really
is the expensive one — but it is **not the reliability mechanism**, and it should not be treated as a
constraint on the vocabularies. A vocabulary may grow (Arknights' content stream is legitimate) as
long as the structure and the descriptions stay well-defined.

**Consequence for pipeline design.** The contract's eighteen variables do **not** imply eighteen
pipelines, nor one pipeline. They imply a decomposition where each pipeline owns *one or a few*
attributes that share a judgement — for instance `elementPrimary` + `elementSecondary` together
(one typing judgement), `aptitudePrimary` + `aptitudeSecondary` together (one build judgement), and
`powerBand` alone (which is number-derived and LLM-audited anyway). **The decomposition is a spec-phase
decision; what this answer settles is the principle it must follow.**

---

## 6. The contract — revised against prior art

The owner's framing: *"we need to clear all variables that affect the generator before we make
generator spec. LLM need a closed contract to make reliable outcome."*

§6.1 is the contract as the twenty answers left it. **§6.2 is what the eight research passes
changed** — recorded as changes rather than folded in silently, so the reasoning survives.

### 6.1 The variables

| Variable | Openness | Vocabulary | Size | Source |
|---|---|---|---|---|
| `side` | closed | plant · zombie | 2 | captured |
| `elementPrimary` | closed | fire · ice · air · earth · light · dark | 6 | classified |
| `elementSecondary` | closed | same, **or `none`**; max 2 concrete, `omni` illegal in a slot | 6+1 | classified |
| `aptitudePrimary` | closed | the 12 aptitudes | 12 | classified |
| `aptitudeSecondary` | closed | the 12, **or `none`**; `pure` flag when same posture | 12+1 | classified |
| `posture` | closed | Force · Finesse · Bastion | 3 | **derived** from `aptitudePrimary` |
| `powerBand` | closed ordinal | nuisance → calamity (threat nouns) | 10 | number-derived, LLM-audited |
| `rarity` | closed ordinal | chaff → almanac (the item ladder) | 10 | classified |
| `deployMode` | closed | PlantAvatar · HypnoAlly | 2 | classified |
| `acquisition` | closed flags | Summonable · CaptureOnly · EventOnly | 3 | classified |
| `variants` | closed set | normal · ancient · mutated · corrupted · blessed · cursed · shiny | 7 | named by LLM; **count** from rarity |
| `resourceProfile` | closed subset | hp · stamina · hunger · spirit · qi · poise | 6 | classified, posture-validated |
| `basis` | closed ordinal | observed · stated · inferred · blocked | 4 | **derived** from which source produced the number |
| `family` | **open** | 19 today | grows | classified |
| `traits` | **open** | — | grows | classified |
| **`attackTempo`** | closed ordinal | **NEW — see §6.2** | ~5 | classified |
| **`reach`** | closed ordinal | **NEW — see §6.2** | ~4 | classified |
| **`targetPreference`** | closed | **NEW — see §6.2** | ~6 | classified |

**Eighteen variables. Two derived, one hybrid, fifteen classified. Not one is a number.**

### 6.2 What the research changed

**① Dual typing is required, not optional.** §4.1 computes it: single-element gives **12.6 units per
grid cell — Fire Emblem Heroes' failure zone**; dual gives **3.59 — the Genshin/FGO safe band**. The
owner already wanted Pokémon-style hybrid typing; this makes it load-bearing rather than flavour.
`elementSecondary` is therefore expected to be populated for most of the roster, not exceptional.

**② Three variables were missing, and they are universal everywhere else.** Attack rate, range and
targeting appear in *every* engine surveyed — SC2 carries a targets-allowed mask on 57 of 57 weapons —
and §4.2 measures their worth directly: type + **speed modes** + resistances lifts creature uniqueness
from **63% to 93%**. They are also the only axes besides element and aptitude that survive the
"a faster Banshee is still a Banshee" test (§4.8).

Verified absent on our side: `DerivedStatChannels` registers **`move.range` and nothing else** for
tempo or reach. `EntityBaseline.AttackInterval` exists but is *captured from PvZ*, not RPG-native —
so on the lawn PvZ supplies tempo, and in **web battle**, which the owner named as the home of the
RPG's own base stats, a generated creature currently has none.

They are ordinals, never numbers: `attackTempo` (something like *ponderous · slow · steady · quick ·
flurry*), `reach` (*melee · short · long · siege*), `targetPreference` (which population it prefers).
The deterministic layer turns each into a real interval or distance, exactly as `powerBand` becomes `Θ`.

**③ Every closed enum needs an explicit `none`, never an omitted field.** SC2's Archon, Ghost,
Ravager, Baneling and Queen carry **neither** Light nor Armored, which makes them immune to a large
share of every bonus-damage term in the game (§4.8). **Tag absence is a stat.** A model that is merely
unsure must not be able to hand a creature a hidden defensive buff by leaving a field out. `none` is an
answer; a missing key is a defect.

**④ Know the cheap-to-widen axis — but it is not the reliability mechanism.** §5 Q22 corrected the
frame this item was written under: a *closed contract* is a well-defined JSON structure with a
description per attribute, **not a frozen vocabulary**. So the table below is planning information,
not a constraint — a vocabulary may grow, as Arknights' does, provided the structure and descriptions
stay well-defined. Every studio widened the axis with
the fewest downstream dependencies and left the load-bearing one alone — FEH widened weapon colour
(feeds one ±20% modifier) five times and **never** touched movement type (~100 skills key off it).
For this design:

| Axis | Cost to widen | Verdict |
|---|---|---|
| `element` | matchup table + 196 combat channels + every reaction | **Most expensive. Treat as frozen.** |
| `aptitude` | 12 is a computed product of 3 postures × 4; the class system, aura ids and `ZombossPatterns` all key off it | **Expensive.** |
| `rarity` | five verified consumers (summon rates, both pity thresholds, `FusionRoller.SlotsFor`, `SoulEarnPolicy.DiscoveryDelta`, `shard.{rarity}` ids) | Expensive. |
| **`powerBand`** | **nothing consumes it yet** | **Cheapest — the designated growth axis.** |
| **`family` · `traits`** | already open by construction | Free. |

**⑤ `family` does not need to grow toward 270.** The rarefaction result (§4.1) says a *flat* taxonomy
at 900 units wants ~270 families — but Ragnarok Online gets 417 mechanical identities from **27
authored values across four orthogonal axes**. This contract is already multiplicative, so ~19
families is adequate and the axis stays open for organic growth.

**⑥ The distinctness burden does not rest on this contract.** §4.2 is unambiguous: stats do not
distinguish units — **abilities do**, and a 900-unit roster needs roughly **1,500–3,500 named ability
instances**. The anchor's job is to be a correct, cheap, orthogonal *index*; the thing that makes 900
creatures feel different is the ability layer, which is a separate and much larger generation program
(§5 Q9's passive skill graph). **Recording this so a downstream session does not mistake a complete
anchor for a complete roster.**

### 6.3 The combinatorial position, restated

With dual typing the primary grid is **21 element-combinations × 12 aptitudes = 252 cells** for ~904
species — **3.59 per cell**, inside the band where no surveyed game has documented power-creep
problems. Adding `powerBand` and `rarity` multiplies the space enormously, but neither is a
distinctness axis: a stronger or rarer version of a creature is not a different creature (§4.8). **The grid
that matters is 252 cells, and it is adequately, not comfortably, filled.**

### 6.4 Both rulings have since been made — recorded so this section is not re-opened

This section listed two owed rulings while it was written. **Both were answered by the owner the same
day**, and the answers are §5 Q21 and §5 Q22. Kept as a pointer rather than deleted, because the
reasoning that made them look open is still worth reading:

- **Q21 — HP vs damage curve → ✅ ONE CURVE.** The prior-art divergence is real, but those games have
  no aptitude layer. Here the divergence lives in *allocation share*, not in the curve. See §5 Q21.
- **Q22 — closed contract vs content stream → ✅ neither, as posed.** A closed contract is a
  well-defined JSON structure with a description per attribute, not a frozen vocabulary. See §5 Q22,
  which also demotes §6.2 ④ from a constraint to planning information.

---

## 7. The aspect → atom gap, closed 2026-09-01

An earlier draft of this document recorded an honest gap: the aspect→atom decomposition was left out
because `effect-atom/definitions.md` had only been read at section level, and **that document wins
over any spec**. It has now been read in full. The gap is closed, and the answer is smaller than
expected.

### 7.1 An aspect needs no new atom vocabulary. It is a `species-passive` container.

`definitions.md:41` gives the container grammar:

```
container_id : ^(item|trait|skill|species-passive|patron|world-buff)\.[a-z0-9-]+$
```

**`species-passive` is already a legal container kind.** So an aspect is not a new concept in the atom
layer — it is a container that puts atoms on a creature's effect list, exactly as an item or a trait does.

The model §0 states plainly, and it settles the shape:

> **Items have no behaviour. Actors do.** … An item, trait, skill, or species passive is a **source**
> that put the atom on the list. None of them participates at runtime.

So "what does this creature do" decomposes to: *which atoms does its species-passive container carry.*

### 7.2 ⭐ Rarity's atom mechanism is the mechanism we already adopted

This is the find. §4 of `definitions.md` defines what a container's rarity governs:

| Column | Meaning |
|---|---|
| `pool_rolls` | **how many atoms are drawn** |
| `min_tier` / `max_tier` | **the tier window the pool may offer** |

That is **exactly** the count-band-plus-tier-window that §5 Q4 adopted from the item rarity ladder,
and it is the same reason §4.5's prior art gives for rarity buying breadth rather than power. **The
creature-rarity decision and the atom-container mechanism are one mechanism, not two that must be
reconciled.** A creature's rung sets how many atoms its aspect rolls and from which tier window; nothing
new has to be designed for that.

Two further rules fall out for free:

- **Pool grouping defaults to `(family_id, variant)`**, so a container may roll *fire* power and *ice*
  power — two variants of one family. **That is dual-element typing expressed in the atom layer with
  no extra work.**
- `pool_rolls ≤ count(distinct group HAVING max(weight) > 0)`, and an all-zero-weight pool is rejected
  `UnsatisfiablePool`. **Silent under-filling is already impossible.**

### 7.3 What a generator may and may not emit

`definitions.md` decides this, and it tightens the contract in §6:

| Field | Who produces it |
|---|---|
| `atom_id` | **Never authored.** Derived as `{family_id}[.{variant}].t{tier}` and validated against its columns; a mismatch is `IdMismatch` |
| magnitudes | **Never authored.** Tier bands are authored *per channel family* and *"never copied across"*; units are non-negotiable — game units for primary channels, resolver points for derived, integer per-mille for chances |
| `family_id`, `variant`, `tier` | authorable |
| trigger | authorable, from **4 event triggers** (`OnSpawn`, `OnDamageDealt`, `OnDamageTaken`, `OnDeath`) plus `OnTimer` |

**⛔ `stat.modify` and `stat.derived` must declare NO trigger at all.** They are permanent modifiers;
apply and revert are runtime lifecycle. Authoring a trigger on either is `TriggerNotAllowed`, and
E7 must compile them as `EffectType = Passive` — *"a triggerless atom compiled with the default type
satisfies neither and would never apply at all. This is a compiler rule, not an optional one."*

This is the same shape as the anchor's own rule: **the model chooses categories; magnitudes come from
tables.** An aspect pipeline would emit `(family, variant, trigger)` and never an id, a tier value, or
a number.

### 7.4 What is still genuinely blocked

- **`stat.derived` is quarantined everywhere** (§2 W1) — no opcode, no bag branch, no sink arm, and
  battle reads channel mods only from `TraitBattleCatalog`. It is the kind an aspect would most
  naturally use to write a derived channel, so an aspect built on it is **inert until that wiring
  lands**. A wiring gap on a scheduled path, not a wall.
- **`aspect-scope` is reverted** (§5 Q9), so one creature has exactly one aspect — its own. The container
  is 1:1 with the species, which makes `species-passive.{speciesId}` the natural container id.
- **The full aspect vision remains blocked on two unbuilt programs** named in Q9: hybrid element
  typing, and the passive skill graph. This section closes the *decomposition* question, not those.

### 7.5 What this changes about the creature-seed program

**Nothing in this document's scope, which is why the gap was safe to carry.** Aspect generation is not
among §6's eighteen anchor variables and is not part of this program. What §7 buys is that when aspect
*is* specced, it starts from a settled decomposition rather than reopening the atom layer — and that
the rarity work already done is directly reusable rather than parallel.

---

## 8. What this document deliberately does not do

No spec. No plan. No schema. No code. **§7 closes the one honest gap this document previously
carried**; the aspect *decomposition* is settled, but aspect generation remains out of scope and
blocked on the two unbuilt programs §5 Q9 names.

---

## 9. Fusion trait/action inheritance + soul-cost choice, and why species effects stop rolling per player (added 2026-09-06)

**Owner's own framing:** *"the fusion should be unique that allow user sacrifice they strong creature to
make stronger creature like get rare trait/specific action from parent or special bonus from roll but
they cannot get everything, only pick some of them with the cost and some other will be random, so
this is roll with fixed version and cost soul, other stats will random."* Inspired explicitly by SMT's
fusion skill inheritance and PoE/Last Epoch style crafting. A second, connected owner decision landed
the same session: **creature species base stats AND base effects/traits must be identical for every
player** (a Pokémon-species-compendium model), with individual variance moved to wherever a specific
summon/gacha/capture/fusion result can be special — this section is that "wherever."

### 9.0 Principles restated (Step 0, this repo's own discipline)

Every mechanism below is server-side RPG-layer data (`FusionRpg.Core`/`FusionRpg.Data`) — souls, traits,
fusion recipes, rolls. None of it needs PvZ/Unity to represent anything; the lawn never has to "know"
what a creature inherited. **Read before propose** governs everything that follows: every claim below is
checked against the running code or a primary spec, not recalled from summary, with `file:line` for
what already exists.

### 9.1 Built — a real fusion trait roll already ships, further along than either the owner or this
session's own earlier read assumed

`FusionRoller.Roll` (`gk-core/src/FusionRpg.Core/Creatures/Fusion/FusionRoller.cs:18-50`) is live, tested, and
wired into the real `/api/fusion/execute` path (`RpgStore.Fusion.cs:217`) **today**:

1. The player supplies exactly **one** `pickedTraitId` (`RpgStore.Fusion.cs:21`, `FusionRequest`
   record) — it must be a real `CreatureTraitCatalog` id and must appear on one of the two sacrificed
   (input) creatures' own trait lists (`RpgStore.Fusion.cs:204-206`, refuses `trait.missing`/not-on-inputs
   otherwise). **This is player agency, already shipped** — the class doc's own words: *"Pick-one is
   player agency."*
2. The remaining slots — `SlotsFor(resultRarity)`, i.e. `StarPolicy.Tuning.SlotsByRarity[rarity]`,
   already a real tunable in `gk-core/data/tuning/fusion.v1.json` (`slotsByRarity`: 1 for Chaff/Sprout/Grafted,
   2 for Cultivated/Fused/Chimeric/Heirloom, 3 for Firstseed/Sunwoven/Almanac) — are filled **randomly**
   from the combined remaining input-creature trait pool, via a **named, seeded RNG stream**
   (`SeededRng.DeriveStream(seed, "fusion:traits")`, already following `definitions.md` §4a's "one
   stream per layer" law). An exhausted pool yields fewer traits, never padding from elsewhere — the
   class doc's own words again: *"the rest comes from the combined INPUT pool."*
3. A separate `"fusion:variant"` stream rolls a rare cosmetic **shiny** variant (odds shared with
   `SummonRoller.ShinyOneIn` so the two can never drift apart) — this is the existing, adjacent
   "special bonus from roll" the owner's message also named, already built, orthogonal to trait
   inheritance and not something this section needs to touch.
4. A **separate, already-shipped, simpler mechanic** exists for **promotion** (star growth within the
   same species, not fusion): `FusionRoller.RollPromotionTraits` (`FusionRoller.cs:52-74`) keeps
   existing traits **in order** and rolls only the NEW slots from the species' own `TraitPool` (not the
   fusion inputs) — *"the creature grows into its kind, not its fuel."* No player choice, no soul cost,
   today. §9.6 below asks whether that should change too, rather than assuming it should.

**Net effect: roughly 80% of "the mechanism" the owner asked for already exists and is already tested.**
What's missing is narrower than "design a new feature" — see §9.2-§9.4.

### 9.2 The one real reason this mechanism does nothing today — a wiring gap, not a design gap

`combinedInputTraits` and every sacrificed creature's own `TraitIds` are **always empty**, for every one
of the 829 real species, unconditionally — `RpgStore.Species.cs` (`BuildCreatureSpeciesSnapshot()`,
~line 246) hardcodes `TraitPool = Array.Empty<string>()`, never `s.TraitPool`, confirmed by a direct
DB-edit-and-remint test this session (editing `trait_pool_json` had no effect — the hardcode never
reads the column at all). This is already documented as a deliberate, deferred 2026-09-02
`catalog-runtime` decision (`SpeciesCatalogDiffTests` already caught and reverted one attempt to wire
the anchor's own OPEN flavor-text `traits` field directly into this CLOSED gameplay vocabulary — the
two are genuinely different vocabularies sharing one field name, not the same data under two names).

**Consequence: `FusionRoller.Roll` cannot select or roll a single trait for any real species today**
— not because the mechanism is unbuilt, but because every input to it is `[]`. Assigning real
`CreatureTraitCatalog` ids to all 829 species (§9.5) is a **prerequisite that activates already-shipped
code**, not new plumbing.

**One real, small request-shape change is also needed, not a redesign:** `FusionRequest.PickedTraitId`
(`RpgStore.Fusion.cs:21`) is a single `string?`. Supporting more than one guaranteed pick (§9.3) needs
this to become a list (`PickedTraitIds: IReadOnlyList<string>`), with `FusionRoller.Roll`'s own
pick-one branch generalised to pick-N-then-random-rest — mechanical, bounded, the same shape the
method already has.

### 9.3 Real gap 1 — soul-gated, tunable pick count (the owner's actual new ask)

Nothing charges souls for a trait pick today, and the pick count is hardcoded at exactly one. The
owner's ask — "pick some with a cost, cost soul, other stats random" — needs:

- **A tunable extra-pick count**, capped by `slotsByRarity[resultRarity] - 1` (cannot guarantee more
  picks than the result has slots for) — the same shape `slotsByRarity` already has, extended, not
  replaced.
- **A soul cost per extra pick**, shaped like the two costs `fusion.v1.json` already carries side by
  side — `recipeCost` (150→1000 souls, scaling with output rarity) and `promotionCostByRarity`
  (150→1000 souls, same shape) — so a new `inheritCostByRarity` (or per-pick cost scaled by the
  **picked trait's own rarity/source**, an open question, §9.6) slots in as a third row of the same
  established table, not a new mechanism.
- **The spend itself** is `TrySpendSouls(playerId, amount, reason, correlationId)` — already the one
  real primitive (`spec-soul-economy.md`), already idempotent via `(playerId, correlationId)` replay,
  already required to run in the SAME transaction as the fusion's own writes
  (`spec-soul-economy.md`'s own rule for "feature flows that pair a spend with further writes"). **A
  new spend sink is `spec-soul-economy.md`'s own explicit "Ask first" boundary** — this section is
  that ask, not a decision made here.

### 9.4 Real gap 2 — is "action" inheritance the same mechanism as trait inheritance, or a second one?

The owner's message names two inheritable categories: "rare trait" (§9.1-§9.3 above, already
mechanism-complete) and "**specific action** from parent." No `CreatureAction` concept exists on
`CreatureSpeciesDef` today (grepped — absent); the closest real analogue is `species-passive.{speciesId}`
— the per-species effect **container** T5.3 (`species-effects`) already designs against
(`docs/architecture/creature-seed/spec-species-effects.md`), built on the SAME closed
`slots → affixes → atoms → tiers → values` resolution order `definitions.md` §4a already normalises,
with its own named RNG streams (`affix.slot`, `affix.draw`, `affix.tier`, `atom.value`). **Real, open
question, not decided here:** does "inherit a specific action" mean the fusion result can pick a
**specific affix** off a sacrificed parent's own already-rolled `species-passive` instance (the exact
same shape as picking a trait, just at the affix layer instead of the trait layer, reusing
`affix.draw`'s own stream family) — or is this asking for something genuinely new (an action distinct
from an atom-backed affix)? §9.1's mechanism is a strong template either way, but which concrete rows
it operates over is unresolved.

### 9.5 The connected, binding-principle-level change: species effects stop rolling per player

`docs/DESIGN-GATE.md` §1 (row "Creature species generation") is explicit and **currently binding**:
*"Species stats are deterministic and shared; only effects roll, per player, at runtime — never assume
a species table is finished content once generated."* `tasks/seed-to-concrete-plan.md`'s own
architecture decisions restate it (*"Species stats are deterministic and shared; only effects roll. This
is what keeps `WaveCatalog`, `CreatureRecipeCatalog`, `CreatureMaterialCatalog` and `LaneCost` free of player
context."*), and it is built exactly that way: `SpeciesMaterialiser.Materialise` (T5.5) reproduces a
**different** roster per `(worldSeed, catalog_revision)` by design — two players' "Peashooter creature"
base effects differ today, on purpose. **A third program already cites this exact sentence as a
general principle**, not a creature-only detail: `docs/architecture/passive-tree/spec-tree-catalog.md:50`.

**The owner's ask directly narrows this principle, and does not violate its own stated reason.** The
reason given — keeping the four listed catalogs "free of player context" — is satisfied *more*
strongly by a fixed, shared value than a per-player-rolled one (a constant needs no player context to
read at all). The original "roll per player" choice for species-base effects was a **product/variety**
decision (every player's collection should feel individually theirs), not a technical necessity — and
the owner's own counter-argument (a shared community/wiki understanding of "what a Peashooter creature
does" is real player-facing value that per-player rolling destroys) is a legitimate, competing product
reason, not a mistake in the original one.

**What actually needs to change, precisely, and what does not:**

| | Before (current binding text) | After (this section's proposal) |
|---|---|---|
| Species **stats** | Deterministic, shared | **Unchanged** |
| Species **base effects** (fixed core + eligible pool, T5.3) | Rolled per `(worldSeed, catalog_revision)` via `SpeciesMaterialiser` | **Fixed, shared** — resolved once at seed time (LLM decides identity, deterministic code resolves magnitude — the same split every other generator in this program already uses), committed like `_fusion-recipes.json` |
| **Individual-instance variance** (a specific fusion result, capture, or gacha pull) | Does not exist as a concept | **This is where rolling still happens** — §9.1-§9.4 above |
| `passive-tree/spec-tree-catalog.md`'s own citation of the same principle | Cites the creature rule as precedent | **Out of scope here** — this section narrows the CREATURE application only; passive-tree's own model is untouched unless that program separately decides to revisit it |

This is a real, cross-cutting, currently-binding architecture principle being narrowed — exactly
AGENTS.md's *"architecture changes that lock behavior need `decisions.md` first"* boundary, and exactly
why this stays an idea-phase document rather than code: the spec phase should record this as its own
reviewed decision (with the table above as the starting proposal), not silently redefine what "seed →
concrete → per-player" means wherever it's already cited.

**What this means for already-shipped T5.3/T5.5/T5.6/T5.7 work, named plainly rather than glossed
over:** `SpeciesMaterialiser.Materialise`'s own reproduce-per-seed guarantee, `RpgStore.PlayerSpecies.cs`'s
own per-player `player_species` table, and the dev-reforge endpoint's own "re-derive against the
current catalog" behavior were all built and tested against the CURRENT (per-player-roll) principle —
none of it is wrong or wasted (the pure roll mechanism, the transactional write, the idempotent
reforge, the RNG-stream discipline all stay directly reusable), but a spec closing this section needs
to decide explicitly: does the base-species roll collapse to "roll once, at seed time, with no player
context at all" (removing the per-player table's own reason to exist for the BASE layer), while the
SAME materialiser/transaction shape gets reused one layer down for individual-instance variance
(fusion results, captures) where per-player-and-per-instance rolling is exactly what's wanted? That
reuse-not-discard framing is this section's own recommendation, not a decision.

### 9.6 Genre research — concrete numbers and formulas, with sources

**SMT fusion skill inheritance** — the precedent the owner named directly:

- *Nocturne*: normal two-creature fusion inherits up to **4** skills; Sacrifice fusion (three creatures) up
  to **5-6**, bounded by the result's own skill-slot count.
- Across the series generally: *"creatures may have from zero to three inheritable spells"* per source
  creature, and **signature skills cannot be inherited under any circumstances** — a closed exclusion
  set, the same shape as this repo's own `CreatureAcquisition.CaptureOnly` or `AffixValidator`'s closed
  refusal categories (some things are structurally excluded, not merely unlikely).
- **The series' own evolution validates the owner's exact ask**: *"many older Megami Tensei titles
  feature randomized skill inheritance with weighted results... newer Megami Tensei titles give the
  player more control by allowing them to directly choose which skills are passed on."* Player choice
  over randomness is the modern, preferred direction in the series this owner is drawing from — not a
  design risk relative to its own genre.
- [Skill Inheritance — Megami Tensei Wiki](https://megamitensei.fandom.com/wiki/Skill_Inheritance),
  [How many skills can a demon inherit? — GameFAQs](https://gamefaqs.gamespot.com/switch/296161-shin-megami-tensei-iii-nocturne-hd-remaster/answers/592032-how-many-skills-can-a-demon-inherit)

**Path of Exile — Harvest crafting** (the "targeted category, random within it" half of the ask):

- A **Reforge** guarantees a modifier of a specific **tag** (a category, e.g. "life" or "attack") —
  not the exact modifier, not its roll — matching the owner's own "pick some of them" (the category)
  vs. "other stats will random" (the specific value) split closely.
- **Add-then-Remove** is the series' own answer to "I want ONE exact thing, deterministically, without
  the randomness a Reforge still carries" — a two-step combo, not a single "guarantee anything" button.
  Worth naming as a possible SECOND, more expensive tier above a plain guaranteed pick (§9.6 open
  question below), not assumed necessary.
- Crafts themselves are a stored, spendable resource (a cap of 15 at a time) — i.e. even the
  "deterministic" side of this genre's own crafting is still resource-gated, matching the soul-cost
  framing already chosen here independently.
- [Harvest crafting — PoE Wiki](https://pathofexile.fandom.com/wiki/Harvest_crafting),
  [Harvest Crafting Guide — Maxroll.gg](https://maxroll.gg/poe/crafting/harvest-crafting-guide)

**Last Epoch — Forging Potential, runes, glyphs** (the "limited budget, not a hard action-count" half):

- **Forging Potential** is a per-item budget that depletes by a random amount per craft action (0 up
  to roughly the full remaining cost) — a resource ceiling on total modification, not a fixed count of
  actions. A closer analogue to "how many souls you're willing to spend" than to `slotsByRarity`'s own
  fixed slot count.
- **Glyph of Order** removes randomness from a specific step (preserves roll range on an upgrade);
  **Glyph of Chaos** trades a random affix change for a tier upgrade; **Glyph of Despair** can *lock*
  (seal) a chosen affix outright, moving it out of further risk — i.e. the genre's own precedent for
  "spend more to convert a probability into a certainty" on ONE specific slot, which is exactly the
  shape "pick this trait for a soul cost, or leave it to the random pool" already has.
- **Critical Success** grants a small chance of a fully free extra action — an interesting, optional
  parallel to `FusionRoller`'s own existing "shiny" bonus-roll, if the owner ever wants inheritance
  itself to have a rare "free extra pick" chance layered on top of the paid picks (not proposed here,
  named as a real option for the spec phase).
- [Crafting — Last Epoch Wiki](https://lastepoch.fandom.com/wiki/Crafting),
  [Crafting Basics Guide — Maxroll.gg](https://maxroll.gg/last-epoch/resources/beginner-crafting-guide)

**The common shape across all three, and why it fits what's already built here:** a hard or
resource-gated CEILING on total control (SMT's slot count / Last Epoch's Forging Potential /
`slotsByRarity` itself), player choice over a CATEGORY or specific target within that ceiling (SMT's
direct pick / PoE's tag-targeted reforge), a COST for exercising that choice (Last Epoch's FP spend /
souls here), and RANDOMNESS filling whatever the player didn't or couldn't afford to control
(`fusion:traits`'s own existing pool-draw, unchanged). Every one of these four already has a real,
named analogue in this codebase today — the ask is a genuine, well-precedented feature, assembled from
pieces that mostly already exist.

### 9.7 Open questions for the spec phase — named, not answered here

Per this document's own §8 boundary (no spec, no plan, no schema, no code), the following are real
open questions this idea phase surfaces rather than resolves:

1. **What counts as "inheritable," precisely** — traits only (mechanism-complete, §9.1-§9.3), or also
   affixes off a rolled `species-passive` instance once real content exists (§9.4)? Can both be
   inherited in the same fusion, or is a fusion result's inheritance budget shared across categories?
2. **Is any trait/affix ever exclusion-listed from inheritance**, mirroring SMT's signature-skill
   exclusion — e.g. should a species' own rarest, most identity-defining trait be un-inheritable, so
   players cannot farm it purely through a common fusion partner rather than earning that species
   directly? A real balance question, not a wiring one.
3. **Does the soul cost scale by the OUTPUT's rarity (matching `recipeCost`/`promotionCostByRarity`'s
   existing shape) or by the INHERITED TRAIT's own source rarity** (a rarer parent's trait costs more
   to guarantee, independent of what the fusion produces)? Both are real, precedented options above.
4. **Does `RollPromotionTraits` (§9.1 point 4, star growth within a species) gain the same
   choice-plus-cost treatment**, or does it deliberately stay simple/free, on the reasoning that
   growing *into your own kind* is a different, lower-stakes moment than fusing two different creatures
   away? Not assumed either way here.
5. **What is the actual pick-count ceiling formula** — reuse `slotsByRarity` as-is (so a max-rarity
   fusion could in principle guarantee all 3 slots, at rising soul cost per pick), or a separate,
   smaller cap so randomness is never fully eliminated even at the top rarity? PoE's own Reforge (a
   tag, not the exact roll) suggests never fully removing all randomness is a deliberate genre choice,
   not an oversight to fix.
6. **Does this apply to every fusion recipe indiscriminately, including the Phase 8 cross-rung
   gap-fill recipes** (`crossRungGapFill: true`, 14 of 709 today) — those already sit slightly outside
   the ladder's normal shape; whether inheritance treats them identically or needs its own note is
   open.
