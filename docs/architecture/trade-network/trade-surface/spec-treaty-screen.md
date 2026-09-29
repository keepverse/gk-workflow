# Spec: `treaty-screen`

**Status: written 2026-09-19 against the approved map** ([trade-surface-map.md](../trade-surface-map.md),
APPROVED 2026-09-19, module 11, wave 5). **UI-gate:** the layer's home, data, bus, commands and acceptance
are fixed here; its layout is not (see *Layout pending `/idea-ui`*). Every `file:line` below was opened
this session. Docs only.

## Objective

The diplomacy surface for trade-network ideal §7.7: every known faction with its relation band, the
derived access level both ways, active treaties with their terms and truce state, embargoes, and
**proposals** — pick a treaty kind the band allows, see its terms and tariff, file it; see an AI answer
with the refusal's terms and counter-offers from the fixed article list. It renders derived values and
files commands; it computes neither access nor valuation.

## Locked anchors

- **Owner decision OD-1 (2026-09-19): treaties live in a new "Diplomacy" rail layer, unlocked at first
  contact.** This closes the map's Q1 (option (a)). A layer on the rail is reachable from every stage
  (GG-7), which a crest-only sibling inspector is not.
- **The amendment is a requirement, not an edit made here.** The IA and `decisions.md` rows below must be
  amended by their owners before this layer is built.
- **Access is derived by `exchange` `trade-access`; the band is the one ladder** (npc-story-events
  `relation-ledger`, four bands `eager, open, wary, hostile`, `gk-data/packs/fusion/data/seed/dungeon/_registry/disposition.v1.json`)
  read through `counterparties`' **logged band snapshot** (counterparties map assumption 3), so the screen
  and the step see the same band.
- **Command kinds are the providers'.** Treaty, embargo and bloc commands: `exchange` `treaty-lifecycle`.
  War and peace: `counterparties` `diplomatic-stance` (`war-declare`, `peace-offer`, `peace-accept`).
  AI answers and refusal terms: `trade-ai` `ai-treaty-policy`, `counter-offer-articles`. (Correction to the
  map's contradiction 3, which assigned treaty command kinds to `counterparties`: the approved
  `exchange` map owns them.)
