# Spec: `decision-inspector` (combat-ai module 10)

**Program:** [combat-ai](../combat-ai-map.md) · **Ideal:** [combat-ai-ideal.md](../combat-ai-ideal.md)
§6.2a "Visibility (D4)" · **Depends on:** `core-scorer` (1), `ai-tiers-personality` (3),
`intent-router` (4) · **Unblocks:** nothing (it is an instrument; `auto-policy-switch` (14) uses it but
does not require it) · **Status:** **both halves built** (CAI2.4/CAI2.5): the record + sink seam (`AiDecisionRecord`, `BattleTraceDecisionSink`), the Core ring, and (2026-09-23, lane `cai2`) the lawn ring's injector half — the switch, the sink adapter and the additive registry drops. The ring's decision FEED is still `CAI4.8`'s. See `:70` for the full status.

## Objective

One decision explanation exists today and it is siege-only. `SiegeAiIntentSource` records the top three
scored candidates with their full per-term breakdown into `BattleTrace.AiDecision` every time it
actually rescores (`SiegeAiIntentSource.cs:340-373` (re-anchored by CAI1.13/CAI1.14)), formatted by `AiScoring.FormatTopThree`
(`Actions/Ai/CandidateScorer.cs:399-417` as built by CAI1.14; was `:271-275`, moved from SiegeAi.cs lines 179-189 by CAI1.1), and `BattleTrace`
keeps those lines out of `Digest` deliberately so *"an
observability addition must not become indistinguishable from a behavior change in the fixture the
parity ladder compares"* (`BattleTrace.cs:121-129`). That design is right and it is already proven
(`BattleTraceTests.cs:99-108` asserts the digest exclusion; `SiegeAiIntentSourceTests.cs:456-461`
asserts the line's shape; `:464-470` asserts that supplying no trace records nothing and does not throw).

What is missing is everything else. Four of the five `IIntentSource` policies explain nothing, the
record is a pre-formatted string with no room for the things D4 names, and nothing on the lawn can
record a decision at all — the injector has zero hits for `IIntentSource | ActionIntent |
FrozenActionSet | IBattleView` (`AUDIT.md` §1 "Verified correct"). Owner ruling **D4**: *"See the full
mechanism, hidden by default"* — per actor, the tier and profile, the personality offsets, the trigger
state (swing count, timer, lock, tokens), every candidate with its gate verdicts and score breakdown,
and the chosen intent plus the top-3 (ideal §6.2a).

This module widens that one siege line into a structured record over the shared core, gives it a sink
seam so each place can carry it its own way, ships the lawn sink as a bounded ring in the injector, and
keeps four properties non-negotiable: **hidden by default, golden-neutral, zero cost when off, and it
reads real decisions — it never fabricates one.**

## Tech stack

`FusionRpg.Core` (`Actions/Ai/`, `Battle/Timeline/BattleTrace.cs`), `FusionRpg.Injector`
(`Effects/`, the lawn ring + the switch). No new dependency, no new tuning file. Closed vocabularies are
**referenced, never redefined**: `UsabilityReason` (`UsabilityResult.cs:9-29`) is the gate-verdict
vocabulary, `AiScoreBreakdown` (now `ScoreBreakdown`, `Actions/Ai/CandidateScorer.cs:22-25`, moved from SiegeAi.cs by CAI1.1) is the per-term vocabulary, `AiTier` is module 3's.

## Commands

```powershell
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleTrace|AiDecision|SiegeAi"
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden|PreAdoptionTrace"  # must be UNCHANGED
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~DecisionInspector"
python gk-core/scripts/guard-secondary-no-unity.py
python gk-core/scripts/guard-debug-scope.py
.\scripts\verify-change.ps1 -Paths <changed files> -Session backlog-clean-up-20260920
```

Injector tests (`FusionRpg.Injector.Tests`) need interop refs and are not in CI (`AGENTS.md`); the ring
buffer's own logic therefore lives in **Core** and is tested there, with the injector holding only the
adapter. That is the same split the program's rule 4 already requires (*"Logic lives in Core, because
CI never builds the injector"*, map §Load-bearing rules).

## Project structure

| What | Where |
|---|---|
| The record + the sink seam | `gk-core/src/FusionRpg.Core/Actions/Ai/AiDecisionRecord.cs` (new; **built by CAI2.4** — records, `AiTriggerState`, the three-member `AiDecisionOrigin` vocabulary and `IAiDecisionSink`) |
| The `BattleTrace` sink (turn modes) | `gk-core/src/FusionRpg.Core/Actions/Ai/BattleTraceDecisionSink.cs` (new; **built by CAI2.4** — emits the byte-identical line) |
| The bounded ring (Core logic, injector-free) | `gk-core/src/FusionRpg.Core/Actions/Ai/AiDecisionRing.cs` (new; **built by CAI2.5**, with `AiDecisionRingTests` — bounded, `last-per-actor` index surviving eviction, copy-on-read, a reused ptr never rewriting history) |
| The existing trace method, unchanged | `gk-core/src/FusionRpg.Core/Battle/Timeline/BattleTrace.cs:110-129` |
| The formatter the siege line already uses | `gk-core/src/FusionRpg.Core/Actions/Ai/CandidateScorer.cs:309-417` (moved from Battle/Siege/SiegeAi.cs lines 148-189 by CAI1.1 — `ScoreBreakdownOf`, `TopThree`/`TopThreeInto` at `:309`/`:326`/`:349`, `FormatTopThree` at `:399`, re-anchored by CAI1.14) |
| The siege recording site, re-pointed at the sink | `gk-core/src/FusionRpg.Core/Battle/Siege/SiegeAiIntentSource.cs:340-373` (re-anchored by CAI1.13/CAI1.14) |
| Lawn switch (default OFF) | `gk-fusion/src/FusionRpg.Injector/Effects/AiInspectFeature.cs` (new; **built by CAI2.5** — the three-layer switch with `DefaultEnabled = false` and the whole rule as a pure `Resolve`) |
| Lawn sink + death/ptr-reuse cleanup | `gk-fusion/src/FusionRpg.Injector/Effects/LawnAiDecisionObservability.cs` (new; **built by CAI2.5** — the `IAiDecisionSink`, the one ptr→actor-key derivation, the read accessors) + the additive `InjectorEntityRegistry.Remove`/`Clear` drops |
| Tests | `gk-core/tests/FusionRpg.Core.Tests/Actions/Ai/DecisionInspectorTests.cs` (**built by CAI2.4**), `.../AiDecisionRingTests.cs` (**built by CAI2.5**) |

**Status, 2026-09-20 (lane `combat-ai-2`).** Built: the record + sink seam, the `BattleTrace` adapter and
siege recording through it (byte-identical line, golden-neutral, one record per scored decision), and the
Core ring with its own eight tests. **Injector half built 2026-09-23 (lane `cai2`, session
`combat-ai-2b`, `CAI2.5`):** `AiInspectFeature` (the switch, `DefaultEnabled` false, and the whole rule as
a pure `Resolve(envValue, debugOverride, defaultEnabled)` so the two env-var wins are testable at all),
`LawnAiDecisionObservability` (the sink, the ONE ptr→actor-key derivation, the read accessors), and the
additive `InjectorEntityRegistry.Remove`/`Clear` drops — 14 new tests in `gk-fusion/tests/FusionRpg.Injector.Tests`,
all green. The ring therefore HAS a production edge (every death and every match reset reaches it) but the
**decision feed** does not exist yet: nothing calls `Sink.Record` until `CAI4.8`'s lawn decision host, which is itself blocked on `CAI4.3`'s payload decision. The ring's **read route** DID land (2026-09-23, lane `cai2`): `debug.combat.snapshot` carries `aiDecisionCount` and `aiDecisions`, projected to primitives through `CandidateScorer.FormatTopThree`, the ONE formatter (`DebugCombatActions.cs:377,418`) — an existing audit-visible route, so it added none. See `tasks/reports/CAI2.5.md`. **Not built:** `ChosenActionId` at the siege site (its recorded
decision is the target decision; the action is chosen one step later), per-candidate gate verdicts (the
gate loop runs against the chosen target only — `AiCandidateVerdict.Gate`/`.ActionId` are nullable for
exactly that reason), the "all four policies behind the router" line, and the whole injector half —
`AiInspectFeature`, `LawnAiDecisionObservability` and the additive `InjectorEntityRegistry` cleanup.
**Corrected 2026-09-23 (lane `cai3`): the router line LANDED, and so did the injector half.** The four arms
record through one sink — `IntentRouter.Compose` wraps the policy, the fallback and the steered source in
`AiDecisionRecordingSource` (`IntentRouter.cs:68-70`), and the ORDER arm records from `Resolve`'s own order
step, which returns BEFORE any wrapped source runs (that arm had **no producer at all** until then:
`grep -rn "AiDecisionOrigin.Order" src/` returned nothing). The sink is also supplied in PRODUCTION at the
two Core battle sites — `BasicAttack` and `TimelineDispatch` pass a `BattleTraceDecisionSink` when the
trace is active — so the arms are no longer unreachable. The delve site is deliberately excluded: its
`Trace` is a `DecisionTrace`, the delve's own type, not a `BattleTrace`. **The last sentence's shape still
holds, for a different reason:** the ring has no production FEED (nothing calls `Sink.Record` from the
lawn), so `CAI2.5` stays open on `CAI4.8`'s decision feed → `CAI4.3`'s payload ruling.

