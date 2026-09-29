# BP4 — aura-binding-producer owner/live proof

**Claim:** enabling `Might` through the real production endpoints (no hand-made `effect_instance` /
`effect_binding` row) raises a live lawn plant's `combat.power.omni` by exactly
`AuraMagnitude.ReferenceChannelValue(...)`'s own shipped output, and disabling moves it back —
the A5 shape, done through the producer this program built instead of by hand.

## Environment

Worktree `worktree-agent-a133b88741cadeb4f`, MelonLoader host, `dist\FusionRpg.Server` (built from this
tree post-merge), game process relaunched clean, `injectorConnected: true` throughout. Player 1 =
`Crazy Dave` (the only save on this machine).

## Sequence and evidence

| Step | Call | Result |
|---|---|---|
| 1. Equip | `POST /api/loadout {"playerId":1,"actionIds":["Might"]}` | `200 {"playerId":1,"actionIds":["Might"]}` |
| 2. Baseline (real endpoint) | `GET /api/aura-runtime/1` | `activeAuraIds:[]`, `equippedAuraIds:["Might"]` |
| 3. Baseline (DB, `dist\FusionRpg.Server\data\rpg-hot.sqlite`) | `SELECT count(*) FROM effect_binding` / `effect_instance` | `0` / `0` |
| 4. Baseline (live plant, real injector read) | `GET /api/debug/actor-derived?ptr=1EC430556C0` → poll `/api/debug/events?kinds=debug.actor-derived` | `combat.power.omni = 0` |
| 5. **Enable — the real production write** | `POST /api/aura-runtime/1/enable {"auraId":"Might"}` | `200 {"activeAuraIds":["Might"]}` |
| 6. Read back (DB) | same query | **1 binding**: `owner_kind='player' owner_key='1' source='aura'`; **1 instance**: `container_id='world-buff.aura-might'` |
| 7. Read back (real endpoint) | `GET /api/aura-runtime/1` | `activeAuraIds:["Might"]` |
| 8. Read back (live plant) | same poll | **`combat.power.omni = 3644`** |
| 9. Independently computed expected value | `AuraMagnitude.ReferenceChannelValue(0, 1, PowerTuningHub.Tuning.Curve.PinValue, AuraTuningHub.Tuning, AptitudeTuningHub.Tuning)` against the real shipped `gk-core/data/tuning/aura.v1.json` + `aptitudes.v2.json` (temporarily printed from `AuraContentDeliveryTests.A_single_channel_real_aura_resolves_to_the_reference_value_not_the_raw_externalRef`, reverted after reading) | **3644** — exact match |
| 10. Live grant observed in the real injector | `POST /api/debug/effect/list` → poll | `grantIds` includes `"atom:aura.might"` |
| 11. Disable | `POST /api/aura-runtime/1/disable {"auraId":"Might"}` | `200 {"activeAuraIds":[]}` |
| 12. Read back (DB) | same query | **0 bindings** — withdrawn |
| 13. Read back (live plant) | same poll, twice, 2s apart | ⛔ **`combat.power.omni` still 3644** — did NOT move back |

Δ (enable) = 3644, matching the shipped formula's own output exactly — not an invented number, and no
`effect_instance`/`effect_binding` row was ever hand-written for this proof (unlike the A5 proof, which
had to write one by hand because this producer did not exist yet).

## Verdict: PASS (grant half) — ⛔ FAIL (withdraw half), real defect found live

**BP4's own acceptance text includes "and back."** The grant half is fully proven. The withdraw half
is not: disabling the aura through the real endpoint updates the server's own database (binding
withdrawn) but the change never reaches the already-connected live injector, so the buff is permanently
stuck on the plant from the player's point of view. A unit test cannot see this class of bug because
the test harness has no live injector to leave stale — `AuraContentDeliveryTests.
Disabling_returns_the_channel_to_its_prior_value_via_the_real_endpoint` (line ~148) only asserts that
the *next* `AtomPushService.Build(...)` payload excludes the aura; it never sends that payload to an
injector that already holds the old grant, so it cannot catch what this live probe caught.

### Root cause (file:line)

- `gk-core/src/FusionRpg.Server/UniqueActorService.cs:227-260` (`PushAtomUnionAsync`) sends exactly one wire
  command, `EffectGrantRehydrate.ApplyCommandName` ("effects.grants.apply"), carrying the CURRENT
  owner-union grants. There is no companion "withdraw" command anywhere in production use (confirmed by
  grep: `ApplyCommandName` is the only `effects.grants.*` message ever sent).
- `gk-fusion/src/FusionRpg.Injector/CheatCommandRunner.cs:872-903` (`RunEffectsGrantsApply`) only **applies**
  `grants[]` — it has no concept of "a grant that was active last time and is absent from this push
  must now be withdrawn." `EffectRuntime.Withdraw` (`EffectRuntime.cs:260`) exists and works (it is
  literally how `debug.effect.withdraw` removes a grant by id), but nothing on this path ever calls it.
- `gk-core/src/FusionRpg.Server/AuraBindingProducer.cs:64-67` calls `_store.Withdraw(bindingId)` for each
  `plan.ToWithdraw` entry — correct for the DB, silent for the injector.

This is a structural gap in the atom-push wire contract (additive-only, no reconcile/removal), not an
aura-specific bug — anything else that calls `PushAtomUnionAsync` to revoke a mid-session grant (e.g. a
future unequip) would hit the identical defect. Fixing it needs a real withdraw/reconcile message on
the wire (diff old vs. new owner union, or an explicit withdraw list) — a module-sized change, not a
live-qa patch-in-passing. Reporting to the owning program (`aura-skill`/`backlog-clear`, the
"aura-delivery-path" gap `AuraContentCatalog.cs`'s own doc comment already named as deferred) rather
than attempting an in-scope fix.

## Secondary defect found and fixed (small, in scope)

`AuraBindingProducer.SyncAsync`'s refusals (e.g. "no container for aura X") were silently discarded by
both `/enable` and `/disable` (`AuraRuntimeEndpoints.cs`) — a real bind failure looked identical to
success to any caller, including this probe, and cost real diagnosis time before the actual cause (a
stale pre-merge `dist/` build) was found. Fixed: both handlers now log refusals to `Console.Error`
(`[aura-bind] refused for player {id}: {reason} — {detail}`), matching the existing
`[atom-push] mid-session re-push failed` convention `PushAtomUnionAsync` already uses. Non-breaking
(response shape unchanged). Verified: `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter
FullyQualifiedName~Aura` (38/38), full `dotnet test gk-core/tests/FusionRpg.Server.Tests` (663/663),
`guard-dal.ps1` OK.

## A real, unrelated blocker found and fixed first (why the diagnosis took as long as it did)

Before any of the above could run at all, the injector could not connect to a fresh game install:
`RpgHost.Initialize` throws `DirectoryNotFoundException` on
`Mods\data\seed\commanders\_registry\default-commanders.v1.json` because no injector host `.csproj`
ever `Content`-Included that tree (or `gk-data/packs/fusion/data/seed/dungeon/_registry`, the same pattern one row above it)
— see the separate commit `fix(injector): deploy commanders + dungeon seed registries with every host
build`. Fixed and proven live (`injectorConnected: true`) before this probe could even begin.
