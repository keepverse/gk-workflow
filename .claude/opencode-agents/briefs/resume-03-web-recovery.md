# Resume P1 03 — authoritative web recovery and match isolation

## Goal

Close the confirmed web recovery P1/P2s using the owner-ruling snapshot-on-recovery contract. A cold client, reconnect, empty binding snapshot, reverse event order, and foreign match event must converge to one explicit state.

## Read first

- `AGENTS.md`
- `docs/DESIGN-GATE.md`
- `docs/architecture/event-pipeline-v2-ssot.md`
- `docs/architecture/fe-game-foundation.md`
- `docs/architecture/game-gui-principles.md`
- `docs/architecture/actor-hud-ideal.md`
- the current Server hub/event code, web bus/lawn fold, and focused tests

## Allowed paths

- `gk-web/web/fusion-rpg-web/src/features/lawn/LawnPage.tsx`
- `gk-web/web/fusion-rpg-web/src/features/lawn/lawnProjectorFold.ts`
- `gk-web/web/fusion-rpg-web/src/features/lawn/lawnSessionFold.ts`
- `gk-web/web/fusion-rpg-web/src/lib/bus/hub-provider.tsx`
- `gk-web/web/fusion-rpg-web/src/lib/bus/log-store.ts`
- `gk-core/src/FusionRpg.Server/RpgHub.cs`
- `gk-core/src/FusionRpg.Server/EventIngest.cs`
- `gk-core/src/FusionRpg.Contracts/**`
- `gk-web/web/fusion-rpg-web/src/features/lawn/lawnProjectorFold.test.ts`
- `gk-web/web/fusion-rpg-web/src/features/lawn/lawnSessionFold.test.ts`
- `gk-web/web/fusion-rpg-web/src/lib/bus/hub-provider.test.tsx`

## Requirements

1. Implement the owner-selected authoritative snapshot on entry/reconnect; invalidate/refetch dependent state at the recovery edge.
2. Make match-key scope explicit; reject/isolate foreign events rather than changing the visible model.
3. Treat snapshot bindings as authoritative: empty snapshots clear stale bindings; preserve binding-before-spawn and spawn-before-binding convergence.
4. Separate loading, error, empty, and stale states; do not claim browser behavior without browser evidence.
5. Keep the change within the selected contract. If a new shared DTO is required, add it under Contracts and update all affected tests in this fence.
6. Do not redesign the whole FE or add a second event source.

## Evidence/report contract

Run focused Vitest/build checks; use `npm ci` only if dependencies are absent and record it. Report full SHA, changed files, exact commands/results, browser evidence or its explicit absence, open questions, and next plan. Leave dirty for manager review.

## Verification

- `npm test -- --run src/features/lawn/lawnProjectorFold.test.ts src/features/lawn/lawnSessionFold.test.ts src/lib/bus/hub-provider.test.tsx`
- `npm run build`
- `git status --porcelain`
- `git rev-parse --short HEAD`
