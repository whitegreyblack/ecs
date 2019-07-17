# turn_system.py

from .system import System


class TurnSystem(System):
    def process(self):
        while True:
            entity = self.engine.entity
            takes_turn = self.engine.inputs.find(entity)
            if not takes_turn:
                self.engine.next_entity()
                continue
            if takes_turn.needs_input:
                if self.engine.requires_input:
                    return False
                command = self.engine.keypress
                self.engine.requires_input = True
            else:
                command = self.engine.ai_system.process(entity)
            turn_over = self.engine.command_system.process(entity, command)
            if takes_turn.needs_input:
                if not turn_over:
                    return True
                else:
                    self.engine.ai_system.update()
            self.engine.next_entity()
        return True
