# energy_system

from .system import System


class EnergySystem(System):
    def process(self):
        for eid, energy in self.engine.energies:
            energy.amount += energy.gain
            if energy.amount >= energy.full:
                energy.ready = True
    def update(self, entity):
        energy = self.engine.energies(entity)
        turns = 0
        while energy.amount >= energy.full:
            energy.amount -= energy.full
            turns += 1
        return turns
