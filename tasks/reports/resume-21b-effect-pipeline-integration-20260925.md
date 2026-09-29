# Resume 21b effect-pipeline triage integration record

**Date:** 2026-09-25
**Integrated report:** `tasks/reports/resume-21b-effect-pipeline-triage-20260925.md`
**Disposition:** **DONE TRIAGE / EPL1.1 READY FOR A FENCED IMPLEMENTATION LANE**

## Hash chain

- Source report SHA-256: `D504DEB7D1D7E9B678A8A0B2AE6E56D6E97EEE1B33B5FE9185DCECBB7870A772`.
- Integrated report SHA-256: `D504DEB7D1D7E9B678A8A0B2AE6E56D6E97EEE1B33B5FE9185DCECBB7870A772`.

The report bytes are unchanged. It is a read-only dependency decision, not product acceptance.

## Manager review

The current tree independently confirms the key census: `effect-pipeline | R-bold | 6 | 0 | 10 | 0`
for open blocks, done blocks, unticked boxes, and shaded blocks. The report verifies the four EPL1.1
paths are absent and identifies the closed five-value vocabulary, rarity-collision guard, and
family-coverage contract.

EPL1.1 is bounded to:

- `gk-data/packs/fusion/data/seed/items/_registry/power-classes.v1.json` (**new** registry; proposed EPL1.1 file);
- `gk-core/src/FusionRpg.Core/Effects/Atoms/AffixPowerClass.cs` (**new** C# mirror; proposed EPL1.1 file);
- `gk-core/tests/FusionRpg.Core.Atoms.Tests/Atoms/AffixPowerClassTests.cs` (**new** mirror tests; proposed EPL1.1 file);
- `gk-forge/tools/seedsmith/tests/test_power_class_registry.py` (**new** registry/provenance tests; proposed EPL1.1 file).

The implementation must not add a model call, generated affix rows, Data columns, channel policy,
runtime wiring, or a population-count pin. EPL1.3's owner charter and EPL2.1's channel-SSOT ruling
remain later gates; stale population/caller/fence claims are not silently adopted.

## Dispatch boundary

A new implementation lane may be opened for EPL1.1 only with exactly the four paths above, the
closed-vocabulary/rarity/coverage tests, the current Core.Atoms test project, and the path-owned
verifier. No later row is included.
