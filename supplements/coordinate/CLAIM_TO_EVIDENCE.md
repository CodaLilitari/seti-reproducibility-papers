# Non-exhaustive coordinate claim-to-evidence map

V1.0 documentary pointer: all claim entries and numerical evidence below are retained unchanged from v3/v2. The four external ReadMe references are identified in `analysis/ren2024/ren2024-assessment/g-surveys/DOCUMENTATION_REFERENCES.json`. Current bundled paths are defined only by `MANIFEST_SHA256.json`; the two provenance-only source changes have static proof in `derivations/readme-omission/`, and their subsequent two-command execution is recorded in `status/README_OMISSION_RUNTIME.json`.

This map retains 25 historical claim-ledger entries plus COV-01, one added coverage entry. It is not an exhaustive audit of every manuscript sentence. All supplied file paths below are relative to this supplement root. Blank paths mean interpretive, literature or private historical attribution support rather than a delivered numerical command. Numerical replay qualifications are in `status/REPLAY_COMPARISONS.json` and `status/COORDINATE_REPLAY_STATUS.md`.

## A01 — 4; Appendix A and B

43 central-value rows, with 24 A-F/12 H-J/7 radio

Supplied evidence: [support/astrometry/rowwise_offsets.csv](support/astrometry/rowwise_offsets.csv); [analysis/d1-core/independent_core_check.py](analysis/d1-core/independent_core_check.py)

Preserved numerical reconstruction; summaries recalculated in assembly Comparison tolerance is not a measurement error or significance threshold.

Use recorded inputs and the isolated replay receipt; a supplied command is not itself proof of successful execution.

## A02 — 4; Figure 1

Per-object shifts and arithmetic mean

Supplied evidence: [support/astrometry/effective_epoch_fits.csv](support/astrometry/effective_epoch_fits.csv); [analysis/d1-core/independent_core_check.py](analysis/d1-core/independent_core_check.py)

Preserved historical fitted outputs and figure; no figure regeneration in the replay. Mean of optima differs from pooled fit; no fit-confidence interval claimed.

Original figure-generation code is not supplied; numerical fit replay and preserved figure bytes are separate. The one I optimizer discrepancy and its two representations remain in status/REPLAY_COMPARISONS.json; Figure 1 retains the historical reference identity.

## A03 — 3.2; 4

Pooled A-F optimum -16.00235 years

Supplied evidence: [support/astrometry/coda_joint_and_individual_fits.csv](support/astrometry/coda_joint_and_individual_fits.csv); [analysis/controls/falsification/audit_falsification.py](analysis/controls/falsification/audit_falsification.py)

Coda executed fit retained Not an independent blinded experiment or an uncertainty estimate.

Use recorded inputs and the isolated replay receipt; a supplied command is not itself proof of successful execution.

## A04 — 4.1

A W1/W2 radius changes and D W3 increase

Supplied evidence: [support/astrometry/rowwise_offsets.csv](support/astrometry/rowwise_offsets.csv); [analysis/d1-core/independent_core_check.py](analysis/d1-core/independent_core_check.py)

Arithmetic on preserved centroids and Gaia inputs No re-extracted images; change is vectorial, not a scalar subtraction.

Use recorded inputs and the isolated replay receipt; a supplied command is not itself proof of successful execution.

## A05 — 3.3; 5

36/36 printed Table10 triples compatible; only 2/24 stated-epoch A-F replacements

Supplied evidence: [support/astrometry/rayleigh_rounding_tests.csv](support/astrometry/rayleigh_rounding_tests.csv); [support/astrometry/table10_compatibility.csv](support/astrometry/table10_compatibility.csv); [analysis/controls/falsification/audit_falsification.py](analysis/controls/falsification/audit_falsification.py); [analysis/controls/falsification/source_tables.json](analysis/controls/falsification/source_tables.json)

Compatibility under displayed-value intervals Numerical linkage is not recovery of the original execution path.

Coda all-36 implementation is supplied; this is not the omitted D1 HTML implementation. Parsed source tables are included, source PDFs are not.

## A06 — 5; Table 2

Fixed published-scale survival diagnostics

