---
description: Start spec-driven development — write a structured specification before writing code
---

Invoke the agent-skills:spec-driven-development skill.

Begin by understanding what the user wants to build. Ask clarifying questions about:
1. The objective and target users
2. Core features and acceptance criteria
3. Tech stack preferences and constraints
4. Known boundaries (what to always do, ask first about, and never do)

Then generate a structured spec covering all six core areas: objective, commands, project structure, code style, testing strategy, and boundaries.

If the request bundles several independently testable capabilities, first propose a capability map (module ids, dependency direction, build order) per the skill's Phase 0 and get it approved, then spec each module in dependency order.

Save the spec and confirm with the user before proceeding.

**Where it goes — no condition to evaluate.** Capability map → **`docs/architecture/<program>-map.md`**; each module spec → **`docs/architecture/<program>/spec-<module-id>.md`**. Always. **`SPEC.md` at the root is not a default and not a fallback** — do not read it, do not test whether it is occupied, do not write to it. State the paths you wrote.
