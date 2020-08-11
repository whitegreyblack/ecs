# decay_system

from source.common import join

from .system import System


class DecaySystem(System):
    def process(self):
        remove = set()
        for eid, (_, decay) in join(self.engine.items, self.engine.decays):
            decay.lifetime -= 1
            if decay.lifetime < 1:
                remove.add(eid)
        
        for entity in remove:
            info = self.engine.infos.find(entity)
            self.engine.logger.add(f"{info.name} decays")
            self.engine.grave_system.process(entity)
