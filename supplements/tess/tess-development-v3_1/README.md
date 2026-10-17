# TESS development v3.1 — offline reusable components

Coda, collaborating with Andrei and Lilitari. This is an executed **synthetic development implementation**, not an activated unfamiliar-star survey. Earlier source artifacts, result ZIPs and the stopped Kepler transaction are unchanged. No network request, unfamiliar metadata query, unfamiliar flux inspection, GPU task or native UI operation is part of these components or their verification.

## Verified result

`VERIFICATION_RECEIPT.json` and `unittest.log` record **47 tests, zero failures/errors/skips**, with unchanged Python source during execution. The combined run includes 39 photometry/timing/contribution/connected-path tests and eight metadata tests (some have multiple adversarial subcases). The final verification took **2.97 seconds**, measured **104,251,392-byte peak working set** (about 99.4 MiB), and used one numerical thread with verified Windows below-normal priority. Outbound socket/DNS/bind/sendto operations were blocked.

Pinned existing environment used: CPython 3.13.15, NumPy 2.5.3, SciPy 1.18.1, Astropy 8.0.1. No packages were installed. Exact source and environment identities are in the receipt; the artifact manifest separately pins documents and generated evidence.

The connected synthetic path starts from raw SAP/PDC/formal-error/quality/sector arrays, preprocesses them, attempts three global maxima, builds the complete other-mask ledger, fits discovery-only event times and ephemeris, remeasures discovery at that fitted ephemeris, freezes every attempt together, then creates and evaluates separate synthetic holdout data at fixed predictions. It returns `recovered` for its fully covered injected control. A separate original sector-edge fixture remains `inconclusive` because the covered event-cycle set changes after timing refinement. That edge outcome is preserved as a regression; no criterion was relaxed to rescue it.

The synthetic search fixture uses a declared 2–4 day range and a 2-hour duration to make a small, interpretable test. It does not replace the proposed survey's default 0.6–13 day/duration choices. The first known injected signal's alias is specified from its generating construction; the other two attempted maxima remain explicitly unresolved. This is no claim that the code can infer an orbital alias or validate an actual planet.

## v3.1 diagnostic-only amendment

This directory began as an exact, verified copy of the 13 files listed in the v3 manifest plus that manifest, with no cache files. The original v3 directory and archive were not changed. Its manifest SHA256 is `89eacdaf36a78fafd517c000af9696363fa754fbb0936d9ad8fe415a469114f8`. A final read-only check verified all 13 original files and that manifest identity again.

Only the production function `combine_events` changes. Each computed combination now includes `event_contributions`, in original input order, with the zero-based `event_index`, `normalized_inverse_variance_weight` (`a_i=w_i/sum(w)`), and signed `signed_snr_contribution` (`c_i=w_i*d_i/sqrt(sum(w))`). The weights sum to one; the signed contributions sum to the existing formal combined S/N within floating-point arithmetic. All covered negative and zero depths remain included. Insufficient or invalid combinations keep their original inconclusive results.

`max_absolute_snr_contribution_fraction` reports `max(abs(c_i))/sum(abs(c_i))`. A zero denominator produces JSON `null` with `contribution_concentration_unavailable_reason: "zero_total_absolute_snr_contribution"`; otherwise that reason is `null`. There is no new veto, threshold or classification criterion.

The equal-variance examples `[-0.1]+[2.2]*9` and `[-0.1,19.72]+[0.01]*8` retain the same aggregate depth (1.97), formal S/N (about 6.22969), and recovery classification for consistent discovery depth. Their concentration fractions are **0.11055276381909547** and **0.9909547738693468**. Thus the report reveals a dominant single event without silently converting the diagnostic into an acceptance rule. Full example outputs are recorded in `VERIFICATION_RECEIPT.json`.

Five new regressions cover equal-aggregate/different-concentration recovery, unequal inverse-variance weights with uncovered-event index preservation, explicit zero denominator, opposite-sign cancellation, and unchanged invalid/insufficient classifications. All 42 existing tests also pass. The connected outputs were regenerated because source identity changes; a read-only comparison against v3 confirms that every previous numerical value and status is identical after excluding added diagnostic fields and the updated source/freeze hashes. The runner and tests changed only to verify/report this amendment; metadata and synthetic-generation code are unchanged.

## Components and evidence

