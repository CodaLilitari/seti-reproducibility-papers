"""Bounded offline verification of consequential Claude review recommendations.

Creates only reviewer_followup* files and preserves previously reviewed artifacts.
No network, GPU, image measurement, inferred IR epoch, or source refactor.
"""
from __future__ import annotations
import ast
import csv
import hashlib
import importlib.util
import io
import json
import math
import os
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urlparse

sys.dont_write_bytecode = True
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS',
            'NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):
    os.environ[key] = '1'
import numpy as np
import astropy
import astropy.units as u
from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy.utils import iers
iers.conf.auto_download = False

OUT = Path(__file__).resolve().parent
BASE = OUT.parent
PREFIX = 'reviewer_followup'
INPUTS = {}
CHECKS = []

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path):
    data = path.read_bytes(); INPUTS[str(path)] = hashlib.sha256(data).hexdigest()
    return data.decode('utf-8-sig')

def check(name, condition, **detail):
    CHECKS.append({'name':name,'passed':bool(condition),**detail})
    if not condition: raise AssertionError(name)

def tsv(path):
    lines = [line for line in read(path).splitlines() if line and not line.startswith('#')]
    columns = lines[0].split('\t')
    rows = [dict(zip(columns,[x.strip() for x in line.split('\t')])) for line in lines[3:]]
    check(f'exactly one raw source row: {path.name}',len(rows)==1)
    return rows[0]

def load_csv(path):
    return list(csv.DictReader(io.StringIO(read(path))))

def json_out(name, value):
    (OUT/name).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf-8')

def csv_out(name, rows):
    with (OUT/name).open('w',newline='',encoding='utf-8') as f:
        writer = csv.DictWriter(f,fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)

def assigned(body, name):
    found = []
    for node in ast.walk(ast.Module(body=body,type_ignores=[])):
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in node.targets):
            found.append(node.value)
    return found

def survey_if(tree, survey):
    for node in ast.walk(tree):
        if isinstance(node,ast.If) and isinstance(node.test,ast.Compare):
            test = node.test
            if isinstance(test.left,ast.Name) and test.left.id=='survey' and len(test.comparators)==1 and isinstance(test.comparators[0],ast.Constant) and test.comparators[0].value==survey:
                return node
    raise ValueError(survey)

def direct_d(r, g, sx, sy, floor, rho):
    a = float(g[0,0])+sx*sx+floor*floor
    b = float(g[1,1])+sy*sy+floor*floor
    c = float(g[0,1])+rho*sx*sy
    det = a*b-c*c
    if det <= 0: raise ValueError('nonpositive determinant')
    x,y = r
    return math.sqrt(max(0.,(b*x*x-2*c*x*y+a*y*y)/det))

