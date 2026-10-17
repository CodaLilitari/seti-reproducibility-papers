# Public derivative record

Original files remain preserved privately. Exact source/derived hashes and project-relative source identities for the four original derivatives are retained in `history/CURATION_PROVENANCE_v1.json`; the current `CURATION_PROVENANCE.json` records successor ancestry and changes. A change in bytes is identified explicitly; no derivative is described as byte-identical to its source.

## Finite-correlation follow-up

`analysis/ren2024/ren2024-assessment/math/reviewer_followup.py` is derived from the completed October 11 implementation. The source implementation coupled scientific replay to the identity of a private Claude review. This derivative:

1. Removes the reads of the private reviewer-provenance JSON and answer Markdown.
2. Removes exactly three review-only assertions: completed review identity, answer hash, and membership of the private review files among read inputs.
3. Replaces the private review identifiers in generated result/report text with a concise explanation of the derivative.
4. Clarifies that future generated runtime receipts contain local execution paths and require curation before redistribution.

At the v1/v2 derivation, all remaining `check(...)` call expressions were structurally identical to the original, as established by AST comparison without importing or executing the module; `audit_astrometry.py` was then byte-identical. In v3 the follow-up retains its exact-script-hash assertion with only its expected-hash constant updated to the documented audit derivative below. All other AST nodes remain identical to v2. Numerical expressions, scientific assertions, thresholds, hardcoded source qualifications, scenarios, input paths and source/header bindings are unchanged.

The exact unified diff is retained in the private publication receipts; its digest appears in the public curation provenance. The diff itself contains the removed private review identifiers and is not part of this supplement. Source/derived hashes permit a later authorized comparison without publishing those private records.

The original structural check did not establish execution. The separate 15 October replay subsequently executed the v1/v2 public derivative once: all 122 remaining checks passed, the numerical CSV was byte-identical and selected scientific fields matched. The original 125-check count includes three private-review checks and is not attributed to the derivative. The preserved historical comparison is in status/REPLAY_COMPARISONS.json. The later exact-v3 execution is separately identified in `status/README_OMISSION_RUNTIME.json`.

## Three RACS retrieval receipts

The three `racs/header_*.txt.receipt.json` files retain only requested public URL, UTC retrieval time, method, status, byte count and body SHA-256, plus a curation note. Full HTTP headers and receipt-internal metadata are omitted. The scientific follow-up reads the same required status, URL and body-hash values as before. The corresponding retrieved header bodies are byte-identical.

These are derived receipts, not unmodified transport captures. Each source and derivative hash is recorded. Other raw HTTP/session receipts are excluded.


## Astropy72 provenance-only derivative

`analysis/controls/astropy72/astropy_crosscheck_public.py` removes exactly the historical HTML path assignment and its hash assertion; adds exactly the two hashes for parsed source tables and radius CSV; and retains the existing Gaia pin. All other source text is unchanged. Its exact `SOURCE_DIFF.patch`, narrowly normalized `AST_PROOF.json`, input identities and `DERIVATION_PROVENANCE.json` accompany the script. The full HTML remains excluded; the derivative does not revalidate its extraction.

One isolated, single-thread, below-normal execution on 15 October 2026 reproduced the complete 72-row CSV byte-for-byte and matched all scientific summary fields exactly. `REPLAY_COMPARISON.json` records the frozen policy, actual source/input/output hashes, environment, date and guards. The supplied summary is a deliberate derivative of the raw output: only its private executable field is removed, with both hashes retained. The calculation's own output serialization was not changed; a future run still writes its execution path.

## Current status and compact records

The existing eight-command raw execution receipt is curated into `status/REPLAY_COMPARISONS.json`; it retains every comparison's actual/reference hashes and status, per-command source/input identities, criteria and one I exception linked to both failed representations. Absolute interpreter/cache/work paths and unrelated logs are omitted. Null supplied paths explicitly identify exact private artifacts not included in this package. Source retrieval bodies are omitted; their existing dates, public URLs and hashes are recorded in `status/SOURCE_STATUS_RECORD.json`. No new query or old-command rerun was performed to create those records.

The public claim map remains non-exhaustive. README, release status and this derivative note are successor documents; the original frozen package and its ancestry records are preserved, not overwritten. These curation changes assign no blanket license. The author's separate instruction authorizes eventual public release after preparation and review; no public upload is claimed.

## V3 ReadMe omission and dependent identity pin

Four complete CDS ReadMes are omitted in this isolated successor and replaced by canonical references with historical hashes. The numerical TSVs, source provenance facts, epoch/uncertainty table, figures and historical outputs are unchanged. Frozen v2 is preserved.

`audit_astrometry.py` deletes exactly old line 167, an unused `read(BASE/f'g-surveys/{s}_ReadMe.txt')` expression. This removes four documentation hashes from future `INPUTS` receipts and the input-preservation scope; all actual numerical input checks remain. Its complete remaining AST equals v2 after excluding only that expression.

`reviewer_followup.py` changes exactly the expected audit SHA-256 literal in old line 95, from `09adb284f2c2a8cb3f37d1ae37f6979bc69195cc0fedf712035136dc208beffd` to `0f6ea11aa6cc006ab10dfaa644d394c9fdeeb019ae59467b22511a1820b07c93`. The assertion is retained and the new pin equals the actual derivative bytes. A separate proof changes only that one AST Constant; all other nodes match v2.

The exact two-file unified diff and independent narrow proof records are in `derivations/readme-omission/SOURCE_DIFF.patch` and `STATIC_PROOF.json`. Neither module was imported or scientifically executed during the original v3 curation. On 17 October, the exact two derivatives were subsequently executed once each in an isolated copy, passing 174 and 122 assertions. Eight numerical outputs were byte-identical and seven selected scientific JSON fields matched exactly. The separate current record is `status/README_OMISSION_RUNTIME.json`; the older execution identities and the original static proof remain preserved. The source notice is an added documentary payload.

## Final release assembly and runtime record

The v1.0 candidate changes no v3 scientific source, numerical input/output, figure, static proof or historical replay payload. It adds the sanitized two-command runtime record and updates current status documentation. The initial controller stopped after successful audit execution because a reference file was looked up under the wrong relative directory. The corrected reference mapping preserved comparison criteria, did not repeat the audit, and executed only the follow-up. The record retains this failure and recovery, with private absolute paths and review prose omitted. Original receipt/policy hashes and selected scientific-field identities remain available.
