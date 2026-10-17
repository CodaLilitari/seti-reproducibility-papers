"""Pure offline, fail-closed metadata contract; no network or file access.

See METADATA_COMPLETENESS_SPEC.md. This intentionally supports ONE normalized
wire schema and indexed, total-counted pages, not an implemented MAST adapter.
Only explicit null missingness and TESS/SPOC/lightcurve classification are
supported; unknown labels or alternative protocols fail instead of becoming
host exclusions. The two proposal-mandated TIC exclusions are always required.
Raw JSON is the sole record authority; callers cannot supply normalized records.
The full accepted synthetic envelope/config example is make_fixture() in
test_metadata_contract.py. All timestamps and snapshot evidence are supplied
claims checked for internal consistency, never remote verification.

Envelope shape:
  {batch_id, synthetic, retrieval_started_at, retrieval_finished_at,
   availability_cutoff, catalog_snapshot_id, inventory_snapshot_id,
   catalog: Dataset, observations: {canonical_tic_id: Dataset},
   products: {canonical_tic_id: Dataset}}
Dataset: {state: complete|pending|failed, reason, snapshot_id,
          snapshot_evidence, pages: [{raw_json, sha256, byte_length,
                                    retrieved_at}]}
Each raw_json is an exact UTF-8 JSON page; see PAGE_KEYS below. Normalization is
derived exclusively from its hash-checked decoded rows. Inputs are not mutated.
"""

from collections import defaultdict
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import math
import re


CUTS = {"Tmag": [8, 12], "Teff": [3000, 5200], "rad": [0.15, 0.85],
        "logg": [4.2, 5.2], "d": [5, 100]}
UNITS = {"Tmag": "mag", "Teff": "K", "rad": "solar_radius",
         "logg": "cgs", "d": "pc"}
SCHEMAS = {"catalog": "tic-v8.2-normalized-v1",
           "observations": "tess-observations-normalized-v1",
           "products": "tess-products-normalized-v1"}
REQUIRED_EXCLUSIONS = {"259377017", "4206066"}
ENVELOPE_KEYS = {"batch_id", "synthetic", "retrieval_started_at",
                 "retrieval_finished_at", "availability_cutoff",
                 "catalog_snapshot_id", "inventory_snapshot_id", "catalog",
                 "observations", "products"}
CONFIG_KEYS = {"contract_version", "frozen_at", "catalog_name", "catalog_version",
               "pagination", "consistency", "missing_policy", "id_policy",
               "cuts", "units", "sample_size", "excluded_tic_ids", "requests",
               "release_order"}
PAGE_KEYS = {"batch_id", "dataset", "tic_id", "request_sha256", "schema_id",
             "catalog_version", "snapshot_id", "availability_cutoff", "index",
             "next_index", "terminal", "total_rows", "row_count", "http_status",
             "overflow", "error", "rows"}
PRODUCT_KEYS = {"tic_id", "observation_id", "sector", "mission", "pipeline",
                "cadence_seconds", "kind", "release", "uri", "pipeline_version",
                "time_system", "advertised_sha256"}


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False)


def content_digest(value):
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def tic_hash(tic_id):
    return hashlib.sha256(("coda-tess-v1|" + tic_id).encode("utf-8")).digest()


class Invalid(ValueError):
    def __init__(self, code, where, status="FAILED"):
        self.code, self.where, self.status = code, where, status


def require(condition, code, where, status="FAILED"):
    if not condition:
        raise Invalid(code, where, status)


def exact_keys(value, keys, where):
    require(type(value) is dict and set(value) == set(keys), "SCHEMA_KEYS", where)


def nonempty(value):
    return type(value) is str and bool(value.strip())


def positive_int(value):
    return type(value) is int and value > 0


def canonical_id(value, where):
    if positive_int(value):
        return str(value)
    require(type(value) is str and re.fullmatch(r"[1-9][0-9]*", value) is not None,
            "INVALID_TIC_ID", where)
    return value


def timestamp(value, where):
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        require(parsed.tzinfo is not None, "INVALID_TIMESTAMP", where)
        return parsed.astimezone(timezone.utc)
    except (ValueError, TypeError, AttributeError):
        raise Invalid("INVALID_TIMESTAMP", where) from None


