# Spec: `character-pipeline`

**Program:** [narrative-seed](../narrative-seed-map.md) · **Module id:** `character-pipeline` · **Map row:** 19 · **Wave:** 5
**Depends on:** `narrative-planner`, `narrative-validators`, `narrative-emit`, `lore-packet`, `model-config-resolve`; reads `review-render`'s verdict queue for the anchor gate (§2 — Audit 2026-09-19: used but undeclared; Wave 3, so no ordering change) · **Model calls:** yes
**Ideal:** [../narrative-seed-ideal.md](../narrative-seed-ideal.md) §5.1 (Ghostwriter, Inworld), §5.6 (voice), §6.3 (the character contract), §6.6, §11 items 3 and 8
**Sibling rulings:** R2 (the Rotwright speaks), R4 (one 4-band ladder), R8–R11 (names are tokens), R13 (counter-doctrine)
**Status:** spec phase, 2026-09-19. Map approved by the owner 2026-09-19. No build authorized.

---

## Objective

Generate one character per planned species (and one per lead) in three stages:

1. **Identity** — role, voice, name, epithet, bio; three samples, voted on `role` and `voice`.
2. **Anchors** — three to five anchor lines and a small lexicon (signature words, forbidden words),
   **accepted by a human before any line call runs**. Lead-tier characters get two candidates and the
   reviewer's pick is recorded as a verdict, never an edit.
3. **Lines** — one call per disposition band, each writing that band's required lines, with the accepted
   anchors attached as prior turns.

Voice is carried by example lines and a lexicon, not adjectives: a persona told not to be sarcastic stayed
sarcastic (Inworld), retrieved example dialogue beat persona prompting (RoleLLM), and a stronger model bought
under 3% persona fidelity (PersonaGym) — ideal §5.6. Lines are personality-neutral in v1 (map §8 item 19).

## Design

### 1. Identity

