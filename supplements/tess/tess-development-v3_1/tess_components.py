"""Offline development components, not an activated astronomical survey.

Astropy proposes boxes; independent event/coverage/timing components screen them.
No network, FITS importer, metadata acquisition, or alias adjudicator is included.
"""
from __future__ import annotations
import hashlib, json, math, sys, platform
from dataclasses import asdict, dataclass
from pathlib import Path
import numpy as np
import scipy,astropy
from astropy.timeseries import BoxLeastSquares
from scipy.optimize import least_squares
_LOADED_SOURCE_SHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()

class ResourceStop(ValueError): pass
class NumericalStop(ValueError): pass

@dataclass(frozen=True)
class Config:
    period_min: float = .6
    period_max: float = 13.
    duration_hours: tuple = (1.,1.5,2.,2.5,3.,4.)
    oversample: int = 10
    chunk_size: int = 512
    max_grid_points: int = 250000
    attempts: int = 3
    mask_half_duration: float = .75
    coverage_fraction: float = .7
    min_samples: int = 5
    discovery_snr: float = 8.
    holdout_snr: float = 5.
    ingress_fraction: float = .2
    min_ingress_samples: int = 2
    covariance_condition_limit: float = 1e12

@dataclass(frozen=True)
class CadenceClock:
    origin: float
    interval: float = 1/720

