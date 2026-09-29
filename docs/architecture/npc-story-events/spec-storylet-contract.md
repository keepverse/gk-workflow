# Spec: storylet-contract

Status: **DRAFT for owner review, 2026-09-19. Spec phase; no build authorized.** Every `file:line` below was
opened in this session.

Module `storylet-contract`, row 3 of the [npc-story-events map](../npc-story-events-map.md) (`:209`), wave 1.
Depends on `storylet-reseam` (the engine namespace) and `narrative-vocabulary` (catalogs). Reads the storylet seed
contract that narrative-seed's `narrative-contract` module defines (`narrative-seed-ideal.md` §6.2,
`narrative-seed-map.md:209`). Consumed by `cast-resolver`, `storylet-selection`, `narrative-text`,
`choice-resolution` and every host. Gates **G1** and **G2** (`npc-story-events-map.md:297-298`). Session record:
`tasks/sessions/narrative-programs-spec2-20260919.json`.

## Objective

Teach the one engine to load the **widened storylet**: player-facing choices, each with its own condition and
outcomes, roles, hosts, a revision, provenance, arc links and keyed text — while today's 54 Delve events keep
loading in their legacy shape until narrative-seed regenerates them. Lift the loader's refusal of eligibility
trees, and make the runtime preflight refuse what the committed corpus silently gets away with today.

Success looks like: `EventSeedFile.LoadAll` reads today's corpus unchanged and a fixture corpus in the widened
shape; a real eligibility tree loads and compiles; preflight **fails** on a dangling `chainRef`, a role used but
undeclared, a storylet without exactly one `leave`, a lose-lose or dominated choice, a digit in text, and an
id that reuses a tombstone; a storylet's canonical form hashes identically on every load.

## Locked anchors

- The shape widens, it is not replaced (map locked assumption 2, `:139-141`; `EventRow`,
  `gk-core/src/FusionRpg.Core/Delve/Events/EventRow.cs:28-37`, moved by `storylet-reseam`).
- The loader refusal to lift: `EventSeedFile.cs:40-44` throws `NotSupportedException` on any non-null
  `eligibility`.
- The catalog **already** compiles a tree when it gets one: `PredicateCompiler.TryCompile` at
  `gk-core/src/FusionRpg.Core/Delve/Events/EventCatalog.cs:187`; the grammar bound is depth 4, 16 nodes
  (`gk-core/src/FusionRpg.Core/Effects/Atoms/PredicateCompiler.cs:23-24`; `effect-atom/definitions.md` §3). The JSON reader
  exists: `AtomJson.TryReadPredicate` (`gk-core/src/FusionRpg.Core/Effects/Atoms/AtomJson.cs:190`).
- **NS7, approved 2026-09-19:** every storylet carries exactly one `leave` (`npc-story-events-map.md:405`,
  `:414-418`), superseding `leave` only on `kind: story` (`gk-core/src/FusionRpg.Core/Delve/Events/EventChoices.cs:15-31`).
- The seed-side validators are narrative-seed's (`narrative-seed-map.md:211`). The runtime **repeats** the
  structural ones at load so it never trusts the tool — the event-deck precedent for supply tags
  (`party-dungeon/spec-event-deck.md` §9, `:266-280`).
- Revision pinning and tombstones (ideal §11 item 3; `narrative-seed-ideal.md:637-638`).

## Design

### 1. The widened seed (read; authored by narrative-seed)

Generated storylets live under `data/seed/narrative/storylets/` (new); authored storylets under
`data/seed/narrative/authored/storylets/` (`narrative-seed/spec-narrative-contract.md` §2; ideal §11 item 10). Both
pass the same loader. Audit 2026-09-19: the example below was re-aligned field by field to
`spec-narrative-contract.md` §2–§5, the seed side this loader reads — it had drifted (`storyletId`, a `tombstone`
bool, `choiceKind`/`param`, a predicate tree as a choice condition, an empty `leave` outcome list, no envelope). Each
file is the standard envelope `{schemaVersion, kind: "storylet", _meta, entries: [one seed]}` (§2 there). Fields the
runtime reads from the one entry:

