import copy,math,unittest
import numpy as np
from scipy.special import ndtr
from tess_components import *
from synthetic_driver import run_driver

def event(depth,variance=1.,covered=True):return {'covered':covered,'depth':depth,'variance':variance}

class AggregateChecks(unittest.TestCase):
    def test_negative_event_does_not_veto_recovery(self):
        events=[event(-.1)]+[event(2.2) for _ in range(9)]
        result=holdout_decision({'depth':1.97,'variance':.01},events)
        self.assertEqual(result['status'],'recovered')
        self.assertEqual(result['nonpositive_event_count'],1)
        self.assertAlmostEqual(result['formal_snr'],6.2296869905317065,places=12)
    def test_zero_event_is_combined(self):
        result=holdout_decision({'depth':2.25,'variance':.01},[event(0.)]+[event(2.5) for _ in range(9)])
        self.assertEqual(result['status'],'recovered');self.assertAlmostEqual(result['depth'],2.25)
    def test_every_event_sign_rule_math(self):self.assertAlmostEqual(float(ndtr(1)**25),.013315260765244287,places=15)
    def test_no_positive_subset_selection(self):
        result=holdout_decision({'depth':3.,'variance':.01},[event(10.,.01),event(-11.,.01)])
        self.assertEqual(result['status'],'non_recovery');self.assertLess(result['depth'],0)
    def test_coverage_inconclusive_not_nonrecovery(self):
        self.assertEqual(holdout_decision({'depth':3.,'variance':1},[event(10),event(10,covered=False)])['status'],'inconclusive')
    def test_consistency_gate(self):
        result=holdout_decision({'depth':.1,'variance':.0001},[event(1.,.0001),event(1.,.0001)])
        self.assertEqual(result['status'],'non_recovery');self.assertFalse(result['three_se_depth_consistency'])

class ContributionDiagnosticChecks(unittest.TestCase):
    def test_equal_aggregate_different_concentration_does_not_change_recovery(self):
        diffuse=[event(-.1)]+[event(2.2) for _ in range(9)]
        concentrated=[event(-.1),event(19.72)]+[event(.01) for _ in range(8)]
        results=[holdout_decision({'depth':1.97,'variance':.01},rows) for rows in (diffuse,concentrated)]
        for result in results:
            self.assertEqual(result['status'],'recovered');self.assertEqual(result['covered_events'],10)
            self.assertTrue(result['all_covered_events_combined']);self.assertEqual(result['nonpositive_event_count'],1)
            self.assertTrue(result['three_se_depth_consistency']);self.assertAlmostEqual(result['depth'],1.97)
            self.assertAlmostEqual(result['variance'],.1);self.assertAlmostEqual(result['formal_snr'],6.2296869905317065)
            rows=result['event_contributions'];self.assertEqual(len(rows),10)
            self.assertLess(rows[0]['signed_snr_contribution'],0)
            self.assertAlmostEqual(sum(r['normalized_inverse_variance_weight'] for r in rows),1.)
            self.assertAlmostEqual(sum(r['signed_snr_contribution'] for r in rows),result['formal_snr'])
            self.assertIsNone(result['contribution_concentration_unavailable_reason'])
        self.assertAlmostEqual(results[0]['max_absolute_snr_contribution_fraction'],2.2/19.9)
        self.assertAlmostEqual(results[1]['max_absolute_snr_contribution_fraction'],19.72/19.9)
    def test_unequal_weights_signed_contributions_and_original_indices(self):
        events=[event(-2.,4.),event(999.,1e-12,False),event(1.,1.)];unchanged=copy.deepcopy(events)
        result=combine_events(events,2);rows=result['event_contributions']
        self.assertEqual(events,unchanged);self.assertEqual([r['event_index'] for r in rows],[0,2])
        np.testing.assert_allclose([r['normalized_inverse_variance_weight'] for r in rows],[.2,.8])
        np.testing.assert_allclose([r['signed_snr_contribution'] for r in rows],[-.5/math.sqrt(1.25),1/math.sqrt(1.25)])
        self.assertAlmostEqual(result['depth'],.4);self.assertAlmostEqual(result['variance'],.8)
        self.assertAlmostEqual(sum(r['signed_snr_contribution'] for r in rows),result['formal_snr'])
        self.assertAlmostEqual(result['max_absolute_snr_contribution_fraction'],2/3)
    def test_zero_denominator_is_explicit_and_does_not_change_nonrecovery(self):
        result=holdout_decision({'depth':0.,'variance':1.},[event(0.,1.),event(0.,4.)])
        self.assertEqual(result['status'],'non_recovery');self.assertEqual(result['formal_snr'],0.)
        self.assertEqual([r['signed_snr_contribution'] for r in result['event_contributions']],[0.,0.])
        np.testing.assert_allclose([r['normalized_inverse_variance_weight'] for r in result['event_contributions']],[.8,.2])
        self.assertIsNone(result['max_absolute_snr_contribution_fraction'])
        self.assertEqual(result['contribution_concentration_unavailable_reason'],'zero_total_absolute_snr_contribution')
        canonical(result)  # No NaN/Infinity in the reported zero-denominator result.
    def test_cancellation_uses_sum_of_absolute_contributions(self):
        result=holdout_decision({'depth':0.,'variance':1.},[event(-2.),event(2.)])
        self.assertEqual(result['status'],'non_recovery');self.assertEqual(result['formal_snr'],0.)
        self.assertEqual(result['max_absolute_snr_contribution_fraction'],.5)
        self.assertIsNone(result['contribution_concentration_unavailable_reason'])
    def test_noncomputed_results_keep_original_status_and_reasons(self):
        for events,count,reason in [([event(10.)],1,'insufficient_covered_events'),
                ([event(10.,covered=False)],0,'insufficient_covered_events'),
                ([event(1.),event(1.,0.)],2,'invalid_event_statistics')]:
            with self.subTest(reason=reason,covered=count):
                self.assertEqual(combine_events(events,2),{'status':'inconclusive','reason':reason,'covered_events':count})

