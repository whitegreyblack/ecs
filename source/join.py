# source\join.py

from functools import reduce


def first_keys_set_intersection_rest_keys_set(first, *rest):
    keys = set(first.keys())
    for d in rest:
        keys = keys.intersection(d.keys())
    return keys


def set_intersection_update_on_first_manager_keys_set(first, *rest):
    keys = set(first.keys())
    for d in rest:
        keys.intersection_update(set(d.keys()))
    return keys


def reduce_intersection_all_set(*ds):
    return reduce(set.intersection, map(set, ds))


def set_intersection_update_on_first_manager_keys_dict(first, *rest):
    keys = set(first.keys())
    for d in rest:
        keys.intersection_update(d.keys())
    return keys


def first_keys_set_intersection_update_dict(first, *rest):
    keys = set(first.keys())
    for d in rest:
        keys.intersection_update(d)
    return keys


def set_intersection_on_all_mapped_manager_keys_iter_dict(*ds):
    return set.intersection(*map(set, (d.keys() for d in ds)))


def set_intersection_on_all_mapped_manager_keys_dict(*ds):
    return set.intersection(*map(set, ds))


def first_set_intersection_update_op_rest_set(first, *rest):
    keys = set(first)
    for d in rest:
        keys &= set(d)
    return keys


def first_set_intersection_update_op_rest_keys(first, *rest):
    keys = set(first)
    for d in rest:
        keys &= d.keys()
    return keys


def first_keys_intersection_update_op_rest_keys(first, *rest):
    keys = first.keys()
    for d in rest:
        keys &= d.keys()
    return keys


def first_keys_intersection_update_op_rest_set(first, *rest):
    keys = first.keys()
    for d in rest:
        keys &= set(d)
    return keys


def set_intersection_update_on_mapped_manager_keys_set(first, *rest):
    keys = set(first)
    keys.intersection_update(*map(set, rest))
    return keys


def set_intersection_update_on_local_mapped_manager_keys_set(*ds, m=map):
    first, *rest = ds
    keys = set(first)
    keys.intersection_update(*m(set, rest))
    return keys


def first_set_intersection_mapped_rest_set(first, *rest):
    return set(first).intersection(*map(set, rest))


def first_set_intersection_generate_rest_set(first, *rest):
    return set(first).intersection(*(set(d) for d in rest))


def first_set_intersection_rest_set(first, *rest):
    keys = set(first)
    for d in rest:
        keys = keys.intersection(d)
    return keys


def first_set_intersection_update_rest_set(first, *rest):
    keys = set(first)
    for d in rest:
        keys.intersection_update(set(d))
    return keys


def first_set_intersection_update_rest_dict(first, *rest):
    keys = set(first)
    for d in rest:
        keys.intersection_update(d)
    return keys


# group all of join functions into one global variable to be used elsewhere
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

j = first_keys_intersection_update_op_rest_keys


def join(*managers):
    if len(managers) == 1:
        return managers.items()
    for e in j(*managers):
        yield e, (m[e] for m in managers)


def join_drop_key(*managers):
    if len(managers) == 1:
        return managers.items()
    for e in j(*managers):
        yield (m[e] for m in managers)


if __name__ == "__main__":
    a, b, c = {1: 0}, {1: 0, 2: 0}, {1: 0, 3: 0}
    for e, _ in join(a, b, c):
        print(e)
