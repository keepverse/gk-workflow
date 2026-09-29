# Spec: `ip-censor` / `scan` — match, bucket, report findings

**Program:** `ip-censor` · **Module id:** `scan` · **Depends on:** `source`, `registry`
**Capability map:** [../ip-censor-map.md](../ip-censor-map.md) · **Ideal:** [../ip-censor-ideal.md](../ip-censor-ideal.md)
**Status:** spec phase, 2026-09-19. No build authorized. **Amended 2026-09-19 (owner rulings IC-1,
IC-1b, IC-3, IC-4; narrative rulings R8–R12).**

---

## Objective

Match every registry alias group against the tree and **classify each hit** — this is the detection
half of the tool the owner asked for, and the surface the **release gate** enforces (owner ruling IC-3).

The module's whole value is in one distinction the ideal calls the real design problem: **the same
word means different things in different places.** `pvz` is the product premise, EA's mark, and a code
namespace. `Overwatch` in `docs/research/**` is an attributed citation; in
`gk-data/packs/fusion/data/seed/passive-tree/nodes/command.json:538` it is a shipped player-facing name. A scanner that
cannot tell those apart produces the thousands-of-false-positives failure that gets a tool disabled.

`scan` produces **findings**, never edits. It has no write path at all.

### Where `scan` runs — amended 2026-09-19 (owner ruling IC-3)

**`scan` is a release gate, and only a release gate.** It runs before any release and a finding in an
enforced bucket blocks the release. It does **not** run inside generation and does **not** block a
commit, a `verify-change.ps1` run or CI: the owner ruled that *"block generation will cost more than
help."* CI may run it **advisory** (report uploaded, exit 0). Generation-time prevention is the free
avoid-list in briefs ([spec-avoid-list.md](spec-avoid-list.md)), which calls no model and retries
nothing. The hook points are owned by [spec-wiring.md](spec-wiring.md).

**The enforced set** (authored in `scope-policy.v1.json`, IC-3): `player-name`, `player-prose`,
`generator-prompt`. Every other bucket is report-only. `generator-prompt` is enforced because a brief
must never cite another franchise by name (ideal, Narrative generation row 6); the measured example is
`gk-forge/tools/seedsmith/seedsmith/adapters/items/uniques/briefs.py:267` ("a Diablo-style unique item"), which
the first release scan will report.

**Success criteria**
- Every alias group is matched case-folded, **longest-match-first**, with the `registry` boundary
  policy — never bare `\b`.
- Each hit is bucketed into exactly one of: `player-name`, `player-prose`, `generator-prompt`,
  `code-identifier`, `docs-prose-citation`, `deliberate-identity`, `registry-self`. **Amended
  2026-09-19 (IC-1b, R8–R12):** `player-prose` is new (narrative lines, choice labels, the player
  guide); `deliberate-identity` now means only an in-scope PvZ or lead-name hit on a
  **non-player-facing** surface (architecture docs, `tasks/**`, code comments) — on a player-facing
  surface the same hit is `player-name` / `player-prose` and enforced.
- A hit on a path that does not exist in the allowlisted extension set is impossible by construction
  (`source` filtered it).
- Findings are ordered deterministically by `(path, line, column, mark)`.
- The scanner reports **zero** findings in the registry's own `self_paths`.
- Performance: full-tree scan completes in **seconds**, not minutes. Measured ceiling from the ideal:
  `pyahocorasick` + boundary filter = **2,046 ms** over 195.6 MB; a `re` alternation is 17,038 ms and
  is the rejected fallback.

## Tech Stack

Python 3.11+. `pyahocorasick` (installed; Aho-Corasick gives `Θ(text + matches)`, and is the standard
prefilter — this is the "buy, don't hand-roll the trie" decision from the ideal). `regex` (installed,
2026.3.32) if UAX#29 boundaries are wanted in the classifier; otherwise a ~20-line explicit separator
function over the automaton's hits, because `regex`'s `(?V1)\b` **also** fails on `PvZ融合版` (measured
— it is not a fix for trap (c)).

## Commands

