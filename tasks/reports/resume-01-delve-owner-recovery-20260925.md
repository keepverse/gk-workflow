# Delve owner recovery — final report

**Status:** `partial` — the scoped server-owned join contract is implemented and the three focused projects are green; the bounded all-path verifier timed out without a verdict, and the permanent multi-party steering ruling is still an owner decision. No live probe was run.
**Session:** `resume-01-delve-owner-recovery-20260925`
**Branch:** `opencode/resume-01-delve-owner-recovery-20260925`
**HEAD:** `cfaf03553aa6295672307a75fede6a8e67def1cd`
**Worktree:** `D:/Works/source/plant-vs-zombie-rise-of-summoner/.claude/worktrees/opencode-resume-01-delve-owner-recovery-20260925`
**Boundary:** the seven paths in the recovery brief are the only paths in this lane. The worktree is intentionally left dirty. No commit, push, merge, process kill, or external-directory investigation was performed.

## Recovery result

The stopped draft's actual six-file diff was reviewed rather than reset. The confirmed P1 is closed at the scoped seam:

- `talk` and `cage` no longer accept a caller species, price, or sink as an input to the transaction. The compatibility DTO fields remain on the wire, but the handler ignores them.
- The effective room kind is `ResolvedKind ?? Kind` in both the HTTP precheck and the Data transaction. A persisted `cage` marker is required for `/cage`; a rolled `fight`/other room cannot be joined through either route.
- The Data transaction resolves the selected party against the persisted delve world: it must be a configured party index, a `Warband` owned by the sole player faction, and standing in the requested room. The HTTP check is an early refusal; the same persisted-world check runs inside the write transaction.
- The candidate, traits, offer floor, and mint fields are resolved on the server. The selected candidate is drawn from the configured catalog and the sealed delve seed; `OfferFloor` uses the configured altar banner, the dungeon offer multiplier, the persisted `ThetaRun` watermark, and power tuning.
- A malformed/blank effective persisted archetype refuses instead of falling back to a caller value. The effective `ResolvedArchetypeId ?? ArchetypeId` is passed into the resolver; the candidate draw itself remains on the canonical reserved stream `DelveStreams.Wild(row, col, "seq")`, as required by the wild-room determinism contract. Full archetype-specific encounter pools are not silently invented in this join-only recovery.
- The production steering policy is explicit and fail-closed: selector `0` is admitted, selectors other than `0` return `wild.party-not-steered` until a persisted/live steering signal exists. This is documented as temporary, not as a permanent multi-party ruling.

The altar route remains separate. Its existing caller-supplied `ThetaRoom` and banner seam was not changed, as required by the brief; this report makes no claim that `/pray` received a room-local theta redesign.

## Source reasoning and implementation map

- `docs/architecture/party-dungeon/spec-wild-room.md:17-31,111-125,135-153,213-223,243-250` defines the wild/cage join, at-risk souls sink, catalog admission, and reserved deterministic streams. The implementation follows those boundaries rather than treating an HTTP body as the resolver.
- `docs/architecture/party-dungeon-map.md:110-129` places `wild-room` in the party-dungeon program and identifies the Server/Data/Core ownership split. No economy redesign or separate candidate composer was added.
- `docs/architecture/data-architecture.md:157-163` requires SQL to remain in `FusionRpg.Data`; the new world/party validation is in `RpgStore.Delve.cs`, while the Server contains only HTTP orchestration.
- `tasks/reports/mega-merge-deep-audit-20260924.md:48-52,111-114` records the confirmed caller-controlled Delve finding and the required server-owned candidate/party/price correction.

### Changed production paths

1. **`gk-core/src/FusionRpg.Server/DelveWildEndpoints.cs`**
   - `/talk` and `/cage` now route through a server-resolved join path; `/cage` explicitly carries the cage action flag.
   - `ValidateRoom` validates the effective persisted kind before any write, performs the steering refusal, and performs the persisted party/location precheck.
   - `Spec`, `Price`, and `SinkKey` remain compatibility properties only. No body field is passed to `TalkJoin` as candidate/price/sink authority.
   - `ProductionIsPartySteered` is explicit and fail-closed rather than an accidental always-true placeholder.
   - `pray` retains its previous altar behavior and caller theta seam.