**Shown:** the lore packet (species facts as glosses, never the species' name), the planned `const` values
(`characterId`, `speciesId`, side, element), the role list and the voice registers inlined with their
descriptions and negative clauses, and for each voice register its authored exemplar from
`character-vocab`'s `_exemplars/` as the style reference.

**Written:**

| Field | Level | Voted |
|---|---|---|
| `role` | VALIDATED, the closed role list shared with the runtime (`character-vocab`) | **yes** |
| `voice` | VALIDATED, the closed voice registers (`character-vocab`) | **yes** |
| `name`, `epithet`, `bio` | AUTHORED, keyed | no — from the carrier sample |

**Leads (Audit 2026-09-19).** A lead's `role` is PLANNED const `none` (a lead is not one of the nine roles;
its allegiance comes from `character-vocab`'s leads block), and its `name`, `epithet` and `grammar` are
`null` because the names registry owns them (`spec-narrative-contract.md` §6). The lead identity call
therefore writes `voice` and `bio` only; the vote set is `voice` alone and the carrier is the lowest-index
sample whose `voice` equals the resolved value. The call count is unchanged (three samples).

**Why `role` and `voice` are the vote set.** `role` decides where a character appears (casting reads it);
`voice` decides every later line call's exemplar and anchors. A wrong answer on either poisons everything
downstream of it, and both are single enum picks where position bias bites. Options are permuted with
`order_for(characterId, field, sampleIndex)` (`gk-forge/tools/seedsmith/seedsmith/adapters/creatures/anchor/permute.py:26`)
and resolved with `resolve_vote` (`gk-forge/tools/seedsmith/seedsmith/adapters/creatures/anchor/vote.py:26`).

**Carrier sample.** `name`, `epithet` and `bio` come from the lowest-index sample whose `role` and `voice`
both equal the resolved values. With two voted fields such a sample always exists when both resolve (two
majorities of three samples always share a sample), so no splice is ever needed.

**The planned role and the voted role.** The planner targets coverage by (side, role) cells and picks a
species for each slot (`narrative-planner` §4); the identity call still votes the role, with the planned
role **not shown**, so the model reads the species rather than confirming the plan. Outcomes:

| Vote result | Effect |
|---|---|
| equals the planned role | accepted |
| a different role legal for the side | accepted in the voted role — the species' lore wins over the plan, because role decides where the character appears; `Narrative/CellCoverage` reports the actual cell and the next plan fills the shortfall with another species |
| a role the side may not hold (R13 enemy-side restrictions in `character-vocab`) | named defect, identity re-drawn with the restriction named — at most two re-draws |
| `unresolved` (1-1-1) on either field | the character is `unresolved`, recorded, not retried |

Text validators (`narrative-validators`' battery) run on the carrier's `name`, `epithet` and `bio`. A defect
triggers a text-only repair call with `role` and `voice` as `const` — at most two, then `unresolved`. Name
rules include `name_collision` against every committed character name
(`gk-forge/tools/seedsmith/seedsmith/workflow/validators/field_echo.py:69`), the length bound and the literal-name
check; `subject_name_echo` (`gk-forge/tools/seedsmith/seedsmith/workflow/validators/field_echo.py:48`) compares
against the species' own catalog name so a character is never just named after its species.

### 2. Anchors — a human gate before lines

**Written:** `anchors` (`character.anchorLines.{min,max}` lines of text) and `lexicon` (`signature`,
`forbidden` — the contract's and the exemplar files' field names). AUTHORED, reviewed. The text battery
applies to every anchor line; the lexicon words are checked for script, digits and literal names. Audit
2026-09-19: this paragraph named the lexicon members `signatureWords`/`forbiddenWords` and tagged each anchor
with a line context, neither of which the contract (`spec-narrative-contract.md` §6) or the exemplar shape
(`spec-character-vocab.md` §4) has.

| Tier | Candidates | Gate |
|---|---|---|
| texture | 1 | a recorded `accept` verdict in `review-render`'s queue |
| lead (the three names-registry leads, R11) | 2 | a recorded `pick` verdict naming candidate `a` or `b` |

**The gate is mechanical.** The line stage refuses to start for a character whose anchors have no `accept`
or `pick` verdict row for the current anchor revision; a `reject` regenerates the anchors with the reason
named. The unpicked lead candidate is kept in the run ledger, never deleted or merged. This is the ideal's
rule that character anchors are accepted before any line call spends a token (ideal §6.6, §6.7).

**The Rotwright speaks** (R2). The antagonist lead is a character like the other leads: anchors, lexicon
and lines, generated and reviewed by pick. Only the counter-doctrine restrictions below distinguish it.

### 3. Lines — one band per call

For each disposition band that has required pairs (`eager · open · wary · hostile`, the one 4-band ladder,
R4; `gk-data/packs/fusion/data/seed/dungeon/_registry/disposition.v1.json`), one call writes one line per required context of
that band, as `character-vocab`'s required (context, band) registry declares. `B` therefore depends on the
allegiance: 4 for `independent` and `ally`, 2 for `antagonist` (`wary`, `hostile`), 0 for `player` — the
summoner speaks only in spine scenes (`spec-character-vocab.md` §6; Audit 2026-09-19).

**`blocked`.** Every call schema carries the root `blocked` escape (`spec-narrative-contract.md` §9); a
blocked reply ends that stage for the character with a terminal ledger row and its reason, never a retry.

**Anchors as prior turns.** The accepted anchor lines are sent as earlier assistant turns in the chat, so
the model continues a voice it has already "spoken" in, rather than reading a description of it. The
transport today builds exactly two messages, system and user
(`call_model`, `gk-forge/tools/seedsmith/seedsmith/pipeline/llm_caller.py:298`; messages at line 334). This module
adds an optional `prior_turns` argument to `call_model` in the same shape as its optional `schema`: absent,
the request body is byte-identical to today, and a test asserts it. The change is feature-agnostic and
stays in the transport; nothing narrative enters the core (P5).

**Validated by** the text battery plus: the lexicon's forbidden words do not appear (word boundaries); every
required context of the band has exactly one line; and the counter-doctrine rule below. A defect repairs
the named lines only — at most two repairs per band call, then those pairs are `unresolved` and
`Narrative/LinePairCoverage` reports them.

### 4. Counter-doctrine (R13) — enforced in generation, not only in review

R13 is binding on generated antagonist content (map §8 item 11; `npc-story-events-ideal.md` §6.12 rules
1–3):

- **No enemy remembers you personally.** For an enemy-side character, the line contexts `character-vocab`
  flags as personal memory are never requested, and a line that refers to a past encounter with the player
  fails `narrative-validators`' `enemy-memory` check. Enemy memory is faction- and world-level only.
- **No enemy grows or ranks from meeting you.** No character field records a level, rank or title gained
  from the player; the bio brief says so in its negative clause, and the literal-name and token rules keep
  ranks out of names.
- **Friendly relationship lines stay.** Disposition-keyed lines for non-enemy characters are the ordinary
  RPG relationship pattern and are required as registered.

### 5. Transport, retries, runtime

Model resolved through the config layer only (`gk-forge/tools/seedsmith/seedsmith/pipeline/llm_caller.py:47`;
`.env` keys at lines 69–77) — no literal (R6). Constrained decoding, reasoning off, `narrative preflight`
before the run. TRANSIENT replays from checkpoint; QUALITY re-generates with the defect named; the bound of
two is structural (`seedsmith/spec-workflow-runtime.md` §2.3). Three graphs (identity, anchors, lines) in
`tools/seedsmith/seedsmith/workflow/graphs/narrative_character.py` (new), node bodies in the adapter; the
line graph cannot be entered without the anchor verdict (§2). Accepted seeds go to `narrative-emit`, which
bumps `revision` when content changes.

**Provenance handed to emit:** prompt versions per stage, `packetHash`, the resolved model id, vote
confidence and minority for `role` and `voice`, the planned role beside the voted role, the anchor verdict
row it passed, and attempts per call.

### 6. Call budget

`docs/research/ai-native-generation/README.md` §9, as declared in the call-shape table (`narrative-planner` §7).
`B` = bands with required lines (4 at the current ladder).

```text
texture base  = identity 1 + anchors 1 + lines B + 1 voted call x (3 - 1)   = 4 + B  (8)
lead base     = identity 1 + anchors 2 + lines B + 2                         = 5 + B  (9)
texture worst = identity 3x3 + anchors 3 + lines 3B                          = 12 + 3B (24)
lead worst    = identity 3x3 + anchors 2x3 + lines 3B                        = 15 + 3B (27)
```

Anchor re-generations after a human `reject` are new work, counted in the next run's dry run, not in this
bound. Illustration, not an assertion: the ideal's first batch of 54 characters is 432 base calls
(ideal §6.7).

### 7. Tunables

Budget file `gk-data/packs/fusion/data/seed/narrative/_plan/budget.v1.json` (new), block `character`.

| Key | Unit | Starting value | Rationale |
|---|---|---|---|
| `character.anchorLines.{min,max}` | lines | 3 · 5 | ideal §5.6: a few examples carry voice; more change little. Audit 2026-09-19: renamed from `anchorCount` to the key `narrative-contract` reads |
| `character.lexicon.{signature,forbidden}Max` | words | 6 · 6 | small enough to fit every line call |
| `character.leadCandidates` | candidates | 2 | Ghostwriter's writer-picks-one-of-two, for lead tier only (ideal §11 item 3) |
| `character.temperaturePermille.{identity,anchors,lines}` | ‰ | 300 · 600 · 600 | identity is a classification; anchors and lines need voice variety |

**Structural (commented):** three samples; two repairs; the vote set; one band per line call.

## Commands

```powershell
$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest tools/seedsmith/tests/test_narrative_character_pipeline.py -q
cd tools\seedsmith; python -m seedsmith narrative characters run --stage identity --dry-run     # DEFAULT is --dry-run for every stage
cd tools\seedsmith; python -m seedsmith narrative characters run --stage identity --write --limit 12
cd tools\seedsmith; python -m seedsmith narrative characters run --stage anchors --write
cd tools\seedsmith; python -m seedsmith narrative review render --batch <runId> --kind character   # accept / pick anchors
cd tools\seedsmith; python -m seedsmith narrative characters run --stage lines --write           # refuses characters without an anchor verdict
cd tools\seedsmith; python -m seedsmith narrative characters run --resume <runId>
```

## Project structure

```text
tools/seedsmith/seedsmith/adapters/narrative/pipelines/character.py          (new) node bodies for the three stages
tools/seedsmith/seedsmith/adapters/narrative/pipelines/prompts/character.py  (new) prompts, PROMPT_VERSIONs, schemas
tools/seedsmith/seedsmith/workflow/graphs/narrative_character.py             (new) graph wiring only
gk-forge/tools/seedsmith/seedsmith/pipeline/llm_caller.py                             optional prior_turns on call_model
tools/seedsmith/tests/test_narrative_character_pipeline.py                   (new)
gk-forge/tools/seedsmith/tests/test_llm_caller.py                                     prior_turns-absent body is byte-identical
```

## Code style

```python
def line_stage_allowed(character_id: str, anchor_revision: int, verdicts: "VerdictQueue") -> bool:
    """True only when an accept (texture) or pick (lead) verdict exists for this anchor revision.
    The line graph's entry node calls this and refuses otherwise — the human gate is code, not a habit."""
```

## Testing strategy

The transport is a scripted fake that raises when exhausted or called unexpectedly.

| Test | Asserts |
|---|---|
| `dry_run_makes_no_call` | every stage renders its prompts with a transport that raises |
| `species_name_never_in_identity_prompt` | the rendered identity prompt contains no species catalog name |
| `role_and_voice_voted_with_permutation` | three samples, three option orders, resolution by `resolve_vote` |
| `planned_role_not_shown` | the identity prompt does not contain the planned role as a value |
| `voted_role_differs_legal_is_accepted` | a legal different role is accepted and recorded beside the planned role |
| `enemy_restricted_role_redraws` | a role forbidden for the side triggers a re-draw naming the restriction; two re-draws then `unresolved` |
| `carrier_always_exists_when_both_resolve` | property over all 2-1/3-0 combinations: some sample matches both resolved values |
| `lines_refused_without_anchor_verdict` | the line stage refuses a character with no accept/pick row, and makes no call |
| `lead_gets_two_anchor_candidates_and_pick_recorded` | two candidate calls; the pick verdict selects one; the other stays in the ledger |
| `anchors_sent_as_prior_turns` | the line request's messages contain the accepted anchors as assistant turns, in order |
| `prior_turns_absent_is_byte_identical` | `call_model` without `prior_turns` builds today's exact request body |
| `one_line_per_required_context_per_band` | a missing or duplicate context is a defect naming the pair |
| `forbidden_lexicon_word_rejected` | a line containing a forbidden word (word boundary) repairs naming the word |
| `enemy_personal_memory_never_requested_or_accepted` | enemy-side characters get no memory-flagged contexts; a line recalling a past encounter fails |
| `worst_case_bounds` | scripted all-fail runs make exactly 12 + 3B (texture) and 15 + 3B (lead) calls |
| `lead_identity_votes_voice_only` | the lead identity schema has `voice` and `bio` only; `role` is absent from the vote record (Audit 2026-09-19) |
| `lines_per_allegiance` | a fixture antagonist gets line calls for `wary` and `hostile` only; a `player` lead gets none |
| `lexicon_field_names_match_the_contract` | the anchors schema writes `lexicon.signature` and `lexicon.forbidden`; `validate_entry` accepts the draft |
| `blocked_reply_ends_the_stage` | a blocked identity reply writes nothing and makes no further call for that character |
| `no_model_literal` | model from `load_config`; the guard test passes |

No test asserts how many characters exist, any name, or any line text.

## Success criteria

1. Every accepted character has a voted role and voice, a validated name, epithet and bio, human-accepted
   anchors, and one line per required (context, band) pair — or is listed as `unresolved` with the reason.
2. No line call runs before its character's anchors carry an accept or pick verdict.
3. No enemy-side character has a line keyed to its own past encounters with the player.
4. The transport change is invisible to every existing caller.
5. The suite passes with the model transport stubbed to raise.

## Boundaries

- **Always:** vote role and voice; carry voice by anchors and lexicon; gate lines on a recorded verdict;
  enforce R13 in generation; resolve the model through config.
- **Ask first:** personality-flavoured line variants (a v1 exclusion, map §8 item 19); more than two lead
  candidates; any change to the required (context, band) registry's shape.
- **Never:** show the model a species' catalog name or a lead's display name; let a line call run on
  unaccepted anchors; key an enemy line to its own encounters with the player; hand-edit a generated line;
  carry a model literal.

## Open questions

None.

---

## Standards audit (2026-09-19)

Independent adversarial review against `docs/research/ai-native-generation/README.md` §10, seedsmith P1–P5,
`seedsmith/spec-pipeline.md` §3, `spec-quality-gates.md`, `spec-workflow-runtime.md`, `validation-ssot.md`,
`tunables-ssot.md`, `item/seed-contract.md` §2–§7, `DESIGN-GATE.md` §3/§5, owner rulings R1–R13 and IC-3, and
the runtime contracts (`npc-story-events/spec-storylet-contract.md`, `spec-narrative-text.md`). Every change
in the body is marked "Audit 2026-09-19" (or "Owner ruling 2026-09-19 (round 4)" where the owner ruled).

| # | Severity | Finding | Status |
|---|---|---|---|
| 1 | medium | Lead identity voted a `role` and wrote name/epithet the contract forbids on leads | fixed |
| 2 | medium | Lexicon members `signatureWords`/`forbiddenWords` and per-anchor context tags matched neither the contract nor the exemplar shape | fixed |
| 3 | medium | Budget key `character.anchorCount` vs the contract's `character.anchorLines` | fixed |
| 4 | low | `B` depends on allegiance (antagonist 2, player 0); the verdict-queue dependency and `blocked` were unstated | fixed |
