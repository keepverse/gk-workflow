# NS2.1 — Store schema and idempotent append with the key ledger and per-save rev

| Criterion | Command | Result |
|---|---|---|
| four tables created by `EnsureNotificationSchemaUnlocked` on fresh/existing hot DBs; `save_id`/`seq`/`rev` `long`, rev bump `checked` | code review + tests | hooked into `RpgStore.cs`'s schema sequence right after `EnsureTitleLifecycleSchemaUnlocked`; `BumpSaveRevUnlocked` uses `checked(current + 1)` |
| `AppendNotificationTurn` (ledger decides "new", row insert second): same key twice -> empty second time, count stays 1; same key for two saves -> two rows; rev is a row, never `MAX(rev)` | `dotnet test tests\FusionRpg.Data.Tests -c Release --filter "FullyQualifiedName~Notification"` | `Passed! - Failed: 0, Passed: 11, Skipped: 0, Total: 11` |
| `guard-dal.ps1`, `guard-test-substrate.py` | `.\scripts\guard-dal.ps1`; `python gk-core/scripts/guard-test-substrate.py` | `DAL GUARD OK`; `TEST SUBSTRATE GUARD OK` |
| `audit-overflow.py` / `audit-magic-numbers.py` clean on the new file | `python scripts\audit-overflow.py`; `python scripts\audit-magic-numbers.py --targets M1` | `0 finding(s)` both; `DedupKeyMemoryWorldTurns` carries the structural exemption comment verbatim |
| registry mapping upgraded now that a real test exists | `python gk-core/scripts/guard-verification-boundaries.py` | `VERIFICATION BOUNDARY GUARD OK` (added `verificationId: "data.notify-store"` + `[Trait("VerificationId","data.notify-store")]` on the test class) |

**Self-caught defect while writing the ledger-bound test:** aging runs once per call, AFTER that
call's own rows are processed, so a key becomes reusable only on the call FOLLOWING the one whose
aging finally deletes its ledger row — and the row-level `UNIQUE(save_id, dedup_key)` still blocks a
retry independently of the ledger unless the ROW itself was already pruned. First draft used
`retainPerCategory: 10` (never pruning the row) and failed; fixed to `retainPerCategory: 1` and
traced through by hand before re-running, now green.
