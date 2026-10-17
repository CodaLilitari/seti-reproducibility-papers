"""Tiny serial executable counterexamples against an unmodified prototype copy.

The exhaustive oracle is for these tiny synthetic grids only, not a new search
implementation or proposed pipeline repair. No real target selection occurs.
"""
from __future__ import annotations
import os
for _key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS','BLIS_NUM_THREADS'):
    os.environ[_key]='1'
import ctypes, hashlib, importlib, json, sys, time
from pathlib import Path
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT/'package_copy'))
import numpy as np
import search as s
from replay import block_network, memory_peak, verify_manifest, SOURCE
sys.addaudithook(block_network)

def tiny_config():
    s.CONFIG.update(period_min_days=4.,period_max_days=4.,frequency_trials=1,
                    phase_bins=16,duration_hours=[6.])

def memberships(t,result):
    p=result['period_days'];nphase=s.CONFIG['phase_bins']
    phase=np.floor(((t-t.min())/p%1.)*nphase).astype(int)%nphase
    binned=((phase-result['phase_start_bin'])%nphase)<result['phase_width_bins']
    geometric=np.abs(s.phase_distance(t,p,result['epoch_btjd']))<=result['duration_hours']/48
    return binned,geometric

def oracle(t,y):
    """Direct sums over all exact half-open bins; select after event filtering."""
    p=4.;nphase=16;phase=np.floor(((t-t.min())/p%1.)*nphase).astype(int)%nphase
    candidates=[]
    for k in range(nphase):
        inside=((phase-k)%nphase)<1
        ni=int(inside.sum())
        if not 3<=ni<len(t)-3: continue
        depth=float(y[~inside].mean()-y[inside].mean())
        if depth<=0: continue
        epoch=float(t.min()+(k+.5)*p/nphase)
        events,cts=np.unique(np.rint((t[inside]-epoch)/p).astype(int),return_counts=True)
        score=float(depth**2*ni*(len(t)-ni)/len(t))
        candidates.append({'phase_start_bin':k,'score':score,'depth_ppm':depth*1e6,
            'populated_events':len(events),'bins_per_event':cts.tolist(),'in_transit_bins':ni})
    all_best=max(candidates,key=lambda x:x['score'])
    eligible=[r for r in candidates if r['populated_events']>=2]
    return all_best,max(eligible,key=lambda x:x['score'])

