---
name: seedsmith-passivetree-repair
description: >-
  Investigate and repair the SeedSmith PassiveTree *generator* (gk-forge/tools/seedsmith code, briefs,
  quotas, metrics, persistence) AND the binder/resolve seam it feeds (src FusionRpg.Core.PassiveTree
  Binding/Resolve), then regenerate disposable corpus evidence and prove the whole population is
  healthy and actually reaches combat. Use when PassiveTree generation fails, corpus audits fail,
  nodes are missing/stale/inert, a tree is unplayable or contributes nothing, quota/distribution
  metrics break, provenance is wrong, or the owner asks to repair/prove PassiveTree generation or
  rebalance the tree — not merely to make tests green or edit seed JSON.
---

# SeedSmith PassiveTree Repair & Proof Skill

## ⛔ Step 0 — state this before touching any seed file

Restated inline (a pointer does not survive a long session):

1. **The product under repair is SeedSmith code** under `gk-forge/tools/seedsmith/` (generators, briefs,
   quotas, planners, persistence, metrics, CLI, tests).
2. **Generated PassiveTree seeds under `gk-data/packs/fusion/data/seed/` (and sibling out-dirs) are disposable
   evidence**, not the system being fixed.
3. **Regeneration is proof that a code/brief fix works.** It is never a substitute for that fix.
4. A change set that only edits generated seed JSON, or only re-runs generation without a
   corresponding `gk-forge/tools/seedsmith` (or metric/gate) fix, is **not a repair**.

If you cannot name the `gk-forge/tools/seedsmith` (or gate/test) file you will change, you are not ready
to regenerate.

---

## Purpose

This skill governs autonomous investigation and repair of the SeedSmith PassiveTree **generation
pipeline**.

The objective is not merely to make tests pass. The objective is to make both:

1. the **generation pipeline** (code + briefs + wiring) correct, and
2. the generated PassiveTree corpus **demonstrably** correct *as output of that repaired pipeline*.

Order is fixed: **pipeline first → then regenerate evidence → then re-audit.**

Treat generated data as disposable evidence produced by the pipeline, not as the source of truth.

---

## Operating model

Always operate as a closed-loop engineering investigation:

**Inventory → Measure → Investigate → Root-cause → Repair(code) → Test → Regenerate(evidence) → Re-audit → Discover → Repeat → Prove**

Never assume the original task list contains every defect.

A repair is incomplete until:

- the root-cause layer in `gk-forge/tools/seedsmith` (or the metric/gate that falsely reported health) is fixed, **and**
- its effect is observed through the appropriate downstream audit on regenerated (or proven-current) evidence.

---

## Layering rule (hard)

Classify every defect before editing anything:

| Class | What it is | Legal fix surface | Illegal |
|---|---|---|---|
| **A — Generator / brief / quota / planner** | Pipeline emits wrong shape, text, distribution, or incompleteness | `gk-forge/tools/seedsmith/**` (+ focused tests), then regenerate affected trees/nodes | Hand-editing `gk-data/packs/fusion/data/seed/**` to look correct |
| **B — Persistence / wiring** | Fields not written/read (`quotaCell`, provenance, ledger) | Writer/reader/schema/tests in `gk-forge/tools/seedsmith` (and check path) | Patching one record so a metric passes |
| **C — Metric / gate / test defect** | Measurement lies or is unregistered | Metric registration, check path, tests | Weakening thresholds; deleting hard cases |
| **D — Stale evidence only** | Pipeline already correct; corpus vintage predates the fix | Regenerate via real CLI; record scope | Claiming health from pre-fix corpus |
| **E — Incomplete run** | Pipeline OK; generation never finished | Resume/fill via real CLI; ledger reconcile | Inventing missing nodes by hand |

**Default assumption:** a bad seed is class **A** or **B** until proven **D** or **E**.

**Regeneration alone is allowed only for D or E**, and only after you cite evidence that the
current `gk-forge/tools/seedsmith` code/brief already embodies the correct behavior (test or `file:line`).

---

## 0.1 The seam is wider than the language stage (read this before Phase 1)

A PassiveTree only reaches a player through three layers, and a defect in **any** of them makes the
tree unplayable while every SeedSmith test stays green:

