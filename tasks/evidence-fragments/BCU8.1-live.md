# BCU8.1 — live regression: nerve.* VFX apply cue (D17)

Claim: after the BCU8.1 fix (`9ba14033`, three `nerve.*` rows added to `VfxSeedCatalog.StatusFx`), a
`nerve.unsettled/shaken/afflicted` apply on the **real lawn** produces a real transient apply cue at
the moment of application. Scope: **game-injector-debug** (this is the live-engine half; the catalog
join-closure is Core/contract and already covered by `StatusFxCategoryClosureTests`).

| Criterion | Command | Executed result |
|---|---|---|
| Fresh live board | `python gk-fusion/tools/debug-mcp/cli.py debug_lawn_setup --json '{"scenario":"lab-overlay","level":1}'` | `ready=true`, `targetPtr=252FD26FC80`, `liveEntities={plantCount:1,zombieCount:1,liveState:"InMatch"}` |
| Apply all three nerve tiers | `POST /api/debug/status/apply {"statusId":"nerve.unsettled","hostPtr":"252FD26FC80","durationMs":20000}` (then `nerve.shaken`, `nerve.afflicted`) | each `{"ok":true,"queued":1}` |
| Cue fires at apply moment (read back) | `python gk-fusion/tools/debug-mcp/cli.py debug_events --json '{"kind":"debug.fx.shown","limit":5,"cursor":"7000"}'` | id **8801** `cueId=status.nerve.unsettled.apply` ptr `252FD26FC80` `primitives=["burst","flash"]` @13:31:31.921 · id **8804** `status.nerve.shaken.apply` @13:31:32.041 · id **8807** `status.nerve.afflicted.apply` @13:31:32.291 — all within ~0.4 s of the applies |
| Screenshot | `python gk-fusion/tools/debug-mcp/cli.py debug_screenshot --json '{"tag":"bcu81-plant","save_to":"tasks/evidence-fragments/bcu81-nerve-plant.png"}'` | 960×531 PNG captured after the apply |

**Honest gap:** the screenshot shows the live lawn with the actor present but **not** the burst — the
cue's `life=0.45 s` elapses before a screenshot round-trip completes. The decisive evidence is the
`debug.fx.shown` envelope at the apply timestamp, not the image; the image is kept only as the
"what was on screen" artifact. Do not read the screenshot as a cue sighting.

Falsified by: no `debug.fx.shown` envelope carrying `status.nerve.<tier>.apply` after the apply.
