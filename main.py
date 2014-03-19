#!/usr/bin/python
from __future__ import division

import sys
from ConfigParser import ConfigParser
import random

from street import Street
from base_battery import BaseBattery, NoBattery
from offline_battery import OfflineBattery, NonDeterministicOfflineBattery
from heuristic_battery import HeuristicBattery, DeterministicH2Battery


def main(conf, log, seed):
    ws = [.05, .2, .5, 1, 2]
    battery_types = (NoBattery, OfflineBattery, BaseBattery,
                     HeuristicBattery, NonDeterministicOfflineBattery)
    #battery_types = (NoBattery, BaseBattery, HeuristicBattery,)

    T = 48  # this is given by the price data structure: half-hour intervals
    N = conf.getint('params', 'N')
    C = conf.getint('params', 'C')
    B = conf.getfloat('params', 'B')
    alpha = conf.getfloat('params', 'alpha')
    max_rate = conf.getfloat('params', 'max_rate')
    econ_slope = conf.getfloat('params', 'econ_slope')
    Dmax = conf.getfloat('params', 'Dmax')
    Smax = conf.getfloat('params', 'Smax')
    pmax = conf.getfloat('params', 'pmax')
    pmin = conf.getfloat('params', 'pmin')
    c_h = conf.getfloat('params', 'c_h')
    adaptive = conf.getboolean('params', 'adaptive')
    placement_optimistic = conf.getboolean('params', 'placement_optimistic')
    LP_max_runtime = conf.getint('params', 'LP_max_runtime')  # in minutes
    LP_max_k = conf.getint('params', 'LP_max_k')  # max. assumed k

    debug = conf.getboolean('params', 'debug')

    # get price series for us to use in this run
    pfile = open('price_data/APXReferencePriceDataUkPowerMarket2012_noweekends.csv', 'r')
    random.seed(seed)
    row = random.randint(1, 219)  # 219: number of days in data
    for _ in range(row):
        pfile.readline()
    line = pfile.readline().strip().split('\t')
    day = line[0]
    actual_prices = [float(p) / 300. for p in line[1:]]

    # get expected prices for the right month from pre-computed avg file
    exp_prices_in = open('price_data/APXReferencePriceDataUkPowerMarket2012_noweekends_avg.csv', 'r')
    exp_prices_in.readline()  # Title
    for line in exp_prices_in.readlines():
        line = line.strip().split('\t')
        if '-{}-'.format(line[0]) in day:  # we reached the correct month
            avg_price = float(line[1])
            exp_prices = [float(p) for p in line[2:]]
            break

    street = Street(T=T, N=N, C=C, Dmax=Dmax, Smax=Smax, pmax=pmax, pmin=pmin,
                    c_h=c_h, adaptive=adaptive, slope=econ_slope,
                    placement_optimistic=placement_optimistic)
    log.write('# w, ')
    for btype in battery_types:
        log.write('{}, '.format(btype.name))
    log.write('\n')
    for w in ws:
        line = '{}, '.format(w)
        for btype in battery_types:
            b = btype(capacity=B, efficiency=alpha, max_rate=max_rate,
                  street=street, exp_prices=exp_prices, avg_price=avg_price,
                  T=T, c_h=c_h)
            if btype in (OfflineBattery, DeterministicH2Battery):
                b.exp_prices = actual_prices
            if btype in (OfflineBattery, NonDeterministicOfflineBattery):
                b.max_runtime = LP_max_runtime
                b.max_k = LP_max_k
                b.solve_offline(w)
            accumulated_costs = 0
            for t in xrange(0, T):
                pt = actual_prices[t]
                bcharge = b.compute_charge(t, pt)
                if debug:
                    fp, fm = street.f(t, bcharge, pt)
                    print("[{}][{}] exp. price: {}, act. price:{}, fp:{}, fm:{}, magnitude before:{}, magnitude after:{}, b.level:{}, bcharge:{}".format(
                                t, b.name, round(exp_prices[t], 2),
                                round(pt, 2), round(fp, 2), round(fm, 2),
                                round(street.maxf(t, 0, pt), 2),
                                round(street.maxf(t, bcharge, pt), 2),
                                round(b.level, 2),
                                round(bcharge, 2)))
                revenue = b.execute_charge(bcharge, pt)
                cost = street.cost(t, bcharge, pt)
                accumulated_costs += w * cost - revenue
            # now sell the rest in the battery at an assumed worth of the
            # average price of that month
            if not btype is NoBattery:
                accumulated_costs -= b.level * avg_price
            b.level = 0
            line += '{},'.format(accumulated_costs)
            if debug:
                print "Acc. Costs: ", accumulated_costs
        log.write('{}\n'.format(line[:-1]))  # write line w/o last comma
    log.flush()
    log.close()


if __name__ == '__main__':
    if not len(sys.argv) in (2,4):
        print "Usage: ./main.py <conf-filename> [<log-filename> <seed-nr>]"
        sys.exit()
    conf = ConfigParser()
    conf.read(sys.argv[1])
    if len(sys.argv) == 4:
        log = open(sys.argv[2], 'w')
        seed = sys.argv[3]
    else:
        log = open(conf.get('control', 'logfile'), 'w')
        seed = conf.get('control', 'seed')
    main(conf, log, seed)
