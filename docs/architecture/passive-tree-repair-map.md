# Capability Map: passive-tree-repair spec round (anchors + P2.3) — FLIPPED 2026-09-15

**Initiative:** `passive-tree-repair` spec round, 2026-09-15. Parent program map:
`docs/architecture/passive-tree-map.md`. Idea input:
`docs/architecture/passive-tree-repair-ideal.md` (supersedes the "request from the power
program" plan — there is no active power-program session, so this program authors the anchors).
Owner answers 2026-09-15: both tracks; intervals are Milliseconds; status cliff fixed by rescale
AND m1 floor; rate channels get per-channel v3 pins too (overrides the ideal doc's §"shape",
which exempted them — the v3 spec defines pin semantics per unit class).
**FLIP 2026-09-15 (ladder principle, owner: "replace doesn't work in this game principle"):**
`structural-rows` and `mechanism-carriage` are REJECTED, not deferred — Replace substitutes a
constant where the design requires `f(Θ)` (parity §2, PS-3, §5.1). A2 → option (b), exclude.
Module ids stay stable (never renamed); rejected rows stay visible below with their verdict.

| Module id | Responsibility | Depends on | Status |
|---|---|---|---|
| pin-table-v3 | `power-scale.v3.json` pins (GameUnits + regen/s + rate channels) + `FlatReferenceBase` extension + §10 rows | — | active |
| status-anchor | `status.apply` t1 chance/duration + shares + E43 `when.chance` emitter + `effectiveApplyScale` rescale + status m1 floor (unsuppresses §4.3) | — | active |
| interval-ledger | Milliseconds ruling for `attackInterval`/`produceInterval` + ledger entry + channel-policy rows | — | active |
| structural-rows | Amount-less Replace/Flag emission | — | ⛔ REJECTED — ladder principle (constant vs `f(Θ)`) |
| mechanism-carriage | Ladder-valued Replace carriage | structural-rows | ⛔ REJECTED — same verdict; P6.1's surviving half (mechanism-class carriage) needs no new spec |

Build order: pin-table-v3, status-anchor, interval-ledger (any order, parallel-safe). No
downstream module remains — P6.1 proceeds on `spec-status-anchor.md` + `spec-tree-resolve.md`.

**Interfaces at the boundary:** E43 consumes v3 pins through the existing
`flatReferenceBaseGameUnits` delegate (no signature change — the contract lives in
`spec-tree-catalog`/E43's spec, not here); `when.chance` is validated by `AtomRowValidator`'s
existing chance arm; structural rows are defined by the `structural-rows` spec and consumed by
`mechanism-carriage` — the row shape contract lives in the provider (`structural-rows`).
