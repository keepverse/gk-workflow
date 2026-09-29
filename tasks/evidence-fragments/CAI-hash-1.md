# `CAI-hash-1` — the `TableDigests` rename's precondition is met; routed to its owning program

Routed, not attempted: the file is outside this lane's fence. The deliverable is the row in the owning
program's todo plus the measurement that makes its precondition true.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The deferral's own condition is met | `sed -n '318,324p' docs/architecture/combat-ai/spec-replay-identity.md` | that Open question rules the rename out "**now**" and says to *"revisit (b) as its own cosmetic change **once a second non-table consumer exists**"*. Reading the two callers: the second consumer exists — `CombatAiProfileIdentity.StampOf` keys the map by **profile id**, not table name | `spec-replay-identity.md:318-324` |
| …measured, not asserted | `sed -n '48,67p' gk-core/src/FusionRpg.Core/Actions/Ai/CombatAiProfileIdentity.cs` | `digests[pair.Key] = ContentHash.Hex(...)` where `pair.Key` iterates `tuning.Profiles` — keys like `"siege/default"` — then `new ContentHashStamp(tuning.Version, …, digests)`. So `TableDigests` holds profile-part digests for this caller and table digests for `RpgStore.ContentHash.cs` | `Actions/Ai/CombatAiProfileIdentity.cs:48-67`, `Effects/Atoms/ContentHashStamp.cs:16-19` |
| The owning program is identified, not guessed | `grep -rn "Atoms/ContentHashStamp" docs/architecture/` | `docs/architecture/effect-atom/spec-content-hash.md:96` names the file as `effect-atom`'s ("the stamp + the replay verdict") — so the row went to `tasks/effect-atom-todo.md`, not to this program's | `tasks/effect-atom-todo.md` §"Findings routed from `combat-ai`" |
| The row carries the decision, not a mandate | read of the file it lands in | the spec offers (a) reuse as-is, (b) rename with `TableDigests` kept as an obsolete alias, (c) fork — and rules (c) out. The row asks for the **revisit**, and states the acceptance only for the shape the spec already names | — |
| It is genuinely out of this lane | fence check | `gk-core/src/FusionRpg.Core/Effects/Atoms/ContentHashStamp.cs` is under `Core/Effects/**`, which this lane's allowed paths (`Core/{Actions,Battle,Balance,Delve}/**`) do not include — and the Data consumer (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.ContentHash.cs`) is out too | — |

## Not proved

- **Nothing was renamed.** The row is the deliverable; the rename belongs to the file's owner, and the spec
  explicitly wants it as its own single-cause change rather than folded into another commit.
- **The wire-format claim in the row's acceptance is the spec's, not a measurement of mine.** I read
  `ToCompact`/`TryParse`'s key handling but did not exercise a round-trip across a rename, because the
  rename is not mine to make. The row says what the owner must keep true, and its own Verify line names the
  tests that would catch it.
- **Whether `effect-atom` currently has an open wave that would carry this is not checked.** The row is
  filed in that program's todo as a routed finding; where it sits in that program's order is its owner's
  call.
