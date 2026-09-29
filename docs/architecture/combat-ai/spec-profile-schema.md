# Spec: `profile-schema` (combat-ai module 2)

**Program:** [combat-ai](../combat-ai-map.md) · **Ideal:** [combat-ai-ideal.md](../combat-ai-ideal.md) ·
**Depends on:** `core-scorer` (module 1) · **Unblocks:** `ai-tiers-personality`, `replay-identity`,
`action-schedule-twin`, `stance-wiring`, `lawn-held-actions` · **Status:** **built** (CAI1.6 + CAI1.8, 2026-09-20; the revision moved to `combat-ai.v2.json` with `CAI-F1`/`CAI4.7`, 2026-09-23): `Actions/Ai/CombatAiProfile.cs` + `AiVocabulary.cs` + `AiRowSelector`, published as `gk-core/data/tuning/combat-ai.v2.json` (`CombatAiTuningFiles.Current`) and read by both hosts **through that constant** (`Server/Program.cs`, `Injector/Host/RpgHost.cs`) — `SiegeKeyMigrationTests.Both_hosts_load_the_same_file` asserts neither host contains a `"combat-ai.v` literal.

## Objective

Give the one scorer its data. Today **nothing in the repo expresses an AI policy as data**: the only AI
tuning that exists is siege's, and it is a flat block of fourteen keys inside another subsystem's file
(`gk-core/data/tuning/siege.v1.json` `"ai"`, parsed at
`gk-core/src/FusionRpg.Core/Battle/Board/SiegeTuning.cs:333-375` and constructed into `Siege.AiTuning` at
`:432-439`; the record itself is `gk-core/src/FusionRpg.Core/Battle/Siege/SiegeAi.cs:60-64`, fourteen members
counted there). `CombatProfile`
(`gk-core/src/FusionRpg.Core/Combat/CombatProfiles.cs`) is a damage-floor knob, not an AI profile — the audit's
lane S1 is explicit about that ([S1-battle-core.md](../../research/combat-ai/S1-battle-core.md), row
`CombatProfile`). So a second place that wants an AI would today have to copy fourteen keys into its own
file, which is how three incompatible curves shipped once before.

This module ships four things:

1. **The profile data model** — ranked rows (rank, selector, conditions, action filter), the scoring
   block, reserve floors, waste guards, anti-repeat, and a trigger block for real-time places.
2. **Closed vocabularies in code** — selectors, row conditions, tiers, personality axes, places and roles.
   The rows are data; the vocabularies are declarations a human changes under review
   ([validation-ssot.md](../validation-ssot.md)).
3. **`gk-core/data/tuning/combat-ai.v1.json` + a parser + host injection**, following the shipped
   loader convention exactly (Core parses a string, the host reads the file —
   [tunables-ssot.md](../tunables-ssot.md) §7.2).
4. **The siege key migration**, with the reader switched in the same commit (H7).

**Every lever ships at its identity value.** That is the load-bearing posture of this module and the reason
it can land without moving a golden: the file's job in v1 is to *carry siege's fourteen keys to a new
address* and to *reserve the shape* for everything modules 3, 11, 13, 14 and wave 4 will fill in. A module
that changes a number and the schema at once cannot tell which one moved the golden — the same acceptance
`spec-mode-profile.md` (lawn-tuning-profile module 2) already ships under.

## Tech stack

`FusionRpg.Core` (the profile types and a pure parser — no file read, no path, no default),
`gk-core/data/tuning/combat-ai.v1.json` (new — **landed**, CAI1.8; the current revision is `combat-ai.v2.json` since `CAI-F1`), `gk-core/data/tuning/siege.v2.json` (**landed** — published from v1 by the tool; `siege.v3.json` is the shipped revision since `CAI3.1`), `gk-core/src/FusionRpg.Server/Program.cs` (one composition-root load beside
the existing ones), `gk-fusion/src/FusionRpg.Injector/Host/RpgHost.cs` (the same load from the plugin folder), and
`gk-core/tools/tuning/publish.py` (extended, see §Tunables). No new dependency.

## Commands

```powershell
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~CombatAiProfile|CombatAiTuning"
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~SiegeAi|SiegeTuning"
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden|ExpeditionResolver"
dotnet test gk-core/tests/FusionRpg.Server.Tests
.\scripts\verify-change.ps1 -Paths <changed files> -Session backlog-clean-up-20260920
# ONE invocation, ONE version bump (siege.v1 -> siege.v2). --remove-key is repeatable, like every
# other verb in the tool (`action="append"`, publish.py:553-596) -- see Tunables.
python gk-core/tools/tuning/publish.py siege --reason "combat-ai H7 migration" `
  --remove-key ai.weightHitChance --remove-key ai.weightObjective --remove-key ai.weightKill `
  --remove-key ai.weightLowHp --remove-key ai.weightCannotCounter --remove-key ai.weightRound `
  --remove-key ai.weightRisk --remove-key ai.aggressionRange --remove-key ai.maxCandidatesScored `
  --remove-key ai.retargetLatencyTicks
python gk-core/tools/tuning/publish.py combat-ai profiles.siege/default.scoring.weightRisk=120
python gk-core/scripts/audit-magic-numbers.py --summary
python scripts/audit-doc-citations.py --scope docs/architecture/combat-ai/spec-profile-schema.md --summary
```

## Project structure

