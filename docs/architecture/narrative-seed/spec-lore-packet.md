# Spec: `lore-packet`

**Program:** [narrative-seed](../narrative-seed-map.md) · **Module id:** `lore-packet` · **Map row:** 15 · **Wave:** 4
**Depends on:** `gloss-registry`, `names-registry`, `token-grammar` · **Soft, cross-program:** `ip-censor` `avoid-list` · **Model calls:** none
**Ideal:** [../narrative-seed-ideal.md](../narrative-seed-ideal.md) §5.1 (GENEVA), §5.4, §6.5, §6.5b, §11 items 1, 6 and 9
**Status:** spec phase, 2026-09-19. Map approved by the owner 2026-09-19. No build authorized.

---

## Objective

Build the **grounding packet** every narrative model call carries: the facts the call may use, in the
target language, and nothing that would let the model leak a name, a foreign-script token or a magnitude.
One deterministic, content-addressed function builds it; every pipeline renders it into its brief the same
way.

The packet exists because a model falls back on generic fantasy for an obscure world (GENEVA, ideal
§5.1), because a foreign-script token in the brief is what caused 53 of 54 committed Delve events to leak
Han characters (map §3.4), and because a name the model never sees is a name it cannot copy (ideal §6.5b).

**What it contains:** species facts, place, faction, motif glosses, the declared tokens with their
descriptions and feature tags, the allowed-entity list, and the free IP avoid-list rendered from the
`ip-censor` registry. **What it never contains:** a display name of any entity, a raw motif, a number, or
another franchise's name as a style reference.

## Design

### 1. Shape

A frozen, canonical-JSON structure, one per work-order item, built by `build_packet(work_item, registries)`.
Every field is closed or derived from a closed source; none is model-written.

| Field | Content | Source | Never |
|---|---|---|---|
| `subject` | the seed kind and planned id (`storylet.curio-fire-004`) | the planner's work item | a display name |
| `species` | for a character or a cast role with a planned species: side, primary element, family **gloss**, posture words, up to `packet.maxMotifs` motif **glosses** — when a species has more motifs than that, the ones kept are the first `packet.maxMotifs` in `order_for(subjectId, "motifs", 0)` order (Audit 2026-09-19: the selection rule was unstated, so the packet was not provably deterministic) | species anchor (`gk-data/packs/fusion/data/seed/creatures/species/`), glosses through `gloss-registry`'s lookup | the species' catalog or almanac name (R8: prose never names a species) |
| `place` | host kind description and climate description | `storylet-vocab` host kinds; climate from the element vocabulary | a map coordinate or a real sector name |
| `faction` | the side vocabulary (`plant · zombie · none`) and, where the antagonist's faction is in play, the token `{lead_antagonist}` with its description | contract and token grammar | a faction display name |
| `motifs` | target-language glosses for the subject's motifs, each marked as flavour to draw on, never a word to quote | `gloss-registry`'s lookup, which **refuses** an unglossed motif | a raw motif in any script |
| `tokens` | every token this seed may use: its id, its description with the negative clause, and its closed feature tags (`article`, `gender`, `number`) | `token-grammar` descriptions; feature tags from the names registry rows | the token's display string |
| `allowedEntities` | the closed list of entity token ids the text may reference (leads, planned cast characters, declared roles, runtime slots) | the work item plus the contract | any entity not in the list |
| `avoid` | the IP avoid-line, or empty | `ip-censor`'s `avoid-list` helper | a per-adapter IP list |
| `packetHash` | `sha256` of the canonical packet minus this field | derived | — |

**Feature tags without display strings.** A character name's grammatical gender and number matter to the
text around the token (a verb agreement, an article, agreement in a later locale). The packet carries the
tags the names registry declares for each token so the model can keep the surrounding text agreeing,
without ever seeing "the Rotwright". **Pronouns are tokens, never words the model picks:** the model writes
`{lead_antagonist} raises {lead_antagonist_poss} hand`, and the runtime renders the pronoun from the
entity's registry tags ([spec-token-grammar.md](spec-token-grammar.md) §3, pronoun suffixes `_subj`,
`_obj`, `_poss`), so a rename or a re-gendered row cannot break agreement. Reconciled 2026-09-19: this
paragraph used to have the model write a literal pronoun (`raises his hand`) from the gender tag, which
contradicted token-grammar. This is why the module depends on `names-registry`:
it reads the tag columns, never the display column, and a test fails if any display string appears in any
rendered packet.

