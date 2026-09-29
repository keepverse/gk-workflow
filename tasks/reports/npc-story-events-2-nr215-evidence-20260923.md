# Evidence — npc-story-events NR2.15 (token grammar, binder, the one wire text shape)

Lane `npc-story-events-2`, worktree `.claude/worktrees/cmdc-npc-story-events-2`, branch `cmdc/npc-story-events-2`
(integration head merged). Program `npc-story-events`; row `tasks/npc-story-events-todo.md` NR2.15; spec
`docs/architecture/npc-story-events/spec-narrative-text.md` §1–§3 (read this session). C# half only — the web
half is NR2.16/NR2.17 and `web/**` is outside this lane's fence.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Every refusal carries its rule id | `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release --nologo --verbosity quiet --filter "FullyQualifiedName~Narrative.Text"` | `Failed: 0, Passed: 23, Total: 23` (92 ms) — 12 theory cases, one per refusal: stray brace (×2 incidences), unknown token (×3), `role-undeclared`, `character-unknown`, unknown markup, unbalanced markup (×3), `digit-in-text` | `gk-core/src/FusionRpg.Core/Narrative/Text/TokenGrammar.cs` |
| The whole closed grammar validates clean | same run (`The_whole_closed_grammar_validates_clean`) | pass — leads with suffixes, a character epithet, a role, all four placeholders and `<em>/<whisper>/<pause/>` in one fixture | same |
| Every token in a fixture storylet binds from a fixture cast, or binding fails naming it | same run (`Every_token_...`, `An_unbound_token_fails_naming_it`) | pass — the key set equals the five authored tokens; an unbound `c_nightshade` throws naming the token and the field key | `gk-core/src/FusionRpg.Core/Narrative/Text/StoryTextBinder.cs` |
| `role_<id>` resolves through the cast | same run (`A_role_token_binds_to_what_the_role_was_cast_to_not_to_the_role_id`) | pass — the DTO carries what the role was cast to (`character` / `creature.rotwright`), never the role id | same |
| A magnitude carries `long` | same run (`A_magnitude_carries_long`) | pass — `5_000_000_000` survives and `TokenRefDto.Amount` asserts `long?` | `gk-core/src/FusionRpg.Contracts/NarrativeTextDtos.cs` |
| No display string crosses the wire | same run (`The_wire_types_carry_no_display_string`, `Only_one_contracts_type_carries_a_text_key_and_a_token_map`) | pass — no `Display`/`Name`/`Label` member on either type, and reflection over the Contracts assembly finds exactly `NarrativeTextDto` carrying a string `Key` plus a `TokenRefDto` map | same |
| The registry row and the guard's map line land together | `python gk-core/scripts/guard-narrative.py` | `NARRATIVE GUARD OK - 4 row(s) guarded by 'narrative', 4 mapped` | `gk-core/scripts/enforcement-registry.v1.json` (`ns-one-narrative-text-dto`), `gk-core/scripts/guard-narrative.py` |
| The trait filter really selects the new tests | `pwsh … gk-core/scripts/guard-narrative.py -RunTraitFilter` | `FusionRpg.Core.Tests -> Guard=narrative selected 53 test(s), 0 failed` (30 before this row); `FusionRpg.Guard.Tests -> selected 5 test(s), 0 failed` | same |
| The enforcement registry still holds | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~EnforcementRegistryGuardTests"` and `pwsh … gk-core/scripts/guard-verification-boundaries.py` | `Failed: 0, Passed: 18, Total: 18`; `VERIFICATION BOUNDARY GUARD OK` (re-run after the registry rewrite, 436 rows) | — |
| Path-owned verification | `pwsh … scripts/verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/Narrative/Text/TokenGrammar.cs','gk-core/src/FusionRpg.Core/Narrative/Text/StoryTextBinder.cs','gk-core/src/FusionRpg.Contracts/NarrativeTextDtos.cs','gk-core/tests/FusionRpg.Core.Tests/Narrative/Text/NarrativeTextTests.cs','gk-core/scripts/enforcement-registry.v1.json') -AllowUnscoped` | exit 0 — **70 project runs, passed=15966, failed=0**; plan: `core-narrative (focused)` ×3 + `core core.narrative`, `contracts-narrative (module)`, `enforcement-registry (focused)` | — |
| No overflow in the new types | `python gk-core/scripts/audit-overflow.py` | `total 0 finding(s), 0 critical` | — |

**Two real defects the refusal tests caught while implementing** (recorded because they are why the tests exist):
`Groups["close"].Success` / `Groups["self"].Success` are TRUE for `<em>` as well — an optional regex group that
matched the empty string still reports `Success` — so every tag looked self-closing and every unbalanced-markup case
returned an EMPTY issue list. Three of the twelve refusal cases failed on that; the marker is now tested by its value
(`Groups["close"].Value.Length > 0`).

**NOT proved / named deviations.**

- **Only the C# half of this module.** The codegen bridge, the second lingui catalog, `namesRegistry.ts`,
  `renderNarrative.tsx` and the two-locale render tests are NR2.16/NR2.17, and `web/**` has no entry in
  `gk-core/scripts/verification-boundaries.v1.json` and is outside this lane's allowed paths (the spec says so itself:
  web verification is the npm commands until a web boundary exists).
- **The `>Number.MAX_SAFE_INTEGER` boundary is not tested here.** The spec's numeric section defers the serializer
  setting to the build task; this row proves `Amount` is `long?` and carries a value beyond `int.MaxValue`.
- **The row's own Verify line is run renamed**: `-Session <sid>` cannot resolve in this lane (no session record;
  `tasks/sessions/**` is outside its allowed paths), so it passes `-AllowUnscoped`.
- The `contracts-narrative` boundary is `level: module` (NR0.2's row, the `notify-contracts` precedent), so the
  Contracts DTO still pulls the whole `core` project group into the plan; that is the registry's shape, not this row's.
