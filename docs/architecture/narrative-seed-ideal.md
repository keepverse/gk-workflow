# Narrative seed — the ideal

> ### ⚠️ Status line vs. what shipped (checked 2026-09-20)
>
> **This document's status line is not current, and so is its own map's.**
> [narrative-seed-map.md](narrative-seed-map.md) reads **"Map approved by the owner 2026-09-19
> ('approve, go'). Module specs authorized"** — but its own prose still says *"No module spec is
> written until the owner approves..."*. Measured directly against the tree today: **23** module
> specs already exist at `docs/architecture/narrative-seed/spec-<module-id>.md`. No
> `tasks/narrative-seed-todo.md` exists in this worktree yet.
>
> Read this document for its reasoning and its decisions, never for its status. Verify anything
> load-bearing against the module specs and the code directly — the map's own prose is stale here
> too.

**Status:** idea phase, 2026-09-19. Not a spec. No build authorized.
**Program id:** `narrative-seed`.
**Owner request (2026-09-19):** *"do you have seedsmith generate for npc, event and story, they
interactive? if not we need idea for this."*
**How this was produced:** `/idea` under the `seedsmith-design` skill. Two read-only survey agents
(seedsmith's dungeon pipeline; the runtime contracts generated content must land in) and one prior-art
research agent, under the charter the owner approved earlier in this conversation. Every load-bearing
agent claim was re-checked against code in this session.

**Relation to other programs:**

| Program | Owns | This program's relation |
|---|---|---|
| [npc-story-events](npc-story-events-ideal.md) | The **runtime**: one storylet engine for every place, characters, relations, story ledger | This program is its **content supply**. It defines the seeds; that program resolves them |
| [party-dungeon](party-dungeon-ideal.md) | The Delve, its event deck and its dungeon seed contract | The event anchor **widens** here instead of forking; the Delve is the first consumer |
| seedsmith core ([seedsmith-map.md](seedsmith-map.md)) | Corpus, budget, metrics, planner, pipeline, workflow runtime, quality gates | Adds one adapter (`narrative`). The core stays feature-agnostic (P5) |
| [story-scene](story-scene-map.md) | The scene player and its script format | Spine chapters feed it; nothing here builds a second player |

---

## 0. The short answer

| Content | Does seedsmith generate it? | Is it interactive? |
|---|---|---|
| **Delve events** | **Yes** — 54 committed seeds, 6 kinds (`gk-data/packs/fusion/data/seed/dungeon/events/`), from the dungeon adapter | **No.** The seed has no choices. An event's `outcomes[]` is a weighted **result table**: the game draws one outcome; the player never picks between authored options. The runtime offers three fixed verbs — `use`, `interact`, `leave` (`gk-core/src/FusionRpg.Core/Delve/Events/EventChoices.cs:11-13`) — and all three resolve against the same draw. There is also no route to answer an event, so nothing reaches a player at all (§4.2) |
| **Delve quests** | **Yes** — name and flavor over closed objective templates | Objectives only; no choices. Quest `chainRef` is always `"none"` |
| **NPCs / characters** | **No.** No character contract exists anywhere | — |
| **Dialogue** | **No.** Wild creatures talk through 8 verbs with **no text at all** (`TalkTree.cs:6`) | Verbs only |
| **Story** | **No.** The `story` event kind is four rows chained by a planner placeholder, two of them to events that do not exist. Authored scenes are TypeScript literals (`RIFT_PROLOGUE_SCRIPT`, `sceneScript.ts:105`; Reconciled 2026-09-19: `:32` is the `SceneBeat` type; the literal is at `:105`) | Linear only |

So the answer is: **events yes but not interactive; NPCs, dialogue and story no.** The rest of this
document is the design for generating all four, interactively, under the rules this repo already
enforces for generated content.

---

## 1. Principles that constrain every choice below (restated, not linked)

1. **Seed → concrete → per-player.** seedsmith emits **seeds** offline: identity, and picks from
   closed lists. The game runtime turns a seed into a **concrete** object per save, seeded and
   reproducible, through the one roll SDK (`Instantiator.TryInstantiate`,
   `gk-core/src/FusionRpg.Core/Effects/Atoms/Instantiator.cs:98`; the event path already calls it at
   `gk-core/src/FusionRpg.Core/Delve/Events/EventDeck.cs:303`). Nothing here designs a second roll.
2. **The LLM writes identity; deterministic code writes magnitude.** A model has no calibrated sense
   of scale, and a wrong number looks exactly as plausible as a right one. So a model never picks a
   number, a weight, a probability, a cost or a duration — **and never writes one into prose**: a line
   that says "gain 50 souls" is a magnitude with no owner. Enforced by schema audit, never by review.
3. **No model at runtime.** *"The game runtime … never calls a model"* (`party-dungeon-map.md:29`);
   *"Identity at runtime is template composition, NOT a model"* (`action/spec-action-seeding.md:74-77`).
   Play is local and offline. Interactivity is authored offline and resolved deterministically.
4. **A closed contract is a well-described structure, not a frozen vocabulary.** Every field carries a
   description **with a negative clause** (what it is *not*). Every closed enum admits `none`;
   `additionalProperties: false`; every field required. A missing key is a defect; `none` is a value.
5. **Enum choice is the most bias-prone task a model does.** Reordering options alone swings accuracy
   by up to 75 points. Every enum is permuted, seeded from `(entity_id, field, sample_index)`;
   load-bearing fields get a 3-sample majority vote; a 1-1-1 split is `unresolved`, never the first
   option. This program's own survey found the bias live (§4.4: the model left 39 of 54 events
   climate-free and never chose ice, earth or light).
6. **The plan is deterministic** (seedsmith P4). A pure function decides which content to write, in
   what order, with which constraints. No model decides what work to do.
7. **A metric without a declared target is an opinion** (P2), and **every metric says whether it can
   verify its own fix** (P3). Open-loop checks ("is this line in character?") produce a review queue,
   never a pass.
8. **Generated data is never hand-edited.** Fix the generator and regenerate. The 54 existing events
   are regenerated under the widened contract, not patched.
9. **A guardrail validates the contract, never a population.** Corpus size is a reading. Tests assert
   closed enums, joins, uniqueness and structural rules, never "54 events".
10. **One power ladder.** A contest reads `Θ` difference; a magnitude reads `P(Θ)`. Seeds carry bands;
    the runtime resolves them.
11. **The balance surface is data.** Runtime numbers live in `gk-core/data/tuning/`; seedsmith's targets live
    in its `budget`.
12. **Every RPG feature lives in the RPG layer.** Narrative never touches what PvZ is.

---

## 2. Which loop this extends

Content supply for [the-loops.md](../guide/the-loops.md) **7. Quests and events** (primary), and
through it **6. The Delve**, **4. World map**, **5. World stage**, **2. Idle expeditions** and
**B. Summon** (characters who join). No new loop. The runtime side of each is
[npc-story-events-ideal.md](npc-story-events-ideal.md) §6.6.

---

## 3. What "interactive" means here

Three levels, all authored offline and resolved deterministically:

| Level | The player… | Seed content |
|---|---|---|
| **Choice** | reads a situation and picks one of 2–4 options; each option has its own condition and its own consequences | a **storylet** with `choices[]` |
| **Conversation** | talks to a character over a few turns with the talk verbs; the character answers in its own voice, differently when it likes or hates you | a **character** with lines per context and disposition band |
| **Consequence** | meets the same character again, finds a chain continue three rooms or turns later, or finds a failure opened new ground | **arcs**, flags and relations |

**Not in scope, deliberately:** free-text player input, a model generating replies during play (§1.3),
and branching dialogue trees (rejected in `npc-story-events-ideal.md` §6.11 — storylet choices plus
talk verbs cover the need, and *80 Days* showed one playthrough reads about 2% of a branching script).

