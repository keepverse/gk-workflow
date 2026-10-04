# Completion criteria: `status-tracks`

How to tell whether this program is actually done, and how to tell whether it merely looks done. A
green suite is not the test — **a green suite that cannot fail is the failure mode this file exists
to catch.** Every criterion below is written so a reviewer can falsify it.

## A. The program is complete when

1. **Both tracks are expressible without new engine code.** A new combat status is a catalog row
   plus a grant overlay; a new out-of-combat track is a ladder function, a `StatusProjectionHost`
   rung list, and a caller. Neither needs a runtime, a bag, a tick or a catalog.
2. **The tick has exactly two owners, and a third turns the build red.**
   `StatusTickOwnershipTests.StatusTick_is_driven_from_exactly_the_two_known_seams_inside_Core`.
   *Falsifiable:* plant a `StatusRuntime`-typed member whose `.Tick(` is called under
   `src/FusionRpg.Core/` and the suite must fail naming the file. **Verified 2026-10-02** — planted a
   third owner, got `Failed: 1` naming the offender, removed the probe, back to green.
3. **The projection host is proven against the shipped policies, not merely beside them.**
   Walked-ladder parity runs the host and `NervePolicy.Sync` (and `ExhaustionPolicy.Sync`) through
   the same stage sequence on two independent runtimes and asserts the same live id and the same
   grant id at every step.
   *Falsifiable:* change one host behaviour and the parity test must fail.
4. **Idempotence is structural.** N calls at an unchanged stage produce exactly one apply; a stage
   change withdraws before applying so two ids of one track never coexist on one host.
5. **A track has no clock.** No `DateTime.UtcNow`, no wall-clock read, in the host or its tests;
   `BaseDuration 0` means `ExpiresAt == DateTimeOffset.MaxValue`, asserted directly.
6. **The negative rules are pinned as tests, not prose.** No count field on `StatusInstance` (by
   reflection, so adding one breaks it); `Coexist` produces siblings, not a stack; the anti-spiral
   refusal throws at construction for **every** rung, not just the first.
7. **The authoring cost is written down and true.**
   `status-tracks/authoring-combat-statuses.md`, every `file:line` citation openable
   (`audit-doc-citations.py --strict` → 0 HIGH).
8. **Nothing regressed.** The wider Core suite and the guard suite are no worse than before this
   program started.

## B. The program is NOT complete when any of these is true

- The status suite is green **and** criterion 2's mutation no longer fails. A guard that cannot be
  made to fail is not a guard. This exact trap was live during the build and was caught only by
  planting the probe.
- A track needs to be correct at every instant in a place with no `StatusRuntime`. That is the
  second-engine shape, and the answer is deferral (`EventOutcomeDispatch.cs:66-77`), not a new
  runtime.
- A need's only shape is elapsed-real-time decay. There is no legal home for it; that is a product
  decision (`K1.2`), not an implementation problem.
- A status id was added without both count lines moving in the same commit — `status-ssot.md` §9
  **and** `docs/design-gate/combat.md:14`.
- A seventh `ResourceIds` pool was added without an owner ADR. The packet's default is a
  projection; the default is not permission to widen.
- `ExhaustionPolicy`/`NervePolicy` were rewritten onto the host. Extraction without migration is
  the deliverable; migration is separate work and would change shipped behaviour.

## C. Explicitly out of scope — and two corrections to this section

- **D1 (`battle-engine-ssot.md` §4) is FIXED, and this section previously said it was not.**
  It once reported that a status pulse applies its authored number with no hit roll, crit, matchup,
  penetration or block. `BattleRunState.cs:469-497` (solid-remediation T2.5) wires
  `Bag.CombatMath`, `ActorResolve` and a battle-seeded `effect-combat` RNG stream, so a DoT resolves
  through the same math as a swing. **Corrected 2026-10-02 after reading the code**; the earlier
  claim in this file and in `status-tracks-ideal.md` was wrong.
- **`turn.haste` is not inert everywhere.** `BattleModeProfile.Delve` is built with
  `ordersBySpeed: true` (`BattleModeProfile.cs:295-300`), so the delve profile reads readiness and
  haste is live there. What remains true is narrower: **no tuning row in
  `gk-core/data/tuning/*.json` sets an orders-by-speed flag** (`ordersBySpeed` appears in no tuning
  file), so the content surface for it is unwritten. That is a battle-**profile** gap owned by
  battle-tempo, not a status gap.
- **Shield** is deliberately a separate subsystem and is not a status gap.
- Choosing *which* need ships first was answered by the packet default (ship as a projection); the
  balance numbers for any specific track are still not this program's.

## D. Evidence (2026-10-02)

