# Spec: `ip-censor` / `avoid-list` — the shared seedsmith brief helper

**Program:** `ip-censor` · **Module id:** `avoid-list` · **Depends on:** `registry` (its data file, not its code)
**Capability map:** [../ip-censor-map.md](../ip-censor-map.md) · **Ideal:** [../ip-censor-ideal.md](../ip-censor-ideal.md)
**Status:** spec phase, 2026-09-19. No build authorized. **Added 2026-09-19 (owner rulings IC-3, IC-4;
narrative rulings R8–R12)** — this module exists because of those rulings.

---

## Objective

Keep third-party names out of generated content **at the prompt, for free**. The owner ruled
(IC-3) that the scan is a release gate and must **not** block generation — *"block generation will
cost more than help."* What generation keeps is an avoid-list written into every brief that produces
player-facing text, rendered from the registry by **one** seedsmith helper. It adds no model call, no
retry and no answer-side refusal.

Why one helper and not one list per adapter: prevention today is per adapter
(`gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/grid.py:32` keeps its own `BANNED_WORD`). Per-adapter
lists drift; one registry read through one helper cannot.

The module also owns the **prompt-hygiene rule** from the ideal's Narrative generation section, row 6:
a brief never cites another game or franchise by name as a style reference. Style comes from the
program's own exemplars and anchor lines.

**Success criteria**
- One function renders the avoid-list from `gk-data/packs/fusion/data/seed/ip-censor/_registry/marks.v1.json`: every alias
  of every group whose scope includes `player-name` or `player-prose`, case-folded for uniqueness,
  sorted, deterministic.
- Every seedsmith adapter whose output reaches a player-facing surface puts that line in its brief.
  First adopters: the passive-tree node generator (required by IC-4) and the item uniques brief.
  Narrative adapters adopt it when they are built.
- No adapter adds an answer-side IP check, a retry or a refusal on the strength of this list (IC-3).
- No brief names another franchise as a style reference. Measured today:
  `gk-forge/tools/seedsmith/seedsmith/adapters/items/uniques/briefs.py:267` (*"a Diablo-style unique item"*).
- **IC-4, `Overwatch Protocol`, is fixed through this module:** the tree generator adopts the helper,
  and the one affected node is regenerated. See *The IC-4 fix* below.

## Tech Stack

Python 3.11+, inside `gk-forge/tools/seedsmith` (its package, its lockfile, its CI step at
`gk-core/.github/workflows/ci.yml:536-545`). Standard library only (`json`). **No import of `ipcensor`:** the two
tools share no code (`spec-wiring.md` §Tool shape). The helper reads the registry's **data file** by its
versioned contract; `ipcensor`'s `registry` module stays the validating authority, and the helper throws
on any shape it cannot read rather than guessing.

## Commands

```powershell
$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/test_briefkit_avoid_list.py -q
# The real registry renders
$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -c "from seedsmith.briefkit.avoid_list import load_avoid_terms; print(len(load_avoid_terms()))"
```

## Project Structure

```text
gk-forge/tools/seedsmith/seedsmith/briefkit/avoid_list.py      → this module (new)
gk-forge/tools/seedsmith/tests/test_briefkit_avoid_list.py     → its tests (new)
gk-forge/tools/seedsmith/seedsmith/adapters/trees/nodegen/brief.py   → first adopter (IC-4)
gk-forge/tools/seedsmith/seedsmith/adapters/items/uniques/briefs.py  → adopter; loses the franchise citation
```

**Why `briefkit`.** It is seedsmith's shared brief package, and its rule is that *every closed
vocabulary a brief depends on is written into the brief literally, read from the registry at generation
time* (`gk-forge/tools/seedsmith/seedsmith/briefkit/__init__.py:1-6`). An avoid-list is exactly that. Because a
briefkit brief is content-addressed, a registry change changes the brief hash, so provenance shows which
briefs saw which registry version.

**The existing seam in the tree generator.** `render_brief` (`adapters/trees/nodegen/brief.py:114`)
already prints `Avoid entirely: <anti-motifs>` (`:157`). The IP line is a **separate** line, so a motif
the tree should avoid and a name the game must never use keep distinct meanings.

## Code Style

