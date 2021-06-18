# demos\join.py

# Memory usage test of different join methods using set/dict operations

import tracemalloc
from tests.join import DATASETS

""" Final Tests as of 06/18/2021
join_with_return
Total allocated size: 0.0 KiB
join_with_yield
D:\projects\ecs\demos\join.py:107: size=456 B, count=1, average=456 B
Total allocated size: 1.1 KiB
join_with_yield_list
D:\projects\ecs\demos\join.py:107: size=904 B, count=2, average=452 B
Total allocated size: 6.6 KiB
"""

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
    keys = set(first)
    for d in rest:
        keys.intersection_update(d)
    return keys


def join_with_yield(first, *rest):
    keys = set(first)
    for d in rest:
        keys.intersection_update(d)
    for k in keys:
        yield k


def join_with_yield_list(first, *rest):
    keys = set(first)
    for d in rest:
        keys.intersection_update(d)
    yield list(keys)


def memory_usage(join):
    tracemalloc.start()
    print(join.__name__)
    join(*DATASETS)
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics("traceback")
    for stat in top_stats[:5]:
        if "join.py" in str(stat):
            print(stat)
    total = sum(stat.size for stat in top_stats)
    print("Total allocated size: %.1f KiB" % (total / 1024))


if __name__ == "__main__":
    for join in (join_with_return, join_with_yield, join_with_yield_list):
        memory_usage(join)

"""
def test(engine):
    start = time.time()
    g = engine.tiles.join(engine.positions, engine.renders)
    for entity_id, components in g:
        pass
    t1 = time.time() - start

    start = time.time()
    g = engine.positions.join(engine.tiles, engine.renders)
    for entity_id, components in g:
        pass
    t2 = time.time() - start

    start = time.time()
    g = engine.renders.join(engine.tiles, engine.positions)
    for entity_id, components in g:
        pass
    t3 = time.time() - start

    start = time.time()
    g = join(engine.positions, engine.tiles, engine.renders)
    for entity_id, components in g:
        pass
    t4 = time.time() - start

    return t1, t2, t3, t4

def test_loop(engine):
    t1s, t2s, t3s, t4s = [], [], [], []
    for _ in range(1000):
        t1, t2, t3, t4 = test(engine)
        t1s.append(t1)
        t2s.append(t2)
        t3s.append(t3)
        t4s.append(t4)
    print(sum(t1s) / len(t1s))
    print(sum(t2s) / len(t2s))
    print(sum(t3s) / len(t3s))
    print(sum(t4s) / len(t4s))
"""
