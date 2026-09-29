# Brief template — copy, fill in, spawn. The lane sees ONLY this (+ context).

## Goal

<one sentence: what done looks like>

## Allowed paths

<glob list, e.g. gk-core/src/FusionRpg.Core/Items/** — the scope fence. The runner
fails verification on anything outside it, so list everything the task needs>

## Off limits

<pipeline files, other lanes' paths, generated data — anything that looks
tempting but is not this task>

## Definition of done

<acceptance lines, each independently checkable>

## Verification

<exact backticked commands the lane must run, e.g. `dotnet test
gk-core/tests/FusionRpg.Core.Items.Tests`. These default the runner's verify step>
