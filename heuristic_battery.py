from __future__ import division

from base_battery import BaseBattery


class HeuristicBattery(BaseBattery):
    ''' compute our heuristic strategy '''

    name = 'H2'

    def compute_charge(self, t, pt):
        debug = False  # if True, print out results after the three stages
        # 0. Preparations (definitions, look at critical intervals)
        self.future = xrange(t, self.T)
        # this is our schedule, which we'll update in three stages
        self.w = dict.fromkeys(self.future, 0)
        # some shortcuts
        w = self.w
        self.ka = self.kwh_adj
        p = [pr for pr in self.exp_prices]
        p[t] = pt  # this we know for sure now
        b = self.b
        future = self.future
        B = self.capacity
        Bp = Bm = self.max_rate
        C = self.street.C
        # indices of steps where critical intervals begin
        critical_markers = []
        a = self.avg_price
        for i in future:
            if self.street.is_critical(i, 0, p[i]):
                if i == 0 or not self.street.is_critical(i - 1, 0, p[i - 1]):
                    critical_markers.append(i)
        # so we run through the while loop at least once
        critical_markers.append(max(self.future) + 1)
        if debug:
            print("we are at t={}, critical markers {}:"\
                    .format(t, critical_markers))
        # 1. make wishlist w, based on classifing time steps in low- or
        #  high prices (here, we wish ourselves maximum actions, i.e. buy as
        #  much, sell as much as the battery rate allows if we like the price)
        for i in future:
            fp, fm = self.street.f(i, 0, p[i])
            if self.street.is_critical(i, 0, p[i]):
                inT = i == t
                w[i] = super(HeuristicBattery, self).compute_charge(i, p[i],
                                                             checkB=inT)  # H1
                if inT:
                    return w[i]  # t is critical, this is all we do
            elif p[i] > a:
                w[i] = -min(Bm, C + fm)
            else:
                w[i] = min(Bp, C - fp)
        if debug:
            print("wishlist after stage 1: ",
                  [round(x, 2) for x in self.w.values()])
        # from here on, we reduce our desired actions)
        first = t  # this always points to the first non-critical step
        next_critical = critical_markers.pop(0)
        while next_critical:
            # 2. Make non-critical interval feasible
            i = first  # the first step of our currently considered range
            while i < next_critical:
                if b(i + 1) > B:  # if w[i] causes a problem
                    lp = self.same_sign_steps(i, first, next_critical)
                    self.buy_less_than_wished(lp, 1/self.ka * (b(lp[-1] + 1) - B))
                    i = lp[-1] + 1
                elif b(i + 1) < 0:
                    lm = self.same_sign_steps(i, first, next_critical)
                    self.sell_less_than_wished(lm, 1/self.ka * (- b(lm[-1] + 1)))
                    i = lm[-1] + 1
                else:
                    i += 1
            if i >= self.T:
                break
            if debug:
                print("wishlist after stage 2:",
                        [round(x, 2) for x in self.w.values()])
            # 3. Make critical interval feasible
            if self.street.is_critical(i, 0, p[i]):
                # select list of consecutive same-sign critical steps
                X = self.same_sign_steps(next_critical, next_critical,
                                                        self.T, True)
                Sx = sum(w[j] for j in X)
                # Case 1: not enough on battery for critical interval
                if Sx < 0 and b(next_critical) > Sx:
                    lm = [j for j in xrange(first, next_critical) if w[j] < 0]
                    self.sell_less_than_wished(lm, 1/self.ka * (abs(Sx) - b(next_critical)),
                                               True)
                # Case 2: critical interval would exceed capacity
                if Sx > 0 and b(next_critical) > B - Sx:
                    lp = [j for j in xrange(first, next_critical) if w[j] > 0]
                    self.buy_less_than_wished(lp, 1/self.ka * (b(next_critical) - B + Sx),
                                              True)
                # move indices to next non-critical interval
                first = i
                while first < 47 and self.street.is_critical(first, 0,
                                                             p[first]):
                    first += 1
                    if first >= self.T:
                        break
            if len(critical_markers) > 0:
                next_critical = critical_markers.pop(0)
            else:
                next_critical = None
            if debug:
                print("wishlist after stage 3:",
                        [round(x, 2) for x in self.w.values()])

        return w[t]

    def b(self, t):
        '''compute b_t, the (expected) battery level at (before!) time t'''
        bt = self.level
        for i in xrange(self.future[0], t):
            if self.w[i] > 0:
                bt += self.ka * self.w[i] * self.efficiency
            else:
                bt += self.ka * self.w[i]
        return bt

    def same_sign_steps(self, t, start, up_to, critical_condition=False):
        '''
        Return a list of consecutive steps that include t and all have the
        same sign as w[t] (up to, but not including up_to) and have the same
        criticality condition.
        '''
        l = []
        p = self.exp_prices
        w = self.w
        for j in xrange(start, up_to):
            if j == t:
                l.append(t)
                continue
            if w[t] * w[j] > 0 \
                and self.street.is_critical(j, 0, p[j])\
                        is critical_condition:
                l.append(j)
            else:
                if j < t:
                    l = []
                if j > t:
                    return l
        return l

    def sell_less_than_wished(self, lp, r, checkb=False):
        '''Reduce sales (in w) by r. lp is indices of selling steps.'''
        p = self.exp_prices
        w = self.w
        # we will use lp later, so work on copy
        lpr = [i for i in lp]
        # sort by increasing price
        lpr.sort(key=lambda x: p[x])
        for i in lpr:
            oldwi = w[i]
            w[i] = min(0, w[i] + r)
            if checkb:
                if self.is_bfeasible(lp[0], lp[-1]):
                    r -= abs(w[i] - oldwi)
                else:
                    w[i] = oldwi
            else:
                r -= abs(w[i] - oldwi)
            if r == 0:
                return

    def buy_less_than_wished(self, lm, r, checkb=False):
        '''Reduce buying (in w) by r. lm is indices of buying steps.'''
        p = self.exp_prices
        w = self.w
        r /= self.efficiency
        # we will use lm later, so work on copy
        lpr = [i for i in lm]
        # sort by decreasing price
        lpr.sort(key=lambda x: -p[x])
        for i in lpr:
            oldwi = w[i]
            w[i] = max(0, w[i] - r)
            if checkb:
                if self.is_bfeasible(lm[0], lm[-1]):
                    r -= abs(w[i] - oldwi)
                else:
                    w[i] = oldwi
            else:
                r -= abs(w[i] - oldwi)
            if r == 0:
                return

    def is_bfeasible(self, start, end):
        ''' is this interval in w feasible for the battery?'''
        for i in xrange(start, end + 1):
            if self.w[i] > self.max_rate or self.w[i] < - self.max_rate:
                return False
            bi = self.b(i + 1)  # let's check if it is okay after i
            if 0 > bi or bi > self.capacity:
                return False
        return True


class DeterministicH2Battery(HeuristicBattery):

    '''
    Use this for a heuristic battery using H2 which gets the actual_prices
    as input (if you want to see how good it could be).
    '''

    name = 'H2-KnowAll'