```jsonc
{
  "id": "storylet.<body>",                      // PLANNED; never reused; authored ids are "storylet.authored-..."
  "revision": 3,                                // DERIVED, >= 1; bumped by narrative-emit when content changes
  "status": "live",                             // "live" | "tombstone" (withdrawn; only resolvable through a pin)
  "provenance": "generated",                    // DERIVED from the path: "generated" | "authored"
  "tokens": ["role_keeper"],                    // declared tokens (narrative-text closure)
  "pattern": "pattern.persuade-leave-offer",    // a storylet-vocab choice-pattern id (read, not used for selection)
  "hosts": ["world.market"],                    // HostKindCatalog ids (>= 1); each admits `kind`
  "kind": "bargain",                            // the storylet kind vocabulary (today's event kinds)
  "climate": "none",                            // an element or "none"
  "repeatScope": "once-per-player",
  "arcRef": "arc.<body>", "arcLink": "<link id>",   // or both "none" for texture
  "chainRef": "none",                           // DERIVED from the arc; legacy rows carry a free id
  "roles": [ { "roleId": "keeper", "kind": "required", "requires": ["<storylet-vocab 3.6 family>:<value>"] } ],
  "eligibility": null,                          // or [{ "id": "story-flag-set", "arg": "<flag>" }, ...] (arc flagsRead)
  "teaches": ["talk-verbs"],                    // storylet-vocab 3.8 values, or []
  "choices": [                                  // one per pattern slot, in slot order; the slot index is the position
    { "choiceKind": "persuade", "param": "none", "condition": { "id": "none", "arg": "none" },
      "label": { "key": "ns.storylet.<body>.choices.0.label.<h8>", "text": "..." },
      "outcomes": [ { "ordinal": "good",
                      "consequence": { "kind": "relation.shift", "ref": "role:keeper", "param": "helped" },
                      "effects": [ { "family": "...", "powerBand": "..." } ], "dropBand": "staple",
                      "result": { "key": "ns.storylet.<body>.choices.0.outcomes.0.result.<h8>", "text": "..." } } ] },
    { "choiceKind": "leave", "param": "none", "condition": { "id": "none", "arg": "none" }, "label": { "...": "..." },
      "outcomes": [ { "ordinal": "nothing", "consequence": { "kind": "none", "ref": null, "param": "none" },
                      "effects": [], "dropBand": "none", "result": { "...": "..." } } ] },   // the const leave outcome
    { "choiceKind": "offer", "param": "souls", "condition": { "id": "disposition-is", "arg": "open" }, "...": "..." }
  ],
  "name":      { "key": "ns.storylet.<body>.name.<h8>", "text": "..." },
  "situation": { "key": "ns.storylet.<body>.situation.<h8>", "text": "..." }
}
```

- Alignment 2026-09-20: a widened seed's gates are its per-slot `condition` objects and its storylet-level
  `eligibility` list — both `{id, arg}` objects from `conditions.v1.json`, never trees — plus its roles and its arc
  position. `ConditionCompiler` (`spec-narrative-predicates.md` §5) compiles each at load: a slot condition into one
  leaf or a `RoleGate`; the `eligibility` list (`null`, or `story-flag-set` / `doctrine-studying` conditions, the
  `usableIn: eligibility` ids of `narrative-seed/spec-storylet-vocab.md` §3.4) into one `And` of leaves, carried as
  `EventRow.Eligibility`. The 2026-09-19 audit said a widened seed has no `eligibility`; the seed contract has one
  (`narrative-seed/spec-narrative-contract.md` §5), so that sentence is withdrawn. A **legacy** row may still carry a
  `definitions.md` §3 tree in `eligibility`, which §3 below reads through `AtomJson`; an **authored** storylet uses the
  same `{id, arg}` shape as a generated one (one contract, `spec-narrative-contract.md` §2).
