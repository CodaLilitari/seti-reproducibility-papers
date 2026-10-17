"""Connected synthetic raw-array -> preprocessing -> discovery freeze -> holdout.
Known generative parameters justify synthetic alias labels only, not real labels.
"""
import json
from pathlib import Path
import numpy as np
from tess_components import Config,CadenceClock,trapezoid_shape,preprocess_sectors,discovery_freeze,evaluate_holdout

def synthetic_raw(spans,seed):
    rng=np.random.default_rng(seed);times=[];sectors=[]
    for sector,(start,end) in enumerate(spans,1):
        t=np.arange(start,end,1/720);times.extend(t);sectors.extend([sector]*len(t))
    t=np.array(times);sector=np.array(sectors);shape=np.zeros(len(t))
    for center in np.arange(-2,40,2.7)+.8:shape+=trapezoid_shape(t,center,2/24)[0]
    # Same photons need not have identical processing; deterministic separate
    # noise draws are a numerical fixture, not independent-observation evidence.
    errors=np.full(len(t),.0002);trend=1+.0003*np.sin(t/3)
    pdc=trend*(1-.01*shape)+rng.normal(0,.0002,len(t));sap=trend*(1-.01*shape)+rng.normal(0,.0002,len(t))
    q=np.zeros(len(t),int);q[31::157]=1
    return (t,sap,pdc,errors,errors,q,sector)

def run_driver(output=None,discovery_spans=((0,7.4),(10,17.4))):
    discovery_raw=synthetic_raw(discovery_spans,94017)
    discovery=preprocess_sectors(*discovery_raw)
    # A bounded, declared SYNTHETIC fixture configuration. It does not replace
    # the production proposal's period/duration choices.
    config=Config(period_min=2.,period_max=4.,duration_hours=(2.,),chunk_size=37)
    frozen=discovery_freeze(discovery['t'],discovery['y_pdc'],discovery['dy_pdc'],(discovery_spans[0][0],discovery_spans[-1][1]),CadenceClock(0),
        ['resolved','unresolved','unresolved'],config,holdout_span=(21,29),holdout_clock=CadenceClock(21))
    # Freeze is complete before holdout raw arrays are even constructed.
    if output is not None:
        output=Path(output);output.mkdir(parents=True,exist_ok=True)
        (output/'discovery_freeze.json').write_text(json.dumps(frozen,indent=2,allow_nan=False)+'\n')
    holdout_raw=synthetic_raw([(21,29)],94018);holdout=preprocess_sectors(*holdout_raw)
    result=evaluate_holdout(frozen,1,holdout['t'],holdout['y_pdc'],holdout['dy_pdc'],(21,29),CadenceClock(21))
    summary={'scope':'Synthetic connected development demonstration; no real target, source acquisition, alias discovery or FAP calibration.',
        'frozen_sha256':frozen['sha256'],'attempts':[{'attempt':a['attempt'],'computation':a['computation'],
            'period':a.get('maximum',{}).get('period'),'screening':a.get('screening'),'ephemeris_status':a.get('ephemeris',{}).get('status'),
            'timing_reason':a.get('ephemeris',{}).get('reason')} for a in frozen['record']['attempts']],
        'discovery_preprocessing':{'normalization':discovery['normalization'],'accepted_samples':len(discovery['t'])},
        'holdout_preprocessing':{'normalization':holdout['normalization'],'accepted_samples':len(holdout['t'])},'holdout':result}
    if output is not None:(output/'synthetic_driver_result.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    return frozen,summary

if __name__=='__main__':
    _,summary=run_driver(Path(__file__).resolve().parent/'synthetic_output')
    print(json.dumps(summary,indent=2,allow_nan=False))
