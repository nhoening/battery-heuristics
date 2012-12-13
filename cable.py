from pymprog import *  # Import the module
# index and data



#c = (10.0, 6.0, 4.0)
#mat = [ (1.0, 1.0, 1.0),     
#        (10.0, 4.0, 5.0),   
#        (2.0, 2.0, 6.0)]   
#b = (100.0, 600.0, 300.0)
#problem definition
beginModel('basic')  
verbose(True)

b0 = 10
Bp = 8
Bm = 8
B = 20
CC = 50
w = 0.1
alpha = 0.8
fm = (-20, -40, -10)
fp = (10, 55, 20)
p = (0.5, 1, 0.5)
tid = range(3) #T

# create variables
c = var(tid, 'C')
d = var(tid, 'D')
z = var(tid, 'Z')

minimize( #set objective
    sum(z[i] for i in tid) - w * sum(p[i] * (d[i]-c[i]) for i in tid), 'myobj'
)

#set constraints
st(c[i] <= Bp for i in tid)
st(c[i] >= 0  for i in tid)
st(d[i] <= Bm for i in tid)
st(d[i] >= 0  for i in tid)
for i in tid:
    st(b0 + sum(alpha * c[j] - d[j] for j in range(i+1)) <= B)
    st(b0 + sum(alpha * c[j] - d[j] for j in range(i+1)) >= 0)
st(z[i] >= 0 for i in tid)
st(z[i] >=  fp[i] + c[i] - d[i] - CC for i in tid)
st(z[i] >= -fm[i] - c[i] + d[i] - CC for i in tid)

#print r


solve() #solve and report
print "Solver status:", status()
print 'Objective = %g;' % vobj()  # print obj value
#Print variable names and primal values
print ';\n'.join('%s = %g' % (
   c[i].name, c[i].primal) 
                    for i in tid)
print ';\n'.join('%s = %g' % (
   d[i].name, d[i].primal) 
                    for i in tid)
print ';\n'.join('%s = %g' % (
   z[i].name, z[i].primal) 
                    for i in tid)


'''
print ';\n'.join('%s = %g {dual: %g}' % (
   x[i].name, x[i].primal, x[i].dual) 
                    for i in xid)
print ';\n'.join('%s = %g {dual: %g}' % (
   r[i].name, r[i].primal, r[i].dual) 
                    for i in rid)
'''
'''
print ';\n'.join('%s = %g {dual: %g}' % (
   c[i].name, c[i].primal, c[i].dual) 
                    for i in tid)
print ';\n'.join('%s = %g {dual: %g}' % (
   d[i].name, d[i].primal, d[i].dual) 
                    for i in tid)
print ';\n'.join('%s = %g {dual: %g}' % (
   z[i].name, z[i].primal, z[i].dual) 
                    for i in tid)

# Since version 0.3.0
print reportKKT()
print "Environment:", env
for pn in dir(env):
    if pn[:2]=='__'==pn[-2:]: continue
    print pn, getattr(env, pn)
# Since version 0.4.2
print evaluate(sum(x[i]*(i+x[i])**2 for i in xid))
print sum(x[i].primal*(i+x[i].primal)**2 for i in xid)
endModel() #Good habit: do away with the problem
'''
