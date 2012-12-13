
class Customer(object):

    def level(self, t, pt):
        pass


class Consumer(Customer):

    def __init__(self, Dmax, adaptive, econ_slope):
        self.Dmax = Dmax
        self.adaptive = adaptive
        self.slope = econ_slope

    def level(self, t, pt):
        ev = 0.0
        gam = self.slope
        pmax = 0.452
        pmin = 0.074
        if t in xrange(0, 14) or t in xrange(38, 48):
            ev = 1 # EV battery charging
        if self.adaptive:
            l = (self.Dmax + ev + gam * pmin) - gam * pt
        else:
            # mirroring adaptive curve: assume max price (1) to arrive at
            # Dmax EV, then go upwards from there
            l = (self.Dmax + ev - gam * pmax) + gam * pt
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
