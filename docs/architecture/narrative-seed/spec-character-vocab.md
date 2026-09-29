# Spec: `character-vocab`

**Program:** [narrative-seed](../narrative-seed-map.md) · **Module id:** `character-vocab` · **Map row:** 6 · **Wave:** 1
**Depends on:** none · **Model calls:** none
**Status:** spec phase, 2026-09-19. Map approved by the owner 2026-09-19; no build authorized.
**Shared with the runtime:** the role list, line contexts and voice registers are read by
`npc-story-events`' `narrative-vocabulary` (`npc-story-events-map.md` row 1); one file each.

---

## Objective

Author the closed registries a character seed is built from: the **role list** (shared with casting),
**voice registers** each anchored by an authored exemplar, **line contexts**, the **required (context,
band) pairs** over the 4-band disposition ladder (R4), and the **enemy-side restrictions** of R13 written
as registry rules a validator can check.

Voice is carried by example lines and a small lexicon, not by adjectives: a persona prompt without
examples drifts to a generic style, and *"an NPC told not to be sarcastic stayed sarcastic"*
(`narrative-seed-ideal.md` §5.1, §5.6). The exemplars under `_exemplars/` are that example layer for the
register; each character's own anchors come later from `character-pipeline`.

**Done means:** four registry files and one exemplar per register exist, the ladder is read from the one
existing disposition file, the R13 rules are data with tests, and every value has a description and a
negative clause.

---

## Design

### 1. Inputs this module reads, never copies

| Input | Evidence |
|---|---|
| The disposition ladder `eager · open · wary · hostile` — the one relation ladder for characters and factions (R4) | `gk-data/packs/fusion/data/seed/dungeon/_registry/disposition.v1.json`; `npc-story-events-map.md` locked assumption 5 |
| The runtime's role list | `npc-story-events-ideal.md` §6.3 (wanderer, trader, hermit, chronicler, clan elder, warlord, captive, envoy, companion) |
| Personality is derived from the minted specimen, never seeded | `gk-core/src/FusionRpg.Core/Creatures/Contracts/ContractPolicy.cs:195` (`PersonalityFor`); enum at `:18` |
| The anti-Nemesis rules | `npc-story-events-ideal.md` §6.12 rules 1–6; owner ruling R13 |

Lines are **personality-neutral in v1** (map §8 assumption 19): no registry here has a personality
dimension. A later widening can add variants for a few contexts without changing these files' shape.

### 2. Common file shape

The same as `storylet-vocab` §2: `schemaVersion`, `registryVersion`, one map of value → row, each row with
`description` and `negative`. A `none` row is present in every list a model picks from (role and voice
are voted fields; see `narrative-contract`).

### 3. `roles.v1.json`

| Role | `allegiance` | Description (short) | Negative clause |
|---|---|---|---|
| `wanderer` | independent | a creature on the move with no fixed post | not a trader; it has nothing to sell |
| `trader` | independent | exchanges goods; gives a market a face | not the market's rules — prices are the runtime's |
| `hermit` | independent | keeps to one place and knows it well | not a quest-giver by default |
| `chronicler` | independent | keeps and trades in history and rumor | not an oracle; it reports, it does not foretell |
| `clan-elder` | independent | speaks for a clan | not the clan's policy — the clan's needs are computed from world state (`world-graph-ideal.md` §8.2) |
| `warlord` | antagonist | leads a hostile force on the world map | not a rival that grows from meeting the player (R13 rule 1) |
| `captive` | independent | held against its will, found in a cage or a camp | not an ally until freed |
| `envoy` | independent | carries a message between powers | not a trader and not a clan elder |
| `companion` | ally | travels with the player's side | not a roster slot; joining is the runtime's ownership transfer |
| `none` | — | the model cannot place this creature in any role | the seed is refused; a character must have a role |

`allegiance` is a closed attribute, `player · ally · independent · antagonist`, read by the rules in §6.

**Leads** are a separate block in the same file, keyed by lead token (the names registry's first rows,
R11): `lead_summoner` → `player`, `lead_companion` → `ally`, `lead_antagonist` → `antagonist`. A lead is
not one of the nine roles; its allegiance comes from this block.

