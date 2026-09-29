# EP1.18 — Supersede `aptitude-sheet` E3 in its spec (map ask X8)

Spec: docs/architecture/empire-progression/spec-default-build.md; map ask: `docs/architecture/empire-progression-map.md:326` (X8: "`aptitude-sheet` E3 ↔ R-Q3 — E3 keeps an empty unique empty — D1: R-Q3 is the later ruling. Ask filed")

| Criterion | Command | Result |
|---|---|---|
| `docs/architecture/aptitude-sheet/spec-aptitude-auto-assign.md:55-56` gains a one-line supersession pointing at `empire-progression` D1 (the default only; E1 unchanged) | (docs edit) | done — see the added blockquote right after the E3 line |
| Citations still resolve | `python scripts/audit-doc-citations.py --scope docs/architecture/aptitude-sheet/spec-aptitude-auto-assign.md` | 0 resolvable citations in this file, 0 HIGH across all four codes |

## What changed

Added a blockquote directly under the E3 rule ("Empty UniqueCreature / empty commander stays empty
until player Confirm or Activate — favour never writes Hub") stating:

- Superseded for **UniqueCreature only**: `empire-progression`'s `default-build` module (map D1)
  makes an unbuilt, levelled specimen compose the assign ladder's own default instead of staying
  empty — computed at read, never persisted, never written by this file's own favour draft.
- The **commander** half of the same E3 line is unchanged (`default-build`'s own map D1 scoping
  explicitly excludes the commander pool).
- **E1** (draft-then-Confirm, split verbs — confirmed from `aptitude-sheet-ideal.md:224`, an
  interaction-timing rule unrelated to what an unbuilt specimen's allocation resolves to) is
  unaffected either way.

No other file changed — the map's own X8 row (`empire-progression-map.md:326`) is left as-is per
this task's own Files list (docs-only, one file), since that shared map is read/edited by other
lanes too.
