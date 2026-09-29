# BCU2.12 / J10 — the `sheetRead` census gate (H7), all four paths exercised at `3f3a70104`

Lane `cmdc/bcu8-4`. Owner: `tasks/passive-tree-todo.md` **J10: The full census**. J10's own
**Verification** is *"the census refuses any lot with no `sheetRead` row (H7)"*, and its gate's own
docstring adds the second refusal (*"a census against a missing row and against a stale row both
refuse"*, `adapters/trees/review/census_gate.py`). Model-free; nothing under the repository is written.

## The four paths, observed

```
python tasks/reports/bcu2-12-j10-review-gate-probe.py
```

| case | exit | what the tool says |
|---|---:|---|
| no sheet rendered | **2** `EXIT_CANNOT_RUN` | `SheetNotRendered`: *"no sheet rendered for lot 'probe-lot' — expected …/probe-lot/sheet.json; run `node web/…/render-tree-cards.mjs --sheet --lot …` first"* |
| sheet rendered, **no** `sheetRead` row | **3** `EXIT_REFUSED` | `CensusRefused`: *"lot 'probe-lot' has no sheetRead row — read the corpus sheet at … , then dismiss it … before starting a census"* |
| sheet rendered, **stale** `sheetRead` row | **3** `EXIT_REFUSED` | `CensusRefused`: *"lot 'probe-lot''s sheetRead row names revision 'rev-OLD', but the sheet on disk is now 'rev-A' — the sheet changed since it was last read"* |
| sheet rendered, **current** `sheetRead` row | **0** | gate cleared — prints `{"lot": …, "sheetRead": {"sheetRevision": "rev-A", …}}` |

So the Verify clause holds on the surface it names, and the distinction the module's docstring cares
about is real in behaviour: "the sheet was never built" (`exit 2`) is not collapsed into "it was read and
then changed" (`exit 3`).

## The committed state this gate is guarding

| reading | value |
|---|---|
| `docs/research/passive-tree/_review/` (sheet dir) | **does not exist** |
| `data/seed/passive-tree/_review/` (review queue dir) | **does not exist** |
| lots with a rendered sheet | **0** |
| lots with a `sheetRead` row | **0** |

A probe against the committed defaults (rather than the temp overrides) therefore refuses at the *first*
reason, `SheetNotRendered`, exit 2 — which is what a real lot hits today. J10's acceptance — *"Every tree
judged … The acceptance record says **'every tree was judged'**, never 'the catalog was reviewed'"* — is
red by construction: nothing has been sheeted, so nothing can have been read or judged. That is the
correct state for a census whose input corpus is itself 4/904 complete
([bcu2-12-j9-readings.md](bcu2-12-j9-readings.md)).

## What this does and does not cover

**Covered:** the H7 gate, all four outcomes, on the CLI surface the Verify line names.
**Not covered, by the tool's own statement:** the census itself. `report/cli.py`'s `_cmd_trees_review`
docstring says `--census` "lands exactly the gate the todo's H7 acceptance names … and nothing past it —
the sheet itself, the three sampling tiers (§3.2) and the acceptance ladder (§6.2/§6.3) are
`adapters.trees.review.sample` / `.fingerprint` / `.verdict`, none of which exist yet (H8 and later)",
and parsing `trees review` without `--census` exits `EXIT_CANNOT_RUN` with that same message. So "the
census refuses any lot with no `sheetRead` row" is the whole of J10 that exists to verify today, and it
verifies green.

The probe's temp directory is deleted with a throwing delete and the reading records `tempRemoved: true`
(`docs/contributing/testing-standard.md` R3).