def strict_json(raw, where):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "DUPLICATE_JSON_KEY", where)
            result[key] = value
        return result

    def bad_constant(_):
        raise Invalid("NONSTANDARD_JSON_NUMBER", where)

    try:
        return json.loads(raw, object_pairs_hook=pairs, parse_constant=bad_constant)
    except Invalid:
        raise
    except (ValueError, TypeError, OverflowError):
        raise Invalid("INVALID_JSON", where) from None


def validate_config(config):
    exact_keys(config, CONFIG_KEYS, "config")
    fixed = {"contract_version": "offline-metadata-v1", "catalog_name": "TIC",
             "catalog_version": "8.2", "pagination": "indexed-total-v1",
             "consistency": "explicit-snapshot-ids-v1", "missing_policy": "null-only",
             "id_policy": "positive-exact-canonical-v1", "sample_size": 20,
             "cuts": CUTS, "units": UNITS}
    require(all(config[k] == v for k, v in fixed.items()),
            "UNSUPPORTED_CONFIG", "config")
    require(type(config["sample_size"]) is int, "UNSUPPORTED_CONFIG", "config")
    timestamp(config["frozen_at"], "config.frozen_at")
    require(type(config["excluded_tic_ids"]) is list, "SCHEMA_KEYS", "exclusions")
    excluded = [canonical_id(v, "exclusions") for v in config["excluded_tic_ids"]]
    require(len(excluded) == len(set(excluded)), "DUPLICATE_EXCLUSION", "exclusions")
    require(REQUIRED_EXCLUSIONS.issubset(excluded), "REQUIRED_EXCLUSION_MISSING", "exclusions")
    exact_keys(config["requests"], SCHEMAS, "requests")
    for kind, request in config["requests"].items():
        exact_keys(request, {"endpoint", "parameters", "projection", "protocol_evidence"}, kind)
        require(nonempty(request["endpoint"]) and nonempty(request["protocol_evidence"])
                and type(request["parameters"]) is dict, "REQUEST_CONTRACT", kind)
        expected = ({"tic_id", *CUTS} if kind == "catalog" else
                    {"tic_id", "observation_id", "sector"} if kind == "observations"
                    else PRODUCT_KEYS)
        require(type(request["projection"]) is list and
                len(request["projection"]) == len(expected) and
                set(request["projection"]) == expected, "REQUEST_PROJECTION", kind)
    order = config["release_order"]
    require(type(order) is dict, "RELEASE_MAPPING_MISSING", "release_order")
    exact_keys(order, {"policy", "version", "evidence", "ranks"}, "release_order")
    require(order["policy"] == "explicit-rank-v1" and nonempty(order["version"])
            and nonempty(order["evidence"]), "RELEASE_MAPPING_UNSUPPORTED", "release_order")
    ranks = order["ranks"]
    require(type(ranks) is dict and bool(ranks) and
            all(nonempty(k) and type(v) is int for k, v in ranks.items()) and
            len(set(ranks.values())) == len(ranks),
            "RELEASE_MAPPING_UNSUPPORTED", "release_order")
    return set(excluded), ranks


