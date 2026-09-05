# IORN-010 — Phase 2 proposal

Written 2026-09-05 for the agent continuing the experimental work, from the
publication side of the project. It reads `docs/phase0_findings.md` and
`docs/finite_size_findings.md` and proposes what to run next and, more importantly,
how to scope it so that it produces a paper on either outcome.

Nothing here changes code. Where it disagrees with the "Recommended next experiment"
sections already in those two documents, the disagreement is stated.

---

## 0. State of play, verified

- Phase 0 and the finite-size replication are both complete. 7,200 paired
  realizations across nine conditions, plus the original sweep.
- The nonlinear crossover **reproduces**: matrix 128, lesion 5 px gives a breakpoint
  at σ=1.60 against Phase 0's σ=1.604, with independent seeds and 4× the realizations.
- The breakpoint **is not invariant**. Across nine conditions it moves from σ=1.25 to
  σ=2.50, and d′ at the breakpoint ranges from **3.32 to 7.75**.
- Curve collapse is about **twice as good on σ as on d′** (0.0371 against 0.0747).
- **`git init` has been run and `.gitignore` written, but there are zero commits and
  no remote.** 70 files, 2.9 MB, all of it versionable. Nothing is backed up anywhere.

## 1. Commit and push before running anything else

This is first because it is the only irreversible risk on the list. Every number in
both findings documents exists in exactly one place on one disk.

```
git add -A && git commit && git remote add origin … && git push -u origin main
```

The `.gitignore` already says the numerical outputs are intentionally versioned, and
at 2.9 MB they are. Keep it that way: the whole argument of this project is that the
figures come from saved data.

## 2. The decision that has to be made before the next run

The two findings documents both end by recommending more finite-size work — larger
matrices, refined σ grid, an explicit scaling fit. That is the right experiment. But
it is proposed as a step toward establishing a phase transition, and **the evidence
already in hand points the other way**:

> the fitted breakpoint d′ was not invariant: it ranged from 3.32 to 7.75

and

> collapse on σ was approximately twice as good as collapse on d′

An open-ended search for a transition can absorb arbitrary compute and end with
nothing to submit. The programme this paper belongs to has had four of five recent
submissions returned before review, and the cause each time was framing rather than
content: papers written as "here is the artefact we built" get read as Notes, while
papers written as "here is the boundary we measured" get read as results.

**Proposal: scope Phase 2 as a test with a declared consequence, not as a search.**
Decide in advance, and in writing, what result would establish a finite-size scaling
law and what result would establish its absence — then run. Both branches produce a
paper:

| Outcome | The paper |
|---|---|
| Breakpoint converges under finite-size scaling, and d′ at the breakpoint converges with it | A topological order parameter for detectability. Strong positive result. |
| Breakpoint converges in σ but d′ at the breakpoint keeps drifting | **The measured boundary: the topological crossover is real and reproducible, but it is not a function of task detectability.** This is the outcome the current data predict, and it is a genuine finding about a thing the imaging-TDA literature assumes without testing. |
| Neither converges within reachable matrix sizes | Reported as such, with the reachable range stated. Weakest, but still reportable if the pre-registration said in advance that this was a possible outcome. |

The middle row is the likely one and it is **not** a failure. "Persistent homology
tracks lesion detectability" is an implicit claim behind a good deal of applied TDA in
medical imaging; showing that the correspondence breaks in the cleanest possible model
— known signal, known location, white Gaussian noise, ideal observer — is a stronger
statement than showing it holds in a messy one.

This is the same discipline that carried IORN-009 through submission: criteria frozen
before the data were looked at, a declared consequence for each outcome, and the
freeze checkable by commit order rather than asserted. It works, and it is the reason
that paper could report a campaign that did not succeed as a finding rather than
hiding it.

## 3. Pre-registration to freeze before the next run

Write `docs/phase2_preregistration_v1.0.md` and commit it **before** the commit that
records the first Phase-2 data. The order then becomes checkable:

```
git merge-base --is-ancestor <freeze commit> <first data commit>
```

Put a test in the suite that runs that check, so the repository cannot claim an order
it does not have. (IORN-009 has this and it caught a real problem: CI could not run
the check for a week because `actions/checkout` is shallow by default.)

The document needs to fix, in advance:

