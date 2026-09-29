# Evidence — the narrative registry reader reconciled with the authored corpus (NR1.5's second attempt)

Lane `npc-story-events-2`, worktree `.claude/worktrees/cmdc-npc-story-events-2`, branch `cmdc/npc-story-events-2`.
Found by NR1.5's real-corpus boot read: the runtime reader had been written from the specs and its own fixtures,
while `gk-data/packs/fusion/data/seed/narrative/_registry/**` was authored by narrative-seed's adapter from the same specs — and the two
disagree in five places. Every one is a place where the CORPUS follows narrative-seed's own spec and the reader did
not, so the reader was the side to move. Each case is now pinned by a test in
`gk-core/tests/FusionRpg.Core.Tests/Narrative/Vocabulary/RegistryReconciliationTests.cs`.

| Divergence | Seed-side authority | What the reader does now |
|---|---|---|
| the vocabulary is an ARRAY of rows carrying `id`, not a keyed object | `spec-storylet-vocab.md` §2 specifies the keyed object, but the adapter emitted arrays into 8 of the 9 files (`choice-kinds`, `choice-patterns`, `conditions`, `consequence-kinds`, `host-kinds`, `line-contexts`, `roles`, `teaches`, `voices`) | `NarrativeRegistryJson.Rows` reads either shape; an array row's `id` is stripped before the row reaches a catalog, so every catalog's own key check is unchanged. A row with no `id`, or a file that is neither shape, still refuses |
| `roomKind: "none"` on a non-Delve host | §3.1: "`roomKind` is `none` on every non-Delve row" — the corpus writes the word | the sentinel is normalised to null (`HostKindCatalog.NormaliseSentinel`), so a Delve host still must name a real room kind and a consumer sees absence |
| an empty `climates` list | §3.1: "an empty `climates` (`world.anomaly`) means the host fires nowhere today and the planner declares no cell for it" | legal; the reader no longer refuses it (this rule had been over-tightened on this side) |
| the condition's compiled leaf key is `compilesTo` | §3.4's own table column is `compilesTo`; the reader expected `leaf` | both spellings are read; the corpus's wins where both appear |
| the "no leaf" value is the word `nothing` | §3.4: the `none` row's `compilesTo` is `nothing` | `nothing` (like `none`) is normalised to null |

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Each divergence is pinned | `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release --nologo --verbosity quiet --filter "FullyQualifiedName~RegistryReconciliationTests"` | `Failed: 0, Passed: 5, Total: 5` (24 ms) — array-vs-keyed reads the same rows; an array row with no `id` refuses; both sentinel words read as absence; both leaf spellings read the same value; an empty `climates` validates | `gk-core/tests/FusionRpg.Core.Tests/Narrative/Vocabulary/RegistryReconciliationTests.cs` |
| No regression in the module | `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release --nologo --verbosity quiet --filter "VerificationId=core.narrative"` | `Failed: 0, Passed: 130, Total: 130` (547 ms) | — |
| Path-owned verification | `pwsh … scripts/verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/Narrative/Vocabulary/StoryletRegistries.cs','gk-core/tests/FusionRpg.Core.Tests/Narrative/Vocabulary/RegistryReconciliationTests.cs') -AllowUnscoped` | exit 0 — both paths `core-narrative (focused)`, `test: core core.narrative`, **135 passed, 0 failed** | — |
| The guard still holds | `python gk-core/scripts/guard-narrative.py` | `NARRATIVE GUARD OK - 6 row(s) guarded by 'narrative', 6 mapped` | — |

**Still blocked, and by exactly one corpus value now.** The boot read
(`NarrativeRegistryHub.Configure(<the real registry dir>)`) proceeds past all five divergences above and stops at:
`conditions.v1.json: role-cast.leaf 'role requirement: resolved by casting' must start with an upper-case letter (a
LeafId member name)`. The corpus's `role-cast` row carries §3.4's own PROSE cell ("a role requirement, resolved by
casting") in the `compilesTo` column, whose other seven rows hold either a leaf name (`BandIs`,
`RelationBandAtMost`, `CharacterStateIs`, `StoryFlagSet`, `LeadLevelAtLeast`, `DoctrineStudying`) or the sentinel
`nothing` — and whose own negative clause says "not a leaf; casting decides it before eligibility is evaluated". So
the field needs `nothing` (or the spec's cell needs rewording), which is a corpus edit on narrative-seed's side:
the rows' prose is model-authored, so "fix the generator and regenerate" is re-authoring, and **no session record
exists for a narrative-seed lane** — the program is unowned right now. The reader must NOT be made to swallow
arbitrary prose in a leaf column: that would turn a mistyped leaf name into a silent "no leaf", the exact
silently-softer failure this repo forbids.

**NOT proved.** The NR1.5 boot wiring itself (`Program.cs` + `tests/FusionRpg.Server.Tests/Narrative/NarrativeBootTests.cs`)
was written, run against the real corpus (which is how these five divergences and the sixth were measured), and then
REMOVED rather than committed red: a boot test that cannot pass is not evidence, and the wiring lands in the commit
that follows the corpus's `role-cast` fix. The row stays open on that, named above.

## Second pass — two more alignments, and the field-level blocker that ends the tolerance

| Divergence | Seed-side authority | What the reader does now |
|---|---|---|
| the condition's "casting resolves this" marker | `gk-forge/tools/seedsmith/seedsmith/adapters/narrative/storylet_vocab.py:309-310` skips a `compilesTo` starting with `role requirement` ("casting resolves a role requirement"; its test at `test_narrative_storylet_vocab.py:193-194` does the same) | read as ABSENCE, and only that prefix — any other text in the column still refuses, so a mistyped leaf name cannot become a silent "no leaf" |
| `role-tags.v1.json` is FLAT at the root (`roleKinds`, `requireFamilies`, `requirementShape` — spec §3.6) and its `roleKinds` is an ARRAY | spec-storylet-vocab.md §3.6 | the catalog reads the root or the fixtures' `roleTags` wrapper, and accepts an object or an array for either block; `requirementShape` is read and not consumed (the value grammar is enforced by the id checks) |

Readings: `RegistryReconciliationTests` 7/7, the whole `core.narrative` selector **137/137** (355 ms).

**The next divergence is NOT a spelling, so the reconciliation stops here.** `teaches.v1.json`'s rows are built to the
seed side's field set — `value` as the identifier, `loop`, `carriers`, `requires` as a single STRING ("host
`expedition.return`"), `teachingLine`, `negative` — while the runtime reader wants `id`, `description`, `negative`, and
a `requires` LIST. That is a field-set contract difference between two programs (which side's field set is the
contract, and whether `teachingLine` is the runtime's `description`), not something a tolerance can settle: guessing it
would invent a mapping nobody reviewed, and the seed side's own test asserts `requires` is one string shape
(`test_requires_is_one_string_shape`). NR1.5 therefore waits on that decision; the boot wiring and its Server test stay
written-but-uncommitted until the corpus reads end to end.