def main():
    started = datetime.now(timezone.utc).isoformat()
    preserved = {str(p):sha(p) for p in OUT.iterdir() if p.is_file() and not p.name.startswith(PREFIX)}
    original_path = OUT/'audit_astrometry.py'
    original_source = read(original_path)
    check('reviewed script exact hash',sha(original_path)=='0f6ea11aa6cc006ab10dfaa644d394c9fdeeb019ae59467b22511a1820b07c93')
    spec = importlib.util.spec_from_file_location('reviewed_audit',original_path)
    audit = importlib.util.module_from_spec(spec); spec.loader.exec_module(audit)
    source_root = BASE.parent/'source/Ren2024_Coordinate_State_Followup_2026-10-08'
    papers = load_csv(source_root/'data/ren2024_table1_transcribed.csv')
    gaia = load_csv(BASE/'gaia/three_sources_covariance.csv')
    expected_ids = {'A':'3496509309189181184','B':'4843191593270342656','G':'2644370304260053376'}
    check('exact Gaia source ID set',len(gaia)==3 and {r['source_id'] for r in gaia}==set(expected_ids.values()))
    provenance = json.loads(read(BASE/'g-surveys/G_SOURCE_PROVENANCE.json'))
    prov = {x['survey']:x for x in provenance['sources']}
    details = json.loads(read(OUT/'epoch_details.json'))
    sensitivity = load_csv(OUT/'conditional_covariance_sensitivity.csv')
    summary = load_csv(OUT/'seven_rows.csv')
    cov_checks = json.loads(read(OUT/'gaia_covariance_checks.json'))
    products = load_csv(BASE/'racs/cadc_product_uris.csv')
    row_checks, headers = [], []
    expected_racs = {'A':('RACS_1240-25A_3178','13746'),
                     'B':('RACS_0354-43A_3693','8641'),
                     'G':('RACS_2347+00A_4762','8586')}
    for candidate,(source_id,sbid) in expected_racs.items():
        raw = tsv(BASE/f'racs/catalog_{candidate}.tsv')
        p = next(x for x in papers if x['candidate']==candidate and x['survey']=='RACS-DR1')
        check(f'{candidate} RACS source ID SBID and printed source name',
              raw['ID']==source_id and raw['SBID']==sbid and raw['RACS-DR1']==p['source_name'])
        check(f'{candidate} row ID parent tile relationship',source_id.startswith(raw['Tile']+'_'))
        tile = raw['Tile'].removeprefix('RACS_')
        observation = 'RACS-DR1_'+tile
        product = [x for x in products if x['observationID']==observation]
        check(f'{candidate} unique row-linked CADC product',len(product)==1 and product[0]['uri']==f'casda:RACS/{observation}.fits')
        path = BASE/f'racs/header_{tile}.txt'
        header_text = read(path); header = fits.Header.fromstring(header_text,sep='\n')
        receipt = json.loads(read(path.with_suffix('.txt.receipt.json')))
        check(f'{candidate} row-linked header receipt hash and status',receipt['sha256']==sha(path) and receipt['status']==200)
        check(f'{candidate} row-linked header retrieval product',unquote(urlparse(receipt['requested_url']).path).endswith('/'+observation+'.fits'))
        check(f'{candidate} header frame and telescope',header['RADESYS'].strip()=='ICRS' and float(header['EQUINOX'])==2000 and header['TELESCOP'].strip()=='ASKAP')
        # Product-to-row binding does not establish source-specific time contributors.
        headers.append({'candidate':candidate,'catalog_ID':raw['ID'],'catalog_tile':raw['Tile'],
                        'SBID':raw['SBID'],'observationID':observation,'artifact_uri':product[0]['uri'],
                        'header_sha256':sha(path),'RADESYS':header['RADESYS'],'EQUINOX':header['EQUINOX'],
                        'TIMESYS':header.get('TIMESYS'),'DATE-OBS':header.get('DATE-OBS'),
                        'MJD-OBS':header.get('MJD-OBS'),'source_weighted_epoch_proven':False,
                        'fit_major_arcsec':float(raw['amaj']),'fit_minor_arcsec':float(raw['bmin']),
                        'fit_PA_degrees':float(raw['PA']),
                        'centroid_covariance_from_shape':'not inferred; widths/PA alone are insufficient'})
        native = SkyCoord(float(raw['RAJ2000'])*u.deg,float(raw['DEJ2000'])*u.deg)
        printed = SkyCoord(p['ra_hms'],p['dec_dms'],unit=(u.hourangle,u.deg))
        sep = native.separation(printed).arcsec
        check(f'{candidate} RACS native versus printed below0.005arcsec',sep<.005,actual_arcsec=sep)
        row_checks.append({'candidate':candidate,'survey':'RACS-DR1','raw_source_id':raw['ID'],'native_printed_difference_arcsec':sep})
    names = {'VLASS':('CompName','VLASS1QLCIR J233532.86-000424.9'),
             'FIRST':('FIRST','J233532.8-000425'),
             'NVSS':('NVSS','233532-000425'),
             'TGSS':('TGSSADR','J233532.8-000426')}
    raw_g = {}
    for survey,(column,expected) in names.items():
        raw = raw_g[survey] = tsv(BASE/f'g-surveys/{survey.lower()}_g.tsv')
        check(f'{survey} exact raw source ID',raw[column]==expected)
        p = next(x for x in papers if x['survey']==survey)
        printed_name_form = 'J'+expected if survey=='NVSS' else expected
        check(f'{survey} raw source name corresponds to printed name',printed_name_form.endswith(p['source_name']))
        native = SkyCoord(raw['RAJ2000'],raw['DEJ2000'],unit=(u.hourangle,u.deg)) if survey in ('FIRST','NVSS') else SkyCoord(float(raw['RAJ2000'])*u.deg,float(raw['DEJ2000'])*u.deg)
        pos = prov[survey]['native_position']
        json_coord = SkyCoord(pos['ra_hms'],pos['dec_dms'],unit=(u.hourangle,u.deg)) if 'ra_hms' in pos else SkyCoord(pos['ra']*u.deg,pos['dec']*u.deg)
        check(f'{survey} raw position versus provenance JSON',native.separation(json_coord).arcsec<1e-8)
        printed = SkyCoord(p['ra_hms'],p['dec_dms'],unit=(u.hourangle,u.deg))
        sep = native.separation(printed).arcsec
        check(f'{survey} native versus printed below0.005arcsec',sep<.005,actual_arcsec=sep)
        row_checks.append({'candidate':'G','survey':survey,'raw_source_id':raw[column],'native_printed_difference_arcsec':sep})

    # Check the hard-coded reviewed snapshot against external input values, without editing it.
    tree = ast.parse(original_source)
    nvss_if = survey_if(tree,'NVSS')
    nvss_errors = ast.literal_eval(assigned(nvss_if.body,'error')[0])
    nvss_interval = ast.literal_eval(assigned(nvss_if.body,'interval')[0])
    tgss_errors = ast.literal_eval(assigned(nvss_if.orelse,'error')[0])
    tgss_interval_ast = assigned(nvss_if.orelse,'interval')[0]
    tgss_dates = [ast.literal_eval(call.args[0]) for call in tgss_interval_ast.elts]
    nvss_pr = prov['NVSS']['native_position_uncertainty']
    check('hardcoded NVSS errors equal JSON and raw table',nvss_errors==[nvss_pr['ra'],nvss_pr['dec']]==[float(raw_g['NVSS']['e_RAJ2000']),float(raw_g['NVSS']['e_DEJ2000'])])
    check('hardcoded NVSS interval equals provenance scenario',nvss_interval==prov['NVSS']['epoch_evidence']['derived_interval_for_sensitivity_only'])
    tgss_pr = prov['TGSS']['native_position_uncertainty']
    check('hardcoded TGSS errors equal JSON and raw table',tgss_errors==[tgss_pr['ra'],tgss_pr['dec']]==[float(raw_g['TGSS']['e_RAJ2000']),float(raw_g['TGSS']['e_DEJ2000'])])
    months = prov['TGSS']['epoch_evidence']['documented_survey_interval']
    y,m = map(int,months['end'].split('-'))
    end = date(y+1,1,1) if m==12 else date(y,m+1,1)
    derived_dates = [months['start']+'-01',end.isoformat()]
    check('hardcoded TGSS interval equals month-expanded provenance',tgss_dates==derived_dates)
    first_if = survey_if(tree,'FIRST')
    outer = next(n for n in ast.walk(tree) if isinstance(n,ast.For) and isinstance(n.target,ast.Name) and n.target.id=='p' and isinstance(n.iter,ast.Name) and n.iter.id=='papers')
    direct_variants = [n for n in outer.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='variants' for t in n.targets)]
    check('FIRST stale error is guarded by fresh empty variants',len(direct_variants)==1 and ast.literal_eval(direct_variants[0].value)==[] and assigned(first_if.body,'error')==[] and assigned(first_if.body,'variants')==[])
    check('executed snapshot produced no FIRST Gaussian D rows',not any(r['survey']=='FIRST' for r in sensitivity))
    check('baseline numerical Jacobian parallax column is zero',all(np.all(np.array(x['independent_numerical_J'])[:,2]==0) for x in cov_checks))

    a = next(x for x in details if x['candidate']=='A' and x['radio_lane']=='native' and x['epoch_label']=='proxy')
    r = np.array([a['east_arcsec'],a['north_arcsec']]); g = np.array(a['gaia_cov_arcsec2'])
    raw_a = tsv(BASE/'racs/catalog_A.tsv')
    finite = []
    for convention in ('ra_coordinate_arcsec','ra_tangent_arcsec'):
        sx = float(raw_a['e_RAJ2000'])*(math.cos(math.radians(float(raw_a['DEJ2000']))) if convention=='ra_coordinate_arcsec' else 1)
        sy = float(raw_a['e_DEJ2000'])
        for floor in (0.,.5,1.):
            for rho in (-.5,0.,.5):
                d = direct_d(r,g,sx,sy,floor,rho)
                matrix = g+np.array([[sx*sx+floor*floor,rho*sx*sy],[rho*sx*sy,sy*sy+floor*floor]])
                inv_d = math.sqrt(r @ np.linalg.inv(matrix) @ r)
                check(f'A finite rho direct/inverse {convention}/{floor}/{rho}',abs(d-inv_d)<1e-12)
                if rho==0:
                    old = next(x for x in sensitivity if x['candidate']=='A' and x['radio_lane']=='native' and x['epoch_label']=='proxy' and x['ra_error_convention']==convention and float(x['additional_isotropic_sigma_arcsec_scenario'])==floor)
                    check(f'A finite rho0 matches reviewed output {convention}/{floor}',abs(d-float(old['D_rho0']))<1e-12)
                finite.append({'candidate':'A','survey':'RACS-DR1','radio_lane':'native','epoch_label':'proxy',
                               'epoch_jyear':a['jyear_numeric'],'ra_error_convention':convention,
                               'additional_stochastic_isotropic_sigma_arcsec':floor,'radio_rho':rho,'D_conditional':d})

    # Boundary, q=0, and near-singular profiles checked independently of target code.
    cases = [
        ('boundary_positive',[1.,1.],[[.1,0],[0,.1]],1.,1.,.5,1.),
        ('boundary_negative',[1.,-1.],[[.1,0],[0,.1]],1.,1.,.5,-1.),
        ('axis_east_interior',[2.,0.],[[.2,.05],[.05,.3]],1.,1.,0.,-.05),
        ('axis_north_interior',[0.,2.],[[.2,.05],[.05,.3]],1.,1.,0.,-.05),
        ('axis_boundary',[1.,0.],[[1.,.9],[.9,1.]],.1,.1,0.,-1.),
        ('zero_residual',[0.,0.],[[.2,.05],[.05,.3]],1.,1.,.5,None),
        ('interior_mixed',[2.3,-.7],[[.012,.002],[.002,.007]],.8,1.2,.5,None),
        ('near_singular_radio_boundary',[1.,1.],[[1e-8,0],[0,1e-8]],1.,1.,0.,1.)]
    profile_checks = []
    for name,rr,gg,sx,sy,floor,expected_rho in cases:
        rr,gg = np.array(rr),np.array(gg)
        result = audit.rho_profile(rr,gg,sx,sy,floor)
        rho_grid = np.linspace(-1,1,20001)
        aa,bb = gg[0,0]+sx*sx+floor*floor,gg[1,1]+sy*sy+floor*floor
        cc = gg[0,1]+rho_grid*sx*sy
        dd = np.sqrt(np.maximum(0,(bb*rr[0]**2-2*cc*rr[0]*rr[1]+aa*rr[1]**2)/(aa*bb-cc*cc)))
        check(f'{name}: profiled min versus independent grid',abs(result['D_min_over_radio_rho']-float(dd.min()))<1e-6)
        check(f'{name}: profiled max versus independent grid',math.isclose(result['D_max_over_radio_rho'],float(dd.max()),rel_tol=1e-7,abs_tol=1e-7))
        for label in ('min','max'):
            rho = result[f'rho_at_{label}']
            matrix = gg+np.array([[sx*sx+floor*floor,rho*sx*sy],[rho*sx*sy,sy*sy+floor*floor]])
            inverse = math.sqrt(max(0,float(rr @ np.linalg.inv(matrix) @ rr)))
            check(f'{name}: {label} versus independent inverse',math.isclose(result[f'D_{label}_over_radio_rho'],inverse,rel_tol=1e-7,abs_tol=1e-7))
        if expected_rho is not None:
            check(f'{name}: expected minimizing boundary/axis rho',abs(result['rho_at_min']-expected_rho)<1e-10)
        profile_checks.append({'case':name,**result,'independent_grid_min':float(dd.min()),'independent_grid_max':float(dd.max())})

    # A deterministic unknown vector offset of bounded norm is not a variance.
    bias_bound = 1.
    separation = float(np.linalg.norm(r))
    low,high = max(0,separation-bias_bound),separation+bias_bound
    direction = r/separation
    check('fixed bias lower bound attained geometrically',abs(np.linalg.norm(r-bias_bound*direction)-low)<1e-12)
    check('fixed bias upper bound attained geometrically',abs(np.linalg.norm(r+bias_bound*direction)-high)<1e-12)
    check('fixed bias independent angular grid stays in envelope',all(low-1e-12 <= np.linalg.norm(r+np.array([math.cos(t),math.sin(t)])) <= high+1e-12 for t in np.linspace(0,2*math.pi,1441)))
    a_range = next(x for x in summary if x['candidate']=='A')
    bias = {'assumption':'Hypothetical unknown deterministic tangent-plane bias vector with Euclidean norm at most1arcsec; not measured and not a stochastic sigma.',
            'native_A_proxy_radius_arcsec':separation,'bias_norm_bound_arcsec':bias_bound,
            'proxy_geometric_separation_envelope_arcsec':[low,high],
            'survey_support_diagnostic_plus_bias_envelope_arcsec':[max(0,float(a_range['native_support_radius_min_arcsec'])-bias_bound),float(a_range['native_support_radius_max_arcsec'])+bias_bound],
            'limits':'Triangle-inequality bound conditional on this bias limit and tangent geometry; survey-support extrema remain the prior diagnostic, not certified nonlinear global extrema.'}
    check('all previously reviewed math files preserved',all(sha(Path(p))==h for p,h in preserved.items()))
    check('all read inputs preserved',all(sha(Path(p))==h for p,h in INPUTS.items()))
    check('all replay inputs reside under portable package root',all(Path(p).is_relative_to(BASE.parent) for p in INPUTS))
    result = {'curation_scope':'Public derivative; private reviewer-record provenance checks omitted; scientific checks retained',
              'native_A_proxy_residual_arcsec':r.tolist(),'finite_correlations':finite,'fixed_bias_scenario':bias,
              'rho_profile_tests':profile_checks,'source_row_assertions':row_checks,'row_bound_header_assertions':headers,
              'hardcoded_snapshot_checks':{'NVSS_errors':nvss_errors,'NVSS_interval':nvss_interval,'TGSS_errors':tgss_errors,'TGSS_calendar_support':tgss_dates,'all_equal_source_provenance':True},
              'stale_error_assessment':'Harmless in the executed snapshot: variants resets to[] for each paper row, FIRST does not populate it, and no FIRST Gaussian D rows were produced. Snapshot intentionally unchanged.',
              'Jacobian_scope':'The numerical check validates a local linear barycentric direction model against a rectilinear RV=0 direction map. Its parallax column is zero by construction. It is not a validation of apparent-position parallax, uncertain RV, binary acceleration, or the physical adequacy of that model.',
              'interpretation':'D is conditional only. Minimized D does not establish co-location; fit-only D_max near singular rho endpoints is not calibrated significance. Finite rho values expose material model sensitivity.',
              'IR_next_requirement':'Recover the exact excess catalog/release and extraction products for A; verify source identity, per-band measurement positions and contributing exposure/coadd epochs or weights, frame/astrometric convention, and band-specific PSF/deblending/morphology. Only then propagate the star to supported IR measurement times and assess any identified radio emitter\'s IR contribution. No AllWISE-like epoch is assumed here.',
              'changes_to_reviewed_snapshot':False,'check_count':len(CHECKS)}
    csv_out('reviewer_followup_finite_rho.csv',finite)
    json_out('reviewer_followup.json',result); json_out('reviewer_followup_checks.json',CHECKS)
    report = ['# Consequential reviewer follow-up','',
              'Coda, collaborating with Andrei. This public derivative retains the scientific calculations prompted by Claude review. Private reviewer-record checks are omitted; original scientific source and input checks remain.','',
              'Candidate A native RACS proxy residual: east '+f'{r[0]:.6f}'+', north '+f'{r[1]:.6f}'+' arcsec. Conditional D values, without p-value or co-location interpretation:','',
              '| RA error convention | Added stochastic sigma | D(rho=-0.5) | D(rho=0) | D(rho=+0.5) |','|---|---:|---:|---:|---:|']
    for convention in ('ra_coordinate_arcsec','ra_tangent_arcsec'):
        for floor in (0.,.5,1.):
            vals = [next(x['D_conditional'] for x in finite if x['ra_error_convention']==convention and x['additional_stochastic_isotropic_sigma_arcsec']==floor and x['radio_rho']==rho) for rho in (-.5,0.,.5)]
            report.append(f'| {convention} | {floor:.1f} arcsec | {vals[0]:.6f} | {vals[1]:.6f} | {vals[2]:.6f} |')
    report += ['',f'A separate hypothetical fixed bias with norm <=1 arcsec gives a proxy geometric separation envelope of [{low:.6f}, {high:.6f}] arcsec. Combining it with the prior whole-catalog support diagnostic gives [{bias["survey_support_diagnostic_plus_bias_envelope_arcsec"][0]:.6f}, {bias["survey_support_diagnostic_plus_bias_envelope_arcsec"][1]:.6f}] arcsec. This is a bounded unknown vector, not a Gaussian floor, a measured calibration bound, or a confidence interval.',
               '', 'Eight independent profile cases test positive and negative boundary minima, both axis-aligned q=0 cases, an axis case whose zero-covariance solution is outside the allowed interval, a zero residual, an interior minimum and a near-singular radio boundary. Explicit inverse and a 20,001-point independent formula grid agree within recorded tolerances.',
               '', 'All seven source identities and native/printed separations <0.005 arcsec are asserted. RACS row IDs determine each tile, which determines the CADC product, canonical retrieval URL and hash-verified header. Header ICRS/equinox/telescope fields are checked. This mapping does not establish contributing observation times or weights. Source fitted shape/PA values are recorded but do not determine centroid covariance without a documented error derivation.',
               '',result['stale_error_assessment'],'',result['Jacobian_scope'],'',result['IR_next_requirement'],
               '',f'All {len(CHECKS)} recorded checks passed. Many checks are repeated across conventions/scenarios; this is not a count of independent scientific validations. No network or GPU was used.']
    (OUT/'reviewer_followup_RESULTS.md').write_text('\n'.join(report)+'\n',encoding='utf-8')
    generated = {str(p):sha(p) for p in OUT.iterdir() if p.is_file() and p.name.startswith(PREFIX) and p.name!='reviewer_followup_receipt.json'}
    receipt = {'started_utc':started,'completed_utc':datetime.now(timezone.utc).isoformat(),'status':'completed_all_checks_passed',
               'python_executable':sys.executable,'numpy_version':np.__version__,'astropy_version':astropy.__version__,
               'network':False,'gpu':False,'iers_auto_download':False,
               'thread_environment':{k:os.environ[k] for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS')},
               'input_sha256':INPUTS,'preserved_math_sha256':preserved,'new_output_sha256':generated,'check_count':len(CHECKS),
               'portable_input_sha256':{Path(p).relative_to(BASE.parent).as_posix():h for p,h in INPUTS.items()},
               'runtime_dependencies':['Python standard library','NumPy','Astropy','packaged math/audit_astrometry.py imported without executing main'],
               'portability':'All science inputs are relative to this package. Generated runtime receipts contain interpreter/input paths and require curation before redistribution.',
               'earlier_attempt':'First execution stopped at the NVSS source-name assertion: raw catalog lacks the J prefix present in the printed designation. The new checker now explicitly adds only that known NVSS designation prefix. No original source or reviewed artifact was changed.'}
    json_out('reviewer_followup_receipt.json',receipt)
    print(json.dumps({'status':receipt['status'],'check_count':len(CHECKS),'finite_correlations':finite,'fixed_bias':bias},indent=2))

if __name__=='__main__':
    main()
