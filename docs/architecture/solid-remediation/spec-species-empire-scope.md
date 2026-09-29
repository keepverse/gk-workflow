# spec — `species-empire-scope`

**Module 11 of `solid-remediation`.** Register entries: **S1, S2, S3, S7, S8, D9**. Depends on
`battle-mode-parity`.

Sequenced after mode parity because S2 needs battle to have a compose worth adding a species term to.

## Objective

Species progression is scoped to the right empire, credited to the right owner, and reaches battle. Today
a lawn zombie is credited to the human player, Zomboss's empire earns nothing, and a level-4 plant type
composes exactly like a level-1 one.

## The defects

| Id | Defect | Severity |
|---|---|---|
| **S1** | A lawn zombie is credited with the **human player's** species progression | crit — scope |
| **S2** | Battle receives **no species allocation at all** | major — mode |
| **S3** | **Nothing credits progression to Zomboss's empire** | crit — scope |
| **S7** | A plant type at level 4 composes **exactly as** one at level 1 | major — orphan |
| ~~**S8**~~ | ~~A **Bound unique** still resolves the empire-species fallback **on the hot path**~~ — **STRUCK 2026-09-17: already fixed before this program began.** See below | — |
| **D9** | **Kill attribution is absent outside the lawn**, and on the lawn the general horde has no owner row, so no empire earns from it (`MatchHost.cs:322-324`) | rule 2, responsibility 17 |

S1 and S3 are the same defect from two directions: the species cache key has **no empire dimension**, so
every lookup resolves to whoever asked. S8 is the same key on the hot path, where the fallback also costs
time it should not.

**S8 was unassigned in the first draft of the map** — found by the 2026-09-17 standards review. It was
placed here because it looked like the same key and the same fallback.

### ⚠️ S8 is struck: its premise is false in the code (verified 2026-09-17)

The register says a Bound unique *still* resolves the empire-species fallback. It does not, and has not
since **2026-09-13**.

- `SpeciesAllocationSource.Resolve` returns at its Bound branch **before** the species lookup runs
  (`return commander + _resolveUniqueAllocation(instanceId);`). Landed in `f1955a1d7`,
  *aptitude-sheet AS-1.1 (`unique-lawn-wire`)*.
- Three tests already pin it, and the first does so by **throwing** if the species path is reached for a
  Bound ctx — `resolveSpeciesId: (side, typeId) => throw new InvalidOperationException("must not be
  called for a Bound ctx")`:
  - `Bound_entity_resolves_commander_plus_unique_never_the_species_lookup`
  - `Bound_unique_sharing_a_species_id_with_a_general_never_inherits_empire_shares`
  - `Not_Bound_falls_through_to_the_species_path_even_when_the_hook_is_wired` (the correct complement)
- `species-progression-ideal.md` records the rule as *"already pinned by a test, and already leaking once
  (W5)"* — W5 being the past leak, already closed.

**Why it was filed anyway.** The 2026-09-17 review that added it read the register, not the code. That is
the failure mode `DESIGN-GATE` names first: *code beats docs; docs beat comments.* An audit entry is a
claim until someone opens the file.

**Struck, not fixed** — the program's definition of done allows *fixed, reassigned, or struck*, and
inventing work for a defect that no longer exists would be the worse outcome. S1 and S3 were real and are
fixed by this module; S8 rode along on their description.

## Shape

**Wire and extend** — the ideal doc's classification, and the reason this is not a rewrite:

1. **Add the empire dimension to the species cache key** (S1, S3, S8). The cache is correct; its key is
   under-specified. This is one of the eleven wires.
2. **Give the horde an owner row** so kills have something to credit (D9). Zomboss's empire is a real
   empire; the lawn's general horde currently belongs to nobody.
3. **Carry kill attribution into every mode** (D9), on the mechanism `battle-mode-parity` unified.
4. **Let the species term reach the compose** (S2, S7) — through `ActorHub`, never beside it.

## How S1/S3 actually closed — three seams, not one (T4.1, 2026-09-17)

"Add the empire to the key" reads as one edit. It is three, and stopping after the first one leaves the
defect standing while looking fixed.

