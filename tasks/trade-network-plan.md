# Trade-network family — build plan

**Program:** `trade-network` (the umbrella; the family also covers `world-continuity`, `legion-build` and
`empire-seed`)
**Status:** plan, written 2026-09-20. Task list: [trade-network-todo.md](trade-network-todo.md).
**Design sources, all binding:**

| Artifact | What it fixes |
|---|---|
| [docs/architecture/trade-network/landing-order.md](../docs/architecture/trade-network/landing-order.md) | The integration ledger: wave order, one capability flag and one ruleset bump per wave, the shared-file landing order, one creator per tuning file, the golden re-bless points, the cross-program blockers. **This plan's phases are its rows.** |
| [docs/architecture/trade-network/decisions-round-4.md](../docs/architecture/trade-network/decisions-round-4.md) | Owner decisions, rounds 4, 5 and 6. Where a spec disagrees, the register wins. |
| [docs/architecture/trade-network/audit-2026-09-20-global.md](../docs/architecture/trade-network/audit-2026-09-20-global.md) | The standards audit: 3 critical, 8 major, 20 minor, and the 30 asks owed to other programs. |
| The 13 capability maps and ~150 module specs | What each module does. The map wins on behaviour; the landing order wins on order. |

---

## 1. What this program builds

A sector's goods economy, the logistics that move them, the counterparties that want them, the market that
prices them, the routes that carry them between worlds, and the surface that shows all of it. Trade existed
in this repo only as a list across a dozen documents; base-defense decision 19 deferred it to an economy
program, and this is that program.

The shape, decided in the idea rounds and not re-opened here:

- **Pooled node stock plus aggregate lane flow.** A sector holds a pooled stock (L4); a lane carries an
  aggregate flow (L3). There are never per-unit cargo agents — that is the performance decision the whole
  design rests on.
- **Buildings unlock features.** Every trade and logistics feature in a sector is opened by a specific
  building kind, and its tier widens the feature. Tiers are `variants` of one structure row.
- **Caravans are automated legions**, not a vehicle catalog. Vehicles are capacity, not entities.
- **Goods are located material.** Banking is a ledger fact that moves a good from a located stock to an
  unlocated wallet; nothing auto-banks, and loam is never traded.
- **One power ladder, one ActorHub compose, one battle engine.** Legion power is a roll-up that sums Hub
  output — never a second composer and never a private curve.

### Out of scope, named so nobody builds them here

| Not built here | Where it goes |
|---|---|
| Rift-gate import and export, and the gate's weight limits | `world-transit` — a named future program (round 6 W2) |
| The six `world.*` derived channels as a channel family | `world-derived` — a named future program (round 6 D2). Specs here consume them behind a stated default |
| Sector-specific recruit, train and hire buildings | The future unit-system program (round 4 §U) |
| `BuildResolver`, `WorldValidation`, `SlotTypeCatalog` changes | World-map's. Asks X-11 and X-14 |
| Unique items and creatures as tradeable goods | Not in v1. Legion equipment **is** tradeable |

---

## 2. Dependency graph, in one page

Read top to bottom; every arrow points down, which is what the landing order's §3 bought by turning eight
backwards edges into registration seams owned by the earlier module.

```
Phase 0  foundation + content      0a trade-foundation W0 (minus sector-features)
                                   0b empire-seed I1-I5 + schema widening + name index + metrics
                                   0c the eight feature building rows
                                   0d sector-features                      [first flag, first bump]
                                   0e legion-build W1
                                   0f world-continuity state vocabulary
                                   0g material-ledger                      [waits: save identity]
                                          |
Phase 1  the sector economy        1 stocks, capacity, halt, bank-point query
                                   2 structure loam upkeep
                                   3 structures yield goods
                                   4 the Logistics phase slot
                                          |
Phase 2  the lane layer            5 phase steps  ->  6 lanes  ->  7 policy and building
                                   9 forecast + bench
                                          |
Phase 3  outflow                   8 the banking step                      [GATE: save identity]
                                          |
Phase 4  income + fleet            10 located income · 11 legion equipment stock
                                   12 fleet W1 -> 13 fleet W2 -> 14 fleet W3
                                          |
Phase 5  counterparties            15 needs/roster/diplomacy/treasury -> 16 stance/clans -> 17 economy/sinks/conquest
                                          |
Phase 6  market + AI               18 exchange waves  ->  19 trade-ai waves
                                          |
Phase 7  cross-world               20 rift W1 -> 21 rift W2 -> 22 rift W3
                                   23 the lane-loss power switch           [needs: X-2 contest row]
                                          |
Phase 8  surface + stories         24 trade-surface · 25 trade-stories

Lanes that attach at their anchors, not at the end:
  legion-build   0d, then its later waves after rows 1 and 11 (equipment, standards)
  world-continuity  0e, then its later waves; advance-carry exposes the post-move hook rift-trade registers into
  empire-seed    0b/0c, then each structure-seed publish in its consumer's wave
```

