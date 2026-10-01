# Spec: `pvz-write-surface`

**Program:** [`solid-enforcement`](../solid-enforcement-map.md) · **Wave 2** · depends on:
`guard-runner`, `retire-atk` (both edit around `EntityStatWriter`'s retired atk lines).

## Objective

`CLAUDE.md`'s first hard rule: *"Every RPG feature lives in the RPG layer — never in the PvZ game."*
The RPG observes PvZ and contributes deltas. Its narrow Unity write surface constrains exactly one
thing, which persistent vanilla stat changes are possible. On 2026-09-16 that surface was
deliberately **narrowed**: five damage-equation fields stopped being written, because writing them
made the RPG's own combat math pay twice:

| Retired Unity field | Where | Why (from the code's own comment) |
|---|---|---|
| `Plant.attackDamage` | `EntityStatWriter.cs:120` | the RPG's `combat.power` already pays attack; writing it too double-paid |
| `Zombie.theAttackDamage` | `EntityStatWriter.cs:199` | same, zombie side |
| `Plant.theShieldHealth` | `EntityStatWriter.cs:146` | `ShieldGate` and the host game both absorbed the same shield |
| `Zombie.theArmor` | `EntityStatWriter.cs:219` | a composed flat armour made PvZ's calculator redundant |
| `Zombie.takeDmgMultiplier` | `EntityStatWriter.cs:220` | a legal passive-tree target, so it was a latent double-pay |

**These live on as commented-out lines.** Nothing stops them being uncommented. Nothing stops a
*sixth* field being written tomorrow either, and a new write is precisely how a feature slides from
the RPG layer into "changing what PvZ is" (the 2026-08-29 aura incident started from reading this
surface as the design boundary).

This module pins the surface: **a closed set of fields that may be written, and a closed set that
never may**.

## Design

### Extend `guard-single-writer`, don't fork it

`gk-fusion/scripts/guard-single-writer.py` already owns this territory. It holds a list of field-assignment
patterns and the four files allowed to contain them (`EntityStatWriter.cs`, `ZombieCombatFields.cs`,
`UniqueBoundLoadout.cs`, `EntityPositionWriter.cs`). That answers **"which files may write"**. This
module adds the two missing questions to **the same guard** (the O in SOLID: extend the gate that
exists; a second guard over the same files is the dual-fold defect wearing a script):

- **W2 — which fields a writer file may write.** For each allowed file, parse its live (comment-free)
  assignments of the form `p.<field> =`, `z.<field> =`, and `ZombieCombatFields.Set<X>` calls. The set
  must be a subset of that file's pinned field list.
- **W3 — retired fields are written nowhere.** The five fields above may not be assigned in *any*
  file, allowed files included. A comment-free scan of all of `gk-fusion/src/FusionRpg.Injector/**`.

### The pinned field set (measured 2026-09-18, comments stripped)

`EntityStatWriter.cs` writes **23** distinct live targets:

- **Plant (11):** `thePlantHealth`, `thePlantMaxHealth`, `thePlantAttackCountDown`,
  `thePlantAttackInterval`, `thePlantProduceCountDown`, `thePlantProduceInterval`, `thePlantSpeed`,
  `attackSpeedAdder`, `moveSpeed`, `theLevel`, `shootingLevel`.
- **Zombie (12):** `SetHp` and `SetMaxHp` via `ZombieCombatFields`, plus `theFirstArmorHealth`,
  `theFirstArmorMaxHealth`, `theSecondArmorHealth`, `theSecondArmorMaxHealth`, `theSpeed`,
  `theOriginSpeed`, `uniqueSpeed`, `butterSpeed`, `coldSpeed`, `freezeSpeed`.

The other three allowed files get their own lists, measured the same way at build time.

**The list is a closed vocabulary, and its size is pinned deliberately, with the reason in the
script.** A new writable Unity field is a reviewed architecture change, and the comment beside the
list says so: *"Adding a field here means the RPG writes a persistent vanilla value. Read CLAUDE.md
'Every RPG feature lives in the RPG layer' first. Most features that seem to need a new field are an
RPG-layer channel that already exists."*

### Comment stripping

This is the detail that makes W2/W3 precise. A naive scan of `EntityStatWriter.cs` finds
`attackDamage` and `theAttackDamage`, because the retired lines survive as comments carrying their
history, and the file is right to keep them. The guard removes `/* … */` blocks and `//`-to-end-of-line
before scanning (string literals containing `//` do not occur in these files; verify at build time and
fail loudly if one appears). The measurement above was taken exactly this way.

### What happens to the retired lines themselves

Nothing. They stay as comments. They are the trail explaining *why* each field is not written, and W3
makes them safe to keep. A tidy-up that deleted them would destroy the reasoning while the guard
already provides the protection.

## Commands

```powershell
python gk-fusion/scripts/guard-single-writer.py
.\scripts\run-guards.ps1 -Only single-writer
dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~SingleWriter"
```

## Project structure

| Path | Change |
|---|---|
| `gk-fusion/scripts/guard-single-writer.py` | W2 per-file field lists; W3 retired list; comment stripping |
| `gk-core/tests/FusionRpg.Guard.Tests/` single-writer tests (locate at build; add if none) | falsifiers below |
| `gk-core/scripts/enforcement-registry.v1.json` | invariant row `claude-rpg-layer-only` → `single-writer` (no new guard row) |

## Testing strategy

Falsifiers against temporary copies of the writer files:

- Uncommenting `p.attackDamage = …` fails **W3** (inside an allowed file, which the old rules could
  never catch).
- Adding `z.theZombieType = …` to `EntityStatWriter.cs` fails **W2** (a new field).
- A line `// z.theArmor = …` passes (comment).
- `z.theSpeed == x` (a comparison) passes, reusing the existing `(?!=)` convention.

The real tree passes.

## Boundaries

- **Always:** strip comments before scanning. Measure each writer file's list, don't guess it.
- **Ask first:** adding any field to a list. That is the RPG-layer question, and the owner's.
- **Never:** delete the commented retired lines. Never write a retired field.

## Success criteria

- [ ] W2 and W3 enforced within `guard-single-writer`, which stays one guard and gating.
- [ ] Every falsifier behaves as listed, including the uncommented-`attackDamage` case.
- [ ] Per-file field lists measured and pinned with the reason comment.

## Self-audit — the debate

**Objection: "The single-writer guard already lists `attackDamage`. Isn't W3 redundant?"** No. The
existing list says *which files* may write `attackDamage`, and `EntityStatWriter.cs` is on the
allowed list. So uncommenting line 120 **passes today's guard**. W3 is the first rule anywhere that
says a field is retired *everywhere*.

**Objection: "Pinning 23 fields will fail the first legitimate new write."** It is meant to. Such a
write is an architecture decision about the PvZ boundary, and the hard rule says to decide it
deliberately. A failing guard with a message pointing at that rule is the cheapest possible way to
make it deliberate.

**Objection: "Why depend on `retire-atk`?"** `retire-atk` edits code around these lines, and
`UniqueBoundLoadout.cs` (an allowed file) loses its atk grant there. Measuring the field lists
*after* it lands means pinning the post-retirement truth once, instead of pinning and immediately
re-pinning.

## Gaps found and closed while writing

- **The first draft proposed a new `guard-pvz-write-surface.ps1`, which was never created.** Reading
  `guard-single-writer.py` showed it already owns the file boundary. A second guard over the same
  files would split one invariant across two scripts, so it was folded in as W2/W3.
- **The raw grep counted the commented-out atk lines as live writes** (26 targets, not 23). Comment
  stripping is now a stated requirement, with the measured number.
- **The allowed-files list has four entries,** and the first draft only measured one. Each now gets
  its own measured list.
