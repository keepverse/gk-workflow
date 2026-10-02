# Spec: `ip-censor` / `report` — the plan output, and the CLI

**Program:** `ip-censor` · **Module id:** `report` · **Depends on:** `scan`, `suggest`, `census`
**Capability map:** [../ip-censor-map.md](../ip-censor-map.md) · **Ideal:** [../ip-censor-ideal.md](../ip-censor-ideal.md)
**Status:** spec phase, 2026-09-19. No build authorized. **Amended 2026-09-19 (owner rulings IC-1,
IC-1b, IC-3, IC-4).**

---

## Objective

Compose the tool's three readings into the deliverable the owner specified — *"list files and token
need to change, suggest new censor token"* — in two forms:

1. **A machine-readable plan (JSON)** that the **separate execute program** consumes. This is the
   integration contract of the whole program, and it is the reason `report` is a module rather than a
   print statement.
2. **A human-readable Markdown report** the owner reads.

`report` is also the **composition root**: it owns the CLI, reads the registry file, builds the
`source` view, and calls `census`, `scan`, and `suggest`. Nothing else in the program does I/O policy.

**Success criteria**
- `report scan --format json` emits every finding with `path`, `line`, `column`, `matched`, `mark`,
  `bucket`, `surface`, **`remediation`**, and (after `suggest`) `replacement`, `source`, `note`.
- The plan carries a **schema version** and the tool's own provenance so a future execute program can
  detect an incompatible shape.
- The plan is **grouped by file** — the owner asked for *"list files and location"*, so a file is a
  first-class key, not something a consumer must re-derive. It is also **groupable by `remediation`**,
  because that is the axis an execute program routes on (A3): `authored` edits directly,
  `generator-owned` goes to the generator, `upstream-imported` needs a filter, `code-change` is a
  different program.
- The Markdown report summarizes by file, by mark, and by remediation, and **never prints a total as
  a guarantee** (a count is a reading of a population — `validation-ssot.md`).
- The CLI exits non-zero only when explicitly asked (`--fail-on enforced`). **Amended 2026-09-19
  (owner ruling IC-3):** that flag is the **release gate's** invocation and nothing else's. The
  default (exit 0 with findings) is what the advisory CI step and every ad hoc run use; no commit,
  `verify-change.py` run or CI job fails on findings.
- **`--authored-only` requires no network.** The release gate calls `scan` only, which never reaches
  `suggest`, so the gate needs no model and no network by construction. *Erratum 2026-09-23 (ip-censor
  T12):* the gate's command line did not carry the flag, and `scan` does build the LLM proposer unless
  it is passed — `gk-core/tools/ip-censor/ipcensor/cli.py:154-160` calls `_proposer()` whenever `--authored-only` is absent, and
  `suggest` asks it once per mark with no authored replacement pair. On any machine where the
  `IPCENSOR_LLM_*` endpoint answers, that blocks the gate for one model round-trip per such mark; the
  flag is now part of the gate's command in `release.yml` and in the checklist line.

## Tech Stack

Python 3.11+, standard library (`json`, `argparse`, `datetime`). No CLI framework. The only third-party
imports in the program live in `scan` (`pyahocorasick`) and `suggest`'s optional HTTP call — both
**exact-pinned** in `pyproject.toml` + `requirements.lock` (A5).

## Commands

```powershell
# Everything at once: census + scan + suggest, both formats
$env:PYTHONPATH = "gk-core/tools/ip-censor"; python -m ipcensor.report all --plan tasks/ip-censor/plan.json --report tasks/ip-censor/report.md
# The release gate (IC-3) — the only blocking invocation
$env:PYTHONPATH = "gk-core/tools/ip-censor"; python -m ipcensor.report scan --format json --fail-on enforced --authored-only
# Registry sanity, no tree scan
$env:PYTHONPATH = "gk-core/tools/ip-censor"; python -m ipcensor.report registry-check
$env:PYTHONPATH = "gk-core/tools/ip-censor"; python -m pytest gk-core/tools/ip-censor/tests/test_report.py -q
```

**Verified by the `wiring` module (A1):** `.\scripts\verify-change.py -Paths gk-core/tools/ip-censor/ipcensor/report.py -Session <id>`
must return a **plan naming the `ipcensor` pytest lane** — not the `VERIFICATION BOUNDARY MISSING`
throw that `gk-core/scripts/verify-change.py:771` currently produces for every path this program proposes. The lane's
runner kind is owned by `test-verification-boundary/python-test-lane` (Wave 3, unbuilt); see
[spec-wiring.md](spec-wiring.md) for the two-half landing.

## Project Structure

```text
gk-core/tools/ip-censor/
  ipcensor/report.py      → this module: composition root + plan/report writers
  ipcensor/cli.py         → argparse surface (called by report)
  tests/test_report.py
  gk-core/tests/fixtures/
tasks/ip-censor/          → generated plan + report (evidence, not authority; regenerable)
```

`tasks/ip-censor/` follows the repo's `tasks/` evidence convention. The plan is **regenerated**, never
hand-edited: it is output, so editing it by hand is the same defect class as hand-editing generated
seed data. **It is also self-excluded from scanning by construction** (A2) — a committed plan contains
every finding, so without that rule the next scan would flag the previous one, growing every run.


## Code Style

```python
from __future__ import annotations

import json
from dataclasses import asdict, dataclass

# Contract constant: a consumer (future execute program) pins this and refuses an unknown value.
PLAN_SCHEMA_VERSION = 1


@dataclass(frozen=True, slots=True)
class Plan:
    schema_version: int
    generated_from_commit: str          # so a stale plan is detectable
    registry_version: str
    model: str | None                   # proposal provenance, null in --authored-only
    files: dict[str, list[Finding]]     # grouped by file, the owner's requested shape


def write_plan(plan: Plan, path: Path) -> None:
    """Deterministic JSON: sorted keys, LF, trailing newline. Byte-stable for the same commit."""
```

