# narrative-seed NS6 — no-model-literal row (the row's last open half)

Spec: docs/architecture/narrative-seed/spec-model-config-resolve.md §6 · Row: tasks/narrative-seed-todo.md:141

The guard and the Class-C removal landed in `c150d3505` (ledger `mk1-c150d350553754f0`); the row stayed open
only because its *Files* line names `docs/architecture/decisions.md`, outside the predecessor lane's allowed
paths. This lane holds that path, so the drafted row (map §11 item 2) is the whole of the remaining work.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The R6 row is in `decisions.md`, naming the guard test and the resolution order | `pwsh -NoProfile -File scripts/verify-change.ps1 -Paths docs/architecture/decisions.md -AllowUnscoped` | pass — doc-citation audit 0 findings (D1–D4 all 0); `guard.doc-boundary` 4 passed | `docs/architecture/decisions.md` |
| `package_has_no_model_literal` and the S1–S5 positive/negative fixtures still green | `pytest gk-forge/tools/seedsmith/tests/test_no_model_literal.py -q -s` | pass — `7 passed` | `gk-forge/tools/seedsmith/tests/test_no_model_literal.py` |
| Class C: no `DEFAULT_CONFIG` outside the transport | `grep -rn "DEFAULT_CONFIG" gk-forge/tools/seedsmith/seedsmith/ --include=*.py \| grep -v "pipeline/llm_caller.py" \| wc -l` | pass — `0` | `gk-forge/tools/seedsmith/seedsmith/pipeline/llm_caller.py` |

**The whole-seedsmith-suite acceptance line is the predecessor's run, not mine**, and is attributed as such:
ledger `mk1-c150d350553754f0` records `4353 passed, 19 failed, all pre-existing` over six chunks. This lane
changed only `docs/architecture/decisions.md`, so re-running it would be the broad retry the verification
boundary exists to prevent; the scoped boundary above is the check for a doc-only increment.
`-AllowUnscoped` because `tasks/sessions/narrative-seed-2.json` does not exist (see NS25's fragment).