2. **`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Delve.cs`**
   - `TalkJoin` now takes `delveId`, `playerId`, `partyEntityId`, `sectorId`, and `cage`; the old caller `price`, `sinkKey`, and `CreatureMintSpec` seam is gone.
   - The transaction checks player/delve ownership, active state, persisted room, effective kind/cage state, configured party shape, and the persisted world party before spending.
   - It resolves the effective archetype, server candidate, traits, and `OfferFloor`, derives the sink from persisted coordinates, spends, mints, and applies the existing discovery award in one transaction.
   - The public `IsPartyAtRoom` precheck is intentionally non-authoritative; the same check is repeated inside `TalkJoin` under the store transaction.

3. **`gk-core/src/FusionRpg.Core/Delve/Loot/DelvePrices.cs`**
   - `DelveWildJoinResolver` and `DelveWildJoinResolution` provide the server-owned candidate/price result.
   - The resolver uses configured summoning/dungeon/power catalogs, rejects capture-only/event-only/excluded/top-rung candidates through the existing admission/cage gates, and returns named refusals.
   - Traits use `SummonRoller.RollTraits`; the candidate and trait draws use the sealed seed and the reserved Delve streams.
   - `OfferFloor` is called through the existing `DelvePrices` arithmetic; no balance number was added to code or generated data.

### Focused regression coverage

- **`gk-core/tests/FusionRpg.Core.Tests/Delve/Loot/DelvePricesTests.cs`** — deterministic candidate/price resolution, catalog/rank gate, null-tuning refusal, and existing price formulas.
- **`gk-core/tests/FusionRpg.Data.Tests/Delve/DelveWildTransactionTests.cs`** — successful server-resolved mint, server floor shortfall, wrong room, wrong party, cage marker, discovery deduplication, refusal side-effect checks, and existing altar transaction coverage.
- **`gk-core/tests/FusionRpg.Server.Tests/DelveWildEndpointsTests.cs`** — caller `Price = 1`, missing/hostile compatibility fields, malicious species substitution, server price/species read-back, wrong room/party/cage, refusal balance/roster invariants, and the explicit temporary steering policy.

## Verification evidence

All commands below were run in this worktree. The focused projects were run one at a time, as required by the recovery brief.

```text
python scripts/session-boundary-check.py --session resume-01-delve-owner-recovery-20260925
exit 0; [session-boundary] clean for 'resume-01-delve-owner-recovery-20260925'
```

```text
dotnet test gk-core/tests/FusionRpg.Core.Tests --no-restore --filter "FullyQualifiedName~DelvePricesTests" --logger "console;verbosity=normal"
exit 0; Test Run Successful; Total tests: 22; Passed: 22
```

```text
dotnet test gk-core/tests/FusionRpg.Data.Tests --no-restore --filter "FullyQualifiedName~DelveWildTransactionTests" --logger "console;verbosity=normal"
exit 0; Test Run Successful; Total tests: 18; Passed: 18
```

```text
dotnet test gk-core/tests/FusionRpg.Server.Tests --no-restore --filter "FullyQualifiedName~DelveWildEndpointsTests" --logger "console;verbosity=normal"
exit 0; Test Run Successful; Total tests: 18; Passed: 18
```

```text
git diff --check
exit 0; no whitespace errors
```

```text
.\\scripts\\guard-dal.ps1
exit 0; DAL GUARD OK — no SQLite/SQL outside FusionRpg.Data
```

The required concrete-path verification was attempted with every executable path and the active session id:

```powershell
$changed = @(
  'gk-core/src/FusionRpg.Server/DelveWildEndpoints.cs',
  'gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Delve.cs',
  'gk-core/src/FusionRpg.Core/Delve/Loot/DelvePrices.cs',
  'gk-core/tests/FusionRpg.Server.Tests/DelveWildEndpointsTests.cs',
  'gk-core/tests/FusionRpg.Core.Tests/Delve/Loot/DelvePricesTests.cs',
  'gk-core/tests/FusionRpg.Data.Tests/Delve/DelveWildTransactionTests.cs'
)
.\scripts\verify-change.ps1 -Paths $changed -Session resume-01-delve-owner-recovery-20260925
```

That bounded command exceeded the 300-second tool timeout after starting the split Core projects. It produced no final pass/fail verdict, so it is **not** reported as passed. No lock investigation or unrelated process handling was attempted.

## Limitations and open owner questions