**Phase 0's order was corrected on 2026-09-20, during planning.** `sector-features` originally sat in row
0a, but it lands `StructureDef.FeatureUnlock` and `StructureKind.Feature` — fields the anchor schema does not
have until row 0b, against rows that do not exist until 0c. It now has its own row after them, and it takes
**the family's first capability flag and first bump** (`trade.sectorFeatures`), because it turns `build` on a
structure's own slot into an upgrade instead of a `build.occupied` refusal
(`spec-sector-features.md:152-160`). That changes how an existing world's stored order resolves, which is
what a flag exists to prevent. Every later ordinal in the landing order shifted by one.

**The three sequencing facts worth memorising:**

1. **`banking-fact` lands in two waves, and that is what unblocks logistics.** The phase slot (row 4) has no
   ledger dependency; the banking step (row 8) does. If the whole module waited, every logistics wave would
   wait too.
2. **Rows 1–7 and 9 are a complete, playable economy with no outflow.** Production halts at warehouse
   capacity, structures pay their loam term and yield goods, and lanes move goods to the nearest bank point,
   where they wait. Nothing leaves the map and the report prints a banked zero **with the reason**. That is
   the throttle the ideal wants, minus the reward — and no artifact may describe the family as shippable
   before row 8.
3. **A capability gate means no existing golden moves.** Every wave runs only on a stamp that grants its
   flag, and `GrantedBy` is empty for legacy and unstamped worlds. The re-bless list is four rows long
   (landing order §6), and a golden that moves outside it is a defect to diagnose, not a re-bless.

---

## 3. Phases and checkpoints

A **checkpoint** reviews work already done and is where the owner sees a playable state. A **gate** blocks
starting work on an irreversible external fact; this plan has exactly one, and §4 says why.

| Phase | Rows | Checkpoint — what must be true to pass |
|---|---|---|
| **0 — Foundation and content** | 0a–0g | The registry ships empty and no hash moves (`GrantedBy` empty). The eight feature rows load under the neutral `StructureKind.Feature`, regenerated not hand-edited, with the corpus `--check` gate green. The seat start kit (a tier-1 Counting House and a tier-1 Storehouse) re-blesses the template world goldens **once**, shared with `empire-roster` and `clan-seeding`. Verification boundaries exist for `gk-forge/tools/seedsmith/**`, `gk-data/packs/fusion/data/seed/structures/**` and `gk-core/data/tuning/<domain>.v*.json`. `material-ledger` is the only item that may still be open. |
| **1 — The sector economy** | 1–4 | A held sector accumulates located goods, production halts at warehouse capacity instead of wasting, structures pay a loam term and yield goods, and the `Logistics` phase exists with its L3 slot empty. `bank-points` answers which sectors are bank points, so *build a Counting House* is a buildable answer. Four flags, four bumps, in order. |
| **2 — The lane layer** | 5–7, 9 | Goods move along lanes toward the nearest bank point and wait there. `route-set`, `route-clear` and `bank-hold` work; `widen` and `ward` work. The forecast reads and writes nothing. The step benchmark is inside budget at the synthetic graph's largest size. **This is the interim playable state of §2 fact 2.** |
| **3 — Outflow** | 8 | The first good leaves the map. A banking fact is written, the wallet is credited at commit time, and the report's banked total is non-zero. `material-ledger` landed first, against the re-keyed store, and the four writer sites were written **once**. |
| **4 — Located income and fleet** | 10–14 | A located reward is credited through banking. Legion equipment is a located good in a sector warehouse. A caravan legion loads, carries, unloads, is escorted, and can be intercepted — with a stated fate for its cargo. |
| **5 — Counterparties** | 15–17 | Empires and clans have needs, a roster, diplomatic facts and a treasury; relation bands move on real deltas; conquest has consequences. Four flag rows share wave 15's single bump. |
| **6 — Market and AI** | 18–19 | Orders clear at a hub, treaties have a lifecycle (war inside a minimum term writes `treaty.broken`), settlement pays at a bank point, and the AI values deals, spends under a limit and builds its own trade buildings — drawing banked goods under the same rule the player uses. |
| **7 — Cross-world** | 20–23 | A rift route carries goods between two worlds under a weight limit; endpoints sleep and can be lost. Row 23 switches lane-loss escort strength to the power roll-up. |
| **8 — Surface and stories** | 24–25 | The player can see and steer all of it in the repo's locked presentation libraries, in the `trade-lexicon` vocabulary — "unit", "enemy empires", no IP words, no named boss. Trade storylets fire from producers' own facts through the `narrative` adapter, with every trigger tested reachable. |

