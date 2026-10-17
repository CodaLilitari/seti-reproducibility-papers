"""Eight synthetic offline acceptance cases; no network or numerical workers.

make_fixture() is the complete accepted envelope example. Raw pages contain a
deliberately normalized *synthetic wire format*, not alleged MAST responses.
Run only when the coordinator schedules it: python -m unittest -v test_metadata_contract
"""

from copy import deepcopy
import hashlib
import json
import unittest
from unittest.mock import patch

import metadata_contract as contract


START = "2026-10-08T12:00:00Z"
END = "2026-10-08T12:10:00Z"


def raw_page(body, at="2026-10-08T12:01:00Z"):
    raw = json.dumps(body, sort_keys=True, separators=(",", ":"), allow_nan=False)
    data = raw.encode("utf-8")
    return {"raw_json": raw, "sha256": hashlib.sha256(data).hexdigest(),
            "byte_length": len(data), "retrieved_at": at}


def make_dataset(env, config, kind, tic_id, rows, page_size=2):
    chunks = [rows[i:i + page_size] for i in range(0, len(rows), page_size)] or [[]]
    snapshot = env["catalog_snapshot_id" if kind == "catalog" else "inventory_snapshot_id"]
    pages = []
    for index, chunk in enumerate(chunks):
        terminal = index == len(chunks) - 1
        pages.append(raw_page({
            "batch_id": env["batch_id"], "dataset": kind, "tic_id": tic_id,
            "request_sha256": contract.content_digest(config["requests"][kind]),
            "schema_id": contract.SCHEMAS[kind], "catalog_version": "8.2",
            "snapshot_id": snapshot, "availability_cutoff": env["availability_cutoff"],
            "index": index, "next_index": None if terminal else index + 1,
            "terminal": terminal, "total_rows": len(rows), "row_count": len(chunk),
            "http_status": 200, "overflow": False, "error": None, "rows": chunk,
        }))
    return {"state": "complete", "reason": None, "snapshot_id": snapshot,
            "snapshot_evidence": "SYNTHETIC fixed snapshot fixture; no remote claim", "pages": pages}


def rows_of(dataset):
    return [row for page in sorted((json.loads(p["raw_json"]) for p in dataset["pages"]),
                                  key=lambda p: p["index"]) for row in page["rows"]]


def change_page(dataset, index, mutate):
    body = json.loads(dataset["pages"][index]["raw_json"])
    mutate(body)
    dataset["pages"][index] = raw_page(body)


def replace_rows(env, config, kind, tic_id, rows):
    replacement = make_dataset(env, config, kind, tic_id, rows)
    if kind == "catalog":
        env[kind] = replacement
    else:
        env[kind][tic_id] = replacement


def make_fixture(ids=("1", "2", "3")):
    """Return a complete, deliberately small accepted (envelope, config) pair."""
    config = {
        "contract_version": "offline-metadata-v1", "frozen_at": "2026-10-08T11:00:00Z",
        "catalog_name": "TIC", "catalog_version": "8.2", "pagination": "indexed-total-v1",
        "consistency": "explicit-snapshot-ids-v1", "missing_policy": "null-only",
        "id_policy": "positive-exact-canonical-v1", "cuts": deepcopy(contract.CUTS),
        "units": deepcopy(contract.UNITS), "sample_size": 20,
        "excluded_tic_ids": sorted(contract.REQUIRED_EXCLUSIONS, key=int),
        "release_order": {"policy": "explicit-rank-v1", "version": "synthetic-1",
                          "evidence": "SYNTHETIC declared r1 < r2; not a real product-release mapping",
                          "ranks": {"r1": 1, "r2": 2}},
        "requests": {},
    }
    for kind, projection in (
            ("catalog", {"tic_id", *contract.CUTS}),
            ("observations", {"tic_id", "observation_id", "sector"}),
            ("products", contract.PRODUCT_KEYS)):
        config["requests"][kind] = {
            "endpoint": "fixture://" + kind, "parameters": {"scope": "synthetic-fixed-universe"},
            "projection": sorted(projection), "protocol_evidence": "SYNTHETIC indexed-total-v1",
        }
    env = {
        "batch_id": "synthetic-batch-1", "synthetic": True,
        "retrieval_started_at": START, "retrieval_finished_at": END,
        "availability_cutoff": START, "catalog_snapshot_id": "synthetic-catalog-snapshot",
        "inventory_snapshot_id": "synthetic-inventory-snapshot",
        "catalog": None, "observations": {}, "products": {},
    }
    catalog_rows = []
    for tic in ids:
        catalog_rows.append({"tic_id": tic, "Tmag": 10, "Teff": 4000,
                             "rad": 0.5, "logg": 4.6, "d": 20})
        observations, products = [], []
        for sector in (4, 5, 30):
            obs_id = f"synthetic-{tic}-{sector}"
            observations.append({"tic_id": tic, "observation_id": obs_id, "sector": sector})
            products.append({
                "tic_id": tic, "observation_id": obs_id, "sector": sector, "mission": "TESS",
                "pipeline": "SPOC", "cadence_seconds": 120, "kind": "lightcurve",
                "release": "r1", "uri": f"fixture://{tic}/s{sector}/z.fits",
                "pipeline_version": "synthetic-pipeline-1", "time_system": "synthetic-BTJD",
                "advertised_sha256": None,
            })
        env["observations"][tic] = make_dataset(env, config, "observations", tic, observations)
        env["products"][tic] = make_dataset(env, config, "products", tic, products)
    env["catalog"] = make_dataset(env, config, "catalog", None, catalog_rows)
    return env, config