| What | Where |
|---|---|
| Closed vocabularies (selector, condition, tier, axis, place, role) | `gk-core/src/FusionRpg.Core/Actions/Ai/AiVocabulary.cs` (new — **landed**, CAI1.6) |
| Profile record types (rows, scoring, reserve, guards, anti-repeat, trigger) | `gk-core/src/FusionRpg.Core/Actions/Ai/CombatAiProfile.cs` (new — **landed**, CAI1.6) |
| Pure parser (`Parse(string json)`) | `gk-core/src/FusionRpg.Core/Actions/Ai/CombatAiTuningLoader.cs` (new — **landed**, CAI1.6) |
| Static hub the hosts configure | `gk-core/src/FusionRpg.Core/Actions/Ai/CombatAiProfilePolicy.cs` (new — **landed**, CAI1.8) |
| The tuning file | `gk-core/data/tuning/combat-ai.v1.json` (new — **landed**, CAI1.8) |
| Siege's file after the ten keys leave | `gk-core/data/tuning/siege.v2.json` (new — **landed**, CAI1.8) |
| Siege loader: stops reading the ten moved keys | `gk-core/src/FusionRpg.Core/Battle/Board/SiegeTuning.cs` |
| Siege AI construction: takes weights from the profile hub | `gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs` (the `aiTuning != null` arm at `:627-630`) |
| Row selection (rank walk → selector + action filter) | `gk-core/src/FusionRpg.Core/Actions/Ai/AiRowSelector.cs` (new — **landed**, CAI1.6) |
| Server load | `gk-core/src/FusionRpg.Server/Program.cs` (beside `SiegeTuningPolicy.Configure` at `:223-225`) |
| Injector load | `gk-fusion/src/FusionRpg.Injector/Host/RpgHost.cs` (beside the loads at `:57-73`) |
| Parser + vocabulary tests | `gk-core/tests/FusionRpg.Core.Tests/Actions/Ai/CombatAiTuningTests.cs` (new — **landed**, CAI1.6) |
| Row-selection tests | `gk-core/tests/FusionRpg.Core.Tests/Actions/Ai/AiRowSelectorTests.cs` (new — **landed**, CAI1.6) |
| Migration-fidelity test | `gk-core/tests/FusionRpg.Core.Tests/Actions/Ai/SiegeKeyMigrationTests.cs` (new — **landed**, CAI1.8) |
| publish.py remove-key tests | `gk-core/tools/tuning/test_publish_remove_key.py` (new — **landed**, SSH5.7) |

## The shape

### 1. Closed vocabularies — what the code owns

Each of these is an `enum` with a stable string form parsed by name. An unknown string **throws, naming
the value and the key it appeared under** — never a silent skip, which is the failure mode
`spec-mode-profile.md` calls out for mode ids and `SiegeTuningLoader` already practises for
`stanceDefault` (`SiegeTuning.cs:351-353`).

```csharp
namespace FusionRpg.Core.Actions.Ai;

/// Ideal §6.1 step 1. Adding a ninth selector is a REVIEWED change: each member names a concrete read
/// through IBattleView, and a selector with no reader is a promise, not a vocabulary entry.
public enum TargetSelector
{
    Nearest = 0,              // PositionOf + GridDistance.Chebyshev — StubIntentSource.cs:104-131
    SameLaneThenAdjacent,     // PositionOf row/col; the lawn's own shape, inert where PositionOf is null
    LowestHp,                 // FactsOf(key).HpMilli
    HighestThreat,            // the scorer's IncomingThreatMilli term, inverted
    Objective,                // IBattleView.ObjectivePositionOf — IBattleView.cs:73
    Self,                     // the deciding actor
    AllyLowestHp,             // SideOf(key) == mySide, then HpMilli
    AllyDowned,               // SideOf(key) == mySide and the downed predicate the place supplies
}

/// Two tiers today. A third ("dumb"/vanilla) is reserved by the ideal and deliberately NOT registered:
/// D6 defers vanilla PvZ unit control to a later program, and an unused enum member reads as a promise.
public enum AiTier { Smart = 0, Performance = 1 }

/// D5's key axis. `sim` is absent on purpose: the sim runtime (RuntimeId.Sim, AtomKind.cs:82-84) resolves
/// effects, it declares no intents. Adding a place is a reviewed change.
public enum AiPlace { Lawn = 0, Battle = 1, Delve = 2, Siege = 3 }

/// D5's second key axis. NOTHING IN THE REPO SUPPLIES A COMBAT ROLE TODAY — the nearest existing enum,
/// WorldEntityMemberRole (WorldState.cs:271-275), is Fighter/Bearer, a logistics distinction, not a
/// combat one. So `Default` is the only role any actor resolves to in v1, and the other three are the
/// ideal's own named delve rows (§6.2), reserved so a role source can land without a schema version bump.
public enum AiRole { Default = 0, Frontliner = 1, Support = 2, Striker = 3 }
```

**Row conditions** are split into two classes, and the split is the design decision worth reading:

```csharp
/// Conditions about ONE actor's own facts. These are exactly what the shipped compiled predicate
/// already answers through FactReader at gate 5 (UsabilityEvaluator.cs:80-81), so a profile row that
/// wants one NAMES AN ACTION FILTER instead and lets gate 5 do the work. This enum therefore holds only
/// what a row needs BEFORE an action is chosen.
public enum AiRowCondition
{
    Always = 0,
    SelfHpBelowMilli,        // FactsOf(self).HpMilli
    SelfResourceBelowMilli,  // the pool read the reserve floor already uses
    TargetHpBelowMilli,      // FactsOf(target).HpMilli
    HasStatus,               // FactsOf(self).StatusMask
    TargetHasStatus,         // FactsOf(target).StatusMask
}

/// Census conditions — questions about the BOARD, which FactReader structurally cannot answer because it
/// is constructed per (self, target) pair (StubIntentSource.cs:67, SiegeAiIntentSource.cs:146). Exactly
/// four, each answered from IBattleView.LiveActorKeys + SideOf (IBattleView.cs:22,26) at O(live) with no
/// new read. A fifth is a reviewed change.
public enum AiCensusCondition
{
    None = 0,
    EnemiesAtLeast,
    EnemiesAtMost,
    AlliesDownedAtLeast,
    RoundAtLeast,
}

/// Module 3 owns what each axis DOES; this module owns that the list is closed and append-only.
/// Append-only matters for determinism: module 3 draws one value per axis in declaration order from one
/// seeded stream, so inserting a member in the middle would reshuffle every actor's personality.
public enum PersonalityAxis { Aggression = 0, Recklessness = 1, Focus = 2, Thrift = 3 }
```

### 2. The profile record

