# story-scene-todo.md T27a — the four rift.* VFX cues live on the real game

**Claim:** `rift.portal.open`, `rift.portal.surge`, `rift.quarantine.seal`, `rift.quarantine.fade`
(`VfxCatalog.cs:65-68`) resolve through `VfxDirector` and visibly reach the game — the checklist's own
"Owner-run live proof — the four cues visibly reach the game."

## Live sequence

Fired each cue via the same real route `scripts/prove-vfx.ps1` itself uses
(`POST /api/debug/fx/play {"cueId":..., "col":4, "row":2, "amount":<unique>}`), on a real live lab
board, and read the result back through the normal event path (`GET /api/debug/events?kinds=
debug.fx.shown,debug.fx.skipped`), not the play call's own response body (which is just `{"queued":1}`
— fire-and-forget over the command inbox).

| Cue | Result |
|---|---|
| `rift.portal.open` | `debug.fx.shown` — `primitives:["burst"] rgb:"#FFFFFF" bursts:1` |
| `rift.portal.surge` | `debug.fx.shown` — same shape |
| `rift.quarantine.seal` | `debug.fx.shown` — same shape |
| `rift.quarantine.fade` | `debug.fx.shown` — same shape |

**All four fired cleanly — zero skips, zero errors.** They reach `VfxDirector`, resolve a real
recipe, and produce a real Unity burst primitive every time. Screenshots taken immediately after each
`fx/play` call (`rift-portal-open.png`, `rift-portal-surge.png`) show the lawn board but no visually
distinct portal/surge effect at the fired cell.

## Real finding, not a clean sign-off: all four render identically (white, generic burst)

Every one of the four came back `rgb:"#FFFFFF"` — the SAME neutral/fallback color
`scripts/prove-vfx.ps1`'s own doc comment names for "the SYS-ELEMENT-FX-off neutral path" — not the
distinct authored colors the audit text itself describes ("portal purple / surge green / seal blue /
fade muted"). `ptr:""` on every payload: I fired these against a lawn cell (`col`/`row`), which is
this program's own T27a acceptance shape (matching `prove-vfx.ps1`'s existing cases), but these four
cues are onboarding-flow cues really anchored to a UI/menu element, not a lawn cell — so this result
is consistent with "no real anchor was available, degrade cleanly" (a legitimate documented behaviour:
"A missing anchor or shader failure emits a skip reason and leaves the story usable" — except here it
did not skip, it rendered the generic fallback instead of skipping, which is worth the owning
program's attention: is a silent white-burst substitution the intended degrade, or should this
specific case have skipped with a reason like the other anchor-miss path does?).

## Verdict

**Half proven.** The pipeline claim ("the four cues visibly reach the game" in the sense of "resolve
without crashing or being silently dropped") is **PASS** — real `debug.fx.shown` for all four, zero
skips, fired through the exact route the program's own prove script uses. The VISUAL claim (each cue
looks distinctly like its own authored color/shape) is **not confirmed** in this pass — every cue
rendered as the same generic white burst, either because a lawn cell is the wrong anchor for these
onboarding cues, or because a real defect (recipe not distinctly authored, or degrading to a fallback
that should have skipped instead). Not fixed here — this needs the onboarding program's own real
context (the actual Rift teaser sequence) to test the visual claim properly, matching this task's own
recorded coordination note ("T12-T14 coordination named, not closed... that list is the onboarding
program's to close").

## Worth landing

`scripts/prove-vfx.ps1` still has no rift case (confirmed: `grep -n rift scripts/prove-vfx.ps1` before
this probe returned nothing). Adding one — following the exact shape used here — would make this
result rerunnable without live-qa; not added in this pass to avoid guessing at the program's own
intended pass/fail assertions (e.g., should this really assert a NON-white rgb, or is white-burst the
correct fallback shape here — that is a design call for `story-scene`/onboarding to make, not a live
probe to invent).