- The C# names in §2 map the seed names one to one: `id` → `EventRow.EventId`; `status` (`live · tombstone`) →
  `.Tombstone`; `choices[].choiceKind` → `StoryletChoice.ChoiceKind`; `choices[].param` → `.Param` (`"none"` → `null`);
  the array position → `.Slot`; `arcLink` → `.ArcLink` (a link id string); `teaches` → `.Teaches`; `tokens` →
  `.Tokens`. Alignment 2026-09-20: the 2026-09-19 audit had written the choices as `kind`/`arg` — the seed's names
  before the seed's own audit renamed them to `choiceKind`/`param`; the example now matches the seed as it stands.
  `_meta` and `_provenance` are seedsmith provenance and are not loaded. A test loads the seed side's own
  `validate_entry` green fixtures, and one red fixture per seed rule the loader repeats.
- A **tombstone row** is the seed contract's closed five-field shape (`id`, `revision`, `status: tombstone`,
  `provenance`, `withdrawnReason`; `spec-narrative-contract.md` §11); the loader accepts it without the live fields and
  it loads as a row with `Tombstone: true` and nothing drawable.

A **legacy** row is one without `choices` (today's 54 files under `gk-data/packs/fusion/data/seed/dungeon/events/`). It loads as
today: event-level `outcomes[]`, choices presented by `EventChoices.Presented` (`EventChoices.cs:23-32`). A row
is widened or legacy as a whole; a mixed row is a load refusal.

**The consequence object.** Owner ruling 2026-09-19 (round 3): an outcome's `consequence` is the one object
`narrative-seed/spec-narrative-contract.md` §5 owns — `{kind, ref, param}` — and this loader reads it **as-is**:
`kind` a `ConsequenceKindCatalog` id; `ref` the target or `null` (`role:<roleId>`, `character:<characterId>`,
`flag:<flagId>`, `quest:<questId>`, `scene:<sceneId>`, `host:wild`, per kind); `param` a closed modifier (for
`relation.shift` the relation fact kind `met · helped · refused · betrayed · spared`, `none` otherwise). Which kinds
require `ref` and which `param` values each allows are declared in `narrative-seed/spec-storylet-vocab.md` §3.5 and
read through `ConsequenceKindCatalog`, never restated here. `consequenceRef` and the proposed `consequenceParam`
are retired. A legacy row keeps today's plain string consequence (`EventOutcomeRow.Consequence`,
`gk-core/src/FusionRpg.Core/Delve/Events/EventRow.cs:17-18`) and loads as `{kind: <that string>, ref: null, param: none}`.

### 2. C# shape

```csharp
namespace FusionRpg.Core.Narrative.Storylets;

public enum StoryletProvenance { Generated, Authored }
public enum RoleKind { Required, Optional, Forbidden }

public sealed record TextRef(string Key, string Text);                 // keyed text, rendered by narrative-text
public sealed record StoryletRole(string RoleId, RoleKind Kind, IReadOnlyList<string> Requires);
// Owner ruling 2026-09-19 (round 3): the seed's {kind, ref, param} object, loaded as-is.
public sealed record StoryletConsequence(string Kind, string? Ref, string Param);   // Param: "none" unless the kind lists params
public sealed record StoryletOutcome(
    string Ordinal, string DropBand, StoryletConsequence Consequence,
    IReadOnlyList<EventEffectRef> Effects, TextRef? Result);
public sealed record StoryletChoice(
    int Slot, string ChoiceKind, string? Param, PredicateNode? Condition, string? RoleGate,
    TextRef Label, IReadOnlyList<StoryletOutcome> Outcomes);
// Slot = the array position; ChoiceKind/Param = the seed's choiceKind/param; Condition/RoleGate = the compiled
// {id, arg} condition (Alignment 2026-09-20).

// EventRow widens by appended, defaulted members so every existing constructor call still compiles.
public sealed record EventRow(
    string EventId, string Kind, string? Theme, string? ClimateAffinity, string RepeatScope,
    PredicateNode? Eligibility, IReadOnlyList<EventOutcomeRow> Outcomes,   // widened: the compiled eligibility list
    string? SupplyOverride, string? ChainRef)
{
    public long Revision { get; init; }                                   // 0 for legacy rows
    public StoryletProvenance Provenance { get; init; } = StoryletProvenance.Generated;
    public bool Tombstone { get; init; }
    public IReadOnlyList<string> Hosts { get; init; } = Array.Empty<string>();   // legacy: derived from Kind (§3)
    public IReadOnlyList<StoryletRole> Roles { get; init; } = Array.Empty<StoryletRole>();
    public IReadOnlyList<StoryletChoice>? Choices { get; init; }          // null = legacy
    public string? ArcRef { get; init; }
    public string? ArcLink { get; init; }                                 // Audit 2026-09-19: a link id (seed §5), not an int
    public IReadOnlyList<string> Tokens { get; init; } = Array.Empty<string>();    // seed `tokens` (narrative-text closure)
    public IReadOnlyList<string> Teaches { get; init; } = Array.Empty<string>();   // Owner ruling 2026-09-20: storylet-vocab 3.8
    public TextRef? Name { get; init; }
    public TextRef? Situation { get; init; }
    public bool IsLegacy => Choices is null;
    public bool IsNegative { get; init; }                                  // derived at load (§5), never authored
}
```

