# SGC-stale-pins-1 — two stale corpus pins, fixed (found while verifying T21/T22's socket scope)

Not a `species-gear-chain` queue row: the two failures surfaced in the socket scope the todo's own
T21/T22 rows own, and `tests/**` is this lane's fence. Both are READINGS of a corpus that deliberately
changed — the corpus change is the design, the pin was the residue.

| Criterion | Command | Executed result | Artifact |
|---|---|---|---|
| Both stale pins reproduce red, before any edit | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~No_shipped_gem_declares_an_omni_affinity\|FullyQualifiedName~Three_shipped_uniques_carry_a_family" -v minimal --nologo` | exit=1 :: `Failed: 2, Passed: 0` — `Expected: ["gem.g1-007"] / Actual: []` and `Expected: 4 / Actual: 0` | tests/FusionRpg.Core.Tests/Items/SocketOperationsTests.cs:329, tests/FusionRpg.Core.Tests/Items/UniqueCorpusTests.cs:520 |
| The contract is asserted, not the corpus reading | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~SocketOperationsTests\|FullyQualifiedName~UniqueCorpusTests" -v minimal --nologo` | exit=0 :: `Passed: 41, Failed: 0` (was 39 passed / 2 failed) | the two files above |
| Scoped Core filter the lane brief names | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Items\|FullyQualifiedName~Stats" -v minimal --nologo` | exit=0 :: `Passed: 1723, Failed: 0` | — |
| Path-owned verification | `.\scripts\verify-change.ps1 -Paths tests/FusionRpg.Core.Tests/Items/SocketOperationsTests.cs,tests/FusionRpg.Core.Tests/Items/UniqueCorpusTests.cs -Session species-gear-chain-20260920` | exit=1 :: `Passed: 14898, Failed: 1` — `FamilyExpansionTests.Committed_generated_files_match_the_generator_byte_for_byte`, a pre-existing stale generated atom tree in unmodified code (already filed at `tasks/atom-family-expansion-todo.md:623`); both touched classes are green in the same run | — |
| `guard-actor-hub.ps1` | `powershell -NoProfile -ExecutionPolicy Bypass -File ./scripts/guard-actor-hub.ps1` | `ACTOR-HUB GUARD OK` | — |

Notes
- The sockwords pin's subject no longer exists: SSH2.6 (`e79c0fde8`) retired
  `data/seed/items/socket-words/sockwords.json`, and the test still read it (FileNotFound). It now
  asserts the retirement — the file's absence plus the migrate ledger record beside it — so a
  resurrected partition is caught; the 2026-09-20 merge did raise exactly that modify/delete conflict.
  Row opened in the owning program's todo: `tasks/strain-splice-host-todo.md`.
- The omni pin and the unique-family pin are the two tests `tasks/item-todo.md:10040` (live-qa lane,
  2026-09-20) asks a `tests/**`-scoped lane to fix. That file is claimed by an ACTIVE session
  (`convergence-resume-20260920`), so its row is NOT ticked here — the orchestrator routes the tick.
- `Three_shipped_uniques_carry_a_family_their_own_frame_cannot_execute` is now
  `No_shipped_unique_carries_a_family_its_own_frame_cannot_execute`: the old name stated a defect the
  regenerated corpus no longer carries. Its `UniqueRules.Shape` detail assertion was vacuous over an
  empty set and is covered by `UniqueTests`' fixtures instead.
- Cause reading (not the symptom): `39fbed34` stopped forwarding an element pick into a gem's
  `affinityElement` (cause 8b/3) and `12175b3d` constrained unique family draws by frame (cause 8b/1);
  both regenerated the corpus and left the two pins behind.
