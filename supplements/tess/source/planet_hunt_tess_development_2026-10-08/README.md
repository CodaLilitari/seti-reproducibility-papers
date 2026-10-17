# Planet hunting: TESS development run 01

**2026-10-08 | Lilitari | Known-system recovery benchmark, not a new discovery**

A separate TESS planet-search branch has begun. The existing Kepler Q5 known-transit anomaly protocol and its stages were not altered or executed.

## What ran

An official MAST SPOC light curve for TOI-270 (TIC 259377017), Sector 4, was retrieved via Wolfram. The local runtime could not resolve external DNS and did not have Astropy installed. A compact, deliberately lossy, quality-filtered 30-minute export was transferred with an independently checked compressed-file checksum.

I wrote a NumPy binned box-least-squares (BLS) prototype and searched periods 0.6-13 days. The code was not given catalog periods, epochs or depths. I had already read approximate periods and chose a known system deliberately, so this is source-aware development, not a blind discovery experiment. The bounded search/export choices were saved in PLAN_BEFORE_FLUX.md before the flux export. They were not retuned after the three search results appeared.

The search recovered its three strongest successive positive-depth peaks as follows:

| Iteration | Search period (days) | PDC box depth (ppm) | SAP at the same box (ppm) | Interpretation |
|---|---:|---:|---:|---|
| 1 | 5.65546 | 3366.7 | 3166.6 | Approximately recovers known TOI-270 c; four populated events |
| 2 | 11.37401 | 2704.3 | 2843.5 | Approximately recovers known TOI-270 d; only two populated events |
| 3 | 10.75797 | 776.8 | -272.6 | Processing-sensitive/nuisance peak, not promoted as a planet candidate |

A NASA Exoplanet Archive exact-TIC query AFTER the search returned known periods of 3.35992, 5.66051 and 11.38194 days for b, c and d, respectively. These catalog values are comparison data, not search inputs. The periods measured here are coarse-grid estimates without calibrated uncertainties.

The smaller known planet b was NOT recovered among the three chosen peaks. We preserve that miss rather than tune until success. The third peak and the miss show that this development implementation is not yet ready for a discovery claim or a completeness statement. Opposite SAP/PDC fitted signs are a diagnostic, not proof of which upstream operation caused the peak.

## Input and export

Source:
https://archive.stsci.edu/missions/tess/tid/s0004/0000/0002/5937/7017/tess2018292075959-s0004-0000000259377017-0124-s_lc.fits

The remotely downloaded FITS file was 1,897,920 bytes, SHA-256 09f1e69d89dce001e447fbc509b9453f033b2428d183add334b43b93dbc8c93b. This is a tool-returned remote hash; original FITS bytes were not retained in the local package. The full FITS had 18,684 rows; 14,444 had numeric time and positive finite SAP/PDC with QUALITY=0. Requiring at least ten two-minute measurements per 30-minute bin left 965 bins representing 14,332 original cadences. DATA_REL=42; SECTOR=4; TICID=259377017; TIMESYS=TDB; BJDREFI=2457000; TIMEDEL=0.001388888888888889 day.

Columns in the headerless exported CSV:
1. BTJD multiplied by 1,000,000, rounded to an integer.
2. Median-normalized SAP flux residual in ppm, rounded to an integer.
3. Median-normalized PDC flux residual in ppm, rounded to an integer.

The normalization medians are 8314.016406666666 and 9555.939393333334, respectively. The transferred gzip hash, independently recomputed locally, is ea6d4c0ceb83df5683ab100b93f32e95c5b9cf1fdcaaeb52c39130ca4664e6f6. Decompression produces data/toi270_s4_binned.csv without changes. The transfer excludes per-bin errors, masks and centroids. Time binning can blur short transits; QUALITY=0 is conservative and not asserted to be the optimal scientific mask. PDC and SAP derive from the same observations and are not independent telescope confirmations.

## Method and limits

A one-day moving median, computed separately across gaps longer than half a day, removes slow trends. The primary search uses PDC. A two-level box is fitted on 512 phase bins using counts and sums, over 12,000 uniformly spaced frequencies and a one-to-four-hour duration grid. The objective is the decrease in residual sum of squares. Three successive peaks are searched, masking intervals around preceding recovered events. At least two populated events are required by the prototype. A separate direct least-squares calculation checks the bin-based objective on an injected synthetic example.

The mask/refit is a development approximation, not a full simultaneous multi-planet model. The median baseline may suppress longer or crowded signals. Search scores are NOT false-alarm probabilities or calibrated sigma levels. No target-pixel localization, centroid vetting, odd/even validation, secondary-eclipse test, physical transit fit, detrending sensitivity study, injection-recovery efficiency map or novelty audit was completed. Known-planet recovery is partial, not final validation of the search.

## Replay

Dependencies used locally are recorded in environment.json. With NumPy installed:

    python verify.py
    python search.py
    python -m unittest test_search -v

search.py overwrites the development result files, so work in a COPY to preserve the originally delivered artifacts. verify.py is read-only. Six tests passed; they are implementation checks, not six independent astronomical validations. No external model/API calls are needed for local replay. Results may differ in last floating-point digits between platforms.

## Next useful work

Use the original two-minute FITS and a second sector of this development system. Cross-check the custom prototype against a standard BLS implementation; quantify recovery and aliases with synthetic injections including no-transit and eclipsing-binary cases. Freeze the candidate-screen criteria before choosing the unfamiliar-star cohort. A reasonable first search is 20 nearby K/M dwarf hosts with at least three archived TESS sectors, chosen by metadata rather than their light-curve appearance. Fit/search on designated earlier sectors, freeze predicted times, and test the later sector without refitting the ephemeris. That sector remains archival holdout data, not genuinely prospective unseen observations. Pixel-level localization and catalog/literature checks are needed for any surviving candidate.

This is a proposed continuation, not an executed 20-star survey. No new-candidate target universe was queried. No paid computation was purchased, no correspondence was sent, and no background run was scheduled.

## Primary methodological and catalog sources

- NASA discovery description and original known-planet attribution: https://svs.gsfc.nasa.gov/13200/
- NASA TESS program listing tying TOI-270 to TIC 259377017: https://heasarc.gsfc.nasa.gov/docs/tess/approved-programs.html (G03196).
- Kovacs, Zucker & Mazeh (2002), original BLS method: https://arxiv.org/abs/astro-ph/0206099
- Astropy BLS documentation, consulted for method description, not used as the local implementation: https://docs.astropy.org/en/stable/timeseries/bls.html
- NASA Exoplanet Archive TAP: https://exoplanetarchive.ipac.caltech.edu/docs/TAP/usingTAP.html

Public data credit: TESS mission and MAST; the underlying known-planet discovery belongs to the published TOI-270 discovery team. This package is an AI-assisted local development benchmark, not independent expert peer review.
