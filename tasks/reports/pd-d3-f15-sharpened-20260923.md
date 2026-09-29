# Evidence — F15 sharpened and one of my own claims corrected (lane `pd-d3`, 2026-09-23)

No code. One measurement pass over the species corpus; F15 keeps its open state and its two failing
tuples are now distinguished by rung, with a correction to my own earlier census claim.

| Reading | Printed value |
|---|---|
| Bastion+melee by `targetPreference`, ALL rungs | `backline 33, frontline 7, structure 1` — **swarm 0** |
| Bastion+melee by `targetPreference`, rungs 9-10 | `backline 6, frontline 1` — **swarm 0** |
| do the 41 Bastion+melee anchors survive the expander? | `ClassifiedCorpus()` holds 904; Bastion+melee = 41, by rung `1=6 2=1 4=5 5=4 6=1 7=4 8=13 9=2 10=5` — **all 41 survive**, so `SpeciesExpander.UnresolvedFields` drops none |
| which tuple does each refusal demand? | boss `encounter.boss-mono-001` → `[Bastion, Melee, Swarm]`; pack `encounter.pack-mono-001` → `[Bastion, Melee, Frontline]` (read from `Encounter.Build`'s own refusal, because the preflight's printed slot text omits `targetPreference`) |

**The two failures, now distinct**

- **Boss slot** `[Bastion, Melee, Swarm]`: **zero** such anchors at any rung → `domain.fire-001`'s
  `0 candidate(s) ignoring element`.
- **Pack slot** `[Bastion, Melee, Frontline]`: exactly **one** such anchor in rungs 9-10, matching none of
  the six climates → the other five domains' `1 candidate(s) ignoring element, 0 under climate <X>`.

**Correction to my own earlier claim**

My first F15 note said "`Bastion/Melee/Swarm` and `Bastion/Melee/Frontline` do not appear at all". The
`Frontline` half was wrong — it appears 7 times across all rungs and once in rungs 9-10. Corrected in the
row, with the reading that produced it.

**NOT proved**

- F15 is not fixed and nothing was attempted: both tuples are content-distribution questions whose two
  possible fixes (`gk-forge/tools/seedsmith`'s encounter anchors, `gk-data/packs/fusion/data/seed/creatures`' species tuples) are outside
  this lane's fence.
- The expander exclusion is proved only for the 41 Bastion+melee anchors (they all survive). I did not
  measure which anchors `SpeciesExpander.UnresolvedFields` does drop, or how many.
- No probe was committed: the throwaway test was removed before this commit and `git diff` is empty.
