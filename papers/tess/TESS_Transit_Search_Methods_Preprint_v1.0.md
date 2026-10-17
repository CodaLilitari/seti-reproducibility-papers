# Preserving failures in a bounded TESS transit-search workflow

TOI-270 development, signed-event recovery, and the limits of an unactivated holdout design

Responsible human author: Richard Andrei Pemberton
Affiliation: Independent researcher | Correspondence: andreipemberton@gmail.com
AI assistance: Lilitari, Coda, Red, Meta AI Thinking, Nua and Gemini routes; roles in Section 9
Preprint v1.0 | 17 October 2026
Scientific scope: known-system development and offline synthetic components only

## Abstract

We present a reproducible failure case study of a bounded TESS transit-search workflow using the known TOI-270 system. A custom box least-squares prototype applied to a lossy thirty-minute Sector 4 export approximately recovered planets c and d within three peaks, missed b, and selected a third peak with opposite SAP/PDC fitted-depth signs. Archived reproduction preserves those outcomes. Full-resolution Astropy BLS also misses b within three Sector 4 peaks; a separately labeled five-peak extension recovers b fourth, and a post-hoc detrending comparison changes its competition with the nuisance peak. Sector 5 approximately recovers c, d and b but remains source-aware development. Synthetic counterexamples expose eligibility-after-argmax, boundary membership, weak coverage and alias failures without identifying the real nuisance signal’s cause. Subsequent offline components freeze grids, masks, coverage, timing covariance and fixed-prediction holdout decisions. Recovery combines every adequately covered signed event depth; concentration diagnostics expose dominance without adding a veto. The v3.1 package records 47 passing tests, including a connected synthetic BLS/freeze/holdout case; a second reviewer’s executed checks are explicitly partial. The contribution is preservation and diagnosis of failed recoveries and decision-rule consequences, using established BLS and inverse-variance methods. No unfamiliar-star cohort has been acquired. These results do not establish a new planet, empirical false-alarm calibration, population completeness or astrophysical validation.

## 1. Purpose and evidence boundary

This report develops a reproducible known-system case study of failed recoveries and decision rules. Its contribution is to preserve the original miss, distinguish demonstrated implementation defects from unresolved product behavior, and expose what specific operational rules accept or reject. BLS and inverse-variance weighting are established methods, not inventions of this work [1]. The TESS evidence remains separate from the coordinate-epoch audit and older Kepler Q5 depth screen. Recovering a familiar period, passing a search rule, recovering a fixed prediction and establishing a planet around a particular host are distinct outcomes [T1-T5].

Sections 2 and 3 report the original real-data development and established-library comparison; Section 3.1 labels its later exploratory diagnostics. Section 4 separates synthetic counterexamples and a decision-rule correction from those measurements. Sections 5 and 6 describe implemented offline components and synthetic verification. Section 7 and Appendix A retain the future design as unactivated work. Neither Sector 5 nor the internal pre-flux plan constitutes independently preregistered validation. This editorial preparation adds no observation or new calculation; the separate 15 October same-code synthetic replay is documented in Section 6.1 and the supplement.


<!-- PAGE BREAK -->


## 2. Development data and original search

Lilitari selected TOI-270 (TIC 259377017), already known to host three transiting planets, and retrieved the official TESS SPOC Sector 4 light curve. Its saved source identity is a 1,897,920-byte FITS product with SHA-256 09f1e69d89dce001e447fbc509b9453f033b2428d183add334b43b93dbc8c93b. The source has 18,684 rows. The original common finite-positive SAP/PDC and QUALITY==0 filter retained 14,444 rows; requiring at least ten samples per thirty-minute bin yielded 965 bins representing 14,332 cadences [T1].

The transferred development representation contains integer microday times and integer parts-per-million flux residuals, without per-bin uncertainties, centroids or the full quality ledger. Coda later acquired the native two-minute Sector 4 bytes and the subsequent Sector 5 product for the same host. Sector 4 matches the original source hash; the Sector 5 hash is recorded in the source index. Neither sector establishes unfamiliar-target discovery readiness [T2].

