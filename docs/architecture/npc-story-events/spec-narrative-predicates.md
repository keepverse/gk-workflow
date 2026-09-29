# Spec: narrative-predicates

Status: **DRAFT for owner review, 2026-09-19. Spec phase; no build authorized.** Every `file:line` below was
opened in this session.

Module `narrative-predicates`, row 9 of the [npc-story-events map](../npc-story-events-map.md) (`:215`), wave 2.
Depends on `story-ledger`, `relation-ledger` and `character-registry` (the facts the new leaves read). Consumed by
`storylet-contract`'s loader (condition nodes), `storylet-selection` (eligibility and specificity) and
`choice-resolution` (per-choice conditions). Session record: `tasks/sessions/narrative-programs-spec2-20260919.json`.

## Objective

Add the six predicate leaves storylets need, each a **reviewed addition** to the closed `LeafId` enum with a
`FactReader` reader, so eligibility and per-choice conditions compile through the **one** `PredicateCompiler`:
relation band, story flag, character state, the lead's level, the antagonist's doctrine study, and the
**party-composition** leaf that `bring:{tag}` choices need (a real gap, `narrative-seed-map.md:151`). Add the
narrative condition vocabulary's compiler, which turns a seed's condition id into these leaves. Alignment
2026-09-20: the sector-kind leaf is withdrawn and the doctrine-study leaf takes its place (§1, §5).

Success looks like: each new leaf compiles, validates its argument, evaluates through the flat form and the typed
reference graph identically, and reads only a caller-supplied frame; a combat compile that meets a narrative leaf
rejects it; the combat hot path's `EntityFacts` is unchanged.

## Locked anchors

- **The leaf list is closed; adding one is a reviewed code change, because each needs a reader on `FactReader`**
  (`gk-core/src/FusionRpg.Core/Effects/Atoms/PredicateNode.cs:3-6`); today 16 leaves (`:28-46`).
- **Core reads no store**: facts are resolved at evaluation setup by whoever evaluates, never by I/O inside a leaf
  (`PredicateNode.cs:13-17`); a leaf with a named value reads a caller-resolved ordinal (`:19-26`).
- **Allocation-free, string-free evaluation** (`gk-core/src/FusionRpg.Core/Effects/Atoms/FactReader.cs:3-6`); strings are
  interned to ints at compile time (`gk-core/src/FusionRpg.Core/Effects/Atoms/CompiledAtom.cs:23-31`). The precedent for a
  string-plus-threshold leaf is `HoldsStock`: the stock id interns to a slot, the threshold rides in `Set[0]`
  (`CompiledAtom.cs:169-172` in the intern block; evaluation at `:90`).
- **Grammar bounds**: depth 4, 16 nodes (`gk-core/src/FusionRpg.Core/Effects/Atoms/PredicateCompiler.cs:23-24`;
  `effect-atom/definitions.md` §3). `subject` is required on every leaf (`definitions.md` §3).
- **Ownership**: the party-composition leaf is npc-story-events' (`narrative-seed-map.md:342`); narrative-seed may
  not add a `LeafId` (`:342`, "must not … add a `LeafId`").

## Design

### 1. The six leaves (appended; existing ordinals never move)

| `LeafId` (new, appended after `PartyDownedCount`) | Subject | Argument (after compile) | True when |
|---|---|---|---|
| `DoctrineStudying` | `Target` (the host) | none (`Value` = 0) | the host world's antagonist faction has a study in progress or a doctrine active (`spec-counter-doctrine.md` §5: `StudyMilli > 0` or `ActiveUntilTurn > turn`) |
| `RelationBandAtMost` | `Self` | `Value` = narrative slot; `Set[0]` = disposition ordinal | the referenced subject's band is that band **or friendlier** (ordinal ≤, `eager` = 0) and it is on the ladder (not joined) |
| `StoryFlagSet` | `Self` | `Value` = narrative slot | a `flag.set` fact for the flag exists in scope |
| `CharacterStateIs` | `Self` | `Value` = narrative slot; `Set[0]` = `CharacterState` ordinal | the referenced character is in that state |
| `LeadLevelAtLeast` | `Self` | `Value` = level | the summoner lead's level ≥ `Value` |
| `PartyCarriesTag` | `Self` | `Value` = narrative slot; `Set[0]` = minimum count (≥ 1) | at least that many party creatures carry the tag |