```
tree-language (gk-forge/tools/seedsmith)  →  tree-binder (src/…/PassiveTree/Binding)  →  tree-resolve (src/…/PassiveTree/Resolve)
   picks affixIds, writes seed        prices atoms into NodeAtom               fans atoms into combat channels
```

**A corpus that binds nothing, or binds atoms nothing reads, is a failed repair even if `check
--family PassiveTree` is green.** Two measurements catch this class, and both belong in every
completion report:

| Metric | What it catches | Healthy value |
|---|---|---|
| **Refusal census** (bound vs refused, bucketed by reason) | vocabulary/generator drift | refused = 0, or every refusal named and evidenced |
| **Inert-bound census** (bound nodes carrying zero *readable* atoms) | binder prices a kind the resolver drops | 0 |

**The binder is the authority on what binds; the resolver is the authority on what is read. Both must
be measured, and the kinds they agree on must be non-empty.** A "bound" node whose `kindId` is not the
one `TreeAtomSource` reads contributes exactly zero — the most expensive failure in this seam, because
it is silent.

### Defects already measured (2026-09-11) — do not re-derive

Baseline: 42/42 trees `Fail`, 266/1,680 nodes bound, 1,414 refused, 108 bound-but-inert, and
`gk-forge/tools/TreeBinder --check` **crashes**.

| Root cause | Class | Fix surface |
|---|---|---|
| **R1** language offers 125 branch-tagged affix ids; only 26 have generated atoms | **A** | `gk-forge/tools/seedsmith/…/nodegen/vocab.py`, `quota.py` |
| **R2** 6 generated families use `op:"more"`; `NodeAtomOp` has no `More` | **C** | `src/…/PassiveTree/Catalog/NodeAtom.cs` (+ loader/binder/resolve) |
| **R3** `AffixComposer.ParseAtom` calls `GetString()` on a pool-object `channel` → unhandled crash | **B** | `src/…/PassiveTree/Binding/AffixComposer.cs` |
| **R4** binder prices `stat.modify`; `TreeAtomSource` reads only `stat.derived` → all bound nodes are inert | **B** | `TreeBinderRun.cs` + `Resolve/TreeAtomSource.cs` |
| **R5** mechanism atoms never carried → 108 inert bound nodes, deep tiers dead | **B** | `TreeBinderRun.cs` + `mechanism-wiring` seam |
| **R6** committed `gk-data/packs/fusion/data/generated/passive-tree` stale, not reproducible | **D** | regenerate only after R1–R5 |

Full plan and task list: `tasks/passive-tree-repair-plan.md`, `tasks/passive-tree-repair-todo.md`.
**Regeneration is Phase 5 there, never Phase 1** — and `gk-data/packs/fusion/data/generated/passive-tree/**` is generated
evidence, so the same "never hand-edit" rule applies to it as to `gk-data/packs/fusion/data/seed/**`.

---

## 1. Inventory / coverage

Before making substantial changes:

- discover every PassiveTree and expected node;
- inspect plans/specs, generation configuration, quotas, mechanisms and provenance;
- inspect generation ledgers and committed corpus;
- determine generated/missing/stale status;
- establish a per-tree/per-node coverage view;
- locate the **code** paths that emit, persist, and check those trees (`gk-forge/tools/seedsmith/...`).

Never use an aggregate metric as proof that every tree works.

A single broken tree remains a failure.

---

## 2. Evidence hierarchy

Prefer evidence in this order:

1. direct source/code inspection (`gk-forge/tools/seedsmith`);
2. deterministic tests;
3. machine gates;
4. complete corpus measurements;
5. statistical sampling;
6. human/census evidence.

Every conclusion must identify its population.

Distinguish:

- PASS
- FAIL/GAP
- NOT_MEASURED
- BLOCKED
- EXPECTED/EXEMPT

Never convert NOT_MEASURED into PASS.

---

## 3. Failure taxonomy

For every failure determine the actual root cause (use the layering table above):

- generator implementation defect
- quota/distribution defect
- prompt/brief defect
- persistence/wiring defect
- validation/metric defect
- incomplete generation
- stale generated corpus (evidence-only; pipeline already fixed)
- test/tooling defect
- legitimate domain exception

Fix the earliest correct layer.

Do not compensate for a generator defect by manually editing generated records.

Do not weaken thresholds or remove failing cases merely to obtain green output.

---

## 4. Measurement

Use the existing PassiveTree methodology and infrastructure.

Run available machine gates and metrics.

