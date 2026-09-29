---
name: seedsmith-design
description: Design a seedsmith generation feature — a seed contract, an LLM pipeline, or a runtime concrete-generator. Loads the three domains a seedsmith design needs at once (this repo's generation principles, game-design prior art, and AI-native contract rules) and refuses the failure modes each one has already cost. Use for any seedsmith idea or spec work — species anchors, item seeds, action seeds, effect containers, roster metrics — before /idea or /spec.
---

# Seedsmith design

The domain layer under `/idea` and `/spec`. Those skills own the *process*; this one owns the
*knowledge* — what a generator is allowed to decide, what a good roster looks like, and what a language
model can be trusted with.

**Use it for:** a new seed contract · an LLM pipeline · a runtime concrete-generator · an effect
container · roster/coverage metrics · anything that turns lore into content.

**Then run `/idea` or `/spec` for the deliverable.** This skill does not replace them; it is what you
load first so the deliverable is not written against a system you misread.

---

## ⛔ Step 0 — state these out loud before reading anything else

Restated inline, not linked. **A pointer does not survive a long session, and the moment you need these
is the moment they are out of context.**

### Law 1 — Seed → concrete → per-player. Three layers, and the middle one rolls.

Owner, 2026-09-01, stated as binding for **every** generation feature:

> *"Seedsmith generate seed, game generator in game runtime generate concrete object, per player game
> store that object … every generator use this sdk baseline, so no need to duplicated code for all."*

```text
SEED       seedsmith, offline, enums only, no magnitudes      committed, diffable
   |
   v       the GAME RUNTIME resolves it - seeded per player, like Diablo loot
CONCRETE   Instantiator.TryInstantiate(container, lookup, rollSeed, thetaContent, ...)
   |
   v
STORED     that player's own tables. "each player play they own game"
```

**The SDK is already built and already reused.** `Instantiator.TryInstantiate`
(`gk-core/src/FusionRpg.Core/Effects/Atoms/Instantiator.cs:92`) rolls a container into an `InstanceRow` with
`RollSeed`, `CatalogRevision`, `ThetaContent` and `ContentFingerprint()` — reproducibility over
`(container_id, catalog_revision, roll_seed)`. `ActionSeeder.cs:19,45` already reuses
`Instantiator.Draw` **verbatim**, *"unchanged, only its visibility widened."*

**So never design a second roll.** Before proposing any generator, check whether the container-roll path
already does it. It usually does — and `TryInstantiate` currently has **zero production callers**, which
makes almost every "we need to build a generator" finding a **wiring gap**, not a new build.

### Law 2 — The LLM writes identity. Deterministic code writes magnitude.

Seedsmith P1, and the reason is a property of the model:

> *"a model has no calibrated sense of scale, so a number it picks is a plausible-looking guess that
> survives review because nothing looks wrong with it."*

A wrong enum is visible. A wrong number is not — `hp: 4200` reads exactly as plausibly as `hp: 2400`,
and over 900 entries nobody re-derives it. **Enforced mechanically by a schema audit, never by review.**

### Law 3 — Every RPG feature lives in the RPG layer.

Never built by changing what PvZ is. The lawn keeps its own numbers; only a signed progression delta
crosses. *"Does the lawn support X"* is almost always the wrong question — ask whether the RPG layer has
a channel/atom/runtime for it (usually yes), then whether that path is **wired** (often not).

### Law 4 — One power ladder.

Contests read `Θ` (linear, difference-based). Magnitudes read `P(Θ)`. Any number derived from a level
goes through `ssot-power-scale.md`; its §10 inventory is a **closed list**. Writing a fresh `f(level)`
in a subsystem is how three incompatible curves came to ship at once.

### Law 5 — The numeric rules are design constraints, not code details.

Overflow is a **range** question: `long` for every integer magnitude `P(Θ)` can grow · widen before
multiplying · in integer per-mille math divide by 1000 last, exactly once · integer **overflow throws,
never wraps**. **Floating point is allowed** (owner ruling 2026-09-15): a `float` or `double` not being
integer-exact past 2^24 / 2^53 is precision, not overflow — the old "never `float`" line here is void.
And **no hard progression ceilings** — a cap on a magnitude is removed or made a configurable soft cap.

### Law 6 — A number a balance pass would change lives in `gk-core/data/tuning/`, not in code.

Policy, Catalog, Rules, Ruleset and Math files **are** the balance surface. When both readings are
defensible, it is tunable.

---

## Step 1 — the reading gate

`docs/DESIGN-GATE.md` is binding: **read → verify against code → propose.** Read these *in this
session*, not from a summary. Pick the rows that apply.

| Designing… | Read |
|---|---|
| **always** | `docs/research/ai-native-generation/README.md` · `docs/architecture/seedsmith-map.md` (P1-P5) |
| a **seed contract** | `docs/architecture/item/seed-contract.md` §1-§3 — the one law and the four ownership levels |
| a **roster / taxonomy** | `docs/research/game-design/` — all seven files, or at minimum `README.md`, `03-roster-scale.md`, `05-failure-modes.md` |
| an **LLM pipeline** | `docs/architecture/seedsmith/spec-pipeline.md` · `spec-workflow-runtime.md` |
| an **effect container** | `docs/architecture/effect-atom/definitions.md` **in full** — it wins over any spec |
| anything with **magnitudes** | `docs/architecture/power/ssot-power-scale.md` §4, §5, §10 |
| **rarity** | `docs/architecture/item/ssot-rarity.md` §3.3, §3.5, §8 |
| **metrics** | `docs/architecture/seedsmith/spec-metrics.md` · `spec-quality-gates.md` |

**Three gate rules that get broken most:**

- **A comment is not evidence.** Code beats docs; docs beat comments. Open the file.
- **Read the section, not the line.** A rule under *"what the Server may do during a run"* is not a
  universal law.
- **Test the constraint before declaring it.** *"This moves goldens"* / *"this needs sign-off"* are
  claims. Run the suite first.

Sort every finding into **built · wiring gap · real gap**, using those exact words, with `file:line`. A
default-off toggle, a null delegate, a debug-only entry point, or a missing argument at every call site
is a **wiring gap** — never report one as an architectural limit.

---

## Step 2 — the game-design questions

From `docs/research/game-design/`. Answer these *with numbers* before proposing a taxonomy.

**① Grid density — the ratio that decides roster design.**
`axis_combinations × second_axis` vs roster size. Measured bands: **~3.6 units per cell is the safe
zone** (Genshin/FGO); **~12.6 per cell is the failure zone** (Fire Emblem Heroes). This is what forces
dual typing rather than making it flavour. Compute it; do not estimate it.

**② Distinctness is carried by abilities, not stats.**
Type + speed modes + resistances lifts creature uniqueness from **63% to 93%**. A 900-unit roster needs
roughly **1,500-3,500 named ability instances**. **A complete anchor is not a complete roster** — say so
explicitly, or a downstream session will think the job is done.

**③ Know which axis is cheap to widen, and widen only that one.**
Every studio widened the axis with the fewest downstream dependencies. FEH widened weapon colour (feeds
one ±20% modifier) five times and **never** touched movement type (~100 skills key off it). Name your
cheap axis in the doc.

**④ Rarity buys breadth and ceiling. In every game studied, never power.**
A rung sets a **count band** and a **tier window** — how many effects roll and from which tiers. A
multiplier on the rung makes rarity dominant and destroys the overlap that makes low rungs live content.

**⑤ Ordinals, never numbers.**
`threatBand`, `attackTempo`, `reach` are ordinals the deterministic layer turns into intervals — the
same way a band becomes a magnitude. If you are about to let a model pick "1.5 seconds", stop.

**⑥ Check the failure modes before proposing, not after.**
`05-failure-modes.md` has the corpses. The two that recur: **distribution skew** (D2's Hammerdin — every
individual number defensible, the *offering* degenerate) and **a stronger version is not a different
unit** (a faster Banshee is still a Banshee — so power and rarity are not distinctness axes).

**⑦ Before searching the web, read `06-unsourced.md`.**
Eight research passes and several hundred searches already established what does **not** exist — no
studio has ever published a quantified counter-strength target, no threshold at which a matrix becomes
unlearnable, almost no designer commentary on roster design anywhere. **Re-running those searches costs
the same budget for the same nothing.**

---

## Step 3 — the AI-native contract rules

Full detail in `docs/research/ai-native-generation/README.md`. The load-bearing short form:

- **Enum selection is the most bias-prone task shape there is**, and an enum-only contract is entirely
  made of it. Reordering options alone swings accuracy by up to 75 points.
- **Permute every enum, seeded from `(entity_id, field, sample_index)`.** Free. `sample_index` must be
  *inside* the seed or the three votes are one sample with extra steps.
- **Majority-vote only the load-bearing fields.** Voting everything triples the run.
- **1-1-1 → `unresolved`**, never the first option.
- **A closed contract is a well-defined structure with a description per attribute — not a frozen
  vocabulary.** Every description needs a **negative clause** saying what the field is *not*.
- **`none` is a value; a missing key is a defect.** Tag absence is a stat.
- **Prove constrained decoding is on** with one real call before the run.
- **TRANSIENT ≠ QUALITY retry.** A pause is transient — replay, no new call. Name the defect when
  re-prompting; bound repairs at two.
- **Stochastic output breaks idempotency and you will not notice.** Provenance + `stale_ids()` +
  byte-identical rerun proven by hash. This repo has already shipped this bug once.
- **Every metric declares closed-loop or open-loop.** An open-loop metric never contributes to a pass.
- **Tests never call a model.** Stub the transport so it *raises*.
- **Compute the call budget before choosing a decomposition** — it decides the architecture, not the
  schedule.

---

## Step 4 — the deliverable

| Phase | Path | Rule |
|---|---|---|
| idea | `docs/architecture/<program>-ideal.md` | findings sorted built/wiring-gap/real-gap with `file:line`; prior art with numbers; open questions only where the answer changes the work |
| capability map | `docs/architecture/<program>-map.md` | module ids, dependency direction, build order — approved before any module spec |
| spec | `docs/architecture/<program>/spec-<module-id>.md` | one per module |
| plan | `tasks/<program>-plan.md` · `tasks/<program>-todo.md` | **always the prefixed pair** |

**`SPEC.md`, `tasks/plan.md` and `tasks/todo.md` are not defaults and not fallbacks.** Do not read them
to check whether they are free. State the paths you wrote.

**Restate load-bearing principles inline in the doc** rather than linking — a downstream session reads
the doc, not its links.

**Order the build so the model-free modules come first.** A parse, a table, a schema and a dump produce
real value with **zero tokens spent**, and they make the expensive stage's inputs reviewable.

---

## Refuse to ship a design that does any of these

| Red flag | Why |
|---|---|
| a model picks a magnitude, a weight, a probability, or a duration | Law 2 |
| a new roll implementation beside `Instantiator` | Law 1 — *"no need to duplicated code for all"* |
| a private `f(level)` in a subsystem | Law 4 |
| an `int` magnitude `P(Θ)` can outgrow, or a hard `Math.Min` cap on a magnitude | Law 5 |
| a threshold literal in a Policy/Catalog/Rules file | Law 6 |
| an enum with no `none` and no stated reason | tag absence is a stat |
| a description with no negative clause | half-written |
| a vote set chosen by vibes rather than by cost-of-being-wrong | budget |
| "the lawn cannot express X" | almost always a wiring gap — cite the inert line |
| a taxonomy proposed without computing grid density | ① |
| an open-loop metric contributing to a pass | P3 |
| a generated tree that is not committed | *"a generated row nobody can diff is a row nobody can review"* |
| re-running the searches `06-unsourced.md` already exhausted | budget |

---

## Related

- `docs/research/ai-native-generation/README.md` — the AI-native half, in full
- `docs/research/game-design/` — the game-design half, seven files
- `docs/architecture/demon-seed-ideal.md` · `-map.md` · `demon-seed/` — the worked example
- `docs/architecture/item/seed-contract.md` — the seed law
- `docs/DESIGN-GATE.md` — the binding reading gate