| Seam | Where | What it does now |
|---|---|---|
| The persisted key | `SpeciesAllocation.ScopeKey(playerId, empire, speciesId)` | Dave keeps the unchanged key shape on purpose, so every existing row still resolves and no migration is owed; a non-player empire gets its own `:empire:<token>:` segment |
| The resolve seam | `SpeciesAllocationSource.Resolve` | Derives the empire from `ctx.Side` (`EmpireForSide`) and asks the commander and species terms **separately** — a zombie gets neither of the player's |
| The transport cache | `CheatState.SpeciesAllocation`'s `resolveSpeciesAllocation` delegate | Takes `(empire, speciesId)`, not `speciesId` |

**The third seam is the one that hides.** The commander term was the visible symptom, so fixing it feels
like the end of the job. It is not: `/api/aptitudes/{playerId}` returns the player's `species` map and
nothing else, and the injector cached it under `speciesId` alone. With the first two seams fixed and the
third untouched, a lawn zombie resolved an empty commander — looking correct — and then merged **the human
player's species progression** through a key that could not tell the two empires apart. That is S1 again,
one seam further down.

So the delegate carries the empire, and the cache answers `Empty` for any empire whose rows it does not
hold. Two tests pin it, and both fail if the empire stops being threaded (verified by breaking it):
`The_species_term_is_asked_for_an_empire_and_the_two_sides_ask_for_different_ones` and
`A_lawn_zombie_never_inherits_the_players_commander_or_species_allocation`.

**What is deliberately empty, and what ends it.** Zomboss's empire owns no commander allocation and no
species rows anywhere — nothing writes them yet. So a lawn zombie resolves `Empty` on both terms. Empty is
strictly more correct than another empire's rows, and it is the *honest* answer rather than a silent
default: the moment Zomboss's own rows land, both terms start reading them with no further change at these
three seams. That is `species-progression`'s question, named here and not answered here.

### A fourth seam, found while starting T4.4

T4.1 closed three seams. There was a fourth, and it is the same lesson again: **`SpeciesBaselineAllocation`
accepted an `empire` parameter and never used it.**

The override half keys on `ScopeKey(playerId, empire, speciesId)` and was correct. The baseline half
derives from a **per-player species LEVEL row** (`GetRpgActor(playerId, Species, creatureTypeId)`), and
that lookup ignored the empire it was handed — so a Zomboss ask returned the human player's level-derived
baseline. S1 surviving one path further down, behind a signature that looked threaded.

Fixed the same way the other terms already answer: an empire that owns no rows gets `Empty`. Nothing
writes a Zomboss species level anywhere, so `Empty` is the honest answer rather than someone else's
progression. Pinned by two tests — one through `EffectiveSpeciesAllocation`, one directly on
`SpeciesBaselineAllocation`, because the outer call could start short-circuiting earlier and leave the
parameter lying again with nothing noticing. Both verified to fail when the guard is removed.

**A parameter that is accepted and ignored is worse than one that is missing** — a missing parameter is a
compile error at every call site, while an ignored one reports success. That is what made this survive
T4.1's own verification run.

## ActorHub — the gate

S2 and S7 both add a **species term to an actor compose**. That contribution goes in as an
`IActorStatSubsystem` or a registered atom reader with a non-empty GG-49 `ContributionSourceIds` grammar
id, or it consumes Hub output. **Never a private fold, never a second composer.**

This is the module where "just add it where the number is used" is most tempting and most wrong.

## The cache invalidation rule (DESIGN-GATE §2.16)

This module changes the **key set** of an event-refreshed cache, which is the edge that rule exists for.
The spec must list **every** trigger that invalidates the species cache, **including the edge where its key
set changes** — an entity entering the empire dimension the key now carries. Each trigger needs a test.

**Do not copy a trigger set from a cache with different key-set behaviour.** That is the named failure
mode, and adding a dimension to a key is exactly when it happens.

### The enumerated set (T4.2, 2026-09-17)

All three refresh triggers reach the cache through **one** fetch: `RefreshCommanderAllocationAsync`
parses the `species` map out of the same `/api/aptitudes/{playerId}` response it already reads `shares`
from. There is no second entry point, which is what makes three trigger tests plus one join test
complete rather than merely plausible.