### 2. Motif glosses — refuse, never pass through

Motifs reach the packet only through `gloss-registry`'s lookup — `GlossTable.gloss_all` in
`gk-forge/tools/seedsmith/seedsmith/briefkit/gloss.py` (new, owned by `gloss-registry`,
[spec-gloss-registry.md](spec-gloss-registry.md) §4), which raises `GlossMissing` listing every unglossed
motif. A motif with no gloss is a **refusal**: the packet build fails naming the motif and the subject, and the work item is reported `blocked: unglossed
motif`, never sent with the raw token and never sent with the motif silently dropped (a silent drop would
change the brief without anyone knowing). The committed motif list is Chinese throughout
(`gk-data/packs/fusion/data/seed/creatures/_registry/motifs.v1.json`; ideal §11 item 1), so until `gloss-fill` lands, every
work item that needs a motif refuses — which is correct: `gloss-fill` runs in Wave 0, long before any
narrative pipeline (map §6; Owner ruling 2026-09-19 (round 4), was "first in Wave 5").

The dungeon brief's demand *"Use at least one of the listed motifs"*
(`gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/briefs.py:324`) is the cause of the committed leak. Narrative
briefs render glosses under the heading "flavour to draw on (do not quote)" and never require a motif to
appear; motif coverage is not a narrative validator.

### 3. The IP avoid-list — free, advisory, owned elsewhere

`lore-packet` calls `ip-censor`'s shared helper — `load_avoid_terms` and `render_avoid_line` in
`gk-forge/tools/seedsmith/seedsmith/briefkit/avoid_list.py` (new, owned by `ip-censor`'s `avoid-list` module,
`docs/architecture/ip-censor/spec-avoid-list.md`). It never reads the registry file itself and never keeps
its own list (map §7).

| Registry state | Packet behaviour |
|---|---|
| `gk-data/packs/fusion/data/seed/ip-censor/_registry/marks.v1.json` (new, owned by `ip-censor`) does not exist yet | `avoid` is empty; provenance records `avoidList: absent`; generation proceeds (IC-3: the list is advisory and never a blocker) |
| exists and parses | `avoid` is the rendered line; provenance records the registry file's content hash, so a registry change stales exactly the briefs that saw it |
| exists but the helper refuses its shape | the build stops with the helper's own error; a malformed registry is never guessed around |

No answer-side IP check, retry or refusal is added on the strength of the list (IC-3; ideal §6.5b). The
narrative corpus is scanned by `ip-censor`'s release gate, whose scope already includes the narrative
surfaces (`docs/architecture/ip-censor/spec-registry.md` "Narrative surface" table).

### 4. Prompt hygiene

- **No franchise named as a style reference** (ip-censor ideal "Narrative generation" row 6). The packet
  and the brief template carry style only through the program's own exemplars (`character-vocab`'s
  `_exemplars/`) and anchor lines. A test renders a fixture brief and asserts no registry mark spelling
  appears outside the avoid line.
- **No citation instead of content.** Closed vocabularies are written into the packet literally, read from
  the registry at build time, never cited by filename — briefkit's rule
  (`gk-forge/tools/seedsmith/seedsmith/briefkit/__init__.py:1-6`).
- **No number.** The packet carries bands and vocabulary words only; a digit anywhere in a rendered packet
  outside ids and hashes fails the build.

### 5. Determinism and staleness

The packet is a pure function of the work item and the registry versions it read. `packetHash` joins the
seed's provenance input hashes (the staleness key `narrative-emit` records, the
`staleness_key` shape at `gk-forge/tools/seedsmith/seedsmith/pipeline/staleness.py:32`), so a changed gloss, token
description, feature tag or avoid-list stales exactly the seeds whose packets it changed and no others.

### 6. Tunables

Budget file `gk-data/packs/fusion/data/seed/narrative/_plan/budget.v1.json` (new), block `packet`.

