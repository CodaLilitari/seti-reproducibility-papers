"""Separate offline TGSS common-versus-single-different-epoch diagnostic.

Preserves the reviewed main audit and outputs. No network, image interpretation,
new sources, or inference about the authors' actual historical implementation.
"""
from __future__ import annotations
import csv
import hashlib
import io
import json
import math
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS',
            'NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):
    os.environ[key] = '1'
import astropy
import astropy.units as u
from astropy.coordinates import SkyCoord
from astropy.utils import iers
iers.conf.auto_download = False

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
PREFIX = 'tgss_reference_'
SID = '2644370304260053376'
CHECKS = []
INPUTS = {}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load_csv(path):
    data = path.read_bytes(); INPUTS[str(path)] = hashlib.sha256(data).hexdigest()
    return list(csv.DictReader(io.StringIO(data.decode('utf-8-sig'))))

def check(name, condition, **details):
    CHECKS.append({'name':name,'passed':bool(condition),**details})
    if not condition:
        raise AssertionError(name)

def bisect_increasing(fn, target, low=1990., high=2030.):
    if not fn(low) <= target <= fn(high):
        raise ValueError('root outside declared epoch interval')
    for _ in range(80):
        middle = (low+high)/2
        if fn(middle) < target: low = middle
        else: high = middle
    return (low+high)/2

def golden(fn, low=1990., high=2030.):
    ratio = (math.sqrt(5)-1)/2
    a,b = high-ratio*(high-low),low+ratio*(high-low)
    fa,fb = fn(a),fn(b)
    for _ in range(100):
        if fa < fb:
            high,b,fb = b,a,fa
            a = high-ratio*(high-low); fa = fn(a)
        else:
            low,a,fa = a,b,fb
            b = low+ratio*(high-low); fb = fn(b)
    return (low+high)/2