| # | Trigger | Where | Test |
|---|---|---|---|
| 1 | Session start | `RpgClient.StartAsync` | `Trigger1_session_start_refreshes_the_species_cache` |
| 2 | SignalR reconnect | `RpgClient`'s `_hub.Reconnected` handler | `Trigger2_signalr_reconnect_refreshes_the_species_cache` |
| 3 | The `AptitudesUpdated` broadcast | enqueues `aptitudes.allocation.reload`, handled in `CheatCommandRunner` | `Trigger3_the_AptitudesUpdated_broadcast_refreshes_the_species_cache` (both halves) |
| — | The join the other three depend on | `RefreshCommanderAllocationAsync` parses `species` and calls `ApplySpeciesAllocations` | `All_three_triggers_reach_the_species_map_through_the_one_fetch_that_parses_it` |
| — | A refresh reaches entities **already spawned** | `ApplySpeciesAllocations` calls `Stats.Invalidate()` | `Applying_a_refresh_invalidates_live_stats_...` — the species form of the 2026-08-30 defect §2.16 lists by name |
| — | Wholesale replace, never an incremental merge | `_speciesAllocations = bySpeciesId` | `A_refresh_replaces_the_whole_cache_rather_than_merging_into_it` |

### The key-set edge, answered rather than assumed

§2.16's real question is *when does the KEY SET move, and what fires then?* For this cache, two answers:

1. **The empire half does not move on any state change.** It is derived from `ctx.Side` at read time
   and is never stored, so an entity cannot "enter" an empire the way a specimen enters `Bound`. That
   is why adding the empire to the key added **no** fourth trigger. The reasoning is pinned by
   `The_key_set_edge_is_resolved_per_read_and_therefore_needs_no_fourth_trigger`, which fails if the
   empire ever becomes cached state — at which point whoever made that change owes this cache a
   trigger and a test.
2. **The half with teeth is which empires the cache can answer for.** It is fed from
   `/api/aptitudes/{playerId}`, so that set is exactly `{Dave}`. **The day Zomboss's own species rows
   ship, that set changes, and *that* is this cache's real key-set trigger** — a new fetch and a new
   invalidation edge. Nothing writes those rows today, so the honest answer is `Empty`, and
   `The_cache_holds_exactly_one_empires_rows_and_refuses_to_answer_for_another` is what makes the
   future change loud instead of silent.

### What was deliberately NOT copied

The two caches next door have genuinely different key-set behaviour, so neither trigger set transfers:

- The **unique** cache is keyed by currently-Bound instanceIds, so its key set moves on a **bind** — a
  4th trigger this cache does not have and must not grow. That edge was missing once and shipped a real
  defect (2026-09-07: allocate-then-deploy produced an unbuffed actor). Covered by
  `UniqueAptitudeRefreshCadenceTests`.
- The **commander** cache resolves through `MatchCommanderSnapshotHolder`, so a match edge changes its
  answer with **no fetch at all** — which is why `MatchHost` calls `RefreshCommanderAllocationCache()`
  there. The species cache has no match-scoped override, so a match edge is not a species trigger, and
  adding one would be a trigger that cannot fire. Pinned by
  `A_match_edge_is_not_a_species_trigger_and_the_trigger_set_was_not_copied`.

**Where the tests live, and why.** `gk-core/tests/FusionRpg.Guard.Tests/SpeciesAllocationCacheTriggerTests.cs`,
not the injector's own test project — `FusionRpg.Injector.Tests` needs interop refs and **is not in CI**
(`AGENTS.md`). A trigger set whose tests never run in CI is a trigger set nobody is enforcing. They are
source-scan tests because `RpgClient` has no HTTP seam to mock; each one was verified to fail by
breaking the wiring it asserts.

## D9 — the horde's owner, and why null was not "unowned" (T4.3, 2026-09-17)

The lawn's ownership model is `SpecimenOwnershipOracle`: `ptr → owning player id`, **null** for anything
not registered as a specimen. Every vanilla zombie in a wave is unregistered, so the horde resolved to
null and `MatchHost` skipped it outright.

**The conflation.** Null there means *no player row exists*. The code read it as *no owner exists*. Those
are different questions, and collapsing them is what left an entire army belonging to nobody — while
`MatchHost`'s own comment had already said the true answer since the Zomboss-deploy work: *"a vanilla
zombie IS Zomboss's own army, a vanilla plant is the player's."* Nothing read that as ownership.

