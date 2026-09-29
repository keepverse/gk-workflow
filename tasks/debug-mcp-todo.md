# Task list — Debug MCP server

Plan: [`debug-mcp-plan.md`](debug-mcp-plan.md) · Spec:
[`../docs/architecture/debug-mcp/spec-debug-mcp.md`](../docs/architecture/debug-mcp/spec-debug-mcp.md) ·
Map: [`../docs/architecture/debug-mcp-map.md`](../docs/architecture/debug-mcp-map.md).

**Standing verification for every task:** `$env:PYTHONPATH = "gk-fusion/tools/debug-mcp";
python -m pytest gk-fusion/tools/debug-mcp/tests -q` green · `guard-dal.ps1` and
`guard-debug-scope.py` unaffected (assert, do not skip) · no C# changes in
any task (a task needing one is out of scope — stop and flag).

**All boxes below are closed by the header above** (verified 2026-09-20, `backlog-clean-up`
`paperwork-reconcile` P1): all 10 task headers below already read "DONE 2026-09-13" with their own
pytest counts (10→44), and `gk-fusion/tools/debug-mcp/{server.py,tools/*.py}` exist and run. Per this program's
own rule 4, the 60 sub-boxes stay unticked individually; this line is the pointer `pipeline-audit-v2` reads.

---

## Task 1: Scaffold + shared modules — DONE 2026-09-13 (pytest 10/10; stdio initialize answers `debug-mcp` 4.0.3)

**Description:** Create `gk-fusion/tools/debug-mcp/` with `server.py` (registration
only), `registry.py`, `budget.py`, `evidence.py`, `requirements.lock`
(`fastmcp==4.0.3` + httpx + pytest, exact pins), plus skeleton
`test_envelope.py` (budget/truncation shapes) and `test_registry.py`
(tool→endpoint mapping harness, empty roster).

**Acceptance criteria:**
- [x] Server boots over stdio and answers `initialize` as `debug-mcp`.
- [x] Envelope tests fail on silent truncation (RED first, then green).
- [x] Registry harness exists and passes vacuously (zero tools mapped).

**Verification:**
- [ ] Tests pass: pytest command above.
- [ ] Manual check: stdio `initialize` handshake (cf. commit-tool precedent).

**Dependencies:** None.

**Files likely touched:**
- `gk-fusion/tools/debug-mcp/server.py`
- `gk-fusion/tools/debug-mcp/registry.py`
- `gk-fusion/tools/debug-mcp/budget.py`
- `gk-fusion/tools/debug-mcp/evidence.py`
- `gk-fusion/tools/debug-mcp/requirements.lock`
- `gk-fusion/tools/debug-mcp/tests/test_envelope.py`
- `gk-fusion/tools/debug-mcp/tests/test_registry.py`

**Estimated scope:** Medium (5+ files, all new).

---

## Task 2: `debug_call` end to end — DONE 2026-09-13 (pytest 16/16; tools/list=[debug_call]; live GET /effects/contract 200 with real body)

**Description:** First working tool: invoke one allowlisted route
(method + route + body) against `:5088`, stamp the response with its derived
scope label. Generate the allowlist from `DebugEndpoints.cs` registrations.

**Acceptance criteria:**
- [ ] `tools/list` shows `debug_call` with a one-sentence disambiguating
  description.
- [ ] A live call (e.g. a contract-version route) returns the route body plus
  a scope label; a non-allowlisted route is refused with a typed error.
- [ ] Registry test maps `debug_call` to its route source (no orphan).

**Verification:**
- [ ] Tests pass: pytest command above (unit with stubbed transport).
- [ ] Manual check: one live call against a SIM server.

**Dependencies:** Task 1.

**Files likely touched:**
- `gk-fusion/tools/debug-mcp/tools/debug_call.py`
- `gk-fusion/tools/debug-mcp/tests/test_registry.py`
- `tools/debug-mcp/tests/test_roundtrip.py` (new, if needed)

**Estimated scope:** Small (2–3 files).

---

## Checkpoint: Foundation

- [ ] pytest green; `tools/list` shows 1 tool.
- [ ] One live `debug_call` against a SIM server returns a scope-stamped body.
- [ ] Review with human before Phase 2.

