# Spec: `trade-fact-source`

**Status: written 2026-09-19 against the approved map** ([trade-stories-map.md](../trade-stories-map.md),
APPROVED 2026-09-19, module 2, wave 2). Every `file:line` below was opened this session. Docs only.

## Objective

After a world turn commits, the trade records and report lines of that turn become story-ledger facts
**in the same commit**, so a lane cut or a lost caravan is a fact before any storylet reads it
(trade-network ideal §14b: *"lane cuts and lost caravans write story facts at once"*).

## Locked anchors

- **Owner decision OD-4 (2026-09-19): `trade-fact-source` registers into `counterparties`' `relation-facts`
  projection.** `relation-facts` owns the one commit-time projection seam that writes world-turn facts into
  the story ledger ([counterparties-map.md](../counterparties-map.md) module 7 and contradiction C5). This
  module supplies a classifier registered into that seam; it adds no second writer, no second pass and no
  second transaction.
- **Pure classifier, Data-side append** — the shape of notification-ssot's `world-notify-source` (a pure
  Core classifier over committed report entries).
- **Reads durable records, never hooks producers' code** (the npc `failure-branches` rule).
- **Fog is reused.** A fact is written only for the audience that can see its source line — the visibility
  rule (`gk-core/src/FusionRpg.Server/WorldEndpoints.cs:565-576`), moved into Core by notification-ssot's ask.
- **Hash-neutral.** The world state hash is computed at `Step`; story facts are Data-side and never enter
  it.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| Post-Step, same-transaction Data work in the turn commit (the precedent `relation-facts` builds on) | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CargoCommands.cs:131` (`DebitActCostUnlocked`, run in the commit's transaction) |
| Report entries with sector and audience | `gk-core/src/FusionRpg.Core/World/Turn/TurnReport.cs:30-31` |
| Visibility rule | `gk-core/src/FusionRpg.Server/WorldEndpoints.cs:565-576` |

### Real gap

The seam itself (`relation-facts`), the story ledger (`story-ledger`), and every producer record are
unbuilt.

## Design

### 1. The registration

`relation-facts` defines the seam ([spec-relation-facts.md](../counterparties/spec-relation-facts.md) §1):
`ICommitFactProjector { string ProjectorId; IReadOnlyList<StoryFactAppend> Project(CommittedTurn turn); }`
over `CommittedTurn(PlayerId, WorldId, Turn, Before, After, Report, Deltas)`, run by `CommitFactProjection`
in `ProjectorId` order inside the commit transaction, after the turn-log insert, appending through the
story ledger's `AppendStoryFactsUnlocked`. This module registers one projector into it:

```csharp
// src/FusionRpg.Core/World/Trade/Stories/TradeStoryProjector.cs (new)
public sealed class TradeStoryProjector : ICommitFactProjector
{
    public string ProjectorId => "trade-story";              // the id relation-facts reserves for this module
    public IReadOnlyList<StoryFactAppend> Project(CommittedTurn turn); // pure; classify per trade-fact-kinds
}
```

Report-derived kinds read `turn.Report`; the two diplomacy-derived kinds read the diplomacy facts present in
`turn.After` and absent from `turn.Before`; stock-affecting context (a caravan's lost goods) reads
`turn.Deltas`.

### 2. Classification

For each report entry and diplomacy fact of a kind listed in `trade-fact-kinds`: build the draft with the
declared subject, attributes and `source_ref`; keep it only when `turn.PlayerId`'s faction is in the
entry's audience under the fog rule (the seam runs per save); skip AI-only audiences (AI factions keep no story ledger; their
relations are `relation-facts`' pair facts). One source record yields at most one draft per audience.

### 3. Idempotence

Drafts carry the ledger's dedupe key; a re-committed or replayed turn appends nothing (the ledger's
append returns `(false, existingSeq)` on a duplicate key).

## Contract exposed

`TradeStoryProjector` (registered, id `trade-story`). Consumers: `relation-facts` (host of the seam);
downstream readers see only ledger facts.

## Acceptance (contract level)

1. **Idempotent:** replaying a commit writes nothing new.
2. **Complete and exact:** for a fixture world driven by real commands, every source record of a covered
   kind yields exactly one fact per eligible audience, and no fact exists without its record
   (reconciliation both ways).
3. **Fog:** an entry the viewer cannot see yields no fact for that save.
4. **Same commit:** a fact is visible to a storylet read issued immediately after the commit returns.
5. **Hash-neutral:** the turn's stored state hash is identical with and without the projection registered.
6. **One writer:** no code path outside `relation-facts`' pass appends a trade kind (a scan over Data
   sources for trade wire ids).
7. **Order-independent:** the drafts are the same set whichever order the report's entries are visited.

## Test plan and verification boundary

- Core classifier tests (kinds, audience, idempotent keys) — `core-fallback`.
- Data commit tests (same transaction, idempotence, hash-neutral) — `data-fallback`
  (`FusionRpg.Data.Tests`, world commit).

## Hard edges

- Blocked on `counterparties` `relation-facts` (the seam) and npc-story-events `story-ledger`.
- If `relation-facts` lands its seam with a different signature, this module adopts it; it never
  builds its own pass.

## Dependencies

`trade-fact-kinds`; `counterparties` `relation-facts`, `diplomacy-facts`; npc-story-events `story-ledger`;
producers in `sector-yield`, `logistics-flow`, `exchange`, `fleet`; notification-ssot's Core fog-rule move.

## Boundaries

- **Always:** register into the one seam; dedupe through the ledger key; fog by the one rule.
- **Ask first:** writing facts for AI-only audiences.
- **Never:** a second commit-time pass; hooking a producer; a fact inside the hashed state.

## DESIGN-GATE §5 checklist

```
[x] Subsystems: turn commit (Data), story ledger, fog rule, counterparties relation-facts.
[~] Session boundary: trade-network-idea-20260919 record; check script not re-run (docs only).
[x] Read: counterparties-map modules 3/7 and C5, spec-story-ledger §2–§3, notification-ssot-map module 7.
[x] decisions.md: no lock on the seam.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run; no HIGH finding.
[x] Verified in code: the post-Step debit seam, VisibleTo, TurnReportEntry.
[x] Surrounding sections read.
[x] No untested constraint claimed; hash-neutrality is an acceptance test.
[x] No §2 invariant contradicted (SQL in Data only; determinism: Data-side after the hash).
[x] Corrections propagated: C5 resolved as OD-4 in the map.
[x] No population pinned.
[x] No cache.
[x] Ordering: stated order-independent and tested.
[x] No actor magnitude.
[x] No parallel path: one projection seam, one ledger.
[ ] Registry row: "one writer for trade story kinds" needs a guard row when built.
```
