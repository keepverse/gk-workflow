# Spec: `continuity-doc-amendment`

**Status: EXECUTED 2026-09-19 — this spec is the record of what changed, written after the fact.** The
edit itself was made by another agent in commit `e19d8328` (*"Record map approvals and apply
world-continuity's product-doc amendments"*), on the map's approval, as the map's wave 0 requires
(ideal §7 end: *"changed when this program's map is approved, in the same change, never piecemeal"*).
Module 16 of the [world-continuity map](../world-continuity-map.md). This spec adds nothing to that
commit and edits none of its files.

## Objective

Every product and architecture document the ideal's §7 names says what the approved program says: worlds
do not end; victory makes a world *developing*; losing your seat makes it *fallen* and the save continues
(Q2); old worlds *hibernate* or go *idle*; advancing carries a **weight-limited** payload (round 6 W1); loam
never crosses; **rubble, ironwork and every other trade good cross only over a `rift-trade` route, never on an
advance** (round 6 S2 — superseding *"cross only as cargo"* everywhere this program's amendments put it);
recruits never cross; the per-sector warden is retired (Q3).

## What changed — by the map's item list

Verified by reading the files at `HEAD` (this session) and `git show --stat e19d8328`.

| # (map §16) | Document | State after `e19d8328` |
|---|---|---|
| 1 | `docs/guide/the-game.md` | **Done.** Win row `:39`, Lose row `:40` (Q2 wording: *"That world becomes fallen … and your save continues"*), slogan `:42` (*"You keep who you are. The worlds you leave keep going."*), advance paragraph `:44`, world-stock line `:73` |
| 2 | `docs/guide/mechanisms/_content/new-world-prestige.json` + rendered `.md` and `site/…html` | **Done** (re-rendered; slug kept) |
| 3 | `docs/guide/the-loops.md` | **Done.** One clock-table row `:20`; the count stays three |
| 4 | `docs/architecture/empire-resource-ssot.md` | **Done** (rule 5b: world stocks cross only as cargo, `:77`) |
| 5 | `docs/architecture/empire-economy-ssot.md` §4, §7 | **Done** (§4 now states the two columns and advance, `:129-156`) |
| 6 | `docs/architecture/base-defense-ideal.md:95` (decision 18) | **Not done.** Still reads *"they die with the map"*; the file is outside the session's `paths` (`tasks/sessions/trade-network-idea-20260919.json`). Also `:1337-1341` in the same file |
| 7 | `docs/architecture/trade-network-ideal.md:88` | **Done** (8 lines changed; `:94` now records the old slogan as superseded) |
| 8 | `docs/architecture/world-graph-ideal.md` §1 | **Done** |
| 9 | `docs/architecture/npc-story-events-ideal.md`, `npc-story-events-map.md:209` | **Filed as an ask, not edited by this program.** npc-story-events' own session has since edited both files (uncommitted in the tree at the time of writing); `:416` of the ideal and `:157` of the map still quote *"you lose where you were"* |
| 10 | `docs/architecture/decisions.md` | **Done.** *World lifecycle* row added (`:144`); *World store — delve worlds* row amended with the one-active-per-save index (`:134`); phase-order row corrected to ten phases (`:7`) |
| 11 | `docs/guide/features.md`, `how-you-play.md`, `the-rift.md`, `glossary.md`, `site/index.html`, `_content/*.json` for `chronicle`, `dave-level`, `failure-branches`, `loam`, `map-orders`, `sector-buildings`, `unlock-chapters`, `world-map`, `zomboss-commander` (+ renders) | **Done** for the files listed. The map also named `souls`, `essence`, `specimens`, `world-generator` `_content` pages; they are not in the commit, and the acceptance search finds no stale line in any of them — nothing is owed |
| 12 | `docs/PRINCIPLES.md` §11 | **Done** (13 lines) |

## Remaining stale lines — found by the acceptance search, outside the executed set

The map's acceptance search (*"lose where you were"*, *"dies with the map"*, *"die with the map"*,
*"into the next world"* across `docs/`) still returns, at `HEAD` plus the working tree, lines that are
neither historical nor marked superseded:

| File:line | Owner (for the fix) |
|---|---|
| `docs/architecture/base-defense-ideal.md:95`, `:1337`, `:1339`, `:1341` | base-defense program (item 6 above) |
| `docs/architecture/loam-map.md:56`, `:380-381` | loam program (closed map; an amendment note) |
| `docs/architecture/achievement-title-ideal.md:375` | achievement-title program |
| `docs/architecture/empire-wonder-surfaces-ideal.md:84` | empire-wonder-surfaces program |
| `docs/architecture/power/ssot-power-scale.md:24`, `:239` (realms axis "one per retired world") | power program — `:239` is also a design question, filed by `world-victory` §5 |
| `docs/architecture/npc-story-events-ideal.md:416`; `npc-story-events-map.md:157`; `npc-story-events/spec-failure-branches.md:94` | npc-story-events (item 9) |
| `docs/architecture/trade-network/trade-stories-map.md:166`; `trade-network/trade-stories/spec-trade-fact-kinds.md:27` (*"Trade dies with the map"*) | trade-network `trade-stories` — inside this session's `paths`, but another agent's files in this round; reported, not edited here |
| `docs/architecture/trade-network-map.md:123` (decision 18 paraphrase) | trade-network umbrella — same |

## Round-4 follow-up (2026-09-19) — owed, not yet made

| Document | Change owed | Why | Status |
|---|---|---|---|
| `docs/architecture/empire-resource-ssot.md` rule 5b (`:77-78`) | ~~*"World stocks cross worlds only as cargo"* → *"… as cargo or over a cross-world route, and never bank"*~~ **Round 6 S2 replaces the wording again, and simplifies it:** *"World stocks cross between worlds **only over a cross-world (`rift-trade`) route**, never on an advance and never banked."* Advance carries units, their members and their item cargo under a weight limit (W1); a good aboard a departing legion is refused, not voided (`spec-advance-carry.md` §5) | `rift-trade` owner decision Q2 plus round 6 S2/W1/W2; `rift-trade-map.md` ask A12 names this module as the writer | **Accepted, not made** — the file is outside this docs session's edit fence. It lands with this module's next docs change or with `rift-trade` `crossing-goods`' implementing commit, whichever is first, and the other checks it. The same sentence is owed in `docs/architecture/base-defense-ideal.md:95` and the other rows above, each to its own owner |
| `docs/guide/the-game.md:73` and every guide page this program already amended to *"cross only as cargo"* | The same S2 sentence: goods cross by rift route, an advance is a weight-limited transit | Round 6 S2/W1 | **Owed** — inside this program's own amendment set, so it lands with this module's next docs change (it is the one item round 6 adds to the §7 list) |

## Acceptance (contract) — status

1. The search returns only historical or superseded contexts that say so — **not yet met**: the table
   above lists what remains.
2. `python docs/guide/mechanisms/_render.py --check` passes — not re-run by this spec; the commit
   re-rendered every page it changed.
3. `audit-doc-citations.py --scope <each doc>` has no HIGH finding — owned by the executing commit.

## Hard edges

Docs only. No schema, replay or corpse-cache change.

## Dependencies

Map approval (2026-09-19). Every other module's player-facing words hang on it (glossary rows for the
five labels, *advance*, *warden*).

## DESIGN-GATE §5 checklist

```
[x] Subsystems: product guide, architecture SSOTs, decisions.
[~] Session boundary: the edit was made under tasks/sessions/trade-network-idea-20260919.json; this
    record is a new file inside docs/architecture/world-continuity/**.
[x] Read this session: the-game.md and the-loops.md at HEAD (post-amendment), empire-economy-ssot.md §4,
    git show --stat e19d8328.
[x] decisions.md checked: World lifecycle row exists; :7 and :134 amended.
[x] Every factual claim cites file:line or the commit.
[x] audit-doc-citations.py --scope run on this file; no HIGH.
[x] Verified against the files, not against the commit message (the search was re-run).
[x] Surrounding sections read.
[x] Constraint tested: the acceptance search was run; its remaining hits are listed.
[x] No §2 invariant contradicted.
[x] Corrections propagated: the remaining hits are listed with owners.
[x] No population pinned.
[x] No cache.
[x] No ordering criterion.
[x] No actor magnitude.
[x] No SOLID fork.
[x] No new rule.
```