## The shape

### 1. `BattleTrace` keeps its signature; the structure lives behind a sink

`BattleTrace.AiDecision(int round, string actorKey, string topThreeSummary)` takes a **pre-formatted
string on purpose**: *"this class stays domain-agnostic, the same as every other method here, which
takes only primitives and never a subsystem's own scoring type"* (`BattleTrace.cs:110-119`). Widening
that signature to carry a tier, a personality and a candidate list would break exactly the rule the
method's own comment states, and would create the `Timeline` → decision-layer dependency
`Actions/Ai/CandidateScorer.cs:399-417` (`FormatTopThree`, as built by CAI1.14; was `:271-275`, moved from SiegeAi.cs lines 179-184 by CAI1.1)
was written to avoid.

So the widening goes the other way:

```csharp
// gk-core/src/FusionRpg.Core/Actions/Ai/AiDecisionRecord.cs (new)

/// <summary>One decision, exactly as it was made. Every field is a value the decision ACTUALLY read
/// or produced — never a re-derivation. `Total` inside each breakdown comes from `AiScoring.Score`
/// called directly, the discipline `AiScoring.ScoreBreakdownOf` already keeps (SiegeAi.cs:148-155):
/// "a second accumulation could overflow/round differently than the tested, already-shipped one".</summary>
public readonly record struct AiDecisionRecord(
    long NowTick, int Round, string ActorKey,
    AiTier Tier,                              // module 3
    string ProfileId,                         // module 2 — place x role (D5)
    AiPersonalityOffsets Personality,         // module 3
    AiTriggerState Trigger,                   // lawn only; AiTriggerState.None in turn modes
    IReadOnlyList<AiCandidateVerdict> Candidates,   // capped by maxCandidatesScored, already
    string? ChosenActionId, string? ChosenTargetKey,
    IReadOnlyList<AiScoredCandidate> TopThree);

/// <summary>One candidate's gate outcome. `Reason` is `UsabilityResult`'s own typed vocabulary
/// (UsabilityResult.cs:9-29) — never a second refusal vocabulary, and never a bare bool: the enum
/// already exists precisely because "the FE needs to explain a greyed button" (:5-7).</summary>
public readonly record struct AiCandidateVerdict(
    string TargetKey, string ActionId, UsabilityResult Gate, AiScoreBreakdown? Breakdown);

/// <summary>Real-time trigger state (ideal §6.2a): swings since the last cast, the timer's tick,
/// the post-cast lock's expiry tick, and tokens held. `None` for a turn mode, which has no trigger
/// of its own — the engine pulls (S1-battle-core.md "a pull model").</summary>
public readonly record struct AiTriggerState(int Swings, long TimerTick, long LockUntilTick, int Tokens)
{
    public static readonly AiTriggerState None = default;
}

/// <summary>The one recording seam. A null sink means the inspector is off, and OFF MUST COST
/// NOTHING — every call site is `sink?.`-guarded and every argument is built INSIDE that guard.</summary>
public interface IAiDecisionSink { void Record(in AiDecisionRecord record); }
```

