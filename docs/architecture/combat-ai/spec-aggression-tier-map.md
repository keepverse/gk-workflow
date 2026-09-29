# Spec: `aggression-tier-map` (combat-ai module 6)

**Program:** [combat-ai](../combat-ai-map.md) · **Ideal:** [combat-ai-ideal.md](../combat-ai-ideal.md)
§6.1 "Aggression bound" · **Depends on:** `core-scorer` (module 1) ·
**Unblocks:** any content that writes `ai.aggression` — taunt, stealth, decoy, the 59 passive-tree seed
files that already name the channel, and module 3's `Aggression` personality axis ·
**Status:** built (CAI1.13, 2026-09-20). The two `Stats/Derived/**` comments this spec corrects are outside the CAI1.13 lane's allowed paths — opened as a row in `tasks/derived-stats-todo.md`.

> **Correction, CAI1.13:** the two stale comments named in §3 (`DerivedStatChannels.cs:568-577`,
> `DerivedStatRegistry.cs:289-294`) were NOT corrected in the implementation commit, because
> `gk-core/src/FusionRpg.Core/Stats/**` is outside that lane's allowed-file fence. The function, the signed
> `saturatedBy`, the trace line and every test in §Testing shipped; only the two comment rewrites are
> outstanding, and they are filed with `file:line` and the cause in `tasks/derived-stats-todo.md`.

## Objective

`AiScoring.EffectiveTier` **throws** when an actor's aggression falls outside `±aggressionRange`:

```csharp
// gk-core/src/FusionRpg.Core/Actions/Ai/CandidateScorer.cs:91-118 (as built by CAI1.13; the pre-CAI1.13 body was at `:79-86`, moved from Battle/Siege/SiegeAi.cs by CAI1.1)
public static int EffectiveTier(int baseTier, int aggression, int aggressionRange)
{
    if (aggressionRange <= 0) throw new ArgumentOutOfRangeException(nameof(aggressionRange));
    if (aggression < -aggressionRange || aggression > aggressionRange)
        throw new ArgumentOutOfRangeException(nameof(aggression),
            $"aggression {aggression} outside the authored ±{aggressionRange} range — the range IS the vocabulary.");
    return checked(baseTier - aggression);
}
```

The value it guards is not authored. It is **composed**. `ai.aggression` is registered with
`DerivedComposeKind.FlatSum` and no `Cap`
(`gk-core/src/FusionRpg.Core/Stats/Derived/DerivedStatRegistry.cs:289-294`), read through
`IBattleView.AggressionOf` → `BattleRunState.AggressionOf`, which rounds the composed channel to an `int`
(`gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs:1089-1090`), and handed straight to `EffectiveTier` by the
siege candidate builder (`gk-core/src/FusionRpg.Core/Battle/Siege/SiegeAiIntentSource.cs:501`). `aggressionRange`
is **2** (`gk-core/data/tuning/combat-ai.v1.json` `profiles["siege/default"].scoring.aggressionRange`; the key
moved out of `siege.v1.json` in CAI1.8's H7 migration, and its `> 0` refusal is now
`gk-core/src/FusionRpg.Core/Actions/Ai/CombatAiTuningLoader.cs:167-170`).

So the arithmetic is: **two +1 sources and a +1 status sum to +3 and crash the AI mid-battle.** That is
the audit's M13, and it is not hypothetical — 59 seed files under `gk-data/packs/fusion/data/seed/passive-tree/nodes/` already
name the channel (AUDIT M13), and module 3's `Aggression` personality axis adds a second additive
contributor on top of the channel.

**A `FlatSum` channel has no mechanism to refuse a third contributor.** Nothing in composition can say
"this is the second +1, reject it" — `DerivedComposer` folds every modifier for a channel and hands back a
number (`gk-core/src/FusionRpg.Core/Stats/Derived/DerivedComposer.cs:60-80` is the fold loop;
`ComposeChannel`/`Cap` at `:83-100` is the clamp itself). The throw is therefore unreachable
by a content author at authoring time and reachable only at runtime, in the worst possible place: mid-fight,
in the decision path, for the player who happened to stack a taunt. This module replaces the throw with
**saturation into the closed tier range**, and makes the saturation **visible** so it is a stated rule
rather than a silent swallow.

