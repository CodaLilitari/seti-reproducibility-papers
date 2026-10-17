# TESS v3.1: synthetic replay status

**15 October 2026: passed.** The existing v3.1 `run_offline_checks.py` command was executed exactly once from an isolated copy of its six frozen Python sources. All **47 tests passed**, with **zero failures, errors or skips**. The connected synthetic output and discovery-freeze JSON files were **byte-identical** to their retained 8 October references. No scientific source or test output was changed, no numerical command was repeated, and no comparison criterion was relaxed.

## What was reproduced

The suite contains 39 photometry, timing, masking, connected-path and contribution-diagnostic tests, plus eight metadata-contract tests. It exercises actual Astropy BLS calculations on small synthetic fixtures and checks the existing connected discovery → freeze → fixed holdout example. The 730-day grid regression stops before allocating its oversized grid; the command does not perform a full real-data search.

The connected synthetic holdout result remains `recovered`, with discovery-freeze digest:

`68f4b8d3693539290efe44dc0dd753ca0683a4ae6996201bc8d84c5714c49662`

All scientific values and statuses in both generated JSON files matched exactly. This includes the discovery attempts, frozen masks, timing and depth records, input/configuration identities, holdout prediction and signed contribution diagnostics. The retained sector-edge regression still passes by requiring an `inconclusive` result when timing refinement changes the covered event-cycle set; no criterion was weakened to convert it to recovery.

The historical test names and outcomes also matched exactly. All nonexcluded verification-receipt fields matched the reference, including source/library identities, the fixed holdout status, the long-baseline grid plan and contribution examples. Only UTC, executable location, memory use and elapsed time were treated as runtime metadata; the unittest log's duration line was handled separately. These exclusions were declared before execution.

## Execution conditions and observations

| Item | Observed replay result |
|---|---:|
| Tests | 47 |
| Failures / errors / skips | 0 / 0 / 0 |
| Numerical thread setting | 1 |
| Windows process priority | Below normal, verified by the runner |
| Runner-measured elapsed time | 2.9839494000189006 seconds |
| Runner-measured peak working set | 103,927,808 bytes, approximately 99.1 MiB |
| Unchanged memory acceptance criterion | Less than 1 GiB |
| Scientific command exit code | 0 |
| Outer audit-hook blocked events | 0 |

The existing environment supplied Python 3.13.15, NumPy 2.5.3, SciPy 1.18.1 and Astropy 8.0.1. No packages were installed. Commands ran serially; thread environment variables were set to one. Temporary and scientific-library cache/config directories were isolated. An inspected outer Python audit hook denied network socket operations, subprocess creation and writes outside the disposable replay directory, while allowing the local host-name lookup needed by imports. The runner retained its own network restrictions. No acquisition or GPU code was invoked.

These are observed conditions for this one run. Thread settings and process priority are not a kernel CPU quota, and the memory criterion is checked after execution rather than enforced as a preemptive cap. The Python audit hook is an application-level safeguard, not an OS firewall or packet capture.

## File identities and preservation

The discovery-freeze object's digest above differs from its file SHA-256 because it hashes the canonical record inside the JSON wrapper. The exact output file identities are:

| Artifact | SHA-256, identical for historical and replay output |
|---|---|
| `synthetic_output/discovery_freeze.json` | `c978b901025857d894737b7f2fb251dc86c55eb840811e9c2220de1dfcdbe668` |
| `synthetic_output/synthetic_driver_result.json` | `392c976a64ab24ef08265d992b1421e85208a66465a5a559889d9a0eaa315047` |

The unchanged runner source SHA-256 is `e92419e95be37e9f2503a1491a355691a66019c2b7d50ba10137dcb92b9819e8`; the production-component source SHA-256 is `1e01c9ba8b358228aed0581f1731f99dc1595402037f4bbf9f7cc0f8c6832826`. Before/after checks also verified the other four sources. All six staged source files, all six canonical source files and the four canonical reference outputs remained unchanged. Raw execution records are retained separately from this public-safe status document.

## Scope of the evidence

This is a replay of the same implementation and fixed synthetic fixtures. It supports the reproducibility of the existing tests, connected numerical example and reporting-only contribution diagnostics. It does not establish live metadata completeness, unfamiliar-host execution, FITS transport/header correctness, full observational processing, empirical false-alarm or completeness calibration, physical vetting or a planet discovery. No real target, full-cadence scan or additional numerical study was introduced.

This status document does not authorize publication or assign licenses. Public release and licensing remain subject to the separate release decision.