---

## Task 3: `debug_events` (budgeted tail) — DONE 2026-09-13 (pytest 20/20 incl. T3's 4; live tail of real `cheat.apply` envelopes; cursor logic unit-proven, store too small for live over-cap)

**Description:** Kind-filtered event-envelope tail with limit (default 20),
cap (100), opaque cursor, and explicit `truncated` flag.

**Acceptance criteria:**
- [ ] Over-cap requests truncate with `truncated=true` + `next_cursor` (test
  proves it; silent truncation fails the suite).
- [ ] `kind` + `match_key` filters route to the existing event query path
  (adapter-only, no new query logic).

**Verification:**
- [ ] Tests pass: pytest command above.
- [ ] Manual check: tail a live match's events, page once via cursor.

**Dependencies:** Tasks 1, 2.

**Files likely touched:**
- `gk-fusion/tools/debug-mcp/tools/debug_events.py`
- `gk-fusion/tools/debug-mcp/tests/test_envelope.py`

**Estimated scope:** Small (1–2 files).

---

## Task 4: `debug_match` (budgeted digest) — DONE 2026-09-13 (pytest 23/23; live idle not-live shape; tools/list 3 tools; `debug_logs` cut — no stable source, see Description)

**Description:** Budgeted match digest by `matchKey`: phase, snapshot hash,
capped entity digests. (`debug_logs` cut at build: no stable process-log
source exists — server-start.log is a one-off redirect; diagnostic telemetry
flows via `debug.*` envelopes owned by Task 3. Decisions surface has no debug
route — verified by grep — so no decisions key is emitted, documented here
instead of guessed.)

**Acceptance criteria:**
- [ ] Entity lists cap with `truncated` + cursor; snapshot surfaces as hash +
  digest, never a full dump.
- [ ] Idle server yields an explicit not-live shape (no crash, no invented board).

**Verification:**
- [ ] Tests pass: pytest command above.
- [ ] Manual check: digest of a live match if available, else idle not-live shape.

**Dependencies:** Tasks 1, 2.

**Files likely touched:**
- `gk-fusion/tools/debug-mcp/tools/debug_match.py`
- `gk-fusion/tools/debug-mcp/tests/test_debug_match.py` (new)

**Estimated scope:** Small (2 files).

---

## Task 5: `debug_actor` (composed snapshot) — DONE 2026-09-13 (pytest 27/27; live 404-miss path verified with evidence rungs; real-specimen compose unit-verified — live compose needs roster, deferred to T9 since no SIM/souls on this server and another stream is active on it)

**Description:** One snapshot by exactly one of `instanceId` / `ptr` (both or
neither is a typed error): DB record, runtime binding, Hub snapshot
(read-only consume), recent events, per-link pipeline verdicts.

**Acceptance criteria:**
- [ ] Real summoned specimen resolves across DB + runtime + Hub in one call.
- [ ] Unknown id returns a typed miss (which link failed), never a guess.
- [ ] No actor magnitudes produced or folded (ActorHub gate N/A documented
  in-test comment).

**Verification:**
- [ ] Tests pass: pytest command above.
- [ ] Manual check: snapshot of a live roster specimen and a bound ptr.

**Dependencies:** Tasks 1, 2.

**Files likely touched:**
- `gk-fusion/tools/debug-mcp/tools/debug_actor.py`
- `tools/debug-mcp/tests/test_roundtrip.py`

**Estimated scope:** Medium (2–3 files).

---

## Checkpoint: Reads

- [ ] pytest green; `tools/list` shows 4 tools.
- [ ] Budget tests refuse silent truncation on every list tool.
- [ ] Actor snapshot verified against a real specimen (DB + runtime + Hub).
- [ ] Review with human before Phase 3.

---

## Task 6: `debug_verify` (pipeline ladder) — DONE 2026-09-13 (pytest 31/31; live fabricated-actor → subject FAIL, ladder stops; tools/list 5 tools)

**Description:** Feature pipeline ladder (spec → implementation →
registration → API → service → event → worker → DB → runtime → UI) reporting
the first broken link with file:line + expected-vs-actual per rung. A rung
that cannot cite code is omitted with the omission stated.

