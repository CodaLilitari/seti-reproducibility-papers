"""Independent falsification-first replay, Python stdlib only.

No controls are reconstructed. Probabilities below are arithmetic consistency
checks against printed pairs, not replacement statistical inferences.
"""
from pathlib import Path
import csv, json, math, re, sys, platform, hashlib, statistics
BASE=Path(__file__).resolve().parent
RAW=BASE/'inputs'
T=json.loads((BASE/'source_tables.json').read_text(encoding='utf8'))
def num(s): return float(re.search(r'[+-]?\d+(?:\.\d*)?',s.replace(' ',''))[0])
def pm(s): return [float(x) for x in s.split('\\pm')]
def prob(s):
    if '\\times' in s:
        a,ten,b=re.findall(r'[-+]?\d+',s);return float(a)*10**int(b), .5*10**int(b)
    return float(s),.5*10**(-len(s.split('.')[1]))
def sex(s,ra=False):
    q=s.replace('\\',' ').split(); sign=-1 if q[0].startswith('-') else 1
    return sign*(abs(float(q[0]))+float(q[1])/60+float(q[2])/3600)*(15 if ra else 1)
def sep(ra1,de1,ra2,de2):
    a,b,c,d=map(math.radians,(ra1,de1,ra2,de2))
    h=math.sin((b-d)/2)**2+math.cos(b)*math.cos(d)*math.sin((a-c)/2)**2
    return math.degrees(2*math.asin(min(1,math.sqrt(h))))*3600
def golden(f,lo,hi):
    # Grid first prevents selecting a secondary epoch-distance minimum.
    grid=[lo+(hi-lo)*i/2000 for i in range(2001)]
    k=min(range(len(grid)),key=lambda i:f(grid[i]));lo=grid[max(0,k-1)];hi=grid[min(2000,k+1)]
    for _ in range(90):
        a=lo+(hi-lo)*.3819660112501051;b=lo+(hi-lo)*.6180339887498949
        if f(a)<f(b):hi=b
        else:lo=a
    x=(lo+hi)/2;return x,f(x)
gaia={r['source_id']:{k:float(v) for k,v in r.items() if k!='source_id'} for r in csv.DictReader((RAW/'gaia_dr3_snapshot_20260925.csv').open())}
assert hashlib.sha256((RAW/'gaia_dr3_snapshot_20260925.csv').read_bytes()).hexdigest()=='ebc0f022f36d65525a96082be2c9b7d96302e17f24a02276af50a5fc70dd5c8b', 'Pinned Gaia snapshot changed'
stars={}
for r in T['S2.T1'][1:]:
    letter=r[0][0];stars[letter]={'source_id':r[1],'table_ra':num(r[2].split(',')[0]),'table_dec':num(r[2].split(',')[1]),'epoch12':float(r[9]),'epoch34':float(r[10]),**gaia[r[1]]}
