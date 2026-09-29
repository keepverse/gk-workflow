# `CAI-perf-1` — the `PerfSection` residue landed (remedy (a))

Lane `cai2` (session `combat-ai-2b`), 2026-09-23. The row was blocked on "a fence or an erratum":
`Core/Diagnostics/**` was outside every combat-ai lane's fence, so a lane taking `CAI4.7` and adding only
`LawnAiDecide` would have landed it at 25 with `SectionCount = 26` and made `CAI4.7`'s own acceptance
unreachable. `gk-core/src/FusionRpg.Core/Diagnostics/**` **is** in this lane's fence, so **remedy (a)** was taken:
the residue landed, and `CAI4.7`'s `26`/`27` are now reachable exactly as written — no erratum needed.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `PerfSection` carries CAI1.14's residue **and** CAI4.7's line, in index order | `grep -n "AiDecide\|LawnAiDecide\|SectionCount\|ai.decide" gk-core/src/FusionRpg.Core/Diagnostics/PerfProbe.cs` | `AiDecide = 25`, `LawnAiDecide = 26`, `const int SectionCount = 27`, and `"ai.decide"`/`"lawn.ai.decide"` appended to `SectionNames` in the same order | `gk-core/src/FusionRpg.Core/Diagnostics/PerfProbe.cs` |
| The "must match PerfSection's member count" comment is **enforced**, not asserted | `dotnet test gk-core/tests/FusionRpg.Core.Diagnostics.Tests --filter "FullyQualifiedName~PerfSections_match"` | **1 passed / 0 failed** — `PerfSections_match_the_enum_the_names_and_this_bound` records every member once, then asserts the snapshot holds exactly one name per member (a member past the bound is dropped silently by `PerfProbe.Measure`) and names `ai.decide`/`lawn.ai.decide` explicitly | `gk-core/tests/FusionRpg.Core.Diagnostics.Tests/Diagnostics/PerfProbeTests.cs` |
| The test has teeth (planted violation) | revert `SectionCount` to 25, re-run, restore | **1 failed / 0 passed** with `SectionCount = 25`; **1 passed / 0 failed** after restoring — the mutation file is byte-identical again (`git diff --stat` shows only the intended 19-line `PerfProbe.cs` edit) | — |
| The project as a whole | `dotnet test gk-core/tests/FusionRpg.Core.Diagnostics.Tests` | **18 passed / 0 failed** | — |

## Why the pin is a contract, not a population count

`PerfSection` is a **closed vocabulary this code owns** — the enum, the `SectionNames` array and the
structural `SectionCount` bound must describe the same set, and `Measure` silently drops anything at or past
the bound. That is the shape `validation-ssot.md` allows a literal for. What the test does **not** do is
assert any count as a content reading: it derives the expected size from `Enum.GetValues<PerfSection>()`, so
a future member added with its name passes and a member added without one fails.

## What this unblocks, and what it does not

- `CAI4.7`'s `PerfSection` acceptance line is met. Its remaining lines are the Injector frame slot
  (`CAI4.8`) and `data/tuning/combat-ai.v3.json`'s lawn section — whose H7 blocker the row recorded **no
  longer applies to this lane** (it holds `gk-core/data/tuning/**`, `Server/Program.cs` and
  `Injector/Host/RpgHost.cs`, so one commit can publish and switch both readers). What is still external
  there is the lawn plan's `lawn-perf-budget.v1.json` (`LW1.1`, measured absent), which the lawn's own
  numbers come from.
- The section is a **section**, not a producer: nothing emits into `ai.decide` or `lawn.ai.decide` yet
  (CAI1.14's caller and CAI4.8's frame slot respectively). `CAI-perf-1`'s own subject was the index
  collision, and that is what is fixed.
