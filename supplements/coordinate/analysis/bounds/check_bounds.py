"""Conditional reverse-triangle control-scale bounds; Python stdlib only.

This is an algebraic test under an explicit reference-shift hypothesis, not a
reconstruction of signed control residual vectors or a corrected Table 10.
"""
from pathlib import Path
import csv,json,math,hashlib,sys,platform
BASE=Path(__file__).resolve().parent
EXPECTED={
    'A_controls_transcribed.csv':'9310f8e93b0c0da997f85abacdb882ce3702d9ef3ee0884aa1338fa34872a4a2',
    'candidate_radius_models.csv':'846bffa0d5a7f084f22fb2c9c74b0a04201a522b89ff3ea32b22ee710a6f2eab',
    'gaia_A_controls.csv':'4bd7293532668068e74a875e459775c64919d495109161fb1cf6ccadf4e9d737',
    'gaia_A_control_uncertainties.csv':'38b63656356082d673d0908f56e93a85fd464890aa8d9268923f17edf4f02d23',
}
for name,digest in EXPECTED.items():
    assert hashlib.sha256((BASE/'inputs'/name).read_bytes()).hexdigest()==digest, f'Input bytes changed: {name}'
controls=list(csv.DictReader((BASE/'inputs/A_controls_transcribed.csv').open()))
gaia={r['source_id']:r for r in csv.DictReader((BASE/'inputs/gaia_A_controls.csv').open())}
errors={r['source_id']:r for r in csv.DictReader((BASE/'inputs/gaia_A_control_uncertainties.csv').open())}
candidates={(r['candidate'],r['band']):r for r in csv.DictReader((BASE/'inputs/candidate_radius_models.csv').open())}
assert len(controls)==len(gaia)==len(errors)==15
assert set(gaia)==set(errors)=={r['gaia_dr3_source_id'] for r in controls}
rows=[]
for row in controls:
    sid=row['gaia_dr3_source_id'];g=gaia[sid];e=errors[sid]
    mua,mud=map(float,(g['pmra'],g['pmdec']));sa,sd=map(float,(e['pmra_error'],e['pmdec_error']))
    rho=float(e['pmra_pmdec_corr']);par=float(g['parallax']);pare=float(e['parallax_error'])
    d=16*math.hypot(mua,mud)/1000
    epsilon_pm=3*16*math.hypot(sa,sd)/1000
    epsilon_par=2*par/1000
    epsilon=epsilon_pm+epsilon_par
    epsilon_larger=epsilon_pm+2*(par+3*pare)/1000
    # Largest covariance eigenvalue <= trace for every valid correlation.
    trace=sa*sa+sd*sd
    eigmax=.5*(trace+math.sqrt((sa*sa-sd*sd)**2+4*(rho*sa*sd)**2))
    assert eigmax<=trace+1e-15 and abs(rho)<=1
    for band in ('W1','W2'):
        r=float(row[band.lower()+'_offset_arcsec']);roundhalf=float(row['label_resolution_arcsec'])/2
        lo,hi=max(0,r-roundhalf),r+roundhalf
        dlo,dhi=max(0,d-epsilon),d+epsilon
        # Gap between the allowed length intervals for residual and correction.
        lower=max(0,dlo-hi,lo-dhi)
        equivalent=max(0,abs(d-r)-epsilon-roundhalf)
        assert abs(lower-equivalent)<1e-14
        larger_margin_lb=max(0,abs(d-r)-epsilon_larger-roundhalf)
        rows.append({'figure_order':int(row['figure_order']),'source_id':sid,'band':band,
                     'r_printed_arcsec':r,'round_halfwidth_arcsec':roundhalf,
                     'pmra_masyr':mua,'pmdec_masyr':mud,'pmra_error_masyr':sa,'pmdec_error_masyr':sd,
                     'pmra_pmdec_corr':rho,'parallax_mas':par,'parallax_error_mas':pare,
                     'nominal_16yr_displacement_arcsec':d,'pm_3sigma_norm_allowance_arcsec':epsilon_pm,
                     'parallax_allowance_arcsec':epsilon_par,'total_positional_allowance_arcsec':epsilon,
                     'corrected_radius_lower_bound_arcsec':lower,
                     'one_sided_displacement_minus_radius_bound_arcsec':max(0,dlo-hi),
                     'nominal_no_allowance_lower_bound_arcsec':abs(d-r),
                     'larger_parallax_margin_lower_bound_arcsec':larger_margin_lb,
                     'binary_mixed_branch_radius_lower_bound_arcsec':min(lo,lower),
                     'largest_cov_eigenvalue_mas2yr2':eigmax,'covariance_trace_mas2yr2':trace})