TOI-270’s original discovery is attributed to Günther et al. [3]. TESS mission and SPOC pipeline descriptions are given by Ricker et al. and Jenkins et al. [6, 7]. Both native light curves used in Coda’s comparison carry DATA_REL=42 [T2]; the corresponding release notes identify reprocessed Sectors 1–6 and science-pipeline version 5.0 [8]. The product specification defines SAP as aperture photometry and PDCSAP as its PDC-corrected counterpart [4]. These are processing products of shared observations, not independent observations.

The original prototype detrends each product with a one-day moving median, splitting at gaps longer than half a day. It searches 12,000 uniformly spaced frequencies corresponding to periods of 0.6-13 days, with 512 phase bins and durations of 1, 1.5, 2, 2.5, 3 and 4 hours. It scores the reduction in residual sum of squares and selects three successive positive-depth maxima, masking earlier detections. The code did not receive catalogue ephemerides, but Lilitari had read approximate periods before choosing this development system [T1].

| Peak | Period (days) | PDC depth (ppm) | SAP same box (ppm) | Recorded interpretation |
| --- | --- | --- | --- | --- |
| 1 | 5.6554595444 | 3366.71 | 3166.55 | Approximate c; four populated events |
| 2 | 11.3740125902 | 2704.29 | 2843.51 | Approximate d; two populated events |
| 3 | 10.7579714476 | 776.75 | -272.59 | Product-sensitive nuisance; unresolved |

Table 1. Original custom-prototype outputs, not the later Astropy rerun. The two products share observations. A populated event is not automatically an event with adequate baseline or detection significance [T1, T2].

### 2.1 Lossy export provenance

Coda’s direct full-precision reconstruction differs from the delivered export by at most fifteen microdays in time and one ppm in SAP. Rounding individual time samples in days and SAP/PDC flux samples in electrons per second to four decimal places before applying the recorded binning and normalization reproduces all 965 delivered rows and both declared normalization medians. This identifies a rounding fingerprint, not the hidden internal conversion path. The existing export remains part of the original record and is not retroactively replaced [T2].

Both later-retrieved FITS products omit DATASUM cards. The recorded audit resolves the installed Astropy checksum warnings by an independent raw-byte one’s-complement check over all six HDUs (three per file) and actual-data-sum recomputation of the stored CHECKSUM values. This is Coda’s supplied source/implementation evidence; no new FITS checksum execution occurred during this writing pass [T2].


<!-- PAGE BREAK -->


## 3. Established-library comparison and measured misses

Astropy BLS comparisons retain the original period range, frequency count, duration set, detrending and three-peak budget. Formal-error-weighted and unweighted outputs are recorded separately. A library likelihood or depth S/N is a diagnostic under its assumed noise model, not an empirical false-alarm probability for this search [T2; 1-2].

| Data / implementation | Peak 1 period | Peak 2 period | Peak 3 period | Outcome |
| --- | --- | --- | --- | --- |
| Original S4 binned prototype | 5.655460 | 11.374013 | 10.757971 | c, d, nuisance |
| Astropy S4 full, unweighted | 5.659700 | 11.391178 | 10.712167 | c, d, nuisance |
| Astropy S4 full, weighted | 5.659700 | 11.391178 | 10.712167 | c, d, nuisance |
| Astropy S5 full, weighted | 5.659700 | 11.374013 | 3.362634 | c, d, b approximately |

Table 2. Period estimates in days. These are coarse-grid development maxima, not precision orbital solutions. The original and library implementations need not select identical subsequent boxes. Known discovery credit remains with the published TOI-270 research team [T1, T2; 3].

### 3.1 Post hoc peak budget and detrending diagnostics