`Condition` compiles through the same `PredicateCompiler`; `RoleGate` holds a `role:<roleId>` requirement that
`cast-resolver` checks instead of a leaf (the condition vocabulary compiles *"to `PredicateNode` leaves or a role
requirement"*, `narrative-seed-ideal.md:305`). `EventCatalog` gains `ChoiceConditionFor(eventId, slot)` beside
`EligibilityFor` (`EventCatalog.cs:84-85`).

### 3. Loader changes

- `EventSeedFile.LoadAll` stops throwing on a tree: it reads a legacy row's `eligibility` tree through
  `AtomJson.TryReadPredicate`, and every widened `choices[].condition` and widened `eligibility` list (`{id, arg}`
  objects) through `ConditionCompiler` (`spec-narrative-predicates.md` §5), and carries the compiled result on the row
  (Audit 2026-09-19: conditions are condition ids, not trees; Alignment 2026-09-20: the widened `eligibility` list
  too). A tree or condition that fails to parse or compile is a load rejection naming the file and rule id, not a
  thrown `NotSupportedException`.
- A widened file is the seed envelope: `schemaVersion`, `kind: "storylet"`, `_meta`, and `entries` holding exactly
  one seed (`narrative-seed/spec-narrative-contract.md` §2). Anything else is `storylet.envelope`.
- It reads both directories — `gk-data/packs/fusion/data/seed/dungeon/events/` (legacy) and `data/seed/narrative/storylets/` (widened)
  — into one row list, so there is one catalog, not a legacy catalog beside a new one.
- Legacy rows get `Hosts` derived from `Kind` through the Delve's existing room-kind fit
  (`gk-core/src/FusionRpg.Core/Delve/Events/EventFilters.cs:16-24`, moved to the Delve adapter): `curio` → `delve.curio`,
  `bargain` → `delve.merchant`, `story` → `delve.wild`, `encounter-event` → `delve.rest` and every kind also fits
  `delve.unknown`. This is the only place a legacy row learns hosts, and it goes away when
  narrative-seed's `delve-event-regen` retires the legacy directory (`narrative-seed-map.md:221`).
- Text: widened rows carry `TextRef`s. Token closure is checked by `narrative-text`'s load validator (it owns the
  grammar); this module checks only that no text field contains an ASCII digit (`narrative-seed-ideal.md:344`).

### 4. Canonical form, revision and tombstones

- `StoryletCanonical.Serialize(EventRow)` (new) writes one canonical JSON form (ordinal key order, no whitespace,
  trees in `definitions.md` §3 form) and `StoryletCanonical.Hash` is its SHA-256. The same bytes are what
  `story-ledger` stores in a pin (`spec-story-ledger.md` §4) and what `StoryletCanonical.Parse` loads back through
  this loader, so a pinned revision is validated by the same rules as a live one.
