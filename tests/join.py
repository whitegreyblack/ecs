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


from source.contextmanagers import Timer
from source.join import JOINS
from source.join import first_keys_intersection_update_op_rest_keys as join

DATASETS = [
    {i: i for i in range(20000)},
    {i: i for i in range(5000, 15000)},
    {i: i for i in range(4000, 12000, 2)},
    {i: i for i in range(6000, 8000, 5)},
]
DIFF = len(join(*DATASETS))


def time_joins(joins, *datasets):
    num_times = 50
    timings = {j.__name__: None for j in joins}
    for join in joins:
        times = []
        for _ in range(num_times):
            with Timer() as timer:
                join(*datasets)
            times.append(timer.secs)
        timings[join.__name__] = sum(times) / num_times
    return sorted(timings.items(), key=lambda x: x[1])


if __name__ == "__main__":
    for j, t in time_joins(JOINS, *DATASETS):
        print(f"{t:.6f} {j}")