Conventions: `PLAN_SCHEMA_VERSION` is a structural constant with a reason comment
(`tunables-ssot.md` T2); output writers are pure functions of their inputs; **no clock value enters
the JSON** except an explicit, documented `generated_at` the determinism test excludes.

## Testing Strategy

`pytest`, `gk-core/tools/ip-censor/tests/test_report.py` (new).

Levels:
- **Plan shape** — a fixture tree yields a plan whose `schema_version` equals `PLAN_SCHEMA_VERSION`,
  whose `files` keys are every path with a finding, and whose entries carry all required fields
  **including `remediation`**.
- **Byte-stability** — writing the same plan twice yields identical bytes (excluding `generated_at`).
- **Grouping** — a file with three findings appears once as a key with three entries; a `--by
  remediation` view groups the same findings without losing any (A3).
- **Exit codes** — `scan` returns 0 by default with findings present; returns non-zero with
  `--fail-on enforced` and an enforced finding (`player-name`, `player-prose` or `generator-prompt` —
  IC-3); returns 0 with `--fail-on enforced` when the only findings are `docs-prose-citation`,
  `deliberate-identity` or `code-identifier` (the A4 split and IC-1b, proven rather than asserted).
- **No network in `--authored-only`** — the test monkeypatches the proposer to raise if called and
  asserts the run succeeds.
- **Self-exclusion of the output (A2)** — a plan written to `tasks/ip-censor/` is not a finding source
  on the next scan; the derived class-4 rule is exercised, not just described.
- **Population discipline** — no assertion on the real tree's finding count.

## Boundaries

- **Always:** version the plan; record the commit it was generated from; group by file (and be
  groupable by remediation); keep `--authored-only` network-free; exit 0 by default; keep the plan
  regenerable and self-excluded.
- **Ask first:** changing `PLAN_SCHEMA_VERSION`; making a non-zero exit the default; writing a plan
  anywhere outside `tasks/ip-censor/`.
- **Never:** write to any path under `src/`, `data/`, `web/`, or `gk-core/tools/ip-censor/` itself (this
  module produces plans, the execute program mutates) — with one exception, **amended 2026-09-19
  (owner ruling IC-2):** `curate admit` writes `gk-data/packs/fusion/data/seed/ip-censor/_registry/marks.v1.json`, and only
  from a candidate file a person has decided ([spec-curate.md](spec-curate.md)); edit a plan by hand; assert a count as truth;
  print a model name into a file the owner did not ask for; wire `--fail-on enforced` into a
  per-commit guard (a `guard-ip-vocabulary.ps1`), `verify-change.py` or a blocking CI step —
  **amended 2026-09-19 (owner ruling IC-3):** the release is the only thing the scan blocks.

## Boundaries — where this program stops

Restated because it is the most likely thing a downstream session gets wrong: **the execute change is
a separate program.** The plan's job is to make each route **legible** — `remediation` says which
applies to each finding — not to walk it. **Amended 2026-09-19 (owner rulings IC-1b, IC-4, R9, R12):**

| Execute-phase work the plan must express | Who does it | `remediation` |
|---|---|---|
| Display and prose `PvZ` / `Plants vs. Zombies` → `Fusion` on player-facing surfaces (IC-1b) | the identity-rename program (R9, R12) | `authored` (or `generator-owned` where the row carries provenance) |
| The lead names on existing surfaces → R11 names. Measured: the commander display name is already data, `gk-data/packs/fusion/data/seed/commanders/_registry/default-commanders.v1.json:15` (`"displayName": "Dr. Zomboss"`), read by `DataCommanderDirectory` (`gk-core/src/FusionRpg.Core/Commanders/DataCommanderDirectory.cs:23`); `PlayerEmpireCommanders.cs` no longer holds a display-name switch | the identity-rename program | `authored` |
| `Overwatch Protocol` (IC-4) | `avoid-list` adoption in the tree generator, then regenerate — [spec-avoid-list.md](spec-avoid-list.md) | `generator-owned` |
| The `Jackson*` species family (IC-4) | an authored import-time rename map, applied where the upstream almanac is imported — see the map's *Release-blocking fixes*. *Audit 2026-09-19:* owned by this program's plan (T17–T20), and the species ids are re-keyed too (gate G1 answered yes, T19b, a backed-up idempotent save migration) | `upstream-imported` (names); `code-change` (ids) |

The earlier text here named "de-hardcoding `PlayerEmpireCommanders.cs:14-15`" as execute work. Verified
2026-09-19: that switch is gone (`PlayerEmpireCommanders.ForPlayer` now takes an `ICommanderDirectory`);
the remaining work is the data row above.

## Open Questions

1. **Where does the plan live?** `tasks/ip-censor/` (evidence, regenerable) vs `dist/` (build output).
   Recommendation: **`tasks/ip-censor/`**, because the plan is reviewed evidence an execute program
   consumes, and `dist/` is never committed. Note `tasks/**` already carries **247** IP marks across
   393 files, so this directory is a `self_paths` member either way (A2).
2. ~~Does the plan include `deliberate-identity` and `docs-prose-citation` findings?~~ Settled by the
   owner's *"include docs as normal findings"* together with **IC-1** (citations out of scope, so
   never enforced): the plan includes them with their report-only bucket; the consumer filters. Kept
   as a trail.
3. ~~Gate wiring~~ — answered by **IC-3**: a release gate, with an advisory CI step; no per-commit
   guard. Hook points in [spec-wiring.md](spec-wiring.md). Kept as a trail.