The map is explicit that this must land **before** any content writes the channel.

## Tech stack

`FusionRpg.Core` only — one function body in `gk-core/src/FusionRpg.Core/Battle/Siege/SiegeAi.cs`, which module 1
has already moved to `gk-core/src/FusionRpg.Core/Actions/Ai/CandidateScorer.cs`, plus two stale comments corrected
in `Stats/Derived/`. No new dependency, no tuning file of its own, no host change.

## Commands

```powershell
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~SiegeAi|CandidateScorer|Aggression"
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~DerivedStatRegistry|DerivedCompose"
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden|ExpeditionResolver"
dotnet test gk-core/tests/FusionRpg.Guard.Tests
.\scripts\verify-change.ps1 -Paths <changed files> -Session backlog-clean-up-20260920
python gk-core/scripts/audit-overflow.py --targets A3
python scripts/audit-doc-citations.py --scope docs/architecture/combat-ai/spec-aggression-tier-map.md --summary
```

## Project structure

| What | Where |
|---|---|
| `EffectiveTier` — the throw becomes a saturating clamp | `gk-core/src/FusionRpg.Core/Actions/Ai/CandidateScorer.cs:91-118` (module 1's file; the pre-CAI1.13 body moved there from Battle/Siege/SiegeAi.cs by CAI1.1) |
| The saturation report (what was asked for vs what was used) | `gk-core/src/FusionRpg.Core/Actions/Ai/CandidateScorer.cs` — a second, opt-in overload |
| Stale comment: "a status outside that range makes EffectiveTier throw, by design" | `gk-core/src/FusionRpg.Core/Stats/Derived/DerivedStatChannels.cs:568-577` |
| Stale comment: "the −2..+2 bound is enforced by SiegeAi.EffectiveTier throwing out of range" | `gk-core/src/FusionRpg.Core/Stats/Derived/DerivedStatRegistry.cs:289-294` |
| Tests | `gk-core/tests/FusionRpg.Core.Tests/Actions/Ai/AggressionTierMapTests.cs` (new — **landed**, CAI1.13) |
| Existing siege suites — **not edited** | `gk-core/tests/FusionRpg.Core.Tests/Battle/Siege/SiegeAiTests.cs`, `SiegeAiIntentSourceTests.cs`, `SiegeAiLiveWiringTests.cs` |

## The shape

### 1. The function

```csharp
/// Signed aggression applied INSIDE the tier computation — never as a score bonus, which is what makes a
/// taunt absolute within its tier and irrelevant outside it (the shipped rule, SiegeAi.cs:88-95, unchanged).
///
/// STRUCTURAL, and this is the exemption AGENTS.md's no-hard-ceiling rule names explicitly: the ±range is
/// a CLOSED VOCABULARY of 2*range+1 tiers, not a magnitude a balance pass widens and not a ceiling on any
/// actor's progression. `ai.aggression` is a FlatSum channel with NO Cap (DerivedStatRegistry.cs:289-294)
/// and it stays that way — the channel is uncapped and composes freely; only this READER saturates, and
/// only onto its own vocabulary. Saturating here is the difference between "your third taunt adds nothing"
/// (a stated rule) and "your third taunt throws ArgumentOutOfRangeException mid-fight" (the shipped bug).
public static int EffectiveTier(int baseTier, int aggression, int aggressionRange) =>
    EffectiveTier(baseTier, aggression, aggressionRange, out _);

public static int EffectiveTier(int baseTier, int aggression, int aggressionRange, out int saturatedBy)
{
    // Unchanged, and deliberately still a throw: a non-positive range is MALFORMED CONFIGURATION, not a
    // runtime data value. Module 2's loader already refuses it at parse; this is the last line of defence.
    if (aggressionRange <= 0) throw new ArgumentOutOfRangeException(nameof(aggressionRange));

    var used = Math.Clamp(aggression, -aggressionRange, aggressionRange);
    saturatedBy = checked(aggression - used);       // 0 when nothing was lost; signed, so direction shows
    return checked(baseTier - used);
}
```

Three deliberate details:

- **`Math.Clamp`, not a hand-rolled pair of `if`s.** The result is an index into a closed vocabulary, so
  the operation has a name and the name should be in the code.
- **`saturatedBy` is signed**, so `+1` and `−1` are distinguishable. "My stealth is being ignored" and "my
  taunt is being ignored" are different player complaints.
- **`checked` stays on the subtraction.** `baseTier` is structurally 0 for every candidate today
  (`SiegeAiIntentSource.cs:491-496` explains why: signed aggression is the only per-candidate input into
  tier), but the arithmetic keeps its guard because that is the repo's rule for integer magnitude
  arithmetic, and because a future `baseTier` is exactly the kind of change that would make it matter.

### 2. What gets saturated — the sum, not the channel alone

The input to `EffectiveTier` is the **total** aggression an actor carries. Today that is one term, the
composed channel (`BattleRunState.cs:1089-1090`). After module 3 it is two:

```
aggression = round(Derived.Get("ai.aggression"))  +  personality.Offset(PersonalityAxis.Aggression)
```

**The sum is what saturates.** Saturating the channel first and then adding the personality offset would
reintroduce exactly the defect this module removes — a +2 channel plus a +1 personality would leave the
vocabulary again. This is stated in module 3's spec too, so the two cannot be implemented against
different assumptions.

### 3. Why this is not the "throw, never clamp" rule being broken

`CLAUDE.md`'s Caps rule says an absolute bound is **derived from the arithmetic and throws**, never clamps
silently, because *"a clamp turns 'your gear stopped mattering' into a bug with no symptom."* It also
exempts, **and requires a comment for**, structural limits and bounded ratios. This module sits squarely in
the exemption, and the argument has three parts:

1. **The thing being bounded is a vocabulary index, not a magnitude.** The tier range *is* the
   taunt/stealth/decoy vocabulary — the shipped comment says so in those words
   (`Actions/Ai/CombatAiProfile.cs:59`, moved from `SiegeAi.cs` by CAI1.1/CAI1.8;
   `siege.v1.json`'s own `ai._note`). There are `2*range+1` tiers and there is no tier −3 to fall off. This
   is not a cap on how strong an actor may become; no magnitude is clamped and no progression stops.
2. **No magnitude is lost.** `ai.aggression` keeps composing with no `Cap` and the sheet keeps showing the
   real number. What saturates is one reader's projection of that number onto its own closed set.
3. **The symptom is restored, not removed.** The rule's real objection is to a clamp with *no symptom*.
   `saturatedBy` is the symptom: it is surfaced on the decision trace (§4), so "the third taunt does
   nothing" is a visible, explainable fact instead of a mystery. That is a strictly better outcome than a
   mid-fight exception, which is a symptom that *ends the battle* rather than explaining anything.

**The stale claim that says otherwise, and where it lives.** Two comments in `Stats/Derived/` assert the
current throw is correct design:

- `DerivedStatChannels.cs:568-577`: *"A future taunt/stealth status that sets this outside that range makes
  `EffectiveTier` throw, by design, matching this repo's 'throw, never silently clamp' rule generalized
  from magnitude overflow to a closed vocabulary."*
- `DerivedStatRegistry.cs:289-294`: *"the −2..+2 bound is enforced by `SiegeAi.EffectiveTier` throwing out
  of range, not by composition."*

**That generalisation is what this module overturns, and both comments are corrected in the same commit.**
The overflow rule exists because a wrapped integer silently inverts a comparison; there is nothing to wrap
here and nothing silent about a reported saturation. The comments are honest about their own reasoning,
which is why they are quoted rather than quietly deleted — a future reader who finds the clamp should find
the argument that replaced them, not a gap (`CLAUDE.md` workflow step 5: fix the contradicting text in the
same change).

### 4. Saturation is observable

When `saturatedBy != 0`, the fact reaches the decision trace. Today that is
`BattleTrace.AiDecision(round, actorKey, summary)`
(`gk-core/src/FusionRpg.Core/Battle/Timeline/BattleTrace.cs:125`), which siege already writes on every rescore
(`SiegeAiIntentSource.cs:333-373`, reordered by CAI1.13 so the line can name the CHOSEN candidate) and which is kept out of `Digest`, so it is **golden-neutral by
construction** (`SiegeAi.cs:25-30`). Module 10 (`decision-inspector`) widens that surface; this module only
guarantees the fact is *available* and that the trace line names it when it is non-zero.

Cost when the trace is off: `_trace` is null and nothing is formatted (`SiegeAiIntentSource.cs:337`). The
`out int` costs nothing — no allocation, no boxing.

**Never a log line, never an exception, never a debug endpoint that fabricates it.** The saturation is read
off a real decision or it is not reported (`AGENTS.md`'s debug-scope rule).

### 5. Where the saturation happens — at the read, and nowhere else

Not in composition. `DerivedComposer`'s `Cap` clamps only the top end — `DerivedStatRegistry.cs:294-298`
says exactly that, and calls it *"the wrong shape for a symmetric range"*, which is correct and is why the
channel has no `Cap` today. Clamping at compose would also hide the real channel value from the actor
sheet and from every other future reader, which is the opposite of what a derived channel is for.

So: **the channel is uncapped, and its one reader saturates.** One reader, one place, one rule. If a second
reader of `ai.aggression` ever appears, it calls `EffectiveTier` rather than re-deriving the clamp — the
same discipline that keeps one damage resolver.

## Tunables

**None of its own.** `aggressionRange` is module 2's, migrated from `siege.v1.json` into
`gk-core/data/tuning/combat-ai.v1.json` under `profiles["*/default"].scoring.aggressionRange`, seed **2**,
published `v{n+1}` through `gk-core/tools/tuning/publish.py`.

| Number | Value | Kind | Label required in code |
|---|---|---|---|
| `aggressionRange` | 2 | **structural** | *"the ±range IS the taunt/stealth/decoy vocabulary; 2\*range+1 tiers, not a magnitude a balance pass widens"* — the wording already used at `Actions/Ai/CombatAiProfile.cs:59` (moved from SiegeAi.cs by CAI1.1/CAI1.8) |

Widening the range is a **vocabulary change**, not a balance pass: it adds tiers, so it changes what a
taunt means and what every profile's weights are calibrated against. It goes through review, not through
`publish.py` alone.

No literals in the changed code beyond `0` (the saturation-free sentinel).

## Code style

- **`Math.Clamp`** for a bounded ratio / vocabulary index; `checked` for the integer subtraction.
- **The comment carries the exemption.** `AGENTS.md` requires a structural limit to say it is structural
  and why; this one also has to say why it is not the throw-never-clamp rule, because the code it replaces
  argued the opposite.
- **The malformed-configuration throw stays a throw.** Distinguish, in the comment, a bad *configuration*
  (`aggressionRange <= 0` — a developer error, fail loud) from a legal *runtime value* (a stacked channel
  — a content outcome, saturate and report).
- **The `out` parameter, not a returned tuple** — the hot path allocates nothing, matching the discipline
  `UsabilityEvaluator` and `RetargetLedger.TryGetHeld` already follow
  (`gk-core/src/FusionRpg.Core/Actions/UsabilityEvaluator.cs:36-84`, `gk-core/src/FusionRpg.Core/Actions/Ai/RetargetLedger.cs:26-36` (moved from `SiegeAiIntentSource.cs` by CAI1.4)).

## Testing strategy

Contract and closed vocabulary only.

**`AggressionTierMapTests`**
- ✅ `Inside_the_range_is_unchanged` — for every value in `−range..+range`, the result equals the shipped
  `baseTier - aggression` and `saturatedBy` is 0. **This is the byte-identity proof**: every value any real
  implementor produces today is 0 (`BattleRunState.cs:1089-1090` and its own comment), so the whole live
  domain is inside this test.
- ✅ `Outside_the_range_saturates_to_the_edge` — `+3` and `+7` both give the same tier as `+2`; `−3` and
  `−7` the same as `−2`. No throw.
- ✅ `SaturatedBy_reports_the_signed_overshoot` — `+3` reports `+1`, `−4` reports `−2`, `+2` reports `0`.
- ✅ `A_stacked_channel_plus_a_personality_offset_saturates_as_a_sum` — `+2` channel and `+1` personality
  give the same tier as `+2` alone. This is the module-3 interaction, asserted here so the two modules
  cannot drift.
- ✅ `Non_positive_range_still_throws` — `0` and `−1` throw, because a malformed range is a developer
  error, not a content outcome.
- ✅ `Tier_vocabulary_width_is_two_range_plus_one` — with `range = 2`, exactly 5 distinct effective tiers
  are reachable from a fixed `baseTier`. **A pinned literal with its reason stated in the test:** the tier
  set is a closed vocabulary the code owns, and widening it is a reviewed change. (The number of *actors*
  at any tier is a reading, and nothing asserts it.)
- ❌ Never assert how many seed files name `ai.aggression` (a population that content grows), or the text
  of any trace line.

**Existing suites, unedited.** `SiegeAiTests`, `SiegeAiIntentSourceTests` and `SiegeAiLiveWiringTests` must
pass with no change. If one of them asserts the throw, **that assertion is the stale test** — the standard
answer under `CLAUDE.md`'s seed-data rule's corollary ("a failing test is either a stale test or a real
defect") — and replacing it is part of this module, with the replacement asserting the saturation instead.
That is the one edit to an existing siege test this module is permitted to make, and it must be called out
in the commit body.

**Golden impact: byte-identical, provably, today.** Every production implementor of `AggressionOf` returns
0 — `BattleRunState.cs:1089-1090` composes the channel and its own comment records that no taunt/stealth/decoy
content exists anywhere (repo-wide search, 2026-09-07), so `Derived.Get` returns the registered default of
0 (`DerivedStatRegistry.cs:292`). Nothing reaches the throw, so nothing changes when the throw goes away.
`BattleGoldenTests` and `ExpeditionResolverTests.Tier_goldens_are_locked` unchanged and unblessed.

**And that is exactly why this must land before content.** The change is free today and expensive the day
after the first `ai.aggression` writer ships: after that, every fight in which two sources stack is a crash,
and the fix would arrive with a moved golden and a bug report instead of with a clean diff.

## Boundaries

**Always**
- Saturate the **sum** of every aggression contributor, at the one reader.
- Report the overshoot through `saturatedBy` so the clamp has a symptom.
- Keep `aggressionRange <= 0` a throw.
- Correct the two `Stats/Derived/` comments in the same commit.

**Ask first**
- Changing `aggressionRange` from 2. It widens a vocabulary and moves what every weight is calibrated
  against.

**Never**
- Add a `Cap` to `ai.aggression` in the registry. `Cap` clamps one end only
  (`DerivedStatRegistry.cs:294-298`), which is the wrong shape for a symmetric range, and clamping at
  compose would hide the real value from every other reader and from the sheet.
- Clamp silently. Without `saturatedBy` reaching a read surface this becomes precisely the symptomless
  clamp `CLAUDE.md` forbids.
- Re-derive the clamp at a second call site. One reader, one rule.
- Turn the saturation into a thrown exception "just for debug builds" — a decision path that behaves
  differently by build configuration is not deterministic.
- Fabricate a saturation report from a debug endpoint. It is read off a real decision or it is not
  reported.

## battle-engine-ssot §5 — the six answers

1. **Which responsibility (§3), or a new one?** **None, and not a new one.** This is one line of the
   deciding side's arithmetic. It does touch a registered derived channel, but only as a **reader** —
   `ai.aggression` is already on the register as part of responsibility 11 ("all battle derived stats and
   their mechanisms"), registered at `DerivedStatRegistry.cs:292`, and this module adds no channel and
   changes no compose rule.
2. **Does it DECIDE or RESOLVE?** **Decide.** `EffectiveTier` orders candidate targets inside
   `AiScoring.ChooseTarget`; it never reaches a resolution step. Nothing about hit, mitigation, status or
   death changes.
3. **Mechanism or loop?** **A mechanism** — one mapping from a summed channel onto one closed vocabulary,
   shared by every place that scores a target. No mode gets its own rule.
4. **Which existing implementation does it extend?** `AiScoring.EffectiveTier` itself
   (`Actions/Ai/CandidateScorer.cs:91-118`, moved from SiegeAi.cs by module 1) and the shipped composition of
   `ai.aggression` (`DerivedStatRegistry.cs:289-294`, `BattleRunState.cs:1089-1090`). It replaces a refusal
   inside one function; it copies nothing and forks nothing.
5. **Does every mode get it?** **Yes** — it is inside the one scorer, so siege has it now and battle,
   delve and the lawn get it as they adopt the scorer. Critically, it means a taunt or stealth status
   authored for any mode behaves the same in all of them, which is the property S3 already names as free
   ("taunt/stealth content authored for ANY mode automatically works for siege's AI for free").
6. **Is it deterministic and seeded?** **Yes.** Pure integer arithmetic, no RNG, no clock, no ambient
   state. It is strictly *more* deterministic than what it replaces: an exception thrown from inside a
   decision is a non-deterministic outcome from the caller's point of view, because whether it fires
   depends on how much content happened to stack.

## Success criteria

1. `EffectiveTier` no longer throws for any legal `aggression` value; it saturates to `±aggressionRange`.
2. `aggressionRange <= 0` still throws, and the comment says why the two cases differ.
3. The saturation is reported through a signed `saturatedBy` and reaches `BattleTrace.AiDecision` when
   non-zero, at zero cost when the trace is off.
4. The sum of channel + personality offset is what saturates, not the channel alone.
5. `DerivedStatChannels.cs:568-577` and `DerivedStatRegistry.cs:289-294` no longer claim the throw is the
   bound, and each states the saturation rule instead — in the same commit.
6. `ai.aggression` stays `FlatSum` with no `Cap`.
7. `AggressionTierMapTests` covers inside-range identity, saturation both ways, the signed report, the
   sum case, the malformed-range throw, and the `2*range+1` vocabulary width.
8. Every golden hash unmoved; no siege test edited except one that asserts the removed throw, called out
   in the commit body.
9. The change lands **before** any content writes `ai.aggression`.

## Open questions

None.

The one question that looked open — *should the channel be capped at compose instead?* — is closed by the
code: `DerivedComposer`'s `Cap` clamps only the top end and `DerivedStatRegistry.cs:294-298` already
records that as the wrong shape for a symmetric range. Capping at compose would additionally hide the real
composed value from the actor sheet and from every future reader, so the reader-side saturation is not a
compromise, it is the correct place.

*(Cross-module note, not this module's to specify.)* `FoggedBattleView` fog-gates `AggressionOf` — a
target's aggression is board information, not self-knowledge (S3, "Per-mode constraints"). The lawn adapter
declares no fog (ideal §6.2), so a lawn stealth status would have no effect there. That is module 15's
(`lawn-actor-view`) statement to make; it is noted here because this module is where a reader would expect
to find the aggression story complete.

## Design gate checklist

```
[x] I identified the subsystem(s) this touches: battle AI, and DESIGN-GATE §1 "Stats" (it reads a
    registered derived channel) and "Any numeric magnitude".
[x] Session boundary: backlog-clean-up-20260920 (tasks/sessions/backlog-clean-up-20260920.json). This
    lane writes four spec files and edits no source.
[x] I read every doc in the §1 row(s) this session: battle-engine-ssot.md §2/§3c/§5, combat-ai-map.md
    (row 6), combat-ai-ideal.md rev 3 §6.1 "Aggression bound", AUDIT.md M13, S3 (the aggression row),
    CLAUDE.md's Caps and numeric-types sections in full, AGENTS.md Hard boundaries.
[x] I checked decisions.md for a lock: nothing locks the aggression bound. The nearest lock, the
    "Action selection (battle adoption)" row, governs trait wrappers and the RulesetVersion trigger,
    neither of which this module touches.
[x] Every factual claim cites file:line, and every file cited was opened this session: SiegeAi.cs,
    SiegeAiIntentSource.cs, BattleRunState.cs, DerivedStatChannels.cs, DerivedStatRegistry.cs,
    DerivedComposer.cs, BattleTrace.cs (the AiDecision line), SiegeTuning.cs, siege.v1.json,
    UsabilityEvaluator.cs.
[x] python scripts/audit-doc-citations.py --scope docs/architecture/combat-ai/spec-aggression-tier-map.md
    reports no HIGH finding.
[x] I verified claims against CODE, not comments — and this module is the case where the comment and the
    code disagree with the DESIGN. Both comments are quoted verbatim, named as the text being overturned,
    and scheduled for correction in the same commit rather than left to rot.
[~] I tested (not assumed) any constraint I am reporting. PARTIAL, and the gap is named: "byte-identical
    today" is an argument from three read facts (the channel's registered default is 0 at
    DerivedStatRegistry.cs:292; the only production reader composes it at BattleRunState.cs:1089-1090; its
    own comment records a repo-wide search finding no content writer). I did NOT run the suite - this is
    a spec lane with a no-build, no-test boundary (SPEC-BRIEF). I also did NOT open the three siege test
    files to check whether one asserts the throw; the spec therefore PERMITS exactly one such edit and
    requires it to be called out, rather than claiming none is needed.
[x] Nothing contradicts a §2 invariant. The one rule this module argues WITH rather than against -
    "an absolute bound throws, never clamps silently" - is addressed head-on in §3 against its own
    stated exemption for structural limits and bounded ratios, and the clamp is given a symptom.
[x] Corrections are propagated: the two Stats/Derived comments are named with their line ranges and
    required in the same commit; the module-3 sum interaction is stated in both specs; the fog/lawn
    consequence is handed to module 15 by name.
[x] No assertion pins a derived-population count or generated text. The one pinned literal is the tier
    vocabulary width 2*range+1, a closed vocabulary the code owns, with the reason in the test. The
    count of seed files naming the channel is explicitly refused as an assertion.
[ ] Event-refreshed cache (§2.16): not applicable - no cache is introduced or touched.
[x] No acceptance criterion fixes an ordering that can vary in real play.
[x] Actor combat/derived magnitude: this module CONSUMES one Hub channel (ai.aggression via
    IBattleView.AggressionOf -> Derived.Get) and produces none. It registers no subsystem, adds no
    channel, and explicitly refuses to change the channel's compose rule (no Cap). guard-actor-hub.py
    has nothing to catch.
[x] Does not invent or extend a SOLID-violating parallel path. It removes a refusal from the one
    reader; it adds no second clamp site and states "one reader, one rule" as a Boundary.
[~] A new rule has a registry row. PARTIAL: the rule "a summed channel read as a closed vocabulary
    saturates at its reader and reports the overshoot" is new and has no guard. I am not proposing one
    - a single call site is covered by AggressionTierMapTests, and a source-scan guard over one
    function would be enforcement theatre. If a SECOND channel ever gets this treatment, the pair
    justifies a registry row, and that is the trigger to record. Stated rather than silently skipped.
```
