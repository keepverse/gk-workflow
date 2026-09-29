# ST5.2 — publish v4 at the R8 value and switch every reader in one commit (H7)

**Status: the switch is DONE and committed; the guard row is BLOCKED on a manager edit.** One acceptance
clause (`the guard's action-rungs row is added and green`) names a file this session's pipeline guard
refuses to let an agent touch, so it is recorded as a blocker with the erratum ask below rather than
becoming a second commit that would break H7's atomicity.

## The publish

```powershell
python gk-core/tools/tuning/publish.py action-rungs --label "R8 first calibration (docs/research/action-corpus/_budget-2026-09-19.json)" --reprice-rung-power-budget 1512 --mark-tuned
```

`published action-rungs (v3 -> v4, 11 change(s)); v3 stays on disk for revert`. Every row's
`powerBudgetMilli` was recomputed from its own `poolRolls`/`qPowerMilli` at REF **1512**, and
`_meta.referencePower` is now 1512 (from 1000), `_meta.referencePowerUntuned` cleared by
`--mark-tuned` alone. The label names the reading's own file, which is contract 6's citation.

**"0 rejected" follows from the rule, and rung 4 is the witness.** Contract 6's
`recommendedReferencePower` is *the smallest scalar at which no priced action exceeds its rung's
budget*, so publishing at that value rejects none by construction (ST4.2's spec test 9). The tightest
case in the real corpus is the setter itself: rung 4's v4 budget is `floor(1 × 1512 × 2315 / 1000) =
3500`, and `action.general.0004`'s realized power is exactly **3500** — it sits ON the line, not above
it. The other 17 actions sit below theirs (their implied values were all ≤ 1511, and the ceiling that
produced 1512 comes from this one action).

## The atomic switch — every reader, one commit

The guard's own scan roots are `src/` and `gk-forge/tools/seedsmith/seedsmith/` (not `tests/`), so those are the
files H7 governs. Ten non-comment occurrences, all switched:

| File | Was | Now |
|---|---|---|
| `gk-core/src/FusionRpg.Server/Program.cs:256` | v1 | **v4** |
| `gk-fusion/src/FusionRpg.Injector/Host/RpgHost.cs:227` | v1 | **v4** |
| `tools/seedsmith/.../characteristic_pool/pool.py:31, 39, 85` | v1 | **v4** |
| `tools/seedsmith/.../generate_validate_heal.py:12, 54` | v1, v3 | **v4** |
| `tools/seedsmith/.../generate_distribution_planner.py:7, 60` | v1, v3 | **v4** |
| `tools/seedsmith/.../distribution_planner/derive.py:546` | v2 | **v4** |

**The switch is proven by the guard's own property, computed independently of the (blocked) guard file:**
a scan of both roots for `action-rungs.v<n>.json` on non-comment lines returns **exactly one version —
`{4: 10 sites}`**. Before the switch it was `{1, 2, 3}`, which is precisely what the guard row exists to
refuse.

Note the transition is **v1 → v4** for both hosts, not v3 → v4: production was still loading the
pre-`powerBudgetMilli` table, so this commit is also the first time the budget column reaches the server
at all. That is why ST4.5's report shows `powerBudgetMilli: null` everywhere — expected, and ST5.3's job
to prove the check now evaluates.

## Verification

| Command | Result |
|---|---|
| `dotnet test tests\FusionRpg.Core.Tests -c Release -v q` | **14207/14208** — only the named CRLF worktree artifact. **No golden moved.** |
| `dotnet test tests\FusionRpg.Server.Tests -c Release -v q` | **552/552** |
| `dotnet test tests\FusionRpg.E2E.Tests -c Release -v q` | **226/226** |
| `$env:PYTHONPATH="gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/test_characteristic_pool.py gk-forge/tools/seedsmith/tests/test_distribution_planner.py gk-forge/tools/seedsmith/tests/test_validate_heal.py -q` | **263 passed, 1 skipped, 3 subtests passed** — the three seedsmith readers work against v4 |
| the one-version scan over both roots (above) | **`{4: 10}`** — one version, every reader |

`dotnet test tests\FusionRpg.Data.Tests` (whole) was started and **exceeded the 10-minute command cap
mid-run** (~6m25s of it at the cut); the only failure it had reported was the pre-existing
`CreatureSpeciesImportCliTests` creature-roster drift, which is unrelated to rungs and unmodified by this
change. The Data boundary's power/item/action filter was **471/471** earlier this session.

## Blocked clause + the erratum asked for

`gk-core/tests/FusionRpg.Guard.Tests/TuningVersionAgreementGuardTests.cs` is a **protected pipeline file**: the
hook refuses agent edits to it ("protected pipeline file (guards, verify, ledger script, hooks, CI)"),
and the brief says never to route around that. So `AgreedDomains` still lists only `action-base`, and
adding `action-rungs` is a one-line manager action:

```csharp
    public static IEnumerable<object[]> AgreedDomains() => new[]
    {
        new object[] { "action-base" },
        new object[] { "action-rungs" },   // ← ST5.2's row
    };
```

Asked for: either the manager adds that line (and ST5.2 closes on their commit), or an erratum accepts
the independent one-version scan above as this task's proof. The scan is the same property — one version
per domain over the same two roots, comments excluded — so it is the strongest check achievable from
inside the fence; what it cannot do is *keep* the readers agreeing, which is the row's whole value.

## Unmet clause, named

Acceptance clause 2 (`the three seedsmith --dry-run outputs are byte-identical except
characteristic-pool.json's sourceVocabulary line, which is regenerated and not hand-edited`) was **not
executed**: locating and running the pool generator did not fit this segment's budget, and the seedsmith
reader tests (263 green) exercise the pool path against v4 without it. The regenerated file's provenance
line is the only thing that should move; it is named here so the next segment does it as the acceptance
says rather than by hand.