`LeafId` grows from 16 to 22 — a declaration, pinned with this reason in the leaf-count test and in the leaf table
of `docs/architecture/effect-atom/spec-predicate-tree.md` (edited in the same change, since that spec lists every
leaf and `definitions.md` wins over specs, DESIGN-GATE §1 atom row).

- **Alignment 2026-09-20 — `SectorKindIs` withdrawn, `DoctrineStudying` added.** `SectorKindIs` existed on this side
  only: no seed condition reached it, and a storylet's place is already its host kind (`world.shrine` …
  `world.wildland` are one host kind per sector slot, `spec-narrative-vocabulary.md` §2), so a sector-kind gate
  duplicated host placement. `DoctrineStudying` is the leaf `counter-doctrine` §5 filed here ("a `doctrine.studying`
  leaf") for study-site raids; it now exists on both sides (seed condition `doctrine-studying`,
  `narrative-seed/spec-storylet-vocab.md` §3.4). The count stays six, so the Boundaries' "a seventh narrative leaf" ask
  is not triggered.

- **Lead level, not a level band.** The map says "the lead's level band" (`:215`). A band would be a bucketing
  function of level — a private `f(level)` the power SSOT forbids (map principle 5, `:86-90`). The leaf compares the
  raw summoner level (`daveLevel`, the one persisted ladder input, `gk-core/src/FusionRpg.Server/Power/ServerPowerIndexProvider.cs:45-49`)
  with a threshold; no curve is involved. Recorded under Contradictions 1. Audit 2026-09-19: a seed can carry no
  number (`narrative-seed/spec-narrative-contract.md` §10), so the threshold is never in a seed: the condition names a
  gate id and `ConditionCompiler` resolves `Value` from `narrative.v{n}.json` `gates.leadLevel.{gateId}`
  (`spec-narrative-vocabulary.md` §4). A condition id for it (`lead-level-at-least`, argFamily `levelGate`) is owed to
  `storylet-vocab` §3.4; until it exists no seed reaches this leaf and only authored/legacy trees may use it.
- **References** in `RelationBandAtMost` and `CharacterStateIs` are `role:<roleId>` (resolved through the storylet's
  cast), `character:<characterId>`, or `host-faction` (the owner faction of the host sector). They are strings
  interned to a slot at compile.
- **Tags** in `PartyCarriesTag` are `element:<id>` at first ship — the one `bring` argument family
  `storylet-vocab` §3.2 declares; `trait:<id>` and `species:<id>` (`narrative-seed-ideal.md:319`) are that registry's
  "later reviewed widening" and compile only when it lands (Audit 2026-09-19).

### 2. The narrative frame — keeping combat untouched

The combat path's `EntityFacts` is a flat struct copied per candidate (`FactReader.cs:34-51`;
`gk-core/src/FusionRpg.Core/Delve/Events/EventFilters.cs:58-63`). Adding narrative fields to it would grow every combat
copy. Instead:

```csharp
namespace FusionRpg.Core.Effects.Atoms;

/// Narrative facts for one evaluation, filled by the caller from the ledger before evaluating.
/// Reference type: null on every combat path, so FactReader's combat copy grows by one pointer only.
public sealed class NarrativeFrame
{
    public const int SlotCount = PredicateCompiler.MaxNodes;   // structural: one slot per possible leaf
    public int DoctrineStudying { get; init; }                 // Alignment 2026-09-20: 1 while the host world's study/doctrine is live
    public int LeadLevel { get; init; }
    public int[] Slots { get; } = new int[SlotCount];          // per compiled predicate, by interned slot
}

public struct FactReader
{
    // existing fields unchanged (FactReader.cs:61-71)
    readonly NarrativeFrame? _narrative;
    public FactReader(EntityFacts self, EntityFacts target, NarrativeFrame? narrative) : this(self, target) =>
        _narrative = narrative;
    public int NarrativeSlot(int slot) => _narrative is { } n && slot >= 0 && slot < NarrativeFrame.SlotCount
        ? n.Slots[slot] : int.MinValue;                        // absent → every narrative leaf evaluates false
    public int DoctrineStudying() => _narrative?.DoctrineStudying ?? 0;
    public int LeadLevel() => _narrative?.LeadLevel ?? int.MinValue;
}
```

The absent-frame answer is **false, not throwing** — the posture `FactReader.StockQty` already takes for an
unresolved slot (`FactReader.cs:95-101`). It is a backstop only: §3 makes a narrative leaf uncompilable outside a
narrative compile.

