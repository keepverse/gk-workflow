# Spec: `diplomacy-facts`

**Status: written 2026-09-19 against the approved map. Spec phase; no build authorized.** Every
`file:line` below was opened in this session. Module id `diplomacy-facts`, row 3 of the
[counterparties map](../counterparties-map.md) (wave 1). Ideal:
[trade-network-ideal.md](../../trade-network-ideal.md) §7.7 (*"Access is derived, never stored … a pure
function of treaty facts in the ledger"*; *"Events move access as ledger facts"*), §14b (sparse canonical
form). Session record: `tasks/sessions/trade-network-idea-20260919.json`.

## Objective

One **append-only, hashed list of diplomacy facts** inside `WorldState`, so war, peace, treaties,
embargoes, blocs and offers are replayed state rather than a side table the step cannot see. Everything
else in diplomacy — the war/peace stance, trade access, which treaties are active, which offers are
open — is **derived** from this list and never stored.

Success looks like: replaying a world's command log rebuilds the list byte for byte; a world with no
diplomacy hashes exactly as it does today; every faction's AI reads the same list the engine does,
because diplomacy is public.

## Scope and non-goals

**In scope:** the fact record, its closed kind vocabulary, the one append API, the one place in the turn
where facts are appended, the canonical rows, persistence, and the `IWorldView` projection.

**Non-goals:** deciding anything. The stance is `diplomatic-stance`; access, treaty kinds and tariffs are
`exchange` (`trade-access`, `treaty-vocabulary`, `treaty-lifecycle`); relation bands are
`npc-story-events` (read through `relation-facts`). No command kind lands here.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| Faction rows are hashed through one canonical writer | `gk-core/src/FusionRpg.Core/World/WorldCanonical.cs:29-30` |
| The conditional-row pattern: a new piece of state emits rows only when off its default, so older worlds keep their bytes | `gk-core/src/FusionRpg.Core/World/WorldCanonical.cs:89-98`, `:100-117`, `:119-128` |
| Belief is state and is hashed; a world with no intel produces the bytes it always did | `gk-core/src/FusionRpg.Core/World/WorldCanonical.cs:71-87`; `gk-core/src/FusionRpg.Core/World/WorldState.cs:344-351` |
| The view already exposes public facts unfogged (factions, lane shapes) | `gk-core/src/FusionRpg.Core/World/Intel/IWorldView.cs:20-31` |
| Turn commit writes only what changed through the diff writer | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldGraphDiff.cs:45`; called at `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:607` |
| Claims settle in `Snapshot`, after every resolver that depends on them | `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:136-137`, `:195`, `:408` |

### Wiring gap

None.

### Real gap

The whole list: record, canonical rows, table, load, view projection.

## Design

### 1. The record

```csharp
namespace FusionRpg.Core.World.Diplomacy;       // (new)

