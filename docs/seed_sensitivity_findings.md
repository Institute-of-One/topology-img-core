# Phase 2 seed-sensitivity findings

## Why this experiment was inserted

The first two independent breakpoint runs gave 1.60 on the older coarse design and
1.30 on the refined design, with little interval overlap. Amendment v1.1 therefore
froze a five-run measurement at the fixed 128 by 128, lesion-width 5 px condition to
separate within-run bootstrap uncertainty from between-seed variability before any
N=192 or N=256 scaling data were generated.

## Primary five-run result

The five refined-grid root seeds produced breakpoint point estimates from 1.20 to
1.40 before the boundary extension. Their observed between-run standard deviation
was approximately 0.071 and the typical within-run bootstrap standard error was
approximately 0.080. The Q-test gave p=0.529 and the DerSimonian-Laird estimate was
tau=0. Under the v1.1 decision rule, within-run uncertainty was adequate.

However, two run-level intervals touched the preregistered lower knot boundary of
1.00. This triggered the v1.1 inconclusive condition. No seed was removed or
replaced. Amendment v1.2 was frozen before adding data and specified 64 new paired
realizations at sigma 0.80 and 0.90 for every registered seed.

## Boundary-extended result

After adding all 640 planned extension realizations, the five breakpoint estimates
were 1.30, 1.30, 1.40, 1.30, and 1.10. Their intervals no longer touched the new
lower boundary 0.80 and none exceeded width 0.40. The extended study is therefore
conclusive under amendment v1.2.

The frozen heterogeneity statistics were:

- Cochran Q=8.549 with 4 degrees of freedom;
- Q-test p=0.0734;
- I-squared=53.2%;
- tau=0.0885 in noise-sigma units;
- observed between-run SD=0.1095;
- typical within-run bootstrap SE=0.0853;
- between-run SD / typical within-run SE=1.284;
- random-effects pooled breakpoint=1.2745;
- primary random-effects 95% interval=1.1677 to 1.3814;
- run-level bootstrap sensitivity interval=1.16 to 1.36.

The preregistered adequacy rule passes because Q p is at least 0.05 and tau is no
greater than 0.10. Material heterogeneity is therefore not declared, and v1.0's
one-run-per-size scaling plan may proceed.

## Interpretation

The result does not support the initial suspicion that within-run bootstrap
intervals grossly omit a larger seed-variance component. The measured seed effect is
of similar magnitude to within-run uncertainty and is covered by the random-effects
interval.

The pass is nevertheless close to both thresholds: Q p=0.073 is near 0.05,
tau=0.0885 is near 0.10, and I-squared is moderate. It would be incorrect to summarize
this as "no seed dependence." The defensible statement is that seed-to-seed
variability was directly measured, was not significantly larger than within-run
uncertainty under the frozen rule, and yields a pooled crossover region around
sigma 1.17 to 1.38.

The historical coarse-grid estimate 1.60 is outside that pooled interval. It was not
part of the primary five-run variance calculation because its grid differed, as
specified before the new runs. It remains reported as evidence that analysis design
and ensemble realization can shift a single fitted knot. No value is selected or
discarded to improve agreement.

## Consequence for scaling

The N=192 resource measurement may proceed with the v1.0 interval definition. The
measured tau and random-effects interval must be carried as a seed-sensitivity
benchmark: an apparent matrix-size shift smaller than roughly 0.1 in sigma should not
be treated as compelling size dependence from a single run. The scaling report must
show both the preregistered within-size bootstrap result and sensitivity to this
measured noise floor.
