from __future__ import division

import math

from customers import Consumer, Generator


class Street(object):
    '''
    '''

    def __init__(self, T, N, C, Dmax, Smax, pmax, pmin, c_h, adaptive, slope,
                 placement_optimistic):
        self.N = N
        assert(N % 2 == 0)
        self.C = C
        self.Dmax = Dmax
        self.Smax = Smax
        self.c_h = c_h
        self.adaptive = adaptive
        self.slope = slope
        self.placement_optimistic = placement_optimistic
        self.cable = []
        self.magnitudes = dict.fromkeys(range(T), 0)
        self.magnitudes_per_segment = {}
        # one segment for each customer, one for battery
        for n in range(N + 1):
            self.magnitudes_per_segment[n] = dict.fromkeys(range(T), 0)
        if placement_optimistic:
            for _ in range(int(N / 2)):
                self.cable.append(Consumer(Dmax, pmax, pmin, adaptive, slope))
                self.cable.append(Generator(Smax))
        else:
            for _ in range(int(N / 2)):
                self.cable.append(Consumer(Dmax, pmax, pmin, adaptive, slope))
            for _ in range(int(N / 2)):
                self.cable.append(Generator(Smax))

    def __repr__(self):
        return '[Cable N={}, C={}, Dmax={}, Smax={}, adaptive={},'\
                'slope={}, optimistic={}]'\
            .format(self.N, self.C, self.Dmax, self.Smax, self.adaptive,
                    self.slope, self.placement_optimistic)

    def f(self, t, bcharge, pt):
        '''
        Compute f^+ and f^- on cable y going from end to start
        Note: These are not absolute values.
        '''
        level = fp = fm = bcharge
        l = len(self.cable)
        for i in xrange(1, l + 1):
            level += self.cable[l - i].level(t, pt)
            fp = max(fp, level)
            fm = min(fm, level)
        return fp, fm

    def magnitude(self, t, bcharge, pt):
        ''' magnitude (absolute value) of cable level '''
        return max([abs(f) for f in self.f(t, bcharge, pt)])

    def maxf(self, t, bcharge, pt):
        ''' return fp or fm - the one with higher absolute value '''
        fp, fm = self.f(t, bcharge, pt)
        if fp > abs(fm):
            return fp
        else:
            return fm

    def cost(self, t, bcharge, pt):
        ''' In this work, we use a specific cost function'''
        return self.cost_consecutive(t, bcharge, pt)

    def cost_binary(self, t, bcharge, pt):
        '''
        Overheating costs (binary, ignores actual magnitude to compute costs)
        '''
        magnitude = self.magnitude(t, bcharge, pt)
        if magnitude <= self.C:
            return 0
        else:
            return 1

    def cost_magnitude(self, t, bcharge, pt):
        '''
        Overheating costs (by magnitude)
        '''
        magnitude = self.magnitude(t, bcharge, pt)
        if magnitude <= self.C:
            return 0
        else:
            return magnitude - self.C

    def cost_consecutive(self, t, bcharge, pt):
        '''
        Overheating by consecutive overloading, ignores actual magnitude
        '''
        magnitude = self.magnitude(t, bcharge, pt)
        self.magnitudes[t] = magnitude
        consecutive_overheating = 0
        for i in xrange(0, t):
            if self.magnitudes[t - i] > self.C:
                consecutive_overheating += 1
            else:
                break
        if consecutive_overheating == 0:
            return 0
        else:
            return math.pow(self.c_h, consecutive_overheating)

    def cost_consecutive_persegment(self, t, bcharge, pt):
        '''
        Overheating consecutively, by segment, ignores actual magnitude
        '''
        # first, we update magnitudes per segment
        level = bcharge
        self.magnitudes_per_segment[0][t] = abs(bcharge)
        l = len(self.cable)
        for segment in xrange(1, l + 1):
            level += self.cable[l - segment].level(segment, pt)
            self.magnitudes_per_segment[segment][t] = abs(level)
        # now we compute costs per segment for t
        costs = 0
        for segment in xrange(0, l + 1):
            consecutive_overheating = 0
            for i in xrange(0, t):  # looking back in time
                if self.magnitudes_per_segment[segment][t - i] > self.C:
                    consecutive_overheating += 1
                else:
                    break
            if consecutive_overheating > 0:
                costs += math.pow(self.c_h, consecutive_overheating)
        return costs

    def is_critical(self, t, bcharge, pt):
        return self.magnitude(t, bcharge, pt) > self.C

    def draw(self, t, bcharge, pt):
        ''' draw the state at this price and battery charge '''
        print
        print self
        print '[t: {}, bcharge: {}, pt: {}]'.format(t, bcharge, pt)
        fp, fm = self.f(t, bcharge, pt)
        print '[fp: {}, fm: {}]'.format(round(fp, 2), round(fm, 2))

        l = len(self.cable)
        levels = dict.fromkeys(xrange(1, l + 2), 0)
        levels[len(levels)] = bcharge
        # compute all segment levels (back to front)
        for i in xrange(l - 1, -1, -1):
            levels[i] = levels[i + 1] + self.cable[i].level(t, pt)

        def fmt(v):
            return str(round(v, 8)).rjust(7)

        print
        # print negative charges (generation)
        for i in xrange(0, l):
            val = self.cable[i].level(t, pt)
            if val < 0:
                print fmt(val),
            else:
                print '       ',
        if bcharge < 0:
            print fmt(bcharge)
        print '\n'
        # print states
        print self.N * '-----------'
        for i in xrange(0, len(levels)):
            print fmt(levels[i]),
        print
        print self.N * '-----------'
        # print positives (consumption)
        for i in xrange(0, l):
            val = self.cable[i].level(t, pt)
            if val > 0:
                print fmt(val),
            else:
                print '       ',
        if bcharge >= 0:
            print fmt(bcharge)