---

## 4. What already exists

### 4.1 Built (works end to end)

| What | Evidence |
|---|---|
| **The dungeon adapter's generation machinery**: per-field ownership levels (AUTHORED, PLANNED, VALIDATED, DERIVED, GENERATED), per-call JSON schemas, bounded quality retry that names the defect | `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/schema.py:1-5`; event schema `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/briefs.py:273`; retry `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/pipelines.py:328` (`MAX_QUALITY_RETRY`) |
| **Enum permutation seeded from the id and sample index**, reused by dungeon | `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/anchor/permute.py:26-33` (`order_for`); dungeon use `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/pipelines.py:67` |
| **Majority vote** with `unresolved` on a 1-1-1 split | `creatures/anchor/vote.py:26-43` (`resolve_vote`) |
| **Transport with constrained decoding**, proven by test | `pipeline/llm_caller.py`; `tests/test_llm_caller.py:225-232`. Model: local `google/gemma-4-26b-a4b-qat` (`llm_caller.py:47`) — the locked seedsmith model (`seedsmith-map.md` §3d, *"Local Gemma-26B, no hosted tier"*) |
| **Offline tests**: the transport stub raises on a real call | `tests/test_dungeon_event_pipelines.py:49-58,171-176` |
| **Prose validators** | `gk-forge/tools/seedsmith/seedsmith/workflow/validators/field_echo.py` — `field_echo` (a value echoing its field name; 7 of 8 outputs did it once), `subject_name_echo` (`:48`; 83 of 83 once) and `name_collision` (`:69`); `language.py` (`language_consistency`, CJK/Latin mixing); `motif.py`; corpus-wide `metrics/dedup.py` (`SemanticDedup`: exact, canonical-word-set, MinHash near-duplicate) |
| **Runtime event engine, seed to magnitude** | `EventCatalog.Load` → `EventFilters` → `EventDraw` → `OutcomeResolver` → `EventEffectContainerBuild` → `Instantiator.TryInstantiate` (`EventDeck.cs:303`) → `EventDeck.Answer` (`:339`). An outcome's `{family, powerBand}` becomes a magnitude through `ContentScale` once (`Instantiator.cs:116`) — the right shape for generated consequences |
| **A 16-leaf predicate vocabulary**, all compiled and readable, including the four event leaves (`BandIs`, `HaulAtLeast`, `RoomKindIs`, `PartyDownedCount`) | `gk-core/src/FusionRpg.Core/Effects/Atoms/PredicateNode.cs:28-46`; `PredicateCompiler.cs:143-152,205-208`; `FactReader.cs` |
| **Keyed text as a seed rule** — every entry carries a key and its string, authored together; a second locale is a file drop | `item/seed-contract.md` §6 |

### 4.2 Wiring gap (exists, inert — not a wall)

| What | The inert line |
|---|---|
| **The language check never runs during generation.** `language_consistency` exists and was written after this exact defect, but the dungeon adapter never imports it (only `creatures/commander_effect.py`, `trees/nodegen/run.py` and the post-hoc metric do); its retry loop checks only motifs. And its script test is narrow: `_CJK = re.compile(r"[一-鿿]")` (`workflow/validators/language.py:33`) covers U+4E00–9FFF only — not CJK extension A, compatibility ideographs, CJK punctuation, fullwidth forms, kana or Hangul | `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/pipelines.py:334`: `problems = motif_coverage(draft, context) + anti_motif_violation(draft, context)` |
| **Event eligibility cannot be loaded.** Seeds may only say "always eligible" | `gk-core/src/FusionRpg.Core/Delve/Events/EventSeedFile.cs:40-44` throws `NotSupportedException` for any non-null `eligibility` |
| **No route answers an event**, and no production code calls `EventDeck.Resolve`/`Answer` | `src/FusionRpg.Server/DelveEventEndpoints.cs` does not exist; `gk-core/tests/FusionRpg.Data.Tests/Delve/EventSeenStoreTests.cs:12-13` records it |
| **Event text has no wire path**: `EventView` carries no `name`/`flavor` | `gk-web/web/fusion-rpg-web/src/contract/types.ts:1276-1282` |
| **Run ledger and staleness exist but dungeon does not use them**; dungeon has no `PROMPT_VERSION` and no committed orchestrator from `pipelines.py` to `emit.py` | `pipeline/run_ledger.py`, `pipeline/staleness.py`; dungeon `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/completeness.py:19` says so |
| ~~**The model is hard-coded in 11 places.**~~ **CLOSED 2026-09-23** (NS3–NS6): zero model literals and zero `DEFAULT_CONFIG` references outside `pipeline/llm_caller.py`, enforced by `gk-forge/tools/seedsmith/tests/test_no_model_literal.py` (7 tests, shapes S1–S5). The history below is what the gap WAS. seedsmith already resolves the model from `.env` (`SEEDSMITH_LLM_MODEL`) → `seedsmith.toml` → the `LlmCallerConfig` default (`pipeline/llm_caller.py:47,66-78`), but seven adapter files carry their own `"google/gemma-4-26b-a4b-qat"` literal as a function or CLI default and bypass that layer: nine in five `adapters/actions/*` files (e.g. `generate_action_pipeline.py:78,180`), `adapters/creatures/generate_commander_effects.py:71` and `adapters/effects/affix/generate_affixes.py:378`. Two emit helpers also default provenance to a model the run did not use — `model: str = "claude-sonnet-5"` in `adapters/items/affixfamgen/emit.py:124` and `adapters/items/basetypegen/emit.py:152`. (Corrected 2026-09-19 by the map pass: this row first said 14 literals in ten files, counting a comment and a mention in `items/uniques/briefs.py:158`.) Reconciled 2026-09-19: the wave-0 spec (`narrative-seed/spec-model-config-resolve.md` §2) counts **three bypass classes**, not two: (A) the 11 executable literals above; (B) **six** provenance-stamp defaults, not two — the two `claude-sonnet-5` emit helpers plus four invented provenance names (`basetypegen/run.py:287`, `droptablegen/run.py:216`, `gemgen/run.py:254`, `recipegen/emit.py:221`); (C) functions and CLI flags that default to `DEFAULT_CONFIG` and so skip `.env` and `seedsmith.toml` (e.g. `adapters/creatures/generate_families.py:73-74`). The spec's guard test, not this count, is the contract — and that test is green | Owner ruling R6: no hard-coded model. Every call site reads the resolved config; a test fails on any model literal outside `llm_caller.py` |
| **Outcome count pinned to 2** (the contract allows 2–4) because array-position voting was never built | `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/briefs.py:236` (`EVENT_OUTCOME_COUNT = 2`), reason at `:227-235` |
| **Talk resolves no turns**: `/talk` only commits an already-resolved join | `gk-core/src/FusionRpg.Server/DelveWildEndpoints.cs:14-22` |

### 4.3 Real gap (no mechanism anywhere)

| What | What must be built |
|---|---|
| **Player-facing choices** — option text, a per-choice condition, per-choice consequences. Not in the seed (`spec-dungeon-seed-contract.md` §1.4), not in `EventOutcomeRow` (`EventRow.cs:14-18`: `(Ordinal, DropBand, Consequence, Effects)` only). `spec-event-deck.md` §6 left it as *"a seed-contract widening — ask first"*; this document is that ask | The storylet contract (§6.2) |
| **A character contract**: name, role, voice, lines | §6.3 |
| **Arcs**: multi-part stories with a cast that persists across links | §6.4 |
| **A party-composition predicate** ("a fire creature is in the party") for roster-keyed choices | One reviewed `LeafId` addition plus its `FactReader` field |
| **Generated text into translation catalogs.** Lingui accepts only compile-time literals: *"`msg({ message: someRuntimeString })` is a hard error"* (`gk-web/web/fusion-rpg-web/src/features/story-scene/messages.ts:13-19`). The committed catalog holds 45 ids, none for events or quests | §6.8 |
| **Name quality bounds**: no adapter has a length bound or a banned-word list (survey, grep) | Two tier-2 validators |

