# Narrative programs — handoff to the next project manager

**Written 2026-09-20, at the end of the planning phase.** Nothing in these four programs is built.
Every document below is committed on `features/mega-merge`. This page exists because the plans do not
carry the owner's reasoning, and a later session that re-derives it will get it wrong.

---

## 1. What exists, and where

| Program | Ideal | Map | Specs | Plan pair | Size |
|---|---|---|---|---|---|
| `narrative-seed` (offline content generation) | [narrative-seed-ideal.md](../docs/architecture/narrative-seed-ideal.md) | [narrative-seed-map.md](../docs/architecture/narrative-seed-map.md) | [narrative-seed/](../docs/architecture/narrative-seed/) 23 | `narrative-seed-plan.md` · `narrative-seed-todo.md` | 71 tasks, 7 checkpoints, 4 gates |
| `npc-story-events` (the runtime) | [npc-story-events-ideal.md](../docs/architecture/npc-story-events-ideal.md) | [npc-story-events-map.md](../docs/architecture/npc-story-events-map.md) | [npc-story-events/](../docs/architecture/npc-story-events/) 29 | `npc-story-events-plan.md` · `npc-story-events-todo.md` | 94 tasks, 6 checkpoints, 3 gates |
| `ip-censor` (third-party-IP release gate) | [ip-censor-ideal.md](../docs/architecture/ip-censor-ideal.md) | [ip-censor-map.md](../docs/architecture/ip-censor-map.md) | [ip-censor/](../docs/architecture/ip-censor/) 9 | `ip-censor-plan.md` · `ip-censor-todo.md` | 25 tasks, 7 checkpoints, 1 gate |
| `identity-rename` (the new IP's names) | — (rulings live in the npc ideal) | — | — | `identity-rename-plan.md` · `identity-rename-todo.md` | 19 tasks, 5 checkpoints, 1 gate |

Every map is **owner-approved**. Every spec has been through three passes: the writer's citation
audit, an independent standards audit, and a cross-program alignment pass. Both narrative plans have
been through an independent plan audit. `audit-doc-citations.py` reports **0 HIGH** on all of it.

---

## 2. The owner's rulings — the part that is not derivable

`npc-story-events-ideal.md` §10 holds R1–R23; `ip-censor-ideal.md` holds IC-1–IC-6. Do not re-open
them; do not infer around them.

| # | Ruling, in one line |
|---|---|
| R1 | The main story is **fully generated**; the chapter list is planned, the model writes the scenes |
| R2 | The antagonist speaks (story-scene's v1 deferral is lifted for this program) |
| R3 | **Seven** chapters, one per time-machine piece recovered, then endless arcs and texture |
| R4 | **One 4-band relation ladder** for characters and factions (trade-network maps onto it) |
| R5 | *Superseded by R13* |
| R6 | **No hard-coded model**: every pipeline resolves it from the environment, default Gemma 26B |
| R7 | The ip-censor design prevents blocked words at generation (prompt avoid-list) and gates at release |
| R8 | Story text uses **our own names, as tokens**; prose never names a species by its PvZ or Fusion name |
| R9 | Rename every existing player-facing surface; internal `FusionRpg.*` names stay |
| R10 | Lead names are generated and ip-censor-checked (superseded for the three leads by R11) |
| R11 | **The Garden Keeper** (was Crazy Dave) · **Hourbloom** (was Penny) · **the Rotwright** (was Dr. Zomboss) |
| R12 | **"Garden Keeper and his Multiverse"** replaces "Rise of Summoner" as the player-facing title |
| R13 | **No Nemesis-style system** (US 10,926,179 B2, active to 2036). Counter-doctrine replaces it, with six rules: no enemy grows from meeting the player, no enemy hierarchy, no enemy remembers the player personally, no base from enemy traits, no shared enemy data, warlords grow by world rules only |
| R14 | Narrative rewards come **out of** each host's existing budget, never on top |
| R15 | **The story is also the tutorial** — a closed `teaches` vocabulary, first-seen priority once per save, skippable, never gating |
| R16 | The four legacy `story` Delve events are **regenerated clean**, not retired |
| R17 | World claim loot is **pulled into npc-story-events** (`world-claim-loot`), not left to world-map |
| R18 | Counter-doctrine is **fog-correct**: the Rotwright reads only what his faction observed |
| R19 | *Superseded by R20* |
| R20 | World storylets read the **sector's own climate** |
| R21 | The **Anomaly** slot is added to `storm`, `nexus`, `barren`; new worlds only |
| R22 | The mythic claim bonus is seeded from the **world seed**, not the turn number |
| R23 | The same new template versions place **guarded Vault slots** |
| IC-1 | In scope: game and franchise marks, real-person names, company and brand names. Titles out |
| IC-1b | Player-facing "PvZ" / "Plants vs. Zombies" becomes "Fusion"; code identifiers untouched |
| IC-2 | Registry: import a trademark dataset curated down first, then census plus model proposals, each confirmed by a human |
| IC-3 | The scan is a **release gate**, never a generation blocker |
| IC-4 | Fix `Overwatch Protocol` and the `Jackson*` family before release |
| IC-5 | The registry is tracked in the repo |
| IC-6 | Aliases under 4 characters need an explicit narrow scope |
| G1 (ip-censor) | **Yes**: re-key the `Jackson*` species ids too (task T19b, with a backed-up migration) |
| G1 (rename) | **No** migration of names already stored in saves |

---

## 3. Build order across the four programs

1. **`ip-censor` and `identity-rename` are ready now** and do not wait on the narrative programs.
   `identity-rename` should land its names registry early, because `narrative-seed` adopts it (whoever
   lands first owns the file; the other adopts).
2. **`narrative-seed` waves 0–4 spend no model calls** — model-literal removal, the script check, the
   motif gloss registry, the dungeon generator repair, registries, contract, emit, validators,
   metrics, review rendering, lore packet, planner. Start here.
3. **`npc-story-events` waves 0–2** can run in parallel with the above, up to the point where its
   loader needs the seed contract.
4. **The Delve cutover is ONE change across both programs** (narrative-seed `delve-event-regen` +
   the runtime loader switch + party-dungeon's room pools). Do not split it.
5. **The two web modules** (`storylet-card`, `quest-log-layer`) are blocked on `/idea-ui` and carry no
   tasks.

---

## 4. Dependencies on programs this handoff does not own

| Needed | Owner | Effect if it does not land |
|---|---|---|
| `WorldCreation.Rebuild` (versioned template rebuild) | `world-continuity` | The Anomaly/Vault template versions (R21, R23) cannot ship; editing a template would change existing worlds' replay |
| `world-victory` / `world-fall` facts | `world-continuity` | Spine progress cannot pass its opening chapter; world-scope story state has no freeze trigger |
| Extraction / `CloseDelve` route | `party-dungeon` | Delves cannot be completed; the rest of the Delve live path is transferred here (D4.16, D4.22, D4.14, D3.9, D3.3, D3.5 — see the dated note atop `party-dungeon-todo.md`) |
| `AchievementEvaluator` hosting | `achievement-title` | Quest and story facts produce no achievements |
| Player-routed push | `notification-ssot` | Story notifications have no transport |
| Item base price | item program | Delve merchants stay sell-nothing |
| `/idea-ui` for the two web surfaces | UI program | The storylet card and quest log have no design |
| TVB3.3 / TVB4.6 / TVB4.7 boundary rows | `test-verification-boundary` | Two mapping tasks in each plan wait |

---

## 5. Sequencing conflicts already found and resolved

- `identity-rename` **T13 before** `npc-story-events` **NR2.32** when both are in flight: they re-bless
  the same world-template goldens.
- `ip-censor` T16/T1/T11 touch `report/cli.py` and `ci.yml`, which `narrative-seed` NS6b re-orders.
- `npc-story-events` NR2.2 edits files party-dungeon's still-open D3.3/D3.5/D3.9 live in.

---

## 6. Known defects these programs inherit (not caused by them)

- 53 of 54 committed Delve event seeds carry Chinese motif fragments in English text; the cause is the
  prompt (theme motifs are Chinese and the brief asks the model to use one). Fixed by
  `narrative-seed` wave 0, never by hand-editing the seeds.
- `climateAffinity` was model-authored and is skewed: 39 of 54 events chose `none`, and ice, earth and
  light never appear (15 of 42 cells covered). The planner takes the field over.
- Two of four story chains point at events that do not exist, because the planner forges a `-{n+1}`
  terminal id.
- `guard-generated-seed.py` only reads a top-level `_meta`, so it misses generated files whose
  provenance sits elsewhere. Reported, unfixed, owned by nobody yet.

---

## 7. How to pick this up

Read, in order: this page → the program's ideal §10 (rulings) → its map → its plan → its todo. The
todo carries status; the plan does not. One task is one commit (code, tests, evidence, the todo
line). Gates need the owner. Session boundary and charter rules in `AGENTS.md` and `CLAUDE.md` apply
as always — in particular, a multi-agent run needs the owner's charter in the current conversation
before any worker starts.
