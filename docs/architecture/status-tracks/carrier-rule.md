# Carrier rule

**The deciding question, stated once.** *Does anything spend it?*

Apply it and the carrier is determined. There is no second question, and no need in
[need-inventory](need-inventory.md) needed a third.

## The test

Ask one thing: **will an action cost read and decrement this value?**

- **Yes** — something pays it to do something. It is a 0..max scalar with a spender, which is exactly
  what `ActorResourcePools` is (`gk-core/src/FusionRpg.Core/Actions/Cost/ActorResourcePools.cs`).
- **No** — nothing pays it; its only consequence is crossing a threshold. It is a ladder.

## The two outcomes

- **A spender exists → pool.** Legal only as a **seventh** `ResourceIds` entry, which is an ADR, not
  a content edit (`resource-hub-ssot.md:134`), and it inherits the six-coverage rule
  (`resource-hub-ssot.md:203-208`): every derived-stat family must then cover seven. Build cost is
  real but procedural — a catalog row, a seed roster row, aptitude edges, and four locked tests go red
  on purpose (ideal §3).
- **No spender → projection.** A ladder of staged status ids over a scalar in durable party state. No
  ADR, no locked count, no aptitude work (ideal §3). `nerve.*` and `wound.*` are both this shape.

The asymmetry is worth stating once: a projection is strictly more code for a *number* and strictly
cheaper for a *tier*.

## The escape hatch

If the answer is genuinely **both** — the need must render as a bar *and* be spendable — then it is a
pool, and a pool is the owner's ADR. Ask. Do not route around K1.1.

Two things that are **not** the test and do not open it:

- **Wanting a nicer HUD.** A projection is a token; only a pool publishes a ratio. Wanting a bar is a
  reason to *ask for a pool*, not a reason the need already is one.
- **Being two-sided, tick-based, or otherwise awkward.** Those are modelling problems for the ladder
  resolver (see temperature in [need-inventory](need-inventory.md)), not evidence that a pool exists.

Context: [ideal](../status-tracks-ideal.md) · [map](../status-tracks-map.md) ·
[packet](../../research/status-tracks/owner-decision-packet.md).