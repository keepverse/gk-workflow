# Spec: `ip-censor` / `suggest` — the censor-token proposal

**Program:** `ip-censor` · **Module id:** `suggest` · **Depends on:** `registry`, `scan`
**Capability map:** [../ip-censor-map.md](../ip-censor-map.md) · **Ideal:** [../ip-censor-ideal.md](../ip-censor-ideal.md)
**Status:** spec phase, 2026-09-19. No build authorized. **Amended 2026-09-19 (owner rulings IC-1b,
IC-2, IC-3; narrative ruling R11).**

---

## Objective

Attach a **suggested censor token** to each finding, so the plan a future execute program consumes
already says *what to replace it with* — the owner's *"suggest new censor token by agent"*.

Two rules make this safe, and they are the whole spec:

1. **The authored map wins.** If `registry`'s `replacements.v1.json` (new) has a pair, that pair is
   used verbatim. An LLM never overrides an owner-authored pair. **Amended 2026-09-19 (IC-1b, R11):**
   the owner has authored these pairs already — `pvz` / `Plants vs. Zombies` → `Fusion` (display and
   prose only), Crazy Dave → *the Garden Keeper*, Penny → *Hourbloom*, Dr. Zomboss → *the Rotwright*.
   So no proposal is ever requested for those marks.
2. **An LLM proposal is a proposal.** Every generated suggestion is marked
   `proposed — needs owner confirm` and is **never** applied without a human decision.

**Success criteria**
- A finding whose mark has an authored replacement gets `source: "authored"` and the exact authored
  string.
- A finding whose mark has no authored replacement gets `source: "proposed"` with the literal marker
  `proposed — needs owner confirm`, produced by the LLM seam.
- A `code-identifier`-bucket finding gets **no** replacement and `source: "none"`. Renaming a code
  namespace is a code change, not a content edit; proposing a string there would invite a damaging
  edit (measured: `PVZRH` → `fusionRH` under a blind replace).
- Determinism: with the LLM seam stubbed, the same findings yield byte-identical suggestions. The LLM
  path is **not** part of the deterministic contract and is excluded from the reproducibility test.

## Tech Stack

Python 3.11+. Standard library for the authored-map path. The LLM path uses an **injected client
callable** — this module never imports a provider SDK directly, matching the repo's
"Core never reads a file; hosts load and inject" discipline (`tunables-ssot.md` §7.2) applied to a
tool. The default client is the local LM Studio endpoint that seedsmith already uses; see Open
Question 1 for the exact seam and whether to reuse seedsmith's client.

## Commands

```powershell
# Suggest for every finding (authored map + LLM for the remainder)
$env:PYTHONPATH = "gk-core/tools/ip-censor"; python -m ipcensor.report suggest --format json
# Authored-map only: no LLM call, fully deterministic. This is the CI-safe mode.
$env:PYTHONPATH = "gk-core/tools/ip-censor"; python -m ipcensor.report suggest --authored-only
$env:PYTHONPATH = "gk-core/tools/ip-censor"; python -m pytest gk-core/tools/ip-censor/tests/test_suggest.py -q
```

## Project Structure

```text
gk-core/tools/ip-censor/ipcensor/suggest.py  → this module: authored-map resolution + LLM seam
gk-core/tools/ip-censor/tests/test_suggest.py
gk-core/tools/ip-censor/tests/fixtures/replacements.v1.json
```

## Code Style

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Literal

PROPOSAL_MARKER = "proposed — needs owner confirm"   # structural literal: the exact marker contract


@dataclass(frozen=True, slots=True)
class Suggestion:
    mark: str
    replacement: str | None
    source: Literal["authored", "proposed", "none"]
    note: str | None                  # PROPOSAL_MARKER when source == "proposed"


SuggestFn = Callable[[Finding], str | None]


def suggest(
    findings: list[Finding],
    registry: Registry,
    propose: SuggestFn | None = None,
) -> list[Suggestion]:
    """Authored map first; `propose` for the remainder; identifiers get none.

    `propose=None` is the authored-only mode and is fully deterministic.
    """
