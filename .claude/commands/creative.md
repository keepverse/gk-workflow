---
description: Creative mode — the owner is the customer, you are the hired creative project manager. One intake interview, then invent and ship one or more new game mechanisms to the owner's landing branch with no human (reviewer agents and screenshot gates stand in for the owner)
---

Invoke the `creative-mode` skill and follow it exactly. The policy it loads is
`docs/contributing/creative-mode.md` — binding, and it wins over the skill.

**The one conversation: the intake.** Before any work, interview the owner (policy §0): the brief,
the charter (runtimes, exact models, token budget, concurrency, stop rule), the landing branch, the
creative game install (an existing clone, or a source and target the owner permits you to copy), and
content generation (local LM Studio by default; a cloud provider only on the owner's explicit command
with its details). Confirm the brief once. After that, never ask again — also not when a later session
resumes the program.

**What the owner gets:** each shipped feature merged into the landing branch, a report per feature at
`tasks/<program>-report.md`, and a program report at `docs/ideas/<program-id>/report.md` — the pitch,
how to try it, every decision made in the owner's place, the evidence including judged screenshots,
and the honest gaps. A killed or NO-GO feature is reported, not merged.

**What the program never does** (policy §3): add a loop, an element, a class, a clock or new fiction;
amend a locked decision; merge anywhere but the landing branch; push or open a PR; touch the owner's
`dist/` server, port 5088, save or own game install; run `deploy-play.py --restart-server`; call a
non-local LLM without an intake grant; start a worker outside the charter.

Start it from a session in the main tree, not from a worktree-isolated session.

ARGUMENTS: $ARGUMENTS — an optional theme (a loop, a Vision hole from `docs/guide/the-loops.md`, or a
phrase) that seeds the intake's first question.
