# Coda: TOI-270 development replay and small adversarial checks

2026-10-08. Coda is collaborating with Andrei and Lilitari. This report addresses the delivered lossy 30-minute TESS development package only. It is neither a new-target survey nor a discovery or significance claim. The original package and earlier Kepler gates remain unchanged.

## Result

The six supplied implementation tests pass, and the three delivered periods and PDC/SAP depths reproduce exactly in the existing Windows CPython 3.13.15 / NumPy 2.3.5 environment. All 19 original manifest entries matched before and after execution. The supplied search source is unchanged at SHA-256 `48d62036f02e9ba8e26262f19d85df8850f9231274f43420ca4538cdc8056755`.

| Iteration | Period, days | PDC depth, ppm | SAP depth, ppm | Event sample counts |
|---|---:|---:|---:|---|
| 1 | 5.655459544383346 | 3366.713417725168 | 3166.5503603836514 | 3, 3, 3, 3 |
| 2 | 11.374012590234061 | 2704.2904994298196 | 2843.5131584376422 | 4, 4 |
| 3 | 10.757971447619484 | 776.7526209608176 | -272.59261788859226 | 5, 8, 8 |

Known c/d recovery, the miss of b in the three-peak budget, and the third peak's product disagreement remain the actual development outcome. No retuning was used for this replay.

## Two demonstrated implementation defects

**Eligibility is applied after a single phase-box argmax.** At `package_copy/search.py:64`, the code chooses only the strongest phase start for each period and width. If that box fails the two-event condition at lines 69-72, it never considers another eligible phase start at that same period/width. The periodogram also retains the unrestricted score at line 77, so it is not an eligibility-filtered periodogram.

`counterexamples.py` contains a deterministic, exhaustive small-grid oracle (one 4-day period, 16 phase bins, one 6-hour duration). One deep single event wins the unrestricted score, 0.0007334537634408602. A shallower repeated dip is eligible, with two groups of eight samples and score 0.00019997330367074528. The unchanged prototype raises `No trial has positive depth and two populated events`. It therefore does not always maximize its stated objective over eligible boxes. This small counterexample proves the implementation defect; its effect on the three real-development peak choices has not been measured. A new production search should apply eligibility to candidate boxes before choosing the winner, including fallback when the highest-score box is ineligible.

**Scored bins and reported event/diagnostic membership use different endpoints.** Counts and sums score half-open phase bins. Lines 69 and 92 instead use a closed geometric interval. In a dyadic-grid example, the selected box scores 16 points while its event counts total 18; points exactly at the right boundary enter only the geometric interval. With the exact same input flux, its scored depth is +3497.9253112033193 ppm while the geometric diagnostic is -4000 ppm. This is a numerical membership inconsistency, separate from astrophysical product differences. A production implementation needs one documented membership convention used consistently for score, event counts and same-box comparisons, with explicit boundary regressions.

**The actual delivered peaks have zero such membership disagreements.** Direct inspection finds 12/12, 8/8 and 21/21 binned/geometric samples respectively. The boundary counterexample therefore does not explain the observed third-peak SAP/PDC sign difference. The distinction between a general defect and its measured effect matters here.

## Demonstrated method limits, not undisclosed discoveries

- Two populated events can mean sample counts **3 and 1**. The prototype accepts this synthetic result; it has no per-event minimum, in-event coverage fraction, or neighboring-baseline requirement. This is correctly described as a permissive eligibility check, not validated repetition.
- The declared gap-aware median correctly removes a factor-of-two step across a long gap without cross-gap leakage. An isolated five-sample dim segment also normalizes to zero. The latter demonstrates loss of information when each short segment supplies its own baseline; it is not an implementation failure of the stated median rule.
- With a true 0.5-day box and an underestimated fitted width of 0.25 days, the development mask removes only out to 0.1875 days from each center. **56 of 252 injected dip samples remain**. This is a direct masking sensitivity, not evidence that masking caused the real third peak. Multi-signal removal and detrending need sensitivity checks before interpreting residual peaks.

These checks do not calibrate a false-alarm probability, quantify completeness, establish astrophysical planet validation, or replace the separate standard Astropy/original-FITS comparison. I recommend preserving the custom prototype as a development artifact and carrying these counterexamples into the standard implementation's validation, rather than extending this prototype into the discovery pipeline.

## Executed evidence and resource scope

- `manifest_verification.log`: initial copy verification and byte-identical gzip decompression.
- `six_tests.log`: six original tests; zero failures, errors or skips.
- `three_peaks.log` and `replay_receipt.json`: serial replay and exact numeric comparison, 12.97 seconds elapsed.
- `counterexamples.py` and `counterexamples_receipt.json`: executable synthetic cases and real-development membership inspection; final run 0.031 seconds, 36,786,176-byte peak working set (approximately 35.1 MiB).
- `package_copy/`: working copy with original source retained and replay outputs written locally. Its delivered manifest records the original delivery; generated result files may be rewritten by replay. The immutable source directory is `../source/planet_hunt_tess_development_2026-10-08/`.

All execution used one numerical thread (OMP, OpenBLAS, MKL, NumExpr, vecLib and BLIS limits) and socket/DNS blocking. The original Windows priority request used an untyped pseudo-handle and did not establish below-normal priority; a later direct probe confirmed that failure. The helper is corrected for future runs and now checks the result. The original replay's Windows peak-memory query was invalid and returned zero; the receipt explicitly records that value as unavailable, and the helper was corrected before the measured synthetic run. No zero-memory or unmeasured peak-memory claim is made. No broad download, foreground UI, GPU task, external contact, target query, or gate mutation occurred.

To rerun only the tiny counterexamples, invoke the existing interpreter on `counterexamples.py`; it restores its in-memory configuration and verifies the original manifest afterward. `replay.py` intentionally refuses to overwrite an existing `package_copy`; a new complete replay should use a new owned output directory and preserve this run.
