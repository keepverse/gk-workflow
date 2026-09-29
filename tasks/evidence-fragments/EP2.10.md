# EP2.10 — `relead.py`: the pass-2 pipeline spec, enum-of-12 schema wrapped in `_blocked_variant`, kept out of `PIPELINES`

Spec: `docs/architecture/empire-progression/spec-lead-relabel-pass.md` (stage L, and "Seedsmith /
generator"'s pipeline row).

| Criterion | Command | Result | Artifact |
| --- | --- | --- | --- |
| `audit_schema` passes on the schema; a numeric variant fails; a variant without the wrapper fails (test 1) | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/test_build_favour_relead.py gk-forge/tools/seedsmith/tests/test_classify_pipelines.py -q` | pass — **28 passed** (0.52s). `test_the_relead_schema_passes_the_audit_and_carries_no_number` → `audit_schema(RELEAD.schema) == []` and the property set is exactly `aptitudePrimary · blocked` with the closed enum of twelve ids; the numeric variant is refused at `$.leadCount`; the wrapperless variant is refused for `blocked` | `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/build_favour/relead.py` (new) |
| A blocked sample counts as no vote (test 1) | same run | pass — `test_a_blocked_sample_is_not_a_vote`: one declination out of three leaves a 2-vote majority (`"Pierce"`, and `votes` is `("Pierce","Pierce")` — the declination is absent, never an empty-string vote); two declinations leave one vote → `unresolved`; three → `unresolved` | same file |
| The relead spec id is not a `PIPELINES` key, and the pins do not move | same run | pass — `test_the_relead_spec_is_not_a_pipelines_key` asserts `RELEAD.id not in PIPELINES` **and** `len(PIPELINES) == 8` (pass 2 is a separate pass, not a ninth classifier); `test_classify_pipelines.py` — the file that pins the eight and the audit behaviour — is part of the same green run, unchanged | `gk-forge/tools/seedsmith/tests/test_build_favour_relead.py` |
| One vote implementation where it applies; the reduced case is explicit | same run | pass — three real votes are handed to pass 1's own `resolve_vote` (3-0 `high` / 2-1 `split` / 1-1-1 `unresolved`, asserted equal to `ReleadVote` values), and 2/1/0 real votes are resolved here, with a non-enum answer raising rather than becoming a primary | same file |
| The brief shows the measured crowding, never a creature magnitude | same run | pass — `test_the_brief_shows_the_measured_crowding_and_never_a_creature_magnitude`: `369 of 892` and the current role are shown, the twelve ids are offered, staying put is stated as legal, and no `hp:`/`attack:`/`armor:` appears (pass 1's rule, reused through `_lore_block`) | same file |
| Path-owned verification | `.\scripts\verify-change.ps1 -Paths gk-forge/tools/seedsmith/seedsmith/adapters/creatures/build_favour/relead.py,gk-forge/tools/seedsmith/tests/test_build_favour_relead.py -Session empire-progression-20260920` | the seedsmith boundary runs the whole pytest suite: `9 failed, 932 passed, 1 skipped, 1176 subtests passed` — the same nine nodes EP2.9 proved pre-existing (SS-F1 in `tasks/seedsmith-todo.md`), with passed up by exactly this task's 8 new cases. That run again left `gk-data/packs/fusion/data/seed/creatures/_registry/themes.v2.json` modified (SS-F1's second half); restored with `git checkout --`, never committed | — |
| Not proved | — | No model call and no pass-2 run: the runner, the CLI verb and the provenance block are EP2.11/EP2.12. The schema contract is proven; the prompt's judgement quality is not (and cannot be, offline) | — |

> **Correction (EP2.12).** The line above says the boundary runs the whole pytest suite — that is
> wrong. For these paths the boundary selects a FOCUSED subset; a broader selection (any changed
> `gk-forge/tools/seedsmith/seedsmith/**` path mapping to `seedsmith-fallback`, e.g. `report/cli.py`) runs
> the whole file set instead and reports **22 failed / 4142 passed in 9m27s** on this tree, in
> subsystems this lane never touched — including `test_actions_description_completeness`, which
> attempts a real model call and times out here (the pre-existing state AGENTS.md already
> documents). The counts quoted above are the focused selection's.
