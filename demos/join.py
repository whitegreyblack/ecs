# tests\join.py

import time
import tracemalloc
from functools import reduce


class Manager:
    def __init__(self, components):
        self.components = components
    def __iter__(self):
        return iter(self.components.items())

# pre build sets for reading
a = Manager({i:i for i in range(200000)})
b = Manager({i:i for i in range(3000, 180000)})
c = Manager({i:i for i in range(4000, 120000, 2)})
diff = set(a.components) & set(b.components) & set(c.components) # 3500 elements
print(len(diff))

def clock(fn, *args):
    start = time.time()
    keys = fn(*args)
    end = time.time() - start
    return end, len(keys)

def join1(first, *rest):
    keys = set(first.components)
    for d in rest:
        keys = keys.intersection(d.components)
    return keys

def join2(first, *rest):
    keys = set(first.components.keys())
    for d in rest:
        keys = keys.intersection(d.components.keys())
    return keys

def join3(first, *rest):
    keys = set(first.components)
    for d in rest:
        keys.intersection_update(set(d.components))
    return keys

def join4(first, *rest):
    keys = set(first.components)
    for d in rest:
        keys.intersection_update(d.components)
    return keys

def join5(*ds):
    return reduce(set.intersection, map(set, (d.components for d in ds)))

def join6(*ds):
    return set.intersection(*map(set, (d.components for d in ds)))

def join7(first, *rest):
    keys = set(first.components)
    for r in rest:
        keys &= set(r.components)
    return keys

def join8(first, *rest):
    keys = set(first.components)
    keys.intersection_update(*map(set, (d.components for d in rest)))
    return keys

# map as local function
def join9(first, *rest, m=map):
    keys = set(first.components)
    keys.intersection_update(*m(set, (d.components for d in rest)))
    return keys
    
def join10(first, *rest):
    return set(first.components).intersection(*map(set, (d.components for d in rest)))

def join11(first, *rest):
    return set(first.components).intersection(*map(set, (d.components for d in rest)))

def join12(first, *rest):
    return set(first.components).intersection(*(set(d.components) for d in rest))

def join_timings():
    """Compare timings for different join functions"""
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
        join10,
        join11,
        join12,
    )
    r = len(joins)
    avgs = {i+1: 0 for i in range(r)}
    counter = {i+1: 0 for i in range(r)}
    iterations = 10
    runs = 10
    for iteration in range(iterations):
        timings = {i+1: None for i in range(r)}
        for i, join in enumerate(joins):
            times = []
            for _ in range(runs):
                timing, count = clock(join, a, b, c)
                while not count:
                    timing, count = clock(join, a, b, c)
                assert count == len(diff)
                times.append(timing)
            timings[i+1] = sum(times) / runs
        l = sorted(timings.items(), key=lambda x: x[1]) # sort by timings
        for place, (i, timer) in enumerate(l):
            avgs[i] += timer
            counter[i] += place + 1
    rows = '\n'.join(
        f"| {i:>6} | {p:>9} | {avgs[i]/iterations:.06f} |"
            for i, p in sorted(counter.items(), key=lambda x: x[1])
    )
    print(f"""
(from best to worst)
+--------+-----------+----------+
| join # | placement | avg time |
+--------+-----------+----------+
{rows}
+--------+-----------+----------+"""[1:]
    )

""" `Testing new joins with engine syntax`
# join without key
start = time.time()
tiles = [
    (v, p)
        for v, p in join_drop_key(
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

def join_with_return(first, *rest):
    keys = set(first.components)
    for d in rest:
        keys.intersection_update(d.components)
    return keys

def join_with_yield(first, *rest):
    keys = set(first.components)
    for d in rest:
        keys.intersection_update(d.components)
    for k in keys:
        yield k

def join_with_yield_list(first, *rest):
    keys = set(first.components)
    for d in rest:
        keys.intersection_update(d.components)
    yield list(keys)

def memory_usage(join):
    tracemalloc.start()
    print(join)
    x = join(a, b, c)
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('traceback')
    for stat in top_stats:
        print(stat)
    total = sum(stat.size for stat in top_stats)
    print("Total allocated size: %.1f KiB" % (total / 1024))

if __name__ == "__main__":
    # join_timings()
    # # Total allocated size: 1024.8 KiB
    # memory_usage(join_with_return)
    # # Total allocated size: 0.8 KiB
    # memory_usage(join_with_yield)
    # # Total allocated size: 0.8 KiB
    # memory_usage(join_with_yield_list)
    for join in (join_with_return, join_with_yield, join_with_yield_list):
        memory_usage(join)
