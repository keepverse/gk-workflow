# `CAI-cite-5` — the citations this lane's own edits moved

Lane `cai3` (session `combat-ai-3`), 2026-09-23. Found while checking what this lane's own code moves broke:
the rule is *re-anchor doc citations in the same commit as the code move that breaks them*, and
`guard-doc-citations.ps1 -Strict` **cannot see this class** — it checks bounds, not content, which
`CAI-cite-4` records too. Every in-fence citation was re-anchored in this commit; the out-of-fence ones are
filed as `CAI-cite-5` for routing.

## The in-fence ones, re-anchored here

| File | Was | Now | Why it moved |
|---|---|---|---|
| `spec-decision-inspector.md:85` | `IntentRouter.cs:92-94` | `IntentRouter.cs:68-70` | the per-arm wrap moved from `Compose` into the **constructor** |
| `spec-decision-inspector.md:78` | `DebugCombatActions.cs:377,397` | `DebugCombatActions.cs:377,418` | `LawnDecisionDump()` was inserted above `AiDecisionDump()` |
| `tasks/reports/CAI2.4-fourth-arm.md:16-18` | `IntentRouter.cs:92/93/94` | `IntentRouter.cs:68/69/70` | same move |
| `tasks/reports/CAI-spec-status-4.md:83` | `DebugCombatActions.cs:377,397` | `DebugCombatActions.cs:377,418` | same insertion |
| `tasks/reports/CAI4.8-start-edge.md:14` | `LawnDecisionHost.cs:83` | `LawnDecisionHost.cs:85` | `BeginMatch(ulong)` and `Configure` were inserted above it |

Verified after the edit: `IntentRouter.cs:68` is the policy wrap and `:69`/`:70` the fallback and steered
ones; `DebugCombatActions.cs:418` is `AiDecisionDump`'s `Recent()` read; `LawnDecisionHost.cs:85` is
`BeginMatch(CombatAiLawnTuning tuning, ulong matchSeed)`.

## The out-of-fence ones, filed

Measured from `git diff -U0`'s own hunk headers against `001e03713ac4`, so the shifts are arithmetic rather
than eyeballed:

| Changed file | Shift | Broken citations | Owner |
|---|---|---|---|
| `gk-core/src/FusionRpg.Core/Battle/BasicAttack.cs` | **+7 from line 180** | `docs/architecture/action/spec-action-costs-cooldowns-adoption.md:107` (`:198` → `:205`); `spec-action-resolution-by-category.md:11` (`:171-219` → `:178-226`), `:15` (`:175-193` → `:182-200`) | the `action` program |
| `gk-fusion/src/FusionRpg.Injector/Host/RpgHost.cs` | **+14 from line 100** | `action-enrich/spec-lawn-action-base.md:40,41`; `action-skill-tiers/spec-rung-table-activation.md:18,58`; `action-skill-tiers-map.md:97,160`; `class-system/spec-residual-fit.md:75` | `action-enrich`, `action-skill-tiers`, `class-system` |
| `gk-fusion/src/FusionRpg.Injector/Match/MatchHost.cs` | **+16 from line 241** | `battle-engine-ssot.md:237` (`:322-324` → `:338-340`) | `battle-engine-ssot` |
| `gk-core/src/FusionRpg.Core/Actions/IntentRouter.cs` | the wraps moved | `tasks/evidence-fragments/CAI-defer-1.md:16,30` (`:77,86-88` → `:54,68-70`) | this program, but the directory is outside this lane's fence |

Citations *before* each insertion point are unmoved and were checked, not assumed — e.g.
`BasicAttack.cs`'s `:105-143`, `:88-97`, `:156-174` and `:117`; `RpgHost.cs`'s `:57`; and everything under
line 241 in `MatchHost.cs`.

## NOT proved

- **No code changed**, so no build or test was run.
- **The out-of-fence shifts are arithmetic from the hunk headers, not a read of every cited line.** An owner
  re-anchoring one should confirm the target line still says what the citation claims — the same discipline
  this report applied to its own five.
