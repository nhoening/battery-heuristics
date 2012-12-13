from __future__ import division

import unittest
import sys
sys.path.append('..')

from base_battery import BaseBattery


class DummyStreet(object):

    def __init__(self, C, fp, fm):
        self.C = C
        self.fp = fp
        self.fm = fm

    def f(self, t, bc, pt):
        return self.fp, self.fm

    def is_critical(self, t, bc, pt):
        if abs(self.fm) > self.fp:
            return self.C < abs(bc + self.fm)
        else:    
            return self.C < bc + self.fp


class H1Test(unittest.TestCase):

    def setUp(self):
        pass
 
    def test_h1(self):
        '''
        '''
        b = BaseBattery(capacity=10, efficiency=.7, max_rate=8, street=None,
                  exp_prices=[], avg_price=.5, T=48, c_h=1.2)
        #b = BaseBattery(10, .7, 8, None, [], 100)
        b.level = 1
        cases = {}
        cases[(13, -9)] = -1
        cases[(8, -7)] = 2
        cases[(4, -4)] = 4 * (1 / b.efficiency)
        cases[(11, -13)] = 1
        cases[(11, -8)] = -1
        cases[(8, -11)] = 1
        cases[(11, -10)] = -.5
        cases[(12, -12)] = 0
        cases[(0, 0)] = 4 * (1 / b.efficiency)
        cases[(7, -5)] = 3
        cases[(3, -5)] = 4 * (1 / b.efficiency)
        
        for c in cases.keys():
            s = DummyStreet(10, c[0], c[1])
            b.street = s
            self.assertEqual(b.compute_charge(None, None), cases[c])
        
