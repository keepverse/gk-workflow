# Task 12 — Cage eligibility rank floor (in-fence half) — row left OPEN on the caller wire

## CLOSE-OUT 2026-09-24 (mega-merge QC fix cycle 10): wire re-landed, root cause found, row DONE

The reverted caller wire was **re-landed** and the manager's reopen diagnosis is resolved:

- **Root cause of the "Almanac floor does not refuse" reading: a TEST FIXTURE bug, not the gate.**
  The below-floor test built its candidate from the shared `WildSpecies` fixture, whose predicate
  (`Acquisition != CaptureOnly && TraitPool.Count > 0`) resolves to **`dolldiamond` — a Sunwoven
  species, the top rarity rung**, which the cage's structural rule (`isTopRung`) has always excluded.
  The endpoint answered 400 for that structural reason, never reaching the rank floor, and the
  test read the 200-vs-400 result as "the floor did not stick". The fixture predicate is now fixed
  to mirror `ExpeditionResolver.WildBand` (non-CaptureOnly **and** not Sunwoven) — the
  "Sunwoven-exclusion fixture fix" the reopen note named. (The pre-wire endpoint was inert, so the
  fixture bug had been invisible.)
- **Wire re-landed** (`gk-core/src/FusionRpg.Server/DelveWildEndpoints.cs:HandleJoin`, shared by `/talk` and
  `/cage`): passes the candidate's own catalog rank into `Cage.OccupantEligible`; structural inputs
  mirror `WildBand` (`== CaptureOnly`, `== Sunwoven`); refusal `wild.below-rank-floor` BEFORE any
  spend; an unknown species keeps `TalkJoin`'s own refusal rather than a fabricated rank; price
  rank-blind.
- **Proof:** `DelveWildEndpoints` 15/15 (a new below-floor test asserts the exact
  `wild.below-rank-floor` reason, souls untouched, no mint, under an Almanac floor); whole
  `FusionRpg.Server.Tests` 862/862; `CageTests` 13/13; `guard-magic-numbers` OK;
  `guard-population-pin` 0 findings.

The in-fence half below (the predicate + its Core proofs) is unchanged and still green.

---

Lane `cs-rank` (session `creature-seed-rank`, branch `cmdc/cs-rank`), 2026-09-23.
Row: `tasks/creature-seed-todo.md` Task 12. Spec: `docs/architecture/creature-seed/spec-species-rank.md` §6.
Edited: `gk-core/src/FusionRpg.Core/Delve/Wild/Cage.cs` (`OccupantEligible`), `gk-core/tests/FusionRpg.Core.Tests/Delve/Wild/CageTests.cs`.
**The row is NOT closed:** the predicate now carries the floor and is proven, but it still has no production
caller — the Delve wild endpoints assemble the occupant spec themselves and live in
`gk-core/src/FusionRpg.Server/**`, which this lane's fence denies (measured below).

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Floor on `OccupantEligible` | `dotnet test gk-core/tests/FusionRpg.Core.Tests --nologo --verbosity quiet --filter "FullyQualifiedName~CageTests\|FullyQualifiedName~DelveWild\|FullyQualifiedName~Wild"` | **Passed! — Failed 0, Passed 160, Total 160, 543 ms** | `Cage.cs` |
| Pass-through proof | same run — the pre-existing theory `OccupantEligible_never_a_capture_only_species_never_the_top_rung` | its four expectations are unchanged, now passing `rank: null` — which is simultaneously the shipped compiled-roster state (every compiled species carries no rank) and the proof that the floor narrows nothing at the shipped bottom rungs | `CageTests.cs` |
| A raised floor narrows, and a skipped rank is not admitted | same run — `A_raised_cage_floor_refuses_below_floor_and_rank_skipped_candidates` | at a Heirloom floor: below-floor refused, **rank-skipped refused** (null maps to the bottom rung at the gate), at-floor eligible; and the two structural rules still decide first at any floor (`CaptureOnly` refused, top rung refused) | same |
| Pricing untouched (rarity-keyed) | same run — `The_cages_price_stays_rarity_keyed_and_never_reads_rank` | `OfferPricing.Contract(Fused, thetaRoom: 3, loyalty: 500, loyaltyMax: 1000, tuning)` returns the SAME value with the floor at the bottom and at the TOP rung — the price function takes rarity/thetaRoom/loyalty and nothing else | `CageTests.cs` |
| No regression in the rest of Core | `dotnet test gk-core/tests/FusionRpg.Core.Tests --nologo --verbosity quiet` | **EXIT=0 — Passed! Failed 0, Passed 9596, Skipped 0, Total 9596, 1 m 28 s** | — |
| Static guards | `guard-magic-numbers` · `guard-population-pin` | `M1=0 M2=0 M3=0 M4=0` · `total 0 finding(s)` | — |

## What blocks this row (exact, and measured)

**`Cage.OccupantEligible` has NO production caller, and the caller-side wire is on a denied path.**
Measured 2026-09-23: `grep -rn "OccupantEligible" src/ tests/ tools/ --include=*.cs` returns exactly two
hits — the definition and `CageTests`. That is **pre-existing**, not introduced here: the spec's own gate
table says so ("**No Delve-side band selector exists** … talk/cage commit caller-assembled specs
(`DelveWildEndpoints.cs:22-27`)"), and that endpoint is `gk-core/src/FusionRpg.Server/**`, which this lane's fence
denies (`verify-change -Paths gk-core/src/FusionRpg.Server/FusionEndpoints.cs -Session creature-seed-rank` answers
`path is outside session scope`; the runner's allowed-path list excludes `gk-core/src/FusionRpg.Server/**` and
`gk-fusion/src/FusionRpg.Injector/**` entirely). So the predicate now carries the floor and is tested, but no host
passes a rank into it, and the gates' tuned floors have no production effect — the same denied-path gap as
T8's boot wire and T9's payloads. The signature takes `CreatureRank?` as a REQUIRED parameter (not an
optional one) precisely so that whoever wires the real cage path is forced by the compiler to supply it.

## NOT proved / declared gaps

- No end-to-end cage/talk resolution exercising the floor: that path needs the Server endpoint.
- The pricing assertion proves rank-blindness of `OfferPricing.Contract` under a raised floor; it is not a
  claim that any shipped price changed (none did — no tuning file moved in this task).
- The other `WildVerb`/talk-tree behaviour in this file is untouched by the change (its own tests are green).
