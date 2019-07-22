# test_entity_manager.py

"""Testing entity manager methods"""

from pytest import raises

from source.ecs.managers import EntityManager


def test_entity_manager_next_id_with_manual_entity_id():
    em = EntityManager()
    e = em.create(31)

    assert e.id == 31
    assert em.next_id == 32

def test_entity_manager_duplicate_manual_entity_id():
    em = EntityManager()
    e = em.create(22)

    with raises(ValueError):
        f = em.create(22)
