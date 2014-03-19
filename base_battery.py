from __future__ import division

import math


class BaseBattery(object):

    name = 'H1'

    def __init__(self, capacity, efficiency, max_rate, street, exp_prices,
                 avg_price, T, c_h, kwh_adj=1):
        self.capacity = capacity
        self.efficiency = efficiency
        assert(efficiency >= 0 and efficiency <= 1)
        self.max_rate = max_rate
        self.street = street
        self.exp_prices = exp_prices
        self.avg_price = avg_price
        self.T = T
        self.c_h = c_h
        self.kwh_adj = kwh_adj
        self.level = self.capacity / 2.
        self.account = -self.level * self.avg_price

    def compute_charge(self, t, pt, checkB=True):
        '''
        Basic heuristic strategy H1: if cable is not critical,
        try to get close to half capacity
        '''
        fp, fm = self.street.f(t, 0, pt)
        C = self.street.C
        if self.street.is_critical(t, 0, pt):
            # return best possibility to reduce over-capacity of cable
            A = (fp + fm) / - 2
            if fp >= abs(fm):
                A = max(A, C - fp)
            else:
                A = min(A, -C - fm)
        else:
            # go as near to half capacity as possible
            A = 1/self.kwh_adj * (self.capacity / 2. - self.level)
            if A > 0:  # account for efficiency losses
                A *= 1 / self.efficiency
            # respect cable constraint
            A = min(A, C - fp)
            A = max(A, - C - fm)
        # respect physical limits
        if checkB:
            if A > 0 and self.kwh_adj * (A * self.efficiency) > self.capacity - self.level:
                A = 1/self.kwh_adj * (self.capacity - self.level)
            A = max(A, -self.level * 1/self.kwh_adj)
        A = min(A, self.max_rate)
        A = max(A, -self.max_rate)
        return A

    def execute_charge(self, charge, pt):
        '''
        Do all the bookkeeping necessary when actually charging.
        This is the place where we actually round charges to fix outcomes.
        Return revenues made in step t.
        '''
        precision = 2  # rounding precision

        def rounddown(num):
            '''
            rounding, preventing us from accumulating rounding-up errors
            '''
            num2 = round(num, precision)
            if abs(num2) > abs(num):
                adapt = 1 / math.pow(10, precision)
                if num > 0:
                    return num2 - adapt
                else:
                    return num2 + adapt
            else:
                return num2

        # we round down to get rid of inexactness from * and /
        rounding_needed = not self.name.startswith('Offline')
        
        if rounding_needed:
            charge = rounddown(charge)
        assert(charge <= self.max_rate)
        assert(charge >= -self.max_rate)
        
        if charge > 0:  # Apply efficiency. Efficiency only affects level,
                        # not revenue or what the cable experiences!
            if rounding_needed:
                self.level += self.kwh_adj * rounddown(charge * self.efficiency)
            else:
                self.level += self.kwh_adj * (charge * self.efficiency)
        else:
            self.level += self.kwh_adj * charge
        if rounding_needed:
            self.level = rounddown(self.level)
        try:
            assert(round(self.level, precision) >= 0)
            assert(round(self.level, precision) <= self.capacity)
        except:
            print('Ooops: {}'.round(self.level))
            raise
        revenue = -1 * charge * pt  # negative bcs sales amounts are negative,
                                    # but we earn by selling and pay for buying
        self.account += revenue
        return revenue


class NoBattery(BaseBattery):
    ''' use this when no battery is present '''

    name = 'No Battery'

    def compute_charge(self, t, pt):
        return 0