Supplied evidence: [support/astrometry/conditional_probabilities.csv](support/astrometry/conditional_probabilities.csv); [analysis/d1-core/independent_core_check.py](analysis/d1-core/independent_core_check.py)

Conditional candidate-only substitution Control scales held fixed; not revised publication probabilities.

Use recorded inputs and the isolated replay receipt; a supplied command is not itself proof of successful execution.

## A07 — 5.1; Table 3; Appendix C

15 A controls, 54 radii and four zero-location MLE scales

Supplied evidence: [support/astrometry/A_controls_transcribed.csv](support/astrometry/A_controls_transcribed.csv); [support/astrometry/control_estimator_replay.json](support/astrometry/control_estimator_replay.json); [analysis/controls/scripts/fit_recovered_A.py](analysis/controls/scripts/fit_recovered_A.py)

Coda figure recovery plus prior Lily verification; scales recalculated Rounded radial values lack signed/unrounded vectors and exact epochs.

Use recorded inputs and the isolated replay receipt; a supplied command is not itself proof of successful execution.

## A08 — 5.1

Exclusion of unrestricted unweighted uncensored iid free-location MLE on same bounded samples

Supplied evidence: [analysis/controls/source_archives/verify_free_location_rounding.py](analysis/controls/source_archives/verify_free_location_rounding.py)

Preserved exact-score proof and executed prior review Does not exclude different data, weighting or another estimator; original call unknown.

Use recorded inputs and the isolated replay receipt; a supplied command is not itself proof of successful execution.

## A09 — 6; Table 4

Uniform and strictly binary control-path bounds

Supplied evidence: [support/astrometry/conditional_bounds.json](support/astrometry/conditional_bounds.json); [support/astrometry/per_source_bounds.csv](support/astrometry/per_source_bounds.csv); [analysis/bounds/check_bounds.py](analysis/bounds/check_bounds.py)

Conditional reverse-triangle inequality Stipulated intervals; 3 sigma not guaranteed or simultaneous. Candidate central and rounded sensitivities separate. Componentwise bounds.

Use recorded inputs and the isolated replay receipt; a supplied command is not itself proof of successful execution.

## A10 — 7.1

Recorded SIMBAD/Gaia J2000 match and availability split

Supplied evidence: [support/astrometry/simbad_snapshot.csv](support/astrometry/simbad_snapshot.csv); [support/astrometry/gaia_snapshot.csv](support/astrometry/gaia_snapshot.csv); [analysis/d1-core/QUERY_PROVENANCE.md](analysis/d1-core/QUERY_PROVENANCE.md)

Dated source-query evidence and mechanism hypothesis Not present-day query or proof of historical source availability/code path.

Dated query snapshots; no current query and no historical-availability inference.

## A11 — 7.2; 8.1

Ren2024 inversion recovers J2000 state

Supplied evidence: [support/astrometry/ren2024_inversion.csv](support/astrometry/ren2024_inversion.csv); [analysis/d1-core/independent_core_check.py](analysis/d1-core/independent_core_check.py)

Printed signed-component inversion A J2000 state in 2024 is not proof of the identical 2026 extra-propagation implementation.

Use recorded inputs and the isolated replay receipt; a supplied command is not itself proof of successful execution.

## A12 — 7.2; 7.3

Table1 mixed listed epochs and F two-table discrepancy

Supplied evidence: [analysis/controls/falsification/source_tables.json](analysis/controls/falsification/source_tables.json); [analysis/controls/falsification/audit_falsification.py](analysis/controls/falsification/audit_falsification.py)

Separately scoped source-table comparisons F requires same-centroid assumption; G convention remains inferred.

Parsed source tables support the Table 1/F comparison. The supplied alternative-input audit tests Table 1 propagation models but does not implement the specific F Table 5/Table 7 centroid-separation versus component-norm check. That subclaim is retained source arithmetic, not a supplied executable replay.

## A13 — 9.2

Independent evidence for D/E and G is not overturned

Supplied evidence: No numerical payload claimed for this entry.

Bounded review attribution, not new follow-up analysis Does not certify every operation in those papers.

