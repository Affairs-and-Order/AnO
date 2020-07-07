# stats to be used in all tests:
"""
- let n = number of units
- let v = very slight random advantage/disadvantage (0.5/1.5)
- let m = morale between 1 - 100 (inclusive)
- let t = tech score - between 1 - 30
- let e = effectiveness - between 0-2
"""
n1 = 50
v1 = 1
m1 = 50
t1 = 20
e1 = 1

n2 = 50
v2 = 1
m2 = 50
t2 = 20
e2 = 1.1

x = lambda n, m, v, t, e : (n+v) * ((t*e)/10 + m)

print("Group 1: {}".format(int(x(n1, v1, m1, t1, e1))))
print("Group 2: {}".format(int(x(n2, v2, m2, t2, e2))))
# lets keep this file, for future testing, although you might want to rename it to something other than test.py