class GridAndMaskChecks(unittest.TestCase):
    def test_long_gap_baseline_resource_stop(self):
        plan=grid_plan(730.)
        self.assertGreaterEqual(plan['points'],1810401)
        self.assertLessEqual(plan['points'],1810402)
        with self.assertRaises(ResourceStop):make_grid(np.array([0.,1.,729.,730.]))
    def test_grid_endpoints_and_bound(self):
        cfg=Config(period_min=2.,period_max=4.,duration_hours=(2.,))
        grid,plan=make_grid(np.array([0.,3.,10.,17.]),cfg)
        self.assertEqual(grid[0],4.);self.assertEqual(grid[-1],2.)
        self.assertLessEqual(plan['actual_frequency_step_per_day'],plan['max_frequency_step_per_day']*(1+1e-10))
        self.assertEqual(plan['baseline_days'],17.)
    def test_chunk_invariance_and_tie_break(self):
        t=np.arange(0,12,1/144);dy=np.full(len(t),.0002);y=-.003*(abs(phase_distance(t,2.4,.6))<.04)
        periods=1/np.linspace(1/4,1/2,503);cfg=Config(period_min=2,period_max=4,duration_hours=(1.5,2.))
        all_at_once=global_bls_maximum(t,y,dy,periods,cfg,503)
        for chunk in (1,7,37,200):
            self.assertEqual(global_bls_maximum(t,y,dy,periods,cfg,chunk),all_at_once)
        tied=global_bls_maximum(t,np.zeros(len(t)),dy,periods,cfg,17)
        self.assertEqual(tied['period'],2.)
    def test_failed_screen_maximum_still_masks_other_candidate(self):
        attempts=[{'attempt':1,'computation':'computed','screening':'pass','maximum':{'period':3.,'epoch':.5,'duration':.1}},
                  {'attempt':2,'computation':'computed','screening':'failed','maximum':{'period':2.,'epoch':1.,'duration':.1}},
                  {'attempt':3,'computation':'failed','reason':'no_support'}]
        ledger=mask_ledger(attempts)
        np.testing.assert_array_equal(other_mask(np.array([.5,1.,2.5,3.]),ledger,1),[False,True,False,True])
        self.assertEqual(len(ledger),2)
    def test_other_masks_reduce_coverage_including_failed_mask(self):
        t=np.arange(0,2,1/720);clock=CadenceClock(0);duration=.1;center=1.
        support,_=event_support(t,center,duration,clock)
        blocked=abs(t-center)<.04;after,_=event_support(t,center,duration,clock,blocked)
        self.assertTrue(support['covered']);self.assertFalse(after['covered'])
        self.assertGreater(after['windows']['inside']['lost_to_other_masks'],0)
    def test_out_of_sector_expected_cadences_remain_denominator(self):
        t=np.arange(1.,2.,1/720);support,_=event_support(t,1.02,.1,CadenceClock(1.))
        self.assertGreater(support['windows']['left']['expected'],0)
        self.assertEqual(support['windows']['left']['accepted_unique'],0)
        self.assertFalse(support['covered'])
    def test_duplicate_cadence_straddling_window_boundary_rejects_event(self):
        t=np.arange(0,2,1/720);t=t[abs(t-.95)>1e-10];t=np.sort(np.r_[t,.95-1e-6,.95+1e-6])
        support,_=event_support(t,1.,.1,CadenceClock(0))
        self.assertTrue(all(not w['duplicate_cadence_ids'] for w in support['windows'].values()))
        self.assertTrue(support['duplicate_cadence_ids_across_windows']);self.assertFalse(support['covered'])

