"""Bounded, explicitly post-hoc diagnostic work on the known TOI-270 host.
No production search criteria, immutable source or standard-bls files are edited.
"""
from __future__ import annotations
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS','BLIS_NUM_THREADS'): os.environ[k]='1'
import sys, json, hashlib, importlib.util, time, warnings, inspect
from pathlib import Path
from datetime import datetime, timezone
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent;STANDARD=ROOT.parent/'standard-bls'
from replay import block_network,memory_peak,verify_manifest,SOURCE
sys.addaudithook(block_network)
import numpy as np
from astropy.io import fits
from astropy.timeseries import BoxLeastSquares
import astropy
spec=importlib.util.spec_from_file_location('crosscheck_readonly',STANDARD/'run_crosscheck.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
PERIODS=1/np.linspace(1/13.,1/.6,12000);DURATIONS=np.array([1.,1.5,2.,2.5,3.,4.])/24
B_PERIOD=3.35992 # explicit POST-HOC known-catalog comparison, never blind input

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def py(x):
    if isinstance(x,np.ndarray):return [py(y) for y in x]
    if isinstance(x,np.generic):return py(x.item())
    if isinstance(x,float) and not np.isfinite(x):return None
    if isinstance(x,dict):return {k:py(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [py(v) for v in x]
    return x

def fixed_keep(t,peaks,mask=.75):
    keep=np.ones(len(t),bool)
    for p in peaks:
        keep &= np.abs(c.legacy.phase_distance(t,p['period_days'],p['epoch_btjd']))>mask*p['duration_hours']/24
    return keep

def short_peak(r,ix):
    return {'period_days':float(r.period[ix]),'epoch_btjd':float(r.transit_time[ix]),
        'duration_hours':float(r.duration[ix]*24),'power':float(r.power[ix]),
        'depth_ppm':float(r.depth[ix]*1e6),'formal_depth_snr':float(r.depth_snr[ix])}

def rank_b(t,y,dy,keep):
    m=BoxLeastSquares(t[keep],y[keep],dy[keep]);r=m.power(PERIODS,DURATIONS,objective='likelihood',method='fast',oversample=10)
    b=m.power([B_PERIOD],DURATIONS,objective='likelihood',method='fast',oversample=10)
    close=np.flatnonzero(abs(PERIODS-B_PERIOD)<.01);ix=int(close[np.argmax(r.power[close])]);top=int(np.argmax(r.power))
    return {'retained':int(keep.sum()),'maximum':short_peak(r,top),'best_grid_point_within_0p01d_of_b':short_peak(r,ix),
        'b_neighborhood_grid_point_rank':int(1+(r.power>r.power[ix]).sum()),
        'catalog_period_phase_optimized':short_peak(b,0),
        'grid_points_with_power_above_exact_b_period':int((r.power>b.power[0]).sum()),
        'rank_note':'Rank counts 12000 correlated frequency-grid points, not independent peaks or a p-value; exact known period optimizes phase/duration post hoc.'}

def five_peak(t,y,dy):
    keep=np.ones(len(t),bool);peaks=[]
    for i in range(5):
        model=BoxLeastSquares(t[keep],y[keep],dy[keep]);r=model.power(PERIODS,DURATIONS,objective='likelihood',method='fast',oversample=10)
        ix=int(np.argmax(r.power));peak=short_peak(r,ix);peak['iteration']=i+1
        inside=model.transit_mask(t,peak['period_days'],peak['duration_hours']/24,peak['epoch_btjd'])&keep
        _,cts=np.unique(np.rint((t[inside]-peak['epoch_btjd'])/peak['period_days']).astype(int),return_counts=True)
        peak['event_counts']=cts.tolist();peaks.append(peak)
        keep &= np.abs(c.legacy.phase_distance(t,peak['period_days'],peak['epoch_btjd']))>.75*peak['duration_hours']/24
    return peaks

def matched_depths(t,arrays,keep,peak):
    p=peak['period_days'];epoch=peak['epoch_btjd'];duration=peak['duration_hours']/24
    inside=(abs(c.legacy.phase_distance(t,p,epoch))<=duration/2)&keep;outside=keep&~inside
    out={'ephemeris':peak,'n_in':int(inside.sum()),'global_depths_ppm':{},'events':[]}
    for key,y in arrays.items():out['global_depths_ppm'][key]=float((y[outside].mean()-y[inside].mean())*1e6)
    cycles=np.unique(np.rint((t[inside]-epoch)/p).astype(int))
    for cycle in cycles:
        center=epoch+int(cycle)*p;im=inside&(abs(t-center)<duration);om=outside&(abs(t-center)<2*duration)
        row={'cycle':int(cycle),'center_btjd':center,'n_in':int(im.sum()),'n_local_out':int(om.sum()),
            'n_left_out':int((om&(t<center)).sum()),'n_right_out':int((om&(t>center)).sum()),'local_depths_ppm':{}}
        for key,y in arrays.items():row['local_depths_ppm'][key]=float((y[om].mean()-y[im].mean())*1e6) if om.any() else None
        out['events'].append(row)
    return out

def ones_sum(blob):
    assert len(blob)%4==0
    value=int(np.frombuffer(blob,dtype='>u4').sum(dtype=np.uint64))
    while value>>32:value=(value&0xffffffff)+(value>>32)
    return value

def checksums(path):
    raw=path.read_bytes();out=[]
    with fits.open(path,memmap=False,checksum=False) as h:
        for i,x in enumerate(h):
            info=x.fileinfo();start=info['hdrLoc'];end=info['datLoc']+info['datSpan']
            raw_sum=ones_sum(raw[start:end]);data_sum=ones_sum(raw[info['datLoc']:end])
            actual=x._calculate_checksum(data_sum)
            out.append({'hdu':i,'name':x.name,'header_checksum':x.header.get('CHECKSUM'),
                'datasum_card_present':'DATASUM' in x.header,'astropy_verify_checksum':x.verify_checksum(),
                'astropy_verify_datasum':x.verify_datasum(),'raw_hdu_ones_complement_sum_hex':f'{raw_sum:08x}',
                'raw_hdu_sum_is_negative_zero':raw_sum==0xffffffff,'raw_data_ones_complement_sum':data_sum,
                'recomputed_checksum_with_actual_data':actual,'matches_stored_when_data_included':actual==x.header.get('CHECKSUM')})
    return out

def reconstruct(t,sap,pdc):
    delivered=np.loadtxt(SOURCE/'data/toi270_s4_binned.csv',delimiter=',')
    groups=np.floor(t*48).astype(int);indices=[np.flatnonzero(groups==g) for g in np.unique(groups) if (groups==g).sum()>=10]
    b=np.array([[t[ix].mean(),sap[ix].mean(),pdc[ix].mean()] for ix in indices])
    reconstructed=np.c_[np.rint(b[:,0]*1e6),np.rint((b[:,1]/np.median(b[:,1])-1)*1e6),np.rint((b[:,2]/np.median(b[:,2])-1)*1e6)]
    delta=reconstructed-delivered
    out={'bins':len(indices),'cadences':sum(map(len,indices)),
        'medians_full_precision':{'sap':float(np.median(b[:,1])),'pdc':float(np.median(b[:,2]))},
        'delivered_declared_medians':{'sap':8314.016406666666,'pdc':9555.939393333334},
        'time_integer_delta_range':[float(delta[:,0].min()),float(delta[:,0].max())],
        'time_rms_microdays':float(np.sqrt(np.mean(delta[:,0]**2))),
        'mismatching_bins_by_column':(delta!=0).sum(axis=0).tolist(),
        'max_abs_delta_by_column':abs(delta).max(axis=0).tolist(),'rounding_probes':{}}
    for places in [3,4,5,6,7]:
        values=np.array([np.round(t,places)[ix].mean() for ix in indices]);candidate=np.rint(values*1e6)
        out['rounding_probes'][f'time_samples_{places}_decimal_places']={'max_abs_delta_microdays':float(abs(candidate-delivered[:,0]).max()),'exact_bins':int((candidate==delivered[:,0]).sum())}
    for places in [1,2,3,4]:
        sr=np.round(sap,places);pr=np.round(pdc,places)
        means=np.array([[sr[ix].mean(),pr[ix].mean()] for ix in indices]);med=np.median(means,axis=0)
        candidate=np.rint((means/med-1)*1e6)
        out['rounding_probes'][f'flux_samples_{places}_decimal_places']={'median_sap_pdc':med.tolist(),
            'max_abs_delta_ppm':abs(candidate-delivered[:,1:]).max(axis=0).tolist(),'exact_bins':(candidate==delivered[:,1:]).sum(axis=0).tolist()}
    return out

def small_synthetic():
    rng=np.random.default_rng(42317);t=np.arange(0,26,1/48);epoch=.4;dur=1.5/24
    periods=np.array([B_PERIOD/2,B_PERIOD,2*B_PERIOD,4*B_PERIOD]);dy=np.full(len(t),.0002)
    noise=rng.normal(0,.0002,len(t));cases={}
    for name,y,keep in [('flat_null',np.zeros(len(t)),np.ones(len(t),bool)),
                        ('single_white_noise_null',noise,np.ones(len(t),bool)),
                        ('known_box_injection',noise-.001*(abs(c.legacy.phase_distance(t,B_PERIOD,epoch))<dur/2),np.ones(len(t),bool)),
                        ('injection_with_central_gap',noise-.001*(abs(c.legacy.phase_distance(t,B_PERIOD,epoch))<dur/2),~((t>9)&(t<15))),
                        ('equal_eclipses_half_orbit_alias',noise-.001*(abs(c.legacy.phase_distance(t,B_PERIOD,epoch))<dur/2),np.ones(len(t),bool))]:
        m=BoxLeastSquares(t[keep],y[keep],dy[keep]);r=m.power(periods,[dur],objective='likelihood',method='fast',oversample=10);ix=int(np.argmax(r.power))
        cases[name]={'peak':short_peak(r,ix),'tested_periods_days':periods.tolist(),'powers':r.power.tolist()}
    cases['equal_eclipses_half_orbit_alias']['construction']='Two equal eclipses per true binary orbital period 2*3.35992 d are exactly the same box sequence as a 3.35992 d planet model; photometric period recovery cannot distinguish these constructions.'
    return {'seed':42317,'n':len(t),'cases':cases,'scope':'Four specified alias periods and one noise realization only; no false-alarm or completeness calibration.'}

def main():
    start=time.monotonic();before={str(p):digest(p) for p in STANDARD.rglob('*') if p.is_file()}
    root_results=json.loads((STANDARD/'crosscheck-results.json').read_text());prior=root_results['cases']['s4_full_formal_error_weighted']
    with warnings.catch_warnings(record=True) as caught:
        t,sap,pdc,se,pe,meta=c.series(STANDARD/'data/toi270-s0004.fits')
    warning_text=[str(w.message) for w in caught]
    pn=pdc/np.median(pdc);sn=sap/np.median(sap)
    y,tr=c.legacy.detrend(t,pn);ys,ts=c.legacy.detrend(t,sn);dy=pe/np.median(pdc)/tr
    out={'scope':'Explicitly post-hoc exploratory development diagnostics; original outcomes unchanged; formal SNR is not FAP.',
        'generated_utc':datetime.now(timezone.utc).isoformat(),'python':sys.version,'numpy':np.__version__,'astropy':astropy.__version__,
        'source_sha256':meta['sha256'],'five_peak_extension':five_peak(t,y,dy),
        'b_after_fixed_c_d_masks':rank_b(t,y,dy,fixed_keep(t,prior[:2])), 'detrend_ablation':{},'mask_ablation':{}}
    for window in [.5,2.]:
        c.legacy.CONFIG['median_window_days']=window
        yy,tt=c.legacy.detrend(t,pn);dd=pe/np.median(pdc)/tt
        out['detrend_ablation'][str(window)]=rank_b(t,yy,dd,fixed_keep(t,prior[:2]))
    c.legacy.CONFIG['median_window_days']=1.
    for mask in [.5,1.,1.5]:out['mask_ablation'][str(mask)]=rank_b(t,y,dy,fixed_keep(t,prior[:2],mask))
    arrays={'sap_raw_median_normalized':sn-1,'pdc_raw_median_normalized':pn-1,'sap_detrended':ys,'pdc_detrended':y}
    legacy_peaks=json.loads((SOURCE/'results/search_results.json').read_text())['peaks']
    out['third_peak_matched_full_resolution']={
        'standard_box':matched_depths(t,arrays,fixed_keep(t,prior[:2]),prior[2]),
        'legacy_box':matched_depths(t,arrays,fixed_keep(t,legacy_peaks[:2]),legacy_peaks[2])}
    b5=root_results['cases']['s5_full_formal_error_weighted'][2]
    out['s5_recovered_b_ephemeris_fixed_in_s4']=matched_depths(t,arrays,fixed_keep(t,prior[:2]),b5)
    out['export_reconstruction_diagnostics']=reconstruct(t,sap,pdc)
    out['fits_checksum_diagnostics']={str(s):checksums(STANDARD/'data'/f'toi270-s{s:04d}.fits') for s in [4,5]}
    out['astropy_checksum_implementation']=inspect.getsource(type(fits.PrimaryHDU()).verify_checksum)
    out['initial_fits_warnings']=warning_text
    out['small_synthetic']=small_synthetic()
    after={str(p):digest(p) for p in STANDARD.rglob('*') if p.is_file()}
    out['standard_files_unchanged']=before==after
    out['original_manifest_after']=verify_manifest(SOURCE)
    out['elapsed_seconds']=time.monotonic()-start;out['peak_working_set_bytes']=memory_peak()
    assert out['standard_files_unchanged'] and not out['original_manifest_after']['failures']
    assert out['peak_working_set_bytes']<1024**3
    (ROOT/'posthoc_diagnostics_results.json').write_text(json.dumps(py(out),indent=2,allow_nan=False)+'\n')
    print(json.dumps(py({'elapsed_seconds':out['elapsed_seconds'],'peak_working_set_bytes':out['peak_working_set_bytes'],
        'five_periods':[p['period_days'] for p in out['five_peak_extension']],
        'baseline_b':out['b_after_fixed_c_d_masks'],'detrend':out['detrend_ablation'],'mask':out['mask_ablation'],
        'checksum_valid':{k:[p['raw_hdu_sum_is_negative_zero'] for p in v] for k,v in out['fits_checksum_diagnostics'].items()},
        'reconstruction':out['export_reconstruction_diagnostics']}),indent=2))

if __name__=='__main__':main()