`NarrativeFrame.SlotCount` is structural: a tree has at most `MaxNodes` leaves (`PredicateCompiler.cs:24`), so it
cannot intern more distinct references than that — the same argument `FactReader`'s four stock slots make
(`FactReader.cs:16-21`).

### 3. Compiling

`PredicateCompiler.TryCompile` (`PredicateCompiler.cs:34-51`) gains one optional parameter,
`NarrativeCompileContext? narrative`. It carries two resolvers — `DispositionOrdinal(string)` and
`CharacterStateOrdinal(string)` — plus the `levelGate` resolver `LeadLevelGate(string gateId)` over
`narrative.v{n}.json` `gates.leadLevel`, and a per-compile slot interner (Alignment 2026-09-20: the sector-kind
resolver left with `SectorKindIs`). Rules:

- `narrative` null and the tree contains a narrative leaf → rejection `AtomRejectionReason.LeafNotInContext`
  (new member, reviewed; `gk-core/src/FusionRpg.Core/Effects/Atoms/AtomRejection.cs:7`). Every atom, action and consumable
  compile passes null, so no combat or action predicate can reference a story fact.
- `ValidateLeaf` arms: `DoctrineStudying` needs `Value = 0`; `LeadLevelAtLeast` needs `Value ≥ 0`; `RelationBandAtMost`,
  `StoryFlagSet`, `CharacterStateIs`, `PartyCarriesTag` need non-empty `Text`; `PartyCarriesTag`'s threshold ≥ 1;
  subject must be the one §1 names (the other is `AmbiguousSubject`).
- `FlatPredicate.Build`'s intern block (`CompiledAtom.cs:111`, arms at `:166-172`) interns `Text` to a narrative
  slot and carries the threshold in `Set[0]`, as `HoldsStock` does. The compiled predicate exposes
  `NarrativeSlots: IReadOnlyList<(LeafId, string Text)>` so the caller knows what to fill.
- The typed reference graph (`PredicateCompiler.cs:188-208`) gains the same six nodes, so the existing equivalence
  fuzz between the flat and typed forms covers them.

### 4. Filling the frame

`NarrativeFrameBuilder.Fill(compiled.NarrativeSlots, NarrativeFactView view)` (new, Core, pure) writes one int per
slot:

| Leaf | Slot value |
|---|---|
| `RelationBandAtMost` | the reference's band ordinal from `RelationLedger.Derive`, or `int.MaxValue` when joined or uncast (never matches) |
| `StoryFlagSet` | 1 if a `flag.set` fact for the flag exists in the scope the flag belongs to, else 0 |
| `CharacterStateIs` | the reference's `CharacterState` ordinal, or −1 when uncast |
| `PartyCarriesTag` | the count of party creatures carrying the tag |

`DoctrineStudying` and `LeadLevelAtLeast` read frame fields, not slots: `NarrativeFrame.DoctrineStudying` is filled
from `counter-doctrine`'s per-world study state for the host's world (Alignment 2026-09-20) and `LeadLevel` from the
summoner level.

`NarrativeFactView` is a read model the caller builds once per pulse from `ListStoryFacts`, the cast and the party
(`storylet-selection`); it performs no I/O itself. A frame is filled per candidate storylet and discarded — a value,
not a cache.

### 5. The condition compiler

Seeds write conditions from the closed condition vocabulary (`conditions.v1.json`,
`spec-narrative-vocabulary.md` §1), not raw leaves (`narrative-seed-ideal.md:305`). `ConditionCompiler` (new) maps a
condition to either a `PredicateNode.Leaf` (with names resolved to ordinals, the importer's job per
`PredicateNode.cs:22-26`) or a `RoleGate`. Audit 2026-09-19: the seed's condition is the per-slot object
`{ "id": "<condition id>", "arg": "<named value or none>" }` (`narrative-seed/spec-narrative-contract.md` §5,
`spec-storylet-vocab.md` §3.4) — not the `{cond, subject, args}` node this section first invented, which no seed could
emit. The mapping at first ship:

**The one mapping table (Alignment 2026-09-20).** Seed names are the authored surface
(`narrative-seed/spec-storylet-vocab.md` §3.2 intrinsic gates and §3.4 condition ids); `LeafId` names are this
module's. Every seed name maps to exactly one runtime target, and every narrative leaf below is reached by a seed name,
so no leaf exists on one side only. The `LeafId` column covers the 16 existing members (`PredicateNode.cs:28-46`) only
where a seed reaches them; the other built leaves are atom and action vocabulary that seeds never name.