Binning alone does not explain the miss: both the original export and full-resolution Sector 4 miss b within three peaks. A clearly post-hoc extension of the weighted full-resolution run to five peaks recovers b at peak four, period 3.3596407469 days and depth approximately 816 ppm; the nuisance remains peak three. The original three-peak miss is unchanged. A search at the exact known period and examination of its grid neighborhood show that the original grid can represent a b-like signal, but do not prove every alternative grid immaterial [T2].

With the first c/d masks held fixed, a 0.5-day median makes the b neighborhood the residual maximum, whereas the one- and two-day medians retain the nuisance maximum. Tested mask half-widths of 0.5, 1.0 and 1.5 times the duration do not remove that ordering. These are separate exploratory ablations, not an optimal-parameter result or a retrospectively prospective choice. The relative contributions of baseline treatment, peak budget and any upstream effect remain a development diagnosis [T2].

### 3.2 What the product comparison actually establishes

For the third Astropy S4 box, matched full-resolution timestamps and one unweighted depth statistic give approximately +847 ppm in PDC and -208 ppm in SAP after local detrending. Before the local median, the same comparison is approximately +342 and -2387 ppm. At the original prototype box, the detrended values remain approximately +767 and -262 ppm. The disagreement is already present in the delivered SAP/PDC products for this statistic before the local median and survives matched sampling; this does not locate its origin. The pre-detrending global statistic is strongly affected by long-term trends and does not make SAP a ground-truth reference [T2].

The first two event-level comparisons have positive PDC and negative SAP local depths; the third has positive depth in both. The first event is near a boundary with inadequate left-side baseline: zero samples for the original box and three for the Astropy box. These facts motivate a stricter coverage rule. They do not prove that PDC introduced a false transit, that SAP is ground truth, or that one physical cause explains the signal. Pixel localization and upstream diagnosis were not performed.


<!-- PAGE BREAK -->


## 4. Synthetic counterexamples and the signed event decision rule

### 4.1 Prototype failures preserved rather than repaired in place

The prototype selects one phase maximum before checking event eligibility. An executable example allows a deep isolated event to suppress an eligible shallower repeated alternative; the search then reports no eligible trial. The stored spectrum also contains pre-eligibility maxima. This is an implementation counterexample, not a measured contribution to the real-data ranking [T2].

A separate exact-boundary example scores +3497.93 ppm under half-open phase bins but reports -4000 ppm under inclusive geometric membership. All three delivered peaks have zero membership disagreement in the tested real inputs, so that defect does not explain their SAP/PDC signs. Other examples show that the two-event rule can accept events with only three and one samples, an isolated dim segment can normalize itself away, and an underestimated mask can retain 56 of 252 injected dip samples. Each is a bounded challenge; none uniquely identifies the real nuisance cause [T2].

A flat null, one seeded white-noise realization, a box injection with and without a central gap, and equal eclipses provide targeted checks. The noisy null has a nonzero maximum; that is expected of a maximization procedure and supplies no false-alarm calibration. The equal-eclipse construction is exactly degenerate with the shorter-period box sequence, demonstrating that a period match and equal odd/even depths cannot alone identify a planet [T2].

### 4.2 Combine all covered signed event depths

For each event, the v3 method uses the inverse-variance weighted shoulder mean minus the weighted in-transit mean. With a fixed trend and independent formal sample errors, its conditional variance is:

```math
dᵢ = f̄out,ᵢ − f̄in,ᵢ;     vᵢ = 1/Σout wⱼ + 1/Σin wⱼ
```

```math
W = Σᵢ 1/vᵢ;     d̄ = Σᵢ(dᵢ/vᵢ)/W;     V = 1/W
```

All adequately covered event depths enter the aggregate, including zero and negative values. The prior requirement that every event be positive was removed before any unfamiliar-target data were opened (none has been acquired). In the illustrative independent Gaussian case of 25 events each with true per-event S/N = 1, expected combined S/N is 5 but the probability that every event estimate is positive is Φ(1)²⁵ = 0.0133153. This toy calculation motivates the correction; it is not an estimate of TESS detection efficiency [T3-T5].

