# SE3.12 — Doc backlog: D3 path-qualification outside architecture

Same method as SE3.8–SE3.11, scoped to `docs/**` outside `docs/architecture/`.

## Scope measured before the edit

`docs/` minus `docs/architecture/`: D1 143 (3 HIGH), D2 6 (0 HIGH, all `docs/research/` LOW), D3 61
(4 HIGH, all bare `types.ts` citations).

## The four D3-HIGH findings, verified by content

- `docs/design/gui-lego/recipes/wonder-composer.ACCEPTANCE.md:23` — `types.ts:817-830`/`:890-898` →
  `gk-web/web/fusion-rpg-web/src/contract/types.ts`. Both ranges verified word-for-word: `:817-830` lands on
  the `wonderLiveCountSector`/`wonderLiveCountEmpire` fields whose own doc comment names *"wonder-wire
  §Design 3 (plan Task 4A.4)"* — the exact task this row cites; `:890-898` lands on `SlotView`'s Wonder
  facet field, doc comment *"wonder-wire §Design 2 (plan Task 4A.4)"* — again the exact task. Zero
  drift, purely an ambiguous basename (3 different `types.ts` files exist in the repo).
- `docs/design/spec-lawn-interactive.md:98,314,520` (same citation, 3 sites) — `types.ts:575-591` →
  `gk-web/web/fusion-rpg-web/src/contract/types.ts:635-651`, the real `ActorView` declaration, verified to
  carry no explicit resources/statuses/actions fields (only `channelSummary`, `elementTyping`,
  `shieldStack`, `equipSlots`) — matching the claim *"Absent from `ActorView` — no resources, no
  statuses, no actions"* exactly. Drifted from :575-591 to :635-651.

## The 3 D1-HIGH findings outside architecture

All three are genuine runtime-generated artifacts that correctly do not exist in the tracked tree —
not proposals, not drift, not a wrong path:

- `docs/runbook/local-dev.md:190` — `_candidates/.../round-N.json`, a scratch path a real propose
  run creates (`N` a real round number); noted inline as run-generated, never tracked.
- `docs/runbook/release-prove.md:10` and `docs/testing/player-pack-smoke.md:36` — both
  `artifacts/player-pack-smoke.json`, the smoke-test's own summary JSON, written only when
  `smoke-player-pack.ps1` runs; noted inline the same way.

## Post-merge residue found and fixed in the same pass (not originally SE3.12's own scope, but the
## same D3/D4 shape, discovered when re-running `--strict` after merging `features/mega-merge`)

`features/mega-merge` landed new `combat-ai`, `creature-lawn-deploy` and `trade-network` content
between SE3.11's commit and this one, reopening 9 D3-HIGH and 1 D4-HIGH finding repo-wide:

- `Program.cs` (5 sites) — two different real targets depending on context, disambiguated by
  content: `gk-core/tools/ProvePredictor/Program.cs` (`combat-ai/spec-action-schedule-twin.md` x2,
  `spec-auto-policy-switch.md` — `ActionSet.Load("basic")`/`economyOptions` verified at the exact
  cited lines 114-115, the `1e-4` fit-gate threshold at :152-160) vs
  `gk-core/src/FusionRpg.Server/Program.cs` (`spec-profile-schema.md`'s `SiegeTuningPolicy.Configure` at
  :223-224, `trade-ai-map.md`'s `WorldAiTuningLoader.Parse` at :245).
- `CapPolicy.cs` (3 sites, `creature-lawn-deploy/spec-unique-deploy-cap.md`) — all three are
  `gk-core/src/FusionRpg.Core/Match/CapPolicy.cs` (the RAM-gate one, not `Actions/Grants/CapPolicy.cs`):
  `GateResult`/`GateReasons` verified at the exact cited line 54, `TryAdmit` at the exact cited
  line 98.
- `planner.py` (2 sites, `empire-seed-map.md`, `trade-network/trade-foundation/spec-sector-features.md`)
  — both `gk-forge/tools/seedsmith/seedsmith/adapters/structures/planner.py` (the variant-bound-of-4 formula
  already established in SE3.9/SE3.11).
- **D4**: `combat-ai-ideal.md` — `combat-ai-map.md` reads "APPROVED 2026-09-20 by independent agent
  review", 20 module specs written, `tasks/combat-ai-todo.md` exists (0 done / 55 open), while the
  ideal's own status still says "idea phase ... Not a spec" with no banner. Banner added.

## Repo-wide result

`python scripts/audit-doc-citations.py --strict` now **exits 0** — zero HIGH findings anywhere in
the tree (D1 1047/0 HIGH, D2 6/0 HIGH, D3 58/0 HIGH, D4 0/0 HIGH). This is SE3.13's own acceptance
criterion, already met as a side effect of finishing SE3.8–SE3.12.

## Falsifier and guard evidence (scoped per the coordinator's instruction — no full-project run)

| Check | Command | Result |
|---|---|---|
| Falsifier suite | `python -m pytest gk-forge/tools/seedsmith/tests/test_audit_doc_citations.py -q` | **23/23** |
| C# narrow falsifier + registry schema | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~DocCitationAuditTests\|FullyQualifiedName~EnforcementRegistryGuardTests"` | **23/23** |
| Strict repo-wide audit | `python scripts/audit-doc-citations.py --strict` | **exit 0** |

No `scripts/audit-doc-citations.py` change. No `gk-core/data/tuning/**` touched; no golden affected. This
commit does not touch `tests/FusionRpg.Core.Tests/Items/MaterialVocabularyTests.cs` — that file's
population-pin fix is lane C's, per the coordinator's explicit instruction this session.