| Seed name (where) | `usableIn` | Compiles to (`LeafId` or runtime check) | Subject and argument |
|---|---|---|---|
| `none` (condition) | slot | no gate | — |
| `danger-band-is` `{arg: band}` (condition) | slot | built `BandIs` (`PredicateNode.cs:42`) | host; band name → ordinal |
| `disposition-is` `{arg: band}` (condition) | slot | new `RelationBandAtMost` | the storylet's first declared non-`forbidden` role (seed rule); band name → disposition ordinal |
| `character-state-is` `{arg: state}` (condition) | slot | new `CharacterStateIs` | same role rule; state wire id → `CharacterState` ordinal |
| `story-flag-set` `{arg: flagId}` (condition) | slot, eligibility | new `StoryFlagSet` | `flag:<flagId>` interned to a slot |
| `lead-level-at-least` `{arg: gateId}` (condition) | slot | new `LeadLevelAtLeast` | gate id → `Value` from `narrative.v{n}.json` `gates.leadLevel.{gateId}`; an unknown gate rejects |
| `doctrine-studying` `{arg: none}` (condition) | eligibility | new `DoctrineStudying` | the host world; no argument |
| `role-cast` `{arg: roleId}` (condition) | slot | a `RoleGate` (`cast-resolver` decides it; not a leaf) | the named optional role |
| `use` + `param: <supplyTag>` (choice kind, intrinsic gate) | slot | built `HoldsStock` (`PredicateNode.cs:41`) | the supply tag |
| `bring` + `param: <element>` (choice kind, intrinsic gate) | slot | new `PartyCarriesTag` | `element:<id>`, threshold 1 |
| `offer` + `param: <stock>` (choice kind, intrinsic gate) | slot | not a leaf: the runtime's affordability check on the priced cost (`storylet-vocab` §3.2) | — |

An eligibility list compiles to one `And` of its leaves (a single entry compiles to the leaf itself), inside the
depth-4 / 16-node grammar bound. A slot condition compiles to one leaf or `RoleGate`, ANDed with the choice kind's
intrinsic gate. The seed's `proposedLeaves` block names exactly the six new leaves above; its test and this spec's
leaf-count test move together.

Legacy and authored rows may still carry a `definitions.md` §3 tree in `eligibility`; `storylet-contract`'s loader
reads those through `AtomJson.TryReadPredicate` (`gk-core/src/FusionRpg.Core/Effects/Atoms/AtomJson.cs:190`). `AtomJson` is not
taught the condition object: atom content never contains one.

## Data shapes

- No table, no tuning key.
- Seed: the per-slot `{id, arg}` condition object, ids from `conditions.v1.json` (Audit 2026-09-19).

## Numeric types

| Quantity | Type | Why |
|---|---|---|
| leaf `Value`, `Set[0]`, frame slots | `int` | `PredicateNode.Leaf.Value` is `int` (`PredicateNode.cs:79-84`); every value is an ordinal, a count or a level (levels fit `int`: `ServerPowerIndexProvider.cs:48` narrows the stored level with `checked`) |
| sentinels `int.MinValue` / `int.MaxValue` | `int` | answers meaning "absent", chosen so no comparison can match; commented as structural |

## SOLID notes

- **S:** one predicate engine; the narrative leaves are leaves, not a second evaluator.
- **O:** extended through the closed-list process the enum's own comment requires (`PredicateNode.cs:3-6`).
- **I:** combat callers see one extra optional constructor parameter; `EntityFacts` does not change.
- **D:** leaves read a frame; the frame is filled from read models; nothing in `Effects.Atoms` imports a narrative
  or Data type (a reflection test asserts `FusionRpg.Core.Effects.Atoms` references no `FusionRpg.Core.Narrative`
  type except through the `NarrativeCompileContext` delegates).

## Commands

```powershell
.\scripts\verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/Effects/Atoms/PredicateNode.cs','gk-core/src/FusionRpg.Core/Effects/Atoms/PredicateCompiler.cs','gk-core/src/FusionRpg.Core/Effects/Atoms/CompiledAtom.cs','gk-core/src/FusionRpg.Core/Effects/Atoms/FactReader.cs','src/FusionRpg.Core/Narrative/Predicates/ConditionCompiler.cs','tests/FusionRpg.Core.Tests/Narrative/Predicates/NarrativeLeafTests.cs') -Session <session-id>
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~Predicate|FullyQualifiedName~Atoms|FullyQualifiedName~Narrative.Predicates|FullyQualifiedName~Delve.Events"
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~Battle"      # combat evaluation untouched
```

