# Spec: `gloss-registry`

**Program:** [narrative-seed](../narrative-seed-map.md) · **Module id:** `gloss-registry` · **Map row:** 3 · **Wave:** 0
**Depends on:** none · **Model calls:** none (the one model pass that fills it is `gloss-fill`, Wave 0 — Owner ruling 2026-09-19 (round 4), was Wave 5)
**Status:** spec phase, 2026-09-19. Map approved by the owner 2026-09-19; no build authorized.

---

## Objective

Define the motif gloss registry — one target-language gloss per creature motif, keyed by the motif,
versioned under `_registry/` — and the one lookup every brief uses to read it. The lookup **refuses** a
motif that has no gloss; it never passes the raw token through and never drops it silently.

Why: the Delve event brief injects raw Chinese motifs and tells the model to *"Use at least one of the
listed motifs"* (`gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/briefs.py:324`, motifs placed at `:354`),
and the leaked words in the committed corpus are those motifs (`narrative-seed-ideal.md` §4.4). Every
motif in the registry is Chinese today (`narrative-seed-map.md` §3.3). The fix for the cause is to hand
the model a target-language gloss from a deterministic lookup; this module is that lookup and its data
contract. `gloss-fill` produces the rows; `dungeon-generator-repair` and `lore-packet` consume them.

**Done means:** the file exists with its header and an empty `glosses` object, the loader validates it
and refuses malformed rows, and the lookup raises a named refusal listing every unglossed motif. The
split from `gloss-fill` is deliberate (map §4 "Why these boundaries"): the repair in Wave 0 is built and
tested against a fixture table and spends no model call.

---

## Design

### 1. The source vocabulary

| Fact | Evidence |
|---|---|
| The motif list is a flat list under `motifs`, kept in sync by the creature program's motif derivation | `gk-data/packs/fusion/data/seed/creatures/_registry/motifs.v1.json`; reader `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/registries.py:122-127` |
| Each theme row carries its own `motifs` and `antiMotifs` | `gk-data/packs/fusion/data/seed/creatures/_registry/themes.v1.json`; reader `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/registries.py:106-113` |
| The motif registry's version is already recorded as a dungeon input | `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/registries.py:52-60` (`creatures.motifs`) |

The gloss registry is a **view** of that list in one target language. It never adds, removes or renames
a motif; the creature program owns the list (`narrative-seed-map.md` §7).

### 2. The file — `gk-data/packs/fusion/data/seed/narrative/_registry/motif-glosses.en.v1.json` (new)

```json
{
  "schemaVersion": 1,
  "registryVersion": 1,
  "locale": "en",
  "source": { "registry": "gk-data/packs/fusion/data/seed/creatures/_registry/motifs.v1.json", "registryVersion": 1 },
  "glosses": {
    "<motif>": {
      "gloss": "<target-language phrase>",
      "sense": "concrete | abstract | action | quality | none",
      "model": "<resolved model id>",
      "promptVersion": "<gloss-fill prompt version>"
    }
  }
}
```

| Field | Meaning | Negative clause |
|---|---|---|
| `locale` | the target language of every gloss in the file; the file name carries the same code | not a list: one file per locale; a second locale is a second file |
| `source.registryVersion` | the motif registry version this table was filled against | not a compatibility gate: a moved version makes the table *stale* (a reading), never unloadable |
| `glosses` key | a motif exactly as it appears in the source list | not normalised, not translated, not a display string |
| `gloss` | a short target-language phrase carrying the motif's meaning, used inside a brief | not a name, not a sentence, never the transliterated source word, never containing a digit |
| `sense` | the kind of meaning, `gloss-fill`'s closed enum (`concrete · abstract · action · quality · none`), used to stratify the review sample | not a part-of-speech tag for grammar; `none` means the sense could not be placed and is a review signal |
| `model` | the resolved model that wrote the row (`model-config-resolve`) | never a default string; a row with no recorded model is refused |
| `promptVersion` | the `gloss-fill` prompt version that wrote the row | not a registry version |

**Every row is generated output.** Rows are written only by `gloss-fill`'s commit step after review; a
rejected gloss is regenerated with the reviewer's reason named in its brief, never hand-typed
(`spec-gloss-fill.md` §4, map §2 principle 8). The file lives under `_registry/` because it is read as a
vocabulary by every brief; the row-level `model` and `promptVersion` are what make its origin auditable.

This module commits the file with the header and `"glosses": {}`. Until `gloss-fill` runs, every lookup
refuses — the honest state, since there is nothing correct to pass.

### 3. The loader — refuse, never default

`load_glosses(locale: str = "en", path: Path | None = None) -> GlossTable` reads the file (a fixture path
in tests) and refuses, naming the offending key, when:

- a top-level or row key is unknown or missing (forward compatibility comes from `schemaVersion`);
- `locale` differs from the requested locale or the file name's code;
- a `gloss` is empty, contains a digit, contains any character outside `A–Z a–z`, space, hyphen and
  apostrophe (a strict allow-list: a gloss is a short English phrase, so this module does not need the
  general classifier from `script-check`), or has more words than `gloss.maxWords`;
- `sense` is outside the closed enum;
- `model` or `promptVersion` is empty.

`gloss.maxWords` is read from the narrative generation budget,
`gk-data/packs/fusion/data/seed/narrative/_plan/budget.v1.json` (new), block `gloss`. This module creates that file with this
one row, at the value `spec-gloss-fill.md`'s budget table states (4 words: a gloss is flavour for a brief,
not a definition); later modules add their own blocks. No bound is a code constant.