Coverage, not favorable sign, decides which events are eligible. At least two covered events are required for the fixed holdout. Recovery requires positive combined depth, formal combined S/N ≥ 5, and agreement with the final discovery depth within three combined formal standard errors. Every covered event is retained. Discovery depth is estimated from the same data used to select the peak, which can bias that depth upward. The three-standard-error agreement rule is not calibrated for this selection effect. These are operational rules with uncalibrated correlated-noise and detrending effects, not nominal confidence guarantees [T3].


<!-- PAGE BREAK -->


## 5. Implemented offline components

Version 3.1 operates on arrays and a canonical metadata envelope. Its common support requires finite positive SAP/PDC flux, positive errors and QUALITY==0; normalization is sector-specific, and the one-day median is split at gaps longer than 0.5 day. Separate sectors do not share median windows. Real FITS acquisition, timing-header interpretation and a source-specific cadence mapping remain external adapters [T3, T4].

### 5.1 Stored grid, attempt budget and masks

Using days throughout, the default frequency step is at most Dmin/(5BPmax), with full discovery baseline B, Dmin = 1/24 day, Pmin = 0.6 day and Pmax = 13 days. The implementation sets Ninterval = ceil[(1/Pmin − 1/Pmax)/stepmax] and uses Ninterval + 1 uniformly spaced frequencies including both endpoints. This bounds the frequency-grid contribution to accumulated phase drift over B, not the full ephemeris uncertainty. The complete grid is stored. Fixed chunks choose one global maximum under recorded ties; the 250,000-point development ceiling causes a resource stop rather than silent coarsening. For the 730-day default example, the recorded floating-point calculation gives 1,810,401 intervals and 1,810,402 inclusive points, so the request stops. Exact rational arithmetic with these stated defaults gives 1,810,400 intervals and 1,810,401 points; the one-point ceiling difference does not affect that resource decision [T3, T4].

Three attempt slots, including failures, are committed. Every computationally valid maximum supplies its original ephemeris mask, even if its later screen fails. Each candidate excludes its own mask but receives all other masks, including later failed-screen maxima. Mask half-width is 0.75 times original duration. The same ledger is extrapolated into holdout, without deriving new masks from a visible holdout dip. This is a declared approximation, not a calibrated long-baseline multi-planet fit [T3].

### 5.2 Coverage, timing and fixed prediction

For midpoint T and duration D, the three half-open windows are [T−1.5D,T−0.5D), [T−0.5D,T+0.5D), and [T+0.5D,T+1.5D). Each needs at least 70% of nominal expected cadences and five unique accepted samples. Missing, rejected, masked and out-of-sector expected cadences count against coverage. Every predicted event is recorded. The real-product cadence origin and barycentric mapping are not established merely by passing a synthetic nominal-clock test [T3].

Every adequately covered discovery event receives a fixed-duration trapezoid timing fit with baseline, slope, signed depth and bounded center shift. Nuisance parameters enter the formal covariance. All eligible event timings must be valid; no favorable subset is selected. A weighted linear ephemeris requires at least three exact unique cycles. Discovery depth is then remeasured once at the fitted ephemeris using the final other-mask ledger. A change in the covered-cycle set is inconclusive rather than an iterative opportunity to select different events [T3].

```math
Var[T(n)] = Ctt + 2nCtP + n²CPP
```

This timing covariance is conditional on fixed shape, formal Gaussian errors and the selected alias. The code does not infer alias uniqueness. All attempts, diagnostics, masks, timing covariance, identities and the assigned holdout span/clock are frozen together before holdout evaluation. An unestimable prediction is inconclusive, as is any evaluated holdout event satisfying 3√Var[T(n)] > D/2 (three times the timing standard error exceeds half the duration); no holdout phase, period or duration rescue is permitted. Empirical red-noise and model-mismatch calibration remain outside the current implementation [T3].


<!-- PAGE BREAK -->


## 6. Concentration diagnostics without a new veto