summary={}
for band in ('W1','W2'):
    rr=[r for r in rows if r['band']==band];n=len(rr)
    def scale(key):return math.sqrt(sum(r[key]**2 for r in rr)/(2*n))
    s=scale('corrected_radius_lower_bound_arcsec')
    s_larger=scale('larger_parallax_margin_lower_bound_arcsec')
    s_mixed=scale('binary_mixed_branch_radius_lower_bound_arcsec')
    c=candidates[('A',band)];rc=float(c['r_correct_2016'])
    # The saved candidate bound includes radial print rounding; only centroid
    # coordinate-rounding enters r_correct itself, so subtract .005 here.
    centroid_round=float(c['round_bound_arcsec'])-.005
    summary[band]={'N':n,'scale_lower_bound_arcsec':s,
                   'reported_scale_6decimals':{'W1':.485307,'W2':.467973}[band],
                   'one_sided_only_scale_lower_bound_arcsec':scale('one_sided_displacement_minus_radius_bound_arcsec'),
                   'candidate_correct_central_radius_arcsec':rc,
                   'survival_lower_bound_at_candidate_central_radius':math.exp(-rc*rc/(2*s*s)),
                   'reported_probability_6decimals':{'W1':.933124,'W2':.972294}[band],
                   'candidate_centroid_rounding_allowance_arcsec':centroid_round,
                   'survival_lower_bound_with_candidate_centroid_rounding':math.exp(-(rc+centroid_round)**2/(2*s*s)),
                   'scale_lower_bound_with_parallax_plus_3sigma_arcsec':s_larger,
                   'survival_lower_bound_with_larger_parallax_margin':math.exp(-rc*rc/(2*s_larger*s_larger)),
                   'binary_mixed_branch_scale_lower_bound_arcsec':s_mixed,
                   'binary_mixed_survival_lower_bound_at_central_candidate':math.exp(-rc*rc/(2*s_mixed*s_mixed)),
                   'binary_mixed_survival_lower_bound_with_candidate_rounding':math.exp(-(rc+centroid_round)**2/(2*s_mixed*s_mixed)),
                   'positive_control_radius_bounds':sum(r['corrected_radius_lower_bound_arcsec']>0 for r in rr),
                   'hypothesis':'All15 reference points share an extra minus16yr shift; identical centroids, membership, fixedzero Rayleigh MLE; PM and parallax correction-length uncertainty stays within explicitly allowed bounds.'}
    assert round(s,6)==summary[band]['reported_scale_6decimals']
    assert round(summary[band]['survival_lower_bound_at_candidate_central_radius'],6)==summary[band]['reported_probability_6decimals']
with (BASE/'per_source_bounds.csv').open('w',newline='',encoding='utf8') as f:
    w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
result={'band_results':summary,'runtime':{'python':sys.version,'executable':sys.executable,'platform':platform.platform()},
        'input_hashes':{p.relative_to(BASE).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((BASE/'inputs').glob('*.csv'))},
        'formula':'l_i=max(0,abs(16*hypot(pmra,pmdec)/1000-r_i)-.005-3*16*hypot(pmra_error,pmdec_error)/1000-2*parallax/1000); sigma_lb=sqrt(sum(l_i^2)/(2*N)); p_lb=exp(-r_candidate^2/(2*sigma_lb^2))',
        'status':'Conditional geometric inequalities; no recovered signed centroids or historical estimator; statistical confidence not assigned.'}
(BASE/'bound_results.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps(result,indent=2))
