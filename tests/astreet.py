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
        # Each case: t, N, Dmax, Smax, adaptive, slope, placement_optimistic, bcharge, pt = result
        # Hour 18: PVs are on
        # Case 1a: consumer first, thus generator last, who creates negative 1
        #          consumer always adds 2.75
        cases[(18, 10, 3, 1, True, .5, True, 0, .5)] = (round(5 * 2.75 + 5 * -1, 2), -1)
        # Case 1b: Now price is adapted, so they buy 2.85
        cases[(18, 10, 3, 1, True, .5, True, 0, .3)] = (round(5 * 2.85 + 5 * -1, 2), -1)
        # Case 1c: Now try pessimistic
        cases[(18, 10, 3, 1, True, .5, False, 0, .3)] = (round(5 * 2.85 + 5 * -1, 2), -5)
        # Case 2: try higher N
        cases[(18, 30, 3, 1, True, .5, True, 0, .3)] = (round(15 * 2.85 + 15 * -1, 2), -1)
        # Case 3: test non-adaptive case. They buy 2.65
        cases[(18, 10, 3, 1, False, .5, True, 0, .3)] = (round(5 * 2.65 + 5 * -1, 2), -1)
        # Case 4: different time step: let house batteries charge, no PV
        cases[(36, 10, 3, 1, True, .5, True, 0, .3)] = (round(5 * 3.85, 2), 0)
        # Case 5: our battery charges 0.6
        cases[(18, 10, 3, 1, True, .5, True, 0.6, .3)] = \
                        (round(.6 + (5 * 2.85  + 5 * -1), 2), -1 + 0.6)
        # Case 4b: and discharge
        cases[(18, 10, 3, 1, True, .5, True, -0.6, .3)] = \
                        (round(-.6 + (5 * 2.85  + 5 * -1), 2), -1 - 0.6)
        for c in cases.keys():
            T = c[0]
            s = Street(T=T+1, N=c[1], C=None, Dmax=c[2], Smax=c[3], adaptive=c[4],
                       slope=c[5], placement_optimistic=c[6])
            #s.draw(t, c[7], c[8])
            fp, fm = s.f(T, c[7], c[8])
            self.assertEqual((round(fp, 2), round(fm, 2)), cases[c])
