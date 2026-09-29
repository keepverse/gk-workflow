# Trade-network family — handoff to the next project manager

**Written 2026-09-20, at the end of the planning phase. Nothing in this family is built.** Every document
below is committed on `features/mega-merge`. This page exists because the plan does not carry the owner's
reasoning, and a session that re-derives it will get it wrong — the idea phase alone overturned eleven of its
own conclusions before the design settled.

The family is one program with four document trees and thirteen clusters. Build it from
`tasks/trade-network-todo.md`, in the order `docs/architecture/trade-network/landing-order.md` fixes.

---

## 1. What exists, and where

| Artifact | Path | Size |
|---|---|---|
| **Plan** | [tasks/trade-network-plan.md](trade-network-plan.md) | 9 phases, 9 checkpoints, **1 gate** |
| **Task list** | [tasks/trade-network-todo.md](trade-network-todo.md) | **162 tasks**, 2,154 lines |
| **Landing order** (the integration ledger — wave order, flags, bumps, shared files, tuning creators, re-bless points, blockers) | [docs/architecture/trade-network/landing-order.md](../docs/architecture/trade-network/landing-order.md) | §2 is the single source of wave order |
| **Owner decision register** (rounds 4, 5, 6 — binding; a spec that disagrees is corrected) | [docs/architecture/trade-network/decisions-round-4.md](../docs/architecture/trade-network/decisions-round-4.md) | 12 + 17 + 10 rulings |
| **Standards audit** | [docs/architecture/trade-network/audit-2026-09-20-global.md](../docs/architecture/trade-network/audit-2026-09-20-global.md) | 3 critical, 8 major, 20 minor, 30 asks to 22 programs |

Four ideals and thirteen maps, every map **owner-approved 2026-09-19**:

| Tree | Ideal | Map(s) | Specs |
|---|---|---|---|
| `trade-network` (umbrella + 10 sub-clusters) | [trade-network-ideal.md](../docs/architecture/trade-network-ideal.md) | [trade-network-map.md](../docs/architecture/trade-network-map.md) + 10 cluster maps under [trade-network/](../docs/architecture/trade-network/) | 102 |
| `world-continuity` | [world-continuity-ideal.md](../docs/architecture/world-continuity-ideal.md) | [world-continuity-map.md](../docs/architecture/world-continuity-map.md) | 16 |
| `legion-build` | [legion-build-ideal.md](../docs/architecture/legion-build-ideal.md) | [legion-build-map.md](../docs/architecture/legion-build-map.md) | 17 |
| `empire-seed` | [empire-seed-ideal.md](../docs/architecture/empire-seed-ideal.md) | [empire-seed-map.md](../docs/architecture/empire-seed-map.md) | 15 |

Every spec has been through four passes: the writer's own citation audit, a cluster standards audit, a global
cross-cluster audit, and a per-cluster planning pass that read the spec against the landing order.
`python scripts/audit-doc-citations.py` reports **0 HIGH** across all of it.

**The commits of this run, newest first:** `38ff0104` (the plan and todo), `b4dd4090` (Standard Hall tier
names, doctrine upkeep confirmed), `606231d9` (round 6 applied across 102 files), `5f092060` (the round 6
register). The warden decay-freeze code fix that came out of the idea phase is already merged.

---

## 2. The owner's rulings — the part that is not derivable from the documents

Do not re-open these and do not infer around them. The register holds the full wording; this table is the
index a new manager needs before reading any spec.

