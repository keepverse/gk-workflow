# debug-mcp: dll-freshness false FAIL from `obj/` build output

Defect found while running the lane's own preflight (`gk-fusion/tools/debug-mcp/tools/debug_preflight.py:141`).
Cause read in the code, not guessed: `_newest` globbed `gk-core/src/FusionRpg.Core/**/*.cs` (and Contracts),
which matches `obj/Debug/net6.0/*.AssemblyInfo.cs` — regenerated with a fresh mtime by **every**
local build. `_dll_freshness` then compared the published `dist/.../FusionRpg.Core.dll` against that
generated file and reported a genuinely newer DLL as stale, exactly when preflight is run (after a
build). Build output is not source.

| Criterion | Command | Executed result |
|---|---|---|
| Failing evidence (before) | `python gk-fusion/tools/debug-mcp/cli.py debug_preflight --json '{}'` | `dll-freshness FAIL FusionRpg.Core.dll older than .../src/FusionRpg.Core/obj/Debug/net6.0/FusionRpg.Core.AssemblyInfo.cs` (mtime 20:11 vs DLL 20:08) |
| Fix | skip any path containing `obj`/`bin` in `_newest`, with the reason in the docstring | `gk-fusion/tools/debug-mcp/tools/debug_preflight.py` |
| Regression tests | `cd gk-fusion/tools/debug-mcp; PYTHONPATH=. python -m pytest tests/test_debug_preflight.py -q` | `13 passed` (2 new: build output ignored; real newer source still FAILs) |
| Passing evidence (after) | `python gk-fusion/tools/debug-mcp/cli.py debug_preflight --json '{}'` | `dll-freshness PASS FusionRpg.Core.dll newer than newest src`; all 7 checks PASS |

Falsified by: a genuine source edit newer than the published DLL still passing (covered by the second
new test, which asserts FAIL).