`Effects/Atoms` sits under the shared hot path, so the build task also runs the atom benchmark guard
(`gk-core/tests/FusionRpg.Core.Atoms.Tests/Atoms/AtomBenchGuardTests.cs`) in the same command.

## Structure

```
gk-core/src/FusionRpg.Core/Effects/Atoms/PredicateNode.cs        (edited: six LeafId members appended)
gk-core/src/FusionRpg.Core/Effects/Atoms/PredicateCompiler.cs    (edited: context parameter, ValidateLeaf arms, typed nodes)
gk-core/src/FusionRpg.Core/Effects/Atoms/CompiledAtom.cs         (edited: intern and evaluate arms, NarrativeSlots)
gk-core/src/FusionRpg.Core/Effects/Atoms/FactReader.cs           (edited: NarrativeFrame reference and readers)
gk-core/src/FusionRpg.Core/Effects/Atoms/AtomRejection.cs        (edited: LeafNotInContext)
docs/architecture/effect-atom/definitions.md             (edited: LeafNotInContext in the rejection-reason list, :459 —
                                                          Audit 2026-09-19: definitions.md wins over any spec, so the
                                                          closed list it states must move in the same change)
src/FusionRpg.Core/Effects/Atoms/NarrativeFrame.cs       (new)
src/FusionRpg.Core/Narrative/Predicates/ConditionCompiler.cs     (new)
src/FusionRpg.Core/Narrative/Predicates/NarrativeFrameBuilder.cs (new)
docs/architecture/effect-atom/spec-predicate-tree.md     (edited: leaf table)
tests/FusionRpg.Core.Tests/Narrative/Predicates/NarrativeLeafTests.cs   (new)
```

## Testing strategy

- **Per leaf:** compiles with a valid argument; rejects a bad one (empty text, negative value, zero threshold,
  wrong subject) with the compiler's own reason; evaluates true and false against hand-filled frames.
- **Flat equals typed:** the existing equivalence fuzz includes the six leaves (random trees within 4/16, random
  frames): both forms agree on every case.
- **Context rule:** a narrative leaf compiled with no `NarrativeCompileContext` rejects `LeafNotInContext`; every
  existing atom, action and event test still passes (they pass no context and contain no narrative leaf).
- **Absent frame:** a combat `FactReader` evaluates a (hypothetically compiled) narrative leaf false and does not
  throw.
- **Combat untouched:** battle goldens byte-identical; `EntityFacts` has the same members; the atom bench guard is
  within its budget.
- **Slot bound:** a tree with 16 distinct references compiles; interning never exceeds `SlotCount`.
- **Condition compiler:** each condition id in a fixture `conditions.v1.json` compiles to its leaf or role gate;
  an unknown id, an unknown band name, an unknown state name or an unknown gate id rejects naming it; an
  eligibility-only id on a slot and a slot-only id in an eligibility list reject (Alignment 2026-09-20).
- **Mapping closure (Alignment 2026-09-20):** the set of leaves named in the §5 table equals the seed file's
  `proposedLeaves` plus the built leaves it names, and every new `LeafId` member appears in the table.
- **Leaf count:** `Enum.GetValues<LeafId>().Length == 22`, commented as a closed vocabulary with this spec as the
  reason.

## Success criteria

1. Six leaves, each with a reader, validation, both compiled forms and tests. 2. No narrative leaf compiles in a
non-narrative context. 3. Combat hot path and goldens unchanged. 4. `spec-predicate-tree.md` lists 22 leaves. 5.
The condition vocabulary compiles through one compiler.

## Boundaries

- **Always:** append leaves; read a caller-filled frame; resolve names to ordinals at compile.
- **Ask first:** any change to `EntityFacts`; a leaf that needs I/O; a seventh narrative leaf.
- **Never:** reorder `LeafId`; a level-band curve; a narrative leaf in an atom or action predicate; a second
  predicate evaluator.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `LeafId.{RelationBandAtMost, StoryFlagSet, CharacterStateIs, LeadLevelAtLeast, DoctrineStudying, PartyCarriesTag}` (Alignment 2026-09-20) | `ConditionCompiler`, seeds (through condition ids and intrinsic gates) |
