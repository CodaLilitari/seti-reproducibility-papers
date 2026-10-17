"""Small, unweighted binned-BLS development benchmark, not a planet validator.
No catalog periods, epochs, depths, or discovery labels are inputs to the search.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
from numpy.typing import NDArray

ROOT = Path(__file__).resolve().parent
CONFIG = dict(period_min_days=0.6, period_max_days=13.0, frequency_trials=12000,
              phase_bins=512, duration_hours=[1., 1.5, 2., 2.5, 3., 4.],
              iterations=3, gap_days=0.5, median_window_days=1., mask_half_duration=0.75)

def detrend(t: NDArray, f: NDArray) -> tuple[NDArray, NDArray]:
    """Running median by physical time, without bridging >0.5-day data gaps."""
    if len(t)!=len(f) or len(t)<10 or not np.isfinite(t).all() or not np.isfinite(f).all():
        raise ValueError('Invalid input arrays')
    if np.any(np.diff(t)<=0) or np.any(f<=0):
        raise ValueError('Expected positive flux and strictly increasing times')
    trend=np.empty_like(f)
    cuts=np.r_[0,np.flatnonzero(np.diff(t)>CONFIG['gap_days'])+1,len(t)]
    for lo,hi in zip(cuts[:-1],cuts[1:]):
        ts=t[lo:hi]; fs=f[lo:hi]
        for i,ti in enumerate(ts):
            a=np.searchsorted(ts,ti-0.5*CONFIG['median_window_days'],'left')
            b=np.searchsorted(ts,ti+0.5*CONFIG['median_window_days'],'right')
            trend[lo+i]=np.median(fs[a:b])
    return f/trend-1., trend

def phase_distance(t: NDArray, p: float, epoch: float) -> NDArray:
    return (t-epoch+0.5*p)%p-0.5*p

def search(t: NDArray, y: NDArray) -> tuple[dict, NDArray]:
    """Maximize the two-level least-squares improvement over frequency and boxes.

    Equal weights; bins summarize counts and flux, not mean flux without counts.
    No significance or false-alarm calibration is claimed.
    """
    nphase=CONFIG['phase_bins']; n=len(t); tbase=float(t.min())
    freqs=np.linspace(1/CONFIG['period_max_days'],1/CONFIG['period_min_days'],CONFIG['frequency_trials'])
    y=y-np.mean(y); total=float(y.sum())
    spectrum=np.empty((len(freqs),3))
    best={'score':-1.}
    for j,freq in enumerate(freqs):
        p=1./freq
        bi=np.floor(((t-tbase)*freq%1.)*nphase).astype(int)%nphase
        counts=np.bincount(bi,minlength=nphase).astype(float)
        sums=np.bincount(bi,weights=y,minlength=nphase)
        nc=np.r_[0.,np.cumsum(np.r_[counts,counts])]
        sy=np.r_[0.,np.cumsum(np.r_[sums,sums])]
        starts=np.arange(nphase)
        top=-1.; topduration=np.nan
        widths=np.unique(np.maximum(1,np.rint(np.array(CONFIG['duration_hours'])/24/p*nphase).astype(int)))
        for width in widths:
            if width>=nphase//2: continue
            ni=nc[starts+width]-nc[starts]
            si=sy[starts+width]-sy[starts]
            valid=(ni>=3)&(ni<n-3)
            depth=np.zeros(nphase); score=np.full(nphase,-1.)
            depth[valid]=(total-si[valid])/(n-ni[valid])-si[valid]/ni[valid]
            valid &= depth>0
            score[valid]=depth[valid]**2*ni[valid]*(n-ni[valid])/n
            k=int(np.argmax(score)); val=float(score[k])
            if val>top: top=val;topduration=width*p/nphase
            if val>best['score']:
                epoch=tbase+((k+width/2)%nphase)*p/nphase
                # Distinct populated events are computed from actual sample times.
                inside=np.abs(phase_distance(t,p,epoch))<=width*p/nphase/2
                cycles=np.rint((t[inside]-epoch)/p).astype(int)
                _,cts=np.unique(cycles,return_counts=True)
                if len(cts)<2: continue
                best=dict(score=val,period_days=float(p),epoch_btjd=float(epoch),
                          duration_hours=float(width*p/nphase*24),depth_ppm=float(depth[k]*1e6),
                          in_transit_bins=int(ni[k]),populated_events=int(len(cts)),
                          bins_per_event=cts.tolist(),phase_start_bin=k,phase_width_bins=int(width))
        spectrum[j]=[p,top,topduration]
    if best['score']<0: raise ValueError('No trial has positive depth and two populated events')
    return best,spectrum

def main() -> None:
    a=np.loadtxt(ROOT/'data/toi270_s4_binned.csv',delimiter=',')
    t=a[:,0]/1e6; fsap=1+a[:,1]/1e6; fpdc=1+a[:,2]/1e6
    y,trend=detrend(t,fpdc); ys,ts=detrend(t,fsap)
    np.savetxt(ROOT/'results/detrended.csv',np.c_[t,ys,y,ts,trend],delimiter=',',
               header='btjd,sap_relative_residual,pdc_relative_residual,sap_trend,pdc_trend',comments='')
    keep=np.ones(len(t),dtype=bool); peaks=[]
    for i in range(CONFIG['iterations']):
        peak,spec=search(t[keep],y[keep]); peak['iteration']=i+1
        peak['input_bins']=int(keep.sum())
        p=peak['period_days'];epoch=peak['epoch_btjd'];duration=peak['duration_hours']/24
        inside=(np.abs(phase_distance(t,p,epoch))<=duration/2)&keep
        outside=~inside&keep
        peak['sap_depth_same_box_ppm']=float((ys[outside].mean()-ys[inside].mean())*1e6)
        peaks.append(peak)
        np.savetxt(ROOT/f'results/periodogram_{i+1}.csv',spec,delimiter=',',
                   header='period_days,ssr_improvement,effective_duration_days',comments='')
        keep &= np.abs(phase_distance(t,p,epoch))>CONFIG['mask_half_duration']*duration
    result={'status':'known-system development recovery, no novel candidate claim',
            'config':CONFIG,'n_bins':len(t),'btjd_range':[float(t.min()),float(t.max())],
            'peaks':peaks,'remaining_bins':int(keep.sum())}
    (ROOT/'results/search_results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__': main()