- `EventCatalog.Resolve(id)` returns the current revision; a tombstoned id resolves to a row with
  `Tombstone: true` that is never drawable. A live (non-tombstone) row whose id equals a tombstone's id at a
  **different** revision lineage is impossible by narrative-seed's rule (`ids are never reused`); the runtime
  repeats it as a load refusal `storylet.id-reused`.
- Legacy rows have `Revision = 0` and cannot be pinned (they have no arcs).

### 5. Preflight, widened

New rules join `EventDeckPreflight.Run` (`gk-core/src/FusionRpg.Core/Delve/Events/EventDeckPreflight.cs:182-194`) under the
existing `EventRules` namespace (`EventCatalog.cs:8-51`):

| Rule id (new unless noted) | Refuses | Applies to |
|---|---|---|
| `event.chain-ref-dangling` | a `chainRef` or `arcRef` link that names no catalog row. Today `CheckChainRefs` skips it *"silently"* (`EventDeckPreflight.cs:51-55`, the skip at `:64-65`) | all rows |
| `storylet.choice-count` | fewer than 2 or more than 4 choices | widened |
| `storylet.leave-count` | not exactly one `leave` (NS7) | widened |
| `storylet.lose-lose` | no always-eligible non-`leave` choice with an outcome whose ordinal is not `bad` | widened |
| `storylet.dominated-choice` | a choice whose outcome ordinals are all at or below another choice's, at no lower cost and no stricter condition | widened |
| `storylet.conditional-below-unconditional` | a conditional choice (`use`, `bring`, `offer`) whose best ordinal is below the best unconditional choice's | widened |
| `storylet.role-undeclared` | a `role:<id>` in a `RoleGate`, a `consequence.ref` or a text token not declared in `roles[]` | widened |
| `storylet.consequence-shape` | a `consequence` that is not exactly `{kind, ref, param}` (a legacy string is legal only on a legacy row); an unknown `kind` (Owner ruling 2026-09-19 (round 3)) | widened |
| `storylet.consequence-ref-missing` | a kind whose `refForms` requires a target (`relation.shift`, `story.flag`, `quest.offer`, `scene.play`, `recruit`) with `ref: null`, or a `ref` whose prefix is not one of that kind's `refForms` | widened |
| `storylet.consequence-ref-forbidden` | a non-null `ref` on a kind with no `refForms` (`none`, `loot`, `encounter`, `scout`, `battle.start`, `doctrine.setback`) | widened |
| `storylet.consequence-param` | a `param` outside the kind's `params`, including `none` on `relation.shift` | widened |
| `storylet.digit-in-text` | an ASCII digit in any `TextRef.Text` | widened |
| `storylet.provenance-path` | `authored` outside the authored path, or `generated` inside it | widened |
| `storylet.id-reused` | a live row reusing a tombstoned id | widened |
| `storylet.mixed-shape` | a row with both event-level `outcomes` and `choices` | all |
| `storylet.envelope` | a widened file that is not `{schemaVersion, kind: "storylet", _meta, entries: [one seed]}` (Alignment 2026-09-20) | widened |
| `storylet.status` | a `status` outside `live · tombstone`, or a tombstone row that is not the seed contract's five-field shape (Alignment 2026-09-20) | widened |
| `storylet.condition-unknown` | a `condition` or `eligibility` entry whose `id` is not a `conditions.v1.json` member or whose `arg` is outside that id's `argFamily` — `ConditionCompiler`'s refusal (Alignment 2026-09-20) | widened |
| `storylet.condition-context` | a slot-only condition in `eligibility`, an eligibility-only condition (`doctrine-studying`) on a slot, or any condition other than `none` on an unconditioned slot (Alignment 2026-09-20; `storylet-vocab` §3.4 `usableIn`) | widened |
| `storylet.teaches` | a `teaches` value not in `teaches.v1.json`, one whose `carriers` exclude `storylet`, or one whose `requires` the row does not meet (Owner ruling 2026-09-20) | widened |
| `event.room-kind-is-boss-forbidden` (existing, `EventDeckPreflight.cs:92-104`) | a storylet that gates the boss | all |

