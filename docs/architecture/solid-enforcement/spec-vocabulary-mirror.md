# Spec: `vocabulary-mirror`

**Program:** [`solid-enforcement`](../solid-enforcement-map.md) · **Wave 2** · depends on:
`guard-runner`.

## Objective

The C# code owns the repo's closed vocabularies (`ActionTag`, `ActionCategory`, the status catalog,
atom kinds, resource ids). Seedsmith (Python) must generate content *inside* those vocabularies, so it
carries **mirrors**. Seven vocabulary modules exist under `gk-forge/tools/seedsmith/seedsmith/adapters/`. A
mirror is a second declaration of one fact, so it drifts.

**It has drifted twice, measurably:**

| Mirror | C# owner | State (2026-09-18) |
|---|---|---|
| `adapters/actions/vocab.py` `TAGS` | `ActionEnums.cs` `ActionTag` | **was** stale 8 vs 9 (`construct` missing) until fixed by hand on 2026-09-13 |
| `adapters/actions/vocab.py` `STATUSES` | `gk-core/data/tuning/status-catalog.v1.json` | **stale now: 21 vs 24.** `nerve.afflicted`, `nerve.shaken`, `nerve.unsettled` are absent from the mirror |

**Why the existing tests never caught either.** `gk-forge/tools/seedsmith/tests/test_actions_adapter.py` pins
each mirror against a **hand-transcribed literal** (`test_nine_tags` asserts `TAGS == {…}`;
`test_twenty_one_statuses` asserts `len(STATUSES) == 21`). When C# grows, the mirror and its test are
the same transcription, and both stay stale together. A test that compares a copy to a copy of itself
proves nothing about the original.

Solid-remediation's `vocabulary-single-declaration` (X1, X2) fixed two *C#-internal* double
declarations. This module is the cross-language half it did not cover.

## Design

### The manifest: `gk-core/scripts/vocabulary-mirrors.v1.json`

One row per mirrored vocabulary. It declares where the truth lives and how the mirror relates to it:

```jsonc
{
  "schemaVersion": 1,
  "pairs": [
    { "id": "action-tag",
      "owner":  { "kind": "csharp-enum", "file": "gk-core/src/FusionRpg.Core/Actions/ActionEnums.cs", "enum": "ActionTag" },
      "mirror": { "module": "seedsmith.adapters.actions.vocab", "symbol": "TAGS" },
      "transform": "lower",          // Construct -> "construct"; how C# member names map to mirror strings
      "relation": "equal",
      "excludes": [] },
    { "id": "action-status",
      "owner":  { "kind": "json-catalog", "file": "gk-core/data/tuning/status-catalog.v1.json", "path": "entries[].id" },
      "mirror": { "module": "seedsmith.adapters.actions.vocab", "symbol": "STATUSES" },
      "transform": "identity",
      "relation": "equal",
      "excludes": [] }               // or: [{ "member": "nerve.*", "reason": "…" }] — see below
  ]
}
```

- **`relation`** is `equal` or `subset`. A mirror that deliberately covers part of a vocabulary uses
  `subset`, and **every** absent owner member must then match an `excludes` entry with a written
  reason. No silent subsets.
- **`owner.kind`** is `csharp-enum` (parsed from a simple `enum X { A, B, … }` block) or
  `json-catalog` (a JSON path). Only these two shapes exist among the pairs today, and a third is a
  reviewed extension.
- **The owner file for a tuning catalog is the latest published version,** resolved at run time
  (`status-catalog.v<max>.json`), never a pinned version number.

### The checker: `gk-core/scripts/guard-vocabulary-mirror.py` (the `.ps1` wrapper that used to front it was retired 2026-09-26)

Python, because it must import the real seedsmith symbols rather than re-parse Python source. The C#
side is read as text, and the parser handles exactly the enum shape the owner files use (members,
optional `= n`, comments, trailing commas). An enum it cannot parse **fails** the guard with the
file and line. It never passes vacuously.

| Check | Failure |
|---|---|
| **V1** | a mirror member not in the owner (the mirror invents a value) |
| **V2** | `relation: equal` with an owner member absent from the mirror (the mirror is stale; the two live cases above) |
| **V3** | `relation: subset` with an absent owner member not covered by `excludes`, or an `excludes` entry with an empty reason |
| **V4** | a manifest row whose owner file, enum or mirror symbol does not resolve |

### Seeding, and the live backlog

