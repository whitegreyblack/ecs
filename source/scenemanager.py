# scenemanager.py

from source.stack import Stack


class SceneManager(Stack):
    __slots__: list = ('items')
    def __init__(self, *items):
        for item in items:
            item.manager = self
        super().__init__(*items)
    def push(self, scene):
        scene.manager = self
        super().push(scene)
    def run(self, engine, terminal):
        while self.items:
            self.top.process(engine, terminal)
