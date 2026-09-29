# Manager acceptance review — web recovery and match isolation

**Source lane:** `resume-03-web-recovery-20260925` (worker result preserved; no direct merge)
**Review worktree:** `D:/Works/source/plant-vs-zombie-rise-of-summoner/.claude/worktrees/review-web-recovery-20260925`
**Status:** **PARTIAL until exact-SHA clean checkout and browser evidence**

## Change reviewed

The draft adds the existing `debug.snapshot` command as the authoritative recovery edge, carries a typed recovery status through the existing server event path, scopes lawn state to a match key, makes empty binding snapshots authoritative, and distinguishes loading/ready/empty/stale/error UI states. It does not create a second event source.

## Corrected independent evidence

The worker's original verification used the repository root for npm commands and recorded false `package.json` failures. Manager review reran commands from `gk-web/web/fusion-rpg-web`:

```text
npm ci                         # exit 0; node_modules was absent
npm test -- --run src/features/lawn/lawnProjectorFold.test.ts src/features/lawn/lawnSessionFold.test.ts src/lib/bus/hub-provider.test.tsx
# 90 tests passed across 3 files; exit 0

npm run build                  # tsc --noEmit and Vite production build passed; exit 0
# existing bundle/PURE-comment warnings recorded, not treated as failures

dotnet build gk-core/src/FusionRpg.Server/FusionRpg.Server.csproj
# restored build passed, 0 warnings/errors; exit 0

dotnet test gk-core/tests/FusionRpg.Server.Tests/FusionRpg.Server.Tests.csproj
  --filter "FullyQualifiedName~EventIngestIsolationTests"
# 3 passed; exit 0
```

The complete eleven-path `verify-change.ps1` run was executed with the active acceptance session and completed with `WEB_ACCEPTANCE_VERIFY_EXIT=0`. Its disk-backed log SHA-256 is `48E8910C977052AC7C4596FC07A4A889A1814C115AA090265707367A3B64705C`. The log includes expected `ECONNREFUSED` messages from isolated hub-provider tests that intentionally have no live server; those messages did not fail the test run and are not browser evidence.

The first server `--no-restore` build failed because a clean worktree had no assets file. It is excluded; the restored build above is the valid result.

## Browser boundary

No browser session, running server, or live SignalR connection was used. The code/build/test evidence above is not a browser claim. After this exact SHA is accepted and merged, the manager must run the local web/server review flow and record browser evidence separately.

## Remaining requirements

1. Commit the reviewed eleven code/test paths and this report at an exact SHA.
2. Run the focused web tests/build and the path-owned verifier from a clean detached checkout.
3. Validate/write the exact-SHA artifact and merge only that SHA.
4. Collect browser recovery evidence against the merged code; keep any server/live limitation open if it cannot be reproduced.

<<<REPORT {"status":"partial","summary":"Manager review corrected the worker's npm working-directory error. From the web package directory, 90 focused Vitest tests, the web build, restored Server build, 3 server isolation tests, and the complete eleven-path verify-change run all passed. No browser/live proof has been collected; exact-SHA clean-checkout acceptance remains.","changed_files":["gk-core/src/FusionRpg.Contracts/Dtos.cs","gk-core/src/FusionRpg.Server/EventIngest.cs","gk-core/src/FusionRpg.Server/RpgHub.cs","gk-web/web/fusion-rpg-web/src/features/lawn/LawnPage.tsx","gk-web/web/fusion-rpg-web/src/features/lawn/lawnProjectorFold.ts","gk-web/web/fusion-rpg-web/src/features/lawn/lawnSessionFold.ts","gk-web/web/fusion-rpg-web/src/lib/bus/hub-provider.tsx","gk-web/web/fusion-rpg-web/src/lib/bus/log-store.ts","gk-web/web/fusion-rpg-web/src/features/lawn/lawnProjectorFold.test.ts","gk-web/web/fusion-rpg-web/src/features/lawn/lawnSessionFold.test.ts","gk-web/web/fusion-rpg-web/src/lib/bus/hub-provider.test.tsx","tasks/reports/resume-03-web-acceptance-20260925.md"],"verification":["npm ci passed from gk-web/web/fusion-rpg-web","90 focused Vitest tests passed","npm run build passed","restored FusionRpg.Server build passed with 0 errors","3 EventIngestIsolationTests passed","complete eleven-path verify-change exited 0; log SHA-256 48E8910C977052AC7C4596FC07A4A889A1814C115AA090265707367A3B64705C"],"open_issues":["exact-SHA clean checkout and artifact are not yet created","browser/live recovery evidence is absent","isolated test ECONNREFUSED messages are expected and not browser proof","initial no-restore server build was invalid and excluded"],"next_steps":["commit exact reviewed SHA","clean-checkout rerun and acceptance artifact","merge exact SHA","run local server/browser recovery evidence","keep live/browser failures open if not reproducible"]} REPORT>>>
