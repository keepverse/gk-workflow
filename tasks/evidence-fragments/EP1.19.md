# EP1.19 — `/idea-ui` pass for the auto-assign control (placement + catalog key)

Spec: docs/architecture/empire-progression/spec-auto-assign-control.md (C1-C7 locked, not re-decided)

| Criterion | Command | Result |
|---|---|---|
| Pass recorded per `docs/architecture/idea-ui-phase.md`, names host piece/chrome, layout, catalog key | (doc) | `docs/architecture/empire-progression/auto-assign-control-ideal.md` |
| Citations resolve | `python scripts/audit-doc-citations.py --scope docs/architecture/empire-progression/auto-assign-control-ideal.md` | 0 HIGH (2 LOW D1, both the proposed `(new)`-marked catalog file, exempt-7) |
| Repo-wide strict guard unaffected | `python scripts/audit-doc-citations.py --strict` | 0 HIGH across 1678 docs / 24798 citations |

## Decision

- **Host:** the existing `aptitudes-console` recipe (`gk-web/web/fusion-rpg-web/src/ui/gui-lego/recipes/aptitudes-console.json`),
  no new surface/layer (GG-1: a flat 4-6 rule choice doesn't need a new mounted layer the way the
  growable preset list does).
- **Piece:** new `auto-assign-rule-strip`, placed in the `hero` slot after `preset-entry` and before
  `species-build-chrome`. Reuses `preset-action-strip`'s button-row + disabled/`title` refusal
  pattern (`pieces/aptitude.tsx:489`) rather than a new picker layer or a native `<select>`.
- **Catalog key:** `gk-core/data/tuning/aptitude-auto-assign-catalog.v1.json` (new — does not exist yet,
  EP1.20's job to create and publish via `gk-core/tools/tuning/publish.py`, H7-gated). Mirrors
  `aptitude-catalog.v1.json`'s id/displayName split: `RULE_LABELS`'s closed `AutoAssignRule` union
  stays in code as the key; only the display strings move to the catalog.
- Rejected shapes and why: a second click-to-open picker (oversized for a closed 4-6 item set), a
  native `<select>` (can't carry per-rule disabled+title refusal, bypasses the piece/theme registry),
  a new dedicated panel (oversized for one choice, no persisted sub-state).

## Notes

- C1-C7 are unchanged — this pass only answers "which piece" and "which catalog file", per the
  spec's own explicit scoping ("the `/idea-ui` pass decides layout only").
- The three raw citations of the not-yet-existing catalog filename each carry an explicit `(new)`
  marker so `audit-doc-citations.py`'s EXEMPT 7 (forward-looking proposal, not a stale/broken
  reference) applies — confirmed via a scoped re-run after adding the markers.
- No code touched. Per `idea-ui-phase.md` §6 hand-off rule ("Stop at the ideal. No specs, plans, or
  code from this phase"), EP1.20 is the next task and implements the piece + catalog + publish.