def read_dataset(dataset, kind, tic_id, env, config, receipt):
    where = kind + (":" + tic_id if tic_id else "")
    if dataset is None:
        raise Invalid("LOOKUP_MISSING", where, "PENDING")
    exact_keys(dataset, {"state", "reason", "snapshot_id", "snapshot_evidence", "pages"}, where)
    state = dataset["state"]
    require(state in {"complete", "pending", "failed"}, "DATASET_STATE", where)
    if state != "complete":
        require(nonempty(dataset["reason"]), "MISSING_FAILURE_REASON", where)
        raise Invalid("LOOKUP_" + state.upper(), where, state.upper())
    expected_snapshot = env["catalog_snapshot_id" if kind == "catalog" else "inventory_snapshot_id"]
    require(dataset["snapshot_id"] == expected_snapshot and nonempty(dataset["snapshot_evidence"]),
            "SNAPSHOT_UNRESOLVED", where)
    pages = dataset["pages"]
    require(type(pages) is list, "SCHEMA_KEYS", where)
    require(bool(pages), "PAGES_MISSING", where, "PENDING")
    decoded = {}
    page_receipts = []
    for page in pages:
        exact_keys(page, {"raw_json", "sha256", "byte_length", "retrieved_at"}, where)
        require(type(page["raw_json"]) is str, "RAW_BYTES_MISSING", where)
        raw = page["raw_json"].encode("utf-8")
        require(type(page["byte_length"]) is int and page["byte_length"] == len(raw)
                and page["sha256"] == hashlib.sha256(raw).hexdigest(), "RAW_HASH_MISMATCH", where)
        at = timestamp(page["retrieved_at"], where)
        require(timestamp(env["retrieval_started_at"], where) <= at <=
                timestamp(env["retrieval_finished_at"], where), "PAGE_TIME_OUTSIDE_BATCH", where)
        body = strict_json(page["raw_json"], where)
        exact_keys(body, PAGE_KEYS, where)
        expected = {"batch_id": env["batch_id"], "dataset": kind, "tic_id": tic_id,
                    "request_sha256": content_digest(config["requests"][kind]),
                    "schema_id": SCHEMAS[kind], "catalog_version": config["catalog_version"],
                    "snapshot_id": expected_snapshot, "availability_cutoff": env["availability_cutoff"]}
        require(all(body[k] == v for k, v in expected.items()), "PAGE_IDENTITY_MISMATCH", where)
        require(type(body["http_status"]) is int and body["http_status"] == 200,
                "PAGE_HTTP_FAILURE", where)
        require(body["overflow"] is False and body["error"] is None,
                "PAGE_ERROR_OR_OVERFLOW", where)
        index = body["index"]
        require(type(index) is int and index >= 0 and index not in decoded,
                "PAGE_INDEX_DUPLICATE_OR_INVALID", where)
        require(type(body["rows"]) is list and type(body["row_count"]) is int
                and body["row_count"] == len(body["rows"]), "ROW_COUNT_MISMATCH", where)
        require(type(body["total_rows"]) is int and body["total_rows"] >= 0,
                "TOTAL_ROWS_INVALID", where)
        require(type(body["terminal"]) is bool, "TERMINAL_INVALID", where)
        require(body["next_index"] is None if body["terminal"] else
                type(body["next_index"]) is int and body["next_index"] == index + 1,
                "PAGE_LINK_INVALID", where)
        decoded[index] = body
        page_receipts.append({"index": index, "sha256": page["sha256"],
                              "byte_length": len(raw), "retrieved_at": page["retrieved_at"]})
    indices = sorted(decoded)
    require(indices == list(range(len(decoded))), "PAGE_GAP", where, "PENDING")
    ordered = [decoded[i] for i in indices]
    require(not any(p["terminal"] for p in ordered[:-1]), "EARLY_TERMINAL", where)
    require(ordered[-1]["terminal"], "TERMINAL_MISSING", where, "PENDING")
    total = sum(p["row_count"] for p in ordered)
    require(all(p["total_rows"] == total for p in ordered), "TOTAL_ROWS_MISMATCH", where)
    receipt["datasets"][where] = {"raw_rows": total, "snapshot_id": expected_snapshot,
                                  "snapshot_evidence": dataset["snapshot_evidence"],
                                  "pages": sorted(page_receipts, key=lambda p: p["index"])}
    return [row for page in ordered for row in page["rows"]]


def normalize_catalog(rows, receipt):
    groups = defaultdict(list)
    for index, row in enumerate(rows):
        exact_keys(row, {"tic_id", *CUTS}, "catalog.row:" + str(index))
        tic = canonical_id(row["tic_id"], "catalog.row:" + str(index))
        receipt["id_normalizations"].append({"raw_tic_id": row["tic_id"], "tic_id": tic,
                                              "decoded_row_index": index})
        normalized = {"tic_id": tic}
        for key in CUTS:
            value = row[key]
            require(value is None or (type(value) in {int, float} and math.isfinite(value)),
                    "CATALOG_VALUE_INVALID", tic + ":" + key)
            normalized[key] = None if value is None else float(value)
        groups[tic].append(normalized)
    receipt["catalog_records"] = sorted((r for rs in groups.values() for r in rs), key=canonical_json)
    receipt["catalog_accounting"] = {"raw_rows": len(rows), "unique_ids": len(groups),
                                      "repeat_id_rows": len(rows) - len(groups)}
    return groups