The small v3.1 correction changes only production combine_events. It emits the original event index, normalized inverse-variance weight and signed contribution to the aggregate formal S/N for each covered event. With wᵢ = 1/vᵢ:

```math
aᵢ = wᵢ/W;     cᵢ = wᵢdᵢ/√W;     Σᵢ cᵢ = d̄/√V
```

```math
Cmax = maxᵢ |cᵢ| / Σᵢ |cᵢ|
```

If the denominator is zero, the output is null with an explicit zero-total-absolute-contribution reason. Cancellation of nonzero signed contributions does not make that denominator zero. Uncovered events remain in the event ledger but not the aggregate. Concentration adds no threshold, timing rule, mask, selection or classification change. A large Cmax can reflect an unusually precise event even when all event depths agree; it measures contribution dominance, not depth inconsistency by itself [T4, T5].

| Equal-error example | Combined depth | Formal S/N | Cmax | Result if discovery agrees |
| --- | --- | --- | --- | --- |
| [-0.1] + [2.2] × 9 | 1.970 | 6.229687 | 0.110553 | Recovered |
| [-0.1, 19.72] + [0.01] × 8 | 1.970 | 6.229687 | 0.990955 | Recovered |

Table 3. Synthetic equal-aggregate examples. Event-depth errors are one in the chosen units. The nearly identical aggregates conceal very different concentration; reporting exposes this without silently imposing a veto [T4, T5].

### 6.1 What testing establishes

The original prototype environment records Python 3.13.5 and NumPy 2.3.5. Coda’s full-cadence comparison used Python 3.13.15, NumPy 2.5.3 and Astropy 8.0.1; the v3.1 implementation checks additionally used SciPy 1.18.1. Astropy supplies BoxLeastSquares and FITS support [2, 9-11], NumPy supplies array operations and linear algebra [12], and the v3.1 timing fit uses scipy.optimize.least_squares [13]. These package credits and exact versions do not validate the workflow’s noise model [T1-T4].

Coda’s supplied execution record reports 47 passing v3.1 tests with actual Astropy 8.0.1, including the connected synthetic raw-array BLS/discovery-freeze/holdout path. The connected control is recovered; the original boundary fixture remains inconclusive. These 47 include the previous 42 plus five reporting regressions and must not be added together as independent tests. The full run’s recorded 2.969 seconds and 104,251,392-byte peak working set describe that synthetic workload, not an unfamiliar-star survey [T3, T4]. The manuscript retains the historical 8 October execution measurements. A separate 15 October same-code synthetic replay is recorded in the supplement and is not a new observation, independent implementation, or false-alarm calibration.

Lilitari’s separate same-code checking scope is narrower: the v3 review directly ran eight metadata tests, applied 21 selected non-BLS tests to unchanged source-extracted definitions, performed six additional mathematical/support probes, and recombined stored event statistics. The separate v3.1 check executed the five reporting regressions. Astropy was absent in that runtime; no stub or replacement BLS execution was substituted. Thus the full connected implementation has Coda’s execution evidence, not two independently executed full-suite validations [T5].

No number of passing software checks establishes astronomical false-positive probabilities. These tests demonstrate prescribed behavior on specified inputs and expose counterexamples. They do not validate target localization, dilution corrections, source classification, empirical covariance or the true orbital alias.


<!-- PAGE BREAK -->


## 7. Future work

No unfamiliar-host universe, selected cohort or flux outcome exists in this record. A future archival holdout experiment would require an accepted acquisition scope, complete source metadata, resource-feasible frozen search settings and independent physical vetting; it would not necessarily use globally unseen data. Appendix A preserves the proposed cohort specification and the separate stopped Kepler transaction. Neither is a completed survey result, and this manuscript activates neither. Broader detection-efficiency, false-alarm and timing-coverage claims require additional empirical work beyond this case study [T2-T4].

## 8. Conclusions