**Checkpoint protocol.** A checkpoint is a commit boundary, not a ceremony: run the phase's scoped
verification for every task in it, state the playable state in one paragraph, and list what is still open
with its default. A checkpoint never runs the whole suite out of caution — see §6.

---

## 4. The one gate, and why everything else is a default instead

**GATE — row 8 waits on the save-identity re-key.** `save-identity` SE4.12 → SE4.38
(`tasks/solid-enforcement-todo.md:634`, unchecked) re-keys the store. `material-ledger` and the banking step
write four ledger sites against that key. Round 6 C3 is *"wait"*: landing on the current key and re-pointing
later would edit those writer sites twice, against persisted player data, which is the one class of mistake
this repo cannot take back. Rows 1–7 and 9 do not wait, and the interim behaviour is stated in every affected
spec.

Everything else the audit called a blocker ships behind a reversible default and is tracked as a follow-up,
because a plan that freezes on a coordination ask is a plan that does not start:

| Item | Default it ships behind | Follow-up |
|---|---|---|
| Power-ladder §10 consumer rows for lane throughput, warehouse capacity, clearing capacity, located-good scale (X-4) | **Not a wait — our work.** The consuming task authors its own §10 row in the same change, which is what "consumer-authored" means. PS-5 is satisfied because faucet and sink then read one scale | Power program reviews the four rows |
| Power-ladder contest row for two rolled-up powers (X-2) | Warden defence term is **0**; escort strength stays the v1 stance count. Row 23 is last in the order for exactly this reason. **Narrowed during planning:** it does *not* block `deal-valuation` or `ai-trade-buildings` — both read the roll-up to choose, never as a contest term, and both state a default | Ask to the power program; row 23 lands when it does |
| Multi-slot `BuildResolver` and the upgrade arm (X-11) | Every feature row ships `requiredSlotKind: Wildland`, the subset every option keeps. The Trading Post's Market bonus and the upgrade verb arrive when world-map lands the two arms | Ask to world-map, before rows 0c, 1, 12, 20 |
| Verification boundaries (X-18) | **Not a wait — our work**, and wider than the audit said. Unmapped: `gk-core/data/tuning/**` (every domain this family publishes), `gk-data/packs/fusion/data/seed/structures/**`, `data/seed/diplomacy/**`, `gk-forge/tools/seedsmith/**`, `gk-core/tests/FusionRpg.Bench/**`, the whole `gk-web/web/fusion-rpg-web/**` tree, `scripts/guard-*.ps1` (`guard-dal.ps1` included), and the new `World/{Trade,Diplomacy,Facts,Logistics/Rift}/**` directories, which resolve only to `core-fallback`. Each is owned by the first task that touches it. `empire-seed-map.md:709`'s ban on this program editing `verification-boundaries.v1.json` is overruled for that file: an unmapped production path is a defect to repair, never something to compensate for with a wider suite | A second overlapping row later throws `VERIFICATION BOUNDARY AMBIGUOUS` — one row per path |
| `WorldValidation.cs` in `spec-member-stack.md` | The landing order fences that file as world-map's. `member-stack` ships without the edit if world-map has not landed its arms | Extension of ask X-11; the fence itself is world-map's to confirm |
| `EssenceCount` widens to `long` (X-5) | **Not a wait — a task in phase 0.** It is a range fix, and `essence-loop-read` will not ship half of the PS-5 loop | Coordinate the change with the creature program |
| `world-transit`, `world-derived` (round 6 W2, D2) | Every consumer reads a stated default. No spec here implements either | Idea round for each, later |
| The internal wave split and flag ids of `exchange`, `trade-ai`, `trade-surface`, `trade-stories`, `legion-build`, `empire-seed`, `world-continuity` | The todo proposes each split with its flag ids, so the owner confirms them in one reading instead of seven | Owner confirms at the phase's checkpoint |

---

## 5. Protocols for the five shared files

Eighteen modules name `TurnEngine.cs`; seventeen name `WorldState.cs`. Without a protocol these are the
program's merge conflicts, so the landing order §4 fixes each. Restated here because it is what a lane
actually needs at the keyboard:

- **`TurnEngine.cs`** — `RulesetVersion` moves **once per wave**, in row order. A lane that bumps **rebases
  onto the latest constant and takes the next integer**; the plan's `N+k` is an ordinal, never a literal, and
  a capability row references the constant. One wave at a time.