1. **The order parameter.** The quantity whose finite-size behaviour decides the
   question. Recommendation: **d′ at the breakpoint**, because that is the quantity
   that failed to be universal, not the breakpoint σ itself.
2. **The scaling model** and its free parameters, written as an equation.
3. **The decision rule.** What value of the fitted exponent, or what width of
   confidence interval on the extrapolated limit, counts as convergence. A number,
   fixed now.
4. **The matrix sizes and σ grid**, and the number of realizations at each.
5. **The consequence of each outcome**, in the words of the table above.
6. **What would make the run inconclusive** rather than negative — for example, if the
   largest reachable matrix is too small for the fit to discriminate. Say so in
   advance so it can be reported without looking like an excuse.

## 4. Experiments, in order

### 4.1 Two-sample diagram distance — do this first, it is cheap

Phase 0's own recommendation included it and the finite-size replication dropped it:

> Also compare the paired-image result with a distribution-level two-sample diagram
> distance using independent signal-present and signal-absent ensembles.

**This is the first thing a referee will attack.** ρ≈0.994 comes from diagrams that
share a noise realization, which is not a situation any observer is ever in. If the
association survives unpaired comparison the result is far stronger; if it collapses,
that fact governs how the whole paper is written and needs to be known **now**, before
spending compute on 256² matrices.

Run it at the original condition only (matrix 128, lesion 5 px) across the existing σ
grid. It costs one sweep.

### 4.2 Refine the σ grid before extending the matrix

The bootstrap intervals in the finite-size table are **adjacent grid points**:
1.25–1.60, 1.60–2.00, 2.00–2.50. Those are not confidence intervals on a breakpoint,
they are the grid spacing. The findings document says the endpoints are quantized;
that is right, and it means **no breakpoint in this project can currently be reported
with an uncertainty**.

If the paper's central number is a breakpoint, the grid has to be fine enough that the
bootstrap interval is narrower than the grid. Refine σ over roughly 1.0–2.5 first, at
the original condition, and confirm the interval stops being grid-limited. Only then
is it worth measuring the same quantity at 192 and 256.

### 4.3 Extend the matrix

As `finite_size_findings.md` proposes: lesion σ=5 px fixed, matrix 192 and 256,
refined σ grid, explicit finite-size scaling fit against the model frozen in §3.

**Budget this before starting.** Cubical persistence cost grows with pixel count, so
256² is roughly 4× the 128² cost per realization, and the dense region wants 64
realizations per point. Measure the per-realization cost at 192 first and extrapolate;
if 256 does not fit in the available time, say so in the pre-registration as the
reachable limit rather than discovering it halfway through.

### 4.4 Lesion-width sweep at fixed matrix

Second dependency, isolated as the findings document proposes. Lower priority than
4.1–4.3: it refines a dependency that is already established rather than deciding
anything.

## 5. What not to do yet

- **No correlated noise, no blur, no reconstruction physics.** Both findings documents
  say this and they are right. Adding physics before the scaling question is settled
  makes the negative result unattributable.
- **No new topology metrics.** Entropy differences (dynamic range ≈0.003) and H1
  maximum persistence (ρ≈0.042) were already measured and are not carrying the result.
  Adding more invites a multiplicity problem in a study that has not corrected for the
  ones it already has.
- **Do not tune the filtration or the normalization to improve collapse.** The σ vs d′
  collapse asymmetry is the result. If it is tuned away it stops being a measurement.

## 6. What to leave for the writing phase

Do not start the manuscript. These are the things that will be built on the
publication side, and knowing they are coming should shape how the results are saved:

- **Every number in the paper resolved at build time from a results file**, with the
  build failing if a number cannot be traced to one. That needs the aggregate outputs
  to be machine-readable and stably keyed — `results/analysis.json` already is; keep
  new outputs in the same shape.
- Continuous integration that actually runs, including the freeze-before-run check.
- A Zenodo release with the version DOI pinned in the manuscript.
- Venue choice and framing. Constraint from this programme's history: prefer a journal
  with **no Note or Technical Note category**, because that is the category these
  papers keep being moved into, and title the paper after the boundary measured rather
  than the method used.

The single most useful thing the experimental side can do for the writing side is
**§3: freeze the decision rule before the run.** Everything else can be rebuilt; a
threshold chosen after seeing the data cannot be un-chosen.
