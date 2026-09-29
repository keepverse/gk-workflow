# Spec: `ip-censor` / `registry` — alias groups, scope policy, boundary policy, replacements

**Program:** `ip-censor` · **Module id:** `registry` · **Depends on:** nothing (root)
**Capability map:** [../ip-censor-map.md](../ip-censor-map.md) · **Ideal:** [../ip-censor-ideal.md](../ip-censor-ideal.md)
**Status:** spec phase, 2026-09-19. No build authorized. **Amended 2026-09-19 (owner rulings IC-1,
IC-1b, IC-2, IC-5, IC-6; narrative rulings R8–R12)** — see [the ideal's rulings table](../ip-censor-ideal.md).

---

## Objective

Hold **every authored decision** the scanner needs, so that no mark, spelling, scope, boundary rule,
or replacement lives in code. This module is the program's entire judgement surface; `scan` and
`suggest` only apply what this module states.

Four authored artifacts:

1. **Alias groups** — one canonical mark + its spellings + category + scope + **admission record**
   (which curation stage admitted the row — IC-2).
2. **Scope policy** — which category is enforced on which surface, and which are reported-only.
3. **Boundary policy** — which characters separate a token, and how a script change (Han↔Latin) is
   recognized.
4. **Replacement map** — authored `mark → replacement` pairs. The pairs the owner has already
   authored: `pvz` / `Plants vs. Zombies` → `Fusion` in display and prose (IC-1b), and the three leads
   (R11): Crazy Dave → *the Garden Keeper*, Penny → *Hourbloom*, Dr. Zomboss → *the Rotwright*.

**Success criteria**
- A missing or mistyped field **throws naming the key**; nothing is defaulted
  (`tunables-ssot.md` T5: *"a missing tunable is a load rejection naming it, never a built-in
  default"*).
- The registry's own files are excluded from its own patterns (self-exclusion is a parser invariant).
- A duplicate canonical mark, or the same spelling under two groups, is a **load rejection**.
- **Amended 2026-09-19 (owner ruling IC-6).** An alias shorter than **4 characters** is a load
  rejection unless the alias itself declares a narrow scope: its own `scope`, non-empty and a subset
  of its group's scope. A group-level scope inherited by a short alias does **not** satisfy the rule.
  (Measured: bare `wow` produced 142 prose hits, `pop` 221, `ea` 67.) The value 4 lives in
  `boundary-policy.v1.json` as `minAliasLength`, not in code.
- **Amended 2026-09-19 (owner ruling IC-2).** Every alias group carries an `admission` record naming
  the stage that admitted it (`import` or `reconfirm`), its evidence, its source and the person who
  confirmed it. A group without one, or with a stage/evidence pair the table below forbids, is a load
  rejection.
- The registry's member list is a **closed vocabulary** and may be asserted; the **hit population**
  it produces may never be asserted as a count (`validation-ssot.md`).

## Tech Stack

Python 3.11+, standard library only (`json`, `re`, `unicodedata`). No third-party dependency: this
module parses authored JSON and compiles patterns; the matching library belongs to `scan`.

## Commands

```powershell
$env:PYTHONPATH = "gk-core/tools/ip-censor"; python -m pytest gk-core/tools/ip-censor/tests/test_registry.py -q
# A real registry load, proving the shipped file parses and self-excludes
$env:PYTHONPATH = "gk-core/tools/ip-censor"; python -m ipcensor.report registry-check
```

## Project Structure

```text
gk-data/packs/fusion/data/seed/ip-censor/
  _registry/
    marks.v1.json                        → alias groups + category + scope + remediation
    scope-policy.v1.json                 → category × surface enforcement + self_paths
    boundary-policy.v1.json              → separator set, script-change rule, min alias length
    replacements.v1.json                 → authored mark → replacement pairs
    import-filter.v1.json                → IC-2: the dataset curation filter, owned by `curate` (spec-curate.md)
gk-core/tools/ip-censor/ipcensor/registry.py     → the pure parser for the four registry files
```

**Why `gk-data/packs/fusion/data/seed/…/_registry/` and not `gk-core/data/tuning/`:** the registry is a **closed identity
vocabulary a human edits**, not a balance number. `tunables-ssot.md` §1 separates *runtime catalog*
(identity, player-visible) from *tunable* (a balance pass would change it). Nothing here is a balance
pass target, so no `tunable` key is introduced and `audit-magic-numbers.py` has nothing to flag.

**Authored, never generated.** These four files carry no `_meta.model`/`promptVersion`/`batch`
provenance, so the generated-tree rule ("fix the generator, never hand-edit") does not apply — they are
hand-authored authority, in the same class as `**/_registry/**` elsewhere in `gk-data/packs/fusion/data/seed/`. Verified
this session: `guard-generated-seed.py`'s tree table (`:41-68`) has no catch-all `^gk-data/packs/fusion/data/seed/`
pattern, and it explicitly *"correctly ignores"* authored registries under a generated root.

### `remediation` — the axis that makes the plan executable (audit A3)

`bucket` says **what a hit is**; it cannot say **how it may lawfully be fixed.** Those are different
questions, and conflating them is how an execute program hand-edits generated data — the exact defect
`AGENTS.md` calls a hard-rule violation. So every alias group also carries a `remediation`:

| `remediation` | Means | The sanctioned action |
|---|---|---|
| `authored` | Hand-authored source (a display registry, a prose doc) | Direct edit. |
| `generator-owned` | The file carries generator provenance | Change the **generator/prompt/tuning**, then regenerate and commit the pair. Never edit the JSON. |
| `upstream-imported` | Imported from the fan pack (`gk-data/packs/fusion/data/seed/external-reference/**`) | No generator exists. Needs an import-time filter or an authored rename map — a distinct decision. |
| `code-change` | An identifier or namespace (`pvz.*`) | Not a content edit at all; needs a code change and the demon→creature class of verification cost. |

`remediation` is **derived from provenance the file already carries** — the plan reads
`_meta.model` / `promptVersion` / `batch` (what `guard-generated-seed.py:6` defines as provenance) and
the path root — never guessed, and never inferred from a filename. Worked example of why it matters:
`gk-data/packs/fusion/data/seed/passive-tree/nodes/command.json:538` is `"name": "Overwatch Protocol"` — a `player-name`
bucket, **`generator-owned`** remediation (`:542` carries `"promptVersion": "tree-language/3"`), so a
plan that proposed a direct JSON edit would be wrong twice: reverted by the next generator run, and
rejected by the generated-seed guard.

### `self_paths` — three classes, not one hand-maintained list (audit A2)

The scanner's own artifacts are inside its scan scope. Measured this session:

| Path | IP marks it contains |
|---|---|
| `docs/architecture/ip-censor-ideal.md` | **69** |
| `docs/architecture/ip-censor/*.md` (these seven specs) | **31** |
| `docs/architecture/ip-censor-map.md` | **10** |
| `tasks/**` (393 files — where the plan is written) | **247** |

A program that bans `Overwatch` must be able to *write `Overwatch`* when explaining its own ban list,
and a plan containing every finding becomes input to the next scan if it is ever committed — a scan
that flags its own previous scan, growing each run. `self_paths` therefore has three authored classes
plus one derived rule:

1. Everything under `gk-data/packs/fusion/data/seed/ip-censor/` — the registry files and `curate`'s authored import filter.
2. This program's own documentation: `docs/architecture/ip-censor/**`,
   `docs/architecture/ip-censor-map.md`, `docs/architecture/ip-censor-ideal.md`. **Amended
   2026-09-19 (owner rulings IC-3, IC-4):** also `gk-core/tools/ip-censor/tests/fixtures/**`, which holds a
   fixture copy of the pre-fix `Overwatch Protocol` row (`spec-scan.md`). Now that the scan blocks a
   release, a fixture that must contain a real mark cannot sit on an enforced surface.
3. The plan home: `tasks/ip-censor/**`, which also holds `curate`'s candidate files
   ([spec-curate.md](spec-curate.md)).
4. **Derived, not authored:** any path the plan writer targets is self-excluded by construction, so a
   future output location cannot silently reopen the loop.

### Categories and surfaces — amended 2026-09-19 (owner rulings IC-1, IC-1b, R8–R12)

**`Category` has exactly three members** (IC-1): `franchise-mark` (game and franchise marks),
`real-person`, `company-brand`. Film, song and book titles are **out of scope** — the earlier `title`
member is removed, because common-phrase titles are a false-positive source. Attributed research
citations stay out of scope; they are never a registry concern (see `spec-scan.md`, the `docs/`
section).

**`Surface` gains `player-prose`** — player-facing running text, as distinct from a name field. The
narrative programs ([../narrative-seed-ideal.md](../narrative-seed-ideal.md) §6.5b,
[../npc-story-events-ideal.md](../npc-story-events-ideal.md) §10) add surfaces that are names *and*
prose, all player-facing and all in scope:

| Narrative surface | `Surface` |
|---|---|
| Character names and epithets; storylet names; arc names; main-story chapter titles; the names registry (`gk-data/packs/fusion/data/seed/narrative/_registry/names.en.v1.json`, new) | `player-name` |
| Character lines; storylet situations, choice labels and results; arc premises; spine chapter text; the motif gloss registry and any locale file | `player-prose` |

Other `player-prose` surfaces already exist: the player guide (`docs/guide/**`, which R9 renames) and
event copy under `gk-data/packs/fusion/data/seed/dungeon/**`. The surface classifier (owned here, consumed by `census` and
`scan`) reads path rules from `scope-policy.v1.json`; the `gk-data/packs/fusion/data/seed/narrative/**` rules are authored
rows there, not code.

**Entries the owner rulings require from day one** (all `franchise-mark`, admitted at `reconfirm` with
`census` evidence, since the census finds them and the owner confirmed them):

| Group | Aliases | Scope | Why |
|---|---|---|---|
| `pvz` | `pvz` (own scope, IC-6), `plants vs. zombies`, `plants vs zombies`, `plant vs zombie`, `plants versus zombies` | `player-name`, `player-prose` only | IC-1b: display and prose say "Fusion"; code identifiers (`pvz.*`, `drop.pvz.run`) are never in scope (ideal §6.1a) |
| `crazy-dave` | `crazy dave` | `player-name`, `player-prose` | R8/R9: the narrative uses original names; existing surfaces are renamed |
| `penny` | `penny` | `player-name`, `player-prose` | same |
| `dr-zomboss` | `dr. zomboss`, `zomboss` | `player-name`, `player-prose` | same; `zomboss` as a code identifier (`EmpireId` members, `stableId` values) is never in scope |

*Audit 2026-09-19 (standards audit; see [the map](../ip-censor-map.md) §"Standards audit"):*

- **A fifth day-one group.** `overwatch` (`franchise-mark`; scope `player-name`, `player-prose`,
  `generator-prompt`) is also owner-confirmed (IC-4) and ships on day one — [spec-avoid-list.md](spec-avoid-list.md)
  step 1 and `tasks/ip-censor-plan.md` D5 already said so; this table did not.
- **Remediation derivation reads three provenance shapes**, not only `_meta`: a top-level `_meta`, a
  top-level `_provenance` carrying `promptVersion`/`model` (`gk-data/packs/fusion/data/seed/passive-tree/nodes/command.json:2-5`),
  and a per-row `_provenance` or `promptVersion` (species rows; `gk-data/packs/fusion/data/seed/passive-tree/nodes/command.json:542`). One fixture per shape.
- **A sixth file:** `import-renames.v1.json` (IC-4.2) — authored `name → replacement` pairs plus an `ids`
  section (`old species id → new id`, owner answer to the plan's gate G1: yes). Every pair carries
  `confirmedBy`/`confirmedOn`; this module parses it and rejects a pair without them. It is under
  `gk-data/packs/fusion/data/seed/ip-censor/`, so `self_paths` class 1 covers it.
- **`self_paths` class 2 also lists the plan pair** `tasks/ip-censor-plan.md` and `tasks/ip-censor-todo.md`
  (class 3 is `tasks/ip-censor/**`, which a hyphenated name does not match).
- **The classifier is path-based, so a mixed file is not a player surface.** Source-code roots
  (`src/**`, `web/**/src/**`, `tests/**`, `tools/**` except `gk-forge/tools/seedsmith/**`, which stays the enforced `generator-prompt` surface) classify as
  `code-identifier`; player surfaces are pure display files (`*.po`, `docs/guide/**`, display
  registries, `gk-data/packs/fusion/data/seed/narrative/**`). A file such as `WorldTemplateCatalog.cs` holds both a kept
  identifier (`WorldFactionKind.Zomboss`) and a renamed literal; the identity-rename program proves the
  literal, and this gate must not enforce the identifier (`tasks/ip-censor-plan.md` D10).

**Species names are not registry entries.** R8 bars PvZ/Fusion species names from narrative prose; the
check is the narrative-seed "no literal names" validator, which reads the species catalog and this
registry together. Copying the species catalog into this registry would turn a population into a
closed vocabulary, which `validation-ssot.md` forbids.

### `admission` — which stage admitted the row (owner ruling IC-2, amended 2026-09-19)

The owner ruled that the registry is built in two stages: **first** a trademark dataset is imported and
curated down to game-related marks, **then** census hits and model-proposed candidates, each confirmed
by a person, re-confirm it. The flow itself is the `curate` module ([spec-curate.md](spec-curate.md));
this module only parses and validates the record it leaves:

| `stage` | Allowed `evidence` | `source` names |
|---|---|---|
| `import` | `dataset` | the dataset id and the record id inside it |
| `reconfirm` | `census`, `model-proposal` | the census run or proposal run that surfaced it |

`confirmedBy` and `confirmedOn` are required on every row: no row enters the registry without a person.
An imported row that a later reconfirm pass re-checks keeps `stage: "import"` and gains
`reconfirmedOn` — the admitting stage is history and is never overwritten.

**Tracked in the repo (owner ruling IC-5).** All files under `gk-data/packs/fusion/data/seed/ip-censor/` are tracked, so the
release gate runs identically on any clone. The whole directory is `self_paths` class 1.

## Code Style

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Category = Literal["franchise-mark", "real-person", "company-brand"]      # IC-1: titles are out
Surface = Literal[
    "player-name", "player-prose", "generator-prompt",
    "docs-prose", "code-identifier", "registry",
]
Remediation = Literal["authored", "generator-owned", "upstream-imported", "code-change"]
Stage = Literal["import", "reconfirm"]                                     # IC-2
Evidence = Literal["dataset", "census", "model-proposal"]


@dataclass(frozen=True, slots=True)
class Alias:
    text: str
    scope: frozenset[Surface] | None   # IC-6: required when len(text) < min_alias_length


@dataclass(frozen=True, slots=True)
class Admission:
    stage: Stage
    evidence: Evidence                 # import => "dataset"; reconfirm => "census" | "model-proposal"
    source: str
    confirmed_by: str
    confirmed_on: str                  # ISO date
    reconfirmed_on: str | None


@dataclass(frozen=True, slots=True)
class AliasGroup:
    mark: str                          # canonical, e.g. "pvz"
    aliases: tuple[Alias, ...]         # every spelling, includes `mark` itself
    category: Category
    scope: frozenset[Surface]
    remediation: Remediation           # HOW it may be fixed — see above (A3)
    admission: Admission               # WHO admitted it, at which stage (IC-2)


@dataclass(frozen=True, slots=True)
class BoundaryPolicy:
    separators: tuple[str, ...]        # characters that END a token
    script_change_breaks: bool         # Han↔Latin counts as a boundary
    min_alias_length: int              # 4 (IC-6); a shorter alias needs its own narrow scope


@dataclass(frozen=True, slots=True)
class Registry:
    groups: tuple[AliasGroup, ...]
    boundary: BoundaryPolicy
    replacements: dict[str, str]
    self_paths: tuple[str, ...]        # authored classes 1-3; class 4 is derived by `report`
```

Conventions mirror `source`: frozen slotted dataclasses, pure `parse(json_text) -> Registry`, error
messages that **name the offending key and file**.

**Dependencies are exact-pinned, never ranged** — `docs/architecture/seedsmith/spec-dependency-baseline.md`
§2.1: *"a range means two clones can run different code and both call themselves green."* Audit A5
measured that `pyahocorasick` and `regex` are **installed on this machine and declared nowhere** — no
`requirements.lock`, `requirements.txt`, or `[project.dependencies]` entry anywhere in the repo
contains either name. `gk-core/tools/ip-censor/pyproject.toml` + `requirements.lock` must pin them before the
first `import ahocorasick`, or a fresh clone fails at import the way seedsmith's undeclared `jieba`
did before it was declared.

## Testing Strategy

`pytest`, `gk-core/tools/ip-censor/tests/test_registry.py` (new).

Levels:
- **Unit** — every rejection path: missing array, missing field, empty field, duplicate mark,
  duplicate spelling across groups, short alias with no scope, malformed replacement, unknown
  `remediation` value.
- **Amended 2026-09-19 (IC-1, IC-2, IC-6).** A `title` category is rejected; a 3-character alias with
  only a group scope is rejected, and the same alias with its own subset scope is accepted (`pvz`);
  an alias scope wider than its group scope is rejected; a group with no `admission`, with
  `stage: "import"` and `evidence: "census"`, or with no `confirmedBy` is rejected.
- **Closed-vocabulary assertion** — the shipped registry's `category`, `surface` and `remediation` sets
  equal the declared closed sets, and every group's aliases include its canonical mark. **Pin the
  vocabulary, never the hit count.**
- **Self-exclusion (A2)** — parsing the shipped registry yields `self_paths` covering the three
  authored classes (registry files, this program's docs, `tasks/ip-censor/**`); `scan` over the
  shipped tree then reports **zero** findings inside them. This is the test that keeps the tool from
  flagging its own explanation of itself.
- **Boundary policy shape** — the policy rejects `\b`-only as a value (it must name separators), so
  the measured failure mode (`\b` matching inside `pvz-fusion-almanac`, missing `PvZ融合版`) cannot
  be reintroduced by configuration.
- **Remediation derivation (A3)** — a fixture file carrying `_meta.model` yields `generator-owned`; the
  same filename without provenance yields `authored`. Provenance decides, not the path spelling.

## Boundaries

- **Always:** throw on a malformed registry, naming the key; keep every judgement in these four files;
  require an alias-level scope for an alias under 4 characters; require an `admission` record on every
  group; prove self-exclusion across all three classes; pin dependencies exactly.
- **Ask first:** adding a new `Category`, `Surface`, `Remediation`, `Stage` or `Evidence` value (all
  closed vocabularies — a new member is a reviewed decision; re-adding `title` reverses IC-1); changing
  the minimum alias length from the owner-ruled 4 (IC-6).
- **Never:** default a missing field; auto-derive an alias group from the tree (that inverts
  authorship); derive `remediation` from a filename instead of provenance; place a balance-shaped
  number here; write a replacement the owner did not author or confirm.

## Open Questions

None. **Amended 2026-09-19 (owner rulings IC-2, IC-5, IC-1b).** The three questions this spec carried
were answered, and are kept here only as a trail:

1. ~~Registry provenance~~ — answered by **IC-2**: dataset import first, then census hits and model
   proposals confirmed by a person. This spec's earlier recommendation (census-only) is superseded;
   the `admission` record above is the result.
2. ~~Is the registry tracked publicly~~ — answered by **IC-5**: yes, in the repo.
3. ~~`pvz` group scope~~ — answered by **IC-1b**: player-facing surfaces only. This spec had put `pvz`
   in scope for `docs-prose` too, which contradicts the ruling; corrected above. Code identifiers
   (`pvz.*`, `software-architecture.md:13`) stay out, as before.