```powershell
# Findings for the whole tree (ad hoc, and the advisory CI step)
$env:PYTHONPATH = "gk-core/tools/ip-censor"; python -m ipcensor.report scan --format json
$env:PYTHONPATH = "gk-core/tools/ip-censor"; python -m ipcensor.report scan --tree data --bucket player-name
# The release gate (IC-3): non-zero exit when a finding lands in an enforced bucket
$env:PYTHONPATH = "gk-core/tools/ip-censor"; python -m ipcensor.report scan --fail-on enforced
$env:PYTHONPATH = "gk-core/tools/ip-censor"; python -m pytest gk-core/tools/ip-censor/tests/test_scan.py -q
```

## Project Structure

```text
gk-core/tools/ip-censor/ipcensor/scan.py     → this module
gk-core/tools/ip-censor/tests/test_scan.py
gk-core/tools/ip-censor/tests/fixtures/      → trees containing each bucket's canonical example
```

## Code Style

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Bucket = Literal[
    "player-name", "player-prose", "generator-prompt", "code-identifier",
    "docs-prose-citation", "deliberate-identity", "registry-self",
]


@dataclass(frozen=True, slots=True)
class Finding:
    path: str
    line: int                 # 1-based
    column: int               # 1-based
    matched: str              # the exact text as it appears
    mark: str                 # canonical mark from the registry
    bucket: Bucket
    surface: Surface          # from the shared classifier (registry module)
    remediation: Remediation  # HOW it may be fixed (A3); carried, never recomputed by a consumer


def scan(files: Iterable[SourceFile], registry: Registry) -> list[Finding]:
    """Every registry hit, bucketed and ordered. Read-only; no write path exists in this module."""
