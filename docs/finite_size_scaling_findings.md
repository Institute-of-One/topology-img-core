# Phase 2 finite-size scaling findings

Date: 2026-09-06

The primary analysis used the five registered matrix sizes N=64, 96, 128, 192,
and 256 after all within-size continuation criteria passed. Authoritative H0
breakpoints were 1.60, 1.20, 1.30, 1.20, and 1.10, respectively. The corresponding
d-prime values were 5.5389, 7.3852, 6.8171, 7.3852, and 8.0566.

Each size contributed its 500 within-size breakpoint bootstrap draws. Fits used
inverse-bootstrap-variance weighted least squares and the registered AICc formula.
Two thousand scaling bootstrap replicates independently sampled one draw per size.
The convergent model was fit by profiling omega over the registered positive
domain and solving y-infinity and amplitude by weighted linear least squares at
each omega. No bootstrap optimization failed.

## Breakpoint sigma

- Constant model: AICc=9.612, c=1.2704.
- Log-drift model: AICc=8.728, b1=-0.3029.
- Convergent model: AICc=26.546, omega=1.9749.

The constant model is within 2 AICc units of the best model, but the observed
N=128--256 range is 0.20, or 15.7% of the constant estimate, and exceeds Rule A's
10% threshold. Rule A therefore fails. The convergent model is 17.82 AICc units
worse than log drift, and the bootstrap omega interval is approximately
0.000001--8.043. Rule B also fails. The extremely wide y-infinity interval reflects
the expected nonidentifiability as omega approaches zero; it is evidence against
claiming an estimated finite-size limit, not a physically meaningful negative
asymptote.

## d-prime at the breakpoint

- Constant model: AICc=10.294, c=6.6090.
- Log-drift model: AICc=6.622, b1=1.7151.
- Convergent model: AICc=25.732, omega=1.0045.

The constant model is more than 2 AICc units above the best model, and the observed
N=128--256 range is 1.2395, or 18.8% of the constant estimate. Rule A fails. The
convergent model is 19.11 AICc units worse than log drift and its omega interval
again extends effectively to zero (approximately 0.000001--8.105). Rule B fails.

## Seed-noise-floor sensitivity

The measured between-run noise floor tau=0.0885 in breakpoint sigma was added
independently at each size in a labelled secondary bootstrap sensitivity analysis.
It did not change either convergence decision. The point-to-point 0.10 changes
between larger sizes are only about 1.13 tau, and the full N=128--256 change of
0.20 is about 2.26 tau. The apparent downward drift in sigma and upward drift in
d-prime must therefore be described as compatible with nonconvergence over the
tested range, not as a precisely resolved scaling law.

## Preregistered outcome and interpretation

Neither breakpoint sigma nor q satisfies Rule A or Rule B, and no registered
inconclusive condition fires. The preregistered classification is Outcome 3:
nonconvergence over the reachable N range.

This does not prove that no asymptotic limit exists. It shows that the observed
nonlinear topological crossover is reproducible but its location is not universal
over N=64--256 under the registered criteria. There is no credible evidence here
for a critical phase transition or a universal detectability threshold. The
result supports the more limited interpretation already used by the repository:
a nonlinear topological crossover accompanying detectability loss, with position
dependent on finite image support and ensemble realization.