**The rule: the empire is the army you fight for, not the row that owns you.** `KillAttribution.EmpireOf`
is total over the closed `StatSide` vocabulary, and mind control flips it — a hypnotised zombie kills
for the player, which is the same reading `MechanicalOwnSideOracle` already applies for grants.

**Why the player row cannot decide it.** Zomboss owns a real, distinct player row
(`RpgStore.EnsureZombossPlayer`, zomboss-deploy-ai T3.4). Deriving the empire from "a player id resolved"
would credit Zomboss's own deployed unique to Dave for every kill it makes. Side decides; the row rides
along as `KillCredit.PlayerId`, present only when one exists.

**One mapping, not two.** Side to empire is `SpeciesAllocation.EmpireForSide` — the SSOT T4.1 established.
A test asserts the two agree, because a second copy of "zombies are Zomboss's" is the parallel-path defect
this program removes.

### Two vocabularies, which is why one overload covered neither

The lawn says `"plant"`/`"zombie"`; **battle says `"squad"`/`"wave"`** (`BattleModels.cs:10`). A single
string overload would have silently covered neither, so there are separate entry points, and the
squad/wave reading is `BattleHubCompose`'s. It differs in exactly one deliberate way: `BattleHubCompose`
treats anything-not-`"wave"` as squad because a compose must produce a number, while attribution
**refuses** an unknown token — crediting the wrong empire is worse than failing loudly, which is the whole
shape of D9. A bullet refuses for the same reason.

### Present, not merely derivable

A mechanism nothing calls would be a **dark feature** by this program's own definition. `killerPtr` already
named *which entity* killed; it never named *whose it was*, which is how attribution stayed "absent outside
the lawn" while the payload looked complete. So `BattleReportEmitter` now resolves `creditEmpire` at the
one point every mode's die event passes through — no consumer re-derives it, and none can derive it
differently.

**Verified by closure, never by count** (the audit's own wording). Nothing asserts how many kills or
entities exist; what is asserted is that the mapping is total over the closed vocabularies the code owns
and that nothing falls through. The mode test runs a **real battle per registered mode**, walks the die
events it actually produced, asserts the killer's empire is never the victim's, and fails rather than
passing vacuously if no mode produced a death. Collapsing both battle sides to one empire turns it red.

**What this does not do:** change *who earns*. `RpgStore.Souls`'s lawn path still credits the acting
player row. Attribution is the fact; what an empire does with it is the soul economy's question, and
`species-progression` owns when Zomboss's side starts earning.

## What this deliberately does not decide

**What a species level gives**, and **what drives Zomboss's clock**. Those are `species-progression`'s
open questions. This module fixes the scope and wiring underneath them so that, once answered, the answer
reaches the right actor in the right mode.

## Numeric

Species-derived magnitudes are `long`; widen before multiplying; overflow throws. S7 means levels start
producing a difference — magnitudes will move, and that is the fix landing. Before/after measurement, not
a re-tune.

## Tests to rewrite

Any test asserting that a lawn zombie carries the human player's progression is pinning S1 — restate to
the contract: an actor resolves the species progression of **its own** empire.

Assert the **contract and the closure**: every kill credits exactly one owner; every actor resolves
exactly one empire's species row. Never assert how many species, empires or kills exist.

## Boundaries

- **Always:** list every cache trigger including the key-set edge, with a test each
- **Ask first:** what a species level grants — that is `species-progression`'s question
- **Never:** a species fold outside ActorHub

## Verification

```powershell
.\scripts\verify-change.ps1 -Paths <cache> <compose> gk-fusion/src/FusionRpg.Injector/Match/MatchHost.cs <tests> -Session solid-remediation-<date>
```

- [ ] The species cache key carries the empire dimension
- [ ] A lawn zombie resolves Zomboss's empire, not the player's — asserted
- [ ] Zomboss's empire earns from horde kills
- [ ] Kill attribution present in every mode
- [ ] A level-4 plant type composes differently from a level-1 one
- [ ] The Bound-unique hot path no longer resolves the fallback
- [ ] `guard-actor-hub.py` green; every cache trigger has a test

## Success criteria

Progression credited to whoever earned it, in every mode, and the hot path stops paying for a fallback it
should never reach.