rows=[]
for tid,letters in [('S3.T4','AB'),('S3.T5','CDEF'),('S3.T6','HIJ')]:
    rs=[r for r in T[tid] if len(r)>5 and r[1] in ('W1','W2','W3','W4')]
    for i,r in enumerate(rs):
        letter=letters[i//4];b=r[1];st=stars[letter]
        rows.append({'candidate':letter,'band':b,'epoch':st['epoch12' if b in ('W1','W2') else 'epoch34'],'ra':sex(r[2],True),'dec':sex(r[3]),'centroid_uncertainty':float(r[4]),'r_printed':pm(r[5])[0],'r_uncertainty':pm(r[5])[1],'source_table':tid})
def stellar(st,t,model):
    originra,origindec=st['ra'],st['dec'];dt=t-2016
    if model=='offset_minus16':dt-=16
    elif model=='no_propagation':dt=0
    elif model=='double_propagation':dt*=2
    elif model=='sign_reversed':dt=-dt
    elif model=='year2000_reference_on_DR3':dt=t-2000
    elif model=='printed_table1_as2016':originra,origindec=st['table_ra'],st['table_dec']
    cos=math.cos(math.radians(origindec))
    if model=='omit_RA_cos':cos=1
    elif model=='duplicate_RA_cos':cos*=cos
    return originra+st['pmra']*dt/(3.6e6*cos),origindec+st['pmdec']*dt/3.6e6
models=['correct_2016','offset_minus16','no_propagation','double_propagation','sign_reversed','year2000_reference_on_DR3','printed_table1_as2016','omit_RA_cos','duplicate_RA_cos']
for r in rows:
    st=stars[r['candidate']]
    for m in models:r['r_'+m]=sep(r['ra'],r['dec'],*stellar(st,r['epoch'],m))
    # Worst possible radial perturbation from printed centroid and offset precision.
    dec_half=.0005 if r['candidate'] in 'HIJ' else .005
    r['round_bound_arcsec']=.005+math.hypot(.0075*math.cos(math.radians(r['dec'])),dec_half)
    r['minus16_round_consistent']=abs(r['r_offset_minus16']-r['r_printed'])<=r['round_bound_arcsec']
    # Deliberately generous: full opposite parallax phase (2*pi), PM errors at
    # three sigma with independent-component norm, up to one whole year epoch
    # mistake, and the printed-coordinate/radius rounding bound.
    r['generous_correct_epoch_allowance_arcsec']=r['round_bound_arcsec']+2*st['parallax']/1000+3*math.hypot(st['pmra_error'],st['pmdec_error'])*abs(r['epoch']-2016)/1000+math.hypot(st['pmra'],st['pmdec'])/1000
    r['correct_epoch_within_generous_allowance']=abs(r['r_correct_2016']-r['r_printed'])<=r['generous_correct_epoch_allowance_arcsec']
model_report=[]
for group in ['ABCDEF','HIJ','ABCDEFHIJ']:
    subset=[r for r in rows if r['candidate'] in group]
    for m in models:
        ds=[r['r_'+m]-r['r_printed'] for r in subset]
        model_report.append({'group':group,'model':m,'n':len(ds),'rms_arcsec':math.sqrt(statistics.mean(x*x for x in ds)),'max_abs_arcsec':max(map(abs,ds)),'within_print_rounding':sum(abs(d)<=r['round_bound_arcsec'] for d,r in zip(ds,subset))})
def delta_loss(subset,d):
    return sum((sep(r['ra'],r['dec'],*stellar(stars[r['candidate']],r['epoch']+d,'correct_2016'))-r['r_printed'])**2 for r in subset)
epoch_fits=[]
for group in list('ABCDEFHIJ')+['ABCDEF','HIJ']:
    subset=[r for r in rows if r['candidate'] in group]
    shift,loss=golden(lambda d:delta_loss(subset,d),-40,40)
    epoch_fits.append({'group':group,'best_epoch_shift_years':shift,'rms_arcsec':math.sqrt(loss/len(subset)),'minus16_rms_arcsec':math.sqrt(delta_loss(subset,-16)/len(subset)),'zero_rms_arcsec':math.sqrt(delta_loss(subset,0)/len(subset))})
# Rayleigh checks. Since scale and probability are printed, interval consistency
# is the proper question; equality to central printed values is too strict.
tr=[];letter=None
for v in T['S3.T10'][2:]:
    if not v[0].startswith('W'):letter=v[0][0];v=v[1:]
    band,n,sig,ps,zs,note=v;sigma,sigmaerr=pm(sig);p,ph=prob(ps);z,zerr=pm(zs)
    r=next(x for x in rows if x['candidate']==letter and x['band']==band)
    rp=r['r_printed'];slo,shi=sigma-.005,sigma+.005;rlo,rhi=rp-.005,rp+.005;plo=max(0,p-ph);phi=min(1,p+ph)
    attainable_lo=math.exp(-rhi*rhi/(2*slo*slo));attainable_hi=math.exp(-rlo*rlo/(2*shi*shi))
    sf_at_z=.5*math.erfc(z/math.sqrt(2))
    inv=lambda pp,ss: ss*math.sqrt(-2*math.log(pp))
    central_implied=inv(p,sigma)
    r_implied_lo=inv(phi,slo);r_implied_hi=inv(plo,shi) if plo>0 else math.inf
    loc=rp-central_implied
    alt_r=r['r_correct_2016']; alt_lo=math.exp(-(alt_r+r['round_bound_arcsec']-.005)**2/(2*slo*slo)); alt_hi=math.exp(-max(0,alt_r-r['round_bound_arcsec']+.005)**2/(2*shi*shi))
    alternatives={
        'rayleigh_sf':lambda rr,ss: math.exp(-rr*rr/(2*ss*ss)),
        'rayleigh_cdf':lambda rr,ss: -math.expm1(-rr*rr/(2*ss*ss)),
        'rayleigh_rms_scale':lambda rr,ss:math.exp(-rr*rr/(ss*ss)),
        'rayleigh_scale_twice_variance':lambda rr,ss:math.exp(-rr*rr/(4*ss*ss)),
        'gaussian_two_sided':lambda rr,ss:math.erfc(rr/ss/math.sqrt(2)),
        'gaussian_one_sided':lambda rr,ss:.5*math.erfc(rr/ss/math.sqrt(2)),
    }
    alt_matches={}
    for key,fn in alternatives.items():
        corners=[fn(rr,ss) for rr in [rlo,rhi] for ss in [slo,shi]]
        alt_matches[key+'_rounding_compatible']=min(corners)<=phi and max(corners)>=plo
    correct_round=r['round_bound_arcsec']-.005
    tr.append({'candidate':letter,'band':band,'N':int(n),'sigma_printed':sigma,'sigma_uncertainty':sigmaerr,'p_printed':p,'z_printed':z,'r_printed':rp,'r_implied_central':central_implied,'r_implied_min_rounding':r_implied_lo,'r_implied_max_rounding':r_implied_hi,'r_printed_rounding_compatible':attainable_lo<=phi and attainable_hi>=plo,'p_from_printed_pair':math.exp(-rp*rp/(2*sigma*sigma)),'p_attainable_min':attainable_lo,'p_attainable_max':attainable_hi,'p_rounding_min':plo,'p_rounding_max':phi,'z_probability':sf_at_z,'z_p_rounding_compatible':plo<=sf_at_z<=phi,'implied_loc_at_printed_pair':loc,'loc_printed_min':rlo-r_implied_hi,'loc_printed_max':rhi-r_implied_lo,'loc_epoch_correct_min':alt_r-correct_round-r_implied_hi,'loc_epoch_correct_max':alt_r+correct_round-r_implied_lo,'required_loc_using_epoch_correct_r':alt_r-central_implied,'required_sigma_using_epoch_correct_r':alt_r/math.sqrt(-2*math.log(p)),'epoch_correct_r_compatible_with_printed_scale_probability':alt_lo<=phi and alt_hi>=plo,'scale_uncertainty_ratio_to_sigma_over_sqrt2N':sigmaerr/(sigma/math.sqrt(2*int(n))),**alt_matches})
def csvout(name,data):
    with (BASE/name).open('w',newline='',encoding='utf8') as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
csvout('candidate_radius_models.csv',rows);csvout('model_comparison.csv',model_report);csvout('effective_epoch_fits.csv',epoch_fits);csvout('rayleigh_rounding_tests.csv',tr)
loc_ranges=[]
for group in ['ABCDEF','HIJ','ABCDEFHIJ']:
    ts=[r for r in tr if r['candidate'] in group]
    loc_ranges.append({'group':group,'n':len(ts),'correct_r_compatible':sum(r['epoch_correct_r_compatible_with_printed_scale_probability'] for r in ts),'single_loc_intersection_using_printed_r':[max(r['loc_printed_min'] for r in ts),min(r['loc_printed_max'] for r in ts)],'single_loc_intersection_using_correct_r':[max(r['loc_epoch_correct_min'] for r in ts),min(r['loc_epoch_correct_max'] for r in ts)]})
assert len(rows)==36 and len(tr)==36
assert abs(sep(0,0,1,0)-3600)<1e-10
assert abs(sex('-26\\ 52\\ 02.97')+26.86749166666667)<1e-12
assert len({(r['candidate'],r['band']) for r in rows})==36
assert all(r['r_printed_rounding_compatible'] for r in tr)
assert all(r['minus16_round_consistent'] for r in rows if r['candidate'] in 'ABCDEF')
summary={
    'method':'Independent pinned-source extraction; stdlib spherical separations and one-dimensional minimization. Gaia snapshot source IDs joined explicitly. No old review script imported.',
    'python':sys.version,'executable':sys.executable,'platform':platform.platform(),
    'inputs':{'inputs/gaia_dr3_snapshot_20260925.csv':hashlib.sha256((RAW/'gaia_dr3_snapshot_20260925.csv').read_bytes()).hexdigest(),'source_tables.json':hashlib.sha256((BASE/'source_tables.json').read_bytes()).hexdigest()},
    'gaia_snapshot_date':'2026-09-25',
    'rayleigh_all_printed_pairs_round_compatible':sum(r['r_printed_rounding_compatible'] for r in tr),
    'n_rayleigh_rows':len(tr),
    'epoch_correct_r_pairs_round_compatible':sum(r['epoch_correct_r_compatible_with_printed_scale_probability'] for r in tr),
    'epoch_fits':epoch_fits,'models':model_report,
    'loc_central_range':[min(r['implied_loc_at_printed_pair'] for r in tr),max(r['implied_loc_at_printed_pair'] for r in tr)],
    'loc_intersections':loc_ranges,
    'formula_compatibility_counts':{k:sum(r[k+'_rounding_compatible'] for r in tr) for k in alternatives},
}
(BASE/'results_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf8')
print(json.dumps(summary,indent=2))