```python
from __future__ import annotations

from pathlib import Path

#: The two surfaces whose text a generator produces (registry `Surface` values). A group scoped to
#: neither (e.g. a code-identifier-only concern) never reaches a brief.
PLAYER_SURFACES = frozenset({"player-name", "player-prose"})


def load_avoid_terms(registry_file: Path | None = None) -> tuple[str, ...]:
    """Every in-scope alias spelling, case-folded unique, sorted. Throws naming the key on a shape it
    cannot read; never defaults."""


def render_avoid_line(terms: tuple[str, ...]) -> str:
    """The one brief line. Empty tuple -> empty string, so an adapter never prints an empty list."""
```

## Testing Strategy

`pytest`, `gk-forge/tools/seedsmith/tests/test_briefkit_avoid_list.py` (new).

- **Contract** — a fixture registry with one group scoped to `player-name`, one to `code-identifier`
  only, and one short alias with its own scope yields exactly the in-scope spellings; the
  `code-identifier`-only group is absent.
- **Determinism** — two renders are byte-identical; order does not depend on file order.
- **Refusal** — a registry missing `groups`, or a group missing `scope`, throws naming the key.
- **Adoption** — the tree node brief and the uniques brief, rendered from a fixture registry, contain
  the avoid line; neither brief contains a registry `franchise-mark` spelling outside that line (this
  is the prompt-hygiene check, over the brief text, not the corpus).
- **Fixtures use invented marks** (for example `Examplemark`), never a real one: `gk-forge/tools/seedsmith/**`
  is a `generator-prompt` surface, which the release gate enforces.
- **No count is pinned** for the real registry (`validation-ssot.md`): the registry is a closed
  vocabulary a person edits, but the helper's tests use fixtures, so a new registry row never turns
  them red.

## The IC-4 fix — `Overwatch Protocol` (owner ruling IC-4)

The owner ruled the live finding fixed before release. The row is generator output
(`gk-data/packs/fusion/data/seed/passive-tree/nodes/command.json:538`, `"promptVersion": "tree-language/3"` at `:542`), so the
only sanctioned route is **generator change, then regenerate** — never a JSON edit.

| Step | Done when |
|---|---|
| 1. Registry row `overwatch` (`franchise-mark`; scope `player-name`, `player-prose`, `generator-prompt`), admitted with its stage record | `registry-check` passes |
| 2. The tree node brief adopts `render_avoid_line`, and `PROMPT_VERSION` (`adapters/trees/nodegen/brief.py:57`) moves past `tree-language/3` | the adoption test passes; new rows carry the new version |
| 3. Node `skill.command-def-t8-n0` is regenerated through the tree generator's own run, using its ledger's explicit supersede path (`adapters/trees/nodegen/run.py:462`, `record_superseded`), and `command.json` is committed with the new row | the row carries the new `promptVersion`; its `nameKey` is re-derived by the generator (`gk-forge/tools/seedsmith/seedsmith/adapters/trees/nodegen/run.py:655`), not by hand |
| 4. The release scan reports no `overwatch` finding in `gk-data/packs/fusion/data/seed/passive-tree/**` | the release gate is green for that mark |

*Audit 2026-09-19:* step 3 needs a generator change this table did not name. `trees generate --write
--supersede` re-rolls **every** ledger row whose `promptVersion` differs from the current one
(`gk-forge/tools/seedsmith/seedsmith/report/cli.py:3039-3045`), so a prompt-version bump plus `--supersede` would
regenerate the whole `command` tree. The plan's T16 adds a `--node <id>` selector so only
`skill.command-def-t8-n0` regenerates (`tasks/ip-censor-plan.md` D6).

Step 4 is the release gate's outcome, not a suite assertion: a test never pins "zero hits" on the real
tree (ideal, principle 3).

## Boundaries

- **Always:** render from the registry file; keep the IP line separate from motif lines; keep the helper
  free of model calls; bump an adopter's prompt version when its brief changes.
- **Ask first:** adding an answer-side check to any adapter (it reverses IC-3); widening the list beyond
  player-facing scopes.
- **Never:** import `ipcensor`; keep a per-adapter IP list; hand-edit a generated row to remove a mark;
  cite another franchise in a brief.

## Open Questions

None.
