# Refined-grid N=256 findings

Date: 2026-09-06

The resource-approved N=256 condition used the amended uniform dense grid
sigma=0.80--2.50, 64 paired realizations per dense point, five anchors with 16
pairs each, and 500 breakpoint bootstrap replicates. All 1,232 planned pairs
completed.

The H0 breakpoint is sigma=1.10 with 95% bootstrap interval 0.90--1.20 and
d-prime at the breakpoint=8.0566. The interval width is 0.30 and it touches
neither candidate boundary 0.80 nor 2.50. The preregistered within-size
conditions therefore pass.

Measured resource use was 1,932.46 seconds (32.21 minutes) and peak RSS 0.0930
GiB. Wall time was 7.2% above the frozen-model prediction of 1,802.17 seconds
and remained far below the 12-hour gate. Peak RSS remained far below 16 GiB.

This document reports the within-size result only. Scaling-model selection and
outcome assignment are performed separately after this data commit is frozen.
