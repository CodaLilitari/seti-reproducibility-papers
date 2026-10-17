# Central TESS claims and supplied evidence

This is a **nonexhaustive** navigation map for the central claims in the TESS methods manuscript. Paths are relative to this supplement. T1–T5 identify historical collections, not separate public deposits. Exact mapped file identities are in `CLAIM_TO_EVIDENCE.json`; the top-level manifest covers the full payload inventory.

## T1 — Sections 2/Table 1: original three-peak S4 result, b miss and SAP/PDC sign disagreement

- `source/planet_hunt_tess_development_2026-10-08/results/search_results.json`
- `source/planet_hunt_tess_development_2026-10-08/search.py`
- `source/planet_hunt_tess_development_2026-10-08/data/toi270_s4_binned.csv`
- `source/planet_hunt_tess_development_2026-10-08/results/implementation_tests.txt`

Historical known-system output; not blind validation or discovery.

## T2 — Section 3/Table 2: full-cadence S4/S5 established-library comparison

- `standard-bls/crosscheck-results.json`
- `standard-bls/configuration-before-run.json`
- `standard-bls/run_crosscheck.py`
- `standard-bls/data/toi270-s0004.fits`
- `standard-bls/data/toi270-s0005.fits`

Stored real-data development results; S5 is not a held-out validation.

## T2 — Section 3.1: five-peak and detrending probes; checksum and rounding diagnostics

- `development-replay/posthoc_diagnostics_results.json`
- `development-replay/posthoc_diagnostics.py`
- `development-replay/POSTHOC_DIAGNOSTICS.md`
- `provenance/NATIVE_SOURCE_IDENTITIES.json`

Explicit post-hoc diagnostics; no demonstrated upstream physical cause.

## T2 — Section 4: prototype counterexamples and exact original replay

- `development-replay/counterexamples_receipt.json`
- `development-replay/counterexamples.py`
- `development-replay/replay_receipt.json`
- `development-replay/replay.py`
- `development-replay/REPORT.md`

Synthetic counterexamples do not establish the real nuisance cause.

## T3 — Sections 4.2–5: signed recovery, metadata, grid, mask, timing and freeze rules

- `tess-development-v3_1/IMPLEMENTATION_SPEC.md`
- `tess-development-v3_1/METADATA_COMPLETENESS_SPEC.md`
- `tess-development-v3_1/tess_components.py`
- `tess-development-v3_1/metadata_contract.py`
- `tess-development-v3_1/synthetic_driver.py`

Current supplied implementation is v3.1. The intermediate v3 package and separate acquisition proposal are not supplied as complete archives; live adapters and cohort remain unactivated.

## T4 — Section 6/Table 3: diagnostic-only concentration and historical 47 tests

- `tess-development-v3_1/VERIFICATION_RECEIPT.json`
- `tess-development-v3_1/unittest.log`
- `tess-development-v3_1/test_tess_components.py`
- `tess-development-v3_1/test_metadata_contract.py`
- `tess-development-v3_1/synthetic_output/discovery_freeze.json`
- `tess-development-v3_1/synthetic_output/synthetic_driver_result.json`
- `provenance/V3_1_REPORTING_CHANGELOG.md`

Historical Oct8 performance figures and fixed synthetic behavior; no calibrated false-alarm rate.

## T4 — Sections 6.1/9: separate Oct15 same-code synthetic replay

- `replay/TESS_REPLAY_STATUS.md`
- `replay/TESS_REPLAY_COMPARISON.json`
- `tess-development-v3_1/run_offline_checks.py`

One existing 47-test command; not 94 independent tests, a new observation, or an independent implementation.

## T5 — Sections 6.1/9: scope and attribution of Lily partial review

- `provenance/T5_REVIEW_SCOPE.json`

Source-hashed report summary only. Original reviewer answers and scripts are excluded; no complete independent Astropy replay is claimed.

## Limits of the mapping

The complete original T1–T5 transport collections, private reviewer answers and reviewer scripts are not reproduced wholesale. T5 is a narrowly derived scope record, not delivery of an independent runnable reviewer environment. The map is not an exhaustive claim audit. The optional cohort design and stopped Kepler branch are not activated or newly reproduced. See `provenance/INPUT_IDENTITIES_AND_CURATION.json` for the original 56-file curation and `CURATION_PROVENANCE.json` for this successor. The release package retains these evidence limits. Per-source rights are stated in `provenance/SOURCE_ATTRIBUTION_AND_TERMS.md`; no blanket license is assigned.
