# test_entity_manager.py

"""Testing entity manager methods"""

from pytest import raises

from source.ecs.managers import EntityManager


def test_entity_manager_next_id_with_manual_entity_id():
    e = 31
    em = EntityManager()
    em.add(e)
    assert e in em.entity_ids
    assert em.next_id == 0

def test_entity_manager_duplicate_manual_entity_id():
    e = 22
    em = EntityManager()
    em.add(e)

    with raises(ValueError):
        em.add(e)
