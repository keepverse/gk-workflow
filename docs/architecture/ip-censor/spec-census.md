# Spec: `ip-censor` / `census` — distinct-token census

**Program:** `ip-censor` · **Module id:** `census` · **Depends on:** `source`
**Capability map:** [../ip-censor-map.md](../ip-censor-map.md) · **Ideal:** [../ip-censor-ideal.md](../ip-censor-ideal.md)
**Status:** spec phase, 2026-09-19. No build authorized. **Amended 2026-09-19 (owner rulings IC-1,
IC-2).**

---

## Objective

Answer the owner's first request — *"list all targets first … detect and save token pools"* — with a
complete, read-only reading of what actually occurs in the tree, so the registry can be curated
against evidence rather than guesses.

`census` is the module that makes the registry honest. `ip-censor-ideal.md` §6.4 shows what happens
without it: a hand-written mark list aliases `wow` and produces 142 prose false positives. The census
is what would have caught that on day one.

**Amended 2026-09-19 (owner ruling IC-2).** The census is also the evidence input of the registry's
second curation stage: `curate reconfirm` reads census output to re-confirm imported rows and to surface
new candidates for a person to confirm ([spec-curate.md](spec-curate.md)). The census itself stays
read-only and decides nothing; it gains no dependency (the edge is `curate → census`).

**Success criteria**
- Emit, per distinct token: total count, per-tree distribution (`docs`, `src`, `data`, `web`,
  `tools`, `tests`, `tasks`, …), and the surface category each occurrence lands on.
- Tokenization is **word-boundary by the `registry` boundary policy**, not `\b` (which is measurably
  wrong twice on this corpus).
- Case folding uses `str.casefold()`, never `.lower()` — measured: `.lower()` misses `Pokémon`.
- Output is **sorted deterministically** and byte-stable across runs.
- **A count is never asserted as truth in a test.** Counts are a reading of a population that changes
  whenever content ships (`validation-ssot.md`); the census reports them, the suite does not pin them.

## Tech Stack

Python 3.11+. Standard library for the tokenizer (`collections.Counter`, `re`, `unicodedata`).
`pyahocorasick` is imported **only by `scan`**; the census enumerates all tokens and needs no
multi-pattern automaton. `jieba` is already a dependency of `gk-forge/tools/seedsmith` and is available if Han
segmentation is needed — see Open Questions.

## Commands

```powershell
# Full census, JSON to stdout
$env:PYTHONPATH = "gk-core/tools/ip-censor"; python -m ipcensor.report census --format json
# Census restricted to a subtree, useful while curating one mark
$env:PYTHONPATH = "gk-core/tools/ip-censor"; python -m ipcensor.report census --tree data --top 200
$env:PYTHONPATH = "gk-core/tools/ip-censor"; python -m pytest gk-core/tools/ip-censor/tests/test_census.py -q
```

## Project Structure

```text
gk-core/tools/ip-censor/ipcensor/census.py   → this module
gk-core/tools/ip-censor/tests/test_census.py
gk-core/tools/ip-censor/tests/fixtures/      → small synthetic trees with known token sets
```

Census output is **not** committed by default. If the owner wants a snapshot baseline, it goes to
`tasks/ip-censor/census-<date>.md` as evidence, not `data/` as authority.

## Code Style

```python
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TokenStat:
    token: str                      # casefolded canonical form
    display: str                    # most frequent original casing, for the report
    total: int
    by_tree: dict[str, int]         # {"docs": 2119, "src": 782, ...}
    by_surface: dict[str, int]      # {"docs-prose": 2119, "code-identifier": 782, "player-prose": ...}


def census(files: Iterable[SourceFile], boundary: BoundaryPolicy) -> list[TokenStat]:
    """Distinct tokens with counts. Sorted by (total desc, token asc) — deterministic."""
```

Conventions: `Counter` for accumulation; the surface classification is **shared with `scan`** via a
single function the map places in `scan` — see Open Question 1.

## Testing Strategy

`pytest`, `gk-core/tools/ip-censor/tests/test_census.py` (new).

Levels:
- **Unit** — a synthetic tree with a hand-built known token set yields exactly those tokens and
  counts; `demonstrate` does not yield `demon`; `PVZ`, `PvZ`, `pvz` collapse to one token under
  casefold while `display` preserves the dominant casing.
- **Boundary** — a fixture containing `PvZ融合版`, `pvz-fusion-almanac`, `PVZRH`, `drop.pvz.run`
  produces the classification the boundary policy declares (this is the regression test for both
  measured `\b` failures).
- **Determinism** — two runs over the same fixture are byte-identical.
- **Population discipline** — the suite asserts *shape* (keys present, counts non-negative,
  distributions sum to total) and **never** a specific total for the real tree.

## Boundaries

- **Always:** sort deterministically; casefold with `str.casefold()`; classify surface using the one
  shared classifier; keep the census read-only.
- **Ask first:** committing a census snapshot as a baseline; adding Han segmentation; changing the
  surface category vocabulary (closed — owned by `registry`).
- **Never:** assert a token count from the real tree in a test; treat the census as an enforcement
  gate (it reports, `scan` enforces); write to the tree.

## Open Questions

1. **Where does the surface classifier live?** Both `census` and `scan` need "which surface is this
   occurrence on" (path → `docs-prose` / `code-identifier` / `player-name` / `generator-prompt`).
   The map places the bucket vocabulary in `scan`, but `census` needs it first. Recommendation: the
   **classifier is a pure function in `registry`** (it is policy), consumed by both — which keeps the
   map's acyclic direction (`registry` is a root) while removing a `census → scan` edge.
   **The map has been amended to match** (audit A10): `scan`'s row now names the buckets explicitly,
   and `registry` owns `Surface`. This is a resolved interface change, not an open question.
2. **Is a census snapshot worth committing?** It is a population, so it goes stale on every content
   ship. Recommendation: **no**; it is a curated-registry input, generated on demand.
3. ~~Han tokens~~ — resolved by measurement (audit A8) and, for the deferred half, by **IC-1**
   (amended 2026-09-19). The measured need is **boundary** handling on `PvZ融合版`, which the
   `registry` boundary policy supplies. The category list is now settled (three categories, none
   restricted by script), so a Chinese spelling of an in-scope mark is an **alias** in the registry and
   is found by `scan`, not by census segmentation. `jieba` segmentation therefore stays off; it would
   only be a curation convenience. Kept as a trail.

## The `census` → `registry` classifier dependency (audit A10)

`census` previously listed `scan` as an indirect need for surface classification, which the map's
acyclic rule forbids (`census` and `scan` must be independent). Resolved: **`registry` owns the
`Surface` vocabulary and its classifier**, and both `census` and `scan` consume it. `registry` is
already a root, so no new edge appears and no module gains a dependency on a sibling.