Ordinals rank `good > mixed > bad > nothing` — the order `OutcomeResolver` already uses
(`gk-core/src/FusionRpg.Core/Delve/Events/OutcomeResolver.cs:46`). "Always eligible" means a choice with no `Condition` and
no `RoleGate`. The map also names "an unresolved pool id" (`:209`); `EventDeck.Build` already refuses one
(`EventDeck.cs:165-167`), so the rule exists and is not rebuilt.

`IsNegative` is derived at load: true when no always-eligible non-`leave` choice has a `good` outcome. It feeds
`storylet-selection`'s fairness rule and is never authored. Audit 2026-09-19: for a legacy row (no `choices`) it is
true when no event-level outcome has ordinal `good`, so fairness has a defined input on every row.

### 6. Gate G2 — corpus honesty

The committed corpus has two dangling chains (ideal §3.4, `npc-story-events-ideal.md:188`). Making
`event.chain-ref-dangling` a failure turns the corpus red. G2 (`npc-story-events-map.md:298`) orders it: the
rule lands **no later than** narrative-seed's regenerated corpus. If regeneration is later, the rule ships and the
two offenders are listed in a committed, owned **known-defect list** (`data/seed/dungeon/events/_known-defects.json`
(new) — ids, rule, owning program `narrative-seed`, task `delve-event-regen`) that the preflight reads and reports
as a named defect, never as a skip. The list may only shrink; a test fails if it names an id that no longer
fails the rule. Owner ruling 2026-09-20: `dungeon-generator-repair` regenerates the four legacy `story` events clean
and keyed but keeps their committed `chainRef`s, so their dangling tails stay (accepted); they stay on this list,
tolerated only for the legacy tree, until `delve-event-regen` replaces it.

## Numeric types

| Quantity | Type | Why |
|---|---|---|
| `Revision` | `long` | a counter bumped per regeneration over an endless corpus life |
| `Slot` | `int` | a bounded ordinal (slots 0–3). Audit 2026-09-19: `ArcLink` is a link id string (`spec-narrative-contract.md` §5), not a number |
| content hash | `string` (hex SHA-256) | identity, not arithmetic |

## SOLID notes

- **S:** one loader and one catalog for legacy and widened rows; the preflight stays one `Run`.
- **O:** new rules are added to `EventRules` and `Run`; no second validator beside it.
- **L:** a legacy row behaves exactly as before through the Delve adapter (`EventChoices.Presented`); the widened
  path does not weaken any existing refusal.
- No second predicate engine: conditions compile through `PredicateCompiler`, read through `AtomJson`.

## Commands

```powershell
.\scripts\verify-change.ps1 -Paths @('src/FusionRpg.Core/Narrative/Storylets/EventSeedFile.cs','src/FusionRpg.Core/Narrative/Storylets/EventDeckPreflight.cs','tests/FusionRpg.Core.Tests/Narrative/Storylets/StoryletContractTests.cs') -Session <session-id>
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~Narrative.Storylets|FullyQualifiedName~Delve.Events|FullyQualifiedName~Predicate"
```

## Structure

```
src/FusionRpg.Core/Narrative/Storylets/
  EventRow.cs                  (edited: appended members, StoryletChoice/Role/Outcome, TextRef)
  EventSeedFile.cs             (edited: trees, choices, two directories, legacy hosts)
  EventCatalog.cs              (edited: ChoiceConditionFor, tombstones, IsNegative)
  EventDeckPreflight.cs        (edited: §5 rules)
  StoryletCanonical.cs         (new)
data/seed/dungeon/events/_known-defects.json          (new, only if G2's fallback applies)
tests/FusionRpg.Core.Tests/Narrative/Storylets/StoryletContractTests.cs      (new)
tests/fixtures/narrative/storylets/                    (new: widened fixture corpus, red fixtures per rule)
```

## Testing strategy

- **Legacy parity:** the committed Delve corpus loads to the same `EventRow` values as before (field by field over
  every file), plus derived `Hosts`.
