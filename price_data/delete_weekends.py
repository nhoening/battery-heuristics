#!/usr/bin/python 

'''
Take raw input from 2012 (Jan-Oct), and
- delete weekends
'''

first_dow = 7 # Jan , 2012 was a sunday

fin = open('APXReferencePriceDataUkPowerMarket2012.csv', 'r')
fout = open('APXReferencePriceDataUkPowerMarket2012_noweekends.csv', 'w')

# copy title
fout.write(fin.readline())

i = 0
for line in fin.readlines():
    if (i + first_dow) % 7 not in (0,6) :
        fout.write(line)
    i += 1

fin.close()
fout.close()