| `NarrativeCompileContext`, `ICompiledPredicate.NarrativeSlots` | `storylet-contract` loader, `storylet-selection` |
| `NarrativeFrame`, `NarrativeFrameBuilder.Fill`, `NarrativeFactView` | `storylet-selection`, `choice-resolution` |

## Contradictions found (report; not fixed here)

1. **"The lead's level band."** Map row 9 (`:215`) and ideal §6.2 (`npc-story-events-ideal.md:335-337`) say a level
   band. This spec compares the raw level instead, because a band is a new `f(level)`; the map's wording should read
   "the lead's level".

## Open questions

None for the owner.

## Design-gate checklist

```
[x] Subsystems: effect atoms (predicate tree), FactReader, narrative facts.
[x] Session boundary recorded (narrative-programs-spec2-20260919).
[x] Read this session: definitions.md §3; PredicateNode.cs, PredicateCompiler.cs, FactReader.cs, CompiledAtom.cs
    (FlatPredicate), AtomJson.cs, AtomRejection.cs, EventFilters.ByEligibility; spec-predicate-tree.md leaf table.
[x] Every claim cites file:line.
[x] Closed vocabulary widened as a reviewed change with its count and reason.
[x] Perf: combat EntityFacts unchanged; one pointer added to FactReader; bench guard in the command.
[x] No cache (frames are per-evaluation values). No population pinned. No actor number.
[x] No parallel path: one compiler, one evaluator.
[ ] Registry row: the context rule is enforced by the compiler itself; no new guard script. (Audit 2026-09-19:
    row proposed below.)
```

## Standards audit (2026-09-19)

| # | Severity | Finding | Status |
|---|---|---|---|
| 1 | high | The condition grammar (`{cond, subject, args}`) did not match the seed's `{id, arg}` condition object, and the example id `relation-at-least` is not a `conditions.v1.json` member (`disposition-is` is) — no generated seed could have compiled | **Fixed:** §5 reads `{id, arg}` with a mapping table per first-ship id |
| 2 | medium | `LeadLevelAtLeast` needed a numeric threshold that the seed contract forbids (no digit, no number) and no condition id reached it | **Fixed:** named gates in tuning (`gates.leadLevel`); the seed-side condition id is a filed propagation |
| 3 | medium | `LeafNotInContext` widens `AtomRejectionReason`, whose closed list `effect-atom/definitions.md` states (`:459`) and which wins over specs (DESIGN-GATE atom row); the Structure edited only `spec-predicate-tree.md` | **Fixed:** `definitions.md` added to Structure |
| 4 | medium | Leaf names differ from `storylet-vocab` §3.4's `proposedLeaves` (`RelationBandIs`/`StoryFlagIs` there, `RelationBandAtMost`/`StoryFlagSet` here); that registry's own test asserts every named leaf is built or proposed | **Closed — Alignment 2026-09-20:** the seed side now uses these names and §5 holds the one mapping table |
| 5 | low | `PartyCarriesTag` claimed `trait:`/`species:` tags that `storylet-vocab` §3.2 defers | **Fixed:** `element` only at first ship |
| 6 | low | Map citations one line early (`:214`); map row 9 still said "level band" | **Fixed** (map row 9 now "the lead's level") |

Verified: `LeafId` has 16 members today (`PredicateNode.cs:28-46`, counted), so 22 after this module is a
declaration. Checked and clean: one compiler and evaluator, combat `EntityFacts` untouched, narrative leaves refused
outside a narrative compile, `int` ordinals, no cache, no population pin.

**Proposed enforcement-registry row:** `ns-narrative-leaf-context` — no narrative leaf in an atom, action or
consumable predicate; guard: the compiler's `LeafNotInContext` rejection plus `NarrativeLeafTests`' context test.

## Cross-lane alignment (2026-09-20)

Alignment 2026-09-20. The seed side (`narrative-seed/spec-storylet-vocab.md` §3.4) owns the authored condition ids;
this module owns `LeafId`. §5 now holds the one table mapping every seed name (condition ids and the intrinsic gates
of `use`, `bring`, `offer`) to its leaf or runtime check. Leaves that existed on one side only were resolved:
`SectorKindIs` is withdrawn (host kinds already place a storylet); `CharacterStateIs` and `LeadLevelAtLeast` gained
seed condition ids; `DoctrineStudying` (filed by `counter-doctrine`) was added on both sides. The count stays at six
new leaves (`LeafId` 16 → 22). The widened storylet's `eligibility` list compiles here as one `And`
(`spec-storylet-contract.md` §3).
