# Source attribution and unresolved release terms

This is a local curation record, dated 15 October 2026. It assigns no project license, creates no public deposit and claims no blanket clearance. Source hashes establish byte identity, not ownership or permission. Final human responsibility, upstream attribution/terms review and public-release choices remain open.

## Source families

| Material | Attribution and preserved identity | Present treatment |
|---|---|---|
| Original prototype, lossy export, pre-flux plan, reports and figure | Lilitari's October 8 source-aware TOI-270 development package, directed by Andrei; exact original manifest and files retained | Project provenance retained. No project LICENSE/SPDX grant was found or assigned. The figure's generation script is absent, so regeneration is not claimed. |
| Replay, counterexamples, post-hoc diagnostics and v3.1 code/results/specifications | Coda's recorded work with Andrei and Lilitari; original source hashes plus documented receipt/README derivatives | Project licensing remains a human decision. Original and derived identities are distinct; scientific values are not removed by privacy curation. |
| Native Sector 4/5 light curves and lossy derived flux | NASA TESS mission, SPOC pipeline and MAST archive; TIC 259377017, two-minute products, DATA_REL 42; exact product names/URLs/bytes/hashes in `NATIVE_SOURCE_IDENTITIES.json` | Exact native FITS included locally for offline inspection. Preserve mission/archive credit and determine applicable acknowledgment/data terms before public release. Public retrieval alone is not a blanket project relicensing grant. |
| Known-planet periods in `catalog_comparison.csv` | NASA Exoplanet Archive's original exact-TIC comparison, recorded after the original search; original TOI-270 discovery belongs to Günther et al. | Retain original query/comparison provenance and catalog/discovery attribution. This is not a fresh catalog lookup or current ephemeris claim. |
| Astropy `verify_checksum` source excerpt in `posthoc_diagnostics_results.json` | Astropy 8.0.1, obtained through recorded source inspection; field `astropy_checksum_implementation` | Exact installed copyright, redistribution conditions and disclaimer retained in `licenses/ASTROPY_LICENSE.rst`. That notice applies to the excerpt, not the whole supplement. |
| NumPy/SciPy/Astropy dependencies | Version-pinned identities and method citations | Dependency distributions are not bundled, except the explicitly identified Astropy excerpt and notice. Requirements files do not assign licenses or establish validation. |

The native files are the recorded inputs, not target-pixel images or centroid-validation products. They retain their original missing DATASUM cards and corresponding historical Astropy warnings. The later raw-HDU checksum diagnostics are preserved separately; no FITS header was rewritten. A proposed alternative public package that omits the FITS must retain exact fetch locators and hashes and disclose its acquisition dependency. That decision has not been made here.

## Primary scientific references and official source pointers

These bibliographic identities were checked during the accompanying manuscript preparation; this curation does not make new network requests. They support method/product attribution, not a blanket reuse determination.

- Günther et al. (2019), *A super-Earth and two sub-Neptunes transiting the nearby and quiet M dwarf TOI-270*, Nature Astronomy 3, 1099–1108. https://doi.org/10.1038/s41550-019-0845-5
- Kovács, Zucker and Mazeh (2002), *A box-fitting algorithm in the search for periodic transits*, A&A 391, 369–377. https://doi.org/10.1051/0004-6361:20020802
- Ricker et al. (2015), *Transiting Exoplanet Survey Satellite (TESS)*, JATIS 1, 014003. https://doi.org/10.1117/1.JATIS.1.1.014003
- Jenkins et al. (2016), *The TESS science processing operations center*, Proc. SPIE 9913, 99133E. https://doi.org/10.1117/12.2233418
- Twicken et al. (2020), *TESS Science Data Products Description Document*, Rev F, Table 13. https://archive.stsci.edu/missions/tess/doc/EXP-TESS-ARC-ICD-TM-0014-Rev-F.pdf
- Fausnaugh et al. (2021), *TESS Data Release Notes: Reprocessing of Sectors 1–13, DR42 & DR46*, 11 June, v02. DR42 Sectors 1–6 used science-pipeline version 5.0. https://archive.stsci.edu/missions/tess/doc/tess_reprocessing-sector_1_13_drn42_v02.pdf
- Astropy Collaboration software papers: https://doi.org/10.1051/0004-6361/201322068 ; https://doi.org/10.3847/1538-3881/aabc4f ; https://doi.org/10.3847/1538-4357/ac7c74 . Official citation guidance: https://www.astropy.org/acknowledging.html
- Harris et al. (2020), NumPy: https://doi.org/10.1038/s41586-020-2649-2 ; Virtanen et al. (2020), SciPy: https://doi.org/10.1038/s41592-019-0686-2
- Original catalog interface reference: https://exoplanetarchive.ipac.caltech.edu/docs/TAP/usingTAP.html ; mission documentation: https://heasarc.gsfc.nasa.gov/docs/tess/documentation.html . Actual current archive acknowledgment and reuse terms remain a final release check.

The seven derivatives remove only specified interpreter paths, two local input paths, receipt HTTP headers or two README path assignments. The original receipts remain preserved privately; no credential leak is asserted. Historical manifests retain original hashes and may therefore intentionally differ from curated files. Private provider conversations, route/account evidence, personal runtime paths, transport ZIPs, Kepler acquisition records and caches are excluded from this candidate.

This candidate does not include Lily's private review transcripts. Her partial extracted-check scope is described in the manuscript; it is not fabricated into a second full v3.1 execution receipt. A separate newly requested Red review, any later local replay, and final release authorization require their own evidence states.