| Ruling, in one line | Where |
|---|---|
| **Abstract simulation, never literal.** A pooled sector stock (L4) and an aggregate lane flow (L3); never per-unit cargo agents. Realism that costs frames is not realism | ideal §2 |
| **Buildings unlock features.** Every trade and logistics feature in a sector is opened by a specific building kind; tiers are `variants` of one structure row, never separate rows | round 4 §B |
| **Caravans are automated legions**, with or without a commander. No hauler catalog, no second legion mode — extend the legion architecture | round 3, empire-seed §6.2 |
| **Legion equipment is its own equipment scope:** fixed stats, tier from seedsmith, atom effects, **no sets**, no sockets, no rolls, weaker than unique items, mass-produced in sector buildings, held as counted stock | PRINCIPLES, `legion-build-ideal.md` §6.7 |
| **Victory does not end a world.** Worlds persist and go to hibernating or idle; events still fire; strong commanders can be left as wardens; reclaiming an old world is a later mechanism | `world-continuity-ideal.md` |
| **Realms counts worlds held**, not worlds won, and a new world counts from creation | Q8, D1 |
| **Power roll-up:** a container's power is the sum of its children, like file sizes on a disk, over ActorHub Standing. One read, never a second composer | round 4 §P |
| **One flag and one ruleset bump per wave.** A world's rules never change mid-life | round 6 C1 |
| **One neutral `StructureKind.Feature`** for every feature building; no gate ever reads a kind | round 6 C2 |
| **A feature building counts for nobody** until one faction owns both its sector and its slot | round 6 S1 |
| **An advance is a weight-limited transit**, like a spacecraft payload: Σ(unit count × that unit type's carry capacity). Trade goods cross worlds **only** by rift-trade route | round 6 S2/W1 |
| **Doctrine costs goods every turn**, proportional to the army it covers, and lapses rather than blocks when unpayable — the same rule for the player and every AI, so no handicap | round 6 CQ2, confirmed 2026-09-20 |
| **Standards need a Standard Hall**, tiers **Banner Yard → Standard Hall → Hall of Triumphs** — which fixes the standard tier ladder at three rungs | round 6 L6, named 2026-09-20 |
| **Six `world.*` derived channels** (`carry.capacity`, `march.range`, `supply.burn`, `sight`, `hazard.resist`, `upkeep.discount`) compose in ActorHub and roll up per stack and legion | round 6 D2 |
| **Vocabulary is binding.** Strategy-genre words, no IP words, no named boss. The player-facing word is **"unit"**; opponents are **"enemy empires"**, plural; a world carries a **difficulty profile** | owner, rounds 2–3 |
| **Never traded:** loam; world stocks never auto-bank; no sell price and no gold — souls never come out of trade | ideal §4 |

Four owner decisions that overturned this session's own recommendation, so nobody re-litigates them: sets
were removed from legion equipment; unloading at a foreign hub **does** need a yard there; a flag and bump
land **per wave** rather than being deferred; and the carry limit is per-unit-type capacity × count, not a
total unit count.

---

## 3. Build order

`landing-order.md` §2 is the authority. The shape:

```
Phase 0  0a trade-foundation W0 (minus sector-features)
         0b empire-seed I1-I5 + schema widening + name index + metrics
         0c the eight feature building rows
         0d sector-features                    <- first flag, first bump
         0e legion-build W1
         0f world-continuity state vocabulary
         0g material-ledger                    <- GATE: save identity
Phase 1  rows 1-4   the sector economy
Phase 2  rows 5-7, 9   the lane layer          <- interim playable state
Phase 3  row 8      outflow                    <- GATE: save identity
Phase 4  rows 10-14 located income and fleet
Phase 5  rows 15-17 counterparties
Phase 6  rows 18-19 market and AI
Phase 7  rows 20-23 cross-world
Phase 8  rows 24-25 surface and stories
Lanes anchored to trade rows: legion-build L2-L10, world-continuity WC2-WC8, empire-seed ES2-ES6
```

**Three facts a builder must know before touching `TurnEngine.cs`:**

1. **Ordinals run in three lanes** — trade `N+1…N+25`, legion `L1…L10`, continuity `C1…C4`. A series fixes
   order *within* its lane and at its trade anchors. Every lane **rebases onto the live
   `TurnEngine.RulesetVersion` and takes the next integer**; the ordinals are never literals.
2. **A capability gate means no existing golden moves.** `GrantedBy` is empty for legacy and unstamped
   worlds, so the canonical projection is byte-identical for every world created before a wave. The re-bless
   list is four rows long (§6). A golden that moves outside it is a defect to diagnose, not a re-bless.
3. **Rows 1–7 and 9 are a complete, playable economy with no outflow.** Production halts at warehouse
   capacity, structures pay their loam term and yield goods, lanes carry goods to the nearest bank point and
   they wait there. Nothing leaves the map and the report prints a banked total of **zero with the reason**.
   No artifact may call the family shippable before row 8.

---

## 4. The one gate, and the defaults that replaced the rest

**GATE — rows 0g and 8 wait on the save-identity re-key** (`save-identity` SE4.12 → SE4.38,
`tasks/solid-enforcement-todo.md:634`, unchecked). `material-ledger` and the banking step write four ledger
sites against that key. Round 6 C3 is **wait**: landing on the current key and re-pointing later would edit
those sites twice against persisted player data. The audit's option (b) was explicitly not taken.

Everything else the audit called a blocker ships behind a reversible default, because a plan that freezes on
a coordination ask never starts. Full table in the plan's §4; the four that matter:

| Item | Default |
|---|---|
| Power-ladder §10 consumer rows (X-4) | **Our work, not a wait** — the consuming task authors its own row, which is what "consumer-authored" means |
| Power-ladder contest row (X-2) | Warden defence term is **0**, escort strength stays the v1 stance count. Blocks **only** row 23 and `world-warden` — not `deal-valuation` or `ai-trade-buildings`, which read the roll-up to choose |
| Multi-slot `BuildResolver` (X-11, world-map's) | Every feature row ships `requiredSlotKind: Wildland`, the subset every option keeps |
| `world-transit`, `world-derived` (round 6 W2, D2) | Named future programs. Every consumer reads a stated default; no spec here implements either |

---

## 5. Defects planning found — already fixed, do not re-derive

The cluster audits checked clusters; planning checked the build, and found seven things they could not. All
are recorded in `landing-order.md` §10 with the reasoning.

| Defect | Fix |
|---|---|
| `sector-features` could not land in row 0a — it writes `StructureDef.FeatureUnlock` and `StructureKind.Feature` against a schema that gains those fields in 0b, for rows that arrive in 0c | Own row 0d, after both |
| The same module turns `build` on an occupied own slot into an **upgrade**, changing how an existing world's stored order resolves, in a wave with no flag | Row 0d takes the family's **first** flag and bump |
| Row 0b omitted `world-name-index` and `corpus-metrics`, which row 0c depends on | Both added to 0b |
| `trade-ai` claimed it writes no hashed state; `trade-intel` hashes belief inside `Step` and adds two `WorldCanonical` row kinds | Row 19 registers `trade.intel` and takes a bump |
| `trade-stories` claimed the same; the seasonal demand shock is a term in the demand function `exchange` reads, so it moves prices on a live world | `seasonal-demand-shocks` registers `trade.demandShock` |
| `trade.exchange` gated `order-set` across two waves — a world stamped between them gains rules mid-life | New `trade.exchangeOrders` at 18c; the waves were **not** merged |
| `legion-build` and `world-continuity` had no rows in §2, so four clusters could not sequence against `standing-orders`, `escort-stance`, `field-battle-kinds` or `legion-power` | Both lanes added. This closed audit **M2**: C1's question is asked per **wave**, not per module, so `legion-build-map.md` §13 was right about the module and §4 right about the rule |

Two tuning creators were also wrong and are corrected: `diplomacy.v1.json` belongs to `counterparties`
`diplomacy-facts` (row 15, the first module to need the domain), and `ai.v3.json` to `trade-ai`
`ai-spend-limit` (its own spec and map both claim the loader switch).

**Verification boundaries are much wider than the audit said.** Unmapped, and each owned by the first task
that touches it: `gk-core/data/tuning/**`, `gk-data/packs/fusion/data/seed/structures/**`, `data/seed/diplomacy/**`, `gk-forge/tools/seedsmith/**`,
`gk-core/tests/FusionRpg.Bench/**`, all of `gk-web/web/fusion-rpg-web/**`, every `scripts/guard-*.ps1` (`guard-dal.ps1`
included), and the new `World/{Trade,Diplomacy,Facts,Logistics/Rift}/**` directories, which resolve only to
`core-fallback`. `empire-seed-map.md:709`'s ban on this program editing `verification-boundaries.v1.json` is
**overruled for that file**: AGENTS.md is explicit that an unmapped production path is a defect to repair,
never something to compensate for with a wider suite. One row per path — a second overlapping row throws
`VERIFICATION BOUNDARY AMBIGUOUS`.

---

## 6. What the todo cannot close, and says so

Six residual gaps are written into the todo's own closing section rather than hidden: criteria whose evidence
lives in another program's suite; `escort-link` criterion 2 and `interception` criteria 2–4, inert until
multi-entity battle sides and non-district battle kinds land; corpora that can only be tested against
fixtures until their content ships; `25c.2`'s permanently `pending` entries; two publish-only tasks with no
focused suite; and two undated asks.

Two items are deliberately **not decided here**: whether `spec-member-stack.md` may edit
`WorldValidation.cs`, which `landing-order.md:163-164` fences as world-map's (default: ship without the edit),
and `gk-core/data/tuning/narrative.v1.json` (proposed; the file does not exist yet), which `npc-story-events` must
create because `publish.py` can only bump a file that exists.

Roughly **30 asks are owed to 22 other programs** (`audit-2026-09-20-global.md` §5). Five block a row and are
in §4 above; the rest are coordination — power-ladder rows, the effect-atom `int`→`long` widening, actor-hub
`SourceIds`, the battle-engine register row, the IA Diplomacy layer, the item catalyst lock, base-defense
decision 18.

Three named future programs owe an idea round before anything here depends on them for real: **`world-transit`**
(rift-gate import and export, weight-limited), **`world-derived`** (the six `world.*` channels), and the
**unit-system program** (sector-specific recruit, train and hire buildings — round 4 §U).

---

## 7. How to pick this up

1. Read `docs/DESIGN-GATE.md` §1 for the subsystem you are about to touch, **in that session**. Then the
   cluster map, then the module spec. The map wins on behaviour; the landing order wins on order.
2. Start at `0a.1`. Do not renumber task ids — downstream references and the landing order both use them.
3. Record the session boundary in `tasks/sessions/<session>.json` before the first edit, fence `paths` to the
   wave you are landing, and `git add` exactly that set. Several programs share this tree.
4. Land the wave's **one** bump by rebasing onto the current `TurnEngine.RulesetVersion` and taking the next
   integer. A capability row references the constant, never a literal.
5. Verify with the task's own `.\scripts\verify-change.ps1 -Paths <changed> -Session <id>` line. The full suite
   runs at three points only: finishing a phase, a change that genuinely crosses Core/Data/Server together,
   and immediately before a live probe.
6. Commit per task, explicit paths, no watermark. Push only when the owner asks.

**Do not:** touch `docs/architecture/npc-story-events/**` or `docs/architecture/narrative-seed/**` — another
program owns the storylet engine this family contributes facts to. Hand-edit generated seed data — fix the
generator and regenerate. Widen a test suite because a path has no boundary — add the boundary. Assert a
population count, a corpus size, or generated text anywhere.

**Multi-agent runs** read the stored owner charter before spawning (`allowed-models.json`, `approvedAt`
2026-09-20, native Claude Code only, Opus and Sonnet). Only charter models, no fallback, and a credit or quota
error stops the lane and is reported.
