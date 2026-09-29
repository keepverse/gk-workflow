# CAI-F1 — the revision constant, and the publish it was blocking

Lane `cai2` (session `combat-ai-2b`), 2026-09-23. The row measured that *"both readers name
`combat-ai.v1.json` **literally**"*, so an H7 publish could not land with its readers in one commit for any
combat-ai lane. It offered two fixes; **option (a)** — route the revision through the constant pattern the
other domains use — is what landed, because it removes the problem permanently instead of doing one
publish carefully.

| Criterion | Command | Result |
|---|---|---|
| A revision is published and a reader picks it up (read back through the normal path) | `python gk-core/tools/tuning/publish.py combat-ai --add-key :lawn={...}` then `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~CombatAiTuningRevisionTests"` | `published combat-ai (v1 -> v2, 1 change(s))`; **3 passed / 0 failed** — the file `CombatAiTuningFiles.Current` names exists, parses through the SHIPPED `CombatAiTuningLoader`, and carries the lawn section's four keys with their seeds |
| The readers name the CONSTANT, not a literal | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~SiegeKeyMigrationTests"` | **6 passed / 0 failed** — `Both_hosts_load_the_same_file` asserts both hosts reference `CombatAiTuningFiles.Current` and contain **no** `"combat-ai.v` literal |
| The publish is a pure ADDITION | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden\|FullyQualifiedName~Siege"` | **338 passed / 0 failed** — and the test asserts it structurally: `JsonNode.DeepEquals` on `profiles` and `router` against v1 |
| The lawn section is CAI4.7's, with the spec's seeds and no structural values | same focused run | **3 / 0** — 7 / 50 / 10 / `"lawn.ai.offset"`, and `carryCasts`/`decisionsPerFrame`/`castTokens`/`castTokenTimeoutTicks` are asserted ABSENT (they are code consts) |
| The row's named guards | `guard-tuning-immutability.py`; `python gk-core/tools/tuning/resource_ownership.py --check`; `guard-dal`/`guard-single-writer`/`guard-actor-hub` | all **exit 0**; **OK — 166 generated edges match aptitudes.v10.json's 166** |
| Both hosts still compile | `dotnet build gk-core/src/FusionRpg.Server`; `guard-injector-compile.ps1` | `Build succeeded`; `INJECTOR COMPILE GUARD OK` |

## Why the revision is v2 and not the v3 the rows predicted

`CAI4.7`'s row and its spec both said `combat-ai.v3.json`, on the assumption that CAI3.5's four `delve/*`
rows would be v2. Those aborted — `AiRole` declares no `Enemy` member, so `delve/enemy` cannot parse (filed
with its evidence) — so the next revision was **v2**, and the lawn section is in it. The substance the rows
asked for (a `v{n+1}` carrying the lawn section, published through `publish.py`, with its readers moved in
the same commit) is what landed.

## What this does NOT claim

The lawn section's **consumer** is still owed: the frame slot that parses `lawn.trigger.*` is `CAI4.8`'s, so
the four keys have a file and a test that reads them back through the parser, but no production reader yet.
That is `CAI4.8`'s line, and it is named on both rows rather than glossed as done.
