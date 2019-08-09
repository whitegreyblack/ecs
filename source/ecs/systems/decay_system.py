# decay_system

from source.common import join

from .system import System


class DecaySystem(System):
    def process(self):
        print(self.engine.decays.components);
        items = join(
            self.engine.items,
            self.engine.decays
        )
        remove = set()
        for eid, (_, decay) in items:
            decay.lifetime -= 1
            if decay.lifetime < 1:
                remove.add(eid)
            
        for eid in remove:
            entity = self.engine.entities.find(eid)
            info = self.engine.infos.find(entity)
            self.engine.logger.add(f"{info.name} decays")
            self.engine.grave_system.process(entity)
