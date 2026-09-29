# SE3.13 — `doc-citations` gates

Flips `gk-core/scripts/enforcement-registry.v1.json`'s `doc-citations` row from `backlog` to `gating`
(`backlogModule` cleared to `null`), matching `population-pin`'s own already-gating shape exactly.

## Precondition, proven before flipping

`python scripts/audit-doc-citations.py --strict` exits **0** — zero HIGH findings anywhere in the
tracked tree, confirmed in the same session as a side effect of finishing SE3.8–SE3.12 (the last 10
HIGH findings were `features/mega-merge`-introduced content discovered and fixed during SE3.12).

## Evidence

| Check | Command | Result |
|---|---|---|
| CI guard tier, `doc-citations` now listed and gating | `.\scripts\run-guards.ps1 -Tier ci` | **19/19 guards, 0 red** (was 18 before this flip) |
| Registry schema (R8 "every catalog guard named by an invariant", and every other rule) | `dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~EnforcementRegistryGuardTests"` | **18/18** |

No script change beyond the registry flip. `pr-doc-citations`'s invariant row already names
`"guards": ["doc-citations"]` (set in SE3.7) — no further change needed there.

## Wave 3 checkpoint

Checkpoint 3's first bullet (`population-pin` and `doc-citations` gating with 0 findings) is now
true and ticked. Its second bullet (`M3` and `A3` gating, "if the owner confirms Q4") is a separate,
explicitly owner-gated item this session did not touch and cannot resolve unilaterally — left
unticked with a note.