Readings, printed by a `report` helper and never asserted: rows whose motif is no longer in the source
list (orphans — kept, because a motif can return), source motifs with no row (the work `gloss-fill`
still owes), and whether `source.registryVersion` trails the live motif registry.

### 4. The lookup — `briefkit/gloss.py` (new)

```python
class GlossMissing(BriefRefusal):
    """Raised with EVERY unglossed motif in the request, not the first. A subclass of briefkit's
    BriefRefusal, so a brief builder that already refuses on a citation refuses on this too."""
    motifs: tuple[str, ...]

class GlossTable:
    def gloss(self, motif: str) -> str: ...                      # raises GlossMissing
    def gloss_all(self, motifs: Sequence[str]) -> tuple[str, ...]: ...   # order-preserving; raises listing all missing
    def missing(self, motifs: Iterable[str]) -> tuple[str, ...]: ...     # sorted; for reports
```

`BriefRefusal` is `gk-forge/tools/seedsmith/seedsmith/briefkit/render.py:38`. The lookup lives in `briefkit`
because briefkit's rule is exactly this one — *every closed vocabulary a brief depends on is written into
the brief literally, read from the registry at generation time*
(`gk-forge/tools/seedsmith/seedsmith/briefkit/__init__.py:1-6`) — and because a gloss lookup is not narrative
knowledge: the dungeon adapter needs it as much as the narrative one, so it belongs to the shared brief
kit, not to either adapter (seedsmith P5). The same placement is used for the IP avoid-list helper
(`docs/architecture/ip-censor/spec-avoid-list.md`).

The lookup never returns the source motif, an empty string or a placeholder. A caller that wants to go
ahead without a gloss has no API to do it with.

### 5. Relations to other programs

- **`ip-censor`.** Glosses are generated text and a translation can surface a mark the source hid
  (`docs/architecture/ip-censor-ideal.md` "Narrative generation" row 7). The file is in the release scan's
  scope; this module adds no IP check (IC-3).
- **`creature-seed`.** Species display names are a separate table coordinated with `creature-seed`
  (map §7); this registry holds motif glosses only.

---

## Commands

```powershell
$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/test_briefkit_gloss.py -q
# Readings: rows, orphans, unglossed motifs, source-version lag
cd tools\seedsmith; python -c "from seedsmith.briefkit.gloss import load_glosses, coverage_report; print(coverage_report(load_glosses()))"
```

## Project structure

```text
gk-data/packs/fusion/data/seed/narrative/_registry/motif-glosses.en.v1.json   (new) header + empty glosses
gk-data/packs/fusion/data/seed/narrative/_plan/budget.v1.json                  (new) block `gloss` with `maxWords` only
gk-forge/tools/seedsmith/seedsmith/briefkit/gloss.py               (new) load_glosses, GlossTable, GlossMissing, coverage_report
gk-forge/tools/seedsmith/seedsmith/briefkit/__init__.py            export the three names
gk-forge/tools/seedsmith/tests/test_briefkit_gloss.py              (new)
```

## Code style

Match `gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/registries.py`: read fresh on every call, never
transcribed; resolve paths through `gk-forge/tools/seedsmith/seedsmith/workspace_roots.py:47` (`content_root`)
rather than a hard-coded parent count. Refusals name the key and the value.

## Testing strategy

Fixture tables only — invented motifs and glosses, so a real registry row never turns a test red
(`docs/architecture/validation-ssot.md`).

| Test | Asserts |
|---|---|
| `lookup_returns_gloss_never_motif` | a glossed motif returns its gloss; the return value never equals the key |
| `missing_motif_raises_with_every_missing_motif` | a request with two unglossed motifs raises `GlossMissing` naming both |
| `gloss_missing_is_a_brief_refusal` | `issubclass(GlossMissing, BriefRefusal)` |
| `loader_refuses_unknown_key`, `..._missing_key` | named key in the message |
| `loader_refuses_locale_mismatch` | file `en`, row set declared `fr` → refused |
| `loader_refuses_digit_foreign_script_and_empty_gloss` | one fixture each |
| `loader_refuses_gloss_over_max_words` | bound read from a fixture budget file, not a constant |
| `loader_refuses_row_without_model_or_prompt_version` | provenance is required |
| `sense_is_closed` | the five members pinned — a declaration shared with `gloss-fill` |
| `committed_file_loads` | the real file loads (header valid); its row count is printed, never asserted |
| `coverage_report_lists_orphans_and_missing` | fixture source list vs fixture table |

## Boundaries

- **Always:** refuse an unglossed motif; read bounds from the budget file; keep one file per locale.
- **Ask first:** changing the row shape (it is `gloss-fill`'s output contract too); adding a locale.
- **Never:** return a raw motif; hand-edit a row; own or edit the motif list; add an IP check.

## Success criteria

- [ ] The file exists and loads; malformed fixtures are refused with the key named.
- [ ] `GlossMissing` lists every unglossed motif and is a `BriefRefusal`.
- [ ] No lookup path can return a source motif.
- [ ] `gloss.maxWords` lives in `gk-data/packs/fusion/data/seed/narrative/_plan/budget.v1.json`, not in code.
- [ ] The suite passes with the transport stubbed to raise (this module makes no call at all).

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
| 1 | low | Header said `gloss-fill` is Wave 5; the round-4 ruling moved it to Wave 0 | fixed |
| 2 | low | Refusal lookup, `maxWords` in the budget file, fixture-only tests, IC-3 respected | verified |
