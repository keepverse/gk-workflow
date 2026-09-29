# `CAI-perf-1` — CAI4.7's `PerfSection` index presupposes a residue that has not landed

Found by reading `gk-core/src/FusionRpg.Core/Diagnostics/PerfProbe.cs` at the merged head `cb1405011` while
looking for in-fence work, because two rows in this todo assert specific indexes into it.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The file's actual state | `sed -n '6,52p' gk-core/src/FusionRpg.Core/Diagnostics/PerfProbe.cs` | the enum runs `LoopTick = 0` … `LawnMoveDrain = 24` — **25 members**, 0..24, with `const int SectionCount = 25` at `:51` and its own comment *"must match PerfSection's member count above, not balance"* | — |
| Neither AI section exists | `grep -n "AiDecide\|LawnAiDecide\|ai.decide\|lawn.ai.decide" gk-core/src/FusionRpg.Core/Diagnostics/PerfProbe.cs` | **NONE** — no member, and no such report key anywhere in the file | — |
| What the two rows assume | read of this todo | `CAI1.14`'s filed residue: *"`PerfSection.AiDecide = 25`, `SectionCount = 26` and the `"ai.decide"` name … filed in `tasks/combat-ai-todo.md`"*. `CAI4.7`'s acceptance: *"**`PerfSection.LawnAiDecide = 26`, `SectionCount = 27`, `"lawn.ai.decide"`** — CAI1.14 took 25 (plan correction 1)"* | `tasks/combat-ai-todo.md` |
| The hazard, stated exactly | arithmetic on the two rows against the measured file | `CAI4.7`'s `26` is only reachable if `CAI1.14`'s `AiDecide = 25` lands **first**. It has not, and its file (`gk-core/src/FusionRpg.Core/Diagnostics/**`) is outside every combat-ai lane's fence. A lane that takes `CAI4.7` and adds only `LawnAiDecide` lands it at **25** with `SectionCount = 26` — so its own acceptance line becomes unreachable and the closure would be a wrong number rather than a failing test | — |
| The stale citation in the deferred entry, corrected here | `grep -n "LawnMoveDrain" gk-core/src/FusionRpg.Core/Diagnostics/PerfProbe.cs` | the entry says *"`PerfProbe.cs:36` ends at `LawnMoveDrain = 24` today"*; it is at **`:40`** now (`:36` is inside the `KernelSchedule` comment block). Corrected in this commit. The entry's **index** claim (25) and count claim (26) are right; only the line number moved | `tasks/combat-ai-todo.md` |

## Two remedies, and the row is filed under both

1. **A lane lands `CAI1.14`'s residue first** — it needs `gk-core/src/FusionRpg.Core/Diagnostics/PerfProbe.cs`
   (plus, per that entry, the channel-id interning in `gk-core/src/FusionRpg.Core/Stats/Derived/DerivedStatChannels.cs`).
   Then `CAI4.7`'s `26`/`27` are reachable as written and land after it.
2. **An erratum restates `CAI4.7`'s acceptance** to whatever `PerfSection` actually reads when it lands
   (today that would be `LawnAiDecide = 25`, `SectionCount = 26`), the same way `PerfSection` index
   collisions were already ruled on once (the plan's "Correction 1").

Either is a manager call. What is **not** acceptable is a lane discovering this inside `CAI4.7`'s
commit — that is precisely the "one cause per commit" rule the program's hard edge H1 protects.

## Not proved

- **`CAI1.14`'s residue is not landed, and this task did not land it** — `gk-core/src/FusionRpg.Core/Diagnostics/**`
  is outside this lane's fence. The row is filed, not executed.
- **No consumer of `"ai.decide"` / `"lawn.ai.decide"` was searched for.** The claim here is about the
  enum's index and `SectionCount`, which is what the two acceptance lines name; whether a report reader
  keys on those strings is a separate question for whoever lands them.
- **Nothing was changed in `PerfProbe.cs`.** This is a measurement plus a one-line citation correction in
  the todo.