1. **Multi-party steering is unresolved by design.** There is no persisted currently-steered-party signal for these pre-room actions. The temporary policy admits selector `0` and fails closed for other selectors. The owner must choose the durable/live steering source and semantics for `duo`/`quad` raids before this is treated as a final policy.
2. **Room theta is still a schema gap.** Join pricing uses the persisted `ThetaRun` watermark because `rpg_delve_rooms` has no room-local theta column. Replacing that watermark with a persisted room theta is a separate contract change; `/pray` still has its pre-existing caller theta seam.
3. **Archetype content is not expanded here.** The effective persisted archetype is validated and passed into the join resolver, while the candidate draw uses the canonical coordinate stream. If the owner requires archetype-specific encounter pools/disposition content to determine the candidate, that needs its own runtime content/loader seam rather than an ad hoc hash in this recovery.
4. **The existing sink primitive does not create a separate sink ledger row.** The join now supplies a server-derived `wild:{row}:{col}` key to `SpendUnbankedUnlocked`; the primitive's current implementation updates the unbanked pot and does not persist that descriptive key. This lane does not broaden the economy or add a new ledger.
5. **No live behavior was proven.** There was no running game/server/browser probe, and no full unfiltered suite was substituted for the focused evidence.

## Next steps

1. Manager-review this exact dirty worktree and harvest only the seven listed paths.
2. Resolve the owner steering ruling, then replace the temporary selector-zero policy with the chosen persisted/live signal and add its focused multi-party test.
3. Run `verify-change.ps1` again with a boundary/timeout that completes, or record its exact bounded result; do not infer a green verdict from the timeout.
4. If a live proof is required for acceptance, deploy the reviewed code and exercise `/talk` and `/cage` through the real server path; this report intentionally does not claim that proof.
5. Keep the Delve economy/archetype encounter expansion separate unless a new owner-approved contract requires it.

## Exact changed paths

- `gk-core/src/FusionRpg.Server/DelveWildEndpoints.cs`
- `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Delve.cs`
- `gk-core/src/FusionRpg.Core/Delve/Loot/DelvePrices.cs`
- `gk-core/tests/FusionRpg.Server.Tests/DelveWildEndpointsTests.cs`
- `gk-core/tests/FusionRpg.Core.Tests/Delve/Loot/DelvePricesTests.cs`
- `gk-core/tests/FusionRpg.Data.Tests/Delve/DelveWildTransactionTests.cs`
- `tasks/reports/resume-01-delve-owner-recovery-20260925.md`

No commit, push, merge, branch reset, checkout, stash, process kill, external-directory read, or alternate runtime/model was performed.

<<<REPORT {"status":"partial","summary":"Recovered and reviewed the failed Delve owner draft. The scoped server-owned room/cage/candidate/party/OfferFloor join contract is implemented; focused Core (22/22), Data (18/18), and Server (18/18) tests plus diff/session checks pass. The all-path verify-change run timed out without a verdict, live behavior was not probed, and the permanent multi-party steering ruling remains open.","changed_files":["gk-core/src/FusionRpg.Server/DelveWildEndpoints.cs","gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Delve.cs","gk-core/src/FusionRpg.Core/Delve/Loot/DelvePrices.cs","gk-core/tests/FusionRpg.Server.Tests/DelveWildEndpointsTests.cs","gk-core/tests/FusionRpg.Core.Tests/Delve/Loot/DelvePricesTests.cs","gk-core/tests/FusionRpg.Data.Tests/Delve/DelveWildTransactionTests.cs","tasks/reports/resume-01-delve-owner-recovery-20260925.md"],"verification":["session-boundary-check.py --session resume-01-delve-owner-recovery-20260925 — exit 0, clean","dotnet test gk-core/tests/FusionRpg.Core.Tests --no-restore --filter FullyQualifiedName~DelvePricesTests — 22/22 passed","dotnet test gk-core/tests/FusionRpg.Data.Tests --no-restore --filter FullyQualifiedName~DelveWildTransactionTests — 18/18 passed","dotnet test gk-core/tests/FusionRpg.Server.Tests --no-restore --filter FullyQualifiedName~DelveWildEndpointsTests — 18/18 passed","git diff --check — exit 0","guard-dal.ps1 — exit 0; DAL GUARD OK","verify-change.ps1 with all six executable paths — exceeded 300-second timeout, no final verdict; not counted as pass"],"open_issues":["Persistent/live steering semantics for multi-party raids are unresolved; selector-zero is explicitly temporary and fail-closed.","Join pricing still uses the persisted ThetaRun watermark because no room-local theta column exists.","The effective persisted archetype is validated/passed, but archetype-specific encounter-pool expansion is outside this join-only change.","No live game/server/browser proof was run; verify-change did not produce a verdict before timeout."],"next_steps":["Manager-review and harvest only the seven allowed dirty paths.","Obtain the owner steering ruling and add the durable multi-party steering signal/test.","Repeat concrete-path verification to completion or preserve the exact timeout result.","Run a real server/live proof only if required by acceptance; do not broaden into economy redesign."]} REPORT>>>