class MetadataContractTests(unittest.TestCase):
    def assert_blocked(self, result, status=None, code=None):
        self.assertIn(result["status"], ("PENDING", "FAILED"))
        self.assertIsNone(result["selection"])
        self.assertTrue(result["receipt"]["diagnostics_provisional"])
        if status:
            self.assertEqual(result["status"], status)
        if code:
            self.assertIn(code, result["reason_codes"])

    def test_1_order_independence_and_provenance(self):
        env, config = make_fixture()
        rows = rows_of(env["catalog"])
        rows.append(deepcopy(rows[0]))
        replace_rows(env, config, "catalog", None, rows)
        before_inputs = deepcopy((env, config))
        expected = contract.validate_metadata_batch(env, config)
        self.assertEqual(expected["status"], "READY")
        permuted = deepcopy(env)
        for dataset in [permuted["catalog"], *permuted["observations"].values(),
                        *permuted["products"].values()]:
            for i in range(len(dataset["pages"])):
                change_page(dataset, i, lambda p: p["rows"].reverse())
                dataset["pages"][i]["retrieved_at"] = "2026-10-08T12:02:00Z"
            dataset["pages"].reverse()
        for kind in ("observations", "products"):
            permuted[kind] = dict(reversed(list(permuted[kind].items())))
        actual = contract.validate_metadata_batch(permuted, config)
        self.assertEqual(actual["selection"], expected["selection"])
        self.assertNotEqual(actual["receipt"]["input_sha256"], expected["receipt"]["input_sha256"])
        self.assertEqual(expected["receipt"]["catalog_accounting"],
                         {"raw_rows": 4, "unique_ids": 3, "repeat_id_rows": 1})
        self.assertEqual((env, config), before_inputs)
        self.assertEqual(actual["receipt"]["provenance"]["catalog_version"], "8.2")
        self.assertEqual(actual["receipt"]["provenance"]["retrieval_started_at"], START)

    def test_2_missing_distance_vs_incomplete_or_forged_normalization(self):
        env, config = make_fixture(("1",))
        change_page(env["catalog"], 0, lambda p: p["rows"][0].update(d=None))
        result = contract.validate_metadata_batch(env, config)
        self.assertEqual(result["status"], "READY")
        self.assertEqual(result["selection"]["selected_ids"], [])
        self.assertIn("MISSING_d", result["selection"]["exclusions"][0]["reasons"])
        malformed = deepcopy(env)
        change_page(malformed["catalog"], 0, lambda p: p["rows"][0].pop("d"))
        self.assert_blocked(contract.validate_metadata_batch(malformed, config), "FAILED", "SCHEMA_KEYS")
        missing_page = deepcopy(env)
        missing_page["catalog"]["pages"] = []
        self.assert_blocked(contract.validate_metadata_batch(missing_page, config), "PENDING")
        wrong_projection = deepcopy(config)
        wrong_projection["requests"]["catalog"]["projection"].remove("d")
        self.assert_blocked(contract.validate_metadata_batch(env, wrong_projection), "FAILED", "REQUEST_PROJECTION")
        raw_outside, config = make_fixture(("1",))
        change_page(raw_outside["catalog"], 0, lambda p: p["rows"][0].update(d=200))
        self.assertEqual(contract.validate_metadata_batch(raw_outside, config)["selection"]["selected_ids"], [])
        # Counterexample: contradictory supplied typed data must never override raw d=200.
        forged = deepcopy(raw_outside)
        forged["normalized_records"] = [{"tic_id": "1", "d": 20}]
        self.assert_blocked(contract.validate_metadata_batch(forged, config), "FAILED", "SCHEMA_KEYS")
        tampered = deepcopy(raw_outside)
        tampered["catalog"]["pages"][0]["raw_json"] = tampered["catalog"]["pages"][0]["raw_json"].replace('"d":200', '"d":20')
        self.assert_blocked(contract.validate_metadata_batch(tampered, config), "FAILED", "RAW_HASH_MISMATCH")

    def test_3_complete_two_sectors_vs_unfinished_inventory(self):
        env, config = make_fixture(("1", "2"))
        products = rows_of(env["products"]["1"])
        replace_rows(env, config, "products", "1", products[:2])
        complete = contract.validate_metadata_batch(env, config)
        self.assertEqual(complete["status"], "READY")
        self.assertEqual(complete["selection"]["selected_ids"], ["2"])
        self.assertEqual(complete["selection"]["exclusions"][0]["reasons"], ["FEWER_THAN_THREE_SECTORS"])
        replace_rows(env, config, "products", "1", products)
        env["products"]["1"]["pages"].pop()
        self.assert_blocked(contract.validate_metadata_batch(env, config), "PENDING", "TERMINAL_MISSING")
        env["products"]["1"].update(state="failed", reason="synthetic terminal lookup failure")
        self.assert_blocked(contract.validate_metadata_batch(env, config), "FAILED", "LOOKUP_FAILED")

    def test_4_exact_ids_and_forced_hash_tie(self):
        ids = ("9007199254740993", "10", "2", "9007199254740992")
        env, config = make_fixture(ids)
        self.assertEqual(contract.tic_hash(ids[0]), hashlib.sha256(b"coda-tess-v1|9007199254740993").digest())
        with patch.object(contract, "tic_hash", return_value=b"\0" * 32):
            tied = contract.validate_metadata_batch(env, config)
        self.assertEqual(tied["status"], "READY")
        self.assertEqual(tied["selection"]["eligible_order"], ["2", "10", "9007199254740992", "9007199254740993"])
        for invalid in (True, 0, -1, 2.0, 2.5, float(9007199254740993), "02", "2e0", "0", "-2"):
            with self.subTest(invalid=invalid):
                bad, cfg = make_fixture(("1",))
                change_page(bad["catalog"], 0, lambda p: p["rows"][0].update(tic_id=invalid))
                self.assert_blocked(contract.validate_metadata_batch(bad, cfg), "FAILED", "INVALID_TIC_ID")
        integer, cfg = make_fixture(("9007199254740993",))
        change_page(integer["catalog"], 0, lambda p: p["rows"][0].update(tic_id=9007199254740993))
        self.assertEqual(contract.validate_metadata_batch(integer, cfg)["status"], "READY")

    def test_5_duplicates_and_page_failures_do_not_become_exclusions(self):
        env, config = make_fixture(("1", "2"))
        rows = rows_of(env["catalog"])
        rows.append(deepcopy(rows[0]))
        replace_rows(env, config, "catalog", None, rows)
        self.assertEqual(contract.validate_metadata_batch(env, config)["selection"]["pool_size"], 2)
        rows[-1]["d"] = 21
        replace_rows(env, config, "catalog", None, rows)
        conflicting = contract.validate_metadata_batch(env, config)
        self.assertEqual(conflicting["status"], "READY")
        self.assertEqual(conflicting["selection"]["selected_ids"], ["2"])
        self.assertIn("CONFLICTING_CATALOG_DUPLICATE", conflicting["selection"]["exclusions"][0]["reasons"])
        gap = deepcopy(env)
        gap["catalog"]["pages"].pop(0)
        self.assert_blocked(contract.validate_metadata_batch(gap, config), "PENDING", "PAGE_GAP")
        changes = [("loop", lambda p: p.update(next_index=0)),
                   ("total", lambda p: p.update(total_rows=999)),
                   ("overflow", lambda p: p.update(overflow=True)),
                   ("schema", lambda p: p.update(schema_id="other-schema")),
                   ("version", lambda p: p.update(catalog_version="8.1")),
                   ("snapshot", lambda p: p.update(snapshot_id="other-snapshot"))]
        for label, mutation in changes:
            with self.subTest(label=label):
                bad = deepcopy(env)
                change_page(bad["catalog"], 0, mutation)
                self.assert_blocked(contract.validate_metadata_batch(bad, config), "FAILED")
        duplicate = deepcopy(env)
        duplicate["catalog"]["pages"].append(deepcopy(duplicate["catalog"]["pages"][0]))
        self.assert_blocked(contract.validate_metadata_batch(duplicate, config), "FAILED", "PAGE_INDEX_DUPLICATE_OR_INVALID")

    def test_6_release_mapping_and_uri_ties(self):
        env, config = make_fixture(("1",))
        products = rows_of(env["products"]["1"])
        earlier = deepcopy(products[0])
        earlier.update(release="r2", uri="fixture://1/s4/a.fits")
        later = deepcopy(earlier)
        later["uri"] = "fixture://1/s4/b.fits"
        replace_rows(env, config, "products", "1", [later, *products, earlier])
        baseline = contract.validate_metadata_batch(env, config)
        self.assertEqual(baseline["status"], "READY")
        self.assertEqual(baseline["selection"]["assignments"]["1"]["discovery"][0]["uri"], earlier["uri"])
        replace_rows(env, config, "products", "1", [earlier, *reversed(products), later])
        self.assertEqual(contract.validate_metadata_batch(env, config)["selection"], baseline["selection"])
        unknown = deepcopy(products[0])
        unknown.update(release="r-new", uri="fixture://1/s4/new.fits")
        replace_rows(env, config, "products", "1", [*products, unknown])
        self.assert_blocked(contract.validate_metadata_batch(env, config), "FAILED", "RELEASE_UNMAPPED")
        conflict = deepcopy(products[0])
        conflict["pipeline_version"] = "contradictory-version"
        replace_rows(env, config, "products", "1", [*products, conflict])
        self.assert_blocked(contract.validate_metadata_batch(env, config), "FAILED", "PRODUCT_IDENTITY_CONFLICT")
        for replacement, code in ((None, "RELEASE_MAPPING_MISSING"),
                                  ({**config["release_order"], "policy": "guess-semver"}, "RELEASE_MAPPING_UNSUPPORTED")):
            bad_config = deepcopy(config)
            bad_config["release_order"] = replacement
            self.assert_blocked(contract.validate_metadata_batch(env, bad_config), "FAILED", code)
        bad_config = deepcopy(config)
        bad_config["frozen_at"] = "2026-10-08T12:05:00Z"
        self.assert_blocked(contract.validate_metadata_batch(env, bad_config), "FAILED", "CONFIG_NOT_PREFROZEN")

    def test_7_all_required_hosts_resolve_before_selection(self):
        env, config = make_fixture(tuple(str(i) for i in range(1, 22)))
        complete = contract.validate_metadata_batch(env, config)
        self.assertEqual(complete["status"], "READY")
        self.assertEqual(len(complete["selection"]["selected_ids"]), 20)
        del env["products"]["21"]
        self.assert_blocked(contract.validate_metadata_batch(env, config), "PENDING", "LOOKUP_MISSING")
        config["excluded_tic_ids"].append("21")
        del env["observations"]["21"]
        rows = rows_of(env["catalog"])
        next(row for row in rows if row["tic_id"] == "20")["Tmag"] = 14
        replace_rows(env, config, "catalog", None, rows)
        del env["observations"]["20"]
        del env["products"]["20"]
        result = contract.validate_metadata_batch(env, config)
        self.assertEqual(result["status"], "READY")
        self.assertEqual(result["selection"]["pool_size"], 19)
        self.assertEqual({r["tic_id"] for r in result["selection"]["exclusions"]}, {"20", "21"})
        self.assertTrue(all(r["product_lookup"] == "not_required" for r in result["selection"]["exclusions"]))

    def test_8_no_skip_backfill_and_later_failures_preserve_sample(self):
        env, config = make_fixture(tuple(str(i) for i in range(1, 22)))
        result = contract.validate_metadata_batch(env, config)
        self.assertEqual(result["status"], "READY")
        selection = result["selection"]
        frozen = deepcopy(selection)
        tic = selection["selected_ids"][0]
        uri = selection["assignments"][tic]["holdout"]["uri"]
        annotated = contract.record_acquisition_failures(selection, [
            {"tic_id": tic, "uri": uri, "reason": "synthetic FITS integrity failure"}])
        self.assertEqual(annotated["selection"], frozen)
        self.assertEqual(selection, frozen)
        self.assertEqual(len(annotated["selection"]["selected_ids"]), 20)
        outsider = next(t for t in selection["eligible_order"] if t not in selection["selected_ids"])
        self.assertNotIn(outsider, annotated["selection"]["selected_ids"])
        with self.assertRaises(contract.Invalid):
            contract.record_acquisition_failures(selection, [{"tic_id": outsider, "uri": uri, "reason": "bad"}])
        for flag in ("skip_failures", "fill_to_20", "best_available"):
            bad = deepcopy(config)
            bad[flag] = True
            self.assert_blocked(contract.validate_metadata_batch(env, bad), "FAILED", "SCHEMA_KEYS")
        smaller = deepcopy(config)
        smaller["sample_size"] = 1
        self.assert_blocked(contract.validate_metadata_batch(env, smaller), "FAILED", "UNSUPPORTED_CONFIG")


if __name__ == "__main__":
    unittest.main()
