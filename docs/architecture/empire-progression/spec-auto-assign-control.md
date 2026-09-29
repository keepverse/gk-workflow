# Spec: `auto-assign-control`

**Program:** [`empire-progression`](../empire-progression-map.md) · **Wave A** · depends on:
[`assign-ladder`](spec-assign-ladder.md), and an **`/idea-ui` pass** for placement. **Status:** spec
of the contract only, not reviewed, no build authorized.

## Objective

Close **W2**: the auto-assign feature is unreachable because nothing emits its bus event. Two handlers
listen (`gk-web/web/fusion-rpg-web/src/ui/actor/AptitudesTab.tsx:261`,
`gk-web/web/fusion-rpg-web/src/features/species-build/SpeciesBuildPanel.tsx:116`), the event is declared
(`gk-web/web/fusion-rpg-web/src/features/gui-lego/aptitudesSurfaceBus.ts:10,24`), and no control anywhere
emits it. So the handler's `rule` defaults to `"even"` with no caller able to set anything else.

**Placement is not decided here.** The ideal is explicit (*"UI. Where an auto-assign control lives is
`gui-lego`'s question and needs `/idea-ui`, not this page"*), and DESIGN-GATE's player-menus row
requires `/idea-ui` before `/spec` on a menu. This spec fixes what any placement must satisfy, so the
`/idea-ui` pass decides layout only.

## Design — the contract any placement must meet

| # | Requirement | Source |
|---|---|---|
| C1 | The control lists the rules the server returns for this scope, never a hardcoded FE list | `assign-ladder` owns the rule set |
| C2 | Choosing a rule emits `aptitude.autoAssign` with `{ rule }` on the surface bus; nothing else | the existing handlers' payload shape |
| C3 | The result is a **draft**. Nothing persists until the existing Confirm or Activate | `spec-aptitude-auto-assign.md` E1 |
| C4 | A refused rule shows its named reason and offers `even` | `spec-aptitude-auto-assign.md:62-63` |
| C5 | Mode C (no species) hides `species-favour` rather than letting it refuse | existing mode rule |
| C6 | A default build, when shown, is labelled as suggested, and the control offers "keep my own" as the absence of an action, never as a lock | R-Q3, and *"You are not a class"* |
| C7 | Built from existing pieces and the panel shell; no god component | `gui-lego-ideal.md` |

### Rule labels

Rule ids are engine vocabulary. Player-facing labels come from the catalog convention DESIGN-GATE's UI
row requires (*"Player names … load from `gk-core/data/tuning/*-catalog.v{n}.json`"*), never an FE union of
strings. The `/idea-ui` pass names the catalog key.

## Seedsmith / generator

**None.** FE surface over a server route.

## Tunables

None. The rule list and order come from `assign-ladder`'s tuning.

## ActorHub gate

**Not applicable.** A draft is not an actor number until the player confirms, and then it travels the
existing allocate path.

## Integer widths and the power ladder

Not applicable. Shares are rendered, not computed, in the FE.

## Commands

```powershell
cd web\fusion-rpg-web
npm test -- --run aptitude
npm run build
npm run test:e2e -- aptitude-auto-assign
```

## Project structure

Decided by the `/idea-ui` pass. Fixed here: the emitter lives in a gui-lego piece or the panel chrome
that already hosts the aptitudes surface; the Playwright spec is
`gk-web/web/fusion-rpg-web/e2e/aptitude-auto-assign.spec.ts` (new).

## Code style

```ts
// the only thing the control does on choose
typedBus.emit("aptitude.autoAssign", { rule });   // rule: one id from GET suggestions, never a literal list
```

## Testing strategy

1. **Unit:** choosing each server-listed rule emits exactly one `aptitude.autoAssign` with that rule.
2. **Playwright:** open a specimen's aptitudes, choose a rule, see draft shares change, reload, see the
   saved allocation unchanged (C3). Choose `species-favour` on a real species and see it succeed (W3
   closed end to end).
3. **Refusal:** a forced refusal shows the reason and the `even` offer (C4).

## Boundaries

- **Always:** list rules from the server; draft only.
- **Ask first:** any auto-save; any new layer or route (GG-1: menus open over where the player is).
- **Never:** a hardcoded rule list; a control that hides the manual path.

## Success criteria

- [ ] The `/idea-ui` pass is recorded and names placement and label keys.
- [ ] `aptitude.autoAssign` has a producer.
- [ ] Playwright covers C2 to C4.

## Open questions

None for the owner. Placement belongs to the `/idea-ui` pass named as a dependency.

## Self-audit — the debate

- **"A contract-only spec is a spec that can't be built."** It can't be built *before* `/idea-ui`,
  which is the gate's rule, not this spec's gap. What it prevents is the `/idea-ui` pass re-deciding
  C1 to C6, each of which is already ruled.
