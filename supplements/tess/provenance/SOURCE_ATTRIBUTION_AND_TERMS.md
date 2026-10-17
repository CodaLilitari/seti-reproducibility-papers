# Source attribution and per-source rights

Release supplement v1.0, 17 October 2026. This notice describes the prepared public package and supersedes the release-planning statements in the preserved v2/v3 notices. Source hashes establish byte identity. No blanket license is assigned to the mixed contents, and public distribution does not imply provider endorsement.

## Project material and contribution history

Andrei directed the work. Lilitari supplied the original source-aware TOI-270 benchmark and preserved its failed recovery; Coda reproduced and challenged it, implemented the later offline components, and curated the evidence with Andrei. The manuscript gives the separate conceptual-review and partial-check scopes. On 17 October 2026, Lilitari completed the focused v0.4 manuscript/supplement review and Red completed a separate text-only v0.4 review. Their detailed contributions and limits are stated in the manuscript. Neither consultation executed a scientific program or inspected the subsequently assembled v1.0 release. These reviews are not additional numerical replications.

Original project code, reports, plots and calculated outputs retain their recorded provenance. No project-wide LICENSE or SPDX grant is assigned here. The original figure is retained without a supplied generation command; numerical replay is not figure regeneration. The manuscript and package do not transfer rights in upstream material under a project license.

## TESS, SPOC and MAST

The two retained native files are the public mission-produced SPOC two-minute light curves for TIC 259377017 in Sectors 4 and 5, DATA_REL=42. Their canonical source URLs, original product names, byte counts and hashes are in `NATIVE_SOURCE_IDENTITIES.json`. The lossy development export is separately identified. They are not target-pixel or centroid-validation products.

The current [MAST Data Use policy](https://archive.stsci.edu/publishing/data-use) describes most hosted data as public-domain and unrestricted while distinguishing exclusive-access, licensed community products and copyrighted collections. The recorded inputs are public mission-produced SPOC products. This classification supports their public reuse under that policy; it is not a blanket grant over all MAST holdings, documentation or unrelated third-party content. Native FITS headers and bytes, including the original missing DATASUM cards and associated historical warnings, remain unchanged.

We used TESS mission data supplied through MAST at the Space Telescope Science Institute. NASA's Explorer Program funds US institutions participating in TESS. The Association of Universities for Research in Astronomy operates STScI under NASA contract NAS5–26555. This is adapted from the [MAST TESS acknowledgment guidance](https://archive.stsci.edu/publishing/mission-acknowledgements). These mission and facility funding credits do not state that Richard Andrei Pemberton received those funds.

Retain Ricker et al. (2015), doi:10.1117/1.JATIS.1.1.014003; Jenkins et al. (2016), doi:10.1117/12.2233418; the recorded data-product specification; and DR42 release-note attribution in the manuscript. [MAST data attribution guidance](https://archive.stsci.edu/publishing/data-attributions) requests a dataset DOI. No DOI for these exact two products is claimed; their preserved product locators and SHA-256 identities remain the provenance supplied here.

## NASA Exoplanet Archive and original discovery

The saved known-planet comparison used the NASA Exoplanet Archive after the original search. We acknowledge that service, which the California Institute of Technology operates through NASA's Exoplanet Exploration Program. See the [official acknowledgment guidance](https://exoplanetarchive.ipac.caltech.edu/docs/acknowledge.html). This adapted credit and the reference below describe historical service use, not a new query or current ephemeris determination. The original TOI-270 discovery remains attributed to Günther et al. (2019), doi:10.1038/s41550-019-0845-5.

Christiansen, J. L., McElroy, D. L., Harbut, M., et al. (2025). *The NASA Exoplanet Archive and Exoplanet Follow-up Observing Program: Data, Tools, and Usage*. The Planetary Science Journal, 6, 186. https://doi.org/10.3847/PSJ/ade3c2. This current archive overview is requested by the archive's citation guidance; it does not establish validation of this workflow.

## Astropy excerpt and dependencies

The historical `development-replay/posthoc_diagnostics_results.json` contains an identified Astropy 8.0.1 `verify_checksum` source excerpt. The exact applicable copyright, redistribution conditions and disclaimer are retained in `licenses/ASTROPY_LICENSE.rst`. That notice applies to the excerpt, not the complete supplement. Preserve it with any redistribution of that excerpt. Dependency distributions are otherwise not bundled. NumPy, SciPy and Astropy identities and citations are retained; requirements files do not assign their licenses to project material.

## History, privacy and evidence limits

The original 56-file curation and its seven documentary derivatives remain recorded in `INPUT_IDENTITIES_AND_CURATION.json`. V2 records and notices are preserved under `historical/supplement-v2/`; old pending-release statements there describe their historical state. V3 notices and its manifest are separately preserved under `historical/supplement-v3/`. The top-level manifest covers this v1.0 inventory and excludes only itself. Historical manifests must not be mistaken for current checksums of curated successors.

Private provider conversations, route/account records, personal runtime paths, transport ZIPs, Kepler acquisition records and caches are excluded. The T5 scope record is a summary of earlier partial checks, not a complete independent Astropy execution receipt. This release curation adds no observation, scientific run or physical validation. It records the completed prior-version consultations without claiming a review of this final release. Future unfamiliar-host selection and holdout execution remain unactivated.
