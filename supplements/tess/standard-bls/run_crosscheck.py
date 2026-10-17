"""Small CPU-only Astropy comparison on a known development host.
No catalog ephemerides are supplied to search. No survey target is selected.
"""
import os
for name in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[name]='1'
import sys, json, hashlib, platform, time, datetime, importlib.util
from pathlib import Path
import numpy as np
import astropy
from astropy.io import fits
from astropy.timeseries import BoxLeastSquares

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'source'/'planet_hunt_tess_development_2026-10-08'
spec=importlib.util.spec_from_file_location('delivered_search',SOURCE/'search.py')
legacy=importlib.util.module_from_spec(spec);spec.loader.exec_module(legacy)
CONFIG={'period_min_days':.6,'period_max_days':13.,'frequency_trials':12000,
 'duration_hours':[1.,1.5,2.,2.5,3.,4.],'iterations':3,'oversample':10,
 'detrending':'unchanged delivered one-day running median, gaps >0.5d',
 'mask_half_duration':.75,'quality_mask':'QUALITY==0; finite positive SAP/PDC and positive formal errors',
 'scope':'known-host development only, S4 and immediately subsequent S5; no blind validation',
 'acceptance':'report maxima and event coverage even if failed; no outcome-driven tuning or replacement'}

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def pure(x):
    if isinstance(x,np.ndarray): return [pure(y) for y in x]
    if isinstance(x,np.generic): return x.item()
    if isinstance(x,dict): return {k:pure(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)): return [pure(v) for v in x]
    return x

def series(path):
    with fits.open(path,memmap=False,checksum=True) as h:
        d=h[1].data
        meta={'path':str(path),'sha256':digest(path),'rows':len(d),
              'primary':{k:h[0].header.get(k) for k in ['TICID','SECTOR','DATA_REL']},
              'time':{k:h[1].header.get(k) for k in ['BJDREFI','BJDREFF','TIMESYS','TIMEDEL']},
              'checksums':[{'checksum':x.verify_checksum(),'datasum':x.verify_datasum()} for x in h]}
        ok=(d['QUALITY']==0)
        for k in ['TIME','SAP_FLUX','PDCSAP_FLUX','SAP_FLUX_ERR','PDCSAP_FLUX_ERR']:
            ok &= np.isfinite(d[k])
        for k in ['SAP_FLUX','PDCSAP_FLUX','SAP_FLUX_ERR','PDCSAP_FLUX_ERR']: ok &= d[k]>0
        t=np.array(d['TIME'][ok],dtype=float)
        if np.any(np.diff(t)<=0): raise ValueError('unsorted or duplicate time')
        sap=np.array(d['SAP_FLUX'][ok],dtype=float);pdc=np.array(d['PDCSAP_FLUX'][ok],dtype=float)
        se=np.array(d['SAP_FLUX_ERR'][ok],dtype=float);pe=np.array(d['PDCSAP_FLUX_ERR'][ok],dtype=float)
        meta['retained']=len(t)
    return t,sap,pdc,se,pe,meta

def search(t,y,ys,dy=None):
    periods=1/np.linspace(1/13.,1/.6,12000)
    keep=np.ones(len(t),dtype=bool);peaks=[]
    for i in range(3):
        model=BoxLeastSquares(t[keep],y[keep],None if dy is None else dy[keep])
        r=model.power(periods,np.array(CONFIG['duration_hours'])/24,objective='likelihood',method='fast',oversample=10)
        ix=int(np.argmax(r.power));p=float(r.period[ix]);dur=float(r.duration[ix]);epoch=float(r.transit_time[ix])
        inside=model.transit_mask(t,p,dur,epoch)&keep
        outside=keep&~inside
        cycles=np.rint((t[inside]-epoch)/p).astype(int)
        ev,counts=np.unique(cycles,return_counts=True)
        events=[]
        for e,c in zip(ev,counts):
            center=epoch+int(e)*p
            im=inside&(np.abs(t-center)<dur)
            om=outside&(np.abs(t-center)<2*dur)
            events.append({'cycle':int(e),'center_btjd':center,'n_in':int(c),'n_local_out':int(om.sum()),
             'local_depth_ppm':float((y[om].mean()-y[im].mean())*1e6) if om.any() else None})
        stats=model.compute_stats(p,dur,epoch)
        peaks.append({'iteration':i+1,'input_cadences':int(keep.sum()),'period_days':p,'epoch_btjd':epoch,
           'duration_hours':dur*24,'depth_ppm':float(r.depth[ix]*1e6),'formal_depth_snr':float(r.depth_snr[ix]),
           'power':float(r.power[ix]),'sap_same_unweighted_box_ppm':float((ys[outside].mean()-ys[inside].mean())*1e6),
           'populated_events':len(events),'events':events,'stats':pure(stats),
           'two_populated_events':len(events)>=2,
           'note':'Formal library SNR/power are diagnostics; correlated noise and search trials uncalibrated.'})
        keep &= np.abs(legacy.phase_distance(t,p,epoch))>.75*dur
    return peaks