public sealed record DiplomacyFact
{
    public int Seq { get; init; }                // append index within the world, 0-based, gap-free
    public int Turn { get; init; }               // the turn whose Snapshot appended it
    public string Kind { get; init; } = "";      // DiplomacyFactKinds (closed)
    public string ActorFactionId { get; init; } = "";
    public string? TargetFactionId { get; init; }
    public string? BlocId { get; init; }
    public string? TreatyKindId { get; init; }   // exchange treaty-kind.v1 id, when the kind needs one
    public int? MinTermTurns { get; init; }      // treaty.signed / treaty.imposed
    public string? OfferId { get; init; }        // offer.made / offer.declined / the fact that answers an offer
    public int? TariffMilli { get; init; }       // offer.made, treaty.signed, treaty.imposed, founding bloc.joined (E-A13)
    public TreatyDeal? Deal { get; init; }       // offer.made, treaty.signed, treaty.imposed — exchange's record (E-A13, round-4 widening)
    public string? SourceCommandId { get; init; }// the admitted command that caused it; null for a derived fact (war-voids)
}
```

`WorldState` gains `IReadOnlyList<DiplomacyFact> Diplomacy`, empty by default, stored in `Seq` order.

**`TariffMilli` (added 2026-09-19 for `exchange` ask E-A13).** A negotiated tariff travels on the fact that
fixes it: `offer.made` (what was offered), `treaty.signed` and `treaty.imposed` (what was agreed), and the
**founding** `bloc.joined` (the bloc's common external tariff; later joiners inherit it and carry null). Null
means *"the treaty kind's default tariff"*, so every fact written before `exchange` reads it — and every
world that predates the field — keeps its meaning. It is a `int` per-mille, a bounded ratio validated in
`[0, 1000]` at admission by `exchange` `treaty-lifecycle`, which owns what a tariff means; this module only
stores it. It is data on a fact, not a new kind — the vocabulary stays at 12.

**`Deal` (added 2026-09-19 for the round-4 widening of E-A13).** A signed deal must replay from its fact, so
the fact carries the deal: `TreatyDeal` is **`exchange`'s** record (`treaty-vocabulary` §6's shape — tariff,
term, legs, souls top-up, shape, leg hub; `../exchange/spec-treaty-lifecycle.md` §1), stored here as a
nullable field on `offer.made`, `treaty.signed` and `treaty.imposed` only. This module owns neither its
fields nor their validation; it writes `exchange`'s canonical text for it into one column. `TariffMilli`
stays the fact-level field `trade-access` reads without opening the deal; when both are present they must
agree (admission, `treaty-lifecycle`).

### 2. The closed kind vocabulary (12)

| Kind | Scope | Pair key | Written by |
|---|---|---|---|
| `war.declared` | one-sided act, bilateral effect | `(actor, target)` | `diplomatic-stance` |
| `peace.made` | bilateral | `(lower, higher)` | `diplomatic-stance` |
| `treaty.signed` | bilateral | `(lower, higher)` | `exchange` `treaty-lifecycle` |
| `treaty.ended` | bilateral | `(lower, higher)` | `treaty-lifecycle` |
| `treaty.broken` | one-sided (the breaker) | `(actor, target)` | `treaty-lifecycle`; **and `diplomatic-stance`** when a `war.declared` lands inside an active treaty's minimum term (round 6 Q-A — §7a) |
| `treaty.imposed` | bilateral | `(lower, higher)` | `diplomatic-stance` (a peace term) |
| `embargo.set` | one-sided | `(actor, target)` | `treaty-lifecycle`; the mutual embargo at war is derived by `diplomatic-stance`, never written |
| `embargo.lifted` | one-sided | `(actor, target)` | `treaty-lifecycle` |
| `bloc.joined` | multilateral | `(actor, bloc)` | `treaty-lifecycle` |
| `bloc.left` | multilateral | `(actor, bloc)` | `treaty-lifecycle` |
| `offer.made` | one-sided | `(actor, target)` | `diplomatic-stance` (peace), `treaty-lifecycle` (treaties) |
| `offer.declined` | one-sided | `(actor, target)` | the responder's module |

- **Pinned at 12, with the reason:** this is a closed vocabulary the code owns; a new kind is a reviewed
  change to this table, to the canonical writer and to every derivation that switches on kinds
  (validation-ssot: pin declarations, never populations). An unknown kind is a load rejection.
- The approved map listed ten kinds. `offer.made` and `offer.declined` are added so that **offers live
  in the same list** for peace and for every treaty kind: two modules keeping two offer stores would be a
  parallel path (DESIGN-GATE §2.15). An offer is open while no answering fact names its `OfferId` and
  `turn − offer.Turn < offerTtlTurns`; expiry is derived, never written.
- Ordered pair keys: bilateral kinds key `(ordinal lower, ordinal higher)` so a pair has one key; one-sided
  kinds key `(actor, target)`.

### 3. One append API, one position in the turn

```csharp
public static class DiplomacyLedger
{
    /// The only writer. Assigns Seq = world.Diplomacy.Count; refuses an unknown kind or a kind whose
    /// required fields are missing (InvalidOperationException — a programming error, never a report).
    public static WorldState Append(WorldState world, DiplomacyFact fact);

