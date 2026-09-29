# `CAI-pp1` — `ProvePredictor` re-measured at the merged head

`CP2` clause 2 (*"the twin agrees with the real core policy; `ProvePredictor` under `1e-4`"*), `CP3`
clause 3, `CAI2.3` and `CAI3.6` all quote this tool. The last numbers this program recorded were taken at
`CAI2.3`'s identity slice (`max diff 8.836E-007`), **before the mega-merge** and before wave 4's Core
landings, so this re-runs it rather than inheriting the claim.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The tool passes, both scopes and both extra checks | `dotnet run --project gk-core/tools/ProvePredictor -c Release` | **exit 0**; `archetypes: force, finesse, bastion  theta: 100  model: aptitudes.v1` | `gk-core/tools/ProvePredictor/Program.cs` |
| Core path: the port matches the reference | same run | `MAX ABS DIFF in WinShareA across 6 arrows: 2.827E-007` → `PASS -- the port matches the reference within long-rounding tolerance.` | — |
| Theta-invariance (Theta=10 vs 5000) | same run | `MAX ABS DIFF across Theta pairs: 3.495E-006` → `PASS -- Theta-invariant within long-rounding tolerance.` | — |
| Actions-only scope | same run | `Actions-only PASS threshold (1e-4, same as core path): PASS (max diff 8.836E-007)` | — |
| Actions+status scope | same run | `Actions+status PASS threshold (1e-4): PASS (max diff 8.836E-007)` | — |
| Every number is under the bound the rows name | arithmetic against `1e-4` | worst scope is **3.495E-006**, i.e. ~29× under the bound (`2.827E-007` and `8.836E-007` are ~354×/~113× under). The tool's own threshold constants are `< 1e-4` at `Program.cs:72,104,160,200` | — |

## Not proved

- **This is the `ProvePredictor` half only.** `CP2` clause 2 and `CP3` clause 3 also require *"dominance
  unchanged"*, which is `dotnet run --project gk-forge/tools/DominanceBaseline` — outside this lane's
  `tools/{CombatSim,ProvePredictor}/**` fence and therefore routed as **`R-DOMINANCE`**, not measured here.
  Neither checkpoint can close on this fragment alone.
- **`ProvePredictor`'s own bound is not re-derived here.** 1e-4 is the tool's authored threshold with its
  own "KEEP THE 1e-4 BOUND" comment (`Program.cs:197-200`, pointing at the status-COMPOSITION layer in
  `gk-core/tools/CombatSim`'s reference); this task measures against it and does not change it.
- **The "twin agrees with the real core policy" clause is CAI2.3's parity test, not this tool's.**
  `ProvePredictor` compares `Core/Balance/Analytic/Predictor` against `gk-core/tools/CombatSim`'s reference
  `Analytic.Predict`; the core-policy parity test is a different assertion and is already landed.
