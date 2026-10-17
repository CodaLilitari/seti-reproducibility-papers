"""Offline, serial, source-pinned Ren2024 coordinate/covariance sensitivity audit.

No acquisition, image measurement, new targets, counterpart classification, or
calibrated significance claim. See ../review-preflight/math-method.md.
"""
from __future__ import annotations
import csv
import hashlib
import io
import json
import math
import os
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
            'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
    os.environ[key] = '1'
import numpy as np
import astropy
import astropy.units as u
from astropy.coordinates import SkyCoord
from astropy.time import Time
from astropy.utils import iers
iers.conf.auto_download = False

BASE = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
SOURCE = BASE.parent / 'source/Ren2024_Coordinate_State_Followup_2026-10-08'
IDS = {'A': '3496509309189181184', 'B': '4843191593270342656', 'G': '2644370304260053376'}
RAD = 180 / math.pi * 3600
PARAM = ('ra', 'dec', 'parallax', 'pmra', 'pmdec')
INPUTS: dict[str, str] = {}
CHECKS: list[dict] = []

def read(path):
    data = path.read_bytes()
    INPUTS[str(path)] = hashlib.sha256(data).hexdigest()
    return data.decode('utf-8-sig')

def check(name, condition, **details):
    CHECKS.append({'name': name, 'passed': bool(condition), **details})
    if not condition:
        raise AssertionError(name)

def tsv(path):
    lines = [x for x in read(path).splitlines() if x and not x.startswith('#')]
    names = lines[0].split('\t')
    return [dict(zip(names, [v.strip() for v in line.split('\t')])) for line in lines[3:]]

def unit_and_basis(ra, dec):
    a, d = np.deg2rad([ra, dec])
    p = np.array([math.cos(d)*math.cos(a), math.cos(d)*math.sin(a), math.sin(d)])
    east = np.array([-math.sin(a), math.cos(a), 0.])
    north = np.array([-math.sin(d)*math.cos(a), -math.sin(d)*math.sin(a), math.cos(d)])
    return p, east, north

def vector_to_coord(p):
    return SkyCoord(math.degrees(math.atan2(p[1], p[0])) % 360 * u.deg,
                    math.degrees(math.atan2(p[2], math.hypot(p[0], p[1]))) * u.deg, frame='icrs')

def vector_propagate(g, epoch):
    p, e, n = unit_and_basis(float(g['ra']), float(g['dec']))
    tau = epoch - float(g['ref_epoch'])
    p = p + tau * (float(g['pmra']) * e + float(g['pmdec']) * n) / (1000*RAD)
    return vector_to_coord(p)

def astropy_propagate(g, epoch, rv=0.):
    s = SkyCoord(ra=float(g['ra'])*u.deg, dec=float(g['dec'])*u.deg,
                 distance=(1000 / float(g['parallax']))*u.pc,
                 pm_ra_cosdec=float(g['pmra'])*u.mas/u.yr,
                 pm_dec=float(g['pmdec'])*u.mas/u.yr,
                 radial_velocity=rv*u.km/u.s,
                 obstime=Time(float(g['ref_epoch']), format='jyear', scale='tcb'), frame='icrs')
    return s.apply_space_motion(new_obstime=Time(epoch, format='jyear', scale='tcb'))

def residual(star, radio):
    """Spherical logarithm at star: radius equals angular separation exactly."""
    p, e, n = unit_and_basis(star.ra.deg, star.dec.deg)
    r, _, _ = unit_and_basis(radio.ra.deg, radio.dec.deg)
    cr = np.cross(p, r)
    sinth, costh = np.linalg.norm(cr), np.clip(p @ r, -1, 1)
    theta = math.atan2(sinth, costh)
    factor = RAD if sinth < 1e-15 else RAD * theta / sinth
    return np.array([r @ e, r @ n]) * factor

