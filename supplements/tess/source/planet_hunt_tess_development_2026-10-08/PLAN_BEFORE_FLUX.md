# TESS planet hunting: development recovery test

Date: 2026-10-08. Separate from the frozen Kepler Q5 known-transit screen.

TOI-270 (TIC 259377017), Sector 4, is a deliberately known multi-planet calibration target. The investigator has already read approximate catalog periods (3.4, 5.7, 11.4 days). This is not a blind study, and the target is not a new candidate. The period-search code must not receive those periods, transit epochs or catalog depths.

Input: single official SPOC Sector 4 light curve listed by the MAST target directory, DATA_REL=42. The runtime cannot retrieve the FITS bytes directly. A remotely calculated, compressed column export will be used, with its limitations and archive-derived original-file checksum recorded if available.

Export: retain rows with numeric time/SAP/PDC, positive flux, QUALITY=0. Group by floor(TIME*48), a fixed 30-minute grid. Require at least 10 surviving two-minute cadences per bin. Use mean time and mean SAP/PDC flux; normalize each product by its median binned flux. Export time rounded to 1e-6 day and both normalized products rounded to 1 ppm as integers. No catalog transit mask or outcome-driven exclusions.

Search: PDC primary. Divide by a 1-day running median estimated separately on contiguous data segments (gaps >0.5 day). Uniform-frequency trial grid for periods 0.6 to 13 days, 12000 trials; 512 phase bins; absolute duration grid 1.0,1.5,2.0,2.5,3.0,4.0 hours. Fit a two-level box by unweighted least squares. Iterate three peaks, masking +/-0.75 fitted durations around previously recovered transit centers. No period or epoch prior. Require at least two populated transit events, and report the two-event limitation explicitly. The periodogram statistic is diagnostic and not a false-alarm probability. No radius, validation or novelty claim.

Do not alter the already-frozen Kepler artifacts, execute its pending acquisition, contact anyone, or use paid API resources. Any implementation corrections during this development run must be recorded. A separate unfamiliar-star target rule and validation tests are future work, not declared completed here.
