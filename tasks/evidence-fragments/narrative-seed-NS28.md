# narrative-seed NS28 — the spine frame: seven chapter slots and the fragment history

Spec: docs/architecture/narrative-seed/spec-arc-shapes.md §5 · Row: tasks/narrative-seed-todo.md:646

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `spine-frame.v1.json` exists: seven chapter rows chained by `after`, scenes empty, `fragments[]` | `pytest test_narrative_arc_shapes.py -q -s` | pass — printed `committed frame = 7 chapter(s), 7 fragment(s), afterLast='arcs-and-texture'` | `gk-data/packs/fusion/data/seed/narrative/_registry/spine-frame.v1.json` |
| `spine_chain_is_single_and_acyclic` | same | pass — printed `committed spine chain = ['chapter.one' … 'chapter.seven']`; a cycle, a gap, two roots, a duplicate id and an `after` naming no row each fail | `arc_shapes.py` |
| `frame_has_seven_chapter_slots` | same | pass — exactly 7 chapters in one chain, pinned as the owner's seven-piece declaration | same |
| `chapter_row_without_scenes_plans_nothing` | same | pass — a row with `scenes: []` validates clean and chains; printed `committed chapters with scenes = 0` | same |
| `scene_beats_within_tuning_cap` | same | pass — beats 0 and beats cap+1 each fail (`over scene.maxBeatsPerScene=3`); printed `committed scene.maxBeatsPerScene = 6`, read from `gk-core/data/tuning/story-scene-ui.v1.json` | same |
| `antagonist_speaks_when_chapters_exist` | same | pass — a fixture frame with scenes but no `lead_antagonist` speaker fails naming R2; one with it passes; a speaker outside the cast fails | same |
| `frame_teaching_order` | same | pass — in-order passes; backwards, a value the spine does not carry, and a value taught twice each fail | same |
| Fragment rows close: ids unique, `after` acyclic, every `afterChapter` a frame chapter | same | pass — each crafted violation fails; an empty `fragments` list is legal | same |
| `afterLast` is the fixed value | same | pass — anything else fails naming R3 | same |
| The decisions.md row (map §11 item 4, with `narrative-contract`) | `pwsh -NoProfile -File scripts/verify-change.ps1 -Paths <4 changed paths> -AllowUnscoped` | **pass — exit 0**; all four paths focused; doc-citation audit 0 findings (D1–D4 all 0); pytest 154 passed; `guard.doc-boundary` 4 passed | `docs/architecture/decisions.md` |
| ruff | `ruff check arc_shapes.py test_narrative_arc_shapes.py` | pass — `All checks passed!` | same |

**One rule is scoped, and it says why in the code.** §5's antagonist-speaks rule (R2) is applied from the
first SCENE onward, not from the first chapter: a chapter row with no scenes plans nothing and has no
speakers, so the committed frame's seven empty rows could never satisfy a speaker rule, and requiring one
would make the frame unshippable until NS29 authors the scenes. A fixture frame with scenes and no
`lead_antagonist` among the speakers fails, which is the rule doing its work. NS29 fills the scenes and the
same rule then applies to the committed frame.

No test counts chapters or fragments as a population: seven chapters is pinned as the owner's declaration
(a structural answer, not content that grows), and the fragment chain is checked for closure, not for size.
`-AllowUnscoped` because `tasks/sessions/narrative-seed-2.json` does not exist (see NS25's fragment).
