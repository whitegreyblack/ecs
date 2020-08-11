# tests/inventory_controller.py

"""
    Tests inventory controller functions

    Usage: py -m pytest tests\controllers\inventory_controller.py
"""

import pytest

from source.controllers import InventoryController
from source.ecs.components import Inventory, Item
from source.ecs.managers import EntityManager
from source.engine import Engine


@pytest.fixture(scope='function')
def setup():
    e = Engine(
        components=(Inventory, Item),
        systems=None,
        controllers=(InventoryController,)
    )
    return e

def test_check_engine(setup):
    engine = setup
    assert isinstance(engine, Engine)

def test_sort_order_after_add_item(setup):
    engine = setup
    entity = engine.entities.create()
    # create items
    food = engine.entities.create()
    engine.items.add(food, Item('food'))
    sword = engine.entities.create()
    engine.items.add(sword, Item('weapon'))
    # create inventory
    inventory = Inventory()
    engine.inventories.add(entity, inventory)
    # use controller to add items
    engine.inventory_controller.add_item(entity, food)
    engine.inventory_controller.add_item(entity, sword)
    # test
    assert engine.inventories.find(entity).items == [sword, food]

print("Usage: py -m pytest tests\controllers\inventory_controller.py")
