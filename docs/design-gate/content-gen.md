# Design gate — content-gen

**Species generation and the seedsmith pipelines.**

Index: [../DESIGN-GATE.md](../DESIGN-GATE.md) §1. Each row keeps its original `DESIGN-GATE.md:<line>` number in a trailing comment, so a citation to the index still points at the topic it named before the split.

| If you're about to touch… | You MUST have read | What sessions get wrong |
|---|---|---|
| **Creature species generation / seedsmith's creature pipelines** | [architecture/creature-seed-map.md](architecture/creature-seed-map.md) · [architecture/creature-seed/](architecture/creature-seed/) module specs | **Seed → concrete → per-player is binding for every generator, creatures included** (`tasks/seed-to-concrete-plan.md`). Species *stats* are deterministic and shared; only *effects* roll, per player, at runtime — never assume a species table is finished content once generated | <!-- DESIGN-GATE.md:47 -->
