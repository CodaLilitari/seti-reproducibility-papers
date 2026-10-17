# Coda: bounded post-hoc TOI-270 diagnostics

2026-10-08. Coda, collaborating with Andrei and Lilitari. This explicitly exploratory follow-up explains the known development miss and checks provenance warnings. It does not replace the original three-peak result, select a new host, or establish false-alarm probabilities. All original source and `standard-bls` files remained byte-identical.

## The b signal was present but outranked

Extending the original full-resolution, formal-error-weighted Sector 4 Astropy run from three to five peaks produces periods **5.6597003, 11.3911784, 10.7121666, 3.3596407 and 4.5045193 days**. The fourth is near known b, with 816 ppm box depth and five populated events (42, 40, 45, 45, 45 cadences). This is a post-hoc budget extension, not a retroactive successful original three-peak recovery. The fifth peak has no candidate status.

After the original c/d masks, holding those masks fixed, b's best nearby frequency-grid point has power 38.88 versus the nuisance maximum's 50.40. It ranks 20th among the 12,000 correlated grid points. At the exact known catalog period 3.35992 days, optimizing phase/duration post hoc gives power 37.71 and depth 793 ppm. These ranks are not independent-peak counts or p-values. The library's formal depth-SNR is not a false-alarm probability and is not empirically calibrated for correlated noise or the search.

| One-factor median-window change | Residual maximum period | Best b-region power | b-region grid rank |
|---|---:|---:|---:|
| 0.5 day | 3.3626343 d | 37.13 | 1 |
| 1 day, original | 10.7121666 d | 38.88 | 20 |
| 2 days | 10.7121666 d | 38.80 | 134 |

The b power remains similar while competing residual structure changes substantially. This supports sensitivity of the ordering to detrending and the three-peak budget. It does not identify a unique physical or pipeline cause. Changing only the c/d mask half-width multiplier from the original 0.75 to 0.5, 1.0 or 1.5 retains the nuisance maximum and b-region ranks of 20, 20 and 19. Those tested mask widths do not resolve the ordering.

A separate diagnostic fixed the coarse S5-recovered b ephemeris and back-projected it into S4 without refitting. It yields mixed per-event support and a reduced 454 ppm aggregate detrended PDC depth. That exercise is not a predeclared holdout pass. The coarse S5 period differs from the catalog by about 0.0027 day, which accumulates to roughly 31 minutes over eight cycles; timing-grid error is material for a 90-minute box. No uncertainty calibration is inferred.

## The third peak's product disagreement persists before local detrending

Both products use identical timestamps, quality support, c/d masks, and in/out membership. At the standard full-resolution third-peak ephemeris, the global unweighted box depths are SAP/PDC **-208/+847 ppm after** the one-day median and **-2387/+342 ppm before** it (raw products only median-normalized). Raw global depth is strongly affected by long-term trends; the local event comparison is more diagnostic.

| Event center BTJD | In samples | Local outside left/right | Raw SAP/PDC local depth, ppm | Detrended SAP/PDC local depth, ppm |
|---|---:|---|---|---|
| 1410.9710 | 74 | 3 / 130 | -901 / +1517 | -863 / +1478 |
| 1421.6832 | 90 | 134 / 135 | -282 / +674 | -259 / +650 |
| 1432.3953 | 90 | 135 / 135 | +229 / +424 | +245 / +396 |

The first event has severely asymmetric local baseline coverage near the sector edge and dominates the recovered PDC response. The sign disagreement in the first two events already exists in the delivered SAP/PDC products before this local median detrending; it cannot be attributed solely to that median operation. This does not prove that a particular PDC correction caused the structure. The third event has positive local depth in both products. The original legacy ephemeris produces the same qualitative pattern, including zero left-side outside samples for its first event. No planet promotion is justified.

## FITS checksum warnings resolved at the byte level

All six HDUs across the two local original FITS files have a raw big-endian 32-bit one's-complement sum of **`ffffffff`**, as expected when the header CHECKSUM covers the whole HDU. Recomputing each stored CHECKSUM with its actual data sum also matches exactly. Neither file was rewritten.

The inspected Astropy 8.0.1 `verify_checksum()` implementation substitutes `datasum = 0` if a DATASUM card is absent. These files carry CHECKSUM but omit DATASUM. Zero is correct for the empty primary data block and wrong for the LIGHTCURVE/APERTURE data blocks. This explains the observed primary pass and extension failures from that helper. `verify_datasum() == 2` means missing DATASUM, not failed data integrity. The preserved S4 SHA-256 also matches the original source declaration. The raw-byte result, helper behavior, stored strings and actual data sums are all recorded in `posthoc_diagnostics_results.json`.

## The lossy export has an exact rounding fingerprint

Full-precision reconstruction produces the same 965 bins and 14,332 contributing cadences. Relative to the delivered integer export, 903 time bins differ by -12 to +15 microdays (RMS 5.336 microdays; maximum 1.296 seconds), one SAP value differs by 1 ppm, and all PDC values match.

Rounding **each original per-cadence TIME, SAP_FLUX and PDCSAP_FLUX to four decimal places before calculating bin means** reproduces all 965 values in all three exported columns. It also reproduces both declared normalization medians exactly: SAP 8314.016406666666 and PDC 9555.939393333334. The full-precision medians are 8314.01640625 and 9555.939388020834 respectively.

This is an exact numerical fingerprint of four-decimal intermediate rounding for these bytes. The stored Wolfram retrieval source has no explicit four-decimal operation, so the internal import/serialization step responsible remains an inference rather than independently observed execution. The delivered export is therefore precisely reproducible under that intermediate-rounding model; original FITS remains the appropriate full-precision input for further work.

## Small specified adversarial controls

Four specified alias periods and one white-noise realization were tested; this is not a detection-efficiency map or false-alarm calibration.

- Flat input has exactly zero power and depth. A single white-noise realization has a nonzero phase-optimized maximum, formal SNR 3.04, illustrating that a maximum is not validation.
- A 1000 ppm, 1.5-hour injected box at 3.35992 days is recovered at the specified period, about 1002 ppm. Removing a six-day central interval leaves the correct period maximum, about 1008 ppm, with reduced power. This checks a simple gap case only.
- The same box sequence is equally compatible with two identical eclipses per 6.71984-day binary orbit. It returns the 3.35992-day half-orbit period with the same power. That constructed non-identifiability shows why period recovery and even odd/even agreement cannot alone certify a planet; it is not a full eclipsing-binary light-curve model or a claim about TOI-270.

`posthoc_diagnostics.py` is the executable source; `posthoc_diagnostics_results.json` contains complete values, input identities, unchanged-file checks, and embedded local checksum-method source. The final run took **11.82 seconds** with **71,430,144 bytes peak working set** (about 68.1 MiB), one numerical thread, blocked outbound sockets and no GPU. The earlier Windows priority request was found ineffective and corrected afterward; brief runtime and thread/memory measurements remain valid. No standard-bls or original source files were modified.
