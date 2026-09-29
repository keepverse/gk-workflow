# narrative-seed NS27 — arc-shape registry, four shapes and six structural rules

Spec: docs/architecture/narrative-seed/spec-arc-shapes.md §2–§4 · Row: tasks/narrative-seed-todo.md:638

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `arc-shapes.v1.json` exists with the four v1 shapes, each with a description and a negative clause | `pytest test_narrative_arc_shapes.py -q -s` | pass — printed `rescue: 4 link(s), 1 role(s), antagonistRules=False`; `debt: 3/1/False`; `rival: 3/1/True`; `lost-piece: 4/0/False` | `gk-data/packs/fusion/data/seed/narrative/_registry/arc-shapes.v1.json` |
| Rule 1 — link count within the budget bounds; ids unique and prefixed | same | pass — a 2-link and a 6-link fixture each fail `outside arc.linkCount 3..5`; a duplicate id and an unprefixed id each fail | `arc_shapes.py` |
| Rule 2 — `hosts_and_kinds_are_legal` | same | pass — an unknown host and a kind the host does not admit each fail | same |
| Rule 3 — `required_choice_kinds_are_allocatable` | same | pass — `fight` on a `story` link is allocatable (fixture pattern); `offer` is not and fails | same |
| Rule 4 — `flags_read_are_set_earlier` | same | pass — a link reading a flag a LATER link sets fails; a flag id with a digit fails; an unknown `kind` fails | same |
| Rule 5 — `roles_close` | same | pass — undeclared role, declared-but-unused role, bad role id, reserved-suffix role id, bad `kind`, bad `allegiance`, unresolvable `requires` value and malformed requirement each fail | same |
| Rule 6 — `rival_has_only_progress_flags` | same | pass — a crafted antagonist shape with an `outcome` flag fails naming `R13 rule 3`; a `recruit` choice fails naming `R13 rule 1` | same |
| Rule 6 — `antagonist_shape_has_one_antagonist_role` | same | pass — two antagonist roles fail naming `R13 rule 2` | same |
| Rule 6 — `antagonist_role_requires_antagonist_rules` | same | pass — an antagonist role with `antagonistRules: false` fails | same |
| `shape_ids_pinned` + the committed file is clean | same | pass — `tuple(load_arc_shapes()) == ("rescue", "debt", "rival", "lost-piece")`, `all_defects() == []`, and an unknown shape id refuses | same |
| The link-count bound is read, never a constant | same | pass — printed `committed arc.linkCount = 3..5` from `gk-data/packs/fusion/data/seed/narrative/_plan/budget.v1.json`; a budget without the block refuses | `gk-data/packs/fusion/data/seed/narrative/_plan/budget.v1.json` |
| Path-owned verification | `pwsh -NoProfile -File scripts/verify-change.ps1 -Paths <5 changed paths> -AllowUnscoped` | **pass — exit 0**; all five paths focused (no unmapped path); pytest 146 passed; `guard.verification-boundaries` 57 passed | `gk-core/scripts/verification-boundaries.v1.json` |
| Boundary registry: the two narrative data roots now select this test | `python gk-core/scripts/guard-verification-boundaries.py` | pass — `VERIFICATION BOUNDARY GUARD OK` after adding `test_narrative_arc_shapes.py` to `seed-narrative-registry` and `seed-narrative-plan` | same |
| ruff | `ruff check arc_shapes.py test_narrative_arc_shapes.py` | pass — `All checks passed!` | same |

No test counts arcs or chapters: the four shapes are pinned as a declaration (a fifth is a reviewed registry
change) and every rule is proven by a crafted fixture, so shipping a fifth shape does not turn a test red.
NS28 adds the spine frame and its own chain/beats/teaching tests; this row deliberately stops at the shapes.
`-AllowUnscoped` because `tasks/sessions/narrative-seed-2.json` does not exist (see NS25's fragment).