    public static IReadOnlyList<DiplomacyFact> ForPair(WorldState world, string a, string b);  // ordered by Seq
}
```

- **Facts are appended only inside `Step`, in the `Snapshot` phase, after the phase's resolvers
  (`ClaimResolver` through `WardenResolver`, `TurnEngine.cs:408-425`) and before postures land**
  (`TurnEngine.cs:427-433`). A fact appended on turn `N` therefore takes effect from turn `N + 1`: every
  hostility read during turn `N` — contact, zone of control, supply, claims — sees the stance the turn
  began with. That is a one-turn warning before a declared war bites, and it means no phase needs to
  re-read diplomacy mid-turn.
- Both writing modules (`diplomatic-stance` here, `exchange` `treaty-lifecycle`) resolve their admitted
  commands in that one position, in `(CommanderId, CommandId)` order (the reveal order,
  `TurnEngine.cs:215`). No new phase is added, so the locked phase list (`decisions.md` *World turn phase
  order*) does not change.

### 4. Canonical form

After the existing conditional rows (`WorldCanonical.cs:119-128`), one row per fact:

```text
diplomacy <Seq> <Turn> <Kind> <Actor> <Target|-> <Bloc|-> <TreatyKind|-> <MinTerm|-> <OfferId|-> <SourceCommandId|-> <Tariff|-> <Deal|->
```

An empty list writes no row, so every world that predates the module hashes byte-identically. Facts are
sparse by nature (they exist only when something happened), which is the ideal's §14b sparse form.

### 5. Persistence

A new append-only table owned by `FusionRpg.Data`:

```sql
CREATE TABLE IF NOT EXISTS rpg_world_diplomacy_facts (
  world_id TEXT NOT NULL, seq INTEGER NOT NULL, turn INTEGER NOT NULL, kind TEXT NOT NULL,
  actor_faction_id TEXT NOT NULL, target_faction_id TEXT, bloc_id TEXT, treaty_kind_id TEXT,
  min_term_turns INTEGER, offer_id TEXT, source_command_id TEXT, tariff_milli INTEGER, deal TEXT,
  PRIMARY KEY (world_id, seq)
);
```

The diff writer inserts facts whose `Seq` is past the stored maximum; no statement updates or deletes a
row (a text-scan test, the story-ledger precedent). `LoadWorldState` (`RpgStore.World.cs:437`) reads them
in `Seq` order. The table is born keyed by `world_id`, which the save-identity rule for new tables
already scopes through `rpg_worlds` (umbrella `trade-network-map.md` §4, `save-identity` row).

### 6. The view

`IWorldView` gains `IReadOnlyList<DiplomacyFact> Diplomacy`, the full list. **Diplomacy is public:** a
declaration or treaty is known to every faction, so `BelievedWorldView` (`IWorldView.cs:76`) returns the
truth list unfogged, and belief-side and truth-side derivations agree by construction.

### 7. The capability flag

`counterparties.diplomacy` joins `world-stamp`'s flag registry. On a world without it, no command that
writes a fact is admitted (`diplomatic-stance`, `treaty-lifecycle` check the flag), so the list stays
empty and the hash cannot move.

**Round 6 C1 — this flag is wave 1's and covers the fact list only.** This module is `counterparties`
wave 1 (row 15 of [../landing-order.md](../landing-order.md) §2) and its flag is registered there, sharing
that wave's single `RulesetVersion` bump with `counterparties.needs`, `.roster` and `.treasury`. It used to
gate `diplomatic-stance` and `relation-facts` as well, which land in **wave 2** — a flag spanning two
waves, so a world stamped at wave 1 would have gained derived war/peace and the relation projection mid-life
when wave 2 merged (the audit's C1). Those two now gate on wave 2's own flag `counterparties.stance`. The
command-admission check here stays: a command that writes a fact needs *this* flag, and the module that
issues it needs its own.

### 7a. War inside a treaty's minimum term also writes `treaty.broken` (round 6 Q-A)

> *"War inside a treaty's minimum term — **It also writes `treaty.broken`**, with the same observer effect
> as any early exit."* ([../decisions-round-4.md](../decisions-round-4.md) Round 6 Q-A)

So declaring war on a partner inside an active treaty's minimum term appends **two** facts in one step, in
this order: `war.declared` (the act) then `treaty.broken` (its consequence), both keyed as the table says —
`war.declared` on `(actor, target)`, `treaty.broken` on `(actor, target)` with the actor as breaker. Rules
this keeps, each already in force for an ordinary early exit:

- **No new kind.** The vocabulary stays **pinned at 12**; only the *writer* column widens, because
  `diplomatic-stance` now also writes `treaty.broken` where `treaty-lifecycle` used to be its only writer.
- **The observer effect is the same.** `relation-facts` already emits `treaty.break-witnessed` for every
  faction holding an active treaty with the breaker at the start of the turn
  (`spec-relation-facts.md` §2); it fires here unchanged, which is exactly what *"the same observer effect
  as any early exit"* requires — and it is why the fact is written rather than the war alone being logged.
- **The treaty ends.** `treaty-lifecycle` (`exchange`) owns what breaking does to the treaty record; this
  module writes the fact and never mutates a treaty. `treaty.ended` is not also written: a broken treaty is
  broken, not ended, and double-counting would move two bands for one event.
- **Order is fixed and tested**, because both facts are appended in one step and the append order is hashed.

## Tunables

`diplomacy.offerTtlTurns` in `data/tuning/diplomacy.v{n}.json` — turns an offer stays open; starting
value 3 (a response lands the next turn a party commits, `exchange-map.md` `treaty-lifecycle`, plus two
turns of slack). The file is created by the first module that needs it (this one or `exchange`
`treaty-vocabulary`); every later key arrives through `publish.py --add-key`.

## Numeric types

`Seq`, `Turn`, `MinTermTurns` are `int`: turn counts and fact counts, not magnitudes; they grow by one per
event and are bounded by play, well inside `int` range at any reachable campaign length. No `P(Θ)` input.

## Acceptance (contract)

1. **Append-only:** no step removes or rewrites a fact; `Seq` is gap-free and equals the list index; a
   source scan finds no `UPDATE`/`DELETE` against `rpg_world_diplomacy_facts`.
2. **Replay:** replaying a world's command log rebuilds `Diplomacy` byte for byte, and the stored list
   round-trips through save and load exactly.
3. **Closed vocabulary:** an unknown kind, or a kind missing a field its row requires, is refused at
   `Append` and at load.
4. **Pair keys:** `ForPair(a, b)` and `ForPair(b, a)` return the same facts.
5. **Legacy hash:** a world with an empty list writes the same canonical bytes as the same world before
   the module (asserted against today's shipped scenarios).
6. **Position:** a fact appended by a turn-`N` command is visible to reads in turn `N + 1` and to no
   hostility read in turn `N` (tested by declaring war and moving into contact in the same turn: no
   battle that turn; a battle the next).
7. **Public:** for every faction, `BelievedWorldView.Diplomacy` equals `WorldState.Diplomacy`.

No test pins how many facts a scenario produces.

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/Diplomacy/DiplomacyLedgerTests.cs` (new): append, refuse, pair keys,
  canonical rows, legacy hash, position.
