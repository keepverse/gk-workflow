# CC7 — Infrastructure (plan line 152)

Verdict: **PARTIAL.** Sharding, notifications waves 1–4 and the python lane are green. The Core
split (TVB Checkpoint 5/6) has **not landed**. No live notification was emitted on this save.

| Criterion | Command | Executed result | Scope |
|---|---|---|---|
| Sharding | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~TestShardManifest"` | `Failed: 0, Passed: 14` | offline |
| Notifications waves 1–4 | `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~Notification"` | `Failed: 0, Passed: 43` | offline |
| Notifications checkpoints | `tasks/notification-ssot-todo.md` Checkpoints 1–4 | all bullets `[x]` (vocabulary/routing, durable log, G1, "every stage can be told") | offline |
| Python lane (schema 4) | `tasks/test-verification-boundary-todo.md` Checkpoint 3 | every bullet `[x]` — `gk-forge/tools/seedsmith/**` + `gk-core/tools/tuning/*.py` resolve, `schemaVersion` 4 accepted | offline |
| Core split (schema 5) | `tasks/test-verification-boundary-todo.md` Checkpoint 5 + 6 | CP5 "every manifest project applied; residual green; no test→test reference" `[ ]`; CP6 (parent CC7) `[ ]` | offline |
| Live notification (server read-back) | `GET /api/notifications/1` | `{"items":[],"nextSince":0,"hasMore":false}`; history needs a category and none exists | rpg-server-debug |

Live-visible half: none observed — the world-turn and cache notification sources need a world turn /
world cache, and this probe (lawn lab board + aptitude respec) produced neither. Reported rather than
papered over; the wave-1–4 contract is green by test, the live emission was not exercised.

Falsified by: a sharding or notification test failure, or a schema-4 registry rejection.
