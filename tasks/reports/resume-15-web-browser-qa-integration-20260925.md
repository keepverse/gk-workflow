# Browser QA report integration record — resume-15

**Date:** 2026-09-25
**Integrated report:** `tasks/reports/resume-15-web-browser-qa-20260925.md`
**Source worktree:** `.claude/worktrees/opencode-resume-15-web-browser-qa-20260925` (repo-relative reference)

## Hash chain

- Source report SHA-256 before path sanitization: `0EA1C2C079F4D4BB6971479FD57151E66BFAABF88524E57F96FC306C72B80483`.
- Integrated report SHA-256 after replacing the machine-local path: `5CDDA3AF5CD5011D94DB831A324E3B96C92AA93CB4661C9A44AA45BE4DA7F527`.

The source and integrated hashes are intentionally different: sanitization changed the report bytes.
The integrated report is the only tracked report; the raw `.playwright-cli` evidence remains external
and ignored in the source worktree. This hash chain does not claim to preserve those raw files.

## Claim boundary

This integration records **PARTIAL** browser evidence only:

- proven: web production build, local server boot, `/health`, byte-identical built index, SPA boot,
  and the real no-live-game recovery state;
- unproven: stale-to-authoritative-ready recovery, active-match HUD/occupant behavior, and
  cross-match isolation.

The report lane is not a feature acceptance. It must not be used to claim that the live or
cross-match browser gate is green.
