import math
import pymprog

from base_battery import BaseBattery


class OfflineBattery(BaseBattery):
    ''' compute optimal offline solution '''

    name = 'Offline'

    def solve_offline(self, w):
        ''' pre-compute offline solution '''
        T = range(self.T)
        self.w = dict.fromkeys(T, 0)  # vector of charges and discharges

        # making some shortcuts so the LP is more readable and similar to
        # the model in our paper
        b0 = self.level
        # we use a positive Bm in this problem (like d)
        Bp = Bm = self.max_rate
        B = self.capacity
        CC = self.street.C
        alpha = self.efficiency
        p = self.exp_prices

        # magnitudes without me involved
        fp0 = [self.street.f(t, 0, p[t])[0] for t in T]
        fm0 = [self.street.f(t, 0, p[t])[1] for t in T]
        # maximal limit for magnitude we expect
        maxx = 100
        # maximal number of consecutive critical steps
        K = range(1)
        e = [math.pow(self.c_h, k + 1) for k in K]
        TK  = [(t,k) for t in T for k in K if k <= t]

        pymprog.beginModel('offline')
        #pymprog.verbose(True)
        pymprog.solvopt(tm_lim=1000*60*4) #  max. time in milliseconds
        #print "Options:", pymprog.solvopt()

        # create variables
        c = pymprog.var(T, 'C')  # charges
        d = pymprog.var(T, 'D')  # discharges
        x = pymprog.var(T, 'X')  # max mag on cable
        # True if there have been at least k-1 consecutive
        # critical steps before t
        v = pymprog.var(T, 'V')  # cost
        co = pymprog.var(TK, 'CO', bool) # consecutive overload

        # set objective
        pymprog.minimize(
            w * sum(v[t] for t in T) - sum(p[t] * (d[t] - c[t]) for t in T),
            'wC-R'
        # we use a positive d in this problem
        )

        # set constraints
        # ... battery contraints
        pymprog.st(0 <= c[t] <= Bp for t in T)
        pymprog.st(0 <= d[t] <= Bm for t in T)
        # we use a positive d in this problem
        for t in T:
            pymprog.st(b0 + sum(alpha * c[j] - d[j] for j in range(t + 1)) <= B)
            pymprog.st(b0 + sum(alpha * c[j] - d[j] for j in range(t + 1)) >= 0)
        # ... cable constraints
        pymprog.st(x[t] >= 0 for t in T)
        pymprog.st(x[t] >= fp0[t] + c[t] - d[t] for t in T)
        pymprog.st(x[t] >= -fm0[t] - c[t] + d[t] for t in T)
        pymprog.st(x[t] >= -fp0[t] - c[t] + d[t] for t in T)
        pymprog.st(x[t] >= fm0[t] + c[t] - d[t] for t in T)

        # ... cons. overloading constraints
        pymprog.st(v[t] >= e[k] * co[t, k] for t, k in TK)
        pymprog.st(co[t, 0] >= (x[t]-CC)/(maxx - CC) for t in T)
        #pymprog.st(co[t, k] <= co[t, k-1] for t, k in TK if (t, k-1) in TK)
        pymprog.st(co[t, k] >= co[t-1, k-1] + co[t, k-1] - 1.5 for t, k in TK if ((t, k-1) in TK and (t-1, k-1) in TK))

        pymprog.solve()
        # status can be in (opt, feas, undef)
        assert(pymprog.status() in ('opt', 'feas'))
        # value of objective (this should meet the actual outcome!)
        #print 'Objective = {}'.format(pymprog.vobj())
        # use sthg like this to inspect variables
        #print ';\n'.join('%s = %g {dual: %g}' % (
        #            x[t].name, x[t].primal, x[t].dual)
        #                    for t in T)

        for t in T:
            self.w[t] = c[t].primal - d[t].primal

    def compute_charge(self, t, pt):
        if self.name == 'Offline':
            assert(self.exp_prices[t] == pt)
        return self.w[t]


class NonDeterministicOfflineBattery(OfflineBattery):

    '''
    Use this for an offline battery which gets the expected prices as input
    '''

    name = 'Offline-ExpPrices'