### 4. `voices.v1.json` and `_exemplars/voices/`

| Register | Description (short) | Negative clause |
|---|---|---|
| `formal` | measured, complete sentences, titles and courtesy | not cold; formality is manner, not distance |
| `blunt` | short, direct, no softening | not rude for its own sake |
| `playful` | light, teasing, fond of wordplay | not mocking the player |
| `grim` | spare and dark, expects the worst | not despairing; grim creatures still act |
| `sly` | indirect, suggestive, leaves things unsaid | not lying by default |
| `gentle` | warm, patient, careful with others | not weak; gentleness is not submission |
| `none` | no register fits | the identity draft is refused and re-asked |

Each register row names its exemplar file, `gk-data/packs/fusion/data/seed/narrative/_exemplars/voices/<register>.en.json`
(new):

```json
{
  "schemaVersion": 1,
  "register": "grim",
  "locale": "en",
  "lines": ["<line>", "..."],
  "lexicon": { "signature": ["<word>", "..."], "forbidden": ["<word>", "..."] }
}
```

| Field | Meaning | Negative clause |
|---|---|---|
| `lines` | example lines in the register, used as the few-shot style reference in character briefs | not a character's own anchors; not tied to any species or name |
| `lexicon.signature` | words the register tends toward | not required words; a hint, never a quota |
| `lexicon.forbidden` | words that break the register | not an IP list — third-party marks are `ip-censor`'s registry (IC-3) |

Rules, each a test: the line count is within `character.exemplarLines.{min,max}` in
`gk-data/packs/fusion/data/seed/narrative/_plan/budget.v1.json` (the ideal's "3–5 anchor lines", `narrative-seed-ideal.md`
§6.3, as a budget row, never a constant); every line is Latin script with no digit, no brace and no
markup; no line names another game, franchise or person (the prompt-hygiene rule,
`docs/architecture/ip-censor/spec-avoid-list.md`). Exemplars are **hand-authored** — the `_exemplars/`
path is where authored content lives — and reviewed like code.

### 5. `line-contexts.v1.json`