### 4.4 Built, but defective (the current corpus)

| Defect | Evidence | Fix |
|---|---|---|
| CJK fragments in English text in 53 of 54 events. **Caused by the prompt:** every theme's motifs are Chinese almanac words (`gk-data/packs/fusion/data/seed/creatures/_registry/themes.v1.json`, e.g. `从天而降, 仙剑, 召唤`), and the event brief says *"Use at least one of the listed motifs"* (`adapters/dungeon/briefs.py:324`, motifs injected at `:354`). The leaked words are the motifs themselves. None of the other 230 dungeon seeds leaks — rooms, domains and quests get no motifs | Counted this session; the bulk batch (`9aad045cf`, 2026-09-07) predates the language check | **Fix the cause first**: pass motifs as target-language glosses from a deterministic lookup, never as foreign-script tokens to quote. Then wire a widened script check (§4.2) and regenerate |
| Two of four story `chainRef`s point at events that do not exist | Planner flattens all story cells of a run into one sequence and invents `-{n+1}` for the last (`gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/pipelines.py:300-310`) | Arcs generated as units (§6.4); a dangling ref fails preflight |
| **Climate skew**: `climateAffinity` is model-authored (`gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/schema.py:123` sets it AUTHORED; the enum is at `:240`), and 39 of 54 events chose `none`; fire 12, air 2, dark 1, **ice, earth and light 0**. Only 15 of 42 kind × climate cells hold anything | Counted this session over the committed seeds | Make climate **PLANNED** (the planner allocates cells); add a coverage metric per cell |
| `story` short of its plan: 4 of a planned 10; every other kind has 10 | Survey, from the plan in `allocate_event_targets` | The planner re-plans the gap |

---

## 5. Prior art

