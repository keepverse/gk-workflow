# spec — `stub-register`

**Module 4 of `solid-remediation`.** Register entry: **G1**. Depends on `green-baseline`.

## Objective

Create the file the owner asked for — *"stub feature this need to find it own plan to update (not
complete), a own file to track debt and remove stub"* — and the rule that every later module appends to
it as it runs.

**Created early, not at the end.** The ideal doc says a register is *"only useful if written as the work
happens, not reconstructed at the end"*. A register written last is an audit; a register written as the
work happens is a measurement. The first draft of the map sequenced this module last, which contradicted
that directly.

## The defect (G1)

No stub register exists. The closest things are per-program todo entries and inline refusal messages —
both invisible to anyone not already reading that file.

## What belongs in it

A **stub** refuses by design and waits on a named external finding. That is a different thing from a
wiring gap, and the distinction is the whole value of the file:

| | Definition | In this program? |
|---|---|---|
| Shipped | reachable by a player today | fixed here |
| Half-built | built and reachable but incomplete, **or built and dark** | fixed here |
| **Stub** | refuses by design, waiting on a named finding | **registered here, planned separately** |

"Built and dark" is the category that gets misfiled as a stub. Fusion picks are built, validated, carry
nine refusal codes, are reachable from the FE — and render nothing, because one upstream writer has no
caller. That is a wiring defect (S5), not a stub.

## Measured starting content

`NotImplementedException` appears **14 times** in `src` and the web app. **Ten are in one file**,
`gk-core/src/FusionRpg.Server/DelveEndpoints.cs`, and every one names why it refuses and which finding owns it.
Re-measure before writing — this is a reading.

Each row records: what refuses, where (`file:line`), what it waits on, who owns that, and whether anything
ships today that depends on it.

## The append rule

Every module in this program states, in its own spec and its own commit, which register rows it added.
A module that finds a stub and does not register it has left the next program an audit to redo.

## Boundaries

- **Always:** a row names the finding it waits on and an owner. A row with neither is a to-do, not debt
- **Ask first:** completing a stub. That is its own program by definition — this file exists so that
  program can start from a measurement
- **Never:** record a **wiring gap** as a stub. An inert path with working machinery behind it is in
  scope for this program and must be fixed, not filed

## Verification

- [ ] The file exists with its schema and the append rule stated
- [ ] The 14 measured `NotImplementedException` sites are triaged into stub / wiring gap / neither
- [ ] Any responsibility with **no** implementation found by `battle-responsibility-guard` is a row here

## Success criteria

The next program inherits a measurement instead of an audit. Assert the file's **schema and closure** —
every row has a finding and an owner — never the row count, which is a population that grows as the work
proceeds.