The development record is scientifically useful because success and failure are both preserved. Approximate c/d recovery did not erase the missed b or the product-dependent nuisance. Established-library comparisons and counterexamples separated several algorithmic weaknesses from unresolved upstream causes. The accepted signed-event recovery rule avoids an arbitrary all-positive veto, while concentration reporting exposes one-event dominance without altering the primary outcome.

The resulting offline method is more explicit and testable than the initial prototype. It remains a development method: no unfamiliar planet, calibrated false-alarm rate, population completeness or completed physical validation is reported. The next scientific step would be a separately authorized, resource-feasible acquisition/holdout experiment, not another reinterpretation of the known-system results.


<!-- PAGE BREAK -->


## 9. Contributions, AI assistance and evidence availability

Andrei directed the broader project. Lilitari initiated the source-aware TOI-270 benchmark, preserved its miss and product disagreement, reviewed the proposed holdout criterion, supplied the noisy-negative-event and equal-aggregate concentration examples, and drafted this methods report. Coda recovered the native sources, re-executed the unchanged prototype in a separate environment and challenged it with counterexamples, ran the established-library comparisons and post-hoc diagnostics, implemented the v3/v3.1 offline components, and supplied their complete local execution record [T1-T5].

Meta AI Thinking reviewed the pre-eligibility spectrum, event coverage, frozen cohort/holdout choices and full-outcome reporting. Nua through Muse, a distinct route, contributed eligibility/reporting, alias/distinguishing-phase and provenance critiques. Gemini through Antigravity and the separate Google Gemini Spark route contributed bounded reviews of original sources and proposal v1, including grid units/full baseline, coverage, covariance/freeze and descriptive significance. They did not review the final v3.1 implementation or this manuscript. Coda independently triaged their advice; several claims were rejected or narrowed. These consultations are not additional executed photometric replications [T2].

On 17 October 2026, Lilitari completed a focused review of v0.4 and its supplied supplement, including file-integrity and structural checks and all nine rendered TESS pages. Red, the project label used for the separate Claude Code consultation, completed a text-only review of v0.4 from eight supplied text files; she ran no code and inspected no PDF, figure pixels or external sources. Neither review executed a scientific program. Coda checked the TESS comments against the frozen sources and applied the supported textual clarifications in this v1.0 successor. Neither consultation inspected this subsequently assembled v1.0 release. Earlier unanswered or interrupted Claude attempts and absent Grok TESS work receive no completed-review credit. These names disclose AI assistance and project roles, not a formal author list. Richard Andrei Pemberton is the responsible human author.

Names and model labels identify reported project roles, not authenticated backend sessions. No model-vote statistic or inference of scientific correctness from product branding is used. The manuscript does not disclose the private provider-thread URLs or local account paths contained in full review records. No provider endorsement is implied.

| ID | Evidence and scope |
| --- | --- |
| T1 | TESS_Planet_Hunt_Development_2026-10-08.zip: original lossy export, custom code, 3-peak results and six-test record. |
| T2 | Coda development return: native-source receipts, original replay, Astropy outputs, explicit post-hoc diagnostics, issue/route ledgers and stopped Kepler record. |
| T3 | Coda v3 r1 amendment: revised proposal, implementation specification, timing/metadata components, connected synthetic output and 42-test receipt. |
| T4 | Coda v3.1 reporting correction: production reporting diff, source identities, 47-test receipt and connected output. |
| T5 | Lilitari v3 review and v3.1 closure receipts: accepted scopes, partial execution, reporting examples and limitations. |