Primary literature in manuscript references [4] and [6]; not a new numerical replay.

## A14 — 10

Red, Coda, Lily, Nua and Andrei roles

Supplied evidence: No numerical payload claimed for this entry.

Attributed project provenance No backend authentication or model-vote validation.

Contributor history is supported by private provenance; publish bounded attribution prose, not private conversations. Grok and Gemini review roles are included in current Section 10.

## A15 — Version and evidence basis; 2; 10; 11; reference [2]

Unpublished preparation with a bounded 15 October 2026 source-status check; author-reply status unverified.

Supplied evidence: [status/CURRENT_SOURCE_STATUS.md](status/CURRENT_SOURCE_STATUS.md); [status/SOURCE_STATUS_RECORD.json](status/SOURCE_STATUS_RECORD.json)

Action/scope statement Dated older checks are not current nonresponse or publication evidence.

The dated source-status note and compact retrieval metadata are supplied in status/. No current author-reply status, complete absence-of-correction claim or journal-version comparison is made.

## R24-01 — 8.1; Table 6

Six non-TGSS component pairs recover a J2000 state, not proof of the 2026 transformation

Supplied evidence: [support/ren2024/math/printed_reference_inversion.json](support/ren2024/math/printed_reference_inversion.json); [analysis/ren2024/ren2024-assessment/math/audit_astrometry.py](analysis/ren2024/ren2024-assessment/math/audit_astrometry.py)

Accepted source-aware assessment Three stars, six rows; no historical software reconstruction.

Use recorded inputs and the isolated replay receipt; a supplied command is not itself proof of successful execution.

## R24-02 — 8.1; Table 6

Seven native/printed comparisons; source-linked proxy dates versus broader envelopes

Supplied evidence: [support/ren2024/EPOCH_UNCERTAINTY_TABLE.csv](support/ren2024/EPOCH_UNCERTAINTY_TABLE.csv); [support/ren2024/math/seven_rows.csv](support/ren2024/math/seven_rows.csv); [analysis/ren2024/ren2024-assessment/math/audit_astrometry.py](analysis/ren2024/ren2024-assessment/math/audit_astrometry.py)

Preserved outputs; display and table-consistency check Proxy epochs and ranges are not measured effective centroid times or confidence bounds.

Use recorded inputs and the isolated replay receipt; a supplied command is not itself proof of successful execution.

## R24-03 — 8.2; Table 7

A native radius 4.877315 to 3.294057, unresolved association under covariance/registration limitations

Supplied evidence: [support/ren2024/math/seven_rows.csv](support/ren2024/math/seven_rows.csv); [support/ren2024/math/reviewer_followup_finite_rho.csv](support/ren2024/math/reviewer_followup_finite_rho.csv); [analysis/ren2024/ren2024-assessment/math/audit_astrometry.py](analysis/ren2024/ren2024-assessment/math/audit_astrometry.py); [analysis/ren2024/ren2024-assessment/math/reviewer_followup.py](analysis/ren2024/ren2024-assessment/math/reviewer_followup.py)

Preserved numerical scenarios D is an assumed-covariance distance, not a calibrated significance or counterpart probability.

Use recorded inputs and the isolated replay receipt; a supplied command is not itself proof of successful execution.

## R24-04 — 8.2

B is positionally compatible, not established as stellar; 144 MHz fraction cannot directly classify 887.5 MHz source

Supplied evidence: [support/ren2024/math/seven_rows.csv](support/ren2024/math/seven_rows.csv)

Primary-source synthesis adopted from D6 No new stellar emission model or likelihood calculated.

The staged seven-row output supports the numerical B position. The separate emission-origin restriction comes from Callingham et al. (2021), DOI 10.1038/s41550-021-01483-0; preserve its frequency/population restriction.

## R24-05 — 8.2; 9.2

G larger offsets and stronger evidence survive; 2024 IR and 2025 follow-up separated

Supplied evidence: [support/ren2024/math/seven_rows.csv](support/ren2024/math/seven_rows.csv)

Primary-source synthesis adopted from D6 No image re-extraction, signed-convention resolution or naive multi-survey proper-motion fit.

