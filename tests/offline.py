from __future__ import division

import unittest
import sys
sys.path.append('..')

from offline_battery import OfflineBattery


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


class OfflineTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_offline(self):
        '''
        Each case consists of T, C, B, b0, max_charge_rate, c_h,
        a list of prices, a list of fp values and a list of fm values
        (lists should all have length T).
        alpha is assumed to be one (100% efficient battery).
        w (\omega) is assumed to be 1.
        The output of each case is the wishlist.
        '''

        cases = {}
        # Case 1a: a toy example: first five critical steps (need to sell), then 
        #          high-priced non-critical steps, where we also like to sell.
        #          Battery buys when it doesn't resolve, in order to sell later.
        #          If it resolves, it does so reducing consecutive intervals.
        prices = (.501, .502,  .503,  .504,  .505,  .8,  .8,  .8)
        fps =   ( 55,  55,  55,  55,  55,  30,  30,  30)
        fms =   (-10, -10, -10, -10, -10, -10, -10, -10)
        cases[(8, 50, 20, 10, 5, 1.2, prices, fps, fms)] =\
                {0: 5, 1: -5, 2: 5, 3: -5, 4: 5, 5: -5, 6: -5, 7: -5}

        # Case 1b: We shorten the critical interval, add another high-price step.
        #          Resolving is less worthwhile than buying now and 
        #          selling later, since the profit 5*(.8-.5)=1.5, bigger than
        #          even 1.2^2
        prices = (.501, .502,  .503,  .504,  .8,  .8,  .8, .8)
        fps =   ( 55,  55,  55,  55,  30,  30,  30,  30)
        fms =   (-10, -10, -10, -10, -10, -10, -10, -10)
        cases[(8, 50, 20, 10, 5, 1.2, prices, fps, fms)] =\
                {0: 5, 1: 5, 2: -5, 3: 5, 4: -5, 5: -5, 6: -5, 7: -5}


        for c in cases.keys():
            T = c[0]
            prices = c[6]
            self.assertEquals(len(prices), T)
            self.assertEquals(len(c[7]), T) # fps
            self.assertEquals(len(c[8]), T) # fms
            s = DummyStreet(C=c[1], fps=c[7], fms=c[8])
            b = OfflineBattery(capacity=c[2], efficiency=1, max_rate=c[4],
                    street=s, exp_prices=prices, avg_price=.5, T=T, c_h=c[5])

            b.level = c[3]
            b.max_runtime = 1
            b.max_k = 10
            b.solve_offline(1)  # TODO assumption about w
            #print b.w
            bcharge = b.w[0]
            self.assertEqual(round(bcharge, 2), cases[c][0])
            self.assertEqual(b.w, cases[c])