def main():
    started=time.monotonic()
    before={'config':CONFIG,'source_search_sha256':digest(SOURCE/'search.py'),
            'python':sys.version,'executable':sys.executable,'numpy':np.__version__,'astropy':astropy.__version__,
            'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    (ROOT/'configuration-before-run.json').write_text(json.dumps(before,indent=2)+'\n')
    out={'scope':CONFIG['scope'],'config':CONFIG,'cases':{}}
    a=np.loadtxt(SOURCE/'data'/'toi270_s4_binned.csv',delimiter=',')
    t=a[:,0]/1e6;sap=1+a[:,1]/1e6;pdc=1+a[:,2]/1e6
    y,tr=legacy.detrend(t,pdc);ys,_=legacy.detrend(t,sap)
    out['cases']['s4_delivered_binned_unweighted']=search(t,y,ys)
    print('binned comparison finished',flush=True)
    for sector in [4,5]:
        t,sap,pdc,se,pe,meta=series(ROOT/'data'/f'toi270-s{sector:04d}.fits')
        if meta['primary']['TICID']!=259377017 or meta['primary']['SECTOR']!=sector: raise ValueError('identity mismatch')
        if meta['time']['TIMESYS']!='TDB' or meta['time']['BJDREFI']!=2457000: raise ValueError('time contract mismatch')
        pmedian=np.median(pdc);smedian=np.median(sap)
        y,tr=legacy.detrend(t,pdc/pmedian);ys,ts=legacy.detrend(t,sap/smedian)
        dy=pe/pmedian/tr
        out.setdefault('inputs',{})[str(sector)]=meta
        if sector==4: out['cases']['s4_full_unweighted']=search(t,y,ys)
        out['cases'][f's{sector}_full_formal_error_weighted']=search(t,y,ys,dy)
        print('sector',sector,'finished',flush=True)
        if sector==4:
            # Independent reconstruction of the documented lossy export, no catalog input.
            groups=np.floor(t*48).astype(int);rows=[]
            for g in np.unique(groups):
                m=groups==g
                if m.sum()>=10: rows.append([t[m].mean(),sap[m].mean(),pdc[m].mean()])
            b=np.array(rows);expected=np.c_[np.rint(b[:,0]*1e6),np.rint((b[:,1]/np.median(b[:,1])-1)*1e6),np.rint((b[:,2]/np.median(b[:,2])-1)*1e6)]
            out['export_reconstruction']={'bins':len(b),'shape_matches':expected.shape==a.shape,
              'exact_integer_equality':bool(np.array_equal(expected,a)),
              'max_abs_column_delta':np.max(np.abs(expected-a),axis=0).tolist() if expected.shape==a.shape else None}
    out['elapsed_seconds']=time.monotonic()-started
    out['environment']=before
    (ROOT/'crosscheck-results.json').write_text(json.dumps(pure(out),indent=2)+'\n')
    print(json.dumps({'elapsed_seconds':out['elapsed_seconds'],'export':out['export_reconstruction'],
      'periods':{k:[p['period_days'] for p in v] for k,v in out['cases'].items()}},indent=2))

if __name__=='__main__': main()
