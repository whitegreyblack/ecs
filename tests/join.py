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

def join1(*ds):
    start = time.time()
    first, *rest = ds
    keys = set(first.keys())
    for d in rest:
        keys = keys.intersection(d.keys())
    end = time.time() - start
    return end, len(keys)

def join2(*ds):
    start = time.time()
    first, *rest = ds
    keys = set(first.keys())
    for d in rest:
        keys.intersection_update(set(d.keys()))
    end = time.time() - start
    return end, len(keys)

def join3(*ds):
    start = time.time()
    keys = reduce(set.intersection, map(set, ds))
    end = time.time() - start
    return end, len(keys)

def join4(*ds):
    start = time.time()
    first, *rest = ds
    keys = set(first.keys())
    for d in rest:
        keys.intersection_update(d.keys())
    end = time.time() - start
    return end, len(keys)

def join5(*ds):
    start = time.time()
    for d in ds:
        keys = set.intersection(*map(set, (d for d in ds)))
    end = time.time() - start
    return end, len(keys)

def join6(*ds):
    start = time.time()
    keys = set.intersection(*map(set, ds))
    end = time.time() - start
    return end, len(keys)

def join7(*ds):
    start = time.time()
    first, *rest = ds
    keys = set(first)
    for r in rest:
        keys &= set(r)
    end = time.time() - start
    return end, len(keys)

def join8(*ds):
    start = time.time()
    first, *rest = ds
    keys = set(first)
    keys.intersection_update(*map(set, rest))
    end = time.time() - start
    return end, len(keys)

def join9(*ds, m=map):
    start = time.time()
    first, *rest = ds
    keys = set(first)
    keys.intersection_update(*m(set, rest))
    end = time.time() - start
    return end, len(keys)

def join10(*ds):
    start = time.time()
    first, *rest = ds
    keys = set(first).intersection(*map(set, rest))
    end = time.time() - start
    return end, len(keys)

if __name__ == "__main__":
    # print(len(a), len(b), len(c))

    joins = (
        join1, 
        join2, 
        join3, 
        join4, 
        join5, 
        join6, 
        join7, 
        join8, 
        join9, 
        join10
    )
    r = len(joins)
    counter = {i+1: 0 for i in range(r)}
    iterations = 5
    for iteration in range(iterations):
        n = 50
        timings = {i+1: None for i in range(r)}
        countings = {i+1: None for i in range(r)}
        for i, join in enumerate(joins):
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

""" Testing new joins
    # join without key
    start = time.time()
    tiles = [
        (v, p)
            for v, p in join_without_key(
                engine.visibilities,
                engine.positions
            )
            if p.map_id == engine.world.id
    ]
    s = time.time() - start
    # join
    start = time.time()
    tiles = [
        (v, p)
            for _, (v, p) in join(
                engine.visibilities,
                engine.positions
            )
            if p.map_id == engine.world.id
    ]
    t = time.time() - start
    # join conditional
    start = time.time()
    tiles = [
        (v, p)
            for _, (v, p) in join_conditional(
                engine.visibilities,
                engine.positions,
                conditions=((1, lambda x: x.map_id == engine.world.id),)
            )
    ]
    cond = time.time() - start
    # join conditional without key
    start = time.time()
    tiles = [
        (v, p)
            for v, p in join_conditional_without_key(
                engine.visibilities,
                engine.positions,
                conditions=((1, lambda x: x.map_id == engine.world.id),)
            )
    ]
    cond2 = time.time() - start
    # join conditional without key as list
    start = time.time()
    tiles = list(join_conditional_without_key(
                engine.visibilities,
                engine.positions,
                conditions=((1, lambda x: x.map_id == engine.world.id),)
            ))
    cond3 = time.time() - start
    print(s, t, cond, cond2, cond3)
    :: Results ::
    r | time
    --+---------------------
    s | 0.037843179702758786
    t | 0.038519787788391116
    1 | 0.040766637665884835
    2 | 0.040930165563310895
    3 | 0.041590700830732075
"""