```

Conventions: a `Finding` is a value; the automaton is built once from the registry and passed in; the
boundary check is a named function so it is unit-testable in isolation; `remediation` is carried
through from the registry so no downstream consumer has to re-derive it from a path.

## Testing Strategy

`pytest`, `gk-core/tools/ip-censor/tests/test_scan.py` (new).

Levels:
- **Boundary regression (the measured failures)** — fixture cases that must behave exactly:
  | Text | Expected | Why |
  |---|---|---|
  | `PvZ Fusion` | hit | the target |
  | `PVZRH` | no hit | identifier compound |
  | `PvZ2 strategies` | no hit | a different EA game |
  | `pvz-fusion-almanac-3.6.1` | hit (path-prose) | `-`/`.` are declared separators |
  | `drop.pvz.run` | no hit as prose; `code-identifier` if in a code path | namespace |
  | `PvZ融合版` | hit | script-change boundary |
  | `demonstrate` | no hit for `demon` | substring guard |
- **Bucket** — one canonical example per bucket, asserted to land in that bucket and no other.
- **Self-exclusion** — the shipped registry produces zero findings inside **all three** `self_paths`
  classes (A2): the registry files, this program's own docs
  (`docs/architecture/ip-censor/**`, `ip-censor-map.md`, `ip-censor-ideal.md` — measured to contain
  **110** marks between them (ideal 69 + the seven specs 31 + map 10)), and `tasks/ip-censor/**`.
- **Deliberate identity — amended 2026-09-19 (IC-1b, R9).** A PvZ hit in an architecture doc
  (`docs/architecture/software-architecture.md`) is bucketed `deliberate-identity`, report-only. The
  player guide (`docs/guide/the-game.md`) is **no longer** the example: R9 renames it, so a `PvZ` or
  `Crazy Dave` hit there is `player-prose` and enforced. A `pvz.*` or `drop.pvz.run` hit in a code path
  is `code-identifier` and never enforced.
- **Narrative surfaces (R8–R12)** — a fixture `gk-data/packs/fusion/data/seed/narrative/_registry/names.en.v1.json`
  carrying `"Crazy Dave"` is `player-name`, enforced; a fixture storylet choice label carrying
  `Dr. Zomboss` is `player-prose`, enforced; the same fixture carrying `{lead_antagonist}` yields no
  finding.
- **Generator prompt** — a fixture brief string naming `Diablo` as a style reference is
  `generator-prompt`, enforced.
- **Known-collision acceptance (A9)** — the strongest free acceptance test in the program: the tool
  must find `"Overwatch Protocol"` at `gk-data/packs/fusion/data/seed/passive-tree/nodes/command.json:538` and report it as
  `bucket: "player-name"`, `remediation: "generator-owned"` (the file carries
  `"promptVersion": "tree-language/3"` at `:542`). This is a real shipped collision, so a suite that
  cannot find it is not working — and it exercises bucket, remediation and boundary in one case.
  **It asserts the finding's shape and location, never a total count** (population discipline).
  **Amended 2026-09-19 (IC-4):** the owner ruled this row fixed before release, so it will leave the
  real tree. The test therefore reads a **fixture copy** of the pre-fix node row, provenance fields
  included, under `gk-core/tests/fixtures/`; it must not depend on the live file still being wrong.
- **Determinism** — two runs are byte-identical.
- **Population discipline** — no test asserts a total finding count for the real tree.

## Boundaries

- **Always:** longest-match-first; apply the declared boundary policy; bucket every hit exactly once;
  carry `remediation` through; exclude all `self_paths`; remain read-only.
- **Ask first:** adding a new `Bucket` value (closed vocabulary); changing the enforced set the owner
  ruled (IC-3); adding a fuzzy/phonetic match mode.
- **Never:** edit, write, or `git mv` anything (that is the separate execute program); use bare `\b`;
  use `.lower()` for folding; auto-rename a fuzzy hit; report a count as a contract; run inside a
  generator's retry loop or block a commit, `verify-change.ps1` or CI on findings (IC-3 — the release
  is the only thing `scan` blocks).

## Mixed code files — audit 2026-09-19

*Audit 2026-09-19 (HIGH, cross-plan).* The bucket follows the path's surface, and a code file can hold
both a kept identifier (`WorldFactionKind.Zomboss`, `EmpireId.Dave`, `commander:dave`) and a player
literal the identity-rename program renames (`gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.cs:78,83`).
Source-code roots therefore bucket as `code-identifier` (report-only); player literals inside code are
proven by identity-rename's own `check` and web vocabulary guard. A fixture holding every
identity-rename allow-list form must yield no enforced finding (`tasks/ip-censor-todo.md` T4). The
`Zomboss` alias with `.` as a separator would otherwise hit `WorldFactionKind.Zomboss` and keep the
release gate red with no owner.

## The `docs/` scope decision (audit A4) — amended 2026-09-19 (owner ruling IC-1)

The owner answered *"include docs as normal findings."* The ideal measured that `docs/` holds
**~3,400** hits, overwhelmingly **attributed prior-art citations with sources** (Diablo 486, Warcraft
167, Pokémon 164, Arknights 127, Genshin 96 — §6.4), and concluded that flagging those
*"produces the thousands-of-false-positives failure … and the tool gets disabled."*

Those are both true, and they only conflict if "finding" is conflated with "enforced." **IC-1 settles
it:** attributed research citations are out of IP scope. The resolution is therefore no longer a
proposal awaiting confirmation:

- **Citations are findings in the plan.** The reading stays complete and auditable, exactly as asked.
- **Citations are never `enforced`.** `docs-prose-citation` is a report-only bucket, so a future
  `--fail-on enforced` (the release gate) is quiet on ~3,400 legitimate references while the plan
  still lists them.

This preserves the owner's instruction and the ideal's finding simultaneously. The alternative
(exclude `docs/` from the plan) contradicts the owner's answer; the other alternative (enforce
citations) is the outcome the ideal measured as tool death.

## Open Questions

1. **Boundary policy exactness** (map Open Question 2). The separator set and the script-change rule
   are authored in `registry`; this spec requires `scan` to *consume* them and requires a test per
   measured case. The remaining question is the exact separator tuple — default proposal:
   `(" ", "\t", "\n", "-", ".", "/", "\\", "_", ":", ";", ",", "(", ")", "[", "]", "\"", "'", "`")`.
   The owner should confirm `_`, since `Enslave_Demon` was a protected case in the demon rename.
2. **Fuzzy/phonetic mode** — the ideal's §2 says knockout must stay high-precision and fuzzy is a
   human review queue. This spec therefore **omits** fuzzy matching. Adding it later is a scoped
   extension, not a config flag, because it changes the finding shape (candidate similarity + score).
3. ~~The `docs/` enforcement split~~ — answered by **IC-1** (citations out of scope); kept as a trail.
4. ~~Promoting a bucket to enforced~~ (was a Boundaries "ask first") — answered by **IC-3**: the enforced
   set is `player-name`, `player-prose`, `generator-prompt`, at release only.