| Criterion | Evidence |
|---|---|
| Baseline before the program | `FusionRpg.Core.Status.Tests` **170 passed, 0 failed** |
| After Wave 1 | **244 passed, 0 failed** (+74) |
| After Wave 2 + doc-claims tests | **254 passed, 0 failed** |
| Wider Core suite | `FusionRpg.Core.Tests` at `66991a8` is **9758 total: 9625 passed, 133 failed** — ⚠️ **corrected 2026-10-04; this row previously read "9758 passed, 0 failed", and the total was right while the outcome was not.** The 133 are **one** failure, not 133: `RealAnchorCorpusFixture`'s static initializer throws `AnchorRowRejection: anchor: missing or non-string 'aptitudeSecondary'`, and a throwing static initializer takes its whole fixture — and every `Delve.Encounter` test that depends on it — down with it. Cause: gk-core's `AnchorRowReader` requires `aptitudeSecondary` on every anchor row (introduced in `34bf27d`, the legacy import, long before this program), while **28 of the 464** committed species files in `gk-data/packs/fusion/data/seed/creatures/species` do not carry the field. gk-data is clean at `8a6a87e`. **Why it was true when written and is false now:** this program's measurement is dated 2026-10-02, and the creature corpus was regenerated across six gk-data commits on **2026-10-03/04** (`ecea52c` "regenerate the anchor corpus through the delegated authoring pass" onward, including `0621cd7` "every entry in the corpus is now loadable by its own consumer" — evidently an incomplete attempt at this very class). So the suite did not regress *because of this program*; a separate program moved the corpus under it afterwards. **Not caused here and not fixable here**: none of this program's files appear in the failure path, and the fixture's own comment records this same failure class from an earlier root cause ("109 tests in `FusionRpg.Core.Tests` failed through this one helper"). Re-measure after the corpus and the reader agree; the claim to re-establish is `0 failed`, not a passing count |
| Guard suite | **738 tests: 737 passed, 1 failed** at `66991a8` — the failure is `VerificationBoundaryWorkflowTests.Planner_rejects_a_path_outside_the_active_session_scope_before_testing`, throwing *"no active session record"*. Separately, the **guard runner** for this landing, `scripts/run_guards.py --tier ci --ci-range f41559a..66991a8`, is **27 guards run, 0 red, exit 0**. ⚠️ **This row has been corrected twice on 2026-10-04, and the first correction was itself wrong — recorded rather than deleted, because that is the failure mode.** It originally read "737 passed, **1 failed** — `EnforcementRegistryGuardTests.R8_every_catalog_guard_is_named_by_an_invariant` … **verified pre-existing**", which had two separate problems. (a) The *attribution* was stale: `f41559a` ("Name citation-stability by an invariant row, which R8 has been failing on") had already fixed R8 by registering the missing invariant row, and `EnforcementRegistryGuardTests` now passes **20 passed / 0 failed** in isolation. (b) "Verified pre-existing" was a *timestamped* claim about a tree state, and it went stale the moment the tree moved. The first correction then over-corrected to "737 passed, 0 failed", which the full project run contradicts: the count really is **1 failed / 737 passed / 738 total**. What changed is the *cause* — it is a different test, and this workspace has **no active session record**: the only `status: active` file in `tasks/sessions/` is `_template.json`, which that test skips by design (`VerificationBoundaryWorkflowTests.cs:152`). Nothing this program did causes it, and nothing here can fix it — it needs an active session record to exist |
| `citation-stability` | **The one guard that actually failed on this program, and the row this table omitted.** `scripts/guard-citation-stability.py` refused with `NEW CITATION decisions.md:158 - no baseline entry (cited from decisions/combat.md:34)` — the new ADR row is cited *by number* from two places (`decisions/combat.md:34` and this file's Decision-citations row), so landing it required a re-baseline entry. ⚠️ Deliberately NOT re-baselined by `f41559a`, which cites that reasoning in its own message: absorbing a concurrent session's uncommitted `decisions.md:158` into a committed baseline would launder half-landed work. The entry was taken when the work actually landed. Exit 0 before the commit, not beside it |
| Criterion 2 mutation | Planted third tick owner → `Failed: 1`, `StatusTick_is_driven_from_exactly_the_two_known_seams_inside_Core`; probe deleted; suite green again |
| Doc-claims tests are not vacuous | Agent-mutation-verified: a 7th `ResourceIds` entry → `Failed: 1`; renaming one status id → `Failed: 5` (a count-only assertion would have stayed green through an add-one/delete-one swap); rewriting the battle tick seam's arguments → `Failed: 1`. All mutations reverted |
| No weakened tests | 0 `Skip`, 0 `Assert.True(true)` across the new test files (the one `Skip` hit is LINQ `.Skip(`) |
| Citations | `audit-doc-citations.py --strict` over `status-tracks/` and `status-tracks-completion.md` → **0 HIGH** |
| Decision citations | `scripts/check-decision-citations.py` → 187 in-table markers resolve, including `decisions.md:158` |
| Wave 2 | Unblocked by the packet's stated defaults (K1.1 no seventh pool · K1.2 no wall-clock need · K1.3 deferral OK). [need-inventory.md](status-tracks/need-inventory.md) + [carrier-rule.md](status-tracks/carrier-rule.md) built. Verdicts: thirst · morale · disease · environmental-poison → **projection**; temperature → **bad fit, stated plainly**; sleep/fatigue → **excluded**. **No need requires a pool under the default** |

## E. What a reviewer should try to break

The order below is deliberate — cheapest falsification first.

1. Add a third `StatusRuntime.Tick` call under `Core/`. **Must** redden (criterion 2).
2. Change `StatusProjectionHost.Sync` to re-apply on an unchanged stage. **Must** fail the
   idempotence test and the parity test.
3. Make a stage change apply before withdrawing. **Must** fail the coexistence test.
4. Add a `Count` property to `StatusInstance`. **Must** fail the reflection test.
5. Delete one of the two tick seams. **Must** fail loudly rather than pass vacuously — the positive
   control exists precisely so a deleted seam cannot read as a clean bill of health.
6. Put a stage's mods on its own driving pool's regen channel, at a rung other than the first.
   **Must** throw at construction.