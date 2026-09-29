# Spec: `ip-censor` / `curate` — dataset import, then human reconfirmation

**Program:** `ip-censor` · **Module id:** `curate` · **Depends on:** `registry`, `census`
**Capability map:** [../ip-censor-map.md](../ip-censor-map.md) · **Ideal:** [../ip-censor-ideal.md](../ip-censor-ideal.md)
**Status:** spec phase, 2026-09-19. No build authorized. **Added 2026-09-19 (owner ruling IC-2)** — this
module exists because of that ruling.

---

## Objective

Build the registry the way the owner ruled (IC-2): **first** import a trademark dataset, curated down to
game-related marks; **then** re-confirm the registry from the census and from model-proposed candidates,
each confirmed by a person. Every admitted row records which stage admitted it.

`curate` produces **candidates** and transcribes **a person's decisions**. It never admits a row on its
own judgement. The ideal's rule stands: the registry is curated and small, never a copy of a bulk
dataset (a 76M-record register would be un-auditable and would flag the deliberate identity).

Three verbs:

| Verb | Stage | Reads | Writes |
|---|---|---|---|
| `curate import` | `import` | a downloaded dataset export + the authored filter `gk-data/packs/fusion/data/seed/ip-censor/_registry/import-filter.v1.json` | a candidate file under `tasks/ip-censor/curate/` |
| `curate reconfirm` | `reconfirm` | the registry, `census` output, and (optionally) model proposals | a candidate file under `tasks/ip-censor/curate/` |
| `curate admit` | either | a candidate file on which a person has recorded a decision per row | `marks.v1.json`, adding each accepted row with its `admission` record |

**Success criteria**
- `import` applies only the authored filter: the Nice classes, status and goods-description terms that
  mean "game-related" are data, never code. A missing filter key throws naming it.
- Every candidate carries its evidence: `dataset` (dataset id + record id) for `import`; `census`
  (the census run and the surfaces the token occurs on) or `model-proposal` (the proposal run and the
  model) for `reconfirm`.
- `admit` refuses a candidate with no decision, no `confirmedBy` or no scope, and refuses to overwrite an
  existing row's admitting stage. Re-checking an imported row sets `reconfirmedOn` only.
- The model is optional and never decides. With the model off, `reconfirm` still runs on census
  evidence alone.
- Deterministic with the model stubbed: the same inputs give byte-identical candidate files.

## The dataset — decided by principle

The ideal lists USPTO, the WIPO Global Brand Database, EUIPO and TMview. The first adapter reads the
**USPTO trademark bulk data**, because it is public and published for bulk download, so the import is
repeatable without scraping. Each further register is one more adapter behind the same candidate shape.
The raw export is **not committed** (its size, and it is not our data); the dataset id and its version
are recorded in every candidate's `source`. The adapter pins the export format it was written against
and refuses an unknown one. This spec has not downloaded the export; the exact format is read at build
time.

**What "curated down" means here.** The filter narrows the dataset to game-related marks; a person then
reviews the candidates row by row. The result must stay small enough for that review. The filter's
values are tuned against real candidate output, which is why they live in an authored file.

## Tech Stack

Python 3.11+, standard library (`json`, `csv`, `xml.etree` as the export needs). The model path uses the
tool's one injected client, `gk-core/tools/ip-censor/ipcensor/llm.py`, shared with `suggest`
(`spec-suggest.md` §One LLM client). No new dependency.

## Commands

```powershell
$env:PYTHONPATH = "gk-core/tools/ip-censor"; python -m ipcensor.report curate import --dataset uspto --input <export path>
$env:PYTHONPATH = "gk-core/tools/ip-censor"; python -m ipcensor.report curate reconfirm --no-model
$env:PYTHONPATH = "gk-core/tools/ip-censor"; python -m ipcensor.report curate reconfirm
$env:PYTHONPATH = "gk-core/tools/ip-censor"; python -m ipcensor.report curate admit --candidates tasks/ip-censor/curate/<file>.json
$env:PYTHONPATH = "gk-core/tools/ip-censor"; python -m pytest gk-core/tools/ip-censor/tests/test_curate.py -q
```

## Project Structure

```text
gk-core/tools/ip-censor/ipcensor/curate.py                 → this module (new)
gk-core/tools/ip-censor/ipcensor/datasets/uspto.py         → first dataset adapter (new)
gk-core/tools/ip-censor/ipcensor/llm.py                    → the tool's one LLM client (new; shared with suggest)
gk-core/tools/ip-censor/tests/test_curate.py               → its tests (new)
gk-data/packs/fusion/data/seed/ip-censor/_registry/import-filter.v1.json → authored filter (new)
tasks/ip-censor/curate/                            → candidate files (evidence; self_paths class 3)
```

## Code Style

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True, slots=True)
class Candidate:
    mark: str
    aliases: tuple[str, ...]
    category: Category                 # from registry: franchise-mark | real-person | company-brand
    stage: Stage                       # "import" | "reconfirm"
    evidence: Evidence                 # "dataset" | "census" | "model-proposal"
    source: str
    decision: Literal["accept", "reject"] | None   # set by a person, never by this module
    confirmed_by: str | None
    scope: frozenset[Surface] | None   # set by a person on accept; no default
```

`admit` writes through the `registry` module's own serializer and re-parses the result, so a row the
parser would reject never lands.

## Testing Strategy

`pytest`, `gk-core/tools/ip-censor/tests/test_curate.py` (new). No network; fixtures use invented marks.

- **Import** — a fixture export yields candidates filtered by a fixture `import-filter.v1.json`, each with
  `stage: "import"`, `evidence: "dataset"` and a source naming the record; a filter missing a key throws.
- **Reconfirm, census only** — a fixture census plus a fixture registry yields census candidates for
  in-scope tokens not in the registry and a re-check entry for registry rows the census still finds; the
  proposer is not called under `--no-model`.
- **Reconfirm, with a stub model** — proposals are candidates with `evidence: "model-proposal"` and the
  model recorded; a proposer that raises is recorded, not fatal.
- **Admit** — accepted rows land with their admission record; a row without a decision, `confirmedBy` or
  scope is refused; re-checking an imported row sets `reconfirmedOn` and keeps `stage: "import"`.
- **Determinism** — byte-identical candidate files with the model stubbed.
- **Population discipline** — no test asserts how many marks the real dataset or the real registry holds.

## Boundaries

- **Always:** keep the filter in data; record evidence on every candidate; let only a person decide;
  write the registry through its parser.
- **Ask first:** adding a dataset adapter; committing a raw export.
- **Never:** admit a row without a person's decision; import a dataset wholesale; let the model's
  answer set a scope or a category; write outside `tasks/ip-censor/curate/` and `marks.v1.json`.

## Open Questions

None.