Two sinks ship:

- **`BattleTraceDecisionSink`** (turn modes) wraps a `BattleTrace` and formats the record onto the
  existing `AiDecision` line. `BattleTrace` is untouched.
- **`AiDecisionRing`** (the lawn, Core logic) — §4.

Anything else — a future FE panel, a test spy — implements the same one-method interface. Thin
contribution API over a fat surface (SOLID I), depending on the abstraction rather than on `BattleTrace`
(SOLID D).

### 2. The siege line is the identity property

Siege already emits a line whose exact prefix is asserted:
`Assert.StartsWith("5 wave:0 #1=target-a(", line)` and *"both scored candidates are named, not just the
winner"* (`SiegeAiIntentSourceTests.cs:458-461`). After this module, siege records through the sink, and
`BattleTraceDecisionSink` must emit the **byte-identical** line by calling the same
`AiScoring.FormatTopThree` (`Actions/Ai/CandidateScorer.cs:399-417` as built by CAI1.14, was `:271-275`, moved from SiegeAi.cs lines 179-189
by CAI1.1) on the same top-3.

That existing test passing **unchanged** is this module's identity proof, exactly as
`spec-mode-profile.md` uses "every existing caller is byte-identical" as its own. A module that widened
the record and moved the line at once could not tell which change did it.

### 3. Golden-neutral, and zero cost when off

**Golden-neutral** is inherited, not re-argued: `_aiDecisions` is a separate list and `Digest` is
`string.Join("\n", _lines)` (`BattleTrace.cs:24,139`), so nothing this module writes can reach the
fixture the parity ladder compares. `BattleReport` is untouched, so `BattleGoldenTests.Hash`
(which serialises the report) is untouched. Both are re-asserted, not assumed.

**Zero cost when off** is the harder one, and the existing siege site is the pattern to copy verbatim:

