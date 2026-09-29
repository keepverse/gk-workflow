# Spec: `ip-censor` / `source` — tracked-tree reader

**Program:** `ip-censor` · **Module id:** `source` · **Depends on:** nothing (root)
**Capability map:** [../ip-censor-map.md](../ip-censor-map.md) · **Ideal:** [../ip-censor-ideal.md](../ip-censor-ideal.md)
**Status:** spec phase, 2026-09-19. No build authorized.

---

## Objective

Give every read-only verb (`census`, `scan`) one deterministic, byte-stable view of the repository as
**files with indexed lines**, so two runs over the same commit produce identical locations.

The module answers exactly one question: *"what are the scannable units of the tracked tree, and where
does line N of each begin?"* It holds **no policy** — no notion of a mark, a bucket, or a scope. A
scope bug and a reader bug must never be confusable, which is why they are separate modules.

**Success criteria**
- `iter_files()` yields the tracked tree in a **stable, sorted** order, filtered by an explicit
  extension allowlist and an explicit ignore list.
- Each file exposes its text decoded from UTF-8 (with an explicit documented fallback policy) and a
  line index such that a byte offset maps to `(line, column)` deterministically.
- The same commit yields identical `(path, line)` output across runs and across platforms.
- Binary files, lockfiles, and the registry's own files are never yielded.

## Tech Stack

Python 3.11+ (same floor as `gk-forge/tools/seedsmith/pyproject.toml`), standard library only for this module.
No third-party dependency is needed to list files and index lines. `pytest` for tests.

## Commands

```powershell
# From repo root
$env:PYTHONPATH = "gk-core/tools/ip-censor"; python -m pytest gk-core/tools/ip-censor/tests/test_source.py -q
# Single test
$env:PYTHONPATH = "gk-core/tools/ip-censor"; python -m pytest gk-core/tools/ip-censor/tests/test_source.py -q -k line_index
# The module has no CLI of its own; it is exercised through `report`'s entry point.
```

## Project Structure

```text
gk-core/tools/ip-censor/
  ipcensor/
    __init__.py
    source.py          → this module: file enumeration + line indexing
    registry.py        → module `registry`
    census.py          → module `census`
    scan.py            → module `scan`
    suggest.py         → module `suggest`
    report.py          → module `report` (composition root + CLI)
    cli.py             → argparse wiring, called by report
  tests/
    test_source.py
    fixtures/
  pyproject.toml       → declares the tool's deps; EXACT pins, never ranges
  requirements.lock    → the frozen set CI installs (spec-dependency-baseline.md §2.1)
```

**⚠️ Every path above is currently unmapped in `gk-core/scripts/verification-boundaries.v1.json`, and that is
a build blocker (audit finding A1).** `scripts/verify-change.ps1:118` **throws**
`"VERIFICATION BOUNDARY MISSING: <path>"` for a path with no owner boundary, and the registry's 101
boundaries cover **12 C# projects** with no Python lane. The mapping is owned by the amended `wiring`
module (see [spec-wiring.md](spec-wiring.md)). **Resolution, owner decision 2026-09-19:** `ip-censor`
is an independent Python tool like `gk-forge/tools/seedsmith` and gets a real **`pytest` verification project**,
not the `tuning-publish-tool` C#-lane precedent. That lane's runner kind is specified in the binding
[../test-verification-boundary/spec-python-test-lane.md](../test-verification-boundary/spec-python-test-lane.md)
(Wave 3, **unbuilt**), so `wiring` lands in two halves: the package + pinned deps + CI step now, the
`runner: "pytest"` boundary once that lane ships. Until half 2, this path still throws — do **not**
work around it by running the whole suite; `AGENTS.md` names an unmapped production path a
verification-boundary defect to fix or report, never a reason for a broad fallback.

## Code Style

```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

# Structural constant, not tunable: a byte-width/parse concern, not a balance number
# (tunables-ssot.md §1 "Structural"). Changing it breaks whether the reader works.
DEFAULT_ENCODING = "utf-8"


@dataclass(frozen=True, slots=True)
class SourceFile:
    """One scannable tracked file. `text` is decoded once; `line_starts` is built once."""
    path: str            # repository-relative, forward slashes
    text: str
    line_starts: tuple[int, ...]

    def locate(self, offset: int) -> tuple[int, int]:
        """Byte/char offset → (1-based line, 1-based column). Deterministic."""
        ...


def iter_files(root: Path, *, extensions: frozenset[str], ignore: tuple[str, ...]) -> Iterator[SourceFile]:
    ...
```

Conventions: `from __future__ import annotations`; `frozen=True, slots=True` dataclasses for value
types; pure functions that take their inputs (no module-level `Root`); repository-relative paths with
forward slashes everywhere; type hints on every public function.

## Testing Strategy

`pytest`, tests in `gk-core/tools/ip-censor/tests/`. No network, no database, no temp-store (the
`guard-test-substrate.py` concern applies to C# tests, but the discipline is the same). Use
`tmp_path` for synthetic trees.

Levels:
- **Unit** — enumeration filters (extension allowlist, ignore list, binary skip); `locate()` at
  boundary offsets (0, first line start, across `\n`, past EOF); encoding failure **throws** (A8).
- **Determinism** — the same fixture tree enumerated twice yields identical order and identical
  `(path, line)` for a known offset.
- **Real-tree smoke** — enumeration over this repo returns a non-empty set and **does not** include
  any `self_paths` file (self-exclusion is proven, not assumed — expanded by A2 to cover the program's
  own docs and the `tasks/ip-censor/**` plan home, not just the registry).
- **Encoding corpus (A8)** — a test that walks the real tree and asserts every yielded file decodes as
  UTF-8. Measured this session: **10,338 of 10,338 text-extension tracked files decode cleanly, zero
  exceptions**, so this is a true invariant today and the test is the tripwire if it ever changes.

## Boundaries

- **Always:** sort output deterministically; treat paths as repository-relative; strip CRLF
  consistently so `locate()` matches what a human sees in an editor; prove self-exclusion against the
  **full** `self_paths` set, not just the registry.
- **Ask first:** changing the extension allowlist in a way that adds or drops a whole language;
  adding a third-party dependency; adding a new ignore class.
- **Never:** read outside the repository root; follow symlinks out of the tree; **silently** decode a
  file it cannot decode (throw — see A8); embed any mark/scope knowledge in this module.

## Open Questions

1. **Binary detection policy** — extension denylist only, or a content sniff (NUL byte in the first
   8 KiB)? Extension-only is simpler and auditable; content sniff catches a binary with a text
   extension. This spec defaults to **extension allowlist** (an allowlist, not a denylist, so an
   unknown binary extension is skipped by construction) and asks the owner to confirm.
2. **CRLF handling** — this repo checks out CRLF on Windows (`DungeonLootTableSeedFileTests` records
   the artifact). Does `locate()` count columns before or after CRLF normalization? Default: count on
   the normalized text, and state that a report line number is editor-equivalent.

## Resolved by measurement (audit A8)

- **Encoding fallback: none. Throw.** All 10,338 text-extension tracked files are valid UTF-8 today,
  so a decode failure means a genuinely new file class arrived. A silent replacement decode is a
  correctness hazard in a scanner specifically — a mangled byte changes whether a token matched, which
  would make a finding disappear without a trace. The earlier "documented fallback policy" wording is
  withdrawn.

