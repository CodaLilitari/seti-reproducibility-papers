# Source notices and acknowledgments

17 October 2026. This notice applies to the coordinate-epoch numerical supplement release candidate v1.0. It distinguishes the small factual source extracts, project calculations and code, source documentation, and historical curation records. It assigns no blanket license to this mixed package. Public access does not relicense upstream content. The author has authorized eventual release; choosing no blanket project license is not a further approval requirement.

## Gaia DR3 numerical extracts

The Gaia CSVs under `analysis/`, `support/astrometry/`, and `analysis/ren2024/ren2024-assessment/gaia/` retain the recorded DR3 source identifiers, reference epochs and query provenance. The official [DR3 credit instructions](https://gea.esac.esa.int/archive/documentation/GDR3//Miscellaneous/sec_credit_and_citation_instructions/) permit free use of Gaia data with ESA/Gaia/DPAC credit. This condition is recorded for the numerical extracts, not extended to unrelated documentation or images.

Acknowledgment, adapted from that guidance: this work uses ESA Gaia data processed by the Gaia Data Processing and Analysis Consortium (DPAC). DPAC receives funding from national institutions participating in the Gaia Multilateral Agreement. These are mission and consortium credits, not a declaration that the manuscript's author received funding.

Cite the Gaia mission paper and the DR3 summary through the official credit page. The inspected release reference is Gaia Collaboration et al. (2023), *Gaia Data Release 3: Summary of the content and survey properties*, A&A 674, A1, [DOI 10.1051/0004-6361/202243940](https://doi.org/10.1051/0004-6361/202243940). Source columns are reproduced as recorded; project-selected fields and derived quantities remain identified by their files and provenance.

## CDS/VizieR catalog extracts and external documentation

The seven native TSV responses retain their original creator, publication, catalog, request and rights headers. [VizieR's usage policy](https://cds.unistra.fr/vizier-org/licences_vizier.html) permits scientific use with explicit original author, publication and publisher citation; commercial conditions depend on the original source. Catalog-specific notices or the relevant journal policy remain applicable. The policy does not establish a blanket grant to redistribute the CDS information system or its metadata.

We acknowledge the VizieR catalogue access tool at CDS, Strasbourg, [DOI 10.26093/cds/vizier](https://doi.org/10.26093/cds/vizier). The native records and the primary source references below identify the exact products; this package does not claim a fresh query or substitute newer corrected positions.

| Retained source product | Primary attribution and publisher |
|---|---|
| RACS DR1 `J/other/PASA/38.58/galcut` | Hale et al. (2021), PASA 38, e058, Cambridge University Press, [10.1017/pasa.2021.47](https://doi.org/10.1017/pasa.2021.47). |
| Original VLASS Epoch-1 Quick Look `J/ApJS/255/30/comp` | Gordon et al. (2021), ApJS 255, 30, American Astronomical Society / IOP Publishing, [10.3847/1538-4365/ac05c0](https://doi.org/10.3847/1538-4365/ac05c0). |
| FIRST `VIII/92/first14`, 2014Dec17 | Helfand, White and Becker (2015), ApJ 801, 26, American Astronomical Society / IOP Publishing, [10.1088/0004-637X/801/1/26](https://doi.org/10.1088/0004-637X/801/1/26). |
| NVSS `VIII/65/nvss` | Condon et al. (1998), AJ 115, 1693, American Astronomical Society, [10.1086/300337](https://doi.org/10.1086/300337). |
| TGSS ADR1 `J/A+A/598/A78/table3` | Intema et al. (2017), A&A 598, A78, EDP Sciences, [10.1051/0004-6361/201628536](https://doi.org/10.1051/0004-6361/201628536). |

The four complete VLASS/FIRST/NVSS/TGSS CDS ReadMes are externally referenced rather than bundled. `analysis/ren2024/ren2024-assessment/g-surveys/DOCUMENTATION_REFERENCES.json` supplies their canonical URLs, historical hashes and explicit omitted status. The hashes describe the previously inspected copies and are not claims about the current remote bytes. `G_SOURCE_PROVENANCE.json` and the epoch/uncertainty table retain the factual source conventions and historical references byte-for-byte. Their historical file names do not define the current payload inventory; `MANIFEST_SHA256.json` does.

Ordinary numerical facts and this small attributed scientific selection are not characterized here as necessarily requiring separate permission. Complete documentation works have been treated separately from numerical rows. No catalog, document or image was newly acquired for v3.

## RACS DR1 header extracts delivered by CADC

The three `analysis/ren2024/ren2024-assessment/racs/header_*.txt` files are header-only extracts of `RACS-DR1_0354-43A.fits`, `RACS-DR1_1240-25A.fits` and `RACS-DR1_2347+00A.fits`, obtained through CADC. Their paired curated receipts retain the public requested URLs, retrieval dates, status, size and body hashes. No FITS image pixels are supplied. Header bodies are unchanged; receipt reduction is separately documented in `DERIVATIVES.md`.

The official [CADC RACS DR1 page](https://www2.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/en/racs/) identifies these convolved/mosaicked ASKAP products as CASDA data made available under [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/). Retain those product and source credits for these extracts; this notice does not extend that license to unrelated files. Extraction to header-only text and curated transport metadata are the relevant package transformations.

Credit the RACS survey and catalog: McConnell, D., Hale, C., Lenc, E., Banfield, J., et al. (2020), *The Rapid ASKAP Continuum Survey I: Design and first results*, PASA 37, e048, [10.1017/pasa.2020.41](https://doi.org/10.1017/pasa.2020.41), and Hale et al. (2021), [10.1017/pasa.2021.47](https://doi.org/10.1017/pasa.2021.47).

Facility acknowledgment, adapted from the CADC guidance: ASKAP belongs to the Australia Telescope National Facility managed by CSIRO. Its operation receives Australian Government support through the National Collaborative Research Infrastructure Strategy. ASKAP uses Pawsey Supercomputing Centre resources; establishment support came from the Australian Government, the Government of Western Australia and the Science and Industry Endowment Fund. We acknowledge the Wajarri Yamatji as Traditional Owners of the Murchison Radio-astronomy Observatory site. These RACS products are credited to CASDA and were delivered here through CADC; a direct CASDA retrieval is not claimed.

## SIMBAD extracts

`analysis/d1-core/fresh_simbad_tap_2026-09-27.csv` and `support/astrometry/simbad_snapshot.csv` contain the retained SIMBAD factual selections and locally assembled query/status fields. `analysis/d1-core/QUERY_PROVENANCE.md` identifies their query history. The [SIMBAD service](https://simbad.cds.unistra.fr/simbad/) identifies its database under the [Open Database License](https://opendatacommons.org/licenses/odbl/1-0/). Preserve that notice and the source citations. The database's license is not extended to the rest of the supplement.

We acknowledge SIMBAD, operated by CDS in Strasbourg, and cite Wenger et al. (2000), [10.1051/aas:2000332](https://doi.org/10.1051/aas:2000332). Any original-paper references applicable to individual database facts remain relevant.

## Published values, transcriptions and project outputs

The selected 2026 primary values and displayed control radii are project transcriptions from Ren, T., et al. (2026), *Archival Diagnostics for Potential Background Contaminants of Project Hephaistos Dyson Sphere Candidates*, [arXiv:2607.03619v6](https://arxiv.org/abs/2607.03619v6). Preserve that exact audited version, the recorded locators and the transformation labels. The arXiv non-exclusive distribution grant is not represented as a downstream blanket license. No source PDF, full article HTML or original figure pixels are included.

The 2024 Table 1 values are transcribed from Ren, T., Garrett, M. A., and Siemion, A. P. V. (2024), *Background Contamination of the Project Hephaistos Dyson Spheres Candidates*, [arXiv:2405.14921v1](https://arxiv.org/abs/2405.14921v1), Research Notes of the AAS 8, 145, [10.3847/2515-5172/ad5017](https://doi.org/10.3847/2515-5172/ad5017). The inspected arXiv version identifies [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Table transcription, selected columns and machine-readable formatting are changes; subsequent calculations are project outputs. No endorsement is implied, and that notice does not license the independent radio catalogs.

Other retained literature scalars, including the JWST caption comparison, keep their recorded source distinctions. The project PNGs are analysis plots, not source-paper figures or survey images; their generation code was not recovered. Project code, plots, calculations and curated provenance are supplied without assigning a new project license. Dependencies are named but not distributed. Authorship and computational contribution records are separate from licensing, and all upstream rights notices remain applicable.

## Scope of the v3 transformation

Only the four complete ReadMes are omitted. Two source edits are limited to an unused documentation read and its dependent expected-hash constant. `derivations/readme-omission/` records the exact diff and narrow static proof. Scientific inputs, numerical outputs, figures and historical replay evidence remain byte-identical to v2. This preservation statement concerns delivered bytes. The later two-command runtime record in `status/README_OMISSION_RUNTIME.json` separately documents 174/122 passed assertions, eight byte-identical numerical files and seven exact scientific fields for these derivatives, including the controller reference-path recovery.