def covariance5(g):
    sig = np.array([float(g[f'{k}_error']) for k in PARAM])
    cor = np.eye(5)
    for i in range(5):
        for j in range(i+1, 5):
            cor[i, j] = cor[j, i] = float(g[f'{PARAM[i]}_{PARAM[j]}_corr'])
    return sig[:, None] * cor * sig[None, :], cor

def propagated_cov(g, epoch):
    c, _ = covariance5(g)
    tau = epoch - float(g['ref_epoch'])
    h = np.array([[1, 0, 0, tau, 0], [0, 1, 0, 0, tau]], dtype=float)
    return h @ c @ h.T / 1e6  # arcsec^2; local linear tangent model

def radio_sigma(ra_error, dec_error, convention, dec):
    scale = {'ra_time_seconds': 15*math.cos(math.radians(dec)),
             'ra_coordinate_degrees': 3600*math.cos(math.radians(dec)),
             'ra_coordinate_arcsec': math.cos(math.radians(dec)),
             'ra_tangent_arcsec': 1.}[convention]
    north_scale = 3600 if convention == 'ra_coordinate_degrees' else 1
    return float(ra_error)*scale, float(dec_error)*north_scale

def rho_profile(r, gaia_cov, sx, sy, floor):
    """Analytic extrema over unknown radio rho in [-1,1], total covariance SPD.

    floor is an independent isotropic additional 1-sigma scenario, not calibration.
    Gaia positive covariance regularizes radio rho=+-1.
    """
    a = gaia_cov[0, 0] + sx*sx + floor*floor
    b = gaia_cov[1, 1] + sy*sy + floor*floor
    gxy, span = gaia_cov[0, 1], sx*sy
    lo, hi = gxy-span, gxy+span
    x, y = r
    k, q = b*x*x+a*y*y, x*y
    choices = [lo, hi, gxy]
    if q == 0:
        choices.append(float(np.clip(0., lo, hi)))
    else:
        disc = max(0., k*k-4*q*q*a*b)
        # Stable smaller root, plus the other root where finite.
        root = 2*q*a*b/(k+math.sqrt(disc)) if k+math.sqrt(disc) else 0.
        choices.extend([root, a*b/root] if root else [0.])
    def d2(c):
        cov = np.array([[a, c], [c, b]])
        return float(r @ np.linalg.solve(cov, r))
    evaluated = [(d2(c), c) for c in choices if lo-1e-15 <= c <= hi+1e-15]
    small, big = min(evaluated), max(evaluated)
    return {'D_rho0': math.sqrt(d2(gxy)), 'D_min_over_radio_rho': math.sqrt(max(0, small[0])),
            'rho_at_min': (small[1]-gxy)/span,
            'D_max_over_radio_rho': math.sqrt(max(0, big[0])),
            'rho_at_max': (big[1]-gxy)/span}

def epoch_from_mjd(mjd):
    # Numerical Julian-year label; catalog timescale not certified.
    return 2000 + (float(mjd)-51544.5)/365.25

def epoch_from_date(date):
    # Date-to-JD calendar conversion only, not an assertion of UTC/TCB provenance.
    return epoch_from_mjd(Time(date, scale='utc').mjd)

def json_out(name, content):
    (OUT/name).write_text(json.dumps(content, indent=2, allow_nan=False)+'\n', encoding='utf-8')

def csv_out(name, rows):
    with (OUT/name).open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