def resolve_products(tic, observations, products, ranks, receipt):
    obs = {}
    for row in observations:
        exact_keys(row, {"tic_id", "observation_id", "sector"}, tic + ":observation")
        require(canonical_id(row["tic_id"], tic) == tic and nonempty(row["observation_id"])
                and positive_int(row["sector"]), "OBSERVATION_IDENTITY_INVALID", tic)
        previous = obs.setdefault(row["observation_id"], row["sector"])
        require(previous == row["sector"], "OBSERVATION_CONFLICT", tic)
    by_uri, by_sector = {}, defaultdict(list)
    for raw_row in products:
        exact_keys(raw_row, PRODUCT_KEYS, tic + ":product")
        row = deepcopy(raw_row)
        row["tic_id"] = canonical_id(row["tic_id"], tic)
        require(row["tic_id"] == tic and positive_int(row["sector"]) and
                row["observation_id"] in obs and obs[row["observation_id"]] == row["sector"],
                "PRODUCT_OBSERVATION_MISMATCH", tic)
        require(all(nonempty(row[k]) for k in ("mission", "pipeline", "kind", "uri"))
                and positive_int(row["cadence_seconds"]), "PRODUCT_CLASSIFICATION_UNRESOLVED", tic)
        # This narrow wire contract cannot certify unfamiliar classification labels.
        # A future adapter must explicitly extend its schema, never silently skip them.
        require((row["mission"], row["pipeline"], row["kind"]) == ("TESS", "SPOC", "lightcurve"),
                "PRODUCT_CLASSIFICATION_UNSUPPORTED", tic)
        require(row["advertised_sha256"] is None or
                (type(row["advertised_sha256"]) is str and
                 re.fullmatch(r"[0-9a-f]{64}", row["advertised_sha256"]) is not None),
                "PRODUCT_HASH_INVALID", tic)
        if row["uri"] in by_uri:
            require(by_uri[row["uri"]] == row, "PRODUCT_IDENTITY_CONFLICT", tic)
            continue
        by_uri[row["uri"]] = row
        if row["cadence_seconds"] != 120:
            continue
        require(type(row["release"]) is str and row["release"] in ranks,
                "RELEASE_UNMAPPED", tic)
        require(nonempty(row["pipeline_version"]) and nonempty(row["time_system"]),
                "PRODUCT_TIMING_OR_PIPELINE_UNRESOLVED", tic)
        by_sector[row["sector"]].append(row)
    receipt["product_contenders"][tic] = sorted(by_uri.values(), key=canonical_json)
    return {sector: min(options, key=lambda p: (-ranks[p["release"]], p["uri"].encode("utf-8")))
            for sector, options in sorted(by_sector.items())}