- **Widened fixtures:** a green fixture corpus (one storylet per choice kind, one arc of three links, one authored
  row) loads; each §5 rule has a red fixture that fails with exactly its rule id.
- **Trees:** an eligibility tree and a per-choice condition parse, compile and evaluate; a depth-5 tree and a
  17-node tree reject with the compiler's own reason.
- **Canonical form:** `Serialize → Parse → Serialize` is byte-identical for every fixture; the hash is stable
  across two process runs; reordering JSON keys in the source file does not change the hash.
- **Dangling chain:** the committed corpus fails `event.chain-ref-dangling` for exactly the known-defect ids (or
  passes after regeneration); the known-defect list test fails on a stale entry.
- **No population assertion:** tests never count storylets in the committed corpus.

## Success criteria

1. Legacy parity green. 2. Every §5 rule has a named red fixture. 3. Trees load and compile within the grammar.
4. Canonical form round-trips byte-identically. 5. G1: legacy and widened shapes load in one catalog. 6. G2:
dangling chains fail or are listed as owned defects. 7. NS7's `leave` rule is enforced for widened rows and
party-dungeon's spec text is amended in the same change.

## Boundaries

- **Always:** one loader, one catalog; refuse by rule id; repeat seed-side structural rules at load.
- **Ask first:** a new consequence kind or choice kind (a registry change owned by narrative-seed).
- **Never:** hand-edit a generated storylet to pass a rule (fix the generator); a legacy/widened split into two
  catalogs; accept a dangling chain silently.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `EventRow` widened members, `StoryletChoice`, `StoryletRole`, `StoryletConsequence`, `TextRef` | `cast-resolver`, `storylet-selection`, `narrative-text`, `choice-resolution`, `outcome-routing` |
| `EventCatalog.ChoiceConditionFor`, `IsNegative` | `storylet-selection`, `choice-resolution` |
| `StoryletCanonical.Serialize/Parse/Hash` | `story-ledger` (pins) |
| widened `EventDeckPreflight.Run` | domain importer, `narrative-seed` validators (parity) |

## Contradictions found (report; not fixed here)

1. **Who widens the loader.** `narrative-seed-map.md:343` assigns *"`EventSeedFile` loading `choices[]` and
   eligibility trees, `EventRow` widening … the preflight rule that a dangling link fails"* to **party-dungeon**;
   `npc-story-events-map.md:182` and `:209` assign them to **this module**, and the map's ownership table gives the
   engine to npc-story-events after the re-seam (`:311`). This spec follows the npc-story-events map; the
   narrative-seed map row should be corrected. Reconciled 2026-09-19: `narrative-seed-map.md` §7 now gives the
   loader, `EventRow` widening and preflight to npc-story-events (`storylet-contract`); party-dungeon keeps the live
   path (answer route, `MarkRoom`, domain import).
2. **Consequence targets are missing from the seed contract.** `narrative-seed-ideal.md:306` gives an outcome
   `{ordinal, consequence, effect{family, powerBand}, dropBand}` with no target; the runtime cannot route
   `relation.shift` or `story.flag` without one. `consequenceRef` (PLANNED) is filed on `narrative-contract`.
   Reconciled 2026-09-19: `narrative-seed/spec-narrative-contract.md` §5 now carries `outcomes[].consequenceRef`
   (PLANNED, string or null). A remaining `consequence` shape mismatch (`{kind, arg}` there, a string here) is
   recorded in that spec's reconciliation section. **Resolved — Owner ruling 2026-09-19 (round 3):** one object
   `{kind, ref, param}` owned by `narrative-contract` §5, loaded as-is (§1–§2 here); `consequenceRef`, `arg` and
   `consequenceParam` are retired.
3. **Legacy `leave`.** Until regeneration, legacy rows keep `leave` only on `story` (`EventChoices.cs:30`), so the
   Delve presents no escape on a legacy curio. NS7 applies to widened rows at load; the legacy corpus meets it only
   when `delve-event-regen` lands. Stated so no session reads the legacy behaviour as an NS7 violation.

## Open questions

None for the owner.