| File | Implemented scope |
|---|---|
| `tess_components.py` | Common array-level quality support, per-sector normalization, gap-aware median/error propagation, bounded period grid, chunked global BLS maximum, all-three-attempt masks/freeze, coverage, local weighted depths, signed event-time fit/full nuisance covariance, weighted ephemeris covariance, fixed holdout calculation. |
| `synthetic_driver.py` | Connected raw-array discovery → freeze → holdout demonstration, with frozen holdout assignment before holdout construction. |
| `metadata_contract.py` | Pure offline validator for one declared normalized JSON/indexed-page envelope, exact IDs, completeness, release ordering, deterministic selection and sector/product assignments. No provider-specific transport. |
| `test_tess_components.py` / `test_metadata_contract.py` | Executed synthetic/adversarial regressions; no real target inputs. |
| `run_offline_checks.py` | One-thread, verified-priority, network-blocked combined suite and connected artifact generation. |
| `IMPLEMENTATION_SPEC.md` | Frozen computational choices, covariance assumptions, masks, coverage, holding assignment and explicit limitations. |
| `METADATA_COMPLETENESS_SPEC.md` | Metadata completeness/identity/release contract and implemented normalized-envelope boundary. |
| `synthetic_output/discovery_freeze.json` | Full three-attempt record, actual stored grid, original/fitted diagnostics, timing/mask ledger, input/code/dependency identities and precommitted holdout span/clock. |
| `synthetic_output/synthetic_driver_result.json` | Connected synthetic result including event support, depth combination, timing propagation and unrefitted holdout outcome. |

The metadata validator and photometric path are separate offline components. This package does not connect a live metadata universe to downloaded FITS and a survey-wide runner. Calling that full catalog-to-vetting path complete would exceed the executed evidence.

## Important enforced distinctions

- Holdout requires at least two covered events and combines **every covered depth**, including zero/negative values. Aggregate depth must be positive, formal aggregate S/N at least five, and discovery/holdout depths consistent within three combined standard errors. There is no every-event-positive condition. The equal-sigma `[-0.1, 2.2 × 9]` test passes with combined S/N 6.2296869905317065 when discovery depth is consistent; `Phi(1)^25 = 0.013315260765244287` is independently calculated.
- A complete metadata row failing a cut differs from missing/incomplete acquisition. Incomplete required evidence cannot produce a sample. Exact TIC IDs never pass through floating point; release order and all-host completeness are explicit.
- Grid spacing bounds only phase drift across the full discovery baseline. The 730-day default planning example needs 1,810,402 grid points; the frozen 250,000-point development ceiling causes a resource stop, without coarsening. Chunk sizes preserve the same global maximum and tie rule.
- Computationally valid failed maxima remain mask sources. Every candidate excludes its own mask but retains all other original masks, including later failed-screen maxima. The same ledger applies to holdout and records lost coverage.
- Candidate original search/screen depths, discovery timing fits, final fitted-ephemeris discovery depths, and holdout depths are separately named. All adequately covered discovery events must yield valid signed-depth timing fits; any numerical timing failure makes timing inconclusive. Unresolved aliases remain inconclusive. No favorable subset is chosen.
- Holdout span and cadence clock are committed at discovery freeze; narrowing the span or changing the clock is rejected. Executing source, Python and numerical-library identities must match the freeze. Invalid future/overlapping spans, changed code/dependencies, duplicate cadence IDs across adjacent windows, and multidimensional flux/error arrays are covered by regressions.
- Timing covariance includes baseline/slope/depth nuisance parameters but is conditional on a fixed trapezoid, Gaussian formal errors and a resolved cycle alias. It does not account for red noise, detrending uncertainty, dilution or general model mismatch. Formal S/N is not FAP.

## Exact commands

From PowerShell, the combined verification uses the existing interpreter and enforces its own thread, priority and network restrictions:

```powershell
$tessDevRoot = 'C:\path\to\disposable-copy\tess-development-v3_1' # select your disposable working-copy directory
$tessDevPython = 'C:\path\to\existing\python.exe' # select your existing suitable interpreter
& $tessDevPython (Join-Path $tessDevRoot 'run_offline_checks.py')
```

This writes `unittest.log`, `VERIFICATION_RECEIPT.json` and the synthetic outputs. Preserve a returned packet before rerunning, because those development evidence files are refreshed. The original astronomical source files are not inputs to this runner.

For just one test module while retaining the same resource/network guard:

```powershell
Push-Location -LiteralPath $tessDevRoot
try {
    & $tessDevPython -c "import run_offline_checks, unittest; r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromName('test_tess_components')); raise SystemExit(not r.wasSuccessful())"
} finally {
    Pop-Location
}
```

The synthetic connected driver can be inspected through its already generated JSON. Running `run_offline_checks.py` regenerates it under the enforced guard; there is no need to run a separate numerical job concurrently.

## Unimplemented outer stages; live execution remains closed

Actual MAST/TIC request and pagination semantics, returned schema/version evidence, live snapshot consistency, raw-response preservation, product transport and original FITS header/time validation are not implemented here. The nominal cadence clock must be connected to real product cadence/time metadata before real analysis. Discovery-only alias adjudication and its evidence are external; setting `resolved` is not proof. A frozen correlated-noise/systematics/injection development protocol, realistic uncertainty validation, pixel/centroid/crowding checks, unequal-EB/secondary diagnostics, catalog/literature novelty review, and survey orchestration remain required separate work. There is no empirical FAP/completeness calibration or physical planet confirmation.

No code or proposal here authorizes unfamiliar-host execution, changes the existing Kepler review stop, or permits public release. The scope completed is the compact offline implementation and its meaningful synthetic verification.
