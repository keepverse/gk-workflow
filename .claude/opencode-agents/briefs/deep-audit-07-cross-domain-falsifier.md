# Follow-up audit 07 — cross-domain falsifier

## Goal

Independently try to disprove the candidate findings collected from the six initial audit lanes. Treat every candidate as an untrusted hypothesis, not as a conclusion. Recheck the current merged tree and issue a compact verdict for each: confirmed, rejected, or unresolved with the exact missing evidence.

## Candidate hypotheses

- Delve wild/cage join routes trust caller-supplied room/candidate and price rather than server-owned provenance and `OfferFloor` (`gk-core/src/FusionRpg.Server/DelveWildEndpoints.cs`).
- Battle live derived updates use `BattleDerivedModifierLedger` outside ActorHub; battle apply reports pre-clamp values while the sink clamps/narrows HP.
- Web cold join/reconnect lacks authoritative hydration/replay; snapshot bindings lose empty/reverse-order edges; cross-match events and error-vs-stale states are conflated.
- Expedition collect has no durable post-commit result replay; active membership is only instance-local; archived save IDs can pass route admission; concurrency/crash tests are missing; wire DTOs are server-local.
- FamilyExpandGen has registry/version/refusal/pool/provenance/fixture gaps despite byte-stable `--check`; passive-tree vocabulary mirrors are stale.
- Verification/release and QC claims may omit merged-head, environment, browser, live, or cross-lane evidence. The verification lane's report will be added to the manager handoff before final consolidation; inspect the current lane artifacts if needed.

## Method

- Read-only and worktree-local. No edits, commits, deployment, package installation, full suite, or background tasks.
- Use only relative paths inside the current worktree. Never inspect `.claude/opencode-agents/agents`, another worktree, the main checkout, or any absolute path outside this worktree; the candidate list is sufficient input. If a tool requests external-directory permission, skip it and continue.
- Read `docs/DESIGN-GATE.md`, the relevant architecture SSOTs, and the current manager handoff. Verify code at the current HEAD, not only the candidate report.
- For each candidate, inspect the smallest decisive path and run one focused test, static reproduction, or contract check where feasible. Do not infer browser/live behavior from static code. Within 24 steps, stop exploring and emit the report; unresolved is a valid verdict.
- Cite `file:line`, exact commands, output, confidence, and the strongest falsification. Separate a real defect from a missing test, stale prose, and unknown deployment contract.

## Required report

Return a table of every hypothesis with verdict, evidence, current severity if confirmed, and next verification. Then report cross-lane contradictions, newly discovered P0-P3 findings, open owner/product questions, and an ordered remediation sequence with stop conditions. End with the runner's `<<<REPORT {...} REPORT>>>` block; `changed_files` must be `[]`.

## Verification

- `git status --porcelain`
- `git rev-parse --short HEAD`
- `git log -20 --oneline --decorate`