## Design-gate checklist

```
[x] Subsystems: storylet engine, predicate grammar (reader), narrative seeds (consumer), Delve corpus.
[x] Session boundary recorded (narrative-programs-spec2-20260919).
[x] Read this session: map rows 2-3, G1, G2, NS7; ideal §6.2, §11 items 3 and 10; narrative-seed ideal §6.2 and
    map §3-§7; spec-event-deck.md §6, §9; EventSeedFile, EventCatalog, EventChoices, EventDeckPreflight,
    PredicateCompiler, AtomJson.
[x] Every claim cites file:line. Code checked, not comments (the catalog's compile call, the loader's throw).
[x] No population pinned. No cache introduced. No actor number.
[x] No parallel path: one loader and catalog for both shapes.
[ ] Registry row: the preflight rules are covered by EventDeckPreflight tests; no new guard script.
```

## Standards audit (2026-09-19)

| # | Severity | Finding | Status |
|---|---|---|---|
| 1 | high | The §1 seed example did not match the seed contract it claims to read (`narrative-seed/spec-narrative-contract.md` §2–§5): `storyletId` vs `id`, `tombstone: bool` vs `status: live·tombstone`, `choiceKind`/`param` vs `kind`/`arg`, a predicate tree vs the `{id, arg}` condition object, `leave` with `outcomes: []` vs the one const `nothing` outcome, no envelope, `dropBand: "frequent"` (not a band id). A loader built from it would refuse every generated seed | **Fixed:** example re-aligned; the loader maps seed names to the C# names; eligibility on widened rows is null by contract |
| 2 | medium | `IsNegative` undefined for legacy rows, which the fairness filter reads on every host | **Fixed** |
| 3 | low | `roles[].requires` example used `role:trader`, not a storylet-vocab §3.6 family | **Fixed:** points at the family grammar owned there |
| 4 | low | Map citations one line early (`:208`, `:296-297`, `:404`, `:413-418`, `:310`) | **Fixed** |
| 4b | medium | `ArcLink` typed `int` while the seed's `arcLink` is a link id string from the arc shape | **Fixed:** `string?` |
| 5 | low | "today's 54 Delve events" is a population reading in prose, not an assertion; tests correctly never count the corpus | no change |

Checked and clean: one loader and one catalog (SOLID S), the consequence object `{kind, ref, param}` loaded as-is
(round-3 ruling), `revision` as `long`, generated seed never hand-edited (§6's known-defect list reports, it does not
edit).

**Proposed enforcement-registry row:** `ns-storylet-preflight-at-load` — the runtime repeats the structural seed rules
at load; guard `tests/FusionRpg.Core.Tests/Narrative/Storylets/StoryletContractTests.cs` (one red fixture per §5 rule
id).

## Cross-lane alignment (2026-09-20)

Alignment 2026-09-20. Rule applied: narrative-seed's `narrative-contract` owns the storylet seed's shape and this
loader reads exactly that shape. Checked against the six differences `narrative-seed/spec-narrative-contract.md` §13
listed:

| Difference | State before this alignment | Now |
|---|---|---|
| envelope | read (2026-09-19 audit) | read; `storylet.envelope` refuses anything else |
| `id` / `storyletId` | read as `id` | unchanged |
| `status` / `tombstone` | read as `status` | plus the five-field tombstone row and `storylet.status` |
| `slot` | array position | unchanged |
| `arcLink` type | link id string | unchanged |
| `{id, arg}` vs compiled tree | slot conditions compiled; a widened `eligibility` declared absent | slot conditions and the `eligibility` list compiled by `ConditionCompiler` at load; `storylet.condition-unknown`, `storylet.condition-context` |

Two drifts the 2026-09-19 audit introduced are also fixed: the example's choices said `kind`/`arg` (the seed's names
are `choiceKind`/`param`), and a widened `eligibility` was declared impossible. `teaches` (owner ruling 2026-09-20)
and `tokens` are read; `storylet.teaches` refuses a value the row cannot carry. `doctrine.setback` joins the
no-`ref` kinds.