- **Seed rows** by walking the seven vocab modules under `adapters/` and pairing every module-level
  `frozenset`/`tuple` constant that mirrors a C# vocabulary. Measure at build time. Constants that
  are seedsmith's own vocabularies (for example `SCOPES`, `PAIRING_ROLES` if C# has no owner for
  them) get **no row**. A mirror needs an original.
- **`STATUSES`: decide by reading, not guessing.** If `vocab.py`'s own comment says actions draw
  only from non-delve statuses, the row is `subset` with
  `excludes: [{ "member": "nerve.*", "reason": "<that comment, quoted>" }]`. If it says nothing, the
  mirror is stale and gains the three `nerve.*` ids. Either way the drift is resolved *on the
  record*, and it is resolved **before** the guard gates (green-first).
- **Replace the transcription tests.** `test_nine_tags`, `test_twenty_one_statuses` and their
  siblings stop asserting literals and assert equality with the manifest-resolved owner set. The
  **C#-side** size pins stay where they are (e.g. the enum's own tests), so each closed vocabulary is
  pinned **once**, at its owner.

### Registry

A new guard row: `ci` / `backlog` → `vocabulary-mirror` while `STATUSES` is unresolved, then
`ci` / `gating`. Invariant row `dg-15-solid-single-declaration` → `vocabulary-mirror`.

## Commands

```powershell
python gk-core/scripts/guard-vocabulary-mirror.py
.\scripts\run-guards.ps1 -Only vocabulary-mirror
$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/test_actions_adapter.py -q
```

## Project structure

| Path | Change |
|---|---|
| `gk-core/scripts/vocabulary-mirrors.v1.json` | **new** |
| `gk-core/scripts/guard-vocabulary-mirror.py`, `.ps1` | **new** |
| `gk-forge/tools/seedsmith/tests/test_guard_vocabulary_mirror.py` | **new** (falsifiers) |
| `gk-forge/tools/seedsmith/seedsmith/adapters/actions/vocab.py` | `STATUSES` resolved |
| `gk-forge/tools/seedsmith/tests/test_actions_adapter.py` | literal pins → owner-equality |
| `gk-core/scripts/enforcement-registry.v1.json` | rows |
| `gk-core/scripts/verification-boundaries.v1.json` | map the new files |

## Testing strategy

Falsifiers use in-memory fake owner and mirror data:

- A mirror gaining an invented member fails V1.
- An owner gaining a member fails V2 (this reproduces the `construct` incident).
- A `subset` row with an unexcused gap fails V3, and an empty `reason` fails V3.
- A renamed enum fails V4.
- An unparseable enum block fails loudly, never passes.

The real tree passes after `STATUSES` is resolved.

## Boundaries

- **Always:** pin a closed vocabulary's size at its **owner**, once.
- **Ask first:** whether actions may apply `nerve.*` statuses, if `vocab.py` is silent and the choice
  is a design question rather than a stale mirror.
- **Never:** assert a mirror against a transcribed literal. Never add a pair for a vocabulary with no
  C# owner.

## Success criteria

- [ ] Every C#-owned vocabulary mirrored in seedsmith has a manifest row.
- [ ] V1–V4 each have a falsifier, and the real tree is green.
- [ ] `STATUSES` resolved on the record (equal plus 3 ids, or subset plus a quoted reason).
- [ ] No seedsmith test asserts a mirror against a literal.

## Self-audit — the debate

**Objection: "Parsing C# enums with a regex is fragile."** It is fragile only when it fails silently,
so it never does. An unparseable block fails the guard with a location. The owner enums are simple
by construction (closed vocabularies with no attributes-driven members), and a manifest row can only
point at an enum the parser has been shown to read.

**Objection: "Why not generate the Python mirrors from C#?"** Generation is the stronger end state,
and it would delete the mirrors outright. But it adds a codegen step to seedsmith's build that
seedsmith does not have today, for about eight constants. The guard achieves "cannot drift" at a
fraction of the cost. Recorded as the natural follow-on if the pair count grows.

**Objection: "Maybe `STATUSES` excludes `nerve.*` on purpose."** Possibly. That is exactly why the
spec reads the file's own comment before deciding, and records the outcome either way. What is not
acceptable is the current state, where nobody can tell whether it is deliberate.

## Gaps found and closed while writing

- **Found a live drift (21 vs 24) while writing,** not just the historical one. It became part of this
  module's backlog.
- **The transcription tests are the root cause,** not the mirror. Replacing them is in scope, since
  without it the guard would sit beside tests asserting a third copy.
- **The same tests file pins a population** elsewhere (`test_nodegen_vocab.py` asserts 125 affix
  families and per-tag counts). That is not a mirror. It is `population-pin`'s backlog, and handed
  there by name.