```csharp
/// One place x role policy. The ROWS are data (content grows them); the vocabularies above are
/// declarations. That distinction is what the tests assert and what they refuse to assert.
public sealed record CombatAiProfile(
    string ProfileId,                       // "siege/default" — the key, echoed for provenance/trace
    AiPlace Place,
    AiRole Role,
    AiTier? TierOverride,                   // null => the tier-by-actor-class map below decides
    IReadOnlyDictionary<AiActorClass, AiTier> TierByActorClass,  // D6's rule as data; module 3 owns
                                            // what a tier DOES and adds the AiActorClass enum to
                                            // AiVocabulary.cs. This module owns that the map exists,
                                            // is total over the enum, and is rejected at parse if not.
    IReadOnlyList<AiProfileRow> Rows,       // ordered; index IS the rank, lower wins
    AiScoringBlock Scoring,
    AiSelectionBlock Selection,
    IReadOnlyList<AiReserveFloor> Reserves, // per resource id; empty = no floor
    AiWasteGuards Guards,
    AiAntiRepeat AntiRepeat,
    AiTriggerBlock? Trigger,                // real-time places only; null for turn places
    AiPersonalityBounds Personality);

/// Rank is the row's INDEX, not a stored int. Two rows cannot tie, and a rank cannot be skipped — both
/// are classes of authoring bug that a stored rank invites and a list forbids by construction.
public sealed record AiProfileRow(
    TargetSelector Selector,
    AiRowCondition Condition, int ConditionArgMilli, string ConditionArgId,
    AiCensusCondition Census, int CensusArg,
    AiActionFilter Actions);

/// "by tag, family or rung" (ideal §6.1 Layer C). All three are optional; an empty filter admits every
/// held action, which is StubIntentSource's behaviour and therefore the identity.
public sealed record AiActionFilter(
    IReadOnlyList<ActionTag>? Tags,   // the shipped closed enum, ActionEnums.cs:47-58
    IReadOnlyList<string>? Families,
    int? MinRung, int? MaxRung);

public sealed record AiScoringBlock(
    int WeightHitChance, int WeightObjective, int WeightKill, int WeightLowHp,
    int WeightCannotCounter, int WeightRound, int WeightRisk,
    int AggressionRange,        // STRUCTURAL: the range IS the taunt/stealth/decoy vocabulary
    int MaxCandidatesScored);   // STRUCTURAL: a per-decision work bound, not a progression ceiling

public sealed record AiSelectionBlock(SelectionMode Mode, int KeepPctMilli, string RngStreamName);
public sealed record AiReserveFloor(string ResourceId, int FloorMilliOfMax);
public sealed record AiWasteGuards(int MinTargetsForArea, int KillMarginMilli, int FightEndingLiveCount);
public sealed record AiAntiRepeat(long RetargetLatencyTicks, long CommitmentBonus, int RepeatDecayHalfLifeTicks);
/// Real-time places only. THREE fields, not five: the per-frame decision budget and the cast-token
/// pool are per-frame/runtime work caps and live as code `const`s in module 19
/// (`spec-lawn-cast-trigger.md` §Tunables), because a value on the balance surface is editable by a
/// balance pass whatever a table calls it. A schema field for a number that lives in code is the
/// dead-config shape the ideal §8 forbids, so neither is reserved here.
public sealed record AiTriggerBlock(int SwingsN, long TicksT, long PostCastLockL);
public sealed record AiPersonalityBounds(IReadOnlyDictionary<PersonalityAxis, int> BoundByAxis);
```

