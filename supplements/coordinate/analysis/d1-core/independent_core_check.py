#!/usr/bin/env python3
"""Independent core arithmetic check of Red's astrometric-provenance audit.

This implementation was written after receiving Red's archive. It does not import
Red's Python modules or result files. Inputs are fresh Gaia/SIMBAD query snapshots
and values manually transcribed from the primary PDFs.
"""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from statistics import NormalDist, mean

ROOT = Path(__file__).resolve().parent
ARCSEC_PER_RAD = 206264.80624709636


def parse_ra_hms(s: str) -> float:
    h, m, sec = map(float, s.split())
    return 15.0 * (h + m / 60.0 + sec / 3600.0)


def parse_dec_dms(s: str) -> float:
    parts = s.split()
    sign = -1.0 if parts[0].startswith("-") else 1.0
    d = abs(float(parts[0]))
    m = float(parts[1])
    sec = float(parts[2])
    return sign * (d + m / 60.0 + sec / 3600.0)


def propagate(ra_deg: float, dec_deg: float, pmra_masyr: float, pmdec_masyr: float,
              ref_epoch: float, target_epoch: float) -> tuple[float, float]:
    """First-order Gaia tangent-plane proper-motion propagation.

    Gaia pmra is mu_alpha* = d(alpha)/dt cos(delta).
    This is adequate here; motions are <1.5 arcsec across the tested interval.
    """
    dt = target_epoch - ref_epoch
    c = math.cos(math.radians(dec_deg))
    if abs(c) < 1e-12:
        raise ValueError("cos(dec) too small")
    ra = ra_deg + dt * pmra_masyr / (3_600_000.0 * c)
    dec = dec_deg + dt * pmdec_masyr / 3_600_000.0
    return ra % 360.0, dec


def separation_arcsec(ra1: float, dec1: float, ra2: float, dec2: float) -> float:
    """Stable great-circle separation using atan2(cross,dot)."""
    a1, d1, a2, d2 = map(math.radians, (ra1, dec1, ra2, dec2))
    u = (math.cos(d1) * math.cos(a1), math.cos(d1) * math.sin(a1), math.sin(d1))
    v = (math.cos(d2) * math.cos(a2), math.cos(d2) * math.sin(a2), math.sin(d2))
    cross = (
        u[1] * v[2] - u[2] * v[1],
        u[2] * v[0] - u[0] * v[2],
        u[0] * v[1] - u[1] * v[0],
    )
    cross_norm = math.sqrt(sum(x * x for x in cross))
    dot = sum(x * y for x, y in zip(u, v))
    return math.atan2(cross_norm, dot) * ARCSEC_PER_RAD


def rms(values: list[float]) -> float:
    return math.sqrt(sum(v * v for v in values) / len(values))


def golden_minimize(func, lo: float, hi: float, iterations: int = 100) -> tuple[float, float]:
    phi = (1.0 + math.sqrt(5.0)) / 2.0
    invphi = 1.0 / phi
    c = hi - (hi - lo) * invphi
    d = lo + (hi - lo) * invphi
    fc, fd = func(c), func(d)
    for _ in range(iterations):
        if fc < fd:
            hi, d, fd = d, c, fc
            c = hi - (hi - lo) * invphi
            fc = func(c)
        else:
            lo, c, fc = c, d, fd
            d = lo + (hi - lo) * invphi
            fd = func(d)
    x = (lo + hi) / 2.0
    return x, func(x)


def load_gaia() -> dict[str, dict[str, float]]:
    out: dict[str, dict[str, float]] = {}
    with (ROOT / "fresh_gaia_tap_2026-09-27.csv").open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            out[row["source_id"]] = {
                "ra": float(row["ra"]),
                "dec": float(row["dec"]),
                "pmra": float(row["pmra"]),
                "pmdec": float(row["pmdec"]),
                "ref_epoch": float(row["ref_epoch"]),
            }
    return out


def load_simbad() -> dict[str, dict[str, float | str | None]]:
    out: dict[str, dict[str, float | str | None]] = {}
    with (ROOT / "fresh_simbad_tap_2026-09-27.csv").open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            out[row["candidate"]] = {
                "source_id": row["gaia_id"],
                "ra": float(row["ra_j2000_deg"]) if row["ra_j2000_deg"] else None,
                "dec": float(row["dec_j2000_deg"]) if row["dec_j2000_deg"] else None,
                "status": row["query_result"],
            }
    return out