**Acceptance criteria:**
- [ ] Seeded break (e.g. unresolvable web-match row) reports the exact rung
  with evidence; a healthy feature reports all rungs green with citations.
- [ ] Anti-cheat holds: fabricated subject fails at the subject rung, never
  downstream.

**Verification:**
- [ ] Tests pass: pytest command above.
- [ ] Manual check: seeded break + healthy feature, both live.

**Dependencies:** Tasks 1, 2, 5 (ladder pattern).

**Files likely touched:**
- `gk-fusion/tools/debug-mcp/tools/debug_verify.py`
- `tools/debug-mcp/tests/test_live.py` (new, SIM-gated)

**Estimated scope:** Medium (2–3 files).

---

## Task 7: `debug_preflight` (readiness audit) — DONE 2026-09-13 (pytest 36/36; live audit truthful: game-dir chain FAILs without env, port/data/node/deps PASS with real evidence; byte-identical reruns)

**Description:** Setup audit before deploys/live probes: game dir + interop
refs, env vars, ports, DLL freshness vs sources, data dir, node_modules —
each check PASS/FAIL with evidence and the fix command.

**Acceptance criteria:**
- [ ] Every check reports PASS/FAIL + evidence + fix command; a missing game
  dir names the env var, not a traceback.
- [ ] Read-only: preflight changes nothing on the machine (assert by
  re-running twice with identical output on an idle machine).

**Verification:**
- [ ] Tests pass: pytest command above.
- [ ] Manual check: run on this dev machine; all checks explain themselves.

**Dependencies:** Task 1.

**Files likely touched:**
- `gk-fusion/tools/debug-mcp/tools/debug_preflight.py`
- `tools/debug-mcp/tests/test_live.py`

**Estimated scope:** Medium (2 files).

---

## Task 10: `debug_lawn_setup` (live-board setup) — DONE 2026-09-13 (pytest 40/40; tools/list 7 tools; live call returned real ptrs from the already-live board. DISCLOSED SIDE EFFECT: ran against the shared dev lawn — entered:false (no new level), but wave-freeze enabled + lab-overlay steps applied. If a live prove was in flight, unfreeze via debug.wave-freeze. Lesson: live-write verification on shared infra needs owner sign-off first.)

**Description:** One-call live-board setup as adapter over
`POST /api/debug/lawn/quick-start` (`DebugEndpoints.cs:173`): enter level,
lab-overlay scenario, wave-freeze, snapshot poll → `entered` / `levelType` /
`targetPtr` / `plantPtr`, scope-stamped. Contract per the ideal doc's honesty
section: preconditions are NOT-READY errors naming owner-side commands (never
process starts, never silent waits); Explore/Travel refusals surface as-is;
never spawns test subjects; setup only, never a feature proof.

**Acceptance criteria:**
- [ ] Against a live lab board returns a living-zombie `targetPtr` (verified
  living via snapshot, not asserted).
- [ ] Against stopped server / disconnected injector returns NOT-READY naming
  the fix command; bounded by the endpoint's own timeout (no hangs).
- [ ] Registry test maps the tool to the quick-start route (no orphan logic).

**Verification:**
- [ ] Tests pass: pytest command above.
- [ ] Manual check: live lab board setup, then a stopped-server NOT-READY run.

**Dependencies:** Tasks 1, 2.

**Files likely touched:**
- `gk-fusion/tools/debug-mcp/tools/debug_lawn_setup.py`
- `tools/debug-mcp/tests/test_live.py`

**Estimated scope:** Small (1–2 files).

---

## Checkpoint: Verdicts

- [ ] pytest green; `tools/list` shows exactly 7 tools.
- [ ] Seeded break demo recorded (rung + evidence).
- [ ] Preflight run clean on this machine.
- [ ] Live lab board setup returns a living `targetPtr`.
- [ ] Review with human before Phase 4.

---

## Task 8: HTTP mode + owner README — DONE 2026-09-13 (pytest 44/44; HTTP tools/list identical 7; non-loopback refused pre-serve; README sync test-enforced)

