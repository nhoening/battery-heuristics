from __future__ import division

import unittest
import sys
sys.path.append('..')

from street import Street


class StreetTest(unittest.TestCase):

    def setUp(self):
        pass
 
    def test_f(self):
        '''
        '''
        cases = {}
        # Each case: t, N, Dmax, Smax, c_h, adaptive, slope, placement_optimistic, bcharge, pt = result
        # Case 1a: consumer first, thus generator last, who creates negative 1
        #          consumer always adds 2.75
        cases[(26, 10, 3, 1, 1.2, True, .5, True, 0, .5)] = (round(5 * 2.787 + 5 * -1, 4), -1)
        # Case 1b: Now price is adapted, so they buy 2.887
        cases[(26, 10, 3, 1, 1.2, True, .5, True, 0, .3)] = (round(5 * 2.887 + 5 * -1, 4), -1)
        # Case 1c: Now try pessimistic
        cases[(26, 10, 3, 1, 1.2, True, .5, False, 0, .3)] = (round(5 * 2.887 + 5 * -1, 4), -5)
        # Case 2: try higher N
        cases[(26, 30, 3, 1, 1.2, True, .5, True, 0, .3)] = (round(15 * 2.887 + 15 * -1, 4), -1)
        # Case 3: test non-adaptive case. They buy 2.924
        cases[(26, 10, 3, 1, 1.2, False, .5, True, 0, .3)] = (round(5 * 2.924 + 5 * -1, 4), -1)
        # Case 4: different time step: let house batteries charge, no PV
        cases[(38, 10, 3, 1, 1.2, True, .5, True, 0, .3)] = (round(5 * 3.887, 4), 0)
        # Case 5a: our battery charges 0.6
        cases[(26, 10, 3, 1, 1.2, True, .5, True, 0.6, .3)] = \
                        (round(.6 + (5 * 2.887  + 5 * -1), 4), -1 + 0.6)
        # Case 5b: and discharge
        cases[(26, 10, 3, 1, 1.2, True, .5, True, -0.6, .3)] = \
                        (round(-.6 + (5 * 2.887  + 5 * -1), 4), -1 - 0.6)

        for c in cases.keys():
            T = c[0]
            s = Street(T=T+1, N=c[1], C=None, Dmax=c[2], Smax=c[3], pmax=.452, pmin=.074, c_h=c[4],
                       adaptive=c[5], slope=c[6], placement_optimistic=c[7])
            #s.draw(T, c[8], c[9])
            fp, fm = s.f(T, c[8], c[9])
            self.assertEqual((round(fp, 4), round(fm, 4)), cases[c])