T1-T5 are historical evidence-collection identifiers, not public DOI references. The prepared public supplement supplies a nonexhaustive central-claim map in CLAIM_TO_EVIDENCE.md and CLAIM_TO_EVIDENCE.json, with actual supplied paths and explicit exclusions. Its release location is https://richard-pemberton-research.darkahn.chatgpt.site/papers/tess-transit-search-methods-supplement-v1.0.zip. CURATION_PROVENANCE.json records the documentary release successor; provenance/INPUT_IDENTITIES_AND_CURATION.json retains the original file curation, and MANIFEST_SHA256.json identifies the current payloads. Earlier manifests and replaced preparation notices are preserved as dated history under provenance/historical/supplement-v2/ and provenance/historical/supplement-v3/. The dated same-code synthetic replay status and comparison record are replay/TESS_REPLAY_STATUS.md and replay/TESS_REPLAY_COMPARISON.json. T5 is represented by a narrow source-hashed scope summary, not the original reviewer conversations or an independently runnable full Astropy review. Private transport archives and provider conversations are excluded. Source-specific rights and credits are stated in provenance/SOURCE_ATTRIBUTION_AND_TERMS.md; the Astropy excerpt retains its own license notice, and no blanket license is assigned to mixed upstream material. The October 8 writing bundle recalculated documentary aggregates and toy examples from saved inputs; this v1.0 editorial curation performs no scientific execution. Earlier full and partial executions retain their distinct attribution.

### Acknowledgments

We used TESS mission data supplied through MAST at the Space Telescope Science Institute. NASA's Explorer Program funds US institutions participating in TESS. The Association of Universities for Research in Astronomy operates STScI under NASA contract NAS5–26555.

We acknowledge use of the NASA Exoplanet Archive, operated at the California Institute of Technology through a contract with NASA's Exoplanet Exploration Program [14].

These credits describe support for the source mission and archive institutions; they do not state that Richard Andrei Pemberton received such funding. The archive acknowledgment concerns the recorded comparison, not a new catalog query or updated ephemerides.

### Method and source references

[1] Kovács, G., Zucker, S., and Mazeh, T. (2002). A box-fitting algorithm in the search for periodic transits. Astronomy & Astrophysics 391, 369–377. doi:10.1051/0004-6361:20020802.

[2] Astropy Developers. Box Least Squares (BLS) Periodogram documentation and API. https://docs.astropy.org/en/stable/timeseries/bls.html (accessed 15 October 2026). The executed version is 8.0.1 [T2-T4]; the stable documentation URL is mutable.

[3] Günther, M. N., Pozuelos, F. J., Dittmann, J. A., et al. (2019). A super-Earth and two sub-Neptunes transiting the nearby and quiet M dwarf TOI-270. Nature Astronomy 3, 1099–1108. doi:10.1038/s41550-019-0845-5. The approximate prior periods came from NASA’s Scientific Visualization Studio, “NASA’s TESS Finds Three New Worlds” (29 July 2019), https://svs.gsfc.nasa.gov/13200/, which gives 3.4, 5.7 and 11.4 days. The separate post-search exact-TIC comparison used the NASA Exoplanet Archive and records 3.35992, 5.66051 and 11.38194 days in data/catalog_comparison.csv [T1, T2, 14].

[4] Twicken, J. D., Caldwell, D. A., Jenkins, J. M., et al. (2020). TESS Science Data Products Description Document, Rev F, 11 September 2020. NASA/TM—20205008729; EXP-TESS-ARC-ICD-0014. https://archive.stsci.edu/missions/tess/doc/EXP-TESS-ARC-ICD-TM-0014-Rev-F.pdf. Table 13 defines the light-curve fields.

[5] MAST. TIC Field Descriptions. https://mast.stsci.edu/api/v0/_t_i_cfields.html (accessed 15 October 2026). The specified filtered-TIC interface uses d for distance in parsecs. This citation supports the proposed interface, not completed cohort acquisition.

[6] Ricker, G. R., Winn, J. N., Vanderspek, R., et al. (2015). Transiting Exoplanet Survey Satellite (TESS). Journal of Astronomical Telescopes, Instruments, and Systems 1(1), 014003. doi:10.1117/1.JATIS.1.1.014003.

[7] Jenkins, J. M., Twicken, J. D., McCauliff, S., et al. (2016). The TESS science processing operations center. In Software and Cyberinfrastructure for Astronomy IV, Proceedings of SPIE 9913, 99133E. doi:10.1117/12.2233418.