```csharp
if (_trace is not null)
{
    var top3 = AiScoring.TopThree(scoreable, _roundOf(nowTick), _tuning);
    _trace.AiDecision(_roundOf(nowTick), actorKey, AiScoring.FormatTopThree(top3));
}
```
(`SiegeAiIntentSource.cs:340-373` (re-anchored by CAI1.13/CAI1.14); the constructor's own doc: *"ALSO OPTIONAL and defaults to null —
omitting it costs nothing"*, `:78-81`.)

The rules that follow, and they are the module's real engineering content:

1. **No speculative collection.** The core scorer must not accumulate an `AiCandidateVerdict` list on
   the hot path "in case someone is watching". The verdict list is built inside the `sink is not null`
   branch, from the candidate array the decision already holds.
2. **No second evaluation.** Re-running `UsabilityEvaluator` to obtain verdicts for the record would be
   both a cost and a fabrication risk (a gate re-checked one tick later can answer differently —
   `UsabilityResult.cs:5-7` says exactly this: *"`OnCooldown` and `CannotAfford` become true with
   time"*). The scorer therefore keeps the `UsabilityResult` it already computed per candidate in the
   buffer it already owns, and the sink reads that buffer. When off, the buffer is still written —
   it is a stack-local the gate loop already produces — but nothing is copied out of it.
3. **`in` parameter, `readonly record struct` record.** No boxing at the call site.
4. **The acceptance is measured, not argued:** `decision-perf` (module 7) owes *"a zero-allocation-once-warm
   test for every policy"* (map row 7). That test must stay green **with the inspector compiled in and
   off** — a named acceptance of this module, run against module 7's own test, not a new one.

### 4. The lawn: a bounded ring in the injector

`CombatDebugObservability` is the shipped precedent and the shape to follow
(`CombatDebugObservability.cs:5-47`): a `const int Cap` with the comment *"Structural
(tunables-ssot.md T2) — debug ring-buffer size, not balance"* (`:8-9`), a `static readonly object Gate`,
a `Queue` drained with `while (count > Cap) Dequeue()` (`:37-40`), a `_lastOverlay` field held **beside**
the ring (`:12`), and a clone on read so a caller cannot mutate what is stored (`:49-53`).

`AiDecisionRing` copies that shape with three additions the lawn forces:

1. **A last-per-actor map beside the ring.** A flat ring is the wrong instrument here: with up to ten
   smart-tier uniques on the board (ideal §6.2a deploy cap) plus general creatures, one busy actor
   evicts every other actor's last decision, and the first question anyone asks the inspector is *"why
   did **this** creature do that"*. Ring (recent, global, ordered) **plus** `last-per-actor` — the same
   pairing `CombatDebugObservability` already uses for `OverlayRing` + `_lastOverlay`.
2. **Withdraw before ptr reuse.** IL2CPP reuses pointers, and `entity:{ptr}` state must be withdrawn on
   death before reuse (`overlay-control-loops.md` §6 rule 4; DESIGN-GATE §1 match-lifecycle row; ideal
   §3 principle 5 names it for *"any per-actor AI state"*). A dead actor's `last-per-actor` entry is
   dropped on the membership edge, or the inspector will attribute a new actor's decisions to the old
   one — a fabrication by accident, which is the failure mode this module is most exposed to. Entries
   already in the **ring** keep their original ptr and tick and are never rewritten — a historical record
   is not falsified by a later reuse; only the live *index* is cleared.

   **Which edge, measured (CAI2.5, 2026-09-23).** This paragraph first named
   `MatchHost.Runtime.MembershipChanged` as the consumer to copy. Read against the code, that event's
   `Cleared` transition is raised by `UniqueBindings.ClearInstance` — a **unique-binding** lifecycle
   edge — so it never fires for the general creatures the inspector exists to explain. The edge actually
   built is `InjectorEntityRegistry.Remove` / `.Clear`: `Remove` is the lawn's real per-actor death edge
   for BOTH sides (`GameHooks`' plant-death postfix; `NoteZombieDead`, which re-removes on every
   death-animation frame because a resync can re-`Add` a dying zombie) and `Clear` is the match-end edge.
   `InjectorEntityRegistry.Add` is deliberately **not** an edge: `Resync` clears the registry and
   re-`Add`s every live actor every `ResyncFrames`, so treating it as one would wipe a long-lived actor's
   last decision roughly every four seconds.
3. **The recorded tick is the engine clock's**, never `DateTime.Now`. D15 (`battle-engine-ssot.md` §4)
   is explicit that the lawn's DoT and status ticks are the engine clock module's, and the ideal
   (§4.1, §6.1) requires the lawn trigger and cooldowns to read the same clock status expiry reads.
   Insertion order gives the ring its ordering; the tick gives each entry its meaning.

**Enumerating the full trigger set for the per-actor index** (DESIGN-GATE §2.16 — the invariant exists
because a trigger set was copied from a cache whose key set never moves):

| Trigger | Effect on the index | Test |
|---|---|---|
| A decision is recorded for `ptr` | upsert `last[ptr]` | ✅ |
| `ptr` dies (membership edge) | **remove** `last[ptr]` — the key-set edge, the one that gets forgotten | ✅ |
| `ptr` spawns (membership edge, possibly a reused ptr) | **remove** any stale `last[ptr]` before the first new decision | ✅ order-independent with the death edge: both orders reachable, both tested |
| Match ends / run state cleared | clear ring and index | ✅ |
| The switch is turned off mid-match | stop recording; existing entries stay readable until cleared | ✅ |

The key set of `last-per-actor` moves on **spawn and death**, not only on "a decision happened" — that
is precisely the class of miss the invariant logs three shipped instances of.

### 5. Hidden by default, and the switch

D4 is *"hidden by default"*. `LawnBasicAttackFeature` is the shipped three-layer switch and its comment
explains why the shape matters — a default must not be borrowed from `CheatState`, whose *"contract does
not promise one"* (`LawnBasicAttackFeature.cs:35-45`):

```csharp
public static class AiInspectFeature
{
    public const string CheatToggleId = "AI-INSPECT";
    public const string EnvVar = "FUSIONRPG_AI_INSPECT";

    /// <summary>This module's OWN default. FALSE — D4: the inspector is hidden by default. Unlike
    /// LawnBasicAttackFeature (DefaultEnabled = true), the safe state here is off: it is an
    /// instrument, not a feature, and off is also the zero-cost state.</summary>
    public const bool DefaultEnabled = false;

    static readonly string? EnvValue = Environment.GetEnvironmentVariable(EnvVar);
    static readonly bool EnvForcedOff = string.Equals(EnvValue, "0", StringComparison.Ordinal);
    static readonly bool EnvForcedOn  = string.Equals(EnvValue, "1", StringComparison.Ordinal);
    static bool? DebugOverride => CheatState.IsUserSet(CheatToggleId) ? CheatState.On(CheatToggleId) : null;

    public static bool Enabled => !EnvForcedOff && (EnvForcedOn || (DebugOverride ?? DefaultEnabled));
}
```

Read once at process start for the env half, exactly as `LawnBasicAttackFeature.cs:58-61` does — *"this
gate sits on the spawn/die path"* is the same reasoning here (the decision path).

In turn modes there is no switch at all: the sink is a constructor argument that defaults to null, the
same opt-in `BattleTrace` itself already is (*"takes null in production and every record site is a
null-conditional call, so tracing cannot change an outcome"*, `BattleTrace.cs:6-9`).

**Updated 2026-09-23 (lane `cai3`): the sink is no longer only a constructor argument nobody passes.**
Measured then, `grep -rn "sink:" src/` returned nothing — no production `IntentRouter.Compose` supplied
one — so the four arms recorded nothing in any shipped battle. `BasicAttack` and `TimelineDispatch` now
pass a `BattleTraceDecisionSink` gated on the trace being ACTIVE, which keeps the no-trace path
allocation-free (`Compose` allocates one wrapper per arm, and criterion 5 is about the sink-NULL path). A
traced battle therefore carries MORE `AiDecision` lines — one per arm consulted — which is the observable
cost of the wire, named rather than hidden.

### 6. It reads real decisions and never fabricates one — the debug-scope rule

`docs/contributing/live-probe-standard.md` and DESIGN-GATE §1's live-probe row split debug surfaces in
two, and this module must say which it is and behave accordingly.

**The lawn read surface is Game Injector Debug scope.** It reads in-process injector state and proves
only what the injector decided. It is therefore labelled with the `// Game Injector Debug` scope banner
that `guard-debug-scope.py` checks (the guard classifies any route with a relay call to the Injector
as injector-shaped, and *"checks that each route's nearest preceding banner agrees with its computed
classification"* — `guard-debug-scope.py` header). Four rules follow, and they are the reason the
2026-09-13 incident is in the failure log:

1. **A read never triggers a decision.** There is no "decide now and tell me" entry point. Reading an
   empty ring returns empty.
2. **A read never synthesises an entry.** An actor key with no recorded decision returns *nothing* —
   never a freshly computed "what it would do", which is exactly the fabricated-precondition half of
   the T14 incident.
3. **Every field is the value the decision used.** `Total` comes from `AiScoring.Score` directly
   (`Actions/Ai/CandidateScorer.cs:242-251`, moved from SiegeAi.cs lines 148-155 by CAI1.1), the gate
   verdict is the `UsabilityResult` the gate loop returned, the
   profile id and tier are the ones the policy was constructed with, the personality offsets are the
   ones applied. No field is recomputed at read time.
4. **An inspector record is never evidence that a feature works.** It proves the AI *decided*
   something; whether the cast resolved is the lawn activation path's own proof, read back through the
   normal path. Stated here so a later live probe does not read this ring and call it end-to-end.

## Tunables

**None.** The inspector adds no balance number and publishes no `v{n+1}`.

| Constant | Where | Class |
|---|---|---|
| Ring `Cap` | `AiDecisionRing` | **Structural** — a debug ring-buffer size (`tunables-ssot.md` T2), carrying the same comment `CombatDebugObservability.cs:8-9` carries verbatim. Not a progression ceiling: it bounds a debug buffer, not a magnitude. |
| `TopThree`'s `3` | `Actions/Ai/CandidateScorer.cs:349-362` (`TopThreeInto`'s own 3-slot bound, as built by CAI1.14; was `:262`, moved from SiegeAi.cs line 172 by CAI1.1) | **Structural** — the record's own shape, already shipped and already named in D4 ("the chosen intent and the top-3"). Not re-declared. |
| Per-actor index size | `AiDecisionRing` | **Structural**, bounded by the live actor count, which the deploy cap already bounds. Cleared on the membership edges in §4. |

`maxCandidatesScored`, which bounds the candidate list this record carries, is **module 2's** migrated
siege key (ideal §8) and is structural there — this module reads the already-capped list and never
caps again.

## Code style

- The sink is `in`-taken and the record is a `readonly record struct` — no boxing, matching
  `AiCandidate` / `AiScoreBreakdown` / `UsabilityResult`, all of which are already `readonly record
  struct` (`Actions/Ai/CandidateScorer.cs:17,24`, moved from SiegeAi.cs lines 70,78 by CAI1.1;
  `UsabilityResult.cs:36`).
- A breakdown's `Total` is obtained by calling `Score`, never by re-summing terms — the comment at
  `Actions/Ai/CandidateScorer.cs:242-251` (moved from SiegeAi.cs lines 148-155 by CAI1.1) is the rule, and
  it now applies to the whole record.
- Every recording site is `sink?.`-guarded, and every argument is constructed inside the guard.
- Ring code: a `static readonly object Gate`, a clone on read, a `const` cap with its structural
  comment — `CombatDebugObservability.cs:8-53`'s shape, not a new one.
- Injector adapters stay Unity-free where they can (`guard-secondary-no-unity.py`); the ring's logic is
  Core so CI actually builds and tests it.
- A field that is only meaningful in one place says so in its own doc comment (`AiTriggerState.None`
  for turn modes), rather than being explained in a separate document.

## Testing strategy

Contract and closed vocabulary only (`validation-ssot.md`).

**Identity**
- ✅ `SiegeAiIntentSourceTests` (`:456-461`, `:464-470`) pass **with no edit**: the same line, and no
  trace still records nothing and does not throw.
- ✅ `BattleTraceTests` (`:81-108`) pass with no edit, including the digest-exclusion test.

**Golden-neutral**
- ✅ A battle resolved with a sink attached and the same battle resolved without one produce an
  identical `BattleReport` and an identical `BattleTrace.Digest`.
- ✅ `BattleGoldenTests` and the pre-adoption trace fixtures are unchanged. If a golden moves, this
  module is wrong — the acceptance, not a re-bless.

**Zero cost when off**
- ✅ `decision-perf`'s (module 7) zero-allocation-once-warm test stays green with the inspector compiled
  in and the sink null. Named as this module's acceptance against that test.
- ✅ A spy sink counts exactly one `Record` per decision that actually scored, and **zero** on a held-
  target tick — the property siege already has (*"never on a 17.8 held-target tick, since nothing was
  scored"*, `SiegeAiIntentSource.cs:82-83`).

**Content (contract, never values)**
- ✅ Every candidate the decision scored appears in `Candidates`, with the gate verdict the gate loop
  returned; a candidate refused at gate *n* carries that gate's `UsabilityReason`, proving the
  short-circuit order the evaluator documents (`UsabilityEvaluator.cs:7-8`).
- ✅ `ChosenActionId`/`ChosenTargetKey` equal the `ActionIntent` actually returned.
- ✅ `TopThree`'s `Total` equals `AiScoring.Score` for the same candidate and weights — the
  no-second-accumulation property.
- ✅ `Tier`, `ProfileId` and `Personality` equal what the policy was constructed with.
- ❌ Never assert how many candidates, actions or profiles exist, or any weight/score value. Those are
  readings. The **closed vocabularies** — `UsabilityReason`'s members, `AiTier`'s members — are pinned
  by their owning modules (2 and 3), not here.

**Ring — `AiDecisionRingTests` (Core)**
- ✅ Cap holds: `Cap + 3` records leave `Cap` entries, oldest evicted.
- ✅ `last-per-actor` survives eviction from the ring — the reason the pairing exists.
- ✅ Death removes the actor's index entry; a reused ptr that spawns finds no stale entry.
- ✅ **Order-independent**: death-then-spawn and spawn-then-death both leave no stale entry, and both
  are tested (DESIGN-GATE §5 — a criterion that encodes one ordering tests only that ordering).
- ✅ Ring entries already recorded are **not** rewritten by a later reuse of the same ptr.
- ✅ A read returns a copy: mutating it does not change stored state.
- ✅ Reading an unknown actor returns nothing — never a synthesised record.

**Switch**
- ✅ Default off: with no env var and no user toggle, `Enabled` is false.
- ✅ `FUSIONRPG_AI_INSPECT=0` wins over an explicit toggle; `=1` turns it on.
- ✅ A never-toggled `CheatState` does not supply a default (the `IsUserSet` gate), the exact defect
  `LawnBasicAttackFeature.cs:35-45` records.

## Boundaries

**Always**
- Keep `BattleTrace`'s signature and its domain-agnosticism.
- Emit siege's existing line byte-identically.
- Build every record field inside the `sink is not null` guard.
- Record the value the decision used; never recompute at read time.
- Clear the per-actor index on **both** membership edges, before a ptr can be reused.
- Label the lawn read surface with its debug scope banner, and keep `guard-debug-scope.py` green.
- Keep the ring's logic in Core (CI never builds the injector).

**Ask first**
- Any player-facing surface for this. D4 is *"an inspection and debug surface; no player editing"* and
  the ideal's §9 keeps player-editable AI out of scope. A UI is a product decision, not a follow-on.
- Persisting decisions (to SQLite, to the match log, to a file). The ring is in-memory by design; a
  durable decision log is a different feature with different cost and different privacy.
- Adding the record to `BattleReport` or to `Digest`. Either moves goldens.

**Never**
- Fabricate a decision, synthesise one on read, or trigger one from a read path.
- Present an inspector record as proof that a cast resolved (live-probe standard).
- Invent a second refusal vocabulary beside `UsabilityReason`, or a second breakdown beside
  `AiScoreBreakdown`.
- Re-run `UsabilityEvaluator` to populate the record.
- Let the ring grow unbounded, or key it by anything whose reuse is not handled.
- Read a wall clock for a recorded tick.

## battle-engine-ssot §5 — the six answers

1. **Which responsibility (§3)?** **None, and deliberately so.** It is observability over the deciding
   side, which §3c places outside the engine entirely. §3c's own list of adjacent-but-not-engine
   systems begins with presentation for the same reason. The closed register is untouched — this
   module adds nothing to it and needs nothing from it.
2. **Decide or resolve?** **Neither. It reads.** It never returns an `ActionIntent`, never enters
   `TryDeclare`'s return path, and has no way to change a decision. That is enforced structurally: the
   sink returns `void`.
3. **Mechanism or loop?** The **record and the sink seam are one mechanism**, shared by every place.
   The *sinks* are the per-place part — `BattleTrace` in turn modes, a bounded ring on the lawn —
   because a turn-ordered fixture and a real-time frame stream genuinely cannot share a carrier. That
   is the §2 loop/mechanism split applied exactly: one vocabulary, per-mode carriers.
4. **Which implementation does it extend?** `BattleTrace.AiDecision` (`BattleTrace.cs:110-129`),
   `AiScoring.ScoreBreakdownOf`/`TopThree`/`FormatTopThree` (`Actions/Ai/CandidateScorer.cs:309-417` (re-anchored by CAI1.14),
   moved from SiegeAi.cs lines 148-189 by CAI1.1), and
   `UsabilityResult` (`UsabilityResult.cs:9-46`). By calling, never by copying. `CombatDebugObservability`
   is the shape the lawn ring follows.
5. **Does every mode get it?** Yes — battle, delve, siege and the lawn, which is the whole point of
   widening it from siege-only. Siege is unchanged in output; the other three gain it. No mode is
   excused, and no mode is given a private explanation format.
6. **Deterministic and seeded?** It reads no clock and no RNG, so it cannot perturb determinism. The
   recorded tick is the decision's own `nowTick` (the engine clock on the lawn, D15). Because the
   record is out of `Digest` and out of the report, attaching or detaching a sink cannot change a
   replay — asserted, not assumed.

## Success criteria

1. `IAiDecisionSink` + `AiDecisionRecord` exist in Core and carry every field D4 names: tier, profile,
   personality, trigger state, per-candidate gate verdicts and score breakdown, chosen, top-3.
2. Siege records through the sink and its existing tests pass **unchanged**.
3. All four policies behind the router record through the same sink. **MET (2026-09-23, lane `cai3`):**
   the three source arms by `AiDecisionRecordingSource` at `IntentRouter.Compose`, the ORDER arm from
   `Resolve`'s own order step, and the sink supplied in production at the two Core battle sites when a
   trace is active — proven through a real battle by
   `DecisionInspectorTests.A_real_battle_reaches_the_routers_sink`, with a planted violation killing it.
4. `BattleTrace.Digest`, `BattleReport` and every golden are unchanged, asserted.
5. With no sink, module 7's zero-allocation-once-warm test is still green.
6. The lawn ring is bounded, has a last-per-actor index, and is provably stale-free across death and
   spawn in both orders.
7. `AiInspectFeature.Enabled` is false with no env var and no explicit toggle.
8. A read of an unknown actor returns nothing; nothing in the module can trigger a decision.
9. `guard-debug-scope.py` and `guard-secondary-no-unity.py` green.

## Open questions

1. **Whether the lawn ring should be readable from the RPG server or only from the injector debug
   surface.** Options: (a) injector-only (`debug.*` relay, Game Injector Debug scope, banner-labelled);
   (b) also surfaced on a server route, which `guard-debug-scope.py` would classify as
   injector-shaped anyway because it must relay. **Recommended default: (a)**, matching
   `debug.combat.snapshot`'s existing shape (`CheatCommandRunner.cs:525`, relayed by
   `DebugEndpoints.cs:1202`). (b) adds a route with no new capability.
2. **Whether the turn-mode sink should also carry the structured record somewhere beyond the formatted
   `BattleTrace` line.** A formatted line is enough to read; it is not enough to query. Options:
   (a) line only (today's shape, and what keeps `BattleTrace` domain-agnostic); (b) the
   `BattleTraceDecisionSink` also keeps the last N structured records in memory for a test or a future
   panel. **Recommended default: (a)** — (b) is the same ring twice, and the ring already exists for
   the place that needs it. Revisit if a turn-mode consumer appears.
3. *(Cross-module note, outside this module's responsibility.)* The record's `Trigger` field is only
   populated by `lawn-cast-trigger` (module 19), which owns the swing counter, the timer, the lock and
   the token pool. Until 19 lands, lawn records carry `AiTriggerState.None`, which is honest but means
   the inspector is partial on the lawn before 19. Named here so it is not read as a defect of this
   module, and so 19's spec knows it owes the population of this field.

## Design gate checklist (DESIGN-GATE §5)

```
[x] Subsystems identified: battle engine boundary (§3c), battle/turns trace fixtures, match/actor
    lifecycle (ptr reuse), injector debug surfaces / live-probe scope, tunables (structural only).
[x] Session boundary: backlog-clean-up-20260920; this session wrote only the four
    docs/architecture/combat-ai/spec-*.md files, edited nothing else, ran no git mutation and no build.
[x] Read this session: combat-ai-map.md, combat-ai-ideal.md rev 3 (§6.2a D4, D6), AUDIT.md (D4 row,
    C4/C5 perf), S1-battle-core.md, battle-engine-ssot.md §2/§3c/§4 D15/§5, DESIGN-GATE §1 (battle,
    battle/turns, match lifecycle, live-probe rows) + §5, decisions.md rows 43-44, CLAUDE.md +
    AGENTS.md hard rules incl. the debug-API rule.
[x] decisions.md checked: row 44 locks bloodthirsty/loyal as engine-side wrappers (so the inspector
    must record the POST-loyal target, which module 4 supplies); row 43 locks the determinism tuple.
    No lock forbids anything here.
[x] Every factual claim cites file:line; every cited file was opened this session.
[~] audit-doc-citations.py reports no HIGH finding for this file -- run after writing; the six new
    files are marked "(new; does not exist yet)".
[x] Verified against CODE, not comments: BattleTrace keeps _aiDecisions out of _lines (:24,139);
    the siege site is guarded by `if (_trace is not null)` (:270); CombatDebugObservability's cap,
    gate, queue-drain and clone-on-read (:8-53); LawnBasicAttackFeature's three-layer switch
    (:48-73); UsabilityResult's typed reason enum (:9-46).
[x] Read the surrounding section of every rule quoted (BattleTrace's own "domain-agnostic" paragraph
    before using it as a constraint; DESIGN-GATE's live-probe row; §2.16's cache-trigger corollary).
[~] Constraints tested, not assumed: "golden-neutral" is argued from construction (separate list,
    Digest joins _lines only, report untouched) AND listed as a criterion to RUN. This session ran no
    suite (spec-only lane, no builds), so the run is owed at build time, not claimed here.
[x] Nothing contradicts a §2 invariant. Invariant 2 (record-then-drain) shapes the lawn ring as a
    recorder, not a decider; invariant 12 is satisfied because the module adds no balance number.
[x] Corrections propagated: none needed -- no existing doc claim was found wrong. The partial-Trigger
    dependency on module 19 is stated in Open questions 3 rather than left implicit, and the
    post-loyal-target requirement is attributed to module 4 rather than silently assumed.
[x] No assertion pins a derived population, item total, generated text, or per-cycle outcome; the
    testing section bans asserting candidate/profile counts and score values explicitly, and points
    the closed-vocabulary pins at their owning modules.
[x] §2.16 event-refreshed cache: the lawn per-actor index IS one, and its FULL trigger set is
    enumerated in a table in §4 -- including the KEY-SET edges (spawn and death), which is the
    trigger that gets forgotten. Each trigger has a named test, and the spawn/death pair is tested
    in both orders.
[x] No acceptance criterion fixes an ordering that can vary: the death/spawn pair is explicitly
    order-independent and both directions are tested.
[x] Produces/consumes no actor combat or derived magnitude -- it records values other modules
    composed, and folds nothing. No ActorHub interaction.
[x] Extends no SOLID-violating path: it reuses UsabilityReason and AiScoreBreakdown rather than
    forking a second verdict/breakdown vocabulary, and keeps BattleTrace's existing contract.
[x] New rule has a guard: the debug-scope labelling is enforced by gk-core/scripts/guard-debug-scope.py
    (already wired into deploy-play.py); golden-neutrality by BattleTraceTests + BattleGoldenTests;
    zero-cost-when-off by module 7's allocation test. No new repo-wide rule, so no
    enforcement-registry row is owed.
```
