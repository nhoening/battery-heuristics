#!/usr/bin/python
from __future__ import division

fin = open('APXReferencePriceDataUkPowerMarket2012_noweekends.csv', 'r')
fout = open('APXReferencePriceDataUkPowerMarket2012_noweekends_avg.csv', 'w')

# workdays per month
wdim = {'01-Jan': 22, '02-Feb': 21, '03-Mar': 22, '04-Apr': 21, '05-May': 23,
        '06-Jun': 21, '07-Jul': 22, '08-Aug': 23, '09-Sep': 20, '10-Oct': 23}

# copy title
title = fin.readline().strip().split('\t')
fout.write('{}\t'.format(title[0]))
fout.write('AvgOfMonth\t')
for i in xrange(1, len(title)):
    fout.write('{}\t'.format(title[i]))
fout.write('\n')

months = wdim.keys()
months.sort()

date_max_price = ''
max_price = 0
date_min_price = ''
min_price = 1

for m in months:
    print 'processing month: {} 2012'.format(m[3:])
    avgs = dict.fromkeys(xrange(1, 49), 0)
    for wd in range(wdim[m]):
        line = fin.readline()
        assert(m[3:] in line)
        prices = line.strip().split('\t')[1:]
        for h in xrange(1, 49):
            ph = float(prices[h - 1]) / 300.
            avgs[h] += ph
            if ph < min_price:
                min_price = ph
                date_min_price = '{}, hour {}'.format(
                        line.strip().split('\t')[0], h)
            if ph > max_price:
                max_price = ph
                date_max_price = '{}, hour {}'.format(
                        line.strip().split('\t')[0], h)
    for h in xrange(1, 49):
        avgs[h] /= wdim[m]

    fout.write('{}\t'.format(m[3:]))
    avg_of_month = sum([avgs[h] for h in range(1, 49)]) / 48.
    fout.write('{}\t'.format(round(avg_of_month, 4)))
    fout.write('\t'.join([str(round(avgs[h], 4)) for h in xrange(1, 49)]))
    fout.write('\n')

fin.close()
fout.close()

print "max. price: {} (on {})".format(max_price, date_max_price)
print "min. price: {} (on {})".format(min_price, date_min_price)
