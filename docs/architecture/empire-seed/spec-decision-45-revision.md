# Spec: `decision-45-revision`

**Program:** [empire-seed](../empire-seed-map.md) · **Module id:** `decision-45-revision` · **Map row:** 6 ·
**Wave:** 0 (documents only; lands after map approval, which was given 2026-09-19) · **Decision:** D-E2,
confirmed by the owner 2026-09-19
**Depends on:** owner approval of the map (given) · **Model calls:** none · **Code:** none
**Status:** spec phase, 2026-09-19. No edit authorized until this spec is approved.

---

## 1. Objective

D-E2 gives `empire-seed` every world and empire content family, the structure corpus included.
`base-defense` and `trade-network` consume it. Base-defense decision 45's **content** stands: the
structure modules 23–29, their specs and their shipped code. Only the **program boundary** moves. This
module lands that boundary change in every document that still says `base-defense` owns the structure
corpus, and it annotates history rather than rewriting it.

**Done means:** every row of §5 carries its revision, `python scripts/audit-doc-citations.py` reports no
HIGH finding for each edited file, and a reader of any one of those documents reaches the right owner.

## 2. Scope and non-goals

**In scope.** Dated annotations and ownership lines in the documents of §5, and one `DESIGN-GATE.md` §1
row.

**Not in scope.**
- Rewriting base-defense's shipped history, specs or evidence.
- Any code, test or data change.
- The role-count annotations, which belong to `exchange-role` §5.6.
- `PRINCIPLES.md`. No principle changes: ownership is a boundary fact, and `decisions.md` carries it.

## 3. Current state (verified 2026-09-19)

| Where | What it says today |
|---|---|
| `docs/architecture/base-defense-ideal.md:163-164` | Decision 30: `structure-seed` is its own program |
| `docs/architecture/base-defense-ideal.md:183-191` | Decision 33: the planner *"belongs to `structure-seed`"* |
| `docs/architecture/base-defense-ideal.md:253-256` | Decision 45: `structure-seed` folds into `base-defense` as modules |
| `docs/architecture/base-defense-map.md:36-38` | *"`structure-seed` is now a module set inside this program"* |
| `docs/architecture/base-defense-map.md:69`, `:124-130`, `:154-161`, `:284` | The module family table, module rows 23–29, build order c0–c5, the closed-question row |
| `tasks/base-defense-todo.md:1632-1910` | Task sections `structure-schema` (c0) through `structure-metrics` (c5) |
| `docs/architecture/structure-seed-ideal.md:219-227` (§8) | Decision 45 as the program boundary |
| `docs/architecture/trade-network-ideal.md:573` | Boundary table: `base-defense` owns *"the structure anchor schema and its first corpus"* |
| `docs/architecture/decisions.md` — 'Structure corpus owner — empire-seed (2026-09-19)' | **Already present in the working tree** (uncommitted, 2026-09-19): the row *"Structure corpus owner — empire-seed (2026-09-19)"*. The map (§5.6, §11 item 11) said no row existed. That was true when the map was written and is stale now |
| `docs/DESIGN-GATE.md` §1 | No row for structure or empire content generation (grep this session: no `structure-seed` or `empire-seed` in the file) |

The base-defense structure specs are `docs/architecture/base-defense/spec-structure-{schema,corpus,catalog-import,instantiate,planner,pipeline,metrics,state}.md`.
The build session must read the header of each before annotating, because this spec reached them through
their code and todo evidence rather than reading each one in full (§12).

## 4. Principles as they bind this module

- **Propagate corrections** (DESIGN-GATE §3 rule 6). A boundary change that lands in one document but not
  its siblings has not landed.
- **History is annotated, not rewritten.** The shipped modules stay under the name they shipped under.
- **Docs are not code.** Nothing here can change behaviour. The only failure mode is a reader reaching
  the wrong owner.

## 5. Design: the revisions