def main() -> None:
    gaia = load_gaia()
    simbad = load_simbad()
    primary = json.loads((ROOT / "primary_values.json").read_text(encoding="utf-8"))

    rowwise: list[dict[str, object]] = []
    group_summaries: dict[str, dict[str, float | int]] = {}
    free_fits: list[dict[str, object]] = []
    corrected_offsets: dict[tuple[str, str], float] = {}

    for branch_name, groups in (("WISE", primary["wise"]), ("RADIO", primary["radio_2026"])):
        branch_resid_stated: list[float] = []
        branch_resid_m16: list[float] = []
        for cand, obj in groups.items():
            g = gaia[obj["source_id"]]
            rows = obj["rows"]

            def fit_object(shift: float) -> float:
                residuals: list[float] = []
                for band, epoch, ra_s, dec_s, printed in rows:
                    star_ra, star_dec = propagate(g["ra"], g["dec"], g["pmra"], g["pmdec"], g["ref_epoch"], epoch + shift)
                    sep = separation_arcsec(parse_ra_hms(ra_s), parse_dec_dms(dec_s), star_ra, star_dec)
                    residuals.append(sep - printed)
                return rms(residuals)

            best_shift, best_rms = golden_minimize(fit_object, -30.0, 10.0)
            free_fits.append({
                "branch": branch_name,
                "candidate": cand,
                "best_shift_years": best_shift,
                "rms_arcsec": best_rms,
            })

            for band, epoch, ra_s, dec_s, printed in rows:
                cent_ra, cent_dec = parse_ra_hms(ra_s), parse_dec_dms(dec_s)
                star_t = propagate(g["ra"], g["dec"], g["pmra"], g["pmdec"], g["ref_epoch"], epoch)
                star_m16 = propagate(g["ra"], g["dec"], g["pmra"], g["pmdec"], g["ref_epoch"], epoch - 16.0)
                sep_t = separation_arcsec(cent_ra, cent_dec, *star_t)
                sep_m16 = separation_arcsec(cent_ra, cent_dec, *star_m16)
                resid_t = sep_t - printed
                resid_m16 = sep_m16 - printed
                branch_resid_stated.append(resid_t)
                branch_resid_m16.append(resid_m16)
                rowwise.append({
                    "branch": branch_name,
                    "candidate": cand,
                    "band_or_survey": band,
                    "epoch": epoch,
                    "printed_offset_arcsec": printed,
                    "recomputed_at_stated_epoch_arcsec": sep_t,
                    "recomputed_at_epoch_minus_16_arcsec": sep_m16,
                    "residual_stated_arcsec": resid_t,
                    "residual_minus16_arcsec": resid_m16,
                })
                if branch_name == "WISE":
                    corrected_offsets[(cand, band)] = sep_t

        group_summaries[branch_name] = {
            "rows": len(branch_resid_stated),
            "matches_stated_lt_0p05": sum(abs(x) < 0.05 for x in branch_resid_stated),
            "matches_minus16_lt_0p05": sum(abs(x) < 0.05 for x in branch_resid_m16),
            "mae_stated_arcsec": mean(abs(x) for x in branch_resid_stated),
            "mae_minus16_arcsec": mean(abs(x) for x in branch_resid_m16),
            "max_abs_minus16_arcsec": max(abs(x) for x in branch_resid_m16),
        }

    # Separate WISE affected A-F and unaffected H-J summaries.
    wise_rows = [r for r in rowwise if r["branch"] == "WISE"]
    for label, candidates in (("WISE_A_F", set("ABCDEF")), ("WISE_H_J", set("HIJ"))):
        subset = [r for r in wise_rows if r["candidate"] in candidates]
        group_summaries[label] = {
            "rows": len(subset),
            "matches_stated_lt_0p05": sum(abs(float(r["residual_stated_arcsec"])) < 0.05 for r in subset),
            "matches_minus16_lt_0p05": sum(abs(float(r["residual_minus16_arcsec"])) < 0.05 for r in subset),
            "mae_stated_arcsec": mean(abs(float(r["residual_stated_arcsec"])) for r in subset),
            "mae_minus16_arcsec": mean(abs(float(r["residual_minus16_arcsec"])) for r in subset),
            "max_abs_minus16_arcsec": max(abs(float(r["residual_minus16_arcsec"])) for r in subset),
        }

    # Fresh SIMBAD coordinates compared to Gaia propagated to J2000.
    simbad_checks: list[dict[str, object]] = []
    for cand, s in simbad.items():
        if s["ra"] is None:
            simbad_checks.append({"candidate": cand, "status": s["status"], "separation_to_gaia_J2000_arcsec": None})
            continue
        g = gaia[str(s["source_id"])]
        g2000 = propagate(g["ra"], g["dec"], g["pmra"], g["pmdec"], g["ref_epoch"], 2000.0)
        sep = separation_arcsec(float(s["ra"]), float(s["dec"]), *g2000)
        simbad_checks.append({"candidate": cand, "status": s["status"], "separation_to_gaia_J2000_arcsec": sep})

    # Ren 2024: invert radio-minus-star signed components to recover implied star.
    ren2024_checks: list[dict[str, object]] = []
    for cand, survey, ra_s, dec_s, east_arcsec, north_arcsec, printed_total in primary["ren2024"]:
        radio_ra, radio_dec = parse_ra_hms(ra_s), parse_dec_dms(dec_s)
        # Components are radio - star, east/north. Invert in local tangent plane.
        star_dec = radio_dec - north_arcsec / 3600.0
        star_ra = (radio_ra - east_arcsec / (3600.0 * math.cos(math.radians(star_dec)))) % 360.0
        s = simbad[cand]
        if s["ra"] is None:
            sep = None
        else:
            sep = separation_arcsec(star_ra, star_dec, float(s["ra"]), float(s["dec"]))
        component_norm = math.hypot(east_arcsec, north_arcsec)
        ren2024_checks.append({
            "candidate": cand,
            "survey": survey,
            "implied_star_ra_deg": star_ra,
            "implied_star_dec_deg": star_dec,
            "separation_to_fresh_SIMBAD_J2000_arcsec": sep,
            "printed_total_arcsec": printed_total,
            "component_norm_arcsec": component_norm,
        })

    # Table 10 fixed-scale conditional arithmetic.
    table10: list[dict[str, object]] = []
    normal = NormalDist()
    for cand, band, published_offset, scale, published_p, published_sigma in primary["table10"]:
        reproduced_p = math.exp(-(published_offset ** 2) / (2.0 * scale ** 2))
        corrected = corrected_offsets[(cand, band)]
        conditional_p = math.exp(-(corrected ** 2) / (2.0 * scale ** 2))
        conditional_sigma = normal.inv_cdf(1.0 - conditional_p)
        table10.append({
            "candidate": cand,
            "band": band,
            "published_offset_arcsec": published_offset,
            "published_scale_arcsec": scale,
            "published_p": published_p,
            "p_from_rounded_published_inputs": reproduced_p,
            "correct_date_offset_arcsec": corrected,
            "conditional_p_fixed_published_scale": conditional_p,
            "conditional_one_sided_sigma": conditional_sigma,
            "published_sigma": published_sigma,
        })

    # Write rowwise outputs.
    with (ROOT / "independent_rowwise.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rowwise[0]))
        w.writeheader(); w.writerows(rowwise)
    with (ROOT / "independent_effective_epoch_fits.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(free_fits[0]))
        w.writeheader(); w.writerows(free_fits)
    with (ROOT / "independent_ren2024_inversion.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(ren2024_checks[0]))
        w.writeheader(); w.writerows(ren2024_checks)
    with (ROOT / "independent_table10_conditional.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(table10[0]))
        w.writeheader(); w.writerows(table10)

    result = {
        "implementation": "Independent standard-library Python; no Red modules or result files imported.",
        "group_summaries": group_summaries,
        "effective_epoch_fits": free_fits,
        "simbad_j2000_checks": simbad_checks,
        "ren2024_inversion": ren2024_checks,
        "table10_conditional": table10,
        "important_limit": "Conditional Table 10 values hold the published Rayleigh scale fixed; controls and estimator were not reprocessed.",
    }
    (ROOT / "independent_core_results.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

    # Assertions are deliberately tied to claims, not exact agreement with Red's files.
    af = group_summaries["WISE_A_F"]
    hj = group_summaries["WISE_H_J"]
    radio = group_summaries["RADIO"]
    assert af["matches_stated_lt_0p05"] == 3
    assert af["matches_minus16_lt_0p05"] == 24
    assert af["mae_minus16_arcsec"] < 0.003
    assert af["max_abs_minus16_arcsec"] < 0.0052
    assert hj["matches_stated_lt_0p05"] == 12
    assert radio["matches_stated_lt_0p05"] == 7
    affected_fits = [float(x["best_shift_years"]) for x in free_fits if x["branch"] == "WISE" and x["candidate"] in set("ABCDEF")]
    assert all(-16.1 < x < -15.7 for x in affected_fits)
    unaffected_fits = [float(x["best_shift_years"]) for x in free_fits if x["branch"] == "WISE" and x["candidate"] in set("HIJ")]
    assert all(-0.5 < x < 0.2 for x in unaffected_fits)
    assert max(float(x["separation_to_gaia_J2000_arcsec"]) for x in simbad_checks if x["separation_to_gaia_J2000_arcsec"] is not None) < 1e-4
    non_tgss = [x for x in ren2024_checks if x["survey"] != "TGSS"]
    assert max(float(x["separation_to_fresh_SIMBAD_J2000_arcsec"]) for x in non_tgss) < 0.001
    tgss = next(x for x in ren2024_checks if x["survey"] == "TGSS")
    assert 0.99 < float(tgss["separation_to_fresh_SIMBAD_J2000_arcsec"]) < 1.01
    print(json.dumps({
        "status": "PASS",
        "WISE_A_F": af,
        "WISE_H_J": hj,
        "RADIO": radio,
        "affected_shift_mean_years": mean(affected_fits),
        "affected_shift_minmax_years": [min(affected_fits), max(affected_fits)],
        "unaffected_shift_mean_years": mean(unaffected_fits),
        "max_fresh_SIMBAD_vs_Gaia_J2000_arcsec": max(float(x["separation_to_gaia_J2000_arcsec"]) for x in simbad_checks if x["separation_to_gaia_J2000_arcsec"] is not None),
        "max_Ren2024_nonTGSS_implied_vs_SIMBAD_arcsec": max(float(x["separation_to_fresh_SIMBAD_J2000_arcsec"]) for x in non_tgss),
        "TGSS_implied_vs_SIMBAD_arcsec": float(tgss["separation_to_fresh_SIMBAD_J2000_arcsec"]),
    }, indent=2))


if __name__ == "__main__":
    main()