def main():
    started = datetime.now(timezone.utc).isoformat()
    preserved = {str(p):sha(p) for p in OUT.iterdir() if p.is_file() and not p.name.startswith(PREFIX)}
    gaia = next(x for x in load_csv(ROOT/'gaia/three_sources_covariance.csv') if x['source_id']==SID)
    table = load_csv(ROOT.parent/'source/Ren2024_Coordinate_State_Followup_2026-10-08/data/ren2024_table1_transcribed.csv')
    paper = next(x for x in table if x['survey']=='TGSS' and x['candidate']=='G')
    racs = next(x for x in table if x['survey']=='RACS-DR1' and x['candidate']=='G')
    radio = SkyCoord(paper['ra_hms'],paper['dec_dms'],unit=(u.hourangle,u.deg),frame='icrs')
    target = [float(paper['printed_east']),float(paper['printed_north'])]
    a0,d0,ref,ma,md = (float(gaia[k]) for k in ('ra','dec','ref_epoch','pmra','pmdec'))
    dra_year = ma/(3.6e6*math.cos(math.radians(d0)))
    ddec_year = md/3.6e6

    def stellar(epoch):
        return a0+dra_year*(epoch-ref),d0+ddec_year*(epoch-ref)

    def components(epoch):
        a,d = stellar(epoch)
        da = (radio.ra.deg-a+180)%360-180
        return da*3600*math.cos(math.radians(d)),(radio.dec.deg-d)*3600

    def square(epoch):
        e,n = components(epoch)
        return (e-target[0])**2+(n-target[1])**2

    common = components(2000.)
    east_epoch = bisect_increasing(lambda t:components(t)[0],target[0])
    north_epoch = bisect_increasing(lambda t:components(t)[1],target[1])
    # Independent inversion of both printed components into an implied star.
    implied_dec = radio.dec.deg-target[1]/3600
    implied_ra = radio.ra.deg-target[0]/(3600*math.cos(math.radians(implied_dec)))
    ra_epoch = ref+(implied_ra-a0)/dra_year
    dec_epoch = ref+(implied_dec-d0)/ddec_year

    # Fixed local tangent projection; an independent scalar fit retains cos(delta(t)).
    velocity = [-ma/1000,-md/1000]
    difference = [target[i]-common[i] for i in range(2)]
    tau = sum(difference[i]*velocity[i] for i in range(2))/sum(x*x for x in velocity)
    projected_epoch = 2000+tau
    fitted_epoch = golden(square)
    fitted_components = components(fitted_epoch)
    residual = [fitted_components[i]-target[i] for i in range(2)]
    orthogonal_irreducible = abs(difference[0]*velocity[1]-difference[1]*velocity[0])/math.hypot(*velocity)
    normal_dot = sum(residual[i]*velocity[i] for i in range(2))
    check('epoch search has positive east and north component slopes',ma<0 and md<0)
    check('separate east epoch reproduces printed east',abs(components(east_epoch)[0]-target[0])<1e-8)
    check('separate north epoch reproduces printed north',abs(components(north_epoch)[1]-target[1])<1e-8)
    check('independent implied-coordinate epoch inversion',abs(ra_epoch-east_epoch)<1e-4 and abs(dec_epoch-north_epoch)<1e-6)
    check('analytic projection and scalar fit agree',abs(projected_epoch-fitted_epoch)<1e-4,
          epoch_difference_years=projected_epoch-fitted_epoch)
    check('independent orthogonal residual formula',abs(orthogonal_irreducible-math.hypot(*residual))<1e-6)
    check('fitted residual approximately orthogonal to motion',abs(normal_dot)<1e-6)
    check('joint solution lies inside1990to2030 and improves endpoints',1990<fitted_epoch<2030 and square(fitted_epoch)<min(square(1990),square(2030)))
    # A distinct coarse scan checks optimizer placement, not a precision certificate.
    scan_best = min((square(1990+i*.01),1990+i*.01) for i in range(4001))
    check('independent coarse scan brackets joint optimizer',abs(scan_best[1]-fitted_epoch)<.011)
    rounding = []
    for label, tolerance in (
        ('printed_components_only_radio_held_exact',[.0005,.0005]),
        ('including_half_last_printed_radio_coordinate_digits',
         [.0005+.0005*15*math.cos(math.radians(radio.dec.deg)),.0005+.0005])):
        intervals = [[bisect_increasing(lambda t,i=i:components(t)[i],target[i]-tolerance[i]),
                      bisect_increasing(lambda t,i=i:components(t)[i],target[i]+tolerance[i])] for i in range(2)]
        common_interval = [max(x[0] for x in intervals),min(x[1] for x in intervals)]
        possible = common_interval[0] <= common_interval[1]
        rounding.append({'scenario':label,'component_tolerances_arcsec':tolerance,
                         'east_allowed_epoch_interval':intervals[0],'north_allowed_epoch_interval':intervals[1],
                         'common_epoch_exists':possible})
        check(f'no single epoch at stated rounding: {label}',not possible)
    r2000 = SkyCoord(*stellar(2000),unit=u.deg)
    common_radius = radio.separation(r2000).arcsec
    printed_norm = math.hypot(*target)
    printed_radius = float(paper['printed_total'])
    check('printed radius rounds consistently with printed components',abs(printed_radius-printed_norm)<.0005)
    check('common-reference tangent norm and spherical radius agree',abs(math.hypot(*common)-common_radius)<1e-6)
    check('TGSS and RACS printed RA is identical',paper['ra_hms']==racs['ra_hms'])
    racs_radio = SkyCoord(racs['ra_hms'],racs['dec_dms'],unit=(u.hourangle,u.deg))
    dec_difference = (radio.dec.deg-racs_radio.dec.deg)*3600
    printed_offset_difference = target[1]-float(racs['printed_north'])
    check('common reference cannot produce inconsistent north differences',abs(dec_difference-printed_offset_difference+1)<1e-9)
    check('all already reviewed math files preserved',all(sha(Path(p))==h for p,h in preserved.items()))
    check('all input files preserved',all(sha(Path(p))==h for p,h in INPUTS.items()))
    result = {'question':'Can a different SINGLE epoch of this same Gaia linear-motion star reproduce both TGSS printed components?',
              'answer':'No, within1990-2030 and under the specified model, even allowing half-unit rounding of the printed radio coordinates and offsets.',
              'gaia_source_id':SID,'epoch_model':'Gaia linear RA/Dec propagation with pmra cosine convention; east uses cos(propagated declination)',
              'epoch_range_jyear':[1990,2030],
              'printed_radio_coordinates':{'ra_deg':radio.ra.deg,'dec_deg':radio.dec.deg},
              'printed_components_arcsec':target,'computed_common_J2000_components_arcsec':list(common),
              'east_only_effective_epoch_jyear':east_epoch,'north_only_effective_epoch_jyear':north_epoch,
              'implied_star_ra_deg':implied_ra,'implied_star_dec_deg':implied_dec,
              'independent_RA_coordinate_epoch_jyear':ra_epoch,'independent_Dec_coordinate_epoch_jyear':dec_epoch,
              'analytic_joint_projection_epoch_jyear':projected_epoch,'joint_scalar_fit_epoch_jyear':fitted_epoch,
              'joint_fit_computed_components_arcsec':list(fitted_components),
              'joint_fit_computed_minus_printed_components_arcsec':residual,
              'irreducible_component_residual_norm_arcsec':math.hypot(*residual),
              'independent_orthogonal_residual_arcsec':orthogonal_irreducible,
              'rounding_feasibility':rounding,
              'radius_checks':{'printed_radius_arcsec':printed_radius,'printed_component_norm_arcsec':printed_norm,
                               'printed_radius_minus_printed_norm_arcsec':printed_radius-printed_norm,
                               'common_J2000_spherical_radius_arcsec':common_radius,
                               'common_J2000_radius_minus_printed_radius_arcsec':common_radius-printed_radius},
              'TGSS_minus_RACS':{'printed_radio_dec_difference_arcsec':dec_difference,
                                 'printed_north_offset_difference_arcsec':printed_offset_difference,
                                 'difference_of_differences_arcsec':dec_difference-printed_offset_difference},
              'scope_limits':['conditional arithmetic at supplied central Gaia values, not a statistical hypothesis test',
                              'does not exclude a different star, mixed fields, different reference coordinates, transcription or other workflow errors',
                              'does not identify the historical implementation or establish why the discrepancy occurred',
                              'does not change or invalidate the independently catalog-confirmed TGSS radio declination',
                              'the joint fit uses unweighted equal east/north residuals to test exact compatibility, not an astrometric likelihood']}
    (OUT/f'{PREFIX}diagnostic.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    (OUT/f'{PREFIX}checks.json').write_text(json.dumps(CHECKS,indent=2)+'\n',encoding='utf-8')
    report = f'''# TGSS single-stellar-epoch diagnostic

For the same Gaia star under linear proper motion, changing only one common stellar epoch cannot reproduce both printed TGSS components at their stated rounding.

| Diagnostic | Result |
|---|---:|
| East-only effective epoch | J{east_epoch:.9f} |
| North-only effective epoch | J{north_epoch:.9f} |
| Best joint unweighted epoch | J{fitted_epoch:.9f} |
| Joint computed-minus-printed east residual | {residual[0]:.9f} arcsec |
| Joint computed-minus-printed north residual | {residual[1]:.9f} arcsec |
| Irreducible joint residual norm | {math.hypot(*residual):.9f} arcsec |
| Printed radius | {printed_radius:.6f} arcsec |
| Norm of printed components | {printed_norm:.9f} arcsec |
| Same-J2000-reference spherical radius | {common_radius:.9f} arcsec |

The printed radius is consistent with its printed components at rounding. Those components cannot both come from a single different epoch of this star. The separately allowed east and north epoch intervals remain disjoint even after including half of the last printed digit in radio RA (0.0005 seconds of time), radio declination (0.0005 arcsec), and the components (0.0005 arcsec each). The exact intervals are in the JSON.

This is a conditional compatibility calculation for the supplied central Gaia motion, not a probability or significance calculation. It does not exclude another star, mixed fields, a different reference coordinate, transcription, or another workflow error, and does not identify the authors' historical cause. Native TGSS declination remains unchanged.

Independent checks cover implied-coordinate inversion, analytic orthogonal projection, scalar minimization, a separate coarse scan, rounding-feasible interval intersection, component/radius consistency and preservation of all already reviewed math files. All {len(CHECKS)} recorded checks passed.
'''
    (OUT/f'{PREFIX}RESULTS.md').write_text(report,encoding='utf-8')
    generated = {str(p):sha(p) for p in OUT.iterdir() if p.is_file() and p.name.startswith(PREFIX) and p.name!=f'{PREFIX}receipt.json'}
    receipt = {'started_utc':started,'completed_utc':datetime.now(timezone.utc).isoformat(),
               'status':'completed_all_checks_passed','python_executable':sys.executable,'astropy_version':astropy.__version__,
               'network':False,'gpu':False,'iers_auto_download':False,
               'thread_environment':{k:os.environ[k] for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS')},
               'input_sha256':INPUTS,'already_reviewed_math_sha256_unchanged':preserved,
               'new_files_sha256':generated,'check_count':len(CHECKS)}
    (OUT/f'{PREFIX}receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    main()
