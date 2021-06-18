# tests\join.py

# Timing test of different join methods using set/dict operations

""" Final Test as of 06/18/2021
0.000539 first_keys_intersection_update_op_rest_keys
0.000979 first_set_intersection_rest_set
0.000989 first_set_intersection_update_rest_dict
0.001095 first_set_intersection_update_op_rest_keys
0.001227 first_keys_intersection_update_op_rest_set
0.001283 first_keys_set_intersection_update_dict
0.001589 first_set_intersection_update_rest_set
0.001644 first_set_intersection_update_op_rest_set
0.001644 set_intersection_update_on_mapped_manager_keys_set
0.001645 first_set_intersection_generate_rest_set
0.001659 reduce_intersection_all_set
0.001669 set_intersection_on_all_mapped_manager_keys_dict
0.001685 first_set_intersection_mapped_rest_set
0.001693 set_intersection_update_on_local_mapped_manager_keys_set
0.001805 set_intersection_update_on_first_manager_keys_dict
0.001843 first_keys_set_intersection_rest_keys_set
0.002161 set_intersection_on_all_mapped_manager_keys_iter_dict
0.002298 set_intersection_update_on_first_manager_keys_set
"""

from functools import reduce
from source.contextmanagers import Timer

DATASETS = [
    {i: i for i in range(20000)},
    {i: i for i in range(5000, 15000)},  # reduces to 10000
    {i: i for i in range(4000, 12000, 2)},  # reduces to 4000 (8000 / 2)
    {i: i for i in range(6000, 8000, 5)},
]


def first_keys_set_intersection_rest_keys_set(first, *rest):
    keys = set(first.keys())
    for d in rest:
        keys = keys.intersection(d.keys())
    return len(keys)


def set_intersection_update_on_first_manager_keys_set(first, *rest):
    keys = set(first.keys())
    for d in rest:
        keys.intersection_update(set(d.keys()))
    return len(keys)


def reduce_intersection_all_set(*ds):
    return len(reduce(set.intersection, map(set, ds)))


def set_intersection_update_on_first_manager_keys_dict(first, *rest):
    keys = set(first.keys())
    for d in rest:
        keys.intersection_update(d.keys())
    return len(keys)


def first_keys_set_intersection_update_dict(first, *rest):
    keys = set(first.keys())
    for d in rest:
        keys.intersection_update(d)
    return len(keys)


def set_intersection_on_all_mapped_manager_keys_iter_dict(*ds):
    return len(set.intersection(*map(set, (d.keys() for d in ds))))


def set_intersection_on_all_mapped_manager_keys_dict(*ds):
    return len(set.intersection(*map(set, ds)))


def first_set_intersection_update_op_rest_set(first, *rest):
    keys = set(first)
    for d in rest:
        keys &= set(d)
    return len(keys)


def first_set_intersection_update_op_rest_keys(first, *rest):
    keys = set(first)
    for d in rest:
        keys &= d.keys()
    return len(keys)


def first_keys_intersection_update_op_rest_keys(first, *rest):
    keys = first.keys()
    for d in rest:
        keys &= d.keys()
    return len(keys)


def first_keys_intersection_update_op_rest_set(first, *rest):
    keys = first.keys()
    for d in rest:
        keys &= set(d)
    return len(keys)


def set_intersection_update_on_mapped_manager_keys_set(first, *rest):
    keys = set(first)
    keys.intersection_update(*map(set, rest))
    return len(keys)


def set_intersection_update_on_local_mapped_manager_keys_set(*ds, m=map):
    first, *rest = ds
    keys = set(first)
    keys.intersection_update(*m(set, rest))
    return len(keys)


def first_set_intersection_mapped_rest_set(first, *rest):
    return len(set(first).intersection(*map(set, rest)))


def first_set_intersection_generate_rest_set(first, *rest):
    return len(set(first).intersection(*(set(d) for d in rest)))


def first_set_intersection_rest_set(first, *rest):
    keys = set(first)
    for d in rest:
        keys = keys.intersection(d)
    return len(keys)


def first_set_intersection_update_rest_set(first, *rest):
    keys = set(first)
    for d in rest:
        keys.intersection_update(set(d))
    return len(keys)


def first_set_intersection_update_rest_dict(first, *rest):
    keys = set(first)
    for d in rest:
        keys.intersection_update(d)
    return len(keys)


DIFF = first_keys_intersection_update_op_rest_keys(*DATASETS)
JOINS = (
    first_keys_set_intersection_rest_keys_set,
    set_intersection_update_on_first_manager_keys_dict,
    set_intersection_update_on_first_manager_keys_set,
    reduce_intersection_all_set,
    set_intersection_on_all_mapped_manager_keys_iter_dict,
    set_intersection_on_all_mapped_manager_keys_dict,
    set_intersection_update_on_mapped_manager_keys_set,
    set_intersection_update_on_local_mapped_manager_keys_set,
    first_set_intersection_mapped_rest_set,
    first_set_intersection_update_op_rest_keys,
    first_set_intersection_update_op_rest_set,
    first_keys_intersection_update_op_rest_keys,
    first_keys_intersection_update_op_rest_set,
    first_set_intersection_rest_set,
    first_set_intersection_update_rest_set,
    first_set_intersection_update_rest_dict,
    first_set_intersection_generate_rest_set,
    first_keys_set_intersection_update_dict,
)


def time_joins(joins, *datasets):
    num_times = 50
    timings = {j.__name__: None for j in JOINS}
    for join in JOINS:
        times, counts = [], []
        for _ in range(num_times):
            with Timer() as timer:
                join(*datasets)
            times.append(timer.secs)
        timings[join.__name__] = sum(times) / num_times
    return sorted(timings.items(), key=lambda x: x[1])


if __name__ == "__main__":
    for j, t in time_joins(JOINS, *DATASETS):
        print(f"{t:.6f} {j}")
