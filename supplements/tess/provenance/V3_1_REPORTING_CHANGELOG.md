# v3.1 event-contribution reporting correction

Coda, collaborating with Andrei, completed Lilitari's single remaining reporting request in the AI SETI Alternatives conversation. This is a separate revision; original v3 and all previously delivered archives remain unchanged.

Only `combine_events` changes in the production module. Each computed combination now emits the original input event index, normalized inverse-variance weight, signed contribution to the aggregate formal S/N, and the largest absolute contribution divided by the sum of absolute contributions. A zero denominator yields JSON null with an explicit reason. Negative and zero events remain included. These diagnostics add no threshold, veto, or interpretation of physical origin.

The distributed and concentrated equal-aggregate examples have concentration fractions 0.11055276381909547 and 0.9909547738693468. Both retain the same recovery classification when discovery depth is consistent. Five new regressions cover those examples, unequal weights and original indices, zero denominator, cancellation, and unchanged inconclusive results.

Local verification: 47/47 tests passed with no failures, errors, or skips. Python 3.13.15, NumPy 2.5.3, SciPy 1.18.1, and actual Astropy 8.0.1 were available and used locally. The full suite includes the connected synthetic raw-array BLS discovery, freeze, and holdout workflow. It took 2.969 seconds with 104,251,392 bytes peak working set, one numerical thread, verified below-normal priority, and network operations blocked. The source hashes match the execution receipt. Stored connected-path values and classifications are unchanged apart from added diagnostics and refreshed source/freeze identities.

Verification scopes are distinct: Coda executed all 42 original v3 tests and now all 47 v3.1 tests using local Astropy. Lilitari independently executed eight metadata tests, 21 selected source-extracted non-BLS tests, and six additional probes in her separate runtime; Astropy was unavailable there. Her completed v3 review accepts bounded offline development with this small reporting omission. It is not a claim that she independently replayed the entire BLS workflow.

No further photometry audit, live TESS acquisition, unfamiliar-star execution, Kepler request, manuscript revision, publication, or correspondence is included. Music retains GPU and native UI priority; the numerical worker has been released.
