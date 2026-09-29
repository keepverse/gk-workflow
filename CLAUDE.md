# CLAUDE.md — pointer

**The contributor guide is [AGENTS.md](AGENTS.md).** Read that; it is the single instruction file for
this repo and it carries every hard rule, the session-boundary policy, the verification boundary
(`python scripts\verify-change.py --paths <files> --session <id>`) and the context tooling
(CodeGraph + caveman).

This file is kept only because paths still resolve to it:

- **~36 test files** use it as a repo-root marker — they walk up from `AppContext.BaseDirectory`
  looking for it and throw `"repo root not found"` without it (`docs/contributing/session-boundary.md`).
- Code comments across `src/`, `tests/`, `tools/` and `web/` still cite rules by name. Those citations
  are being repointed at `AGENTS.md`; until a given one moves, the rule text is in `AGENTS.md` under the
  same heading.

**What happened (2026-09-27).** The two files were near-duplicates: ~1% line-identical, but the same
rules reworded. Every lane paid to read both — about 21k tokens per session of overlap before writing a
line. The unique content was moved into `AGENTS.md` (the CodeGraph + caveman tooling section, the
"read before structural changes" links, and the `docs/PRINCIPLES.md` digest pointer) and the duplicated
prose was dropped. Nothing was lost; one file now says it once.

If you are an agent: **read `AGENTS.md`, not this file.** If you are a tool resolving a repo root, this
file's presence is the marker and that is intentional.
