# tests\join.py

"""
def join(*ds):
    # at least two needed else yields dict items
    if len(ds) == 1:
        yield ds.components.items()
    first, *rest = ds
    keys = set(first.components.keys())
    for manager in rest:
        keys = keys.intersection(set(manager.components.keys()))
    for eid in keys:
        yield eid, (m.components[eid] for m in ds)
"""

import time
from functools import reduce

# def test(engine):
#     start = time.time()
#     g = engine.tiles.join(engine.positions, engine.renders)
#     for entity_id, components in g:
#         pass
#     t1 = time.time() - start

#     start = time.time()
#     g = engine.positions.join(engine.tiles, engine.renders)
#     for entity_id, components in g:
#         pass
#     t2 = time.time() - start

#     start = time.time()
#     g = engine.renders.join(engine.tiles, engine.positions)
#     for entity_id, components in g:
#         pass
#     t3 = time.time() - start

#     start = time.time()
#     g = join(engine.positions, engine.tiles, engine.renders)
#     for entity_id, components in g:
#         pass
#     t4 = time.time() - start

#     return t1, t2, t3, t4

# def test_loop(engine):
#     t1s, t2s, t3s, t4s = [], [], [], []
#     for _ in range(1000):
#         t1, t2, t3, t4 = test(engine)
#         t1s.append(t1)
#         t2s.append(t2)
#         t3s.append(t3)
#         t4s.append(t4)
#     print(sum(t1s) / len(t1s))
#     print(sum(t2s) / len(t2s))
#     print(sum(t3s) / len(t3s))
#     print(sum(t4s) / len(t4s))

a = {i:i for i in range(20000)}
b = {i:i for i in range(5000, 15000)}     # reduces to 10000
c = {i:i for i in range(4000, 12000, 2)}  # reduces to 4000 (8000 / 2)
diff = set(a) & set(b) & set(c)

def joiner1(*ds):
    start = time.time()
    first, *rest = ds
    keys = set(first.keys())
    for d in rest:
        keys = keys.intersection(d.keys())
    end = time.time() - start
    return end, len(keys)

def joiner2(*ds):
    start = time.time()
    first, *rest = ds
    keys = set(first.keys())
    for d in rest:
        keys.intersection_update(set(d.keys()))
    end = time.time() - start
    return end, len(keys)

def joiner3(*ds):
    start = time.time()
    keys = reduce(set.intersection, map(set, ds))
    end = time.time() - start
    return end, len(keys)

def joiner4(*ds):
    start = time.time()
    first, *rest = ds
    keys = set(first.keys())
    for d in rest:
        keys.intersection_update(d.keys())
    end = time.time() - start
    return end, len(keys)

def joiner5(*ds):
    start = time.time()
    for d in ds:
        keys = set.intersection(*map(set, (d for d in ds)))
    end = time.time() - start
    return end, len(keys)

def joiner6(*ds):
    start = time.time()
    keys = set.intersection(*map(set, ds))
    end = time.time() - start
    return end, len(keys)

def joiner7(*ds):
    start = time.time()
    first, *rest = ds
    keys = set(first)
    for r in rest:
        keys &= set(r)
    end = time.time() - start
    return end, len(keys)

def joiner8(*ds):
    start = time.time()
    first, *rest = ds
    keys = set(first)
    keys.intersection_update(*map(set, rest))
    end = time.time() - start
    return end, len(keys)

def joiner9(*ds, m=map):
    start = time.time()
    first, *rest = ds
    keys = set(first)
    keys.intersection_update(*m(set, rest))
    end = time.time() - start
    return end, len(keys)

def joiner10(*ds):
    start = time.time()
    first, *rest = ds
    keys = set(first).intersection(*map(set, rest))
    end = time.time() - start
    return end, len(keys)

if __name__ == "__main__":
    # print(len(a), len(b), len(c))

    joiners = (joiner1, joiner2, joiner3, joiner4, joiner5, joiner6, joiner7, joiner8, joiner9, joiner10)
    r = len(joiners)
    counter = {i+1: 0 for i in range(r)}
    iterations = 5
    for iteration in range(iterations):
        n = 50
        timings = {i+1: None for i in range(r)}
        countings = {i+1: None for i in range(r)}
        for i, join in enumerate(joiners):
            times = []
            counts = []
            for _ in range(n):
                a = {i:i for i in range(20000)}
                b = {i:i for i in range(5000, 15000)}     # reduces to 10000
                c = {i:i for i in range(4000, 12000, 2)}  # reduces to 4000 (8000 / 2)
                timing, count = join(a, b, c)
                while not count:
                    a = {i:i for i in range(20000)}
                    b = {i:i for i in range(5000, 15000)}     # reduces to 10000
                    c = {i:i for i in range(4000, 12000, 2)}  # reduces to 4000 (8000 / 2)
                    timing, count = join(a, b, c)
                times.append(timing)
                counts.append(count)
            timings[i+1] = sum(times) / n
            countings[i+1] = int(sum(counts) / n)
        l = sorted(timings.items(), key=lambda x: x[1])
        for place, (i, timer) in enumerate(l):
            counter[i] += place+1
            print(i, timer, countings[i])
        print()
    c = sorted(counter.items(), key=lambda x: x[1])
    print(c)