| Where | Revision (one dated line or a new row) |
|---|---|
| `base-defense-ideal.md` decision 30 | *"Superseded twice: by 45 (2026-09-04), then by D-E2 (2026-09-19). The structure corpus is owned by `empire-seed`."* |
| `base-defense-ideal.md` decision 33 | *"Owner of the planner stage: `empire-seed` (D-E2, 2026-09-19). The decision's content is unchanged."* |
| `base-defense-ideal.md` decision 45 | *"Program boundary revised by D-E2 (2026-09-19): the module set 23–29 shipped here; the structure corpus is owned by `empire-seed` from that date. Content unchanged."* |
| `base-defense-map.md:36-38` | The same line as decision 45, with a link to `empire-seed-map.md` |
| `base-defense-map.md:69`, `:124-130`, `:154-161` | One note above the family table and one above the build order: *"Shipped under base-defense; owned by empire-seed from 2026-09-19 (D-E2). Further structure-content work is planned in `tasks/empire-seed-todo.md`."* The rows stay |
| `base-defense-map.md:284` | Append *"; boundary moved to `empire-seed` by D-E2"* |
| `tasks/base-defense-todo.md` before `:1632` | A pointer: *"Structure-content work after 2026-09-19 is tracked in `tasks/empire-seed-todo.md` (D-E2). History below stays."* |
| `structure-seed-ideal.md` §8 | A third row in the decisions table: D-E2, `empire-seed` owns the corpus, with its date |
| `trade-network-ideal.md:573` | The owner column for the structure schema and corpus reads `empire-seed` (D-E2), and `base-defense` becomes a consumer |
| `decisions.md` | **Verify only.** The row at `:147` exists in the working tree. If it is committed by then, cite its commit in the task evidence. If it is not, leave it to the session that wrote it and record that |
| `DESIGN-GATE.md` §1 | A new row: *"Structure or empire content generation (structure corpus, legion seeds)"* → must read `empire-seed-ideal.md`, `empire-seed-map.md`, `structure-seed-ideal.md`, `docs/architecture/empire-seed/`; what sessions get wrong: *"Putting a number in a seed file, or treating the structure corpus as base-defense's. Numbers resolve from `structure-seed` bands at load; empire-seed owns the corpus (D-E2)."* |

`DESIGN-GATE.md` is a shared, binding document. Its row is one table row, added in the same change as the
rest, and the row text is shown above in full so review is one read.

## 6. Commands

```powershell
python scripts/audit-doc-citations.py --scope docs/architecture/base-defense-ideal.md
python scripts/audit-doc-citations.py --scope docs/architecture/base-defense-map.md
python scripts/audit-doc-citations.py --scope docs/architecture/structure-seed-ideal.md
python scripts/audit-doc-citations.py --scope docs/architecture/trade-network-ideal.md
python scripts/audit-doc-citations.py --scope docs/DESIGN-GATE.md
python scripts/audit-doc-citations.py --scope tasks/base-defense-todo.md
```

## 7. Acceptance

1. Every row of §5 carries its revision. The review walks the table.
2. No sentence in the edited documents still states, **as current fact**, that `base-defense` owns the
   structure corpus. The grep `structure-seed.*(module set|folds into)` hits only annotated historical
   lines.
3. `audit-doc-citations.py` reports no HIGH finding for each edited file.
4. No shipped base-defense spec, evidence line or checkbox changes meaning.

## 8. Test plan and verification boundary

Documents only. The citation audit (§6) and the grep in criterion 2 are the verification. `docs/**` maps
to a documentation boundary (`gk-core/scripts/verification-boundaries.v1.json:3372`), and `tasks/**` edits carry
no test. No verify-change mapping gap applies here.

## 9. Hard edges

- **`decisions.md` and `DESIGN-GATE.md` are shared and binding.** Other sessions edit them (the working
  tree holds another session's uncommitted `decisions.md` rows today). Stage only the lines this module
  adds, and never `git add -A`.
- **`tasks/base-defense-todo.md` belongs to another program's ledger.** The edit is one pointer line
  above its structure section.

## 10. Dependencies

- Upstream: map approval (given 2026-09-19).
- Downstream: none in code. `exchange-role` annotates role counts in some of the same files, so schedule
  both in one docs session to avoid two passes over each file.

## 11. Open questions

None.

## 12. DESIGN-GATE §5 checklist

```
[x] Subsystems: program-boundary documents only.
[~] Session boundary: spec inside trade-network-idea-20260919. The edit session must record the six
    target files in its paths; they are outside this spec session's paths.
[x] Read this session: the cited lines of base-defense-ideal, base-defense-map, structure-seed-ideal §8,
    trade-network-ideal §11-§12 boundary table, decisions.md rows 147-148, DESIGN-GATE §1.
[ ] Not read in full: the eight base-defense spec-structure-*.md files (read through code and todo
    evidence). The edit session reads their headers first (§3).
[x] decisions.md checked: the D-E2 row exists (working tree, uncommitted).
[x] Every claim cites file:line.
[x] audit-doc-citations: no HIGH finding for this file.
[x] Verified against the documents themselves, line by line.
[x] Read the surrounding sections of decisions 30/33/45.
[x] Nothing to test beyond the audit and grep.
[x] No §2 invariant touched.
[x] Correction propagated: the map's "no decisions.md row" is stale; recorded here and in the map.
[x] No population pin.
[x] No cache, no ordering, no actor magnitude.
[x] No SOLID concern (documents).
[ ] New rule registry row: none.
```
