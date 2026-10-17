# SETI reproducibility papers and supporting evidence

**Richard Andrei Pemberton** · Independent researcher · andreipemberton@gmail.com  
Preprints v1.0, dated 17 October 2026.

This collection accompanies two separate methods preprints. It contains their Markdown, Word and PDF editions, the exact versioned supplement ZIPs, and the same supplement contents expanded for browsing. The local export was prepared on 17 October 2026. The [GitLab repository](https://gitlab.com/codalilitari/seti-reproducibility-papers) supplies the versioned files linked below. Versioned portfolio URLs in the preserved papers and supplements identify their designated release destinations; availability of an external destination is separate from the integrity of this collection. Repository publication does not establish archive acceptance, DOI assignment or peer review.

## Papers and evidence

| Paper | Manuscript formats | Supporting evidence |
|---|---|---|
| **Coordinate-epoch provenance in archival technosignature vetting** — A reproducible sixteen-year inconsistency in the stellar separations reported by Ren et al. (2026) | [PDF](papers/coordinate/Coordinate_Epoch_Provenance_Preprint_v1.0.pdf) · [Markdown](papers/coordinate/Coordinate_Epoch_Provenance_Preprint_v1.0.md) · [Word](papers/coordinate/Coordinate_Epoch_Provenance_Preprint_v1.0.docx) | [Versioned ZIP](downloads/coordinate-epoch-provenance-supplement-v1.0.zip) · [Browse supplement](supplements/coordinate/README.md) · [Claim map](supplements/coordinate/CLAIM_TO_EVIDENCE.md) |
| **Preserving failures in a bounded TESS transit-search workflow** — TOI-270 development, signed-event recovery, and the limits of an unactivated holdout design | [PDF](papers/tess/TESS_Transit_Search_Methods_Preprint_v1.0.pdf) · [Markdown](papers/tess/TESS_Transit_Search_Methods_Preprint_v1.0.md) · [Word](papers/tess/TESS_Transit_Search_Methods_Preprint_v1.0.docx) | [Versioned ZIP](downloads/tess-transit-search-methods-supplement-v1.0.zip) · [Browse supplement](supplements/tess/README.md) · [Claim map](supplements/tess/CLAIM_TO_EVIDENCE.md) |

The coordinate study concerns a coordinate-epoch inconsistency and its conditional statistical consequences. It does not identify an extraterrestrial source, establish a unique historical software mistake, or provide a complete infrared contamination model. The historical eight-command replay retains **one candidate-I fitted-shift discrepancy in two comparison records: 20 of 22 comparisons passed**. A separate Astropy72 derivative has its own successful record. The later two-command ReadMe-omission replay passed 174 and 122 assertions, with eight numerical files byte-identical and seven selected scientific JSON fields exactly matching. Its initial controller reference-path error and continuation are preserved in the [sanitized runtime record](supplements/coordinate/status/README_OMISSION_RUNTIME.json). That later check did not rerun optimized epochs or resolve the candidate-I exception.

The TESS study preserves known-system TOI-270 development, including the original miss of planet b within three peaks and the third peak's opposite SAP/PDC signs. The v3.1 offline components have a historical 47-test record; the separately documented same-code synthetic replay passed its existing 47-test command and matched two synthetic JSON outputs byte-for-byte. These checks are not an independent implementation, a new observation, calibrated false-alarm rates or a completeness estimate. The proposed unfamiliar-host selection and holdout design remain unactivated.

## Integrity and reproduction

[MANIFEST_SHA256.json](MANIFEST_SHA256.json) identifies every file in this export except itself, with byte lengths and SHA-256 hashes. Each expanded supplement retains its own exact manifest; the files in its corresponding ZIP are byte-identical. The coordinate Markdown's two figure assets are also supplied beside that manuscript.

Read each supplement's instructions before running anything: [coordinate](supplements/coordinate/README.md), [TESS reproducibility](supplements/tess/REPRODUCIBILITY.md). The documented integrity checkers can inspect stored files without running the analyses. Scientific programs write outputs and must run in a separate working copy. Reproduction coverage and historical exceptions remain as stated in the individual records. Preparing this export performed documentary checks only and executed no scientific program.

## Citation, contributions and rights

Please cite the relevant individual preprint, by Richard Andrei Pemberton, using its exact title above, version 1.0 and date 17 October 2026. [CITATION.cff](CITATION.cff) describes the accompanying reproducibility collection; it does not assign a DOI or replace the individual paper citations.

[CONTRIBUTIONS.md](CONTRIBUTIONS.md) summarizes the public manuscript credits. AI assistance is disclosed by role and verification scope, separately from the responsible human author. Provider endorsement and authenticated backend identity are not claimed.

This is a mixed-source collection. **No blanket license is assigned.** Consult the [coordinate source notices](supplements/coordinate/SOURCE_NOTICES_AND_ACKNOWLEDGMENTS.md), the [TESS attribution and terms](supplements/tess/provenance/SOURCE_ATTRIBUTION_AND_TERMS.md), and the retained [Astropy license notice](supplements/tess/provenance/licenses/ASTROPY_LICENSE.rst). Those source-specific notices retain their stated scope. Scientific facts, project-authored material, code excerpts and upstream datasets should not be treated as having one undifferentiated rights status.

Frozen supplement notices and historical receipts retain their recorded preparation dates. Current repository publication status is stated above; scientific execution status and its qualifications remain in the identified later execution records. Private review conversations, account/session records, transport archives and editorial working files are excluded.