Complete missing wiring when measurement is blocked by implementation rather than genuinely unavailable evidence.

For quota distribution, use the same quota derivation functions as generation.

For provenance-related findings, verify the actual prompt/generator version stored in generated records.

For generation completeness, reconcile the corpus against the generation ledger and expected plan population.

For every GAP ask:

**Why did the pipeline produce this result?**

not merely:

**How can I make the metric pass?**

---

## 5. Repair (code is the default deliverable)

For each root cause:

1. identify the source location in `gk-forge/tools/seedsmith` (or the gate/test that is wrong) — cite `file:line`;
2. explain why it causes the observed failure;
3. implement the smallest correct fix **at that layer**;
4. add/update focused regression tests that would fail on the old code without needing the full corpus;
5. run relevant tests;
6. only then regenerate affected evidence if the defect could have poisoned seeds;
7. rerun the affected metric/gate.

Preserve compatibility for old records where practical.

When adding persistence fields, test both new records and legacy records.

When changing validation/reporting, verify the check path actually receives real data.

**Acceptance check for a claimed repair:** the diff must include a `gk-forge/tools/seedsmith` and/or test/gate
change, **unless** the defect was proven class D or E with cited evidence.

---

## 6. Regeneration (evidence only)

Generated corpus data carrying stale generator/brief provenance is not valid evidence for a repaired generator.

If a defect poisoned generation:

- repair the generator/brief/wiring **first**;
- identify affected trees/nodes;
- regenerate them through the real generation CLI;
- record what was regenerated and why;
- rerun the audit.

Do not leave known defective generated data simply because regeneration costs model spend.

Avoid unnecessary regeneration, but never confuse cost avoidance with correctness.

**Never** “fix” a seed by hand and call regeneration optional. If the pipeline is wrong, hand-fixed
seeds will rot on the next honest generate.

---

## 7. Iteration loop

After every meaningful repair:

**test the code fix → generate/reconcile if required → full relevant audit → inspect all failures → select next root cause**

If the audit exposes a new problem, continue.

If fixing one issue changes another metric, investigate the new result.

If only some trees pass, continue with failing trees.

If the audit infrastructure is wrong, repair it and rerun the audit.

The original TODO list is a starting hypothesis, not the completion boundary.

---

## 8. Tests

Tests must prove behavior, not merely implementation details.

Use:

- focused unit tests on generator/quota/persistence/metric code;
- persistence round-trip tests;
- check-path/integration tests;
- generation validation;
- corpus audits;
- full SeedSmith test suite.

Do not move goldens or alter expected values merely to make tests green unless the expected behavior itself has been deliberately changed and justified.

---

## 9. Completion proof

Completion requires evidence for the entire population **and** a repaired pipeline.

Verify:

- every expected tree exists;
- every expected node has a final status;
- no unexplained missing nodes remain;
- current generator/brief provenance is valid;
- distribution/quota checks use real wired data;
- each known defect has a **code/gate fix** (or a proven D/E exemption) **and** affected evidence regenerated when needed;
- machine gates pass or have evidence-backed documented exceptions;
- available statistical/census checks are complete;
- relevant persistence paths work;
- full test suite passes;
- final PassiveTree family check is clean/understood.

The final report must contain:

- root causes with class A–E and `file:line`;
- code/config changes under `gk-forge/tools/seedsmith` (and gates/tests);
- regenerated trees/nodes (scope + why);
- before/after measurements;
- tests and commands executed;
- remaining NOT_MEASURED/BLOCKED items;
- exact blockers and ownership;
- evidence supporting completion.

---

## Refuse to ship a “repair” that does any of these

- edits only `gk-data/packs/fusion/data/seed/**` (or other generated out-dirs) without a pipeline/gate fix;
- regenerates as the sole response to a generator/brief/quota/persistence bug;
- weakens thresholds, deletes hard cases, or moves goldens to hide failure;
- declares success from code inspection or unit tests alone without population audit when corpus health is in scope;
- converts NOT_MEASURED into PASS;
- claims regeneration happened without executing the real CLI;
- claims the pipeline works without exercising the real pipeline after the code fix;
- stops because the original TODO list is complete while audits still fail.

**The system is finished only when the evidence proves both: the SeedSmith PassiveTree pipeline is fixed, and the whole PassiveTree population regenerated from that pipeline is healthy.**
