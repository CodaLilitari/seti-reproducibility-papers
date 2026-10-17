# Coordinate supplement: numerical replay status

**Status as of 15 October 2026: bounded numerical replay completed with one qualified reference discrepancy. Public release and licensing remain pending.** Eight scientific commands were executed once each in an isolated working copy. All eight exited successfully and passed their internal assertions. Twenty of twenty-two reference-comparison records passed; two records report the same candidate-I fitted-epoch discrepancy in different output formats. A separate ninth command reproduced the historical 72-case Astropy cross-check exactly at the CSV level. No scientific source was changed, no numerical command was repeated, and no tolerance was relaxed.

## Calculation coverage

| Calculation | Result and limits |
|---|---|
| Independent core calculation (D1) | All 43 central-offset rows, seven coordinate inversions and five focal conditional-probability rows reproduced within declared tolerances. One of eleven fitted epoch shifts failed the predeclared reference tolerance, as detailed below. |
| Independent 36-row coordinate audit | Candidate-radius, fitted-epoch and probability/rounding tables reproduced byte-for-byte. |
| Candidate-A control estimator | All four numerical band-result records matched exactly, including fixed- and free-location comparisons. Execution metadata was treated separately. |
| Rational rounding exclusion | Full proof output reproduced byte-for-byte. All four bands explicitly satisfied the negative score upper-bound condition across 100 subintervals each. |
| Conditional control bounds | All 30 per-source rows reproduced byte-for-byte; uniform and binary band-result fields matched exactly. |
| Ren 2024 seven-row audit | All 174 checks passed. The seven compared reference artifacts reproduced byte-for-byte, including covariance sensitivity and epoch scenarios. |
| TGSS diagnostic | All 17 checks passed and the diagnostic output reproduced byte-for-byte. This is a scoped astrometric diagnostic, not physical source validation. |
| Public finite-correlation follow-up | All 122 checks passed. The numerical CSV reproduced byte-for-byte and selected scientific result fields matched the original implementation. Three provenance-only assertions were removed from the public derivative; scientific assertions were retained. This is not labeled a new execution of the original 125-check version. |
| Historical 72-case Astropy comparison, replayed separately | All 72 rows and 36 candidate/band pairs reproduced byte-for-byte. The maximum Astropy-versus-stdlib difference remained 8.49259882240716 microarcseconds, rounding to 8.493. This command is not yet included in the frozen staged supplement. |

The eight-command calculations are same-code replays of frozen inputs. The separate Astropy command compares a different propagation/separation implementation against retained stdlib outputs, using the same underlying frozen data. Neither form of replay establishes fresh observational validation, recovery of the historical authors' workflow or a physical source classification.

## Candidate-I fitted-epoch qualification

| Quantity | Retained D1 reference | Replay |
|---|---:|---:|
| Best fitted shift, years | -0.34480909997444087 | -0.34485702729682544 |
| RMS residual, arcsec | 0.00793847850405235 | 0.007938478486915687 |

The fitted-shift difference is **4.792732238456665e-5 years**, exceeding the predeclared absolute tolerance of **1e-5 years**. The RMS values differ by approximately **1.7136663e-11 arcsec**. The cause of this optimizer-position discrepancy has not been established. Near equality of the objective is evidence about its scale, not grounds for converting the failed comparison to a pass. The calculation was not rerun or tuned.

All 43 central-offset rows passed their separate reference comparison; their largest numeric-cell difference was `2.7588709095027752e-11`. The v0.4 manuscript's four candidate-I central-radius pairs retain the same displayed six decimal places. It does not print I's individual optimum numerically. The figure was inspected but not regenerated, so pixel identity of a newly generated figure is not claimed. A future four-decimal printed fit would differ (`-0.3448` versus `-0.3449`); this qualification must therefore remain available to downstream readers.

## Historical Astropy cross-check

The separate command used Astropy 8.0.1 and NumPy 2.5.3 with distance inferred from parallax, zero radial velocity, Gaia reference epochs, spherical space motion and spherical separation. It parsed the retained sexagesimal table coordinates without importing the stdlib audit functions. The comparison covers two epoch models for each of 36 candidate/band pairs.

| Quantity | Result |
|---|---:|
| Maximum discrepancy at stated epoch | 5.592861009873218e-7 arcsec |
| Maximum discrepancy for epoch offset minus 16 years | 8.49259882240716e-6 arcsec |
| Unchanged internal threshold | Less than 1e-4 arcsec |
| Replay versus historical CSV | Byte-identical, all 72 rows |

The maximum occurs for candidate C, W4, in the minus-16-year model: Astropy `4.980143719897028` arcsec versus stdlib `4.980152212495851` arcsec. The scientific summary matches exactly; only operating-system build metadata differs in the raw summary.

The exact historical script additionally requires a full article HTML file only to assert its hash. That input was retained privately for QA and has not been added to the staged supplement. Its redistribution decision remains unresolved. The numerical inputs are already staged, but the extra script and its output are not. Successful private replay therefore does not yet mean the public package can execute this command without further curation.

## Environment and comparison method

The existing environment provided Python 3.13.15, NumPy 2.5.3, SciPy 1.18.1 and Astropy 8.0.1. Commands ran serially with the OMP, OpenBLAS, MKL, NumExpr and VecLib thread environment settings set to one. These settings constrain library threading rather than imposing a kernel CPU quota. Caches and temporary files were isolated; IERS automatic downloads were disabled. No packages were installed and no acquisition or GPU work occurred.

An inspected wrapper denied Python network socket operations, subprocess creation and writes outside the disposable replay directory. It allowed the local host-name lookup needed by library imports. The initial eight-command dependency preflight stopped on that local lookup; the wrapper was corrected before scientific execution, with the failed preflight retained. No science ran during that failed preflight. All subsequent preflights and scientific commands recorded no blocked events. This is an application-level audit guard, not an OS firewall or packet capture.

Reference criteria were saved before execution: exact schemas, row order, identifiers, counts, booleans and strings; ordinary numeric values at relative tolerance `1e-9` and absolute tolerance `1e-10`; tiny nonzero values at relative tolerance only; fitted shifts at absolute tolerance `1e-5` years. An additional read-only comparison explicitly checked fit RMS values with the stricter ordinary numeric criterion; all passed. The candidate-I fitted-shift criterion and failure were unchanged. The separate Astropy CSV reproduced exactly, so its pass did not depend on a tolerance boundary.

Before/after file identities confirm the staged supplement and checked canonical sources were preserved. Raw runtime records remain separate from this public-safe status document.

## Reproducibility boundaries and file identities

This coverage does not include the omitted D1 HTML/pandas extraction, fresh acquisition, source-image inspection, figure regeneration, full observational processing, physical association or infrared contamination measurement. A golden-section fitted-epoch replay is not certification of a global optimum. Unrelated TESS calculations were outside this replay. A complete end-to-end reproducibility claim would therefore be too strong.

| Artifact | SHA-256 |
|---|---|
| Frozen staged-supplement manifest | `af2aa31f22ed3598e44372e915bd2a1c4d9627fe9f8f9b8c39f8bee3d7371d79` |
| Historical Astropy cross-check source | `b28b5324ff2c6c567ca12031bef5221aba1c7c4b245e6a39d4187706c94c0188` |
| Historical and replayed 72-row Astropy CSV | `25b8600736c555a38a6101ff6a422bd516341a42ba48beb61cd4d03684dcdd89` |

These hashes identify the reviewed state; they do not supply missing files or grant redistribution rights. This status document records numerical coverage and qualifications only. It does not authorize publication, assign licenses or alter the frozen supplement.
