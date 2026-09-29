# BCU5.3-5.6 — world-remainders (routing batch)

BCU5.3: already done by combat-ai's own plan (BCU2.9a, this session). combat-ai-map.md module 13
(delve-automated-wiring) covers RpgHub.Resume's auto-policy exactly; combat-ai-todo.md's own
cross-program-edges section already says "Also tracked as BCU5.3". CAI3.4/CAI3.5 are the real build
tasks. No new spec note needed.

BCU5.4: F8 (world-generator entrance placement) and F10 (ContractPolicy.BaseUpkeepPerDay not
Θ-scaled) both re-confirmed live, still genuinely open, correctly routed (not this task's job to
fix). notification-ssot's map already closes the empire-development notify-sources cross-link in
both directions (verified both files carry matching cross-references).

BCU5.5: premise (a Core<->Server EquippedActionIds bridge) is stale — DistrictAssaultResolver
already wires AdditionalHeldActions, a purely additive sibling field that deliberately avoids
touching EquippedActionIds at all. What remains (a real content item, a cell-choosing intent
policy) is out of scope, correctly named.

BCU5.6: ActionStockCommit.TryCommit re-confirmed live to now have 3 real production callers
(BasicAttack.cs:129, ConstructionActions.cs:269, TimelineDispatch.cs:169) — the earlier "zero
callers" finding is fixed, matching base-defense-todo.md's own later-session correction.

```
$ python scripts/audit-doc-citations.py --scope tasks/backlog-clean-up-todo.md --strict
0 HIGH (53 citations)
```
