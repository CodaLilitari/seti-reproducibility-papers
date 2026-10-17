# Reproduction commands and boundaries

These commands document the supplied computations. Curation itself runs none of them. Preserve the candidate and its top-level manifest; use a **new disposable copy with the same sibling-directory layout** for every independently authorized numerical replay. An already-created `development-replay/package_copy` makes `replay.py` stop rather than overwrite it. Use an existing suitable interpreter; no installation or network operation is part of these instructions.

## Read-only package integrity

From the candidate root, with any suitable Python 3 interpreter:

```powershell
python .\verify_manifest.py
```

The checker reads bytes and JSON only, rejects missing/extra files and unsafe paths, and checks every manifest byte count and SHA-256. It does not import any supplied scientific module. Historical manifests under `provenance/historical/` are archival evidence; the top-level manifest is authoritative for the curated candidate.

## Existing dated replay, not a request to rerun

The separate 15 October same-code synthetic replay has already completed once. Its included status and compact comparison record are `replay/TESS_REPLAY_STATUS.md` and `replay/TESS_REPLAY_COMPARISON.json`. The latter preserves the predeclared criteria, all 24 recorded checks, all six input-source hashes, four reference/output identities, environment, dates, runtime exclusions and limits. The two generated synthetic JSON files are byte-identical to the supplied historical references. The raw QA wrapper/logs and private interpreter-path-bearing receipts are not supplied; provenance hashes do not imply delivery of those files. This curation executes no tests. The historical 8 October measurements below remain historical, and the two runs are not two independent implementations.

## Recorded environments

| Lane | Recorded environment | Requirement file |
|---|---|---|
| Original delivered prototype | Linux CPython 3.13.5, NumPy 2.3.5; environment also lists SciPy 1.17.0 and Matplotlib 3.10.8, which `search.py` does not import | `requirements-prototype.txt` gives the actual direct numerical dependency |
| Coda's original replay/counterexamples | Windows CPython 3.13.15, NumPy 2.3.5 | `requirements-prototype.txt` |
| Full-cadence/post-hoc comparison | Windows CPython 3.13.15, NumPy 2.5.3, Astropy 8.0.1 | `requirements-analysis.txt`; SciPy is required additionally by v3.1 |
| v3.1 offline implementation | Windows CPython 3.13.15, NumPy 2.5.3, SciPy 1.18.1, Astropy 8.0.1 | `requirements-analysis.txt` |

Requirements describe historical identities; they do not certify availability or install anything. One modern interpreter is not evidence of identical historical environments. Keep actual environment/version/source hashes with any new run. A freeze explicitly binds Python and numerical dependencies; do not rewrite that identity to force acceptance across versions.

## Separate v3.1 synthetic verification

Set the exact **disposable** copy and existing interpreter paths. The following is one command, not an invitation to run simultaneous workers:

```powershell
$tessWork = 'C:\path\to\new-disposable-copy'
$tessPython = 'C:\path\to\existing\python.exe'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:OMP_NUM_THREADS = '1'
$env:OPENBLAS_NUM_THREADS = '1'
$env:MKL_NUM_THREADS = '1'
$env:NUMEXPR_NUM_THREADS = '1'
$env:VECLIB_MAXIMUM_THREADS = '1'
$env:BLIS_NUM_THREADS = '1'
& $tessPython (Join-Path $tessWork 'tess-development-v3_1/run_offline_checks.py')
```

The six `.py` files in that directory are its runtime file inputs. It generates arrays and metadata fixtures in memory and calls real small Astropy BLS searches. The historical suite contains 47 tests: 39 photometry/timing/contribution/connected-path tests and eight metadata tests. The runner also creates its connected demonstration and signed-contribution examples; these are not added to the test count.

It writes `unittest.log`, `VERIFICATION_RECEIPT.json`, `synthetic_output/discovery_freeze.json` and `synthetic_output/synthetic_driver_result.json` beside the copied source. Its import-time operations set one-thread environment variables, disable bytecode output, install a Python socket/DNS/bind/sendto audit guard and verify below-normal Windows priority. The guard is a Python-level restriction, not an OS sandbox. On non-Windows systems the measured Windows priority/peak-memory fields are unavailable. The historical 2.969 seconds and 104,251,392-byte peak working set are observations of that run, not guarantees for other hosts.

Compare actual counts/status and preserved source hashes first. Separate timing, paths, timestamps, memory and platform/version differences from scientific output. With the same bound identities, compare the connected freeze/result and event-depth/concentration results; any failed or inconclusive fixture must stay visible. A passing suite proves specified behavior on these fixtures, not astronomical false-alarm calibration.

## Historical known-host calculations

The following dependent sequence is supplied for separately authorized reproduction, with existing environment selection as above. `replay.py` uses the NumPy 2.3.5 lane; the later Astropy commands use the NumPy 2.5.3/Astropy 8.0.1 lane. Set `$tessPrototypePython` and `$tessAnalysisPython` accordingly. Execute serially from a fresh disposable package copy:

```powershell
Push-Location -LiteralPath $tessWork
try {
    & $tessPrototypePython .\development-replay\replay.py
    if ($LASTEXITCODE -ne 0) { throw 'Prototype replay failed; stop.' }
    & $tessPrototypePython .\development-replay\counterexamples.py
    if ($LASTEXITCODE -ne 0) { throw 'Counterexample replay failed; stop.' }
    & $tessAnalysisPython -c "import sys,runpy; sys.path.insert(0,'development-replay'); import replay; runpy.run_path('standard-bls/run_crosscheck.py',run_name='__main__')"
    if ($LASTEXITCODE -ne 0) { throw 'Standard comparison failed; stop.' }
    & $tessAnalysisPython .\development-replay\posthoc_diagnostics.py
    if ($LASTEXITCODE -ne 0) { throw 'Post-hoc diagnostics failed; stop.' }
} finally {
    Pop-Location
}
```

The wrapper for `run_crosscheck.py` first imports the existing replay guard because that crosscheck script alone has no network audit hook. No source bytes are altered by this wrapper. On Windows, `replay` also establishes and verifies below-normal process priority. The post-hoc script uses a Windows peak-working-set assertion and is not a demonstrated portable non-Windows runner.

| Script | Reads | Writes in disposable copy |
|---|---|---|
| `development-replay/replay.py` | Original prototype, its 19-entry manifest, lossy CSV and original results | New `package_copy/`, manifest/six-test/three-peak logs and `replay_receipt.json`; result files within `package_copy` |
| `development-replay/counterexamples.py` | `package_copy/search.py` plus original manifest/source | `counterexamples_receipt.json`; changes search configuration only in memory |
| `standard-bls/run_crosscheck.py` | Original `search.py`, lossy CSV and both exact native FITS | `configuration-before-run.json`, `crosscheck-results.json` |
| `development-replay/posthoc_diagnostics.py` | Original prototype/results, crosscheck result, full-cadence FITS and helpers | `posthoc_diagnostics_results.json`; original source and standard comparison files must stay unchanged |

Preserve the original miss of b, third-peak sign disagreement, explicit five-peak/detrending exploratory status and all counterexamples. Last floating-point digits may vary across platforms. Comparison criteria must be stated before interpreting any mismatch; do not rerun with relaxed criteria until a desired match appears. Regenerated receipts contain local interpreter/runtime fields and are **not** automatically public-safe derivatives.

The original `data/retrieval.wl` is a historical remote-fetch program and must not be run as part of offline replay. The provided figure lacks its generator. No commands here select unfamiliar hosts, acquire a cohort, complete physical vetting or activate the stopped Kepler branch.