- `gk-core/tests/FusionRpg.Data.Tests/WorldStoreTests.cs` / `WorldGraphDiffTests.cs` (extend): round-trip, diff
  inserts only new facts, append-only scan. Store tests run in memory.

```powershell
.\scripts\verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/World/WorldState.cs','gk-core/src/FusionRpg.Core/World/WorldCanonical.cs','gk-core/src/FusionRpg.Core/World/Intel/IWorldView.cs','gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldGraphDiff.cs','gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs','tests/FusionRpg.Core.Tests/World/Diplomacy/DiplomacyLedgerTests.cs') -Session <session-id>
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~World.Diplomacy|FullyQualifiedName~WorldTemplate"
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~WorldStore|FullyQualifiedName~WorldGraphDiff"
python gk-core/scripts/guard-dal.py ; python gk-core/scripts/guard-test-substrate.py
```

The change crosses Core and Data, so the full suite runs once when the module finishes (AGENTS.md
verification point 2), not on every edit.

## Hard edges

- **Hash shape.** The canonical rows land after every existing row and only when the list is non-empty;
  appending a column to the faction row instead would move every golden for a value that did not change
  (the recorded failure at `WorldCanonical.cs:89-94`).
- **Schema.** A new table; created with `CREATE TABLE IF NOT EXISTS`, no migration of existing rows.

