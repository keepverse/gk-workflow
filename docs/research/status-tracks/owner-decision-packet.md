# Owner decision packet — `status-tracks`

**Program:** `status-tracks` · **Map:** [architecture/status-tracks-map.md](../../architecture/status-tracks-map.md) ·
**Ideal:** [architecture/status-tracks-ideal.md](../../architecture/status-tracks-ideal.md) ·
**Plan:** [tasks/status-tracks-plan.md](../../../tasks/status-tracks-plan.md) · **Status:** written 2026-10-02, pending owner approval

Nothing here waits without a default; each row states one.

Three questions, all K1. The classification test that matters: a question is K1 only the owner can
answer. Each of these reserves a decision the repo's own documents reserve to the owner, so none of
them is derivable and none should be guessed.

## K1 — scope / authority

| # | Question | Default if unanswered | Releases | Evidence |
|---|---|---|---|---|
| K1.1 | **May a seventh `ActorResourcePool` exist?** `ResourceIds` is `{hp, stamina, hunger, spirit, qi, poise}` and the hub calls it *"the only list"*. Widening it is an ADR, not a content edit, and no ruling anywhere permits **or** forbids it — the question is genuinely open, and both answers have shipped precedent (`poise` widened the pool in 2026-08-26; `nerve.*` solved the same need as a projection in 2026-09-05). The deciding question is *"does anything spend it?"* | **No seventh.** Ship every out-of-combat need as a status projection, following `nerve`/`wound.*`. The pool question stays open for a need that becomes an action cost. | `ST2.1` (need-inventory: the carrier for any need that must render as a bar) | `resource-hub-ssot.md:134` (*"adding one is an ADR"*), `:201-212` (six-coverage, *the only list*); `spec-delve-attrition.md:400-404` (*Never … a seventh `ResourceIds` entry*); `spec-action-costs.md:226`, `spec-poise-resource.md:238-241` (two further ask-first rows); `spec-poise-resource.md:184-190` (the costed recipe, if the answer is yes) |
| K1.2 | **May a need that only makes sense decaying with elapsed real time ship at all?** The repo refuses wall time by design — recovery is counted in delves, the pool tables carry no `*_utc` column, `guard-clock-seam.py` fails the build on a stray `UtcNow`, and the stated reason is that wall-clock meters read as a paywall (`spec-delve-attrition.md` §7 R6, `:45-47`). Sleep and fatigue were **removed** from this game on that basis. | **No.** A time-decaying need ships only if it can be re-expressed as an event charge (per-room, per-delve-crossing) — the `HungerCharge` shape. If it cannot, it does not ship; the answer is a product ruling, not an implementation detail. | `ST2.1` (every candidate need scored under this rule) | `spec-delve-attrition.md:245-249` (R6, *no `DateTime`, no `ElapsedDays`, no due stamp*), `:387-389` (the guard test), `RpgStore.cs:670-672` (no `*_utc` column); `party-dungeon-ideal.md:343-345` (fatigue removed; wall-clock meters read as a paywall) |
| K1.3 | **Is the out-of-combat projection allowed to be eventually-consistent?** Today `Sync` needs a live `StatusRuntime` and a `hostPtr`, which are battle-scoped; outside a room there is none, so the shipped answer defers the projection to whichever room's battle setup runs next (`EventOutcomeDispatch.cs:66-77`). The alternative — a status correct at every instant, everywhere — needs a runtime outside battle, which is the second-engine shape the locked rule refuses. | **Yes, deferral is correct.** The scalar is authoritative and always up to date; the status is a rendered projection of it, refreshed whenever a runtime exists to receive it. | `ST1.7` (deferred-projection: assert the deferral path is a *supported* answer, not a workaround) | `EventOutcomeDispatch.cs:66-77` (the documented shape); `StatusRuntime.cs:8-62` + `NervePolicy.cs:22-28` (why a counter cannot live on a status); `decisions.md` Status-tracks row, rule 4 |

## Why these three and not more

Nothing else in this program is owner-only. The status **vocabulary** stays closed in C# and a widen
is a reviewed change with both count lines moved in the same commit — that is a process obligation,
not a question. The combat-track coverage gaps (`turn.haste` inert under `classic-round`, D1's
status-pulses-bypass-combat-math in `battle-engine-ssot.md` §4) belong to the battle-engine owner
and are filed as cross-program notes, not asked here.

## Applying the answers

After the owner answers, each answered question is applied as a paperwork edit in the rows it
releases, citing the answer's date. Match questions by content, never by number.