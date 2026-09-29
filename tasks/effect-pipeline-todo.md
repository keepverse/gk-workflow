# Todo: `effect-pipeline`

**Plan:** [effect-pipeline-plan.md](effect-pipeline-plan.md) · **Map:**
[../docs/architecture/effect-pipeline-map.md](../docs/architecture/effect-pipeline-map.md) ·
**Status:** plan approved 2026-09-20 (`backlog-clean-up` BCU2.6). Prefix `EPL`. Modules 1–10 are
already shipped inside `seed-to-concrete-todo.md` (T3.1–T3.6, T5.1, T5.2, T5.7, T6.1, T6.2, T7.1,
T7.2) — not re-listed as tasks here, see the plan's own "Already shipped" table.

Verification: `.\scripts\verify-change.ps1 -Paths <changed> -Session <id>` for Core/Data changes;
`pytest gk-forge/tools/seedsmith/tests/<file> -q` for seedsmith changes. No task exceeds 5 files.

---

## Wave 1 — `affix-power-class` (module 11)

- [ ] **EPL1.1 — The closed enum + registry + C# mirror** · S · deps: — · *(spec: affix-power-class)*
  - Acceptance: 5 power classes, append-only, consecutive ordinals (no invented "spaced by 10"
    convention — corrected in the spec itself); no id collides with any rarity rung id, enforced by test.
  - Verify: `pytest gk-forge/tools/seedsmith/tests/test_power_class_registry.py -q`; `dotnet test
    gk-core/tests/FusionRpg.Core.Atoms.Tests --filter AffixPowerClass`.
      **Corrected 2026-09-27 (manager, leftover walk):** this named
      `gk-core/tests/FusionRpg.Core.Tests`, which no longer holds these tests - the atom tests moved to
      `gk-core/tests/FusionRpg.Core.Atoms.Tests` when Core was split, so the filter matched nothing and
      `dotnet test` still **exited 0**. A `Verify:` line that passes while running nothing is the
      shape this repository's own rules forbid, written where a later reader would take it as
      proof. Measured both ways at this head: as written **no test matches, exit 0**; corrected,
      **10 passed, exit 0**. The pytest half is unchanged and green (12 passed). The project
      `gk-core/tests/FusionRpg.Core.Tests` still exists - it is the filter's *target* that moved, not the
      project. Raised as open issue 4 by lane `resume-28b`, which addressed the fix to the program
      manager; its report is at `tasks/reports/resume-28b-effect-pipeline-epl1-1-20260925.md`.
  - Files: `gk-data/packs/fusion/data/seed/items/_registry/power-classes.v1.json` (new), `gk-core/src/FusionRpg.Core/Effects/Atoms/AffixPowerClass.cs` (new), tests.

- [ ] **EPL1.2 — The classifier + `MAX`-over-refs derivation** · M · deps: EPL1.1 · *(spec: affix-power-class)*
  - Acceptance: classifies the atom **family** (98), never the affix (~980); `powerClassOf(affixId) :=
    MAX over refs of familyPowerClass(ref)`, proven over a real bundle; a numeric field in the model's
    output is rejected mechanically, proven by test; `power_class_floor` column exists, nullable,
    unused in v1 (the additive escape hatch).
  - Verify: `pytest tools/seedsmith/tests/test_power_class_classify.py -q`.
  - Files: `tools/seedsmith/seedsmith/adapters/effects/power_class/{classify,derive,registry}.py` (new),
    `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Containers.cs` (`effect_affix` columns), tests.

- [ ] **EPL1.3 — ⛔ The 98-call classification run** · S-run · deps: EPL1.2, owner charter · *(spec: affix-power-class)*
  - Acceptance: all 98 families classified, `basis` on every row, `blocked` counted separately and not
    coerced; the distribution is reported against `data/tuning/affix-power-class.v1.json`'s declared
    target shares, a degenerate run flagged as a finding, not silently accepted.
  - Verify: `pytest tools/seedsmith/tests/test_power_class_metrics.py -q`.
  - Files: `gk-data/packs/fusion/data/seed/items/_registry/power-classes.v1.json` (populated), `data/tuning/affix-power-class.v1.json` (new).
  - **A K2 model-calling task** — 98 real calls, small next to the 4 corpus runs D4 authorized, but
    still spends model credit. Runs under its own owner charter (runtimes/models/budget/stop rule),
    per the multi-agent charter hard rule — not started without one.

### Checkpoint CEP1
- [ ] 98 families classified; `basis` on every row; re-running over unchanged families is byte-identical.
- [ ] No power-class id collides with any rarity rung id.

## Wave 2 — `affix-channel-weights` (module 12)

- [ ] **EPL2.1 — The `(powerClass × channel) → weight` policy shape** · S · deps: EPL1.1 · *(spec: affix-channel-weights)*
  - Acceptance: six closed channels (`drop`, `boss`, `set`, `socket`, `unique`, `craft`); the policy is
    a tunable table, published `v{n+1}`, never a code constant; a `drop`-channel weight may be
    vanishingly small and may never be exactly zero (the 0.01% floor), asserted in test.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter AffixChannelWeights`.
  - Files: the channel-weight tuning file (new), its loader, tests.

- [ ] **EPL2.2 — `poolFor(container, channel, rarity)` resolver** · M · deps: EPL2.1, EPL1.3 (needs real classifications) · *(spec: affix-channel-weights)*
  - Acceptance: extends `eligibility-tags` (module 8, already shipped), never replaces it — module 8
    answers "may this affix appear here" (binary), this module answers "at what rate"; a structural
    zero (e.g. a unique's fixed affixes are not rollable) carries a comment naming the exemption.
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter PoolFor`.
  - Files: the resolver, tests.

- [ ] **EPL2.3 — Wire `poolFor` into L1's existing draw** · S · deps: EPL2.2 · *(spec: affix-channel-weights)*
  - Acceptance: L0 composes the candidate list; L1's existing `affix.draw` stream draws from it — L0
    itself consumes no RNG. A container with no channel-specific weighting configured falls back to
    today's behaviour, byte-identical (the opt-in property, asserted not assumed).
  - Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "AffixDraw|ContainerResolve"`; no golden moved.
  - Files: the L1 draw call site, tests.

### Checkpoint CEP2
- [ ] `poolFor` returns different weighted lists for `drop` vs `boss`/`set`/`socket`/`unique`/`craft`
  on the same container.
- [ ] No golden moved anywhere in this plan; if one did, it is reported, never re-blessed.