## Dependencies

| Consumes | From |
|---|---|
| Capability flag registry | `trade-foundation` `world-stamp` |

| Exposes | To |
|---|---|
| `DiplomacyFact`, `DiplomacyFactKinds`, `DiplomacyLedger.Append/ForPair`, the Snapshot append position | `diplomatic-stance`; `exchange` `treaty-lifecycle` |
| `WorldState.Diplomacy`, `IWorldView.Diplomacy` | `diplomatic-stance`, `relation-facts`, `exchange` `trade-access`, `trade-ai`, `trade-surface` `treaty-screen`, `trade-stories` `trade-fact-source` |

## Contradictions found

1. **Offer storage.** `exchange-map.md` `treaty-lifecycle` says *"an offer is hashed state with a lifetime
   of `offerTtlTurns`"* without saying where; peace offers (`diplomatic-stance`) need the same thing.
   Resolved here by two offer kinds in this one list; propagated to the counterparties map. `exchange`
   consumes the kinds rather than keeping a second offer store (its map is outside this fence; noted for
   its spec).

## Open questions

None for the owner.

## Design-gate checklist

```
[x] Subsystems: world state and canonical hash, turn engine (Snapshot), Data persistence, world intel view.
[~] Session boundary: trade-network-idea-20260919; session-boundary-check.py not re-run for this
    docs-only file.
[x] Read this session: as spec-need-vector.md's checklist, plus exchange-map modules 3, 6, 9.
[x] decisions.md: World turn phase order row (:7) — no phase added; facts append inside Snapshot.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope on this file: 0 HIGH.
[x] Verified against code: WorldCanonical conditional rows, WorldState record, IWorldView members,
    Snapshot/ClaimResolver order, diff writer call site, LoadWorldState.
[x] Surrounding sections read (§7.7, §14b sparse-form row; canonical comments on why rows are appended).
[x] "Legacy hash unchanged" is an acceptance test to run, not a claim.
[x] No §2 invariant contradicted; SQL stays in FusionRpg.Data.
[x] Correction propagated: the kind list (10 → 12) in the map.
[x] Pinned literal: 12 fact kinds, a closed code-owned vocabulary, reason stated.
[x] No event-refreshed cache; every derivation re-reads the list.
[x] Ordering: facts append in reveal order at one position; effect from the next turn in either filing
    order.
[x] No actor magnitude.
[x] No SOLID-violating path: one list, one writer API, one offer store.
[ ] Registry row: the append-only scan is a local Data test; no enforcement-registry row proposed.
```

## Audit 2026-09-20

Checked and clean: append-only, gap-free `Seq`, one writer API, one append position inside `Snapshot`; sparse
canonical rows after every existing row (legacy hash unchanged); the 12-kind vocabulary is pinned as a closed
code-owned list; `TariffMilli` is a bounded ratio validated by its owner; diplomacy is public, so belief equals
truth; SQL only in Data, tests in memory. Noted, not a defect today: the list is hashed state that only grows,
so the canonical text a turn hashes grows with campaign length (a few facts per turn); if a very long campaign
ever shows it in the step benchmark (`trade-foundation` `step-benchmark`), the remedy is a derived-state
checkpoint owned here, never a trim of facts. **Verification boundary:** the `core-world-trade-counterparties`
owner boundary (`spec-empire-goods-sinks.md` *Audit 2026-09-20*) covers `World/Diplomacy/**`; the canonical and
state edits stay on `core-fallback`; the full suite once at module end.
