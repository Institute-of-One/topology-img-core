# Phase 2 resource measurement method

This operational method is recorded before the first N=64, N=96, or N=192
refined-grid calibration run.

- Each matrix-size condition runs in a fresh Python process.
- Wall time starts immediately before the first sigma-level computation and ends
  immediately after the registered 500-replicate breakpoint bootstrap.
- CSV, JSON, and figure serialization occur after the wall-time boundary.
- Peak resident memory is the fresh process's native lifetime peak: Windows Peak
  Working Set on the registered workstation, `ru_maxrss` on POSIX systems.
- The command, Python version, platform, configuration hash, code commit, and
  native resource-counter name are retained with the output metadata.
- The N=128 scientific estimate remains the already registered refined-grid
  result. A clean N=128 resource-only replay is permitted solely to obtain its
  missing peak-memory calibration with the same instrumentation; it cannot
  replace or modify the registered N=128 topology result.