Researched 2026-09-19. It extends, and does not repeat, `npc-story-events-ideal.md` §4 (selection,
pacing, relationships), `empire-progression-ideal.md` (Ghostwriter's two candidates, MarioGPT) and
`research/game-design/06-unsourced.md`. **(computed)** marks a count from shipped data files;
**UNVERIFIED** marks a claim that could not be confirmed. The web-search quota ran out partway, so
consistency checking (§5.2c) has no fresh source.

### 5.1 Production pipelines

| System | Structure and numbers | Failure mode | Lesson |
|---|---|---|---|
| **Hidden Door** ([Engadget](https://www.engadget.com/how-do-you-prevent-an-ai-generated-game-from-losing-the-plot-170002788.html), [interview](https://aigamechangers.substack.com/p/the-machine-is-not-itself-creative)) | "Thousands" of story-thread templates; *"every template is either handwritten or generated and hand-edited by a person"*; an arc is 3–4 templates; each turn offers 3 suggested actions (≈⅓ advance plot, ⅓ mischief, ⅓ character callback); *"turning generation problems into ranking problems. You can do generation offline, when you have the luxury for quality control, and ranking in real time"* | — | **This is seedsmith's architecture, already shipped by someone else**: offline generation with human review, deterministic selection at runtime |
| **Ubisoft Ghostwriter** ([Ubisoft](https://news.ubisoft.com/en-us/article/7Cm07zbBGy4Xml6WgYi25d/the-convergence-of-ai-and-creativity-introducing-ghostwriter); [GDC 2023](https://www.gamedeveloper.com/marketing/here-are-more-details-on-ubisoft-s-narrative-ai-tools-from-gdc-2023)) | Barks only, never cinematics or lore; writer picks from 2 candidates. Acceptance varied **by register**: "confident"/"excited" often accepted, "curious" almost always rejected, "apologetic"/"surprised" frequently rejected | Models *"keep repeating [patterns] if they aren't guided with multiple inputs"* | Measure acceptance per voice register, not per corpus; weak registers need exemplars or a human pass |
| **Inworld / NEO NPC** (runtime; [MIT TR](https://www.technologyreview.com/2024/06/25/1094202/my-colleagues-turned-me-into-an-ai-powered-npc-i-hate-him/)) | An NPC told not to be sarcastic stayed sarcastic; told to tone it down, it swung to exaggerated friendliness | Tone instructions overshoot | Express voice through **example lines**, not adjectives |
| **AI Dungeon** ([case study](https://www.techdirt.com/2021/11/17/content-moderation-case-study-game-developer-deals-with-sexual-content-generated-users-own-ai-2021/)) | A keyword filter flagged *"cockpits, breastplates and 4-year-old laptops"* and soft-locked stories | Word lists without word boundaries | Any word-list gate over prose needs word-boundary matching and a measured false-positive rate |
| **Microsoft GENEVA** ([MSR](https://www.microsoft.com/en-us/research/blog/geneva-uses-large-language-models-for-interactive-game-narrative-design/)) | GPT-4 branching graphs; *"better known … stories yield richer … adaptations"* | Generic output on obscure worlds | PvZ Fusion lore is obscure: **ground every call in an explicit lore packet**, never "the world of PvZ" |
| **Hades** (computed from the shipped-Lua mirror) | 19,510 voice cues; Zagreus 8,122; Hades 1,561; Megaera 1,136; Thanatos 833; recurring characters 350–560; each Olympian ≈180–215 | — | Budget lines by tier: ~200 for a frequent visitor, 350+ for a relationship character |
| **Failbetter** ([parsimony](https://www.failbettergames.com/news/narrative-snippets-parsimony-2)) | *"any one character [should] see 90% of your content, not 50% or 10%"*; "a river rather than a tree"; few qualities, reused | — | Gate content on **few** conditions so most saves see most of it |

### 5.2 Research

- **a) Acceptance.** Värtinen et al. ([IEEE ToG](https://ieeexplore.ieee.org/document/9980408/)): of 500
  generated RPG quest descriptions judged by 349 people, *"one in five … would be deemed acceptable."*
  Older models, but the only published rate. A narrative-planning benchmark
  ([arXiv 2506.10161](https://arxiv.org/abs/2506.10161)): GPT-4-class models are causally sound at small
  scale, but *"character intentionality and dramatic conflict remains challenging."* **Lesson:**
  structure stays planner-owned; the model writes the surface of one beat at a time; plan review
  throughput around a low first-pass acceptance until this corpus measures its own.
- **b) A model as judge.** Chhun et al. ([TACL 2024](https://aclanthology.org/2024.tacl-1.62.pdf), 1,056
  stories, ~150k annotations): per story, best LLM Kendall τ ≈ 0.25 against humans; per system, 0.70
  (humans agree with each other at 0.73) — *"LLMs still cannot be relied upon to evaluate a single
  story."* Judges prefer their own generations ([NeurIPS 2024](https://arxiv.org/abs/2404.13076)).
  **Lesson:** a model judge is open-loop — it may rank prompt versions over a batch, never pass or
  fail one storylet, and never judge its own output. Vote agreement measures contract stability, not
  correctness.
- **c) Consistency.** No fresh source (quota). Derived: continuity facts (who is dead, the disposition
  band, which species) live in the ledger and reach text only through placeholders; a validator
  rejects free text naming an entity absent from the call's fact packet.
- **d) Diversity.** LLM stories reuse plot elements across generations and across models
  ([PNAS 2025](https://www.pnas.org/doi/10.1073/pnas.2504966122)). Compression ratio, long-n-gram
  self-repetition and Self-BLEU are complementary; embedding homogenisation "barely varies"
  ([Shaib et al.](https://arxiv.org/abs/2403.00553)). Distinct-n is length-biased; use the
  expectation-adjusted form ([ACL 2022](https://aclanthology.org/2022.acl-short.86/)). **Lesson:**
  per-cell compression ratio and self-repetition are cheap closed-loop warnings; embedding
  near-duplicate thresholds are calibrated on this corpus, never borrowed.

### 5.3 Choice design

- **FTL, computed from the 2012 event XML** ([orig-xml](https://github.com/vnaum/FTL-rus/tree/master/orig-xml)):
  153 real decisions; options per decision 2 (52.9%), 3 (30.7%), 4 (12.4%), 5–6 (3.9%), mean 2.68.
  71% of decisions offer exactly 2 unconditioned options. 37% carry at least one requirement-gated
  ("blue") option, usually exactly one; 21% of all options are blue.
- **Mawhorter's choice poetics** ([Emily Short](https://emshort.blog/2019/04/09/choice-poetics-peter-mawhorter/)):
  an **obvious** choice has exactly one option that meets a goal and fails none; a **relaxed** choice
  lets every option meet a goal; a **dilemma** threatens a goal with every option. Named defects:
  blind choice, false choice, dead-end option, "unchoice". These are computable from outcome ordinals.
- **Sam Kabo Ashwell's patterns** ([Standard Patterns](https://heterogenoustasks.wordpress.com/2015/01/26/standard-patterns-in-choice-based-games/)):
  floating modules (storylets) *"tend to collapse"* without a large amount of content;
  branch-and-bottleneck needs heavy state; a gauntlet is the easiest to author. Here: texture is
  floating modules, arcs are branch-and-bottleneck, the spine is a gauntlet.
- **Sid Meier** ([GDC 2012](https://www.gamedeveloper.com/design/gdc-2012-sid-meier-on-how-to-see-games-as-sets-of-interesting-decisions)):
  if players always pick the same option, or pick at random, the decision is not interesting.
  **Lesson:** log which option was picked; pick-rate telemetry is the real dominance check after
  release.

### 5.4 Language leakage

Marchisio et al. ([EMNLP 2024](https://aclanthology.org/2024.emnlp-main.380.pdf)): wrong-language
tokens appear where the next-token distribution is flat (entropy 1.228 against 0.356 elsewhere);
few-shot examples lift a base model's line-level pass rate from 86.2 to 99.0; high temperature makes it
worse (Chinese word-level pass rate 69.5% at T=1); LLMs detect code-switching at only 79–86 F1,
*"too low for use as automatic evaluators."* Language ID (fastText lid.176: 98.9% on ~35-character
lines, 80.2% on short ones — [survey](https://modelpredict.com/language-identification-survey)) still
calls "English with two Chinese words" English, so it cannot see this repo's defect. Quantization hurts
non-Latin scripts most ([arXiv 2407.03211](https://arxiv.org/abs/2407.03211)); seedsmith runs a
QAT-quantized model. **Lesson, in order:** remove the cause (never ask for a foreign-script token in
target-language prose); check scripts with Unicode script properties; use low temperature and
target-language few-shot examples; run language ID only on lines of 5+ words.

### 5.5 Localizing generated text

Caves of Qud, a year after 1.0, was still rewriting its text generator to localize it
([Steam](https://store.steampowered.com/news/app/333640/view/509609299607027767)). RimWorld French needed
per-species gender and a pluralization function for 1,555 labels
([LanguageWorker_French](https://github.com/b606/RimWorld-LanguageWorker_French)). Wildermyth tags
generated names `[m]/[f]/[p]/[n]` and splits articles per language
([Translating](https://wildermyth.com/wiki/Translating)). In Polish, "[creature] was defeated" changes
its verb with the subject's gender, so concatenation cannot render it
([Fluent terms](https://projectfluent.org/fluent/guide/terms.html)); plural categories run from one
(Chinese, Japanese) to six (Arabic) ([CLDR](https://www.unicode.org/cldr/charts/latest/supplemental/language_plural_rules.html)).
**Lesson:** the localization path for generated text is a day-one contract — whole messages with
named placeholders, and grammatical feature tags on everything that fills a slot.

### 5.6 Voice consistency

Without examples, models default to a generic style; more examples beyond a few change little
([arXiv 2509.14543](https://arxiv.org/html/2509.14543v1)). Retrieved example dialogue as prior turns
beat plain persona prompting ([RoleLLM](https://arxiv.org/abs/2310.00746)). A stronger model bought
only 2.97% persona fidelity over a weaker one ([PersonaGym](https://arxiv.org/abs/2407.18416)).
**Lesson:** a character's voice is carried by 3–5 anchor lines and a small lexicon (signature words,
forbidden words, register) sent with every call — not by adjectives, and not by a bigger model.

### 5.7 What the prior art changes in this design

1. **Fix the motif prompt before anything else** (§5.4, §4.4). It is the cause of the leak.
2. **Default choice shape: 2 unconditioned options plus 0–2 conditional ones** (FTL). Four or more is
   rare.
3. **Classify every storylet's choice type deterministically** (Mawhorter) and reject obvious choices,
   all-bad dilemmas and unchoices.
4. **A lore packet on every call**, including target-language motif glosses (GENEVA).
5. **Voice by anchors and lexicon**, not adjectives (Inworld, RoleLLM, PersonaGym).
6. **Whole messages, placeholders and feature tags** from day one (Qud, RimWorld, Fluent).
7. **A model judge ranks prompt versions; it never gates an item** (Chhun, NeurIPS 2024).
8. **Review is the bottleneck** (Hidden Door hand-edits every template; Värtinen's one in five). Size
   batches to what a reviewer clears in one sitting.

---

## 6. The shape

### 6.1 Four seed kinds, one adapter

A new `narrative` adapter owns four kinds. The dungeon adapter's `dungeon-event` kind **moves into
it**: a delve event becomes a storylet whose host is a delve room. One storylet generator for every
place — the same rule as the runtime's one engine (`npc-story-events-ideal.md` §0, principle 11).

| Kind | What one seed is | Resolved at runtime by |
|---|---|---|
| **storylet** | a situation with 2–4 choices, each with a condition and 1–3 outcomes | the storylet engine (today `EventDeck`) |
| **character** | a named creature: species, role, voice, lines | casting (`npc-story-events-ideal.md` §6.3) |
| **arc** | 3–5 linked storylets with a cast that persists across links | the story ledger and priority tier |
| **spine chapter** | one chapter of the main story, keyed to a time-machine piece (`npc-story-events-ideal.md` R3); the antagonist is a speaking lead (R2) | `StorySceneHost`, through the lingui codegen bridge (§6.8) |

**The spine is fully generated** (owner ruling R1, 2026-09-19). A spine chapter is a seed like any
other: regenerated, never hand-edited, and reviewed by sample. What keeps it coherent is structure the
planner owns: the chapter list (one per time-machine piece, R3), each chapter's beat count and cast,
and the world facts that trigger it. The model writes the scenes inside that frame. Scene scripts are
emitted as **data** — today's scripts are TypeScript literals (`RIFT_PROLOGUE_SCRIPT`, `sceneScript.ts:105`, typed by `SceneBeat` at `:32`; Reconciled 2026-09-19: `:32` is the `SceneBeat` type; the literal is at `:105`), so a data-driven
script loader is part of the runtime widening.

### 6.2 The storylet contract

The existing event anchor, widened. Ownership levels follow the dungeon adapter's own five
(`gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/schema.py:1-5`).

| Field | Level | Notes |
|---|---|---|
| `storyletId`, `host`, `kind`, `climate`, `arcRef`/`arcLink` | **PLANNED** | Chosen by the planner from coverage targets. **`climate` moves from AUTHORED to PLANNED** (§4.4 skew) |
| `roles[]` — `{roleId, kind, requires[]}` | **VALIDATED** | A role is cast at runtime from the save's characters or party. `requires` picks from closed tags |
| `choices[]` — slot count and each slot's **choice kind** | **PLANNED** | The planner fixes the slots from a closed **choice pattern** registry (below). Fixed slots make each slot's fields votable by position — the fix for `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/briefs.py:227-235` |
| per choice: `condition` | **VALIDATED** | From the closed condition vocabulary; compiles to `PredicateNode` leaves or a role requirement |
| per choice: `outcomes[]` — `{ordinal, consequence{kind, ref, param}, effect{family, powerBand}, dropBand}` | **VALIDATED**, voted | `ordinal` and `consequence` are the load-bearing fields: they decide fairness and mechanics. Owner ruling 2026-09-19 (round 3): `consequence` is one object — `kind` (the closed consequence kind), `ref` (the target id or null, filled by the planner) and `param` (a closed modifier: the relation fact kind for `relation.shift`, `none` otherwise) — owned by `narrative-seed/spec-narrative-contract.md` §5 and loaded as-is by the runtime |
| `name`, `situation`, per-choice `label`, per-outcome `result` | **AUTHORED**, keyed | Text with placeholders from a closed slot list (§6.5) |
| weights, magnitudes, costs, odds, cooldowns | **DERIVED** at runtime | `dropBand` table, `Instantiator` + `P(Θ)`, `OfferPricing`, `CombatProbability.Sigmoid`, tuning |

**Choice kinds** (closed; each maps to machinery that exists):

| Kind | Eligible when | Resolves by | Existing machinery |
|---|---|---|---|
| `interact` | always | a draw among the choice's own outcomes | `EventChoices.Interact`, `OutcomeResolver` |
| `leave` | always — **every storylet has one** (the escape hatch) | nothing; a chain may continue later | `EventChoices.Leave` |
| `use:{supplyTag}` | the party holds a supply with the tag | the supply is spent; this choice's outcomes | `EventChoices.Use`, `supplyOverride`, `HoldsStock` |
| `offer:{stock}` | the player can pay | cost priced from `Θ_room` | `WildVerb.OfferSouls/OfferSpirit/OfferSupply`, `OfferPricing.cs` |
| `fight` | always, or on a condition | a battle through the encounter builder | `WildVerb.Fight`, `Encounter.Build` |
| `bring:{tag}` | a party creature carries the element, trait or species tag | this choice's outcomes — usually the best (FTL's blue options) | **real gap**: the party-composition leaf (§4.3) |
| `persuade`, `threaten` | always, or on a disposition band | a contest (`Θ_party − Θ_content` through the shipped sigmoid) or the shipped flat coin | `WildVerb.Flatter/Threaten`, `CombatProbability.Sigmoid` |

**Choice patterns** are a small authored registry, like the dungeon's six hand-authored layouts
(`layouts.py:35-42`). The default shape follows FTL's measured distribution (§5.3): **two
unconditioned options plus zero to two conditional ones** — for example `[interact, leave]`,
`[fight, leave] + use`, `[persuade, leave] + bring`, `[offer, leave] + use + bring`. Four or more options
are rare. The planner allocates patterns so every choice kind is covered (a distribution metric), and
the model never decides what kind of decision a storylet is.

**Consequence kinds** extend the existing `none | loot | encounter | scout` with the runtime outcomes
`npc-story-events-ideal.md` §6.2 already named: `quest.offer`, `relation.shift`, `story.flag`,
`recruit`, `scene.play`, `battle.start` (a battle request into an existing battle mode, for non-Delve
hosts; never a Delve room fight). A new consequence kind is a reviewed vocabulary change. Reconciled
2026-09-19: `battle.start` added to match `narrative-seed/spec-storylet-vocab.md` §3.5 and the runtime's
routing table (`npc-story-events-map.md` row 15).

**Structural validators — deterministic, closed-loop** (each rejects the draft with a named defect):

| Rule | Why (prior art in §5 and `npc-story-events-ideal.md` §4) |
|---|---|
| 2–4 choices; exactly one `leave` | an escape hatch in every storylet |
| No lose-lose: at least one always-eligible choice has an outcome that is not `bad` | Total War's lose-lose complaints |
| No dominated choice: a choice whose outcome ordinals are all ≤ another choice's, at no lower cost and no stricter condition, is rejected | a dominant option is a non-choice |
| **Choice type is classified from the ordinals** (Mawhorter, §5.3): *relaxed* or *dilemma with an upside* passes; *obvious* (exactly one option meets a goal and fails none), all-bad *dilemma* and *unchoice* (one live option) are rejected | computable, so it gates instead of asking a model |
| A conditional choice (`use`, `bring`, `offer`) is at least as good as the best unconditional one | FTL: the blue option pays for bringing the right thing |
| `flavor`/`situation` never names the good option | already a rule of the dungeon contract (*"flavour never names the good option"*) |
| Every `roleId` used in text is declared in `roles[]`; every placeholder is in the closed slot list | no dangling reference in prose |
| No digit in any text field | principle 2 — magnitudes appear through placeholders the runtime fills |

### 6.3 The character contract

A character is **one seed per species that gets one**. Identity stays specific — a name belongs to a
real creature — and the runtime decides which characters a save meets, where they live and how they
feel about you.

| Field | Level | Notes |
|---|---|---|
| `characterId`, `speciesId` | **PLANNED** | The planner picks species against coverage targets (side × role × element) |
| `role` | **VALIDATED**, voted | The same closed role list as the runtime: wanderer, trader, hermit, chronicler, clan elder, warlord, captive, envoy, companion. Load-bearing: it decides where the character appears |
| `voice` | **VALIDATED** | A small closed register (for example `formal`, `blunt`, `playful`, `grim`, `sly`, `gentle`), each anchored by an authored exemplar under `_exemplars/` used as the few-shot style reference. Acceptance is measured **per register** — Ghostwriter found some registers systematically weak (§5.1) |
| `anchors`, `lexicon` | **AUTHORED**, reviewed | 3–5 anchor lines and a small lexicon (signature words, forbidden words) written first and accepted by a human; every later line call carries them as prior turns. Voice is carried by examples, not adjectives (§5.6) |
| `name`, `epithet`, `bio` | **AUTHORED**, keyed | Name rules: normalized collision (`item/seed-contract.md` §5 — lowercase, strip punctuation, drop connectives, sort tokens), `subject_name_echo`, a length bound |
| `grammar` | **VALIDATED** | `{gender, number, article, epithetArticle}`, each from the closed enums the names registry defines (`gender`: male · female · neuter · none; `number`: singular · plural · none; `article`: definite · none), so a character token can select on them (§6.5). Reconciled 2026-09-19: this row was missing here while `narrative-seed/spec-narrative-contract.md` §6 already carries it |
| `lines` — one per required (context × disposition band) pair | **AUTHORED**, keyed | Contexts are a closed list (for example `greet`, `farewell`, `thanks`, `refused`, `spared`, `betrayed`, `joins`, `taunt`, `rumor`). A registry states which (context, band) pairs are required — a closed-loop coverage metric |
| personality, disposition, home | **not in the seed** | Personality is derived from the minted specimen (`ContractPolicy.PersonalityFor`); disposition from the relation ledger; home from casting |

**Lines are personality-neutral in v1.** Wildermyth's writers had to write 11-way personality splits
for traits players cared about one or two of (`npc-story-events-ideal.md` §4.2). A later widening can
add personality-flavored variants for a few high-value contexts (`joins`, `betrayed`) without changing
the contract's shape.

**Line choice at runtime is deterministic**: the most specific line whose context, band and
conditions match wins (Valve's rule, `npc-story-events-ideal.md` §4.1), with least-recently-used among
ties.

### 6.4 The arc contract

An arc is a **shape** plus identity.

- **Arc shapes are an authored registry**, model-free, like layouts. Each shape fixes the link count
  (3–5), each link's host kind, which roles persist across links, and which flags each link sets and
  reads. Examples: `rescue` (rumor → search → confrontation → aftermath), `debt` (bargain → collection
  → repay or betray), `rival` (taunt → race → duel — a fixed authored chain; the rival never levels, ranks up or remembers encounters, per `npc-story-events-ideal.md` §6.12 rules 1–3), `lost-piece` (fragment → trail → vault →
  revelation), and one per failure branch (`exile` → `gather` → `return`, for a lost sector).
- **The model writes identity inside the fixed shape**: the arc's name and premise, then every link's
  storylet in the **same work order**. A link can therefore never point past its arc — the defect in
  §4.4 becomes structurally impossible, not merely detected.
- **Cast once, reused**: roles are cast when the arc starts; later links read the same cast.

### 6.5 Text rules

- **Keys from row one** (`item/seed-contract.md` §6): every text field carries a key and its string,
  authored together. A string is immutable under its key; a changed string is a new key.
- **Placeholders, never concatenation.** Text uses named slots from a closed list — `{role_<roleId>}`,
  `{place}`, `{supply}`, `{reward}`, `{cost}` — filled by the runtime (spelling per §6.5b and
  `narrative-seed/spec-token-grammar.md`; Reconciled 2026-09-19: was `{role.<id>}`/`{sector}`). Grammar that depends on a
  filled value (plural, gender) uses the message format's own selectors, never string assembly
  (§5 has the localization evidence).
- **Never ask for a foreign-script token in target-language prose.** Motifs reach the model as
  target-language glosses from a deterministic lookup table, inside a **lore packet** (species facts,
  place, faction, glosses, the declared placeholders) that grounds every call (§5.1, §5.4).
- **Whole messages with grammatical tags.** Each string is one complete message. Everything that
  fills a slot (species, character, place) carries closed feature tags — gender, number, vowel-initial
  — so a translation can select on them instead of concatenating (§5.5).
- **Tier-2 checks on every text field:** a **script check by Unicode script property** (Han, kana,
  Hangul, fullwidth forms, Cyrillic — not the current U+4E00–9FFF range), `field_echo`,
  `subject_name_echo`, name collision, placeholder closure (every placeholder declared and used), no
  digits, a length bound per field, no entity named that is absent from the lore packet, and an
  out-of-world word list matched on word boundaries (AI Dungeon's false positives, §5.1).
- **Diversity per cell**: compression ratio and long-n-gram self-repetition as closed-loop warnings;
  embedding near-duplicate thresholds calibrated on this corpus (§5.2d).
- **A model judge is open-loop only**: it may rank prompt versions over a batch; it never passes or
  fails one item and never judges its own model's output (§5.2b).
- **Open-loop quality** (voice, tone, "is this choice interesting") goes to a stratified review
  sample. A miss a human finds becomes a new tier-2 metric wherever one can be written
  (`seedsmith-map.md` §7b) — the loop that makes review effort fall over time.

### 6.5b Structured story text — names are tokens, never words

**Owner rulings R8–R10 (2026-09-19, recorded in `npc-story-events-ideal.md` §10):** story content uses
the game's **own** names, never PvZ or EA names; the names must be **parameters**, so a rename is a
JSON edit, not a rewrite. That is a known, solved shape: the story is written as **structured
messages**, not prose.

**A story string has three parts, and only one of them is words:**

| Part | Syntax (ICU MessageFormat, which lingui renders natively) | Resolved by |
|---|---|---|
| **Literal text** | plain words | the translation catalog |
| **Entity tokens** | `{lead_summoner}`, `{lead_companion}`, `{lead_antagonist}` for the three leads; `{c_<characterId>}` and `{c_<characterId>_epithet}` for a named character; `{role_<roleId>}` for a role cast at runtime; `{place}`, `{supply}`, `{reward}`, `{cost}` | the **names registry** (below) and the runtime cast |
| **Semantic markup** | a closed set of tags — for example `<em>`, `<whisper>`, `<shout>`, `<pause/>` — in lingui's rich-text form | the renderer. A tag names a meaning; the presentation layer owns the style. This is a reviewed widening of `item/seed-contract.md` §6's *"markup forbidden"* rule: semantic tags only, never HTML or styling |

**The names registry** is one JSON file per locale — for example
`gk-data/packs/fusion/data/seed/narrative/_registry/names.en.v1.json` (new) — mapping each token to a display string **plus
grammatical feature tags** (gender, number, vowel-initial) as closed enums. Messages branch on those
tags with ICU `select`, so a gendered language agrees with whatever name is in the file. **Renaming a
lead is one edit to one file**, republished like any registry; every scene, line, choice and quest
picks it up on the next build.

```text
seed text : "{lead_antagonist} laughs. <em>You are too late, {lead_summoner}.</em>"
names.en  : lead_summoner   -> "the Garden Keeper"  gender: male    (owner ruling R11)
            lead_companion  -> "Hourbloom"          gender: neuter
            lead_antagonist -> "the Rotwright"      gender: male
render    : "The Rotwright laughs. You are too late, the Garden Keeper."
             -> a title-style name needs its article handled by the message, not the registry:
                the registry carries a feature tag (article: definite) and the message selects on it
```

The rendered example shows why the feature tags matter even in English: "the Garden Keeper" and "the
Rotwright" are titles, so a sentence that starts with one must capitalise its article, and a vocative
("You are too late, Keeper") may drop it. Those are closed tags on the registry row — `article`,
`gender`, `number` — that messages select on, never string surgery.

**What each rule prevents:**

- **No literal names in text — mechanically.** A tier-2 validator rejects any text field containing
  the display string of **any** names-registry entry or any species' catalog name. (Third-party IP
  marks are **not** checked here: the owner put that check at release, `ip-censor-ideal.md` ruling
  IC-3, because blocking during generation costs more model calls than it saves. Briefs still carry the
  free avoid-list.)
  The repair prompt names the defect: *"use the token `{lead_antagonist}`, not a name."* Per the
  owner's choice of the widest scope (R8), prose never names a species by its PvZ or Fusion name; a
  creature is referred to by its own character token or epithet.
- **Token closure.** Every token is from the closed grammar and declared for this seed (a character
  token must name a character in the lore packet); no stray braces.
- **Round-trip render test.** Every seed renders cleanly against **two** different name sets, and the
  outputs differ exactly where the tokens are — proof that no name is baked in.
- **The model is told the grammar**, with a description and a negative clause per token
  (*"`{lead_antagonist}` is the villain of the chase. Write the token itself. It is not a name, and you
  never invent one for it."*). The model never sees a real name, so it cannot leak one.

**Prior art:** Fluent's **terms** exist for exactly this — a brand name defined once as `-brand-name`,
referenced by every message, carrying attributes such as gender that messages select on
([Fluent 1.0](https://hacks.mozilla.org/2019/04/fluent-1-0-a-localization-system-for-natural-sounding-translations/),
[Fluent syntax](https://mozilla-l10n.github.io/localizer-documentation/tools/fluent/basic_syntax.html)).
Wildermyth writes its comics with role tokens like `<leader.firstname>`, cast at runtime
(`npc-story-events-ideal.md` §4.2). articy:draft, the tool behind Disco Elysium, gives every entity a
technical name that dialogue references instead of the display name
([articy entities](https://www.articy.com/en/adx_basics_entities/)). Yarn Spinner separates a line's
text from its `#line:` id and from range-based markup `[tag]…[/tag]`
([Yarn markup](https://docs.yarnspinner.dev/write-yarn-scripts/advanced-scripting/markup),
[Yarn tags](https://docs.yarnspinner.dev/write-yarn-scripts/advanced-scripting/tags-metadata)). Unicode
MessageFormat 2 standardises open/close markup placeholders whose meaning the developer supplies
([MF2 markup](https://messageformat.unicode.org/docs/reference/markup)). Lingui, already this repo's
translation library, renders ICU messages with named placeholders and `select`
([Lingui ICU](https://lingui.dev/guides/message-format)). **Nothing here needs a new library**: the
tokens are ICU placeholders, the registry is JSON, and lingui already renders both.

### 6.6 Pipelines — narrow, one judgement per call

| Step | Model? | Writes | Vote |
|---|---|---|---|
| **plan** — cells, choice patterns, arc shapes, species for characters | no | work order | — |
| **storylet-structure** | yes | roles, per-slot conditions and outcomes | 3 samples; vote per slot on `ordinal` and `consequence` |
| **storylet-text** | yes | name, situation, labels, results — structure fixed, shown as `const` | none; tier-2 validators with ≤ 2 named repairs |
| **character-identity** | yes | role, voice, name, epithet, bio | 3 samples; vote on `role` and `voice` |
| **character-anchors** | yes, then a human | 3–5 anchor lines and the lexicon | none; a reviewer accepts before any line call runs |
| **character-lines** | yes | lines for one disposition band per call, anchors attached | none; coverage + tier-2 validators |
| **arc** | yes | name, premise; then each link through the two storylet steps | shape is planned; premise unvoted |
| **emit** | no | canonical JSON, `_provenance` (model, prompt version, inputs), run ledger | — |

**Why structure and text are separate calls:** structure is a handful of enum picks where bias
matters and voting is cheap; text is prose where voting means nothing. Splitting them is the
"one judgement per call" rule (`research/ai-native-generation/README.md` §3), and it lets the text
call see the final structure as fixed input rather than inventing around it.

**Reused unchanged:** `llm_caller`, `order_for`, `resolve_vote`, the bounded named-defect retry,
`field_echo`, `subject_name_echo`, `language_consistency` (once wired), `SemanticDedup`, `run_ledger`,
`staleness`, and dungeon's emit and provenance shape.

### 6.7 Budget and call cost

**Targets are declared, never guessed** (P2). They live in seedsmith's `budget`, and metrics report
actual against declared per cell.

- **Storylet grid, Delve (computed):** 6 event kinds × 7 climates (6 elements + `none`) = **42 cells**.
  Today 15 are covered (§4.4). *This is a change to the approved dungeon contract, whose planning grid
  is kind × theme (6 × 8 = 48, `party-dungeon/spec-dungeon-seed-contract.md:78`): climate becomes a
  planned cell dimension and theme becomes casting. It needs a `decisions.md` row at spec time
  (listed in `narrative-seed-map.md`).*
- **Repetition budget** (CK3's lesson, `npc-story-events-ideal.md` §4.1): a pool of `T`
  once-per-save storylets on a host that fires `P` times per session lasts `T / P` sessions before the
  first repeat. The spec sets `T` per cell from the runtime's pulse rates; the corpus grows when a
  metric shows a pool running dry.
- **Character grid (computed):** 9 roles × 2 sides = **18 cells**. At the roster research's
  comfortable ~3 per cell (`research/game-design/README.md`, finding 1) that is ~54 characters for a
  first batch, spread across elements by the planner.

**Call cost** (`research/ai-native-generation/README.md` §9; ~3.1 s per call is derived from that
file's own figure, 16,272 calls ≈ 14 h on the local 26B model):

```text
storylet   = 3 structure samples + 1 text call               ≈ 4-6 calls with repairs
character  = 3 identity samples + 1 anchor call + 4 line calls (one per band)   ≈ 8 calls
arc        = 1 premise call + links × storylet               ≈ 17-31 calls for 4-5 links

first batch: 84 storylets (2 per Delve cell) + 54 characters + 6 arcs of 4 links
           ≈ 84×5 + 54×8 + 6×(1 + 4×5) ≈ 420 + 432 + 126 ≈ 980 calls ≈ 50 min
```

**Model time is not the bottleneck; review is.** Hidden Door hand-edits every generated template, and
the one published acceptance rate for generated quest prose is one in five (§5.1, §5.2a). Batches are
sized to what a reviewer clears in one sitting, and character anchors are reviewed before any line
call spends a token.

The first batch is deliberately small: generate, wire, playtest, then scale — the owner's standing
phased-rollout decision for generators (*"small-batch-then-playtest before the full run"*,
`tasks/item-todo.md:9590-9591`). A `--dry-run` renders every prompt and prints the call count before
anything is spent.

### 6.8 Localization

Two owner-approved rules meet here: seeds carry keyed strings (`item/seed-contract.md` §6), and all
player text goes through lingui (`story-scene-map.md` decision S4). Lingui accepts only compile-time
literals (§4.3). **The bridge is codegen**: a build step reads narrative seeds and emits a generated
module of literal `msg({ id, message })` descriptors, one per keyed string, which lingui extracts like
any other. The module is committed and drift-checked in CI like every other generated tree. Seed keys
become lingui ids, so both rules hold and there is one translation system. The generated catalog
loads in its own chunk; a large catalog is a splitting problem, never a reason to drop the library.

### 6.9 Alternatives rejected

| Alternative | Why not |
|---|---|
| A model generating replies during play | The runtime never calls a model (§1.3); play is offline and local |
| A second storylet generator beside the dungeon one | Two generators for one kind of content; the dungeon event kind moves into the narrative adapter |
| Letting the model decide choice kinds | The plan is deterministic (P4); patterns keep choice kinds covered and slots votable |
| Characters as species-agnostic templates cast onto any species | Names and voices would be generic; one seed per species keeps identity specific and still lets the runtime choose who appears |
| Per-personality lines in v1 | Five times the lines and review load for a trait players weigh lightly (Wildermyth) |
| A second translation system for seed text | Two i18n paths drift; codegen keeps one |
| Hand-fixing the 54 events | Generated data is regenerated, never hand-edited |

---

## 7. Tunables and targets

| Number | Unit | Lives in |
|---|---|---|
| Coverage target per storylet cell, per character cell, per choice kind | count | seedsmith `budget` (declared, not guessed) |
| Required (context, band) line pairs | registry rows | the `narrative` adapter's registry |
| Text length bounds per field | characters | the adapter's validator config |
| Review sample size per metric | count | seedsmith `report` |
| Outcome weights, costs, contest scale, cooldowns | per-mille, Θ units, turns | runtime `gk-core/data/tuning/` (`npc-story-events-ideal.md` §7) |

---

## 8. Build order — model-free first

1. **Fix the current corpus's generator** (no new design): replace verbatim Chinese motifs in the event
   brief with target-language glosses; widen the script check to Unicode script properties and wire it
   into `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/pipelines.py:334`; add a `PROMPT_VERSION`; move `climate` to PLANNED; stop forging chain ids.
2. **Registries** (no model): choice kinds, choice patterns, condition vocabulary, consequence kinds,
   roles, voice registers with exemplars, line contexts, required (context, band) pairs, arc shapes,
   placeholder slots — each value with a description and a negative clause.
3. **Contracts and schema audit** (no model): storylet, character and arc schemas; the no-number audit
   extended to "no digit in prose".
4. **Validators and metrics** (no model): the structural rules of §6.2, line coverage, per-cell
   coverage against budget, chain integrity, choice-kind distribution.
5. **Planner** (no model): cells, patterns, arc shapes, species picks, and a dry run.
6. **Pipelines** (model): storylet, character, arc; then regenerate the Delve events under the widened
   contract.
7. **Runtime widening** — owned by `npc-story-events` and `party-dungeon`: load `choices[]` and eligibility trees, answer per choice, the event route, text on the wire, the lingui codegen. Owner ruling 2026-09-19
   (round 3): the Delve's event route and text on the wire moved to `npc-story-events` (`delve-live-rooms`, with `delve-live-start` for starting a delve); `party-dungeon` keeps its Delve content.

Steps 1–5 produce real value with zero tokens spent and make step 6's inputs reviewable.

---

## 9. What this deliberately does not decide

- Choice-pattern members, arc-shape members, role and voice lists as final vocabularies — the spec
  writes them with descriptions and negative clauses; the lists above are examples.
- Exact coverage targets per cell (spec, from runtime pulse rates).
- Runtime resolution code (`npc-story-events` and `party-dungeon`).
- Voice audio and portraits.
- Any spec, plan, task list or code.

---

## 10. Owner decisions

**Answered by the owner on 2026-09-19** (together with `npc-story-events-ideal.md` §10 R1–R5).

| # | Question | Ruling | Consequence |
|---|---|---|---|
| R6 | Which model writes narrative? | **No hard-coded model. The model is set in the environment; the default is Gemma 26B.** | Every narrative pipeline resolves its model through seedsmith's existing config layer — `.env` `SEEDSMITH_LLM_MODEL` wins over `seedsmith.toml`, which wins over `LlmCallerConfig`'s default `google/gemma-4-26b-a4b-qat` (`gk-forge/tools/seedsmith/seedsmith/pipeline/llm_caller.py:47,66-78`). **No adapter and no CLI flag may carry its own model literal.** The narrative adapter is built that way from day one; the literals that used to bypass the layer were removed in NS3–NS6 (0 remain outside `llm_caller.py`, enforced by `test_no_model_literal.py`), so §4.2's wiring gap is closed |
| R7 | (same answer) Avoid words that will need censoring | **Enrich the ip-censor design so generation never produces them** | One shared registry: a free avoid-list in every brief, and the scan as a **release gate** (not an in-loop validator — `ip-censor-ideal.md` ruling IC-3). Added to `ip-censor-ideal.md` (section "Narrative generation"); this program consumes it (§6.5, §11 item 6) |
| — | Spine authorship (`npc-story-events-ideal.md` R1) | **Fully generated** | The spine becomes a generated seed kind (§6.1) |

---

## 11. Enrichment pass (2026-09-19)

A brainstorm over this document for holes, each checked against the repo. Runtime-side holes are in
[npc-story-events-ideal.md](npc-story-events-ideal.md) §11; these are the generation side.

| # | Gap | Resolution |
|---|---|---|
| 1 | **The leak fix has no input.** §8 step 1 says "pass glossed motifs", but no gloss exists: **all 1,586 motifs** in `gk-data/packs/fusion/data/seed/creatures/_registry/motifs.v1.json` are Chinese (counted this session), and species `displayName` is Chinese too (`themes.v2.json`, e.g. `究极剑仙杨桃`) | A **motif gloss registry** comes first: a one-time translation pipeline over the motif list — identity text, so model-writable — reviewed and committed as a registry. `seedsmith/spec-pipeline.md` §5.1 already names the proven shape (the verify-and-self-heal translation loop from the owner's other repository, lore-weave). The same need exists for **species display names** in the target language, which every `{species}` placeholder resolves to; that table is shared with every surface that shows a species, so it is coordinated with `creature-seed`, not owned here |
| 2 | **Reviewers cannot judge a template.** A storylet with `{role_captive}` and `{reward}` in it reads as a form, not a scene | seedsmith `report`'s sampling mode renders each sampled storylet **with 2–3 sample casts and filled placeholders**, plus its computed choice type and each option's outcome profile. Reviewers read what a player reads |
| 3 | **Two candidates only where it pays.** Ghostwriter's writer-picks-one-of-two (§5.1) doubles prose calls | Two candidates for **lead-tier** text only (spine chapters, lead characters' anchors) — the reviewer's pick is recorded as a sample verdict, not an edit (R1 keeps the spine generated); texture gets one draft plus validators. Line budgets follow tiers from the Hades counts (§5.1): texture characters ≈ 20–40 lines, recurring characters grow toward ~200 over later batches, leads are authored or accepted by hand |
| 4 | **Regeneration versus saves.** The runtime needs `(id, revision)` to keep an in-progress arc stable (`npc-story-events-ideal.md` §11 item 3) | Every seed carries `revision`, bumped by emit when the content hash changes; `staleness` already compares recorded against current inputs. Ids are never reused; a withdrawn seed becomes a tombstone row, not a deletion |
| 5 | **Hand-written storylets** (`npc-story-events-ideal.md` §11 item 10) | The contract carries `provenance: generated \| authored`. Authored entries live in an authored path, pass the same validators, and are never touched by regeneration |
| 6 | **IP-safe names.** | Character names and storylet titles go through the `ip-censor` **release** gate (ruling IC-3) (`ip-censor-ideal.md` already scopes `gk-data/packs/fusion/data/seed/dungeon/**`); its scope widens to the narrative tree. No second filter here |
| 7 | **Grid for places other than the Delve is not computed.** §6.7 computes 42 Delve cells only | World, expedition and homeworld storylet kinds are not defined yet (the runtime owns hosts). The spec computes each host's grid the same way — host kinds × storylet kinds × climate — before any budget target is declared |
| 8 | **Voices can collapse into one.** Anchors and lexicons help, but nothing measures distinctness | An open-loop signal: a cheap offline classifier trained to tell cast members apart by their lines; low accuracy means voices have converged. It feeds the review queue; it never gates (§5.2b, §5.6) |
| 9 | **Lore drift.** A model will fall back on generic fantasy for an obscure world (§5.1, GENEVA) | Every call's lore packet lists the allowed entities; the tier-2 check "no entity named that is absent from the packet" (§6.5) is the closed-loop half. Tone and lore fit stay in the review sample |

---

## 12. Checklists

**AI-native contract checklist** (`research/ai-native-generation/README.md` §10), as designed:

```
[x] No numeric field survives the schema audit; extended to digits in prose (§6.2)
[x] Every attribute has a description with a negative clause (§8 step 2 requires it)
[x] Every closed enum admits none; additionalProperties false; every field required
[x] Options permuted from entity id and sample index (reuses order_for)
[x] Vote set named and small: storylet ordinal + consequence per slot; character role + voice
[x] 1-1-1 split yields unresolved (reuses resolve_vote)
[x] Constrained decoding proven by a real call before the run (existing llm_caller test; a run-start probe)
[x] TRANSIENT and QUALITY retries separate; repair bounded at two
[x] Provenance + prompt version + staleness; rerun byte-identical by hash (dungeon lacks this today — §4.2)
[x] Every metric declares closed-loop or open-loop (§6.5)
[x] Suite passes with the transport stubbed to raise (existing pattern)
[x] Call budget computed (§6.7); a dry run exists before any spend
```

**DESIGN-GATE §5**, abbreviated: subsystems identified (seedsmith, Delve events, story-scene, i18n,
runtime storylets); session boundary recorded (`tasks/sessions/narrative-seed-idea-20260919.json`);
the seedsmith-design reading gate read this session (`research/ai-native-generation/README.md`,
`seedsmith-map.md` P1-P5 and §3d, `item/seed-contract.md` §1-§6, `seedsmith/spec-pipeline.md`,
`seedsmith/spec-quality-gates.md`, `research/game-design/README.md` and `05-failure-modes.md` §5 and
§13; `spec-workflow-runtime.md` and `spec-metrics.md` skimmed by heading); claims verified against
code; no population pinned; no new actor-number path; no parallel generator or roll.

---

## Handoff

Next: `/spec narrative-seed` for a capability map and module specs, after §10 is answered — or
immediately for steps 1–5 of §8, which do not depend on it. Runtime widening stays with
`npc-story-events` and `party-dungeon`.
