# Design gate — persistence

**Data, SQL and schema.**

Index: [../DESIGN-GATE.md](../DESIGN-GATE.md) §1. Each row keeps its original `DESIGN-GATE.md:<line>` number in a trailing comment, so a citation to the index still points at the topic it named before the split.

| If you're about to touch… | You MUST have read | What sessions get wrong |
|---|---|---|
| **Data / SQL / schema** | [architecture/data-architecture.md](architecture/data-architecture.md) · [contributing/architecture-map.md](contributing/architecture-map.md) | SQL lives **only** in `FusionRpg.Data`. `guard-dal.py` enforces it — and scans only `src/`, so `tools/` is a blind spot | <!-- DESIGN-GATE.md:53 -->