| Key | Unit | Starting value | Rationale |
|---|---|---|---|
| `packet.maxMotifs` | glosses per species | 6 | enough flavour to ground a call without crowding the structure out of a small model's attention; revised from review verdicts tagged `lore` |

## Commands

```powershell
$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest tools/seedsmith/tests/test_narrative_lore_packet.py -q
cd tools\seedsmith; python -m seedsmith narrative packet --item <workItemId> --print    # render one packet, model-free
cd tools\seedsmith; python -m seedsmith narrative packet --all --check                  # build every packet in the plan; exit 1 on any refusal
```

## Project structure

```text
tools/seedsmith/seedsmith/adapters/narrative/packet.py        (new) build_packet, render_packet_section
tools/seedsmith/tests/test_narrative_lore_packet.py           (new)
```

## Code style

```python
def build_packet(item: "WorkItem", regs: "NarrativeRegistries") -> LorePacket:
    """Pure. Raises UnglossedMotif naming the motif and the subject; never passes a raw motif and
    never drops one silently. Reads feature-tag columns of the names registry, never display strings."""
```

## Testing strategy

Fixture registries (invented marks and names, never real ones — `gk-forge/tools/seedsmith/**` is a
`generator-prompt` surface for the release gate); the model transport stubbed to raise.

| Test | Asserts |
|---|---|
| `packet_is_deterministic` | the same item and registries give byte-identical packets and the same `packetHash` |
| `motif_selection_is_seeded_from_the_subject` | a species with more motifs than `packet.maxMotifs` keeps the `order_for` prefix; two subjects of one species may keep different motifs, each reproducibly |
| `unglossed_motif_refuses_naming_it` | a fixture motif with no gloss raises, naming motif and subject |
| `no_raw_motif_in_any_packet` | every rendered packet passes `script_policy` under policy `latin` (`script-check`, [spec-script-check.md](spec-script-check.md) §4) |
| `no_display_string_in_any_packet` | no names-registry display string and no species catalog name appears in any rendered packet |
| `feature_tags_ride_with_tokens` | each declared token carries its registry row's `article`, `gender`, `number` tags |
| `allowed_entities_match_declared_tokens` | the allowed-entity list is exactly the leads, planned cast, declared roles and slots |
| `avoid_list_absent_is_not_a_blocker` | with no registry file, the packet builds, `avoid` is empty, provenance says `absent` |
| `avoid_list_change_stales_only_its_briefs` | changing the fixture registry changes `packetHash` for every packet (all briefs saw it) and nothing else in provenance |
| `no_franchise_style_reference` | a rendered fixture brief contains no fixture-registry mark spelling outside the avoid line |
| `no_digit_in_packet` | no decimal digit appears outside ids and hashes |
| `gloss_change_stales_exactly_its_subjects` | changing one gloss changes the hash of the packets that used that motif and no others |

## Success criteria

1. Every narrative work item gets a packet from one function, and the packet's hash joins its provenance.
2. No packet contains a raw motif, a display name, a species catalog name, a digit or a franchise
   reference, each proven by test.
3. An unglossed motif stops the item with a named refusal.
4. The avoid-list comes only from `ip-censor`'s helper and never blocks generation.
5. The suite passes with the model transport stubbed to raise.

## Boundaries

- **Always:** glosses through the lookup; tokens with descriptions and feature tags; literal vocabularies;
  the avoid-list from the shared helper; canonical, hashed output.
- **Ask first:** adding a new fact family to the packet (it changes every brief hash and stales the whole
  corpus); raising `packet.maxMotifs` past a value that has not been reviewed.
- **Never:** pass a raw motif; drop an unglossed motif silently; include any display string; keep an IP
  list here or block on it (IC-3); name another franchise; include a number.

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
| 1 | medium | Which motifs survive `packet.maxMotifs` was unstated, so the packet was not provably deterministic | fixed (`order_for` prefix + test) |
| 2 | low | "Wave 5 runs `gloss-fill` first" is stale after round 4 | fixed |
| 3 | low | IC-3 honoured: avoid-list advisory, never a blocker, no private list | verified |
