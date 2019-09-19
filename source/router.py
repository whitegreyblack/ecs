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
                controller.router_name: controller(self.engine)
                    for controller in controllers
            }

    def add_controller(self, name, controller):
        self.controllers[name] = controller

    def remove_controller(self, name):
        del self.controllers[name]

    def route(self, name, action, *args):
        return getattr(self.controllers[name], action)(*args)


# Using this to control messaging between systems
# >>> router.add_event_map(type(move_event), move_sys, move)
# >>> router.route(move_event)
class EventRouter:
    def __init__(self, engine):
        self.engine = engine
        self.event_map = dict()
    
    def add_event_map(self, event_map):
        self.event_map = event_map

    def map_event(self, event, system_name, func_name):
        """
            Adds one to many mapping of event to systems.
            Note: Maybe needs priority queue
        """
        if event not in self.event_map:
            self.event_map[event] = []
        self.event_map[event].append((system_name, func_name))

    def fire(self, event):
        systems = self.event_map.get(type(event), None)
        if not systems:
            raise Exception(f"No function mapping for {type(event)} {event}.")
        for system_name, func_name in systems:
            # get the system
            system = getattr(self.engine, system)
            # get the method name
            func = getattr(system, func_name)
            # fire event
            func(event)
