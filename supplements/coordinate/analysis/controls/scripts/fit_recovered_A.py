"""Replay the rounded A-control values printed in Ren v6 Figure A1.

These are published radial offsets, not newly measured or epoch-corrected data.
Run with the audit environment; no network access occurs.
"""
from pathlib import Path
import csv, hashlib, inspect, json, math, platform
import numpy as np
import scipy
from scipy.stats import rayleigh

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'source_archives' / 'A_controls_transcribed.csv'
OUT = ROOT / 'results'
OUT.mkdir(exist_ok=True)
ENV = ROOT / 'environment'
ENV.mkdir(exist_ok=True)
rows = list(csv.DictReader(INPUT.open(encoding='utf-8-sig')))
# Direct transcription: mnras_template.tex Table tab:rayleigh lines 601-604;
# candidate radii are from Table 4, TeX lines 349-352.
PUBLISHED = {
    'w1': (15, .17, .03, 1.60, 4e-19),
    'w2': (15, .21, .04, 1.48, 3e-11),
    'w3': (15, 1.50, .27, 2.16, .355),
    'w4': (9, 3.29, .77, 1.96, .837),
}
result = []
for band, (n, published_scale, published_se, r, p) in PUBLISHED.items():
    x = np.array([float(z[band+'_offset_arcsec']) for z in rows if z[band+'_offset_arcsec']])
    assert len(x) == n
    loc_fixed, scale_fixed = rayleigh.fit(x, floc=0)
    loc_free, scale_free = rayleigh.fit(x, loc=0)
    loc_default, scale_default = rayleigh.fit(x)
    rms_scale = math.sqrt(float(np.dot(x,x))/(2*n))
    assert math.isclose(scale_fixed, rms_scale, rel_tol=1e-14)
    lo, hi = np.maximum(0, x-.005), x+.005
    scale_lo = math.sqrt(float(np.dot(lo,lo))/(2*n))
    scale_hi = math.sqrt(float(np.dot(hi,hi))/(2*n))
    # Monotonic bounds conditional on nearest rounding to 0.01 arcsec.
    p_lo = math.exp(-((r+.005)/scale_lo)**2/2)
    p_hi = math.exp(-((r-.005)/scale_hi)**2/2)
    # Candidate error-rule fingerprint only; this is NOT the Rayleigh MLE SE.
    se = float(scale_fixed)/math.sqrt(2*n)
    result.append(dict(
        band=band.upper(), n=n, displayed_offsets_arcsec=x.tolist(),
        published_scale_arcsec=published_scale, published_scale_error_arcsec=published_se,
        zero_location_mle_scale_arcsec=float(scale_fixed),
        closed_form_rms_scale_arcsec=rms_scale,
        scale_rounds_to_published=round(float(scale_fixed),2)==published_scale,
        scale_bounds_if_nearest_rounding=[scale_lo,scale_hi],
        published_scale_interval=[published_scale-.005,published_scale+.005],
        free_location_fit_from_loc0=dict(loc=float(loc_free),scale=float(scale_free)),
        default_fit=dict(loc=float(loc_default),scale=float(scale_default)),
        median_based_scale_arcsec=float(np.median(x)/math.sqrt(2*math.log(2))),
        candidate_error_rule_sigma_over_sqrt_2N=se,
        candidate_error_rule_rounds_to_published=round(se,2)==published_se,
        rayleigh_mle_asymptotic_se_sigma_over_2sqrtN=float(scale_fixed)/(2*math.sqrt(n)),
        published_candidate_offset_arcsec=r, published_p=p,
        p_using_displayed_controls_and_published_candidate=float(rayleigh.sf(r,loc=0,scale=scale_fixed)),
        p_bounds_if_nearest_rounding=[p_lo,p_hi],
        published_point_p_inside_bound=p_lo<=p<=p_hi,
    ))
payload = dict(
    purpose='Partial replay of published A controls; not corrected probabilities',
    python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,
    input_sha256=hashlib.sha256(INPUT.read_bytes()).hexdigest(),bands=result,
    inference='The recovered rounded A data are compatible with a zero-location MLE for all four scales. The numerical rule sigma/sqrt(2N) matches all four printed error labels, but it is not the usual Rayleigh-MLE asymptotic SE sigma/(2sqrt(N)). This does not identify the actual fit or uncertainty algorithm, software version, or other groups.',
    limitations=['Figure values have 0.01 arcsec display resolution; nearest rounding is assumed only for the conditional intervals.',
                 'Free-location fits use rounded inputs; they are implementation contrasts, not recovered author calls.',
                 'No signed vectors, unrounded centroids, exact per-control image epochs or original extraction settings recovered.',
                 'No control coordinate correction or corrected significance is calculated.'])
(OUT/'A_control_estimator_replay.json').write_text(json.dumps(payload,indent=2)+'\n',encoding='utf-8')
(ENV/'scipy_rayleigh_fit_source.py').write_text(inspect.getsource(type(rayleigh).fit),encoding='utf-8')
print(json.dumps({'bands': [{k:v for k,v in row.items() if k not in ['displayed_offsets_arcsec','default_fit']} for row in result]},indent=2))
