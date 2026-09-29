# Evidence — the program's own status claims, corrected (map assumptions + dependencies, plan, format §7)

Lane `sim-t3-2`, worktree `D:\Works\source\plant-vs-zombie-rise-of-summoner\.claude\worktrees\cmdc-sim-t3-2`
(branch `cmdc/sim-t3-2`). Three documents carried **live** status claims — not dated history — that the
program's own work had answered, and a reader would trust them as current. Corrected here, each with what
answered it.

| Claim, as written | Now | Evidence |
|---|---|---|
| The map's **"Assumptions — correct these now"** #1: the four-family chain was *not* executed | **RESOLVED, it runs** | RS1's scenario executes it; `RpgSimInProcHostTests`/`RpgSimProcessHostTests` run the corpus on both hosts; the golden pins it; digest identical across fresh hosts and across both hosts (`daa9df408054f32e…`) |
| …#2: the `gk-core/tools/RpgSim` content root was not attempted | **RESOLVED as the fallback the assumption itself predicted** | RS-F6 decided the CLI is a real-process front end and the E2E project hosts in-process; `gk-core/tools/RpgSim/RpgSim.csproj` still carries no reference |
| …#3: canonical-JSON stability across machines is untested | **RESOLVED, and the fear was wrong** | the digest is identical on two fresh hosts and on a real process; the clock is declared (RS3) and the exclusion list has a reason per field |
| …#4: `DataTestStore`'s non-test home | **STILL OPEN** (RS6; premise retired, manager ruling owed) | `gk-core/tools/RpgSim` stayed store-free; RS-F6 kept the CLI a process front end |
| …#5: `/api/sim/effect/*` is gated by `DM-F2` | **RESOLVED, it is gated** | `MapSimEffect()` is inside `if (SimFlags.Enabled)` (`gk-core/src/FusionRpg.Server/Program.cs:2240-2248`); `DM-F2` is ticked |
| The map's **External dependencies** table: three of five rows said "before …" | **two LANDED (DM-F2, the clock's product shape), one OPEN (the `DataTestStore` home), one unchanged (the item-acquisition route), one owed (`docs/README.md`)** | the same citations as above, plus `docs/architecture/rpg-simulator-spec-clock-seam.md` |
| The map's **"NOT proved"** bullets: the clock surface "is not re-measured here" (200-line `grep`, `TimeProvider` = 0) | **measured by the guard instead** | `gk-core/scripts/guard-clock-seam.py`: 1502 files, 21 ambient reads (2 in the clock type, 19 allowlisted), 0 simulation-tree references; `TimeProvider` now appears in `Program.cs`'s composition root |
| The map's bullet that the content root "was not attempted" | **answered by RS-F6; only the `DataTestStore` half remains** | as above |
| The plan's §1: **"what is not true — the work this plan exists for"** listed eight items | **five are done (the tool, the format + corpus, the verdict/digest contract, the honesty guard, the `ForceExpeditionDue` retirement), `DM-F2` landed, and two remain (`DataTestStore`, `docs/README.md`)** | the paragraph now strikes each answered item and names what answered it, keeping the original text visible |
| `gk-core/tools/RpgSim/scenario-format.md` §7: "the shipped slice-0 fixture is still in RS1's original shape" and "no CI wiring" | **both corrected** — the corpus is migrated and the format's contract test validates every file; the scenarios ARE in CI through the E2E project (`ci.yml:333` with an exit check, and `ci.yml:352-368` asserts CI stays unfiltered), while the CLI itself is still not invoked (RS7's one literal gap) | `gk-core/tools/RpgSim/scenario-format.md` §7 |

| Criterion | Command | Result |
|---|---|---|
| Every citation in the corrected documents resolves | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/guard-doc-citations.ps1 -Strict` | exit **0** with no HIGH (`D1 683 / 0 HIGH`, `D2 7 / 0 HIGH`, `D3 56 / 0 HIGH`) |
| Nothing else regressed | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/run-guards.ps1 -Tier ci` | exit **0** — `GUARDS OK - 25 guard(s) run, 0 red` |

**Why this is worth a commit rather than a note.** Two of the three documents are the program's *index* (the map)
and its *plan*: a lane starting from them would re-derive work that is done — the failure the RS-F9 erratum cost
the manager a ruling over, and the reason this lane re-measures a row before trusting its summary. A claim headed
"correct these now" that is three-quarters answered is the same hazard in the same place.
