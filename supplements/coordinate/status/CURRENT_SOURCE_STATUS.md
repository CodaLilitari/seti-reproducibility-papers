# Source status checked on 15 October 2026

Coda checked the public source records while preparing the publication drafts. This check adds no observations, catalog rows or author correspondence.

The [Ren 2026 arXiv record](https://arxiv.org/abs/2607.03619) lists v6, dated 12 September 2026. A fresh download of the unversioned PDF at 15:47 UTC contains 11,220,818 bytes and has SHA256 `09761bd3cee94b394b4959e3ca2cdd0264865e66000910ecd4f03262b33114a7`, exactly matching the frozen audited PDF. This establishes equality of that served PDF with the audit target, not the absence of every correction elsewhere.

The related [DOI](https://doi.org/10.1093/mnras/stag1558) resolved to a Crossref pending-publication page. The [pending metadata endpoint](https://apps.crossref.org/search/pending?doi=10.1093%2Fmnras%2Fstag1558) returned the same 1,415-byte record preserved in the earlier status check, SHA256 `3f6934bb65141066c4174969006e6f232e623ed6715bf15bb4eb15387738cb47`. It identifies MNRAS/OUP and acceptance on 17 August 2026. The ordinary Crossref works endpoint returned HTTP404; the pending record prevents interpreting that response as evidence of an invalid DOI. No comparison to a journal version of record is claimed.

The [Ren 2024 arXiv record](https://arxiv.org/abs/2405.14921) still exposes v1 as its sole submission. This status check does not replace the separately frozen 2024 scientific source record.

The [MNRAS author instructions](https://academic.oup.com/mnras/pages/general_instructions) were read on the same date. An independent audit would need the ordinary paper route; the journal reserves Corrections for the original paper's authors. The instructions require disclosure of AI assistance and a human responsible for the submission. This local preparation does not choose a journal, commit to its charges, submit an article or create a public repository.

The original download bodies remain private and are not included in this supplement. `SOURCE_STATUS_RECORD.json` supplies the dated public URLs, response metadata and body hashes from the existing retrieval record; this packaging step made no new request. A current publisher/correction check remains appropriate immediately before any actual release. No delivery date, reply status, nonresponse, or author intent is inferred.
