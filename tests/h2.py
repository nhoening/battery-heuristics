from __future__ import division

import unittest
import sys
sys.path.append('..')

from heuristic_battery import HeuristicBattery


class DummyStreet(object):

    def __init__(self, C, fps, fms):
        '''
        fps is a dict of fp values per time slot
        fms is a dict of fm values per time slot
        '''
        self.C = C
        self.fps = fps
        self.fms = fms

    def f(self, t, bc, pt):
        return self.fps[t], self.fms[t]

    def is_critical(self, t, bc, pt):
        if abs(self.fms[t]) > self.fps[t]:
            return self.C < abs(bc + self.fms[t])
        else:
            return self.C < bc + self.fps[t]


class H2Test(unittest.TestCase):

    def setUp(self):
        pass

    def test_h2(self):
        '''
        Each case consists of T, C, B, b0, max_charge_rate, c_h, a list of prices, a list
        of fp values and a list of fm values (lists should all have length T).
        alpha is assumed to be one (100% efficient battery).
        The output of each case is the wishlist w.
        '''

        cases = {}
        # Case 1: our simple whiteboard example
        prices = (.6, .55,  .1,  .4,  .6,  .8,  .9,  .3,  .4)
        fps =   ( 10,  35,  55,  40,  30,  20,  46,  45,  40)
        fms =   (-40, -40, -20, -30, -40, -45, -60, -35, -30)
        cases[(9, 50, 20, 7, 8, 1.0, prices, fps, fms)] =\
                {0: -2, 1: 0, 2: -5, 3: 8, 4: -3, 5: -5, 6: +7, 7: 5, 8: 8}

        # Case 2: with consecutive critical steps
        prices = (.4,  .3,  .6,  .7,  .6,  .3,  .6,  .7)
        fps =   ( 40,  45,  30,  50,  45,  55,  20,  40)
        fms =   (-40, -40, -20, -60, -55, -30, -20, -30)
        cases[(8, 50, 20, 10, 8, 1.0, prices, fps, fms)] =\
                {0: 3, 1: 5, 2: -8, 3: 5, 4: 5, 5: -5, 6: -7, 7: -8}

        # Case 3: similar to Case 1 
        prices = (.7, .6,  .1,  .4,  .6,  .8,  .9,  .3,  .4)
        fps =   ( 10,  35,  55,  40,  40,  40,  35,  40,  40)
        fms =   (-40, -40, -20, -30, -30, -30, -60, -35, -30)
        cases[(9, 50, 20, 7, 8, 1.0, prices, fps, fms)] =\
                {0: -2, 1: 0, 2: -5, 3: 8, 4: 0, 5: -8, 6: 8, 7: 8, 8: 4}


        for c in cases.keys():
            T = c[0]
            prices = c[6]
            self.assertEquals(len(prices), T)
            self.assertEquals(len(c[7]), T) # fps
            self.assertEquals(len(c[8]), T) # fms
            s = DummyStreet(C=c[1], fps=c[7], fms=c[8])
            b = HeuristicBattery(capacity=c[2], efficiency=1, max_rate=c[4],
                    street=s, exp_prices=prices, avg_price=.5, T=T, c_h=c[5])

            b.level = c[3]
            bcharge = b.compute_charge(0, prices[0])
            self.assertEqual(round(bcharge, 2), cases[c][0])
            self.assertEqual(b.w, cases[c])
