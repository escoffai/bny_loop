---
name: validate-fba-output
description: |
  Run after any FBA solve. Checks that biomass flux > 0, exchange fluxes are
  within their declared bounds, and the solution is unique within tolerance.
---

# validate-fba-output

When a new FBA result is produced, run the following deterministic checks
before treating the output as valid:

1. `growth_rate_per_h` is greater than 0 (or the result is explicitly marked
   as a no-growth case).
2. Every exchange flux falls within the bounds declared on its reaction.
3. The optimum is unique to within `1e-6` (run `cobra.flux_analysis.flux_variability_analysis`
   on the objective reaction; the difference between min and max must be
   below tolerance).
4. `solver_status` is `optimal`. Anything else fails the skill.
5. For Phase 0, the only acceptable non-`optimal` status is the documented
   stub value `placeholder-ok`, and this skill must mark such results as
   "stub — not validated".

Emit a structured report with pass/fail per check and the offending values.
