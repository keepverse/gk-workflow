# AECP2 — the lawn reads the action (lawn half of the parent plan's CC3)

**Status: DONE.** All five evidence lines hold, including the live probe that was the only item in this
program that could not be produced without the game.

| # | Evidence line (from `action-enrich-todo.md`, Checkpoint 2) | State |
|---|---|---|
| 1 | For the same action at the same Θ the lawn rider amount equals the battle base (the parity test), and the Hub-parity **planted** test is green | **GREEN.** `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~BasicAttackGrant"` → **21/21**, which includes `TheBakedAmountIsTheBattleBaseForTheSameTheta_negativeForDamage` and `TheBakedAmountFollowsTheta`. The planted falsifier `A_planted_second_contributor_to_progression_power_breaks_that_parity` is 3/3 in `LawnGrantThetaParityTests` (AE2.2's record — `FusionRpg.Injector.Tests` needs real game DLLs, so it is cited from there rather than re-run here). |
| 2 | Every trigger row is tested, and no grant call happens off the main thread | **GREEN, and now measured live.** `LawnBasicAttackGrantBinderRefreshTests` 6/6 (AE2.3) covers the trigger rows in the unit sense; the live probe then exercised **both real refresh triggers on a running game**: the SignalR **reconnect** after a server restart, and the **player-identity** change. Both re-baked live grants without a respawn (`docs/research/action-enrich/live-probe-2026-09-19.md`, results 3 and 4). |
| 3 | An instakill hit does not ride the rider, and unrelated plain-amount riders are unchanged | **GREEN.** The same **21/21** filter includes `TheAmountDoesNotDisturbThePayloadOrCooldown_andTheGrantOptsOutOfInstakill` and `ANeutralOwnerGetsAnAmountAndStillNoPayload`; AE2.1's `OverlayFilterInstakillTests` 5/5 covers the overlay side, including the two unchanged cases. |
| 4a | The live probe has passed and its evidence is committed | **GREEN.** `docs/research/action-enrich/live-probe-2026-09-19.md`, taken by the manager on the real game (MelonLoader host, pvzrh-3.9): four Θ readings **1/69/70/71 → 14/395/403/410**, matching `floor(140 × P(Θ) / 1000)` exactly, and the same actor going **410 → 14** on a player switch with **no respawn**. |
| 4b | `ST5.4` (the `action-base` guard row) is green once it lands | **GREEN.** `ST5.4` landed (`7a6c4ed8`); the guard filter is **9/9** with both `action-base` and `action-rungs` in `AgreedDomains`, each with its own planted-mismatch twin. |
| 5 | Named and not built here: the switch-on mid-match key-set gap (reported to `lawn-combat-wire`), and the zombie-side Θ trigger row (written with `SE` save-identity's build) | **NAMED**, as the checkpoint requires. Neither is built here, which is what this line asks for. The probe adds a third, related instance of the same class to the follow-up list: a real level-up mid-match is invisible to the lawn until a refresh trigger fires. |

Together with Checkpoint 1 (`AECP1`, closed) this is the parent plan's **CC3** — "damage from the
action", and both halves are now complete: the battle half by the builder/parity tests, the lawn half by
the live probe's four Θ readings and the two refresh triggers.

The probe's own four findings are recorded as follow-up notes in the ledger (no push of Θ after a real
level-up; `afterId` paging stopping at a foreign `game` row; `lawn/quick-start` over a defeated board;
bullet hits being attributed to the bullet so the overlay path cannot evidence them). None of them is an
AECP2 row.
