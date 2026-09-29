# TVB5.7 — the split tool's own writes were not editorconfig-clean

Found by running the first real increment (`split … --apply`) and reading what the tool actually wrote.
None of it breaks a build, which is exactly why it would have survived 68 increments: the residual
csproj and `FusionRpg.slnx` are the two files every increment touches, and each defect compounds.

| Defect (read off the first apply's diff) | Cause in `gk-core/tools/FileMove/SplitPlanner.cs` | Fix |
|---|---|---|
| 3 whitespace-only lines where the moved `<PackageReference>`s were | `PackageReference.Replace(text, "")` removed the element, not its line | new `PackageReferenceLine` (line-scoped, multiline) eats indent + newline; `BuildSharedProps` keeps the bare-tag regex |
| a CR at the end of the **LF** residual csproj's `<Project>` line | `text.Insert(open.Index + open.Length, "\r\n" + importLine)` hard-coded CRLF into a file it did not create | `Newline(text)` — the newline the file already uses |
| `FusionRpg.slnx`'s new `<Project …>` line indented 6 spaces where its siblings use 4, with a CRLF in an `eol=lf` repo | `entry + "\r\n  "` inserted AT `</Folder>`, so the close tag's own indent stayed in front of the entry | insert a whole line before the `</Folder>` line, indented one level deeper than that line, with the file's own newline |

| Criterion | Command | Result |
|---|---|---|
| The two hygiene properties are asserted, not seen once | `dotnet test gk-core/tests/FusionRpg.FileMove.Tests/FusionRpg.FileMove.Tests.csproj -c Release --filter "FullyQualifiedName~The_splits_own_writes_keep_the_files_newline_and_leave_no_whitespace_only_line"` | 1 passed |
| Nothing else regressed in the tool | `dotnet test gk-core/tests/FusionRpg.FileMove.Tests/FusionRpg.FileMove.Tests.csproj -c Release` | **40 passed / 0 failed**, 6s |
| Path-owned verification | `.\scripts\verify-change.ps1 -Paths gk-core/tools/FileMove/SplitPlanner.cs,gk-core/tests/FusionRpg.FileMove.Tests/SplitPlannerTests.cs -Session tvb58` | exit 0; `filemove-fallback` module run **40/40**; `test-substrate` guard OK |

Re-proved on the real tree immediately after: the second `--apply` (TVB5.7's own increment) wrote a
residual csproj with no whitespace-only line and an slnx entry at 4 spaces.