def main():
    started=time.perf_counter();old=dict(s.CONFIG);cases={}
    try:
        tiny_config()
        # One deep event wins the per-width argmax, hiding a shallower repeated dip.
        t=np.arange(257)/32
        t=t[~((t>=5)&(t<=5.25))]
        y=np.zeros(len(t));y[(t>=1)&(t<1.25)]=-.01
        shallow=((t>=2.5)&(t<2.75))|((t>=6.5)&(t<6.75));y[shallow]=-.004
        all_best,eligible=oracle(t,y)
        try:
            found,_=s.search(t,y);outcome={'returned':found}
        except ValueError as exc:
            outcome={'raised':str(exc)}
        assert all_best['populated_events']==1 and eligible['populated_events']==2
        assert 'raised' in outcome
        cases['event_eligibility_before_argmax']={'assertion_passed':True,'n':len(t),
            'unrestricted_argmax':all_best,'eligible_global_maximum':eligible,'actual':outcome,
            'finding':'Prototype rejects all trials despite an eligible positive-depth global maximum on its own grid.'}

        # Half-open scored bins vs inclusive geometric diagnostic membership.
        t=np.arange(257)/32;y=np.zeros(len(t))
        transit=((t>=1)&(t<1.25))|((t>=5)&(t<5.25));y[transit]=-.003
        y[(t==1.25)|(t==5.25)]=.06
        found,_=s.search(t,y);binned,geometric=memberships(t,found)
        direct_binned=float((y[~binned].mean()-y[binned].mean())*1e6)
        direct_geometric=float((y[~geometric].mean()-y[geometric].mean())*1e6)
        assert found['phase_start_bin']==4 and binned.sum()==16 and geometric.sum()==18
        assert direct_binned>0>direct_geometric
        assert abs(found['depth_ppm']-direct_binned)<1e-8
        cases['half_open_vs_closed_boundaries']={'assertion_passed':True,'returned':found,
            'binned_count':int(binned.sum()),'geometric_count':int(geometric.sum()),
            'disagreement_times':t[binned!=geometric].tolist(),'same_input_binned_depth_ppm':direct_binned,
            'same_input_geometric_depth_ppm':direct_geometric,
            'finding':'Search and same-box diagnostics can disagree in sign even on the identical flux vector because membership differs.'}

        # A second "populated event" can consist of one sample, with no baseline
        # coverage requirement surrounding it; this is a known validation limit.
        t=np.arange(257)/32;t=t[~(((t>=1)&(t<=1.25))|((t>=5)&(t<=5.25)))]
        dips=np.array([1.03125,1.0625,1.09375,5.0625]);t=np.sort(np.r_[t,dips]);y=np.zeros(len(t))
        y[np.isin(t,dips)]=-.003
        found,_=s.search(t,y)
        assert sorted(found['bins_per_event'])==[1,3]
        cases['sparse_second_event']={'assertion_passed':True,'returned':found,
            'finding':'Two populated events permits one sample in the second event; this is eligibility only, not two independently supported transits.'}

        # Detrending does honor the declared >half-day separation; an isolated
        # short segment, however, supplies its own median and can erase a dip.
        t=np.r_[np.arange(0,1,.02),np.arange(5,6,.02)];f=np.r_[np.ones(50),np.full(50,2.)]
        residual,trend=s.detrend(t,f)
        assert np.all(residual==0)
        t2=np.r_[np.arange(0,1,.02),np.arange(5,5.08,.02)];f2=np.r_[np.ones(50),np.full(len(t2)-50,.997)]
        residual2,trend2=s.detrend(t2,f2)
        assert np.all(residual2[-(len(t2)-50):]==0)
        cases['gap_baseline']={'assertion_passed':True,'step_residual_max':float(abs(residual).max()),
            'isolated_dim_segment_sample_count':len(t2)-50,'isolated_dim_segment_residual_max':float(abs(residual2[-(len(t2)-50):]).max()),
            'finding':'No cross-gap leakage on step control; isolated dim segment is normalized to zero, so coverage is scientifically material.'}

        # Masking at 0.75 * fitted duration leaves shoulders of a broader signal
        # when the fitted box underestimates the true duration. No second search
        # or statistical inference is needed to establish remaining contamination.
        t=np.arange(0,16,1/128);p=4.;epoch=1.125;true_duration=.5;fitted_duration=.25
        phase=np.abs(s.phase_distance(t,p,epoch));dip=phase<true_duration/2
        keep=phase>s.CONFIG['mask_half_duration']*fitted_duration
        residual_dip=int((dip&keep).sum());assert residual_dip>0
        cases['residual_mask_shoulders']={'assertion_passed':True,'true_duration_days':true_duration,
            'fitted_duration_days':fitted_duration,'mask_half_width_days':s.CONFIG['mask_half_duration']*fitted_duration,
            'injected_dip_samples':int(dip.sum()),'retained_dip_samples_after_mask':residual_dip,
            'finding':'The development mask can leave coherent shoulders when fitted width is too short; this is a methodological sensitivity, not proof of the actual third peak origin.'}

        # Neither case above is calibration of a false alarm probability.
    finally:
        s.CONFIG.clear();s.CONFIG.update(old)
    # Inspect delivered real-development memberships without rerunning the search.
    data=np.loadtxt(ROOT/'package_copy/results/detrended.csv',delimiter=',',skiprows=1)
    peaks=json.loads((ROOT/'package_copy/results/search_results.json').read_text())['peaks']
    keep=np.ones(len(data),dtype=bool);actual=[]
    for peak in peaks:
        t=data[keep,0];y=data[keep,2]
        binned,geometric=memberships(t,peak)
        actual.append({'iteration':peak['iteration'],'membership_disagreements':int((binned!=geometric).sum()),
            'binned_count':int(binned.sum()),'geometric_count':int(geometric.sum()),
            'pdc_geometric_depth_ppm':float((y[~geometric].mean()-y[geometric].mean())*1e6),
            'reported_pdc_depth_ppm':peak['depth_ppm']})
        keep &= np.abs(s.phase_distance(data[:,0],peak['period_days'],peak['epoch_btjd']))>s.CONFIG['mask_half_duration']*peak['duration_hours']/24
    cases['actual_development_memberships']={'results':actual,
        'finding':'These membership checks distinguish an executable general defect from its effect, if any, on the three delivered peaks.'}
    receipt={'generated_utc':datetime.now(timezone.utc).isoformat(),'cases':cases,
        'source_manifest_after':verify_manifest(SOURCE),'prototype_copy_source_sha256':hashlib.sha256((ROOT/'package_copy/search.py').read_bytes()).hexdigest(),
        'thread_limits':{k:os.environ[k] for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS')},
        'elapsed_seconds':time.perf_counter()-started,'peak_working_set_bytes':memory_peak(),
        'scope':'Synthetic counterexamples against unchanged custom prototype; no new target, query or observational outcome.'}
    assert not receipt['source_manifest_after']['failures']
    assert receipt['peak_working_set_bytes'] is None or receipt['peak_working_set_bytes']<1024**3
    (ROOT/'counterexamples_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))

if __name__=='__main__':main()
