# NS6.6 — `/idea-ui` pass over `spec-notify-centre.md`

| Criterion | Command | Result |
|---|---|---|
| `docs/architecture/notify-centre-ideal.md` per `idea-ui-phase.md`: the bug/shape-to-module map naming the reused pieces (`tool-search` category filter, `chip` for severity/state, ERM **Row**) and any piece that does not exist yet; R14's home taken as ruled, not reopened | wrote `docs/architecture/notify-centre-ideal.md`, all 11 required sections | `tool-search` (chrome, "Search", README.md:49/192), `chip` (Chip kind, "Rail option", README.md:53/187), `channel-row` (Row kind, README.md:63) all cited real; recipe + React mount named as real gaps; R14 stated as ruled, §1/§10 both say not reopened |
| `python scripts\audit-doc-citations.py --scope docs/architecture --strict` reports no HIGH for `notify-centre-ideal.md` | `python scripts/audit-doc-citations.py --scope docs/architecture --strict` | first pass: 2 HIGH (the not-yet-authored recipe/surface file paths read as literal citations); reworded to name them without a backtick'd tracked-file path; second pass: 0 findings for `notify-centre-ideal.md` |

**Honest finding named in the doc itself (§1):** neither `docs/guide/the-loops.md` nor
`docs/guide/the-game.md` names a loop for Chronicle/Notices — checked directly (grep for
Chronicle/notification/history/review/dossier in both, zero matches). Stated as a real gap in the
source docs rather than invented.

**Cross-program dependency named, not resolved (§4):** the centre's own "same `ChannelControl` as
the rail" requirement depends on `world-notify-source`'s NS5.9 move of that component, which is
blocked on ask A1 (unanswered). Named explicitly so it is not rediscovered mid-React at NS6.11.
