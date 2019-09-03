# router.py

"""Handles controller action calling and rerouting"""


class Router:
    def __init__(self, engine, controllers):
        self.engine = engine
        self.init_controllers(controllers)

    def init_controllers(self, controllers):
        if not controllers:
            self.controllers = dict()
        else:
            self.controllers = {
                name: controller(self.engine)
                    for name, controller in controllers
            }

    def add_controller(self, name, controller):
        self.controllers[name] = controller

    def remove_controller(self, name):
        del self.controllers[name]

    def route(self, name, action, *args):
        return getattr(self.controllers[name], action)(*args)
