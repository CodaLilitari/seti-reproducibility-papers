# Coordinate-epoch numerical supplement — release candidate v1.0

**Release candidate prepared, 17 October 2026; public availability is not yet verified.** This isolated final package preserves frozen v3 scientific source and data bytes and adds a curated record of the subsequent two-command runtime check. Source-family notices are in `SOURCE_NOTICES_AND_ACKNOWLEDGMENTS.md`; no blanket license is assigned to mixed upstream and project material. Bounded reproducibility does not establish a complete scientific pipeline or physical validation.

Intended versioned release locations: [supplement ZIP](https://richard-pemberton-research.darkahn.chatgpt.site/papers/coordinate-epoch-provenance-supplement-v1.0.zip) and [paper PDF](https://richard-pemberton-research.darkahn.chatgpt.site/papers/coordinate-epoch-provenance-v1.0.pdf). These are destination bindings, not a claim that upload, live verification or PhilArchive acceptance has occurred.

The package contains stored numerical tables, figures, exact source snapshots and bounded analysis code. `MANIFEST_SHA256.json` is the complete current payload inventory. `CURATION_PROVENANCE.json` records exact v3 ancestry and this release assembly. Earlier lineage is preserved under `history/`. `derivations/readme-omission/` preserves the exact two provenance-only source changes and their original static proof. `status/README_OMISSION_RUNTIME.json` adds the later successful execution of those exact derivatives once each, with the reference-path recovery history. Original project-relative ancestry labels identify private retained sources; they are not public deposit links. `CLAIM_TO_EVIDENCE.csv` and `.md` supply non-exhaustive public-relative locators. The frozen earlier packages, including v3, and canonical sources remain unchanged.

The proposed paper concerns a coordinate-epoch inconsistency and conditional consequences. Nothing here proves an extraterrestrial source, a unique historical software mistake, calibrated association probabilities, or a complete infrared contamination model.

## What can be checked immediately

Using Python 3.10 or later from this directory:

```sh
python verify_bundle.py
python check_document_arithmetic.py
```

These are **documentary checks**: delivered hashes, stored-table counts, selected arithmetic and cross-table consistency. They do not execute the astrometric analyses. The arithmetic checker has two inherited limits: its finite-correlation comparison does not assert the selected row count, and its seven-row comparison checks shared columns. The local curation validation separately checks the actual fixture's expected three finite-correlation rows and complete seven-row schema. Those additions do not alter the frozen checker.

`CURATION_VALIDATION.json` and `DOCUMENTARY_CHECK_OUTPUT.json` are preserved records from the original v1 curation, not fresh validation of this successor inventory. The current manifest is checked by `verify_bundle.py`; historical execution and comparison evidence is in the separately identified status records. The later two-command execution is recorded separately in `status/README_OMISSION_RUNTIME.json`.

## Scientific code and recorded replay coverage

Run these only in a **separate working copy**. The original programs write numerical outputs beside their inputs. Several also record the execution machine's interpreter and file paths in generated receipts; those future receipts require curation before redistribution. The existing eight-command replay and its qualified I exception are recorded in `status/REPLAY_COMPARISONS.json`; the prose scope is `status/COORDINATE_REPLAY_STATUS.md`. The minimal Astropy derivative executed on 15 October is recorded separately. The exact v3 seven-row audit and finite-correlation follow-up were subsequently executed once each on 17 October: 174 and 122 assertions passed; eight numerical files were byte-identical and seven selected scientific JSON fields exactly matched. The controller first stopped on a wrong reference path after successful audit execution; corrected reference locations allowed comparisons and the single follow-up run, without repeating the audit or relaxing criteria. Supplying a command is not a claim that all its outputs matched reference criteria.

| Scope | Command from the supplement root | Inputs and limits |
|---|---|---|
| Exact September 27 D1 core: 43 WISE/radio rows, effective epochs, 2024 inversion, five fixed-scale substitutions | `python analysis/d1-core/independent_core_check.py` | Python standard library. Three frozen primary/catalog input files and historical expected outputs are supplied. |
| Coda's independent 36-row WISE/printed-statistics audit | `python analysis/controls/falsification/audit_falsification.py` | Python standard library. Pinned Gaia snapshot and retained parsed primary tables. Source HTML extraction is not repeated. |
| A-control fixed/free-location estimator comparison | `python analysis/controls/scripts/fit_recovered_A.py` | NumPy/SciPy. Uses the displayed control radii; this does not recover authors' historical fit call. |
| Free-location rounding exclusion for the displayed controls | `python analysis/controls/source_archives/verify_free_location_rounding.py` | Python standard library; exact rational interval calculation. |
| Conditional uniform/binary control-path bounds | `python analysis/bounds/check_bounds.py` | Python standard library. Four hash-pinned input CSVs supplied. Bounds remain conditional, not reconstructed signed control vectors. |
| Seven original 2024 radio rows, epoch scenarios and covariance sensitivity | `python analysis/ren2024/ren2024-assessment/math/audit_astrometry.py` | NumPy/Astropy. Native catalog rows, reference data and source qualifications supplied. Four complete ReadMes are external links; the unused documentation read is omitted in v3. |
| TGSS single-stellar-epoch diagnostic | `python analysis/ren2024/ren2024-assessment/math/tgss_reference_diagnostic.py` | Astropy; central linear-motion diagnostic, not a probability or historical-cause inference. |
| Historical 72-case arithmetic comparison, minimal public derivative | `python analysis/controls/astropy72/astropy_crosscheck_public.py` | Astropy 8.0.1 and NumPy 2.5.3. Three hash-pinned numerical inputs; no full HTML dependency. Exact diff, AST proof and one successful execution record supplied. |
| Finite radio correlations, fixed-bias scenarios and source/header checks | `python analysis/ren2024/ren2024-assessment/math/reviewer_followup.py` | NumPy/Astropy. Public derivative described in `DERIVATIVES.md`; its expected source hash is updated to the v3 audit. The exact v3 variant passed 122 assertions in the separately recorded 17 October run. Run the seven-row audit first, or use the supplied frozen numerical comparators. |

`requirements-analysis.txt` records direct numerical package versions observed in the historical analysis. No environment was installed or resolved for this stage. Python standard-library checks require no numerical package installation. Use a separate environment and working copy for any future replay. The supplied records describe actual prior executions and their limitations, not a guarantee of success in every environment.

## Deliberate coverage limits

- The exact D1 core script and three input files were recovered from the September 27 archive after verifying its recorded SHA-256. The separate D1 pandas/HTML script for all 36 Table 10 rows depends on an absolute path to a source HTML file. It is omitted. The independent Coda 36-row calculation supplies a different implementation; do not call it a replay of that omitted D1 script.
- The source-table extraction HTML, original source PDFs, source screenshots and image reductions are not bundled. The parsed tables/transcriptions and exact source locators/hashes are retained. Checking the transcriptions against those originals remains a separate source-inspection step, subject to source access and reuse terms.
- Figure PNGs are supplied byte-identically. The original figure-generation code is not in the recovered writing bundle, so figure regeneration is not covered.
- The seven-row numerical programs use original catalog snapshots and preserved epoch/provenance facts. The complete acquisition histories, all remote product bodies and survey HTML documentation are not bundled. This stage does not reverify remote survey information, query archives, or reconstruct source-specific exposure weights.
- Lily's independent October 11 closure checker and private review archive are omitted. Its prior numerical checking is a recorded contribution, not a newly executed check of this stage.
- The JWST caption-value table is documentary support; no JWST reanalysis or source extraction is supplied. No corrected control significances, new targets, TESS measurements, registration calibration, physical emitter classification or IR flux decomposition are performed here.
- Known unknowns remain unknown: source-specific centroid epochs/weights, missing radio covariance, frame registration, historical input/table-generation paths and IR contribution. Missing covariance is not zero covariance. The finite-correlation distances are conditional diagnostics, not calibrated p-values; minimizing them does not support co-location.

The supplied numerical sources are sufficient to attempt the listed bounded computations using the recorded snapshots. Full scientific reproducibility of the entire manuscript has **not** been demonstrated. Twenty of twenty-two reference-comparison records in the historical eight-command run passed; the two failures represent one candidate-I fitted shift, retained without tolerance relaxation. The Astropy derivative passes its separate narrower criteria. The later two-command ReadMe-omission replay passes its predeclared eight-file and seven-field comparisons; it did not rerun the optimized-epoch calculation or resolve the candidate-I exception.

## Provenance, contributions and release

Lilitari supplied source-aware independent reconstruction and numerical checks; Coda supplied source recovery, executable checks, conditional extensions and integration; Red first identified the effective-epoch pattern and supplied critical review. Nua supplied the effective-epoch algebra explanation and caution about the unresolved Table 1 input path. Narrow contributions from Grok's signed-vector critique and Gemini's claim-level review should be credited only where retained in the final manuscript. Computational and conceptual roles are distinct. Nua's review was not a separate catalog query or numerical replay, and Nua's contribution does not supersede Red's first identification.

This is a concise contribution description, not a final publication byline or independent validation by those systems. Private chats, screenshots, account/session records, reviewer answers and operational acknowledgments are not required to run the supplied science code and are not included.

The author has requested publication to PhilArchive, GitLab and his portfolio once preparation and review are finished. The final package is prepared for those destinations; live uploads and any persistent identifiers must be verified separately. Source-family treatment and acknowledgments are supplied without a blanket license. Manuscript review/contributor and human declaration records are separate from computational validation. `RELEASE_STATUS.md` states the current status. No DOI or public repository is claimed.

Dated source-status evidence is included in `status/CURRENT_SOURCE_STATUS.md` and `status/SOURCE_STATUS_RECORD.json`. The note establishes only the bounded observed status, not complete absence of corrections or an author response. This successor adds no new archive query, source observation, TESS/Kepler stage, figure regeneration or image reduction.