- **Filing is not resolving** (GG-15): a proposal is answered with the turn.
- **Round 4 ([decisions-round-4.md](../decisions-round-4.md)):** the layer still **appears** at first contact (OD-1) — relations, clan access and
  embargoes are readable from then — but **proposing a treaty to an empire needs an Embassy**, blocs and a
  deliberate embargo need a **Consulate**, and `preferential` or bloc terms need an **Exchange**
  (`exchange` `treaty-lifecycle` §3a, reading `counterparties` `DiplomacyGate`: the **offerer's** building —
  accepting an empire's offer needs none; **round 5 C2 (owner, 2026-09-20): *"only the side making the
  offer"***, superseding "counterparties CQ1 default"). A **deliberate** embargo needs a Consulate; a
  war embargo is automatic and is shown with no building (round 5 C3). Clans need no embassy. Losing an
  Embassy never un-signs a treaty the screen lists. The dominant enemy empire is listed with no
  proposable treaty **toward the player only** (Q4); the screen may show its treaties with others.

## Required amendments (owners' edits, listed — not made here)

| Where | Today | Amendment required by OD-1 |
|---|---|---|
| `docs/design/information-architecture.md` §3 layer catalog | eight player layers `C K R F P E A H` plus the sector inspector; "nine player layers"; the rail "ten entries" | add **Diplomacy**, key `D`, contains relation bands, access, treaties, embargoes, proposals; counts become ten player layers, eleven rail entries |
| same doc §4 band 2 row | "the ten layers in §3" | eleven |
| same doc §5 verb table | `C K R F P E A H` | add `D` (unused today: no registration of `d` in `layers/system/keybindings.ts` or `shell/keymap.ts`) |
| same doc §7 unlock ladder | no Diplomacy row | *Diplomacy — first contact with a clan or rival* |
| `docs/architecture/decisions.md:110` Game GUI row | "4 stages, 8 layers and 1 gated tree" | 9 layers, citing OD-1 |
| `gk-web/web/fusion-rpg-web/src/shell/railState.ts:8-16` `RailLayerId`; `:65-74` ladder; `:76-93` `isUnlocked` | eight ids | `diplomacy` id, label, key `D`, reason, `hasFirstContact` input (from `trade-unlock`) |
| `gk-web/web/fusion-rpg-web/src/layers/system/keybindings.ts:22-31` `DEFAULT_BINDINGS` | eight rebindable rail verbs | `diplomacy: "d"` and its label |

## What already exists

### Built

| Finding | Evidence |
|---|---|
| Rail rendered from state with a required locked reason | `gk-web/web/fusion-rpg-web/src/shell/railState.ts:1-6,65-93` |
| Rebindable rail verbs | `gk-web/web/fusion-rpg-web/src/layers/system/keybindings.ts:22-31` |
| Four-band disposition registry | `gk-data/packs/fusion/data/seed/dungeon/_registry/disposition.v1.json` |
| Faction kinds that can treat (`Clan`, `Rival`) | `gk-core/src/FusionRpg.Core/World/FactionKindCatalog.cs:13,15` |

### Real gap

No peace state (every pair is hostile, counterparties map *What the code says*); no treaty facts, access
derivation, treaty commands or AI answers; no layer.

## Design

### 1. Data (`trade-wire` W5)

```csharp
public sealed record CounterpartyDto(
    string FactionId, string KindId,                 // clan | rival | dominant (never "zomboss" on a player surface)
    string BandId, int BandSnapshotTurn,             // the logged snapshot the step used this turn
    string StanceId,                                 // war | peace (counterparties diplomatic-stance)
    string AccessToThemId, string AccessFromThemId,  // closed | passage | market | preferential (exchange trade-access)
    IReadOnlyList<ActiveTreatyDto> Treaties,         // kind, since turn, minimum term, truce-until
    bool EmbargoOut, bool EmbargoIn,
    IReadOnlyList<ProposableTreatyDto> Proposable,   // every treaty kind, with Allowed + LockedReason (lowest band, or the missing building — round 4)
    IReadOnlyList<ProposalStateDto> Proposals);      // filed, answered (accepted | refused with terms | countered)
```

Known factions only (met through intel); the dominant enemy empire is listed with its stance and no
proposable treaty toward the player (decided: round 4 Q4 — it treats with rivals and clans, never the
player; read through `diplomatic-stance` `IsLockedWar`), each with the reason.

### 2. Fold and bus

`foldDiplomacyLayer(input) → DiplomacyVm` (pure). Closed bus:

| Event | Files |
|---|---|
| `diplomacy.propose` `{ counterpartyId, treatyKindId, deal }` (`deal` = `treaty-vocabulary` §6's `Deal`: legs, shape, tariff, term, soul top-up, leg hub) | `exchange` `treaty-lifecycle` `treaty-propose` |
| `diplomacy.respond` `{ offerId, response: accept \| decline \| counter, deal? }` (audit 2026-09-20: the player had no way to answer an offer an AI made — `ai-treaty-policy` §2 step 6 proposes to the player) | `treaty-lifecycle` `treaty-respond` |
| `diplomacy.bloc.propose` / `.join` / `.leave` `{ blocId?, inviteeIds?, deal? }` (audit 2026-09-20: blocs had no verb on the one diplomacy surface) | `treaty-lifecycle` `bloc-propose` / `bloc-join` / `bloc-leave` |
| `diplomacy.accept-counter` `{ proposalId }` | `treaty-lifecycle` accept |
| `diplomacy.end` `{ treatyId }` | `treaty-lifecycle` end (breaking inside the minimum term is shown as *break*, with its relation cost named) |
| `diplomacy.embargo.set` / `.lift` `{ counterpartyId }` | `treaty-lifecycle` embargo |
| `diplomacy.war.declare` `{ counterpartyId }` | `counterparties` `war-declare` (a destructive act: band 3 confirm, GG-22 — the one band-3 open here) |
| `diplomacy.peace.offer` / `.accept` `{ counterpartyId }` | `counterparties` `peace-offer` / `peace-accept` |

### 3. Home and unlock

Rail layer `diplomacy`, key `D`, band 2, available from every stage; locked until `trade-unlock`'s
`Diplomacy` capability with the reason *Unlocks when you first meet a clan or rival* (GG-17). A faction
crest elsewhere (sector inspector, turn report, notices) opens this layer focused on that faction.

## Contract exposed

`CounterpartyDto` family, `foldDiplomacyLayer`, the bus, rail id `diplomacy`. Consumers: the rail, other
surfaces' crest links, `trade-click-budget`.

## Acceptance (contract level)

1. **No FE derivation:** access and band shown equal the Core derivation / logged snapshot for every
   fixture pair.
2. **Locked, never hidden:** a treaty kind above the current band shows locked with its lowest band as the
   reason (GG-17, GG-55); a kind blocked by the **viewer's own** missing Embassy, Consulate or Exchange
   shows locked with that building named (only the offerer's building gates, round 5 C2 — never the
   counterpart's),
   and never locked for a clan for want of an embassy. `embargo-set` shows locked without a Consulate;
   an automatic war embargo is listed as in force with no lock and no building (round 5 C3).
3. **Refusals show terms:** every refused proposal renders its terms and any counter-offer articles.
4. **One command per proposal**; the answer arrives with the turn (GG-15); nothing shows accepted before it.
5. **Reachability:** once unlocked, the layer opens from every stage (GG-7 matrix row); before, the rail
   entry is locked with its reason.
6. **War confirms:** declaring war pushes the band-3 confirm; no other diplomacy action does.
7. **Player vocabulary:** no `zomboss` or other code identifier on the surface (GG-23; counterparties
   player-vocabulary rule).
8. **Every verb has a surface (audit 2026-09-20):** an offer an AI files to the player appears with
   accept, decline and counter; each files exactly one `treaty-respond`; bloc propose, join and leave each
   file one command; the bus covers every player-fileable diplomacy kind in `treaty-lifecycle` §1 and
   `diplomatic-stance` (a join test between the two lists).

## Layout pending `/idea-ui`

Not decided here: the layer's recipe (faction list + reading column is the GG-63 default, not a decision),
the band and access pieces, treaty rows, the proposal composer, counter-offer rendering and motion.
Through [idea-ui-phase.md](../../idea-ui-phase.md), with a queue row, before build.

## Test plan and verification boundary

- Server DTO (fog: known factions only; snapshot band) — `server-fallback`.
- Web fold, bus mapping, rail lock and reachability — vitest. **Gap, stated:** no `web/` verification
  boundary (`gk-core/scripts/verification-boundaries.v1.json`); report, never run the full suite instead.
- Derivation tests are `exchange`'s and `counterparties`'.

## Hard edges

- **FE stack (map §3 principle 13, audit 2026-09-20).** Chrome copy goes through Lingui macros and `npm run extract`; content words (goods, causes, kinds, building names) come from `trade-lexicon` / structure rows, never a Lingui key per id and never an id; glyphs map catalog `icon` keys to `lucide-react` with the GG-58 fallback; meters and charts are kit pieces or the locked libraries, never hand-rolled; pieces never fetch; folds are pure; the bus is closed.
- **Blocked on the required amendments above** (IA, `decisions.md`, `railState.ts`, `keybindings.ts`).
- Blocked on `counterparties` (`diplomacy-facts`, `diplomatic-stance`, `relation-facts`), `exchange`
  (`treaty-vocabulary`, `trade-access`, `treaty-lifecycle`), `trade-ai` (`ai-treaty-policy`,
  `counter-offer-articles`).

## Dependencies

`trade-wire` (W5), `trade-lexicon` (treaty kinds, access levels, bands' player words), `trade-unlock`
(`Diplomacy` flag, first contact — a dependency the map did not list; added); providers above; IA and
`decisions.md` owners.

## Boundaries

- **Always:** render derived values; reasons on locks; war confirmed.
- **Ask first:** a treaty kind outside `treaty-kind.v1`; a relation readout beyond the band.
- **Never:** compute access or valuation in the web; a second relation scale; a code faction name on screen.

## DESIGN-GATE §5 checklist

```
[x] Subsystems: IA/rail, GUI Lego menus, diplomacy read model (consumer), relation ladder (read).
[~] Session boundary: trade-network-idea-20260919 record; check script not re-run (docs only).
[x] Read: IA §3–§7, decisions.md :110, GG-7/17/22/23/55/63, counterparties-map (whole), exchange-map module table.
[x] decisions.md: Game GUI (:110) needs the OD-1 amendment — listed, not made.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run; no HIGH finding.
[x] Verified in code: RailLayerId, ladder, isUnlocked, DEFAULT_BINDINGS, no "d" registration.
[x] Surrounding sections read (IA rail uniformity paragraph).
[x] No untested constraint claimed.
[x] No §2 invariant contradicted.
[x] Corrections propagated: treaty command ownership (exchange) and the trade-unlock dependency recorded in the map.
[x] No population pinned: bands (4) and access levels (4) are closed vocabularies owned elsewhere.
[x] Cache: rides trade-wire's triggers.
[x] Ordering: none fixed (proposal and war filed the same turn resolve by counterparties' stated order).
[x] No actor magnitude.
[x] No parallel path: one ladder, one access rule, provider commands.
[ ] Registry row: the rail-from-state rule already exists (GG-44); the "no code faction name" rule needs a row when built.
[x] Round 4 reconciliation (2026-09-19): Embassy/Consulate/Exchange locks with named reasons; Q4 scope.
[x] Round 5 (2026-09-20): C2 (offerer only) and C3 (deliberate embargo needs a Consulate; war embargo
    automatic) are owner decisions; lock text and acceptance 2 follow them.
```
