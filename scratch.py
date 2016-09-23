import itertools
import operator as op

d = {
	0: [('b', 0), ('a', 1)], 
	1: [('a', 1)], 
	3: [('a', 1), ('b', 0)]
}

l = [({1}, [('a', 3), ('b', 1)]),
 ({3, 4}, [('b', 1)]),
 ({0}, [('a', 0)]),
 ({2}, [('a', 3), ('b', 1)])]

print(sorted(l, key=lambda x: 0 not in x[0]))

for k in d:
	d[k].sort()

itemlist = sorted(d.items(), key=op.itemgetter(1))
# print(itemlist)

# for k, g in itertools.groupby(itemlist, key=op.itemgetter(1)):
# 	print((state, list(g)))

new_groups = [{state for state, _ in g} for _, g in itertools.groupby(itemlist, key=op.itemgetter(1))]
# for k, g in :
# 	print()
# print(new_groups)

def f(a, b, c):
	print(a, b, c)

f('a', *['b', 'c'])