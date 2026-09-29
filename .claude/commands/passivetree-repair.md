---
description: Repair SeedSmith PassiveTree *code* first, then regenerate evidence and prove corpus health
---

Invoke the `seedsmith-passivetree-repair` skill and follow it exactly — especially **Step 0** and the
**layering rule**.

**Primary deliverable:** fixes under `gk-forge/tools/seedsmith/` (generators, briefs, quotas, persistence,
metrics, CLI) plus regression tests.

**Secondary deliverable:** regenerate affected PassiveTree seeds through the real CLI as *evidence*
that the code fix works. Generated `gk-data/packs/fusion/data/seed/**` is disposable; never hand-patch it to pass audits.

Operate as a closed loop: **Inventory → Measure → Investigate → Root-cause → Repair(code) → Test → Regenerate(evidence) → Re-audit → Discover → Repeat → Prove**.

Do not stop at the first green test. Never convert NOT_MEASURED into PASS. Regeneration alone is
legal only when the defect is proven stale-evidence or incomplete-run (classes D/E in the skill).

Completion requires population-wide proof **and** a repaired pipeline: every expected tree/node
accounted for, provenance current, metrics on real data, gates clean or evidence-backed exceptions,
and a final report with A–E root-cause classes, `file:line`, code diffs, before/after measurements,
and remaining blockers.

ARGUMENTS: optional focus (e.g. a tree id, a failing metric, a gate name). If omitted, start from full inventory.
