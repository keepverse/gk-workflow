# `CAI-mask-1` — the row walk's status masks carry their real type, and the repo's last A6 finding goes

Found by `CP1`'s sixth row: `audit-overflow.py` still reported `A6 [MEDIUM] unchecked on a magnitude path`
at `gk-core/src/FusionRpg.Core/Actions/Ai/CoreIntentPolicy.cs:323`. Read rather than worked around — the `unchecked`
is *required* by the code as written, so the fix is the type, not the cast.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The audit finding is gone, at the root | `python gk-core/scripts/audit-overflow.py`; `python gk-core/scripts/audit-overflow.py --targets A6` | `A2=0  A3=0  A4=0  A5=0  A6=0`, **`total 0 finding(s), 0 critical`**, exit 0; `--targets A6` prints nothing. This is the whole-repo total, not just `Actions/Ai/` | — |
| Why the cast existed, and why it is now unnecessary | read of `gk-core/src/FusionRpg.Core/Effects/Atoms/FactReader.cs:43` | `EntityFacts.StatusMask` is **`ulong`**; `AiRowFacts` declared it as `long`, so `CoreIntentPolicy.cs:313`/`:323` reinterpreted it with `unchecked((long)…)`. Both masks are now `ulong` and both casts are gone | `Actions/Ai/AiRowSelector.cs:22-42`, `CoreIntentPolicy.cs:308,313,323` |
| Behaviour is bit-identical, proven over the whole index contract | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~AiRowSelector"` | **7 passed, 0 failed** (5 before, +2 new). `A_mask_with_only_bit_63_set_matches_exactly_that_one_index_across_all_64` walks all 64 indices of a mask with only bit 63 set and asserts exactly one match; `The_status_condition_reads_the_bit_index_the_arg_names_in_either_mask` covers both masks and both set/clear. C# masks a 64-bit shift count by 63, so `1L << i` and `1UL << i` set the same bit for every `i`, and AND-then-`!= 0` cannot differ | `gk-core/tests/FusionRpg.Core.Tests/Actions/Ai/AiRowSelectorTests.cs` |
| The gap this also closes | same run | `HasStatus` and `TargetHasStatus` — two of `AiRowCondition`'s six members — had **no test at all** before this; both are now covered in both directions | — |
| Nothing else moved | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Ai"`; `... --filter "FullyQualifiedName~BattleGolden\|FullyQualifiedName~Dominance\|FullyQualifiedName~ExpeditionResolver"`; `... --filter "FullyQualifiedName~Siege"` | **4617 passed / 0 failed** (was 4615), goldens **16 / 0**, siege **333 / 0** | — |
| The spec quoted the old type | `sed -n '291,294p' docs/architecture/combat-ai/spec-profile-schema.md` | corrected to `ulong SelfStatusMask, ulong TargetStatusMask` in the same commit — the spec's §4 record must not outlive the code it quotes | `docs/architecture/combat-ai/spec-profile-schema.md:293` |
| Nothing was widened to get here | `git diff --stat` | 4 files: two source, one test, one spec. **No** guard, allowlist, exemption marker, `knownRed` entry or registry was touched — the A6 rule's own remedy (\"overflow must throw, not wrap\") is honoured by removing the wrap, not the rule | — |
| Boundary | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/Actions/Ai/AiRowSelector.cs','gk-core/src/FusionRpg.Core/Actions/Ai/CoreIntentPolicy.cs','gk-core/tests/FusionRpg.Core.Tests/Actions/Ai/AiRowSelectorTests.cs','docs/architecture/combat-ai/spec-profile-schema.md') -Session combat-ai-3"` | 13 selected boundaries (incl. `doc-citations` for the spec) → **15114 passed, 0 failed, 0 skipped**, exit 0 | — |

## Not proved

- **`AiRowFacts` is a public record struct and its field *types* changed.** A repo-wide grep
  (`grep -rn --include=*.cs "AiRowFacts" src/ tools/ tests/`) finds **three** files — the declaration, its
  one construction site and its one test — so nothing outside `Actions/Ai/` consumes it. Note the break
  shape if something ever did: `long` → `ulong` has no implicit conversion, so such a caller would fail to
  **compile** rather than silently reinterpret — which is the direction this change wants.
- **The A6 rule's own reading was not changed.** The rule matches a MAGNITUDE word on the same line, so it
  would still fire on a future `unchecked` beside an `Hp` field even where that is correct. This task
  removed the instance, not the class; a `ulong` bitfield on a *magnitudes* line would need the audit side,
  which is not this lane's path.
- **No live probe.** This is a Core type widening whose only observable is the row walk's bit test, which
  the 64-index test covers exhaustively; nothing here needs the game running.
