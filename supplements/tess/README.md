# TESS failure-preserving development evidence: release supplement v1.0

Prepared by Coda while collaborating with Andrei and Lilitari, 17 October 2026, for **Preserving failures in a bounded TESS transit-search workflow**, preprint v1.0. The responsible human author is Richard Andrei Pemberton, Independent researcher. This is the prepared public evidence package. Its designated release location is https://richard-pemberton-research.darkahn.chatgpt.site/papers/tess-transit-search-methods-supplement-v1.0.zip. The URL identifies the intended distribution location; this curation receipt alone does not establish live availability. Source-specific rights and credits are described in `provenance/SOURCE_ATTRIBUTION_AND_TERMS.md`; no blanket license is assigned to the mixed contents.

## What this evidence supports

The source-aware TOI-270 / TIC 259377017 development record preserves approximate c/d recovery, the original miss of b within three Sector 4 peaks, and the third peak's opposite SAP/PDC signs. Later full-cadence and post-hoc comparisons and synthetic counterexamples remain separate. The final offline v3.1 components have a historical 47-test execution record using actual Astropy; Lily's independent extracted checks had narrower scope and are not a second full-suite run. These materials establish neither a new planet nor calibrated false-alarm probabilities, completeness or physical validation.

The 15 October v2 curation performed file/hash, existing-record comparison and narrow derivative checks only; it ran no science. The separate 15 October same-code synthetic replay is now carried in `replay/TESS_REPLAY_STATUS.md` and `replay/TESS_REPLAY_COMPARISON.json`: one existing 47-test command passed, and both synthetic JSONs matched the retained references byte-for-byte. Historical 8 October timing/memory measurements remain distinct from that replay. This is not a new observation, independent implementation or false-alarm calibration.

`CLAIM_TO_EVIDENCE.md` and `.json` provide a nonexhaustive T1–T5 central-claim map to actual supplied files and explicit omissions. `CURATION_PROVENANCE.json` records this v1.0 public-copy successor. The v3 manifest and replaced notices are preserved under `provenance/historical/supplement-v3/`. The v2 manifest, curation ledger and replaced notices are preserved byte for byte under `provenance/historical/supplement-v2/`; their dated preparation statements describe that earlier state. Every v2 scientific input, source file, numerical result and execution record is retained byte for byte. The prior 49-exact/seven-derivative counts below describe the first curation, not an additional claim that every v2 file is an exact original copy.

## Contents and provenance

| Directory | Contents and evidence state |
|---|---|
| `source/planet_hunt_tess_development_2026-10-08/` | All 19 original prototype manifest payloads and their manifest: code, original lossy data, delivered outputs, six-test record, historical pre-flux plan and handoff. Byte-identical. |
| `development-replay/` | Coda's historical original replay, explicit synthetic counterexamples and later post-hoc diagnostics, with scripts, outputs and reports. The replay receipt has only its private interpreter path removed. |
| `standard-bls/` | Historical established-library comparison and the two exact native Sector 4/5 FITS inputs. Configuration/results and retrieval receipts have only documented path/transport-field edits. |
| `tess-development-v3_1/` | Six frozen Python source/test/runner files, specifications, recorded 47-test log and synthetic outputs. README path assignments and the execution receipt's interpreter path are the only derivatives here. |
| `provenance/` | Original-to-candidate identities, native source identifiers, exact Astropy license notice, source attribution/terms and unchanged historical manifests/changelog. |

`provenance/INPUT_IDENTITIES_AND_CURATION.json` records 56 source files: **49 exact copies and seven curated derivatives**, each with original and staged SHA-256 and exact transformations. New curation documents and the integrity checker are covered by the top-level `MANIFEST_SHA256.json`. That manifest excludes only itself; its own identity must be carried in the external handoff. Historical manifests identify original artifacts and are not current checksums for the privacy-edited derivatives.

Original documents are preserved as historical records. For example, the prototype README correctly says its original package did not retain native FITS; this later candidate supplies those separately recovered exact bytes under `standard-bls/data/`. References to a replay `package_copy` describe a generated working directory, which is deliberately absent here. Internal T1–T5 manuscript IDs remain provenance labels, not public repository identifiers.

## Integrity and reproduction

For a package-integrity check, run the standard-library `verify_manifest.py` for a read-only integrity check. It imports no science code, accesses no network and writes nothing. See `REPRODUCIBILITY.md` for commands, exact historical environments, dependencies, write locations and comparison limits. Numerical commands must run in a separate disposable copy, serially; never in this preserved release package. The runner regenerates evidence files, and importing some historical runners changes thread/priority/network settings.

The v3.1 synthetic check needs only its six sibling Python files and the recorded NumPy/SciPy/Astropy dependencies; it uses no real target data. Full-cadence comparison uses the bundled FITS and original prototype code. Historical Wolfram `retrieval.wl` performs network acquisition and is retained only as source provenance, not as an offline command. No new catalog, target selection or download is required for the bundled calculations.

The original figure is retained byte-for-byte but has no supplied generation command. Numeric replay is not figure regeneration. Source identity, successful execution, numerical agreement, visual QA, scientific interpretation, rights clearance and publication approval are separate claims.

## Attribution and scope

Lilitari supplied the prototype and preserved its failed recovery; Coda reproduced/challenged it and implemented the later offline components while collaborating with Andrei. The manuscript separately describes conceptual reviewers and their limited scopes. This package excludes private AI answers, account/session records and transport ZIPs. The historic post-hoc JSON contains a short Astropy implementation excerpt; its exact license notice is retained rather than treating that source as project-authored text.

TESS/MAST/SPOC products, the TOI-270 discovery and the NASA Exoplanet Archive comparison retain distinct attribution. Read `provenance/SOURCE_ATTRIBUTION_AND_TERMS.md`. No blanket project license or downstream permission is asserted for mixed upstream material. Proposed unfamiliar-host metadata selection and holdout design remain unactivated. Public distribution of this preserved record does not activate that scientific continuation.

The v1.0 release curation changes documentary notices and inventory only. It performs no scientific execution and adds no claimed reviewer experiment. Historical contribution and partial-check scopes are retained. Lilitari completed the focused v0.4 manuscript/supplement review, including nine TESS pages, and Red completed a separate text-only v0.4 review on 17 October 2026. Neither review executed a scientific program or reviewed the subsequently assembled v1.0 release. Coda separately checked the supported textual clarifications against the frozen sources; the manuscript records the contribution scopes. Older files are evidence of their recorded dates, not current publication instructions.