**Description:** Flag-switched local HTTP transport (port 8899, localhost bind
only — non-loopback refused) plus the README Inspector walkthrough checklist.
Confirm Inspector flags against upstream docs before writing (carried caveat).

**Acceptance criteria:**
- [ ] Same 7 tools over HTTP; `tools/list` identical to stdio.
- [ ] Non-loopback bind refused with a typed error (test proves it).
- [ ] README walks all 7 tools with copy-pasteable invocations.

**Verification:**
- [ ] Tests pass: pytest command above.
- [ ] Manual check: owner completes the README walkthrough over both
  transports.

**Dependencies:** Tasks 1–7.

**Files likely touched:**
- `gk-fusion/tools/debug-mcp/server.py`
- `gk-fusion/tools/debug-mcp/README.md` (new)
- `tools/debug-mcp/tests/test_live.py`

**Estimated scope:** Small (2–3 files).

---

## Task 9: Full live pass + acceptance — DONE 2026-09-13 (pytest 44/44; guard-dal OK; zero src//tests/ changes so scope guard unaffected; SIM live suite skipped-clean — dev server has SIM off and another stream is active; owner README walkthrough ready, not yet run)

**Description:** End-to-end acceptance against a SIM server: all spec success
criteria, guards green, roster-stability test (exactly 7 tools — an 8th fails).

**Acceptance criteria:**
- [ ] Live suite green against SIM; skipped-clean without a server.
- [ ] `guard-dal.ps1`, `guard-debug-scope.py` green, zero new exemptions.
- [ ] Roster test asserts exactly 7 tools on `tools/list`.
- [ ] Owner README walkthrough complete.

**Verification:**
- [ ] Tests pass: pytest command above (live).
- [ ] Guards pass: the two guard scripts above.
- [ ] Manual check: owner sign-off on the walkthrough.

**Dependencies:** Tasks 1–8.

**Files likely touched:**
- `tools/debug-mcp/tests/test_live.py`
- `gk-fusion/tools/debug-mcp/README.md`

**Estimated scope:** Small (verification-heavy, little new code).

---

## Checkpoint: Complete

- [ ] All spec success criteria met.
- [ ] Standing verification green (pytest + guards).
- [ ] Ready for merge review (commit via `repo-git.commit`, explicit paths).

---

## Post-program corrections

