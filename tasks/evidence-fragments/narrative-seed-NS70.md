# narrative-seed NS70 — reconcile the map and the ideal with what was built

Row: tasks/narrative-seed-todo.md:1259 · Docs: `narrative-seed-map.md`, `narrative-seed-ideal.md`

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The ideal reports 0 HIGH | `python scripts/audit-doc-citations.py --scope docs/architecture/narrative-seed-ideal.md` | pass — `67 resolvable citations`, D1–D4 `(0 HIGH)` | `docs/architecture/narrative-seed-ideal.md` |
| The map reports 0 HIGH | `python scripts/audit-doc-citations.py --scope docs/architecture/narrative-seed-map.md` | pass — `96 resolvable citations`, D1 9 **all `(0 HIGH)`** (the `(new)`/unbuilt files) | `docs/architecture/narrative-seed-map.md` |
| The ideal's §4.2 stale claim (model literals) reconciled with the code | (read) `gk-forge/tools/seedsmith/tests/test_no_model_literal.py` + NS3–NS6 | pass — §4.2's row is marked **CLOSED 2026-09-23** with the guard named; the history is kept as the trail | same |
| The R6 row's contradiction removed | (read) ideal §10 R6 | pass — "the 14 literals that already bypass the layer are a wiring gap" → 0 remain outside `llm_caller.py`, enforced by the guard | same |
| The `Instantiator.cs` and `layouts.py` citations verified against the code | `grep -n TryInstantiate src/…/Instantiator.cs`; `sed -n '33,44p' …/dungeon/layouts.py` | pass — `TryInstantiate` begins at `:98` and the six `_TEMPLATES` rows are at `:35-42`, exactly what both docs now cite | same |
| The map's §3.5 items 1–3 marked reconciled | (read) map §3.5 | pass — a "Reconciled 2026-09-23 (NS70)" paragraph says which are fixed and which were never stale citations (items 4–5) | map |
| The map's §13 audit reading refreshed | same command as above | pass — `94 citations; 9 D1 findings` replaces `69 citations; the two D1 findings` | map |
| The map's §7 `verification-boundaries.v1.json` row reconciled with NS1/NS2 | (read) map §7 | pass — the row now says this program DID add its rows there under the lane's protected-path grant, and that the mapping and its guard still belong to `python-test-lane` | map |
| The map's §11 decisions rows marked landed | (read) `docs/architecture/decisions.md` | pass — rows 2, 3, 4 and 6 are in `decisions.md` (NS6, NS25, NS28, NS23); rows 1 and 5 wait on `narrative-contract`/`narrative-emit` | map |
| Path-owned verification | `pwsh -NoProfile -File scripts/verify-change.ps1 -Paths <2 changed docs> -AllowUnscoped` | **pass — exit 0**; both paths focused; both doc-citation audits run, 0 HIGH; `guard.doc-boundary` 4 passed | — |

Every claim above was re-read against the code in this session, not recalled: the two citations the map's §3.5
had recorded as stale (`Instantiator.cs`, `layouts.py`) resolve where the ideal now says they do, and the
model-literal claim was checked by running the guard rather than by trusting the corrected text. A docs-only
commit is the deliverable itself here (spec errata and register rows), which is the sanctioned shape.
`-AllowUnscoped` because `tasks/sessions/narrative-seed-2.json` does not exist (see NS25's fragment).