def canonical(value):
    return (json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
def digest(value):return hashlib.sha256(canonical(value)).hexdigest()
def array_digest(*arrays):
    h=hashlib.sha256()
    for a in arrays:
        a=np.asarray(a,dtype='<f8');h.update(canonical(list(a.shape)));h.update(a.tobytes())
    return h.hexdigest()
def execution_identity():
    return {'source_sha256':_LOADED_SOURCE_SHA256,'python':sys.version,'implementation':platform.python_implementation(),
        'dependencies':{'numpy':np.__version__,'scipy':scipy.__version__,'astropy':astropy.__version__}}
def checked_arrays(t,y,dy):
    t,y,dy=map(lambda x:np.asarray(x,dtype=float),(t,y,dy))
    if any(a.ndim!=1 for a in (t,y,dy)) or len(t)!=len(y) or len(t)!=len(dy) or len(t)<5:
        raise NumericalStop('array_shape_or_length')
    if not all(np.isfinite(a).all() for a in (t,y,dy)) or np.any(dy<=0) or np.any(np.diff(t)<=0):
        raise NumericalStop('nonfinite_nonpositive_errors_or_unordered_times')
    return t,y,dy
def phase_distance(t,p,epoch):return (np.asarray(t)-epoch+p/2)%p-p/2

def validate_span_clock(t,span,clock,after=None):
    if len(span)!=2 or not all(math.isfinite(float(x)) for x in span) or not span[0]<span[1]:raise NumericalStop('invalid_assigned_span')
    if not math.isfinite(clock.origin) or not math.isfinite(clock.interval) or clock.interval<=0:raise NumericalStop('invalid_cadence_clock')
    if len(t) and (min(t)<span[0] or max(t)>span[1]):raise NumericalStop('timestamps_outside_assigned_span')
    if after is not None and span[0]<=after:raise NumericalStop('holdout_not_strictly_after_discovery_span')

def preprocess_sectors(t,sap,pdc,sap_error,pdc_error,quality,sector):
    """Matched array-level quality, normalization and gap-split median processing.
    This consumes already validated source arrays, not FITS or remote products.
    """
    arrays=[np.asarray(a) for a in (t,sap,pdc,sap_error,pdc_error,quality,sector)]
    if any(a.ndim!=1 for a in arrays) or len({len(a) for a in arrays})!=1:raise NumericalStop('raw_array_shapes_differ')
    t,sap,pdc,se,pe,q,sec=arrays
    if not np.issubdtype(sec.dtype,np.integer) or np.any(sec<=0):raise NumericalStop('invalid_sector_identifiers')
    good=(q==0)
    for a in (t,sap,pdc,se,pe):good&=np.isfinite(a)
    for a in (sap,pdc,se,pe):good&=a>0
    ti=np.asarray(t[good],float)
    if len(ti)<5 or np.any(np.diff(ti)<=0):raise NumericalStop('insufficient_or_unordered_common_support')
    values={};normalization=[];sect=sec[good]
    for name,flux,error in [('sap',sap[good],se[good]),('pdc',pdc[good],pe[good])]:
        residual=np.empty(len(ti));formal=np.empty(len(ti));trend=np.empty(len(ti))
        for sid in np.unique(sect):
            indices=np.flatnonzero(sect==sid);tt=ti[indices];ff=np.asarray(flux[indices],float);ee=np.asarray(error[indices],float)
            norm=float(np.median(ff));fn=ff/norm;en=ee/norm;baseline=np.empty(len(tt))
            cuts=np.r_[0,np.flatnonzero(np.diff(tt)>.5)+1,len(tt)]
            for lo,hi in zip(cuts[:-1],cuts[1:]):
                st=tt[lo:hi];sf=fn[lo:hi]
                for j,center in enumerate(st):
                    a=np.searchsorted(st,center-.5,'left');b=np.searchsorted(st,center+.5,'right')
                    baseline[lo+j]=np.median(sf[a:b])
            residual[indices]=fn/baseline-1;formal[indices]=en/baseline;trend[indices]=baseline
            normalization.append({'product':name,'sector':int(sid),'median':norm,'accepted_samples':len(indices),'segments':len(cuts)-1})
        values.update({f'y_{name}':residual,f'dy_{name}':formal,f'trend_{name}':trend})
    return {'t':ti,'sector':sect,'common_input_mask':good,'normalization':normalization,**values,
        'contract':'Common QUALITY==0 finite positive SAP/PDC/errors; sector medians; separate sectors/gaps>0.5d; one-day median endpoints inclusive; errors divided by same normalization and trend; no depth clipping.'}

def grid_plan(baseline,config=Config()):
    if not math.isfinite(baseline) or baseline<=0:raise NumericalStop('invalid_baseline')
    if not 0<config.period_min<config.period_max:raise NumericalStop('invalid_period_range')
    durations=np.asarray(config.duration_hours,dtype=float)/24
    if not np.isfinite(durations).all() or np.any(durations<=0) or max(durations)>=config.period_min:raise NumericalStop('invalid_durations')
    max_step=float(min(durations)/(5*baseline*config.period_max))
    intervals=math.ceil((1/config.period_min-1/config.period_max)/max_step)
    return {'baseline_days':float(baseline),'max_frequency_step_per_day':max_step,'intervals':intervals,
        'points':intervals+1,'phase_drift_bound_days':float(min(durations)/5),
        'claim':'Bound on period-grid endpoint phase drift only; not event-time or period uncertainty.'}

def make_grid(t,config=Config()):
    t=np.asarray(t,dtype=float);plan=grid_plan(float(max(t)-min(t)),config)
    if plan['points']>config.max_grid_points:raise ResourceStop('grid_exceeds_frozen_resource_limit_no_coarsening')
    frequencies=np.linspace(1/config.period_max,1/config.period_min,plan['points'])
    periods=1/frequencies
    return periods,{**plan,'actual_frequency_step_per_day':float(frequencies[1]-frequencies[0]),
                    'period_grid_sha256':array_digest(periods)}

def global_bls_maximum(t,y,dy,periods,config=Config(),chunk_size=None):
    t,y,dy=checked_arrays(t,y,dy);periods=np.asarray(periods,float)
    if periods.ndim!=1 or not len(periods) or not np.isfinite(periods).all() or np.any(periods<=0):raise NumericalStop('invalid_grid')
    size=config.chunk_size if chunk_size is None else chunk_size
    if type(size) is not int or size<1:raise NumericalStop('invalid_chunk_size')
    model=BoxLeastSquares(t,y,dy);best=None;best_key=None
    for offset in range(0,len(periods),size):
        result=model.power(periods[offset:offset+size],np.asarray(config.duration_hours)/24,
            objective='likelihood',method='fast',oversample=config.oversample)
        for i in range(len(result.power)):
            values=[float(result.power[i]),float(result.period[i]),float(result.duration[i]),float(result.transit_time[i]),float(result.depth[i])]
            if not all(math.isfinite(x) for x in values):continue
            power,p,d,epoch,depth=values
            # Global tie convention is independent of chunk boundaries.
            key=(-power,p,d,epoch,offset+i)
            if best_key is None or key<best_key:
                best_key=key;best={'power':power,'period':p,'duration':d,'epoch':epoch,'depth':depth,'grid_index':offset+i}
    if best is None:raise NumericalStop('no_finite_bls_maximum')
    return best

def mask_ledger(attempts,config=Config()):
    return [{'attempt':r['attempt'],'period':r['maximum']['period'],'epoch':r['maximum']['epoch'],
             'duration':r['maximum']['duration'],'half_width':config.mask_half_duration*r['maximum']['duration'],
             'source':'original_computed_maximum_even_if_screening_fails'}
            for r in attempts if r['computation']=='computed']

def other_mask(t,ledger,own_attempt):
    mask=np.zeros(len(t),bool)
    for m in ledger:
        if m['attempt']!=own_attempt:mask|=abs(phase_distance(t,m['period'],m['epoch']))<=m['half_width']
    return mask

def expected_count(lo,hi,clock):
    # Fixed numerical convention on the nominal cadence lattice, half-open.
    a=math.ceil((lo-clock.origin)/clock.interval-1e-9)
    b=math.ceil((hi-clock.origin)/clock.interval-1e-9)
    return max(0,b-a)

def event_support(t,center,duration,clock,removed=None,config=Config()):
    t=np.asarray(t,float);removed=np.zeros(len(t),bool) if removed is None else np.asarray(removed,bool)
    if len(removed)!=len(t) or not math.isfinite(clock.interval) or clock.interval<=0:raise NumericalStop('invalid_cadence_or_mask')
    edges=[center-1.5*duration,center-.5*duration,center+.5*duration,center+1.5*duration]
    windows={};indices={}
    for name,lo,hi in zip(('left','inside','right'),edges[:-1],edges[1:]):
        raw=(t>=lo)&(t<hi);use=raw&~removed
        ids=np.rint((t[use]-clock.origin)/clock.interval).astype(np.int64)
        unique=len(np.unique(ids));expected=expected_count(lo,hi,clock)
        duplicate=len(ids)!=unique
        eligible=expected>0 and unique>=config.min_samples and unique>=config.coverage_fraction*expected and not duplicate
        windows[name]={'expected':expected,'accepted_unique':unique,'lost_to_other_masks':int((raw&removed).sum()),
            'duplicate_cadence_ids':duplicate,'covered':bool(eligible)}
        indices[name]=use
    union=indices['left']|indices['inside']|indices['right']
    union_ids=np.rint((t[union]-clock.origin)/clock.interval).astype(np.int64)
    union_duplicate=len(np.unique(union_ids))!=len(union_ids)
    return {'windows':windows,'duplicate_cadence_ids_across_windows':bool(union_duplicate),
        'covered':not union_duplicate and all(x['covered'] for x in windows.values())},indices

def weighted_depth(y,dy,inside,outside):
    wi=1/np.asarray(dy)[inside]**2;wo=1/np.asarray(dy)[outside]**2
    if not len(wi) or not len(wo):raise NumericalStop('empty_depth_support')
    depth=float(np.sum(wo*np.asarray(y)[outside])/sum(wo)-np.sum(wi*np.asarray(y)[inside])/sum(wi))
    variance=float(1/sum(wo)+1/sum(wi))
    return depth,variance

def predicted_events(epoch,period,span):
    if not 0<period or not span[0]<span[1]:raise NumericalStop('invalid_prediction_span')
    return [(n,epoch+n*period) for n in range(math.ceil((span[0]-epoch)/period),math.floor((span[1]-epoch)/period)+1)]

def measure_events(t,y,dy,epoch,period,duration,span,clock,removed,config=Config()):
    rows=[]
    for cycle,center in predicted_events(epoch,period,span):
        support,m=event_support(t,center,duration,clock,removed,config)
        row={'cycle':cycle,'center':float(center),**support}
        if support['covered']:
            depth,var=weighted_depth(y,dy,m['inside'],m['left']|m['right'])
            row.update(depth=depth,variance=var)
        else:row.update(depth=None,variance=None)
        rows.append(row)
    return rows

def combine_events(events,min_events):
    indexed=[(i,r) for i,r in enumerate(events) if r['covered']]
    selected=[r for _,r in indexed]
    if len(selected)<min_events:return {'status':'inconclusive','reason':'insufficient_covered_events','covered_events':len(selected)}
    if any(r['depth'] is None or r['variance'] is None or not math.isfinite(r['depth']) or not math.isfinite(r['variance']) or r['variance']<=0 for r in selected):
        return {'status':'inconclusive','reason':'invalid_event_statistics','covered_events':len(selected)}
    w=np.array([1/r['variance'] for r in selected]);d=np.array([r['depth'] for r in selected])
    weight_total=sum(w);depth=float(np.dot(w,d)/weight_total);var=float(1/weight_total)
    contributions=w*d/math.sqrt(weight_total);absolute_total=float(np.sum(np.abs(contributions)))
    diagnostics={'event_contributions':[{'event_index':i,'normalized_inverse_variance_weight':float(weight/weight_total),
        'signed_snr_contribution':float(contribution)} for (i,_),weight,contribution in zip(indexed,w,contributions)],
        'max_absolute_snr_contribution_fraction':float(np.max(np.abs(contributions))/absolute_total) if absolute_total>0 else None,
        'contribution_concentration_unavailable_reason':None if absolute_total>0 else 'zero_total_absolute_snr_contribution'}
    return {'status':'computed','covered_events':len(selected),'depth':depth,'variance':var,'formal_snr':depth/math.sqrt(var),
        'nonpositive_event_count':int((d<=0).sum()),'all_covered_events_combined':True,**diagnostics}

def holdout_decision(discovery,events,config=Config()):
    combined=combine_events(events,2)
    if combined['status']!='computed':return combined
    consistency=abs(combined['depth']-discovery['depth'])<=3*math.sqrt(combined['variance']+discovery['variance'])
    recovered=combined['depth']>0 and combined['formal_snr']>=config.holdout_snr and consistency
    return {**combined,'status':'recovered' if recovered else 'non_recovery','three_se_depth_consistency':bool(consistency),
        'criterion':'At least two covered events; all combined, including zero/negative; positive aggregate, formal SNR>=5, depth consistency<=3 combined SE.'}

def trapezoid_shape(t,center,duration,ingress_fraction=.2):
    distance=np.asarray(t)-center;ingress=duration*ingress_fraction;half=duration/2
    shape=np.clip((half-abs(distance))/ingress,0,1)
    ramp=(abs(distance)>half-ingress)&(abs(distance)<half)
    derivative=np.where(ramp,np.sign(distance)/ingress,0.)
    return shape,derivative

def fit_event_time(t,y,dy,nominal_center,duration,config=Config()):
    """Signed depth, baseline+slope nuisance fit, fixed trapezoid shape.
    Formal covariance is the inverse full weighted Jacobian information matrix.
    """
    t,y,dy=checked_arrays(t,y,dy);u=(t-nominal_center)/duration
    initial_shape,_=trapezoid_shape(t,nominal_center,duration,config.ingress_fraction)
    A=np.c_[np.ones(len(t)),u,-initial_shape];initial=np.linalg.lstsq(A/dy[:,None],y/dy,rcond=None)[0]
    def residual(par):
        shape,_=trapezoid_shape(t,nominal_center+par[3],duration,config.ingress_fraction)
        return (par[0]+par[1]*u-par[2]*shape-y)/dy
    def jac(par):
        shape,derivative=trapezoid_shape(t,nominal_center+par[3],duration,config.ingress_fraction)
        return np.c_[np.ones(len(t)),u,-shape,-par[2]*derivative]/dy[:,None]
    result=least_squares(residual,np.r_[initial,0.],jac=jac,bounds=([-np.inf]*3+[-duration/2],[np.inf]*3+[duration/2]),
        x_scale=np.array([.001,.001,.001,duration]),ftol=1e-12,xtol=1e-12,gtol=1e-10,max_nfev=200)
    if not result.success:return {'status':'inconclusive','reason':'timing_optimizer_failed'}
    if abs(result.x[3])>=duration*(.5-1e-4):return {'status':'inconclusive','reason':'timing_center_at_bound'}
    center=nominal_center+float(result.x[3]);distance=t-center;half=duration/2;inner=half-duration*config.ingress_fraction
    ingress_counts=[int(((distance>-half)&(distance<-inner)).sum()),int(((distance>inner)&(distance<half)).sum())]
    if min(ingress_counts)<config.min_ingress_samples:return {'status':'inconclusive','reason':'unsupported_ingress','ingress_samples':ingress_counts}
    J=jac(result.x);norm=np.linalg.norm(J,axis=0)
    if np.any(norm==0):return {'status':'inconclusive','reason':'singular_timing_covariance'}
    scaled=J/norm;information=scaled.T@scaled;condition=float(np.linalg.cond(information))
    if np.linalg.matrix_rank(information)<4 or not math.isfinite(condition) or condition>config.covariance_condition_limit:
        return {'status':'inconclusive','reason':'singular_or_ill_conditioned_timing_covariance'}
    covariance=np.linalg.inv(information)/norm[:,None]/norm[None,:]
    if not np.isfinite(covariance).all() or covariance[3,3]<=0:return {'status':'inconclusive','reason':'invalid_timing_covariance'}
    return {'status':'fitted','time':float(center),'variance':float(covariance[3,3]),'signed_depth':float(result.x[2]),
        'parameters':result.x.tolist(),'full_covariance':covariance.tolist(),'ingress_samples':ingress_counts,
        'reduced_chi_square_diagnostic':float(np.dot(result.fun,result.fun)/max(1,len(t)-4)),
        'covariance_scope':'Formal fixed-shape Gaussian-error covariance including baseline, slope and signed depth; not rescaled or empirically calibrated.'}

def fit_ephemeris(timings,alias_status,config=Config()):
    if alias_status!='resolved':return {'status':'inconclusive','reason':'unresolved_or_undeclared_alias'}
    if len(timings)<3:return {'status':'inconclusive','reason':'fewer_than_three_covered_timings'}
    if any(r.get('status')!='fitted' for r in timings):return {'status':'inconclusive','reason':'a_covered_event_timing_failed_no_subset_selection'}
    cycles=[r['cycle'] for r in timings]
    if any(type(n) is not int for n in cycles) or len(set(cycles))!=len(cycles):return {'status':'inconclusive','reason':'ambiguous_or_duplicate_cycles'}
    origin=min(cycles);x=np.asarray(cycles,float)-origin;y=np.array([r['time'] for r in timings]);v=np.array([r['variance'] for r in timings])
    if not np.isfinite(y).all() or not np.isfinite(v).all() or np.any(v<=0):return {'status':'inconclusive','reason':'invalid_event_timing_variance'}
    A=np.c_[np.ones(len(x)),x];weighted=A/np.sqrt(v[:,None]);info=weighted.T@weighted
    if np.linalg.matrix_rank(weighted)<2 or np.linalg.cond(info)>config.covariance_condition_limit:return {'status':'inconclusive','reason':'singular_ephemeris_covariance'}
    cov=np.linalg.inv(info);base=float(y[0]);par=np.linalg.solve(info,weighted.T@((y-base)/np.sqrt(v)));par[0]+=base
    if par[1]<=0 or not np.isfinite(par).all():return {'status':'inconclusive','reason':'invalid_ephemeris_fit'}
    return {'status':'fitted','epoch':float(par[0]),'period':float(par[1]),'covariance':cov.tolist(),'cycle_origin':origin,
        'timings_used':len(timings),'residual_days':(y-A@par).tolist(),
        'covariance_scope':'Discovery-only weighted timing-line formal covariance, conditional on fixed shape, noise model and resolved cycle alias; no grid uncertainty.'}

def predict_uncertainty(ephemeris,span,duration):
    if ephemeris.get('status')!='fitted':return {'status':'inconclusive','reason':'timing_not_fitted'}
    C=np.asarray(ephemeris['covariance']);rows=[]
    if C.shape!=(2,2) or not np.isfinite(C).all() or not np.allclose(C,C.T,rtol=1e-10,atol=0) or np.any(np.linalg.eigvalsh(C)<=0):
        return {'status':'inconclusive','reason':'invalid_ephemeris_covariance_matrix'}
    for cycle,center in predicted_events(ephemeris['epoch'],ephemeris['period'],span):
        v=float(C[0,0]+2*cycle*C[0,1]+cycle**2*C[1,1])
        if not math.isfinite(v) or v<=0:return {'status':'inconclusive','reason':'invalid_propagated_variance'}
        rows.append({'cycle':cycle,'center':float(center),'sigma_days':math.sqrt(v)})
    if not rows:return {'status':'inconclusive','reason':'no_predicted_holdout_events'}
    if any(3*r['sigma_days']>duration/2 for r in rows):return {'status':'inconclusive','reason':'timing_uncertainty_exceeds_half_duration','events':rows}
    return {'status':'supported','events':rows}

def discovery_freeze(t,y,dy,span,clock,alias_statuses,config=Config(),*,holdout_span,holdout_clock):
    t,y,dy=checked_arrays(t,y,dy)
    validate_span_clock(t,span,clock)
    validate_span_clock([],holdout_span,holdout_clock,after=span[1])
    if config.attempts!=3 or len(alias_statuses)!=3:raise NumericalStop('exactly_three_attempt_slots_and_alias_statuses_required')
    periods,grid=make_grid(t,config);attempts=[]
    for number in range(1,4):
        previous=mask_ledger(attempts,config);keep=~other_mask(t,previous,None)
        try:
            maximum=global_bls_maximum(t[keep],y[keep],dy[keep],periods,config)
            attempts.append({'attempt':number,'computation':'computed','maximum':maximum,'input_samples':int(keep.sum())})
        except (NumericalStop,ValueError) as exc:
            attempts.append({'attempt':number,'computation':'failed','reason':str(exc),'input_samples':int(keep.sum())})
    ledger=mask_ledger(attempts,config)
    for row,alias_status in zip(attempts,alias_statuses):
        if row['computation']!='computed':continue
        p=row['maximum'];removed=other_mask(t,ledger,row['attempt'])
        events=measure_events(t,y,dy,p['epoch'],p['period'],p['duration'],span,clock,removed,config)
        combined=combine_events(events,3);timings=[]
        for event in events:
            if not event['covered']:continue
            center=event['center'];use=(t>=center-1.5*p['duration'])&(t<center+1.5*p['duration'])&~removed
            fitted=fit_event_time(t[use],y[use],dy[use],center,p['duration'],config)
            timings.append({'cycle':event['cycle'],**fitted})
        ephemeris=fit_ephemeris(timings,alias_status,config)
        original_screened=combined['status']=='computed' and combined['depth']>0 and combined['formal_snr']>=config.discovery_snr
        final_events=[];final_combined={'status':'inconclusive','reason':'timing_not_fitted'};coverage_change=None
        if ephemeris['status']=='fitted':
            final_events=measure_events(t,y,dy,ephemeris['epoch'],ephemeris['period'],p['duration'],span,clock,removed,config)
            original_cycles={e['cycle'] for e in events if e['covered']}
            final_cycles={e['cycle']+ephemeris['cycle_origin'] for e in final_events if e['covered']}
            coverage_change={'original_covered_cycles':sorted(original_cycles),'fitted_covered_cycles_in_original_numbering':sorted(final_cycles),
                'changed':original_cycles!=final_cycles,
                'original_accepted_samples':sum(sum(w['accepted_unique'] for w in e['windows'].values()) for e in events),
                'fitted_accepted_samples':sum(sum(w['accepted_unique'] for w in e['windows'].values()) for e in final_events)}
            final_combined=combine_events(final_events,3)
            if original_cycles!=final_cycles:
                ephemeris={**ephemeris,'status':'inconclusive','reason':'covered_cycle_set_changed_after_timing_fit_no_iteration'}
        screened=(ephemeris['status']=='fitted' and final_combined['status']=='computed'
                  and final_combined['depth']>0 and final_combined['formal_snr']>=config.discovery_snr)
        row.update(original_events=events,original_screen_combined=combined,original_screening='pass' if original_screened else 'failed',
            final_fitted_events=final_events,combined=final_combined,screening='pass' if screened else 'failed',
            fitted_coverage_change=coverage_change,
            alias_status=alias_status,event_timings=timings,ephemeris=ephemeris,
            samples_removed_by_frozen_other_masks=int(removed.sum()))
    record={'kind':'development_discovery_freeze_v3','config':asdict(config),'discovery_span':list(span),
        'cadence_clock':asdict(clock),'grid':grid,'period_grid':periods.tolist(),'attempts':attempts,'mask_ledger':ledger,
        'input_arrays_sha256':array_digest(t,y,dy),'source_sha256':_LOADED_SOURCE_SHA256,'execution_identity':execution_identity(),
        'holdout_assignment':{'span':list(holdout_span),'cadence_clock':asdict(holdout_clock)},
        'all_three_attempts_frozen_together':True,'holdout_flux_used':False,
        'alias_scope':'Alias statuses are explicit caller inputs requiring external discovery-only adjudication; component does not prove an orbital alias.'}
    return {'sha256':digest(record),'record':record}

def evaluate_holdout(frozen,attempt,t,y,dy,span,clock):
    record=frozen['record']
    if digest(record)!=frozen['sha256'] or not record['all_three_attempts_frozen_together'] or len(record['attempts'])!=3:
        raise NumericalStop('discovery_freeze_integrity_failure')
    if record['execution_identity']!=execution_identity() or record['source_sha256']!=_LOADED_SOURCE_SHA256:
        raise NumericalStop('executing_implementation_or_dependency_identity_changed')
    t,y,dy=checked_arrays(t,y,dy)
    validate_span_clock(t,span,clock,after=record['discovery_span'][1])
    if record['holdout_assignment']!={'span':list(span),'cadence_clock':asdict(clock)}:
        raise NumericalStop('holdout_span_or_cadence_clock_differs_from_discovery_freeze')
    if type(attempt) is not int or not 1<=attempt<=3:raise NumericalStop('invalid_attempt_index')
    config=Config(**record['config']);candidate=record['attempts'][attempt-1]
    if candidate.get('computation')!='computed':return {'status':'not_eligible','reason':'discovery_computation_failed'}
    if candidate['ephemeris']['status']!='fitted':return {'status':'inconclusive','reason':candidate['ephemeris']['reason']}
    if candidate['attempt']!=attempt or candidate.get('screening')!='pass':return {'status':'not_eligible','reason':'discovery_screen_failed'}
    p=candidate['maximum'];prediction=predict_uncertainty(candidate['ephemeris'],span,p['duration'])
    if prediction['status']!='supported':return prediction
    removed=other_mask(t,record['mask_ledger'],attempt);ep=candidate['ephemeris']
    events=measure_events(t,y,dy,ep['epoch'],ep['period'],p['duration'],span,clock,removed,config)
    combined=holdout_decision(candidate['combined'],events,config)
    return {**combined,'events':events,'prediction':prediction,'freeze_sha256':frozen['sha256'],
        'samples_removed_by_same_frozen_other_masks':int(removed.sum()),'mask_ledger_sha256':digest(record['mask_ledger']),
        'period_phase_duration_refitted':False,'holdout_input_arrays_sha256':array_digest(t,y,dy)}
