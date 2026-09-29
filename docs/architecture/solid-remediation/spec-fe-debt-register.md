# spec — `fe-debt-register`

**Module 5 of `solid-remediation`.** Register entry: **X4**. Depends on `green-baseline`.

## Objective

Create the FE debt file and the hand-off to the later FE program, and have every module append to it as
it runs.

Owner ruling 2026-09-16:

> *"Solve the BE first. When it solid, we will make new plan to solve FE — but I don't think we really
> need, because the FE is ugly, so I want to refactor it almost completely. So we don't really do it now,
> but track it."*

So `web/**` is **out of scope for remediation and in scope for tracking**. This module is the tracking.

## Why tracking rather than fixing

Fixing a formula inside a surface the owner intends to rebuild is effort spent twice. The register exists
so the rebuild starts from a measurement rather than a fresh audit.

## Starting content

| Row | What | Evidence |
|---|---|---|
| **X4** | The C# and TypeScript sigmoids disagree today | the two implementations; a shared shape with two owners |
| **G3 (FE half)** | `web/**` has **no verification boundary** at all | deferred by `verification-boundaries-extend` |
| **Measure caps** | The content measure lives in `layouts/Page.tsx` (`max-w-[1100px]`, 22 pages) but rail stages own theirs separately — `SanctumStage` had none and rendered 1780px wide until 2026-09-17 | measured live at 1922px |
| **god-TSX / page-CSS** | Owned by `gui-lego`; `/idea-ui` is its gate, not `/idea` | ideal doc |

Re-measure before writing. These are readings.

## What a row is

What the debt is, where it lives, what it blocks, and whether anything **back-end** depends on it. That
last column is the one that matters to this program: a row nothing back-end depends on is genuinely
deferrable, and a row something does depend on is a finding this program may have to act on after all.

## The append rule

Every module states which FE rows it added. A module that touches `web/**` at all says why, since the
default is that it does not.

## Boundaries

- **Always:** a row says what it blocks. "The FE is ugly" is not a row
- **Ask first:** any change under `web/**` beyond what `green-baseline` needed to make suites green
- **Never:** fix an FE defect here because it looks quick. That is the decision the owner already made

## Verification

- [ ] The file exists with its schema, the append rule, and the hand-off to the FE program
- [ ] X4 is recorded with both implementations cited
- [ ] `web/**`'s missing verification boundary is recorded, naming this program as where it was deferred

## Success criteria

The FE program starts from this file. Assert its **schema and closure**, never its row count.