```

Conventions: the marker is a module constant because it is a **contract string** a downstream execute
plan and a human both read; the LLM is a parameter, never a global; a `None` proposer is a valid,
tested mode.

## Testing Strategy

`pytest`, `gk-core/tools/ip-censor/tests/test_suggest.py` (new).

Levels:
- **Authored map wins** — a mark with an authored pair returns it with `source: "authored"` even when
  a stub proposer would return something different. The stub must not be called.
- **Proposal marking** — a mark without an authored pair, with a stub proposer, returns
  `source: "proposed"` and exactly `PROPOSAL_MARKER` in `note`.
- **Identifier refusal** — a `code-identifier`-bucket finding returns `source: "none"`,
  `replacement: None`, and the proposer is **not called**. Same refusal for a `code-change`
  remediation: `pvz.*` is in the ownership-prefix namespace, not a text token.
- **Remediation is respected (A3)** — a `generator-owned` finding may receive a proposal, but it is
  marked so the execute program routes it to the generator rather than to a JSON edit. The suggestion
  carries `remediation` through unchanged; `suggest` never downgrades it to a direct edit.
- **Determinism** — `propose=None` over a fixed finding list is byte-identical across runs.
- **Proposer failure is survivable** — a proposer that raises yields `source: "none"` with the error
  recorded, never a crash of the whole report.

## Boundaries

- **Always:** authored pair wins; mark every generated suggestion; refuse to suggest for identifiers
  and `code-change` remediations; keep `propose` injectable so the deterministic mode exists; record a
  proposer failure instead of aborting.
- **Ask first:** adding a new `source` value; changing the marker string (it is a contract a human and
  a future execute plan both parse).
- **Amended 2026-09-19 (owner ruling IC-3):** the release gate runs `scan` only and never reaches this
  module, so there is no gate invocation of the LLM path to decide.
- **Never:** apply a suggestion (this module proposes; the separate execute program applies); call the
  LLM from `scan`; log a model prompt that includes proprietary game text; let an LLM override an
  authored pair.

### One LLM client for the tool — amended 2026-09-19 (owner ruling IC-2)

IC-2 adds a second model use in this tool: the `curate` module asks the model to propose registry
**candidates** ([spec-curate.md](spec-curate.md)). Both uses take the same injected callable, built
once by `report` from the configuration below, in `gk-core/tools/ip-censor/ipcensor/llm.py` (new). `suggest`
proposes replacements; `curate` proposes candidates; neither owns the client, so the configuration has
one home and one reader.

## Configuration — where the endpoint, model and budget come from (audit A7)

This spec previously named an injected callable but no home for its settings, which invites invented
env keys or a hardcoded `localhost:1234`. The repo already has the exact surface, in
`gk-forge/tools/seedsmith/.env.example`:

| seedsmith key | ip-censor equivalent |
|---|---|
| `SEEDSMITH_LLM_ENDPOINT` (`http://localhost:1234/v1/chat/completions`) | `IPCENSOR_LLM_ENDPOINT` |
| `SEEDSMITH_LLM_MODEL` | `IPCENSOR_LLM_MODEL` |
| `SEEDSMITH_LLM_TIMEOUT` (420) | `IPCENSOR_LLM_TIMEOUT` |
| `SEEDSMITH_LLM_ATTEMPTS` (2) / `SEEDSMITH_LLM_RETRY_DELAY` (3) | same names, `IPCENSOR_` prefix |

Rules, mirroring how seedsmith treats the same surface:

- A committed `gk-core/tools/ip-censor/.env.example` documents every key; the real `.env` is **gitignored**
  (the root `.gitignore`'s bare `.env` pattern already covers it) so machine-specific endpoints never
  get committed.
- Precedence is seeded env → committed default → built-in default, never a silent hardcode.
- `--authored-only` **never reads any of these** and never needs a network; that is the CI-safe mode.

## Open Questions

1. **LLM seam** — reuse seedsmith's existing local-LLM client, or a thin new one? **Recommendation: a
   thin injected callable in this tool, not a seedsmith import.** Importing `gk-forge/tools/seedsmith` from
   `gk-core/tools/ip-censor` would couple two independently-versioned tools through an undeclared dependency,
   and the callable is ~20 lines. The *configuration key shape* above is deliberately copied so the two
   tools feel the same to an operator; the *code* is not shared. Owner to confirm.
2. **Proposal provenance** — should a proposal record which model produced it (`_meta.model`, as the
   generated-seed trees do)? Recommendation: **yes**, in the JSON plan only (never in seed data),
   because the execute program's reviewer needs to know what to re-check.
3. **Batching** — one LLM call per finding, or one call per distinct mark? Marks repeat heavily
   (`pvz` alone is 4,146 hits), so **per distinct mark** is the obvious economy. Confirmed as the
   default unless the owner wants per-context proposals.
