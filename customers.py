
class Customer(object):

    def level(self, t, pt):
        pass


class Consumer(Customer):

    def __init__(self, Dmax, pmax, pmin, adaptive, econ_slope):
        self.Dmax = Dmax
        self.pmax = pmax
        self.pmin = pmin
        self.adaptive = adaptive
        self.slope = econ_slope

    def level(self, t, pt):
        ev = 0.0
        gam = self.slope
        if t in xrange(0, 14) or t in xrange(38, 48):
            ev = 1 # EV battery charging
        if self.adaptive:
            l = (self.Dmax + ev + gam * self.pmin) - gam * pt
        else:
            # mirroring adaptive curve: assume max price (1) to arrive at
            # Dmax EV, then go upwards from there
            l = (self.Dmax + ev - gam * self.pmax) + gam * pt
        return max(l, 0)


class Generator(Customer):
    '''
    Modeling PV panels that work only during the day (12am to 4pm).
    We count sold levels in the negative.
    '''

    def __init__(self, S):
        self.S = S

    def level(self, t, pt):
        if t in xrange(24, 32):
            return -self.S # PV output
        else:
            return 0
