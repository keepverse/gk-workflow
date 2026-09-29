# live-probe Task 22 — a summon can roll a species this game build cannot spawn

Two separate defects named in the original finding. Fixed defect (b); reported, not fixed, defect (a).

## (b) FIXED — an injector-side spawn exception during deploy was never reported back

**Claim:** when a unique-specimen deploy fails inside the engine (`SetPlant`/`SetZombie` throws or
returns null), the server's `Deploying` row should clear immediately via the real `fail-deploy`
endpoint, not sit until `UniqueActorService.FailExpiredDeploys`'s multi-minute timeout.

### Fix

`gk-fusion/src/FusionRpg.Injector/RpgClient.cs`: new `ReportFailedDeploy(instanceId, reason)` /
`PostFailDeployAsync`, POSTing to the real `/api/unique/actors/{instanceId}/fail-deploy` endpoint
(already built, previously only reachable by the timeout sweep). `gk-fusion/src/FusionRpg.Injector/
CheatActions.cs`: called from all four unique-spawn failure sites (`SpawnExtraPlant`'s null-check and
catch, `SpawnExtraZombieCore`'s null-check and catch) — only when `instanceId` is present (a
manual/debug spawn has no `Deploying` row to fail).

### Regression test (structural, matching this project's own established convention)

`gk-fusion/tests/FusionRpg.Injector.Tests/SpawnFailDeployReportingTests.cs` (5/5 green) — same idiom as the
pre-existing `UniqueAptitudeRefreshCadenceTests`'s own doc comment: `RpgClient` has no HTTP seam to
mock, so this asserts the WIRING exists (source-scan) at all four failure sites, and the live game is
the real end-to-end proof.

### Live proof (real game, real server, real engine failure — not fabricated)

1. `POST /api/creatures/debug/grant {"playerId":2,"speciesId":"allpeater"}` then
   `POST /api/creatures/debug/grant {"playerId":2,"speciesId":"ashthreepeater"}` — real specimens
   (typeId 1347, 918), deployed successfully. **Finding, not a defect:** both of these
   originally-suspect high-typeId species actually spawn fine on this build now — the corpus/build
   mismatch narrowed since the 2026-09-16 finding, or these two were never actually broken.
2. `POST /api/unique/actors {"playerId":2,"side":"plant","typeId":99999}` — a real roster row with a
   typeId no build has a prefab for (chosen deliberately to *guarantee* reproducing the precondition,
   since guessing at real species ids that fail on THIS build turned out unreliable — see finding
   above). `POST .../deploy` with a real live matchKey.
3. **Real engine failure, MelonLoader log verbatim:**
   ```
   System.NullReferenceException: Object reference not set to an instance of an object.
     at CreatePlant.SetPlant (...) 
   ```
   — the exact exception class Task 22's own report named.
4. **The fix firing, same log, same instant:**
   ```
   [FusionRpg] [fail-deploy] reported 2401ab73662f4dd696717c1c9c0b64ca: plant spawn threw:
   System.NullReferenceException: Object reference not set to an instance of an object.
   ```
5. **Read back through the normal path** (`GET /api/unique/actors/{instanceId}`, not the deploy
   call's own response body): within ~3 seconds, `phase` moved `"Deploying"` → **`"Roster"`**,
   `deployCorrelationId` cleared to `null`, `revision` incremented 1→2 — the server actually processed
   a real `fail-deploy` call, not merely received a log line. Before this fix this row would have sat
   in `"Deploying"` for the full `FailExpiredDeploys` timeout (minutes), matching Task 22's own
   complaint: "the server simply timed its deploy ack out."

## (a) NOT fixed — reported to the owning program

`SummonRoller` drawing from a summonable pool that includes species with no live prefab is a
**generated-seed defect**, not a hand-editable bug: the species corpus (`gk-data/packs/fusion/data/generated/creatures/*.
json`) marks a species `summonable`, and per this repo's own hard rule ("generated seed data is never
hand-edited — fix the generator and regenerate"), the fix belongs in whichever `tools/*Gen` program
emits that acquisition flag, then a full regeneration — never a one-off data edit here. This exact
module is already specced and unbuilt: `docs/architecture/lawn-playable/spec-summon-pool-integrity.md`
("A summonable species is one this build can actually plant (generator + corpus guard)... Fixes P5").
Reporting rather than attempting: `docs/architecture/lawn-playable-map.md:61`.

## Verdict

(b): **PASS**, live-proven with a real engine failure, not fabricated. (a): **reported**, not
attempted — a generated-content fix belonging to `lawn-playable`'s `summon-pool-integrity` module.