- **`WorldCanonical.cs`** — only one module at a time appends hashed rows, after the `sector-ironwork` loop
  (`WorldCanonical.cs:123-129`), in the order stamp → located stock → logistics → carried goods → later rows.
  Each spec states its slot as *"after the last conditional row present at landing"*, never an absolute index.
- **`WorldState.cs`** — additive record fields only, in row order; a field enters the hash only through the
  `WorldCanonical` order above.
- **`WorldCommand.cs`** — the system-command path lands once (closed set: `release-warden`, `rift-window`,
  `rift-arrive`); player verbs land with their waves, one kind per wave, and `WorldCommandAdmission` gains its
  arm in the same change.
- **`RpgStore.WorldTurns.cs`** — ledger tables first, then per-wave packed rows; additive columns through
  `EnsureColumn`, and a turn-log write never changes an existing column's meaning.

**One creator per tuning file** (landing order §5): `gk-core/tools/tuning/publish.py` can only bump a file that
exists, so the first module to need a domain authors `v1` **and its loader**, and every later module publishes
`v{n+1}` with its own keys. The creators are `economy-report` (`trade`), **`diplomacy-facts`** (`diplomacy` — corrected during planning:
it needs a key at row 15, before either exchange module, and §5's own rule is that the first module to need a
domain authors `v1`), **`ai-spend-limit`** (`ai.v3`, and it carries the loader switch — corrected during
planning: its own spec and its map both claim the switch, and `deal-valuation` already withdrew), `legion-cohesion`
(`legion`), `legion-bands` (`legion-seed`), `hibernation-clock` (`world-continuity`), `structure-bands` (the
next `structure-seed`, plus the consumer-added anchor fields table), and `trade-lexicon`
(`trade-catalog`). `narrative.v1.json`, which the demand shock publishes into, is `npc-story-events`' to
create — an ask, because `publish.py` can only bump a file that exists. Each creation needs a
verification-boundary owner row in the same change.

---

## 6. Verification

- **Per task:** `.\scripts\verify-change.ps1 -Paths <every added or modified path> -Session <session-id>`.
  That is the default for every ordinary edit in this program. An unmapped path is a defect to fix in the
  task, never a reason to widen the suite.
- **The full suite** (`test-fast.ps1 -AllDefault`) runs at three points only: finishing a phase, a change
  that genuinely crosses program boundaries (Core + Data + Server together), and immediately before a live
  probe.
- **Audits, when the task touches what they cover:** `python gk-core/scripts/audit-overflow.py` for any magnitude,
  `python gk-core/scripts/audit-magic-numbers.py` for anything on the balance surface, and
  `python gk-core/tools/tuning/resource_ownership.py --check` for a resource edge.
- **Guards** before finishing Core/Data/injector work: `guard-single-writer`, `guard-secondary-no-unity`,
  `guard-funnel-delta`, `guard-actor-hub`, `guard-dal`, `guard-test-substrate`.
- **Generated trees are committed and CI fails on drift.** A seed task's deliverable is the generator, its
  tuning or its registry — then regenerate and commit in the same change. Never hand-edit emitted JSON.
- **What a test may assert:** the contract, the closed enums, joins and closure, uniqueness, reconciliation,
  cross-artifact hashes, determinism, structural bounds. Never a population count, a corpus size, or
  generated `name`/`description` text. Print the scale; do not pin it.

---

## 7. Session and agent rules for this program

- **One session = one problem.** Record the boundary in `tasks/sessions/<session>.json` before the first
  edit, fence `paths` to the wave being landed, and `git add` exactly that set. Several programs share this
  tree — never `git add -A`, and never stash or reset around another session's dirty files.
- **Commits:** plain git, explicit paths, one logical change per commit, at each verified increment. Push
  and PR only when asked.
- **Multi-agent runs** read the stored charter for this creative program before spawning; only charter
  models, no fallback, and a credit or quota error stops the lane and is reported.
- **Do not touch** `docs/architecture/npc-story-events/**` or `docs/architecture/narrative-seed/**` — another
  program owns the storylet engine this family contributes facts to.

---

## 8. Open items owed outward

The audit filed **30 asks to 22 external programs**; the five that block a row are in §4. The rest are
coordination, not sequencing: power-ladder §10 rows, the effect-atom `int`→`long` widening and its owner-key
table, actor-hub `SourceIds`, the battle-engine register row, the IA Diplomacy layer and its "8 layers"
wording, the item catalyst lock, base-defense decision 18, and the verification boundaries for `web/` and
`gk-forge/tools/seedsmith/`. Each is listed with its owner in
[audit-2026-09-20-global.md](../docs/architecture/trade-network/audit-2026-09-20-global.md) §5.

Three named future programs owe an idea round before anything here depends on them for real: `world-transit`,
`world-derived`, and the unit-system program.