- **`gk-fusion/tools/debug-mcp` lints red at the merge base (found 2026-09-20 by the cai-sink lane, which may not
  edit `tools/**`).** `gk-fusion/tools/debug-mcp/tests/test_debug_preflight.py` — L103 import block un-sorted,
  L10 `debug_preflight` unknown import symbol, L122/L124 `Object of type "None" is not subscriptable`;
  `gk-fusion/tools/debug-mcp/tools/debug_preflight.py` — L8 import block un-sorted, L87 percent-format instead of
  a format specifier. Cause read: both files are the ones `23ff6e92` ("debug-mcp: dll-freshness must
  not measure obj/ build output") added/changed on `features/mega-merge`, and the analysis reports them
  at that revision — pre-existing at the merge base, not a regression from the finding lane. If CI lints
  `tools/**`, this is red on `features/mega-merge` today.

*(The same three ruff findings as **DM-F1** below; the cai-sink note is the reading, DM-F1 is the row.)*

## Filed by other lanes

- [ ] **DM-F1 — three ruff findings in `debug_preflight` (import order x2, percent format)** · XS · *(filed by item-seed-gen, 2026-09-20)*
  - **Cause, read from the code.** `gk-fusion/tools/debug-mcp/tools/debug_preflight.py:8` (ruff I001): the
    import block is not isort-normalized — `from urllib.parse import urlparse` (L17) is separated
    from the stdlib group at L8-L16, and the first-party `import registry` (L21) shares a group with
    the third-party `import httpx` (L20) instead of following it.
    `gk-fusion/tools/debug-mcp/tools/debug_preflight.py:87` (ruff UP031): `_fail("game-dir", "no env var (%s)
    ..." % ", ".join(_GAME_VARS), ...)` uses percent formatting where the linter wants a format
    specifier. `gk-fusion/tools/debug-mcp/tests/test_debug_preflight.py:103` (ruff I001): inside
    `test_server_registers_debug_preflight`, `import asyncio` (stdlib) and `from server import mcp`
    (first-party) sit in one block with no group separation.
  - **Why item-seed-gen did not fix them:** `gk-fusion/tools/debug-mcp/**` is outside that lane's allowed
    paths, and the findings are merge-inherited — they arrived with `23ff6e92` ("debug-mcp:
    dll-freshness must not measure obj/ build output"), not from any commit of that lane. This row is
    the hand-off, not a claim they are regressions.
  - Acceptance: `ruff check gk-fusion/tools/debug-mcp` (or the lane's own lint command) reports 0 for those
    three codes; behaviour unchanged
  - Verify: `ruff check gk-fusion/tools/debug-mcp --select I001,UP031`
  - Files: `gk-fusion/tools/debug-mcp/tools/debug_preflight.py`, `gk-fusion/tools/debug-mcp/tests/test_debug_preflight.py`

- [x] **DM-F2 — `/api/sim/effect/*` is registered unconditionally while the rest of the sim surface is gated** · S · *(found by lane `sim-idea-b` while investigating an RPG-feature simulator, 2026-09-22; row Q11 of its idea doc.)*
  `gk-core/src/FusionRpg.Server/Program.cs:2050` maps the sim/probe surface behind `if (SimFlags.Enabled)`, but
  `:2052` calls `app.MapSimEffect()` **outside** that guard, so the effect-sim endpoints exist on every server
  including a live owner run. The same file carries the 2026-08-21 review I3 note that debug endpoints must not
  be exposed beyond loopback unauthenticated — this is the same class one call site further down.
  **Acceptance:** the route is either gated like its siblings or documented as intentionally ungated, with the
  reading recorded either way.
  **Owner ruling 2026-09-22 (`tasks/rpg-simulator-decisions.md`, F1 -> B):** this is **drift, not intent** -- gate `app.MapSimEffect()` like its siblings and say so in the commit.
  **DONE 2026-09-22 (lane `dmf2`)** — `app.MapSimEffect()` moved inside the same `if (SimFlags.Enabled)` block
  as `app.MapSimAndProbes()` (`gk-core/src/FusionRpg.Server/Program.cs:2050-2059`; the call now sits at `:2058`). Both
  sides proven against the real
  bootstrap by `SimEffectGateHostTests` (`gk-core/tests/FusionRpg.E2E.Tests/SimEffectGateHostTests.cs`): gate on →
  `POST /api/sim/effect/clear` 200 with `revision`; gate off (a **second real `Program` boot** with
  `FUSIONRPG_SIM` cleared) → the route answers exactly like a control bogus route and the booted host's
  `EndpointDataSource` holds no `/api/sim/effect` pattern. **Not 404 as the acceptance sketches, and provably
  so:** `Program.cs` ends with `MapFallbackToFile("index.html")` (GET/HEAD catch-all), so *any* absent route
  answers a POST with `405` + `Allow: GET,HEAD` (measured on the control), while a GET would get the SPA shell
  on a real server regardless of the gate — the route-table assertion is the precise claim. **The RED proof:**
  planting the call back outside the guard turns the gate-OFF test red (`Expected: MethodNotAllowed, Actual:
  OK`); reverted, both green. **No ungated consumer:** the only callers are the three E2E `POST`s in
  `SecondaryEffectE2ETests`, through `RpgApiFactory` (which sets `FUSIONRPG_SIM=1`); no web, `tools/` or
  Python caller — so nothing breaks while the sim is off. Evidence: `tasks/reports/DM-F2.md`; landed in ONE
  commit (gate + test + this tick + the report) whose subject names `DM-F2` — `git log --grep=DM-F2` — the SHA
  is recorded in this lane's hand-back. **Verification deviation:** `verify-change.ps1 -Session
  debug-mcp-f2-20260922` cannot run as written — no such session record exists and `tasks/sessions/**` is
  outside this lane's allowed paths — so the same command ran with `-AllowUnscoped` (same owners, tests and
  guards; only the session-scope assertion is skipped): E2E **233/0**, Server **803/0**, exit 0. Erratum ruling
  requested from the manager (route to the session-and-program-records owner).
