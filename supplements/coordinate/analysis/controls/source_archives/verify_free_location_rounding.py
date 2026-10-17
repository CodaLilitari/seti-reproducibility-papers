"""Exact-rational exclusion of unrestricted Rayleigh fits in printed scale bins.

Assumes each printed control and scale was rounded to nearest 0.01 arcsec.
Does not infer author code or change root's analysis implementation.
"""
from fractions import Fraction as F
from pathlib import Path
import csv
import json

HERE = Path(__file__).resolve().parent
rows = list(csv.DictReader((HERE / "A_controls_transcribed.csv").open()))
scales = {"w1": "0.17", "w2": "0.21", "w3": "1.50", "w4": "3.29"}
results = []

for band, printed in scales.items():
    x = [F(row[band + "_offset_arcsec"]) for row in rows
         if row[band + "_offset_arcsec"]]
    n = len(x)
    lo = [value - F("0.005") for value in x]
    hi = [value + F("0.005") for value in x]
    scale_lo = F(printed) - F("0.005")
    scale_hi = F(printed) + F("0.005")
    proof = []
    maximum_upper_score = None
    for j in range(100):
        a = scale_lo + (scale_hi - scale_lo) * j / 100
        b = scale_lo + (scale_hi - scale_lo) * (j + 1) / 100

        # At a joint MLE, sum((x_i-loc)^2) = 2*N*scale^2.
        # A loc below min(lo) with g(loc)>0 is therefore impossible.
        def g(loc):
            return sum((value - loc) ** 2 for value in lo) - 2 * n * b * b

        left, right = F(-100), min(lo)
        assert g(left) > 0
        if g(right) > 0:
            left = right
        else:
            for _ in range(60):
                mid = (left + right) / 2
                if g(mid) > 0:
                    left = mid
                else:
                    right = mid

        # left is a proved lower bound for every possible MLE location
        # in this scale interval. y_i=x_i-loc <= hi_i-left.
        # h(y,scale)=y/scale^2-1/y increases with y and decreases with scale.
        y_upper = [value - left for value in hi]
        assert min(y_upper) > 0
        score_upper = sum(y / (a * a) - 1 / y for y in y_upper)
        maximum_upper_score = (score_upper if maximum_upper_score is None
                               else max(score_upper, maximum_upper_score))
        proof.append({
            "scale_lo": str(a), "scale_hi": str(b),
            "location_lower_bound": str(left),
            "score_upper_bound": str(score_upper),
            "score_upper_bound_decimal": float(score_upper),
        })
    results.append({
        "band": band.upper(),
        "all_subinterval_score_upper_bounds_negative": all(
            F(item["score_upper_bound"]) < 0 for item in proof),
        "max_score_upper_bound": float(maximum_upper_score),
        "subintervals": proof,
    })

(HERE / "free_location_rounding_exclusion.json").write_text(
    json.dumps(results, indent=2) + "\n", encoding="utf-8")
print(json.dumps([{key: value for key, value in row.items()
                   if key != "subintervals"} for row in results], indent=2))