The staged seven-row output supports the numerical G offsets. Separate image-based evidence comes from Suazo et al. (2024), DOI 10.1093/mnras/stae1186, and Ren et al. (2025), DOI 10.1093/mnrasl/slaf006. Original image extraction is not replayed.

## R24-06 — 8.3

Native TGSS declination retained; inconsistent shared reference; 0.691094 arcsec residual

Supplied evidence: [support/ren2024/math/tgss_reference_diagnostic.json](support/ren2024/math/tgss_reference_diagnostic.json); [support/ren2024/math/tgss_discrepancy.json](support/ren2024/math/tgss_discrepancy.json); [analysis/ren2024/ren2024-assessment/math/tgss_reference_diagnostic.py](analysis/ren2024/ren2024-assessment/math/tgss_reference_diagnostic.py)

Preserved executable result with documentary norm check Tested common-star model and J1990-J2030 interval only; no coordinate repair or historical cause asserted.

Use recorded inputs and the isolated replay receipt; a supplied command is not itself proof of successful execution.

## R24-07 — 8.4

1/(31*3600^2)=2.48904819e-9 arcsec^-2; printed density factor 3615.84

Supplied evidence: [check_document_arithmetic.py](check_document_arithmetic.py)

Independent documentary unit arithmetic from preserved source statement Does not establish a flux-matched density or infer the historical error mechanism.

Source values: Ren et al. (2024), DOI 10.3847/2515-5172/ad5017; Assef et al. (2015), DOI 10.1088/0004-637X/804/1/27. Unit arithmetic is not selection-matched population inference.

## R24-08 — 8.4

Hypothetical five-million 10-arcsec aperture expected overlap count 3.91

Supplied evidence: [check_document_arithmetic.py](check_document_arithmetic.py)

Illustrative dimensional arithmetic Not a selected-sample posterior, object classification or contamination exclusion.

Illustrative aperture arithmetic only; original private assembly receipt is not necessary to calculate it.

## R24-09 — 8.5; 9.4

Radio detection, distinctness, IR association and sufficient contaminating flux are separate evidentiary steps

Supplied evidence: No numerical payload claimed for this entry.

Accepted bounded interpretation No new image reduction or population inference; known barriers remain.

Interpretive separation in the manuscript, supported by cited primary sources and the supplied conditional numerical results; no new emitter classification.

## R24-10 — 10; 11

Coda original Astropy runs versus Lily separate implementation remain distinctly credited

Supplied evidence: No numerical payload claimed for this entry.

Historical execution scope from accepted records No full scientific pipeline rerun in this writing pass.

Historical execution roles are provenance claims, not newly replicated observational findings. Private review archives remain excluded.

## COV-01 — 3.1

Historical 72-case Astropy space-motion comparison; reported maximum difference 8.493 microarcseconds.

Supplied evidence: [analysis/controls/astropy72/astropy_crosscheck_public.py](analysis/controls/astropy72/astropy_crosscheck_public.py); [analysis/controls/astropy72/astropy_crosscheck.csv](analysis/controls/astropy72/astropy_crosscheck.csv); [analysis/controls/astropy72/REPLAY_COMPARISON.json](analysis/controls/astropy72/REPLAY_COMPARISON.json); [analysis/controls/astropy72/AST_PROOF.json](analysis/controls/astropy72/AST_PROOF.json); [analysis/controls/astropy72/DERIVATION_PROVENANCE.json](analysis/controls/astropy72/DERIVATION_PROVENANCE.json)

Historical Astropy comparison plus separately identified minimal derivative executed once on 15 October 2026. The derivative omits the original HTML-only hash dependency; no source extraction is repeated. This is distinct from the seven-row Ren 2024 audit, observer-parallax corrections, or measurement uncertainty.

One derivative run reproduced all 72 rows/36 pairs byte-for-byte and the scientific summary exactly. Maximum Astropy-versus-stdlib difference is 8.49259882240716 microarcseconds. The separate D1 I-shift failure remains failed. This map retains 25 historical rows plus one added coverage entry and is not exhaustive.