def validate_metadata_batch(envelope, frozen_config):
    """Return JSON-compatible READY/PENDING/FAILED; never emit a partial sample."""
    issues, selection = [], None
    receipt = {"basis": "offline supplied evidence only", "diagnostics_provisional": True,
               "datasets": {}, "catalog_records": [], "id_normalizations": [], "product_contenders": {},
               "exclusions": [], "input_sha256": None, "config_sha256": None}

    def note(error):
        issues.append({"status": error.status, "code": error.code, "where": error.where})

    try:
        receipt["input_sha256"] = content_digest(envelope)
        receipt["config_sha256"] = content_digest(frozen_config)
        excluded, ranks = validate_config(frozen_config)
        receipt["release_order"] = deepcopy(frozen_config["release_order"])
        receipt["release_order_sha256"] = content_digest(frozen_config["release_order"])
        exact_keys(envelope, ENVELOPE_KEYS, "envelope")
        require(nonempty(envelope["batch_id"]) and type(envelope["synthetic"]) is bool,
                "ENVELOPE_IDENTITY", "envelope")
        require(all(nonempty(envelope[k]) for k in ("catalog_snapshot_id", "inventory_snapshot_id")),
                "SNAPSHOT_UNRESOLVED", "envelope")
        start = timestamp(envelope["retrieval_started_at"], "start")
        end = timestamp(envelope["retrieval_finished_at"], "end")
        require(timestamp(frozen_config["frozen_at"], "freeze") < start <= end,
                "CONFIG_NOT_PREFROZEN", "envelope")
        require(timestamp(envelope["availability_cutoff"], "cutoff") <= start,
                "CUTOFF_AFTER_START", "envelope")
        receipt["provenance"] = {k: deepcopy(envelope[k]) for k in ENVELOPE_KEYS
                                 if k not in {"catalog", "observations", "products"}}
        receipt["provenance"].update(catalog_name="TIC", catalog_version="8.2")
        groups = normalize_catalog(read_dataset(envelope["catalog"], "catalog", None,
                                                 envelope, frozen_config, receipt), receipt)
        for kind in ("observations", "products"):
            require(type(envelope[kind]) is dict, "INVENTORY_MAP_INVALID", kind)
            require(all(type(key) is str and canonical_id(key, kind) == key and key in groups
                        for key in envelope[kind]), "UNKNOWN_INVENTORY_HOST", kind)
        eligible, resolved = [], {}
        for tic in sorted(groups, key=int):
            rows = groups[tic]
            reasons = []
            if len({canonical_json(row) for row in rows}) > 1:
                reasons.append("CONFLICTING_CATALOG_DUPLICATE")
            if tic in excluded:
                reasons.append("FROZEN_EXCLUSION")
            if not reasons:
                for field, (low, high) in CUTS.items():
                    value = rows[0][field]
                    if value is None:
                        reasons.append("MISSING_" + field)
                    elif not low <= value <= high:
                        reasons.append("CUT_" + field)
            if reasons:
                receipt["exclusions"].append({"tic_id": tic, "reasons": sorted(reasons),
                                              "product_lookup": "not_required"})
                continue
            datasets = {}
            for kind in ("observations", "products"):
                try:
                    datasets[kind] = read_dataset(envelope[kind].get(tic), kind, tic,
                                                   envelope, frozen_config, receipt)
                except Invalid as error:
                    note(error)
            if len(datasets) != 2:
                continue
            try:
                products = resolve_products(tic, datasets["observations"], datasets["products"],
                                            ranks, receipt)
            except Invalid as error:
                note(error)
                continue
            if len(products) < 3:
                receipt["exclusions"].append({"tic_id": tic, "reasons": ["FEWER_THAN_THREE_SECTORS"],
                                              "product_lookup": "complete", "sectors": list(products)})
            else:
                eligible.append(tic)
                resolved[tic] = products
        if not issues:
            ordered = sorted(eligible, key=lambda tic: (tic_hash(tic), int(tic)))
            selected = ordered[:20]
            assignments = {}
            for tic in selected:
                sectors = sorted(resolved[tic])
                assignments[tic] = {"discovery": [resolved[tic][s] for s in sectors[:2]],
                                    "holdout": resolved[tic][sectors[-1]],
                                    "unused_sectors": sectors[2:-1]}
            selection = {"eligible_order": ordered, "pool_size": len(ordered),
                         "selected_ids": selected, "assignments": assignments,
                         "exclusions": receipt["exclusions"]}
            selection["sample_sha256"] = content_digest(selection)
            receipt["diagnostics_provisional"] = False
    except Invalid as error:
        note(error)
    except (ValueError, TypeError, OverflowError, KeyError):
        note(Invalid("MALFORMED_INPUT", "envelope_or_config"))
    status = ("FAILED" if any(i["status"] == "FAILED" for i in issues)
              else "PENDING" if issues else "READY")
    return {"status": status, "reason_codes": sorted({i["code"] for i in issues}),
            "issues": sorted(issues, key=lambda i: (i["where"], i["code"], i["status"])),
            "receipt": receipt, "selection": selection if status == "READY" else None}


def record_acquisition_failures(selection, failures):
    """Annotate an already fixed sample; never replace a host, sector or URI."""
    unsigned = {k: v for k, v in selection.items() if k != "sample_sha256"}
    require(selection.get("sample_sha256") == content_digest(unsigned),
            "SELECTION_DIGEST_MISMATCH", "selection")
    require(type(failures) is list, "FAILURES_INVALID", "failures")
    for failure in failures:
        exact_keys(failure, {"tic_id", "uri", "reason"}, "failure")
        tic = canonical_id(failure["tic_id"], "failure")
        require(tic in selection["assignments"] and nonempty(failure["reason"]),
                "FAILURE_HOST_INVALID", tic)
        assignment = selection["assignments"][tic]
        uris = {p["uri"] for p in assignment["discovery"] + [assignment["holdout"]]}
        require(failure["uri"] in uris, "FAILURE_URI_INVALID", tic)
    return {"selection": deepcopy(selection), "acquisition_failures": sorted(deepcopy(failures), key=canonical_json)}
