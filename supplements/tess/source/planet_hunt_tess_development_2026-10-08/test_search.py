"""Offline implementation checks, not astrophysical validation."""
import unittest
import numpy as np
from search import search, detrend, phase_distance, CONFIG

class Checks(unittest.TestCase):
    def test_synthetic_period_recovery(self):
        rng=np.random.default_rng(8513)
        t=np.arange(0,25,1/48)
        y=rng.normal(0,0.00012,len(t))
        y[np.abs(phase_distance(t,2.713,0.293))<0.052]-=0.003
        result,_=search(t,y)
        self.assertLess(abs(result['period_days']-2.713),0.01)
        # Independently reconstruct its exact phase-bin membership and LS score.
        ph=np.floor(((t-t.min())/result['period_days']%1)*CONFIG['phase_bins']).astype(int)%CONFIG['phase_bins']
        inside=((ph-result['phase_start_bin'])%CONFIG['phase_bins'])<result['phase_width_bins']
        pred=np.where(inside,y[inside].mean(),y[~inside].mean())
        direct=np.sum((y-y.mean())**2)-np.sum((y-pred)**2)
        self.assertAlmostEqual(direct,result['score'],places=12)
        self.assertAlmostEqual((y[~inside].mean()-y[inside].mean())*1e6,result['depth_ppm'],places=7)
    def test_flat_has_no_positive_peak(self):
        with self.assertRaises(ValueError): search(np.arange(0,25,1/48),np.zeros(1200))
    def test_gap_baseline_not_bridged(self):
        t=np.r_[np.arange(0,1,0.02),np.arange(5,6,0.02)]
        f=np.r_[np.ones(50),np.full(50,2.)]
        y,tr=detrend(t,f)
        np.testing.assert_allclose(y,0.,atol=0)
    def test_nonpositive_or_unsorted_input_rejected(self):
        t=np.arange(20.)
        with self.assertRaises(ValueError): detrend(t,np.zeros(20))
        with self.assertRaises(ValueError): detrend(t[::-1],np.ones(20))
    def test_phase_wrap(self):
        x=phase_distance(np.array([-0.1,0.,2.9,3.,3.1]),3.,0.)
        np.testing.assert_allclose(x,[-.1,0.,-.1,0.,.1],atol=1e-14)
    def test_export_shape_and_order(self):
        from search import ROOT
        a=np.loadtxt(ROOT/'data/toi270_s4_binned.csv',delimiter=',')
        self.assertEqual(a.shape,(965,3))
        self.assertTrue(np.all(np.diff(a[:,0])>0))
if __name__=='__main__': unittest.main(verbosity=2)