Each context carries `keyedOn` — what fact picks the line at runtime — from a closed set:
`relation` (the disposition band), `personal-history` (something this character and the player did
together), `world-fact` (a world or faction state, never an individual encounter), `outing` (Alignment
2026-09-20: how the player's last outing went, read at a homeworld return — never a single enemy or encounter).

| Context | `keyedOn` | Description (short) | Negative clause |
|---|---|---|---|
| `greet` | relation | the first line when the player arrives | not a farewell; says nothing about past deeds |
| `farewell` | relation | the line when the player leaves | not a refusal |
| `thanks` | personal-history | after the player helped this character | not a generic pleasantry |
| `refused` | personal-history | after the player turned it down | not hostility in general |
| `spared` | personal-history | after the player won and let it go | not a surrender line |
| `betrayed` | personal-history | after the player broke faith with it | not ordinary disappointment |
| `joins` | personal-history | as it joins the player's side | not a greeting |
| `taunt` | relation | a hostile jab | not a threat of a specific consequence; no number, no promise |
| `rumor` | world-fact | a piece of world news or lore | not a quest offer; the runtime decides whether a quest follows |
| `doctrine` | world-fact | the antagonist's voice when its faction adopts a counter-doctrine (`npc-story-events-ideal.md` §6.12 "The voice") | reacts to the player's aggregate strategy, never to an encounter |
| `return-won` | outing | at home, after an outing that went well (a delve extracted, a world battle won, a piece recovered) | not praise for a specific kill; no number |
| `return-wiped` | outing | at home, after a party wiped or a siege failed | not blame and not a lesson in tactics |
| `return-lost` | outing | at home, after a sector was lost | not a threat of more loss |
| `return-quiet` | outing | at home, after an outing with nothing notable | not a greeting to a stranger; it knows the player was away |
| `none` | — | no context fits | the line call is refused |

### 6. `line-pairs.v1.json` — required (context, band) pairs, and the R13 rules

Pairs are declared per allegiance. Bands are the four ladder members read from the disposition file.

| Allegiance | Required pairs |
|---|---|
| `independent` | greet × all four · farewell × all four · thanks × {eager, open} · refused × {wary, hostile} · spared × {wary, hostile} · betrayed × {eager, open} · joins × {eager} · taunt × {hostile} · rumor × {eager, open, wary} |
| `ally` | greet × all four · farewell × all four · thanks × {eager, open} · refused × {wary, hostile} · rumor × {eager, open, wary} · return-won, return-wiped, return-lost, return-quiet × {eager, open} (Alignment 2026-09-20) |
| `antagonist` | greet × {wary, hostile} · farewell × {wary, hostile} · taunt × {wary, hostile} · doctrine × {hostile} |
| `player` | none — the summoner speaks only in spine scenes |

An antagonist's band is its **faction's** relation on the one ladder (R4), which is faction-level memory
and allowed by R13 rule 3.

**Homecoming lines are the hub's reaction (Alignment 2026-09-20).** Ideal §6.6 gives each character at home
*one conversation per return, reacting to how the outing went*. The `return-*` contexts are that reaction, on the
lines contract that already exists (§5, `narrative-contract` §6 `lines[]`), so no new seed kind is added: the
runtime classifies the return's outing (`npc-story-events/spec-sanctum-hub-host.md` §3) and plays the character's
line for that context and its current band as a one-line scene. They are `ally` pairs only — Hourbloom
(`lead_companion` → `ally`, §3) and companions; a visitor (`independent`) at home speaks through a `sanctum.hub`
storylet or its `greet` line; an antagonist is never at home (R13 rule 3). A band outside `{eager, open}` has no
`return-*` pair and falls back to `greet` for that band, which every allegiance that can be at home carries. A
conversation with choices is a `sanctum.hub` storylet (`storylet-vocab` §3.1).

**The R13 rules as data.** The file carries an `antagonistRules` block, each rule a test:

1. **No personal memory** (rule 3): no context with `keyedOn: personal-history` may appear in an
   antagonist pair, and `joins` is never an antagonist pair.
2. **No growth, no hierarchy** (rules 1–2): the character contract has no level, rank, title or
   subordinate field; this module records the prohibition so `narrative-contract`'s schema test can cite
   it, and `character-vocab` itself declares no rank or tier-of-command vocabulary.
3. **Recruit never targets an antagonist**: `storylet-vocab`'s `recruit` consequence is refused against
   a role whose allegiance is `antagonist` (enforced where both registries load, in
   `narrative-validators`).

Rules 4–6 (enemy bases, data sharing, warlord growth) govern runtime systems and are
`npc-story-events`' (`npc-story-events-map.md` principle 17); nothing here can express them.

### 7. The reader

`adapters/narrative/character_vocab.py` (new): loads the four files and the exemplars fresh, joins the
disposition ladder by path, and exposes `required_pairs(allegiance) -> frozenset[(context, band)]` for
`narrative-metrics` and `character-pipeline`.

### 8. `decisions.md` row (drafted; appended in the build change — map §11 item 6)

> **Generated antagonist content obeys counter-doctrine** (owner ruling R13, 2026-09-19). No generated
> enemy-side character carries a line keyed to its own past encounters with the player, a recruit
> outcome, a level, a rank or a title; enemy lines are keyed to the faction's relation band and to world
> facts only. Enforced as registry rules in `gk-data/packs/fusion/data/seed/narrative/_registry/line-pairs.v1.json` and
> validated by `narrative-validators`; cross-referenced to `npc-story-events-ideal.md` §6.12.

---

## Commands

```powershell
$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/test_narrative_character_vocab.py -q
```

## Project structure

```text
gk-data/packs/fusion/data/seed/narrative/_registry/roles.v1.json            (new) nine roles + none, and the leads block
gk-data/packs/fusion/data/seed/narrative/_registry/voices.v1.json           (new)
gk-data/packs/fusion/data/seed/narrative/_registry/line-contexts.v1.json    (new)
gk-data/packs/fusion/data/seed/narrative/_registry/line-pairs.v1.json       (new) pairs per allegiance + antagonistRules
gk-data/packs/fusion/data/seed/narrative/_exemplars/voices/<register>.en.json   (new) six authored exemplars
gk-data/packs/fusion/data/seed/narrative/_plan/budget.v1.json               block `character.exemplarLines`
gk-forge/tools/seedsmith/seedsmith/adapters/narrative/character_vocab.py   (new)
gk-forge/tools/seedsmith/tests/test_narrative_character_vocab.py           (new)
```

## Code style

As `storylet-vocab`: one reader, read fresh, frozen views, refusals naming file and key.

## Testing strategy

| Test | Asserts |
|---|---|
| `every_value_has_description_and_negative` | all four registries |
| `voted_lists_have_none` | `roles` and `voices` carry `none`; `line-contexts` carries `none` |
| `roles_match_the_runtime_list` | the nine members pinned with the reason: the runtime's closed role list (`npc-story-events-ideal.md` §6.3); a change is reviewed in both programs |
| `bands_are_the_disposition_file` | pair bands equal `disposition.v1.json` members; no second ladder |
| `every_pair_names_known_context_and_band` | join closure |
| `antagonist_pairs_have_no_personal_history` | R13 rule 3 |
| `joins_is_never_an_antagonist_pair` | R13 |
| `every_register_has_an_exemplar_that_loads` | file exists, line count within the budget bounds, Latin script, no digit, no brace |
| `exemplar_lines_cite_no_other_franchise` | fixture registry of invented marks, read through `ip-censor`'s shared `load_avoid_terms` helper (`docs/architecture/ip-censor/spec-avoid-list.md`), never a list kept here; absent registry = the test skips with a printed note, never fails (IC-3: the scan is a release gate, not a blocker). Audit 2026-09-19: the source of the mark list was unstated, which invited a private IP list (map §7) |
| `leads_block_matches_the_three_lead_tokens` | exactly `lead_summoner`, `lead_companion`, `lead_antagonist` — a declaration (R11) |
| `required_pairs_is_a_pure_function` | same input, same set |

No test counts characters or lines in any corpus.

## Boundaries

- **Always:** read the ladder from the disposition file; keep R13 as data with a test per rule; hand-author
  exemplars.
- **Ask first:** adding a role (it is the runtime's list too), a register or a context (Alignment 2026-09-20: the
  four `return-*` contexts were added by the cross-lane alignment to close the hub-conversation gap); making lines
  personality-specific.
- **Never:** a second relation ladder; a personality field; an antagonist line keyed to personal history.

## Success criteria

- [ ] Four registries and six exemplars exist and load.
- [ ] Every value has a description and a negative clause; voted lists admit `none`.
- [ ] Required pairs use exactly the four disposition bands.
- [ ] The R13 rules are data, and each has a test that fails on a crafted violation.
- [ ] Exemplar line bounds come from the budget file.

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
| 1 | low | `exemplar_lines_cite_no_other_franchise` did not say where its mark list comes from, inviting a private IP list (map §7, IC-3) | fixed (reads `ip-censor`'s helper; skips when absent) |
| 2 | low | R13 rules 1–3 are data with tests; rules 4–6 are correctly left to the runtime; the ladder is read, not copied; `roles` pinned as a declaration — no defect | verified |
| 3 | low | Citations sampled: `disposition.v1.json` members, `ContractPolicy.cs:195` — resolve | verified |

## Cross-lane alignment (2026-09-20)

Alignment 2026-09-20: `npc-story-events/spec-sanctum-hub-host.md` needed a seed shape for hub conversations that
this program did not define (`spec-scene-script-loader.md` §1 recorded the gap). The smallest change consistent with
ideal §6.6 and this contract: the `outing` `keyedOn` value and four `return-*` line contexts as `ally` pairs (§5, §6)
for the reaction, and the `sanctum.hub` host row in `storylet-vocab` §3.1 for conversations with choices. The shared
`line-contexts.v1.json` is read by the runtime's `LineContextCatalog` (`npc-story-events/spec-narrative-vocabulary.md`
§1), which picks the new members up from the file.