def main():
    started = datetime.now(timezone.utc).isoformat()
    gaia = {x['source_id']: x for x in csv.DictReader(io.StringIO(read(BASE/'gaia/three_sources_covariance.csv')))}
    papers = list(csv.DictReader(io.StringIO(read(SOURCE/'data/ren2024_table1_transcribed.csv'))))
    prov = json.loads(read(BASE/'g-surveys/G_SOURCE_PROVENANCE.json'))
    provenance = {x['survey']: x for x in prov['sources']}
    radio_rows = {}
    for c in IDS:
        radio_rows[(c, 'RACS-DR1')] = tsv(BASE/f'racs/catalog_{c}.tsv')[0]
    for s in ('vlass', 'first', 'nvss', 'tgss'):
        radio_rows[('G', s.upper())] = tsv(BASE/f'g-surveys/{s}_g.tsv')[0]
    for tile in ('1240-25A', '0354-43A', '2347+00A'):
        header = read(BASE/f'racs/header_{tile}.txt')
        check(f'RACS {tile} header frame', "RADESYS = 'ICRS" in header and 'EQUINOX =        2000.' in header)
    check('exactly three Gaia sources and seven printed rows', len(gaia) == 3 and len(papers) == 7)
    check('negative zero declination parsed', SkyCoord('23 35 32.849', '-00 04 26.256', unit=(u.hourangle,u.deg)).dec.deg < 0)
    check('RA seconds cosine once', abs(radio_sigma(1,1,'ra_time_seconds',60)[0]-7.5)<1e-12)
    check('RA coordinate arcsec cosine once', abs(radio_sigma(1,1,'ra_coordinate_arcsec',60)[0]-.5)<1e-12)
    check('RA tangent arcsec no cosine', radio_sigma(1,1,'ra_tangent_arcsec',60)[0] == 1)
    check('RA degrees conversion', abs(radio_sigma(1/3600,1/3600,'ra_coordinate_degrees',60)[0]-.5)<1e-12)
    check('independent vector pmra already tangent', abs(residual(SkyCoord(10*u.deg,60*u.deg),vector_propagate({'ra':10,'dec':60,'ref_epoch':2016,'pmra':1000,'pmdec':0},2017))[0]-1)<1e-9)
    covariance_checks, rows, details, statistics, inversions = [], [], [], [], []
    max_vector_diff = max_linear_diff = max_sep_diff = max_jac_relative = 0.
    for candidate, sid in IDS.items():
        g = gaia[sid]; c, cor = covariance5(g)
        check(f'{candidate} full correlation matrix PSD', np.linalg.eigvalsh(cor).min() > 0,
              minimum_correlation_eigenvalue=float(np.linalg.eigvalsh(cor).min()))
        check(f'{candidate} epoch-zero covariance', np.allclose(propagated_cov(g,2016)*1e6,c[:2,:2],atol=1e-14))
        tau = -16
        explicit = np.array([[c[0,0]+2*tau*c[0,3]+tau*tau*c[3,3],
                              c[0,1]+tau*(c[0,4]+c[1,3])+tau*tau*c[3,4]],
                             [c[0,1]+tau*(c[0,4]+c[1,3])+tau*tau*c[3,4],
                              c[1,1]+2*tau*c[1,4]+tau*tau*c[4,4]]])
        check(f'{candidate} explicit cross-term expansion', np.allclose(explicit,propagated_cov(g,2000)*1e6,atol=1e-14))
        # Independent finite-difference Jacobian of rectilinear unit-vector map.
        center = vector_propagate(g,2000); jac = np.zeros((2,5))
        for j,k in enumerate(PARAM):
            eps = 10. if j < 2 else 1.
            plus, minus = dict(g), dict(g)
            increment = eps/(3.6e6*math.cos(math.radians(float(g['dec'])))) if j == 0 else eps/3.6e6 if j == 1 else eps
            plus[k], minus[k] = float(g[k])+increment, float(g[k])-increment
            jac[:,j] = (residual(center,vector_propagate(plus,2000))-residual(center,vector_propagate(minus,2000)))*1000/(2*eps)
        finite_cov = jac @ c @ jac.T
        relative = float(np.linalg.norm(finite_cov-explicit)/np.linalg.norm(explicit))
        max_jac_relative = max(max_jac_relative, relative)
        check(f'{candidate} finite-difference full Jacobian covariance', relative < 1e-3, relative_frobenius_difference=relative)
        covariance_checks.append({'candidate':candidate,'C5_mas_and_masyr':c.tolist(),'correlation':cor.tolist(),
                                  'C2000_mas2':explicit.tolist(),'independent_numerical_J':jac.tolist(),
                                  'numerical_covariance_relative_difference':relative})
    for p in papers:
        candidate, survey = p['candidate'], p['survey']; g = gaia[IDS[candidate]]
        raw = radio_rows[(candidate,survey)]
        printed = SkyCoord(p['ra_hms'],p['dec_dms'],unit=(u.hourangle,u.deg),frame='icrs')
        variants = []
        if survey == 'RACS-DR1':
            native = SkyCoord(float(raw['RAJ2000'])*u.deg,float(raw['DEJ2000'])*u.deg)
            proxy = epoch_from_mjd(raw['MJD'])
            interval = [epoch_from_mjd(58594),epoch_from_mjd(59023)]
            epoch_kind = 'associated pointing MJD proxy; whole-catalog expanded MJD58594-59023 support'
            error = [float(raw['e_RAJ2000']),float(raw['e_DEJ2000'])]
            variants = ['ra_coordinate_arcsec','ra_tangent_arcsec']
        else:
            pr = provenance[survey]; pos = pr['native_position']
            native = SkyCoord(pos['ra']*u.deg,pos['dec']*u.deg) if 'ra' in pos else SkyCoord(pos['ra_hms'],pos['dec_dms'],unit=(u.hourangle,u.deg))
            if survey == 'VLASS':
                proxy = epoch_from_date(pr['epoch_evidence']['date_obs']); interval = None
                epoch_kind = 'source-linked DATE-OBS proxy; centroid-time support not recovered'
                error = [pr['native_position_uncertainty'][k] for k in ('ra','dec')]
                variants = ['ra_coordinate_degrees']
            elif survey == 'FIRST':
                proxy = epoch_from_mjd(pr['epoch_evidence']['mean_jd']-2400000.5)
                interval = [epoch_from_date('1993-01-01'),epoch_from_date('2012-01-01')]
                epoch_kind = 'weighted contributing-pointing mean proxy; conservative calendar1993-2011 survey support'
                # Survey endpoints must be backed by provenance; fail instead of silently assuming.
                support = pr['epoch_evidence'].get('conservative_full_survey_interval')
                if support is None:
                    interval = None
                    epoch_kind = 'weighted contributing-pointing mean proxy; full-survey support pending provenance'
                else:
                    interval = [epoch_from_date(support['start']), epoch_from_date(support['end_exclusive'])]
            elif survey == 'NVSS':
                proxy = 1995.; interval = [1993.,1997.]
                epoch_kind = 'survey approximate1995+/-2 only; midpoint sensitivity, not source date or certified bound'
                error = [.04,.7]; variants = ['ra_time_seconds']
            else:
                proxy = None; interval = [epoch_from_date('2010-04-01'),epoch_from_date('2012-04-01')]
                epoch_kind = 'full-survey Apr2010-Mar2012 support; upper endpoint conservatively expanded'
                error = [2.,2.]; variants = ['ra_coordinate_arcsec','ra_tangent_arcsec']
        epochs = [('J2000',2000.)]
        if proxy is not None: epochs.append(('proxy',proxy))
        if interval:
            epochs += [('support_start',interval[0]),('support_end',interval[1])]
        row = {'candidate':candidate,'survey':survey,'epoch_class':epoch_kind,
               'proxy_jyear':proxy,'support_start_jyear':interval[0] if interval else None,
               'support_end_jyear':interval[1] if interval else None,
               'printed_table_radius_arcsec':float(p['printed_total'])}
        for label, radio in (('printed',printed),('native',native)):
            values = {}
            for epoch_label, epoch in epochs:
                star = astropy_propagate(g,epoch)
                vstar = vector_propagate(g,epoch)
                max_vector_diff = max(max_vector_diff,star.separation(vstar).arcsec)
                tau = epoch-float(g['ref_epoch'])
                linear = SkyCoord((float(g['ra'])+float(g['pmra'])*tau/3.6e6/math.cos(math.radians(float(g['dec']))))*u.deg,
                                  (float(g['dec'])+float(g['pmdec'])*tau/3.6e6)*u.deg)
                max_linear_diff = max(max_linear_diff,star.separation(linear).arcsec)
                r = residual(star,radio); sep = star.separation(radio).arcsec
                max_sep_diff = max(max_sep_diff,abs(np.linalg.norm(r)-sep))
                cov = propagated_cov(g,epoch)
                values[epoch_label] = sep
                rv_shifts = [star.separation(astropy_propagate(g,epoch,rv)).arcsec for rv in (-500,500)]
                rec = {'candidate':candidate,'survey':survey,'radio_lane':label,'epoch_label':epoch_label,
                       'jyear_numeric':epoch,'east_arcsec':float(r[0]),'north_arcsec':float(r[1]),'radius_arcsec':sep,
                       'gaia_cov_arcsec2':cov.tolist(),'gaia_sigma_east_mas':1000*math.sqrt(cov[0,0]),
                       'gaia_sigma_north_mas':1000*math.sqrt(cov[1,1]),
                       'rv_minus500_shift_arcsec':rv_shifts[0],'rv_plus500_shift_arcsec':rv_shifts[1],
                       'parallax_one_epoch_assumed_1p03AU_envelope_arcsec':1.03*float(g['parallax'])/1000,
                       'parallax_two_epochs_assumed_1p03AU_envelope_arcsec':2.06*float(g['parallax'])/1000}
                details.append(rec)
                for convention in variants:
                    sx,sy = radio_sigma(*error,convention,native.dec.deg)
                    previous = None
                    for floor in (0.,.5,1.):
                        stat = rho_profile(r,cov,sx,sy,floor)
                        if previous:
                            check(f'floor monotonic {candidate}/{survey}/{label}/{epoch_label}/{convention}/{floor}',
                                  stat['D_min_over_radio_rho'] <= previous['D_min_over_radio_rho']+1e-8 and stat['D_rho0'] <= previous['D_rho0']+1e-8)
                        previous = stat
                        statistics.append({'candidate':candidate,'survey':survey,'radio_lane':label,
                                           'epoch_label':epoch_label,'jyear':epoch,'ra_error_convention':convention,
                                           'radio_sigma_east_arcsec':sx,'radio_sigma_north_arcsec':sy,
                                           'additional_isotropic_sigma_arcsec_scenario':floor,**stat})
            row[f'{label}_J2000_radius_arcsec'] = values['J2000']
            row[f'{label}_proxy_radius_arcsec'] = values.get('proxy')
            if interval:
                # Closest point of linear tangent path; evaluate exact spherical propagation there.
                start = astropy_propagate(g,interval[0]); r0 = residual(start,radio)
                velocity = np.array([float(g['pmra']),float(g['pmdec'])])/1000
                dt = float(np.clip(r0 @ velocity/(velocity @ velocity),0,interval[1]-interval[0]))
                near_epoch = interval[0]+dt
                near_sep = astropy_propagate(g,near_epoch).separation(radio).arcsec
                row[f'{label}_support_radius_min_arcsec'] = min(near_sep,values['support_start'],values['support_end'])
                row[f'{label}_support_radius_max_arcsec'] = max(values['support_start'],values['support_end'])
                row[f'{label}_support_nearest_jyear'] = near_epoch
            else:
                row[f'{label}_support_radius_min_arcsec'] = None
                row[f'{label}_support_radius_max_arcsec'] = None
                row[f'{label}_support_nearest_jyear'] = None
        star0 = astropy_propagate(g,2000.)
        implied_dec = printed.dec.deg-float(p['printed_north'])/3600
        implied_ra = printed.ra.deg-float(p['printed_east'])/3600/math.cos(math.radians(implied_dec))
        implied = SkyCoord(implied_ra*u.deg,implied_dec*u.deg)
        inversions.append({'candidate':candidate,'survey':survey,'implied_star_to_gaia_J2000_arcsec':implied.separation(star0).arcsec})
        row['native_vs_printed_radio_arcsec'] = native.separation(printed).arcsec
        row['FIRST_formal_covariance_status'] = 'unavailable; empirical90percent_scales_only' if survey=='FIRST' else 'not_FIRST'
        rows.append(row)
    check('Astropy versus independent rectilinear vectors',max_vector_diff<1e-4,max_difference_arcsec=max_vector_diff)
    check('Astropy versus first-order coordinate propagation',max_linear_diff<1e-4,max_difference_arcsec=max_linear_diff)
    check('spherical-log norm versus Astropy separation',max_sep_diff<1e-7,max_difference_arcsec=max_sep_diff)
    check('six non-TGSS printed implied stars match J2000 within0.00061arcsec',max(x['implied_star_to_gaia_J2000_arcsec'] for x in inversions if x['survey']!='TGSS')<.00061)
    # Analytic radio-correlation minimization checked against an independent dense scan.
    r = np.array([2.3,-.7]); gc = np.array([[.012,.002],[.002,.007]])
    profile = rho_profile(r,gc,.8,1.2,.5)
    scan = []
    for rho in np.linspace(-1,1,10001):
        cv = gc+np.array([[.8**2+.5**2,rho*.8*1.2],[rho*.8*1.2,1.2**2+.5**2]])
        scan.append(math.sqrt(r @ np.linalg.solve(cv,r)))
    check('analytic rho minimum agrees with independent dense diagnostic',abs(profile['D_min_over_radio_rho']-min(scan))<1e-6,
          analytic=profile['D_min_over_radio_rho'],dense=min(scan))
    tg = next(x for x in papers if x['survey']=='TGSS')
    tg_native = provenance['TGSS']['native_position']
    tg_coord = SkyCoord(tg['ra_hms'],tg['dec_dms'],unit=(u.hourangle,u.deg))
    tg_detail = next(x for x in details if x['survey']=='TGSS' and x['radio_lane']=='printed' and x['epoch_label']=='J2000')
    tg_check = {'printed_native_declination_difference_arcsec':(tg_coord.dec.deg-tg_native['dec'])*3600,
                'printed_north_arcsec':float(tg['printed_north']),'computed_north_arcsec':tg_detail['north_arcsec'],
                'computed_minus_printed_north_arcsec':tg_detail['north_arcsec']-float(tg['printed_north']),
                'radio_coordinate_edit_supported':False}
    check('TGSS native declination unchanged',abs(tg_check['printed_native_declination_difference_arcsec'])<1e-8)
    check('TGSS same-reference north component discrepancy approximately1arcsec',abs(tg_check['computed_minus_printed_north_arcsec']+1)<.001)
    first = provenance['FIRST']; morph = first['morphology']; flux = first['native_flux_mjy']
    snr = (flux['peak_per_beam']-.25)/flux['local_rms_per_beam']
    first_scales = {'SNR_definition': '(Fpeak-0.25)/Rms','SNR':snr,
                    'empirical90percent_major_arcsec':morph['fitted_major_arcsec']*(1/snr+1/20),
                    'empirical90percent_minor_arcsec':morph['fitted_minor_arcsec']*(1/snr+1/20),
                    'fitted_PA_deg_east_of_north':morph['fitted_pa_degrees'],
                    'Gaussian_sigma_or_joint90percent_contour_conversion':'not_assumed'}
    check('input files preserved',all(hashlib.sha256(Path(path).read_bytes()).hexdigest()==sha for path,sha in INPUTS.items()))
    csv_out('seven_rows.csv',rows); csv_out('conditional_covariance_sensitivity.csv',statistics)
    json_out('epoch_details.json',details); json_out('gaia_covariance_checks.json',covariance_checks)
    json_out('printed_reference_inversion.json',inversions); json_out('tgss_discrepancy.json',tg_check)
    json_out('first_empirical_accuracy.json',first_scales); json_out('checks.json',CHECKS)
    text = ['# Seven-row coordinate sensitivity audit','',
            'Central separations in arcseconds. Source dates are classified in the CSV; ranges are survey-level supports, not Gaussian confidence intervals. Radio numerical coordinates are retained; no inferred FK5 rotation or registration correction.','',
            '| Star / survey | Printed radius | Printed / J2000 replay | Native / J2000 | Native / epoch proxy | Native / survey support |',
            '|---|---:|---:|---:|---:|---:|']
    for r in rows:
        proxy = 'unavailable' if r['native_proxy_radius_arcsec'] is None else f"{r['native_proxy_radius_arcsec']:.6f}"
        band = 'unavailable' if r['native_support_radius_min_arcsec'] is None else f"{r['native_support_radius_min_arcsec']:.6f}–{r['native_support_radius_max_arcsec']:.6f}"
        text.append(f"| {r['candidate']} / {r['survey']} | {r['printed_table_radius_arcsec']:.3f} | {r['printed_J2000_radius_arcsec']:.6f} | {r['native_J2000_radius_arcsec']:.6f} | {proxy} | {band} |")
    text += ['', 'D values in the detailed CSV are conditional Mahalanobis distances, not calibrated significance or identification probabilities. Additional 0, 0.5 and 1 arcsecond isotropic standard deviations are illustrative scenarios; the 2 arcsecond TGSS systematic contribution is already in its supplied errors and is not added again.',
             '', 'FIRST has no Gaussian coordinate covariance in the inspected catalog; only its documented empirical 90% accuracy scales are calculated. Missing covariance is not zero covariance.',
             '', f"TGSS printed-minus-native declination: {tg_check['printed_native_declination_difference_arcsec']:.9g} arcsec. Same-J2000-reference calculated-minus-printed north component: {tg_check['computed_minus_printed_north_arcsec']:.9f} arcsec.",
             '', f"Executed checks: {len(CHECKS)}, all passed. Independent vector/Astropy maximum difference {max_vector_diff:.3g} arcsec; coordinate-linear/Astropy {max_linear_diff:.3g} arcsec; spherical-log/Astropy separation {max_sep_diff:.3g} arcsec."]
    (OUT/'RESULTS.md').write_text('\n'.join(text)+'\n',encoding='utf-8')
    outputs = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.iterdir() if p.is_file() and p.name!='execution_receipt.json'}
    receipt = {'started_utc':started,'completed_utc':datetime.now(timezone.utc).isoformat(),
               'status':'completed_all_checks_passed','python_executable':sys.executable,'python_version':platform.python_version(),
               'numpy_version':np.__version__,'astropy_version':astropy.__version__,
               'thread_environment':{k:os.environ[k] for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS')},
               'network_in_script':False,'iers_auto_download':False,'gpu':False,'input_sha256':INPUTS,'output_sha256':outputs,
               'checks_count':len(CHECKS),'input_preservation_verified':True,
               'limitations':['local linear covariance, checked against full numerical direction Jacobian',
                              'no full apparent-position ephemeris; geometric envelopes conditional on observer barycentric distance <=1.03AU',
                              'RV+-500km/s is a scenario, not a measured constraint',
                              'unknown radio covariance profiled at listed epochs, no claim of joint epoch-covariance global extrema',
                              'radio frame service labels do not certify frame realization; numerical convention retained',
                              'survey supports and epoch proxies are not source-specific weighted centroid timestamps',
                              'illustrative registration floors do not calibrate absolute registration or p values']}
    json_out('execution_receipt.json',receipt)
    print(json.dumps({'status':receipt['status'],'checks_count':len(CHECKS),'rows':rows,'tgss':tg_check},indent=2))

if __name__ == '__main__':
    main()
