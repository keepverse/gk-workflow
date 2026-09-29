# EP4.12 - the species-build panel shows both payment options

**All acceptance points are green**, including the vitest the row asked for. Commit `@EP4.12` (partial) - session
`empire-progression-3` - branch `cmdc/ep-3` - spec `spec-respec-free-counter.md`

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| With `freeAvailable`, both options show and neither is chosen | `cd webusion-rpg-web; npm run build` | clean (`tsc --noEmit` plus vite, built in 11.97s) | `SpeciesBuildPanel.tsx` - a `payWith` state that starts UNDEFINED, and when the change is priced and a free respec is available it renders both "Spend a free respec (N left)" and "Pay X Soul" as radios with no checked default, plus the reason line naming both |
| Confirm cannot proceed on an unmade choice | same | `choiceRequired = !isFree && freeAvailable && payWith === undefined`, folded into `confirmEnabled` - so a priced change that COULD be paid either way stays unconfirmed until the player picks | same |
| The choice rides the wire only when it was chosen | same | `useSpeciesBuild.save(shares, payWith?)` spreads `payWith` into the body ONLY when defined, so a request with no choice is byte-identical to the pre-EP4.12 request - which the server reads as "no choice named" (a soul charge with no stock, a refusal with stock) | `useSpeciesBuild.ts`, `lib/bus/mutations.ts` |
| The wire types carry both new facts | same | `SpeciesRespecPrice` gains `freeRespecStock`/`freeAvailable`; `SpeciesRespecResult` gains `paidWith`/`freeRespecStock` - the fields EP4.10 added server-side | `lib/bus/types.ts` |
| The existing FE suite is unchanged and green | `cd webusion-rpg-web; npm test -- --run species-build` | `Test Files 1 passed (1)`, `Tests 14 passed (14)` - no existing case moved, because the new block renders only when the price fixture says `freeAvailable` | `SpeciesBuildPanel.test.tsx` (unedited) |
| Extraction stays clean | `cd webusion-rpg-web; npm run extract` | the catalogs report no new messages: the new copy is plain literals, matching the panel's existing strings, so nothing needs translating yet | - |

**One trap worth recording:** the first attempt put the new `useState` next to the derivation that feeds it (mid-component,
after an early return), and every one of the 12 mounted cases failed with `Rendered more hooks than during the previous
render`. The state now sits with the component's other hooks at the top, and the derived booleans stayed where they read
best. A React rule, not a typing one - `tsc` was happy with both.

**The vitest the row asked for, landed (two cases, 16/16):**
`EP4.12: a free respec offers BOTH payments with no default, and nothing is sent until the player picks` asserts both
radios render unchecked, Confirm is disabled, a click on it fires NO request at all - so no request can carry a `payWith`
the player did not choose - and choosing the free respec then sends exactly that spelling. And
`EP4.12: with no free respec available the request carries no payWith at all` asserts no chooser renders and the body has
no `payWith` property, which is the "never sends an unchosen choice" clause in its most direct form.