class TimingChecks(unittest.TestCase):
    def test_signed_negative_event_time_fit(self):
        duration=2/24;t=np.arange(.85,1.15,1/720);shape,_=trapezoid_shape(t,1.008,duration)
        y=.0002+.0001*(t-1)/duration+.003*shape;dy=np.full(len(t),.00005)
        fit=fit_event_time(t,y,dy,1.,duration)
        self.assertEqual(fit['status'],'fitted');self.assertLess(fit['signed_depth'],0)
        self.assertAlmostEqual(fit['time'],1.008,places=7)
        self.assertEqual(np.asarray(fit['full_covariance']).shape,(4,4));self.assertGreater(fit['variance'],0)
    def test_flat_event_covariance_fails(self):
        t=np.arange(.85,1.15,1/720);fit=fit_event_time(t,np.zeros(len(t)),np.full(len(t),.001),1.,2/24)
        self.assertEqual(fit['status'],'inconclusive')
    def test_unsupported_ingress_fails(self):
        t=np.linspace(.999,1.001,20);fit=fit_event_time(t,np.zeros(len(t)),np.full(len(t),.001),1.,2/24)
        self.assertEqual(fit['status'],'inconclusive')
    def test_known_line_covariance_and_alias_failure(self):
        timings=[{'status':'fitted','cycle':n,'time':100+2.7*n,'variance':.01**2} for n in range(3)]
        ep=fit_ephemeris(timings,'resolved');self.assertEqual(ep['status'],'fitted')
        self.assertAlmostEqual(ep['period'],2.7);self.assertAlmostEqual(ep['covariance'][1][1],.00005)
        self.assertEqual(fit_ephemeris(timings,'unresolved')['status'],'inconclusive')
    def test_any_covered_failed_timing_forces_inconclusive(self):
        times=[{'status':'fitted','cycle':n,'time':n*3.,'variance':.0001} for n in range(4)];times[1]={'cycle':1,'status':'inconclusive'}
        self.assertEqual(fit_ephemeris(times,'resolved')['reason'],'a_covered_event_timing_failed_no_subset_selection')
    def test_duplicate_cycles_fail(self):
        times=[{'status':'fitted','cycle':n,'time':float(n),'variance':.0001} for n in [0,0,1]]
        self.assertEqual(fit_ephemeris(times,'resolved')['status'],'inconclusive')
    def test_long_baseline_propagation_inconclusive(self):
        ep={'status':'fitted','epoch':0.,'period':3.,'covariance':[[.0001,0],[0,.0001]]}
        self.assertEqual(predict_uncertainty(ep,(100,110),.1)['reason'],'timing_uncertainty_exceeds_half_duration')

class PreprocessingChecks(unittest.TestCase):
    def test_two_dimensional_flux_and_error_are_rejected(self):
        t=np.arange(10.);flat=np.ones(10);column=np.ones((10,1))
        with self.assertRaises(NumericalStop):checked_arrays(t,column,flat)
        with self.assertRaises(NumericalStop):checked_arrays(t,flat,column)
    def test_common_support_and_gap_sector_normalization(self):
        t=np.r_[np.arange(0,1,.01),np.arange(5,6,.01)];sap=np.r_[np.ones(100),np.ones(100)*2];pdc=sap*3
        errors=np.ones(200)*.001;q=np.zeros(200,int);sec=np.r_[np.ones(100,int),np.ones(100,int)*2]
        sap[5]=np.nan;pdc[7]=-1;q[10]=1
        out=preprocess_sectors(t,sap,pdc,errors,errors,q,sec)
        self.assertEqual(len(out['t']),197);np.testing.assert_allclose(out['y_sap'],0,atol=0)
        np.testing.assert_allclose(out['y_pdc'],0,atol=0)
        self.assertTrue(np.all(out['dy_pdc']>0));self.assertFalse(out['common_input_mask'][5])

class ConnectedPathChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.frozen,cls.summary=run_driver()
    def test_three_attempts_all_frozen_before_holdout(self):
        record=self.frozen['record'];self.assertEqual(len(record['attempts']),3)
        self.assertTrue(record['all_three_attempts_frozen_together']);self.assertFalse(record['holdout_flux_used'])
        self.assertEqual(self.frozen['sha256'],digest(record));self.assertEqual(len(record['mask_ledger']),3)
    def test_connected_recovery_is_fixed_prediction(self):
        result=self.summary['holdout'];self.assertEqual(result['status'],'recovered',self.summary)
        self.assertFalse(result['period_phase_duration_refitted']);self.assertTrue(result['all_covered_events_combined'])
    def test_final_fitted_discovery_depth_is_explicit(self):
        row=self.frozen['record']['attempts'][0]
        self.assertIn('original_screen_combined',row);self.assertIn('final_fitted_events',row)
        self.assertFalse(row['fitted_coverage_change']['changed'])
        self.assertEqual(row['combined'],combine_events(row['final_fitted_events'],3))
    def test_mutated_freeze_rejected(self):
        modified=copy.deepcopy(self.frozen);modified['record']['attempts'][0]['maximum']['period']+=.01
        with self.assertRaises(NumericalStop):evaluate_holdout(modified,1,np.arange(21,22,.01),np.zeros(100),np.ones(100),[21,22],CadenceClock(21))
    def test_overlapping_holdout_rejected_before_classification(self):
        with self.assertRaises(NumericalStop):evaluate_holdout(self.frozen,2,np.arange(10,11,.01),np.zeros(100),np.ones(100),[10,11],CadenceClock(10))
    def test_invalid_holdout_clock_rejected_before_classification(self):
        with self.assertRaises(NumericalStop):evaluate_holdout(self.frozen,2,np.arange(21,22,.01),np.zeros(100),np.ones(100),[21,22],CadenceClock(float('nan')))
    def test_unresolved_alias_is_inconclusive(self):
        result=evaluate_holdout(self.frozen,2,np.arange(21,22,.01),np.zeros(100),np.ones(100),[21,29],CadenceClock(21))
        self.assertEqual(result['status'],'inconclusive');self.assertEqual(result['reason'],'unresolved_or_undeclared_alias')
    def test_narrowed_holdout_span_rejected(self):
        with self.assertRaisesRegex(NumericalStop,'holdout_span_or_cadence_clock'):
            evaluate_holdout(self.frozen,1,np.arange(22,23,.01),np.zeros(100),np.ones(100),[22,29],CadenceClock(21))
    def test_changed_holdout_clock_rejected(self):
        with self.assertRaisesRegex(NumericalStop,'holdout_span_or_cadence_clock'):
            evaluate_holdout(self.frozen,1,np.arange(21,22,.01),np.zeros(100),np.ones(100),[21,29],CadenceClock(21.001))
    def test_rehashed_foreign_implementation_identity_rejected(self):
        changed=copy.deepcopy(self.frozen);changed['record']['source_sha256']='0'*64;changed['sha256']=digest(changed['record'])
        with self.assertRaisesRegex(NumericalStop,'implementation_or_dependency'):
            evaluate_holdout(changed,1,np.arange(21,22,.01),np.zeros(100),np.ones(100),[21,29],CadenceClock(21))
    def test_rehashed_dependency_mismatch_rejected(self):
        changed=copy.deepcopy(self.frozen);changed['record']['execution_identity']['dependencies']['scipy']='different';changed['sha256']=digest(changed['record'])
        with self.assertRaisesRegex(NumericalStop,'implementation_or_dependency'):
            evaluate_holdout(changed,1,np.arange(21,22,.01),np.zeros(100),np.ones(100),[21,29],CadenceClock(21))
    def test_original_sector_edge_fixture_retained_as_inconclusive(self):
        frozen,summary=run_driver(discovery_spans=((0,7),(10,17)))
        self.assertTrue(frozen['record']['attempts'][0]['fitted_coverage_change']['changed'])
        self.assertEqual(summary['holdout']['status'],'inconclusive')
        self.assertEqual(summary['holdout']['reason'],'covered_cycle_set_changed_after_timing_fit_no_iteration')

if __name__=='__main__':unittest.main(verbosity=2)
