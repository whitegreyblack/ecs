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