**The root record — the thing `CombatAiTuningLoader.Parse` actually returns.** Named here because every
downstream module references it (`CombatAiProfilePolicy.Configure(CombatAiTuning)`, module 8's
`TuningVersion` stamp, module 4's `router` reads) and a record nobody declares is a promise:

```csharp
/// The whole file, parsed. `SchemaVersion` is the SHAPE (a reader change); `Version` is the publish
/// counter `publish.py` bumps (a balance change). Module 8 stamps `Version` into the match row, which
/// is why the two are separate fields and not one number.
public sealed record CombatAiTuning(
    int SchemaVersion,
    int Version,
    IReadOnlyDictionary<string, CombatAiProfile> Profiles,   // keyed "<place>/<role>"; "*/default" required
    AiRouterBlock Router);                                   // module 4's two keys; see below

/// Owned by `intent-router` (module 4) — it is the only reader — but DECLARED here, because this
/// module owns the file's shape and a parser cannot parse a block no record names.
/// `OrderTimeoutTicks` and `ReactionsPerRoundExpected` are balance values (module 4's Tunables table
/// states both seeds and why); `MaxLiveOrdersPerActor` is deliberately NOT here — module 4 keeps it a
/// code `const` because a second live order is a queue, which is a design change, not a number.
public sealed record AiRouterBlock(long OrderTimeoutTicks, int ReactionsPerRoundExpected);
```

`AiScoringBlock` projects one-to-one onto module 1's `ScoringWeights`, and `AiSelectionBlock` onto its
`SelectionPolicy`. The projection is positional, so a reviewer can check it by eye — the same property
module 1 relies on for the `AiCandidate` → `TargetCandidate` copy.

### 3. Key resolution — place x role, with a named fallback chain

```
"siege/striker"  ->  "siege/default"  ->  "*/striker"  ->  "*/default"
   exact              place default        role default     the root
```

Four steps, tried in that order, and **the root `*/default` row is required to exist** — a file without it
is rejected at parse time, so a lookup can never fail at decision time on the hot path. A missing
intermediate row is not an error and not a silent no-op: it falls through by the stated rule, which is the
`spec-mode-profile.md` discipline ("a missing row falls back to `battle` — the identity — so a host that
has not been taught about a new mode behaves exactly as today").

Because no role source exists (§1), every actor resolves `AiRole.Default` in v1 and the chain collapses to
`"<place>/default" -> "*/default"`. **That is a wiring gap, not a design gap**, and it is stated here so a
later reader does not mistake the reserved role members for dead vocabulary.

### 4. Row selection — how a rank walk yields a selector and an action filter

**This module owns the walk, not just the rows.** `core-scorer` (module 1) deliberately punts it
(*"Which rank row it must come from is module 2's profile; this module only guarantees one pass over
held actions"*, [spec-core-scorer.md](spec-core-scorer.md) §5), and a rank vocabulary with no evaluator
is a data shape nobody can execute. `AiRowSelector` is that evaluator, and it is a **pure function** —
no view read of its own, every board fact arrives as a supplied value:

```csharp
namespace FusionRpg.Core.Actions.Ai;

/// FF12's gambit rule, and the ONLY place it is expressed: walk Rows in index order (the rank), take
/// the FIRST row whose Condition AND Census both hold, and hand its Selector + Actions to module 1's
/// TargetStage/ActionStage. Pure: the two census counts and the two fact reads are PASSED IN, so this
/// type never touches IBattleView and a caller cannot accidentally make the walk O(rows x live).
public static class AiRowSelector
{
    public static bool TryPick(
        CombatAiProfile profile,
        in AiRowFacts facts,        // self/target facts + the census counts, resolved ONCE per decision
        out TargetSelector selector,
        out AiActionFilter actions,
        out int rankIndex);         // the row's index, for the trace (module 10 reads it)
}

/// Everything a row condition can ask, gathered once before the walk. Four census numbers, not a
/// board: `AiCensusCondition` is exactly four members (§1), so this record is total over it and a
/// fifth member fails the build here rather than defaulting to "condition false".
public readonly record struct AiRowFacts(
    int SelfHpMilli, int SelfResourceMilli, string SelfResourceId,
    int TargetHpMilli, ulong SelfStatusMask, ulong TargetStatusMask,
    int EnemiesLive, int AlliesDowned, int Round);
```

Five rules, each of which is a bug class a looser walk would admit:

1. **First match wins, index order, no re-entry.** `AiProfileRow`'s own doc already fixes this
   (*"Rank is the row's INDEX, not a stored int"*, §2). The walk stops at the first hit; it never
   collects several rows and merges them, which would be a second selection mechanism beside module 1's
   `SelectionPolicy`.
2. **The facts are gathered once, before the walk.** `EnemiesLive` / `AlliesDowned` come from
   `IBattleView.LiveActorKeys` + `SideOf` (`gk-core/src/FusionRpg.Core/Actions/IBattleView.cs:22,26`) at O(live)
   **once per decision**, by the caller. A row that re-counted per row would make an eight-row profile
   eight board scans — the exact per-decision cost module 7 (`decision-perf`) exists to remove.
3. **A row whose `Condition` needs a target is skipped when no target is chosen yet.**
   `TargetHpBelowMilli` / `TargetHasStatus` are evaluated against the *previous* decision's held target
   when the ledger holds one (`RetargetLedger.TryGetHeld`, module 1 §6) and are **false** otherwise.
   False, not "throw" and not "true": a row that cannot be evaluated has not matched, and the walk
   continues. The alternative — running the target stage per row to answer its condition — is the
   O(rows × cap) shape this rule exists to forbid.
4. **The last row is required to be unconditional.** A profile whose final row is not
   `Condition = Always, Census = None` is **rejected at parse**, in the loader, beside the other range
   checks (§Code style). Without it a decision can fall off the end of the walk with no selector, and
   the honest answers at that point are all bad ones. This is the same posture as the required
   `*/default` profile row (§3): make the total function total at load, never at the hot path.
5. **`TryPick` returns `false` only for an empty `Rows` list**, which rule 4 makes impossible for a
   parsed profile and possible only for a test-constructed one. The caller treats `false` as
   `ActionIntent.None` — the deciding side's own "nothing to do" value
   (`gk-core/src/FusionRpg.Core/Battle/Timeline/IntentSource.cs:12-18`), never an exception on a decision path.

**Cost.** O(rows) comparisons over value fields, plus the one O(live) census the caller already pays.
No allocation: `AiRowFacts` is a readonly struct passed by `in`, and the two outputs are the profile's
own already-constructed objects, never copies.

**Who calls it.** `CoreIntentPolicy` (module 3 — [spec-ai-tiers-personality.md](spec-ai-tiers-personality.md)
§6), once per `TryDeclare`, between resolving the profile and entering module 1's target stage. Siege's
own `SiegeAiIntentSource` does **not** call it in module 1's commit: siege has no authored rows at
migration, and a one-row implicit profile would be a row nobody wrote. It joins when siege's rows are
authored, which is `siege-loadout-wiring`'s cause, not this one.

### 5. Loading — the shipped convention, copied exactly

Core parses; the host reads. This is the pattern every recent domain already uses, and the file names the
precedent so nobody invents a fifth shape:

```csharp
public static class CombatAiTuningLoader          // pure; takes a string, returns a record; no I/O
{
    public static CombatAiTuning Parse(string json);
}

public static class CombatAiProfilePolicy         // the static hub the hosts configure, exactly as
{                                                 // SiegeTuningPolicy does (SiegeTuning.cs:481-508)
    public static void Configure(CombatAiTuning tuning);
    public static CombatAiProfile For(AiPlace place, AiRole role);
    public static int TuningVersion { get; }      // read by module 8 for the match stamp
}
```

Server (`gk-core/src/FusionRpg.Server/Program.cs`, beside `:217-219`):

```csharp
FusionRpg.Core.Actions.Ai.CombatAiProfilePolicy.Configure(
    FusionRpg.Core.Actions.Ai.CombatAiTuningLoader.Parse(
        File.ReadAllText(Path.Combine(tuningDir, "combat-ai.v1.json"))));
```

Injector: the same two lines in `gk-fusion/src/FusionRpg.Injector/Host/RpgHost.cs`, against its own
`Path.Combine(_pluginDir, "data", "tuning")` (`RpgHost.cs:57`). Tests construct a `CombatAiTuning` inline
and never touch a fixture file (`tunables-ssot.md` §7.2).

**No default to fall back on.** `CombatAiProfilePolicy` throws the same shape of error
`SiegeTuningPolicy` does when `Configure` has not run (`SiegeTuning.cs:488-490`) — a built-in default would
be a second balance surface hiding in code.

### 6. The siege key migration — which keys move, which stay, which are dead

`gk-core/data/tuning/siege.v1.json`'s `ai` block holds fourteen keys. They are three different things, and the
audit's design challenge 5 is that the ideal moved "`ai.*` weights" without saying which.

| Key | v1 value | Fate | Why |
|---|---|---|---|
| `weightHitChance` | 70 | **move** → `combat-ai.v1.json` `profiles["siege/default"].scoring` | scorer weight |
| `weightObjective` | 50 | **move** | scorer weight |
| `weightKill` | 15 | **move** | scorer weight |
| `weightLowHp` | 10 | **move** | scorer weight |
| `weightCannotCounter` | 10 | **move** | scorer weight |
| `weightRound` | 1 | **move** | scorer weight |
| `weightRisk` | 120 | **move** | scorer weight |
| `aggressionRange` | 2 | **move** | the scorer's closed tier vocabulary width; module 6 reads it |
| `maxCandidatesScored` | 32 | **move** | the scorer's work bound |
| `retargetLatencyTicks` | 0 | **move** | `RetargetLedger`'s window, which moved to `Core/Actions/Ai/` in module 1 |
| `objectiveReferenceDistanceCells` | 20 | **stays** in `siege.v{n+1}.json` | siege board geometry: it normalises a Chebyshev distance to the siege objective, computed while *building* a candidate (`SiegeAiIntentSource.cs:423-430`), never inside the scorer |
| `threatRadiusCells` | 4 | **stays** | siege board geometry: the radius of the threat sum (`SiegeAiIntentSource.cs:484`), again a candidate input |
| `stanceDefault` | `"Guard"` | **dead — does not move** | parsed at `SiegeTuning.cs:351-353` and read nowhere. `StanceRuntime` has no production constructor and every policy gets `NoStanceHeld.Instance` (`BattleRunState.cs:194`), so gate 0 is inert everywhere (audit C3/B3) |
| `autoResolveHandicapMilli` | 1000 | **dead — does not move** | parsed at `SiegeTuning.cs:355-357` and read nowhere |

**The two dead keys stay exactly where they are, untouched, in `siege.v{n+1}.json`.** They are
`stance-wiring`'s (module 11) to wire or delete, with the decision criterion that module already carries
("is any held action a stance action today?"). Migrating dead config is the one outcome the ideal forbids
by name (§8, *"Never migrated as dead config"*), and deleting them here would fold module 11's cause into
this commit.

### 7. H7 — the reader switch lands in the same commit

One commit contains all of:

1. `gk-core/data/tuning/combat-ai.v1.json` created, carrying the ten values **unchanged** plus every new lever at
   its identity default (§Tunables).
2. `gk-core/data/tuning/siege.v2.json` published from v1 with the ten keys dropped, through **one**
   `publish.py --remove-key × 10` invocation (§Tunables) — never a hand edit, and never ten publishes.
3. `SiegeTuningLoader.Parse` stops reading the ten (`SiegeTuning.cs:333-366`), and `Siege.AiTuning`
   (`SiegeAi.cs:60-64`, fourteen members today) **narrows to exactly four**:
   `StanceDefault`, `AutoResolveHandicapMilli`, `ObjectiveReferenceDistanceCells`, `ThreatRadiusCells`
   — the two dead keys plus the two geometry ones. That four-member record is the state
   `stance-wiring` (module 11) starts from, and it says so.
4. `BattleRunState`'s `aiTuning != null` arm (`:627-630`) constructs `SiegeAiIntentSource` with
   `ScoringWeights` from `CombatAiProfilePolicy.For(AiPlace.Siege, AiRole.Default)` instead of from
   `SiegeTuningPolicy.Ai`.
5. `gk-core/src/FusionRpg.Server/Program.cs` loads `combat-ai.v1.json` **and** switches its siege load to
   `siege.v2.json`; `RpgHost.cs` does the same.

A publish without its reader is a silent behaviour change on the next deploy; a reader without its publish
throws at startup. Both are refusals, so they ship together or not at all.

`gk-core/data/tuning/siege.v1.json` stays on disk (T4: reverting a balance pass is restoring a file). Any test or
tool that still pins `siege.v1.json` by name must move to v2 in this same commit, or it silently keeps
reading ten keys nobody writes any more — the implementer greps for the literal `siege.v1.json` and fixes
every hit.

## Tunables

**File:** `gk-core/data/tuning/combat-ai.v1.json`. **Owner:** this spec. **Published:** `v{n+1}` through
`gk-core/tools/tuning/publish.py`, never hand-edited ([tunables-ssot.md](../tunables-ssot.md) T4). Creating v1 is
the authoring act; every change after it goes through the tool.

```jsonc
{
  "schemaVersion": 1,
  "version": 1,
  "_meta": { "owner": "docs/architecture/combat-ai/spec-profile-schema.md" },
  "profiles": {
    "*/default":     { /* the required root — every lever at its identity value */ },
    "siege/default": { /* the ten migrated values, unchanged */ }
  },
  // Top-level, NOT under a profile: the router is one object per battle, not one per place x role
  // (intent-router, module 4 — its Tunables table owns both seeds). Declared as `AiRouterBlock` in §2.
  // It is required: a file without it is rejected at parse, for the same reason `*/default` is.
  "router": { "orderTimeoutTicks": 5000, "reactionsPerRoundExpected": 1000 }
}
```

| Key | v1 value | Unit | Why this seed |
|---|---|---|---|
| `profiles["siege/default"].scoring.weightHitChance` | 70 | weight | XCOM's shipped value, carried unchanged — the migration's whole claim |
| `.scoring.weightObjective` | 50 | weight | unchanged |
| `.scoring.weightKill` | 15 | weight | unchanged (hit-chance dominates lethality 70:15; inverting it reads as suicidal — `siege.v1.json`'s own `ai._note`) |
| `.scoring.weightLowHp` | 10 | weight | unchanged |
| `.scoring.weightCannotCounter` | 10 | weight | unchanged (Fire Emblem's term) |
| `.scoring.weightRound` | 1 | weight | unchanged (anti-turtle) |
| `.scoring.weightRisk` | 120 | weight | unchanged |
| `.scoring.aggressionRange` | 2 | tiers, +/- | **structural** — the range IS the taunt/stealth/decoy vocabulary (`Actions/Ai/CombatAiProfile.cs:59`, moved from SiegeAi.cs by CAI1.1/CAI1.8); comment required at the C# field |
| `.scoring.maxCandidatesScored` | 32 | count | **structural** — a per-decision work bound; comment required |
| `.antiRepeat.retargetLatencyTicks` | 0 | ticks | unchanged; 0 reproduces the stateless path exactly (`Actions/Ai/RetargetLedger.cs:26-36`, its post-CAI1.4 home) |
| `profiles["*/default"].scoring.*` | the same ten values | — | the root row is siege's, because siege is the only place with measured weights today. Marked `UNMEASURED` for every other place, the posture `aptitudes.v{n}.json` and `spec-mode-profile.md` already ship under |
| `.selection.mode` | `"argmax"` | enum | determinism is the default; a weighted pick is opt-in (ideal §3 principle 4) |
| `.selection.keepPctMilli` | 1000 | **bounded ratio** 0..1000 | 1000 keeps only ties with the best, i.e. argmax. Bounded ratio, exempt from the no-ceiling rule, comment says so |
| `.selection.rngStreamName` | `"ai.select"` | string | a stable stream name for `SeededRng.DeriveStream` (`SeededRng.cs:9-28`) |
| `.reserves` | `[]` | — | no floor. Identity: today nothing reserves anything |
| `.guards.minTargetsForArea` | 1 | count | 1 = off (any single target satisfies it). Identity |
| `.guards.killMarginMilli` | 0 | per-mille | 0 = off. Identity |
| `.guards.fightEndingLiveCount` | 0 | count | 0 = off. Identity |
| `.antiRepeat.commitmentBonus` | 0 | score | 0 = off. Lewis: a bonus only moves the oscillation zone, so it starts off |
| `.antiRepeat.repeatDecayHalfLifeTicks` | 0 | ticks | 0 = off. Identity |
| `.tierByActorClass.unique` / `.general` | `"smart"` / `"performance"` | enum | D6, as data. Module 3 gives the tiers their meaning; this module only carries the map and rejects a file whose map does not cover both classes |
| `profiles["siege/default"].tierOverride` | `"smart"` | enum | siege scores every actor today (`BattleRunState.cs:743-757`), so an explicit override keeps the migration byte-identical whether or not any host ever wires a class resolver |
| `.personality.bounds.*` | 0 for all four axes | offset | 0 = every offset is 0 = byte-identical. Module 3 turns them on as its own cause |
| `.trigger` | absent | — | turn places have no trigger block; the lawn's `N`/`T`/`L` are wave 4's to author. The lawn's per-frame budget and token pool are **not** here — they are code `const`s in module 19 (`spec-lawn-cast-trigger.md` §Tunables), which is why `AiTriggerBlock` has three fields and not five |
| `router.orderTimeoutTicks` | 5000 | ticks | module 4's key, in this module's file. Five seconds of virtual time — module 4's Tunables table carries the derivation |
| `router.reactionsPerRoundExpected` | 1000 | per-mille of a round | module 4's key. What the `poise` reserve floor budgets for engine counters; module 1's `ReserveFloorAffordability` is the reader |

**`publish.py` needs one narrow extension, this module owns it, and building it is part of this
module.** The tool edits and adds; it has no way to *remove* a key (its docstring: *"`set` refuses to
invent a key by design"*, `gk-core/tools/tuning/publish.py:22-23`), and the H7 migration must remove ten.
`CLAUDE.md`'s tunables rule is explicit that the answer is to extend the tool (*"extend the tool when a
domain lacks support — tunables-ssot T4"*), and `tunables-ssot.md` §7.1 says the domain that needs a
shape builds it. The verb is **`--remove-key`**, the inverse of the shipped `--add-key`
(`publish.py:421-443`, registered at `:581-583`) and named for it — one name, one spelling, repo-wide.
`stance-wiring` (module 11) is the only other caller and it cites this row rather than restating it.

The extension is deliberately narrow, in the register `--add-key` / `--add-edge` / `--rename-key`
already established:

- `--remove-key <dotted.path>` removes exactly one existing key;
- it **refuses** if the path does not resolve (never a silent no-op), the same refusal `--add-key` makes
  in the other direction;
- it is **repeatable within one invocation** — `action="append"`, exactly like every other verb the tool
  registers (`publish.py:553-596`) — and **one invocation writes exactly one `v{n+1}`**. This is the
  correction that matters: ten removals are **one** publish producing `siege.v2.json`, not ten hops
  through `v2..v11`. Each removed path is its own reviewable line in the command and its own entry in
  `_meta`; reviewability comes from the argument list, not from ten version files;
- it **requires** `--reason "<text>"`, recorded in the published file's `_meta` beside each removed
  path, because a removal is the one publish whose intent cannot be read off the diff.

**Version bookkeeping that follows from "one invocation, one bump":** this module's single invocation
takes `siege.v1.json` → `siege.v2.json` (ten keys). `stance-wiring` (module 11) later takes
`v2` → `v3` in its own single invocation (two keys). Those are the numbers both specs use, and they are
correct **only** under the batch rule above — a one-key-per-invocation tool would land this module on
`v11` and module 11 on `v12`.

Tests for it live in `gk-core/tools/tuning/test_publish_remove_key.py`, beside the existing
`test_publish_add_key.py`, and one of them asserts the batch property directly: *N removals in one
invocation produce exactly one new version file.*

No magic numbers in code: `CombatAiProfile`, the loader and the policy carry no bare numbers beyond `0`,
`1` and the per-mille divisor `1000`. `python gk-core/scripts/audit-magic-numbers.py --summary` must not gain a row
for `Actions/Ai/`.

## Code style

- **Parse by name, throw on unknown, name the value and its key.** `SiegeTuningLoader`'s own rejections are
  the template (`SiegeTuning.cs:351-353`, `:361-366`) — a typed `CombatAiTuningRejection`, one message per
  key, never a `TryParse` that shrugs.
- **Validate at parse, not at decision time.** Range checks (`keepPctMilli` in 0..1000, `aggressionRange`
  > 0, `maxCandidatesScored` > 0) run once, in the loader, exactly as `SiegeTuning.cs:361-366` does. The hot
  path never re-validates. The same applies to the two structural requirements this module adds: a
  missing `router` block and a profile whose **last** row is conditional (§4 rule 4) are both parse-time
  rejections, so a decision can never fall off the end of a rank walk.
- **Records, `init`-only, no mutable collections** on anything a decision reads.
- **Every structural number carries its comment** at the C# field, saying it is structural and why —
  `AGENTS.md`'s no-hard-ceiling rule requires it and `SiegeAi.cs:56-58` is the shipped example.
- **Core reads no file.** The loader takes a `string`.

## Testing strategy

Contracts and closed vocabularies only ([validation-ssot.md](../validation-ssot.md)).

**`CombatAiTuningTests`**
- ✅ `Every_selector_string_resolves_to_a_member` / `...condition...` / `...tier...` / `...axis...` /
  `...place...` / `...role...` — and an unknown string throws with the offending value **and its key** in
  the message.
- ✅ `TargetSelector_has_eight_members`, `AiTier_has_two`, `AiPlace_has_four`, `AiRole_has_four`,
  `AiRowCondition_has_six`, `AiCensusCondition_has_five`, `PersonalityAxis_has_four`. **Pinned literals,
  each with its reason in the test:** these are closed vocabularies the code owns and a human changes
  under review — the mirror image of the population rule, not an exception to it.
- ✅ `Missing_root_profile_is_rejected` — a file without `*/default` throws at parse.
- ✅ `Key_resolution_falls_back_in_the_stated_order` — `siege/striker` → `siege/default` → `*/striker` →
  `*/default`, each step exercised.
- ✅ `Out_of_range_values_are_rejected_at_parse` — `keepPctMilli` 1001, `aggressionRange` 0,
  `maxCandidatesScored` 0.
- ✅ `A_file_without_a_router_block_is_rejected` and `A_profile_whose_last_row_is_conditional_is_rejected`
  — the two structural requirements §2 and §4 rule 4 add, each refused at parse rather than at the hot
  path.
- ✅ `Core_reads_no_file` — the loader's only input is a string (a signature assertion, matching the
  discipline `SiegeTuning.Parse` already follows at `:120`).
- ❌ **Never** assert how many profiles the file holds, how many rows a profile has, or any row's authored
  text. Those are a population that content grows.

**`AiRowSelectorTests`** (§4's walk — contracts, never a row count)
- ✅ `First_matching_row_wins_and_the_walk_stops` — a profile whose rank 0 and rank 2 both match yields
  rank 0's selector and `rankIndex == 0`; rank 2's filter is never returned.
- ✅ `A_row_whose_condition_needs_a_target_is_false_when_no_target_is_held` — rule 3, asserted rather
  than left to the implementer's instinct.
- ✅ `Census_facts_are_read_from_the_supplied_struct_and_never_recounted` — a counting fake for the
  caller-side census is invoked **once** for an eight-row profile. Counted, not timed.
- ✅ `AiRowFacts_is_total_over_AiCensusCondition` — every one of the four census members has a field to
  read; a fifth member would not compile. The closed-vocabulary pin, with its reason in the test.
- ✅ `An_empty_rows_list_returns_false_and_never_throws` — the `ActionIntent.None` path.
- ❌ Never assert how many rows a shipped profile has, or the text of a row.

**`SiegeKeyMigrationTests`**
- ✅ `The_ten_migrated_values_match_siege_v1` — 70/50/15/10/10/1/120/2/32/0 parse out of
  `combat-ai.v1.json` identically. A migration-fidelity contract: the module's claim is *"the same
  numbers at a new address"*, so these ten are the contract, not a reading. The test says so.
- ✅ `Siege_v2_no_longer_carries_the_ten` and `Siege_v2_still_carries_the_two_geometry_keys`.
- ✅ `Siege_v2_still_carries_the_two_dead_keys` — `stanceDefault` and `autoResolveHandicapMilli` are
  **unchanged**, because deleting them is module 11's decision. A test that asserts they are gone would be
  asserting a decision nobody has made.
- ✅ `Profile_defaults_are_the_identity_set` — argmax, keepPct 1000, no reserves, all guards off, all
  anti-repeat off, all personality bounds 0.

**Golden impact: byte-identical, and that is the acceptance.** The ten values do not change, the reader
switches in the same commit, and every new lever is at its identity value. `BattleGoldenTests` and
`ExpeditionResolverTests.Tier_goldens_are_locked` are unchanged and unblessed. **If a golden moves, this
module is wrong** — it is a relocation, not a balance pass.

## Boundaries

**Always**
- Publish `v{n+1}` through `publish.py`; extend the tool when it cannot express the change.
- Land the publish and its reader in one commit (H7).
- Keep every new lever at its identity value in v1.
- Throw, naming the value and its key, on an unknown vocabulary string.
- Keep Core file-free; hosts read.

**Ask first**
- Adding a member to any of the six closed vocabularies.
- Any change to one of the ten migrated values (that is a balance pass, and it is a separate cause).

**Never**
- Publish a multi-key removal as several invocations. One migration is one `v{n+1}`; a chain of version
  hops makes the intermediate files states nobody ever ran and nobody can revert to meaningfully.
- Re-count the census inside the rank walk, or evaluate a row by running the target stage for it.
- Hand-edit a tuning file, including the one this module creates, after v1 exists.
- Migrate `stanceDefault` or `autoResolveHandicapMilli`. They are dead, and `stance-wiring` decides their
  fate.
- Move `objectiveReferenceDistanceCells` or `threatRadiusCells` — they are siege board geometry and
  belong to the loop, not the mechanism.
- Give `CombatAiProfilePolicy` a built-in default profile. A default in code is a second balance surface.
- Build a second predicate engine beside `ICompiledPredicate` (see Open questions).
- Assert a profile-population count in a test.

## battle-engine-ssot §5 — the six answers

1. **Which responsibility (§3), or a new one?** **None.** This is configuration for a deciding system, and
   deciding is outside the engine by §3c. It adds nothing to the closed register.
2. **Does it DECIDE or RESOLVE?** **Neither directly — it is the data a decider reads.** It never reaches
   a resolution step; the only path from this file to the engine is through module 1's scorer and
   `IIntentSource.TryDeclare` (`IntentSource.cs:29-37`).
3. **Mechanism or loop?** **A mechanism**: one schema, one parser, one hub, every mode. Each place's
   *trigger* block describes that place's loop, but the schema that carries it is shared.
4. **Which existing implementation does it extend?** The loader convention itself —
   `SiegeTuningLoader.Parse` + `SiegeTuningPolicy.Configure` (`SiegeTuning.cs:120`, `:481-508`) with the
   host-side read at `gk-core/src/FusionRpg.Server/Program.cs:223-224`. It replaces siege's AI block rather than duplicating it.
5. **Does every mode get it?** **Yes** — that is the point of `place x role`. Siege is keyed in v1;
   battle, delve and lawn rows are authored by modules 13, 14 and wave 4 as their own causes.
6. **Is it deterministic and seeded?** **Yes, and it is the reason replay identity needs a new field.** A
   profile publish changes re-derived automated decisions, and `ComputeContentHash` covers database tables
   only, not `gk-core/data/tuning/*` (audit M3). `CombatAiProfilePolicy.TuningVersion` exists so
   `replay-identity` (module 8) can put it in the match stamp and pin a profile per match. Any RNG the
   profile enables is `SeededRng.DeriveStream` with a stream name **from the file**, never a clock.

## Success criteria

1. `gk-core/data/tuning/combat-ai.v1.json` exists, carries a required `*/default` row and a `siege/default` row,
   and is loaded by both hosts.
2. Six closed vocabularies live in `AiVocabulary.cs`; an unknown string throws naming the value and its
   key; each vocabulary's member count is pinned with a stated reason.
3. Key resolution is `place/role` → `place/default` → `*/role` → `*/default`, tested at every step.
4. `CombatAiTuning` and `AiRouterBlock` exist as declared records; a file missing `router` or `*/default`
   is rejected at parse.
5. `AiRowSelector.TryPick` is the only rank walk in the repo: first match wins, facts are supplied not
   re-read, the last row is required unconditional at parse, and an empty list returns `false`.
6. The ten siege keys are in `combat-ai.v1.json` with their v1 values; `siege.v2.json` no longer carries
   them; the two geometry keys and the two dead keys are untouched.
7. `SiegeTuningLoader`, `Siege.AiTuning`, `BattleRunState:627-630` and both hosts switch in the **same
   commit** as the publish.
8. `publish.py --remove-key` exists, refuses an unresolvable path, is repeatable within one invocation,
   writes exactly **one** `v{n+1}` per invocation, requires `--reason`, and has tests — including one
   that asserts the batch property (ten removals → `siege.v2.json`, not `v11`).
9. Core reads no file; tests construct tuning inline.
10. Every golden hash unmoved; no siege test edited beyond the `siege.v1.json` → `siege.v2.json` literal.

## Open questions

1. **Should `AiRowCondition` compile to `ICompiledPredicate` instead of being a closed enum?** The
   shipped predicate engine already answers self/target fact questions at gate 5 through `FactReader`
   (`UsabilityEvaluator.cs:80-81`), and two predicate vocabularies is the kind of near-duplication this
   program exists to remove. Options: (a) closed enum for v1, with `AiCensusCondition` beside it for the
   four board questions `FactReader` structurally cannot answer; (b) compile fact conditions through the
   existing engine now and keep only the census four in an enum. **Recommended default: (a)**, with a
   stated trigger to revisit — *if `AiRowCondition` reaches eight members, fold the fact half into
   `ICompiledPredicate`.* The reason for (a) first is honest scope: the compiler's authoring surface was
   not read in this session, so specifying (b) now would be a design written against a file nobody opened.
2. **Where does a combat `AiRole` come from?** Nothing supplies one today — the nearest enum,
   `WorldEntityMemberRole` (`WorldState.cs:271-275`), is Fighter/Bearer. Options: (a) every actor is
   `Default` until a role source exists; (b) derive a role from species shape; (c) author a role per
   loadout. **Recommended default: (a).** (b) risks the AI inventing a parallel creature classification
   beside the creature program's own vocabulary, which DESIGN-GATE §1's creature row warns about
   specifically. *Cross-module note:* whoever adds a role source should add it as a creature-program
   concept the AI **reads**, never as an AI-local classification.
3. *(Cross-module note.)* Module 8 (`replay-identity`) needs `TuningVersion` on the match stamp **and** a
   pinned profile per match. This module exposes the version; it deliberately does not implement the
   pinning, because the stamp lives in `WebMatchService` and the pin has to survive
   `ResumeReplayThenLive`. Named so it is not assumed to be covered here.

## Design gate checklist

```
[x] I identified the subsystem(s) this touches: battle AI, and "Any tunable number" (DESIGN-GATE §1).
[x] Session boundary: backlog-clean-up-20260920 (tasks/sessions/backlog-clean-up-20260920.json).
    This lane writes four spec files and edits no source.
[x] I read every doc in the §1 row(s) this session: tunables-ssot.md §7, battle-engine-ssot.md §2/§3c/§5,
    combat-ai-map.md, combat-ai-ideal.md rev 3, AUDIT.md (design challenge 5 is this module's), S1, S3, S5,
    validation-ssot.md's rule as restated in AGENTS.md/CLAUDE.md.
[x] I checked decisions.md for a lock: the "Action selection (battle adoption)" row and the Status SSOT
    row both restate the tunables-ssot §7.2 line ("Core still does no File.Read; hosts inject"). This
    module follows it.
[x] Every factual claim cites file:line, and every file cited was opened this session: siege.v1.json's ai
    block, SiegeTuning.cs (parse block and policy), SiegeAi.cs, SiegeAiIntentSource.cs,
    BattleRunState.cs, Program.cs, RpgHost.cs, publish.py, WorldState.cs, ActionEnums.cs, IBattleView.cs,
    UsabilityEvaluator.cs, SeededRng.cs, AtomKind.cs.
[x] python scripts/audit-doc-citations.py --scope docs/architecture/combat-ai/spec-profile-schema.md
    reports no HIGH finding.
[x] I verified claims against CODE, not comments. The two dead keys were confirmed dead by reading the
    parse site (SiegeTuning.cs:351-357) and finding no reader, not by trusting the audit's C3 row.
[x] I read the surrounding section of every rule I quoted (tunables-ssot §7.1 and §7.2 in full).
[~] I tested (not assumed) any constraint I am reporting. NOT DONE — spec lane, no builds or tests
    (SPEC-BRIEF). Two claims are arguments, not measurements, and are flagged as such: "byte-identical"
    rests on the ten values being carried unchanged plus every new lever at identity; "publish.py cannot
    remove a key" rests on reading its docstring and argument list, not on running it.
[x] Nothing contradicts a §2 invariant.
[x] Corrections propagate: no doc outside this spec is edited; the dead-key decision is handed to
    module 11 by name and the replay stamp to module 8 by name.
[x] No assertion pins a derived-population count or generated text. Pinned literals are the six closed
    vocabularies' member counts and the ten migrated siege values (a migration-fidelity contract), each
    with its reason stated in the test.
[ ] Event-refreshed cache (§2.16): not applicable — the profile hub is configured once at startup and
    never invalidated. If a later module adds hot reload, that module owns the invalidation set.
[x] No acceptance criterion fixes an ordering that can vary in real play. The one fixed order — the
    four-step key fallback chain — is deterministic by construction and is tested at every step.
[x] Actor combat/derived magnitude: none produced or consumed. This module carries policy numbers, not
    actor stats; it registers no subsystem and touches no channel.
[x] Does not invent or extend a SOLID-violating parallel path. The one near-duplication risk (a second
    predicate engine) is named as Open question 1 with a recommended default that avoids it.
[~] A new rule has a registry row. PARTIAL: the rule "an AI number lives in combat-ai.v{n}.json, never in
    code" is already covered by the shipped audit (python gk-core/scripts/audit-magic-numbers.py), which will see
    Actions/Ai/ as a Policy-class path. The rule "the ten siege keys never come back" has no guard and I
    am not proposing one — SiegeKeyMigrationTests covers it as a contract test, which is the honest
    answer for a one-time migration. Stated rather than silently skipped.
```