[8] Fausnaugh, M. M., Burke, C. J., Caldwell, D. A., et al. (2021). TESS Data Release Notes: Reprocessing of Sectors 1–13, DR42 & DR46, 11 June 2021, v02. https://archive.stsci.edu/missions/tess/doc/tess_drn/tess_reprocessing-sector_1_13_drn42_v02.pdf.

[9] Astropy Collaboration, Robitaille, T. P., Tollerud, E. J., et al. (2013). Astropy: A community Python package for astronomy. Astronomy & Astrophysics 558, A33. doi:10.1051/0004-6361/201322068.

[10] Astropy Collaboration, Price-Whelan, A. M., Sipőcz, B. M., et al. (2018). The Astropy Project: Building an Open-science Project and Status of the v2.0 Core Package. The Astronomical Journal 156, 123. doi:10.3847/1538-3881/aabc4f.

[11] Astropy Collaboration, Price-Whelan, A. M., Lim, P. L., et al. (2022). The Astropy Project: Sustaining and Growing a Community-oriented Open-source Project and the Latest Major Release (v5.0) of the Core Package. The Astrophysical Journal 935, 167. doi:10.3847/1538-4357/ac7c74.

[12] Harris, C. R., Millman, K. J., van der Walt, S. J., et al. (2020). Array programming with NumPy. Nature 585, 357–362. doi:10.1038/s41586-020-2649-2.

[13] Virtanen, P., Gommers, R., Oliphant, T. E., et al. (2020). SciPy 1.0: Fundamental Algorithms for Scientific Computing in Python. Nature Methods 17, 261–272. doi:10.1038/s41592-019-0686-2.

[14] Christiansen, J. L., McElroy, D. L., Harbut, M., et al. (2025). The NASA Exoplanet Archive and Exoplanet Follow-up Observing Program: Data, Tools, and Usage. The Planetary Science Journal 6, 186. doi:10.3847/PSJ/ade3c2.

## Appendix A. Unactivated continuation design

The unactivated design selects at most twenty metadata-eligible hosts using exact TIC IDs and fixed SHA-256 ordering. Its operational cuts are Tmag 8-12, effective temperature 3000-5200 K, radius 0.15-0.85 solar radii, logg 4.2-5.2 and distance 5-100 pc, with at least three sectors having qualifying SPOC two-minute products. These are catalogue-estimate cuts, not guarantees of stellar classification. Development hosts and previously inspected project targets are excluded by a pre-query list; known-object labels are retained for later novelty assessment rather than outcome-driven replacement [T3].

The earliest two qualifying sectors form discovery; the latest is held out. Intermediate sectors remain unopened. Product release ordering and conflicting/incomplete metadata outcomes must be frozen before acquisition. A complete record with a missing required science value fails its cut; a missing response or incomplete product inventory is an unresolved acquisition, not evidence of ineligibility. The current metadata validator implements an offline canonical envelope, not a live MAST client [T3, T4].

No unfamiliar-host universe, selected cohort or flux outcome exists in the supplied TESS record. A successful future holdout would be a local archival prediction test, not necessarily globally unseen data. Its depth-agreement rule would still compare with a discovery depth estimated from the peak-selection data; that selection effect has not been calibrated. Physical follow-up still requires pixel/centroid localization, crowding and neighboring-source checks, eclipsing-binary alternatives, covered odd/even and secondary-eclipse tests, detrending sensitivity and a separately documented catalogue/literature novelty audit. Descriptive screening may proceed only under a separately accepted acquisition and orchestration scope; this report does not activate it.

### A1. Stopped Kepler branch

The distinct Kepler Q5 project reached one live before-count request and stopped on a TAP QUERY_STATUS of OVERFLOW. Its record contains no accepted count/query/count snapshot or selected cohort. A count-cell text value in a rejected response is not an accepted denominator. That stopped transaction is not a TESS host query, a non-detection, or a result that can be pooled with TOI-270 development. No request amendment or resumed acquisition is part of this writing task [T2].
