# ecs.py

import sys, os, random, keyboard, array, time

MAP_WIDTH = 20 # 80
MAP_HEIGHT = 6 # 25
DUNGEON = f"""
###########################
#............#......#.....#
#............#............#
######..######......#.....#
#.......#....#####.########
#.......#.................#
#............#........#...#
###########################"""[1:]

sintable = array.array('f', [
    0.00000, 0.01745, 0.03490, 0.05234, 0.06976, 0.08716, 0.10453,
    0.12187, 0.13917, 0.15643, 0.17365, 0.19081, 0.20791, 0.22495, 0.24192,
    0.25882, 0.27564, 0.29237, 0.30902, 0.32557, 0.34202, 0.35837, 0.37461,
    0.39073, 0.40674, 0.42262, 0.43837, 0.45399, 0.46947, 0.48481, 0.50000,
    0.51504, 0.52992, 0.54464, 0.55919, 0.57358, 0.58779, 0.60182, 0.61566,
    0.62932, 0.64279, 0.65606, 0.66913, 0.68200, 0.69466, 0.70711, 0.71934,
    0.73135, 0.74314, 0.75471, 0.76604, 0.77715, 0.78801, 0.79864, 0.80902,
    0.81915, 0.82904, 0.83867, 0.84805, 0.85717, 0.86603, 0.87462, 0.88295,
    0.89101, 0.89879, 0.90631, 0.91355, 0.92050, 0.92718, 0.93358, 0.93969,
    0.94552, 0.95106, 0.95630, 0.96126, 0.96593, 0.97030, 0.97437, 0.97815,
    0.98163, 0.98481, 0.98769, 0.99027, 0.99255, 0.99452, 0.99619, 0.99756,
    0.99863, 0.99939, 0.99985, 1.00000, 0.99985, 0.99939, 0.99863, 0.99756,
    0.99619, 0.99452, 0.99255, 0.99027, 0.98769, 0.98481, 0.98163, 0.97815,
    0.97437, 0.97030, 0.96593, 0.96126, 0.95630, 0.95106, 0.94552, 0.93969,
    0.93358, 0.92718, 0.92050, 0.91355, 0.90631, 0.89879, 0.89101, 0.88295,
    0.87462, 0.86603, 0.85717, 0.84805, 0.83867, 0.82904, 0.81915, 0.80902,
    0.79864, 0.78801, 0.77715, 0.76604, 0.75471, 0.74314, 0.73135, 0.71934,
    0.70711, 0.69466, 0.68200, 0.66913, 0.65606, 0.64279, 0.62932, 0.61566,
    0.60182, 0.58779, 0.57358, 0.55919, 0.54464, 0.52992, 0.51504, 0.50000,
    0.48481, 0.46947, 0.45399, 0.43837, 0.42262, 0.40674, 0.39073, 0.37461,
    0.35837, 0.34202, 0.32557, 0.30902, 0.29237, 0.27564, 0.25882, 0.24192,
    0.22495, 0.20791, 0.19081, 0.17365, 0.15643, 0.13917, 0.12187, 0.10453,
    0.08716, 0.06976, 0.05234, 0.03490, 0.01745, 0.00000, -0.01745, -0.03490,
    -0.05234, -0.06976, -0.08716, -0.10453, -0.12187, -0.13917, -0.15643,
    -0.17365, -0.19081, -0.20791, -0.22495, -0.24192, -0.25882, -0.27564,
    -0.29237, -0.30902, -0.32557, -0.34202, -0.35837, -0.37461, -0.39073,
    -0.40674, -0.42262, -0.43837, -0.45399, -0.46947, -0.48481, -0.50000,
    -0.51504, -0.52992, -0.54464, -0.55919, -0.57358, -0.58779, -0.60182,
    -0.61566, -0.62932, -0.64279, -0.65606, -0.66913, -0.68200, -0.69466,
    -0.70711, -0.71934, -0.73135, -0.74314, -0.75471, -0.76604, -0.77715,
    -0.78801, -0.79864, -0.80902, -0.81915, -0.82904, -0.83867, -0.84805,
    -0.85717, -0.86603, -0.87462, -0.88295, -0.89101, -0.89879, -0.90631,
    -0.91355, -0.92050, -0.92718, -0.93358, -0.93969, -0.94552, -0.95106,
    -0.95630, -0.96126, -0.96593, -0.97030, -0.97437, -0.97815, -0.98163,
    -0.98481, -0.98769, -0.99027, -0.99255, -0.99452, -0.99619, -0.99756,
    -0.99863, -0.99939, -0.99985, -1.00000, -0.99985, -0.99939, -0.99863,
    -0.99756, -0.99619, -0.99452, -0.99255, -0.99027, -0.98769, -0.98481,
    -0.98163, -0.97815, -0.97437, -0.97030, -0.96593, -0.96126, -0.95630,
    -0.95106, -0.94552, -0.93969, -0.93358, -0.92718, -0.92050, -0.91355,
    -0.90631, -0.89879, -0.89101, -0.88295, -0.87462, -0.86603, -0.85717,
    -0.84805, -0.83867, -0.82904, -0.81915, -0.80902, -0.79864, -0.78801,
    -0.77715, -0.76604, -0.75471, -0.74314, -0.73135, -0.71934, -0.70711,
    -0.69466, -0.68200, -0.66913, -0.65606, -0.64279, -0.62932, -0.61566,
    -0.60182, -0.58779, -0.57358, -0.55919, -0.54464, -0.52992, -0.51504,
    -0.50000, -0.48481, -0.46947, -0.45399, -0.43837, -0.42262, -0.40674,
    -0.39073, -0.37461, -0.35837, -0.34202, -0.32557, -0.30902, -0.29237,
    -0.27564, -0.25882, -0.24192, -0.22495, -0.20791, -0.19081, -0.17365,
    -0.15643, -0.13917, -0.12187, -0.10453, -0.08716, -0.06976, -0.05234,
    -0.03490, -0.01745, -0.00000
])
 
costable = array.array('f', [
    1.00000, 0.99985, 0.99939, 0.99863, 0.99756, 0.99619, 0.99452,
    0.99255, 0.99027, 0.98769, 0.98481, 0.98163, 0.97815, 0.97437, 0.97030,
    0.96593, 0.96126, 0.95630, 0.95106, 0.94552, 0.93969, 0.93358, 0.92718,
    0.92050, 0.91355, 0.90631, 0.89879, 0.89101, 0.88295, 0.87462, 0.86603,
    0.85717, 0.84805, 0.83867, 0.82904, 0.81915, 0.80902, 0.79864, 0.78801,
    0.77715, 0.76604, 0.75471, 0.74314, 0.73135, 0.71934, 0.70711, 0.69466,
    0.68200, 0.66913, 0.65606, 0.64279, 0.62932, 0.61566, 0.60182, 0.58779,
    0.57358, 0.55919, 0.54464, 0.52992, 0.51504, 0.50000, 0.48481, 0.46947,
    0.45399, 0.43837, 0.42262, 0.40674, 0.39073, 0.37461, 0.35837, 0.34202,
    0.32557, 0.30902, 0.29237, 0.27564, 0.25882, 0.24192, 0.22495, 0.20791,
    0.19081, 0.17365, 0.15643, 0.13917, 0.12187, 0.10453, 0.08716, 0.06976,
    0.05234, 0.03490, 0.01745, 0.00000, -0.01745, -0.03490, -0.05234, -0.06976,
    -0.08716, -0.10453, -0.12187, -0.13917, -0.15643, -0.17365, -0.19081,
    -0.20791, -0.22495, -0.24192, -0.25882, -0.27564, -0.29237, -0.30902,
    -0.32557, -0.34202, -0.35837, -0.37461, -0.39073, -0.40674, -0.42262,
    -0.43837, -0.45399, -0.46947, -0.48481, -0.50000, -0.51504, -0.52992,
    -0.54464, -0.55919, -0.57358, -0.58779, -0.60182, -0.61566, -0.62932,
    -0.64279, -0.65606, -0.66913, -0.68200, -0.69466, -0.70711, -0.71934,
    -0.73135, -0.74314, -0.75471, -0.76604, -0.77715, -0.78801, -0.79864,
    -0.80902, -0.81915, -0.82904, -0.83867, -0.84805, -0.85717, -0.86603, 
    -0.87462, -0.88295, -0.89101, -0.89879, -0.90631, -0.91355, -0.92050,
    -0.92718, -0.93358, -0.93969, -0.94552, -0.95106, -0.95630, -0.96126,
    -0.96593, -0.97030, -0.97437, -0.97815, -0.98163, -0.98481, -0.98769,
    -0.99027, -0.99255, -0.99452, -0.99619, -0.99756, -0.99863, -0.99939,
    -0.99985, -1.00000, -0.99985, -0.99939, -0.99863, -0.99756, -0.99619,
    -0.99452, -0.99255, -0.99027, -0.98769, -0.98481, -0.98163, -0.97815,
    -0.97437, -0.97030, -0.96593, -0.96126, -0.95630, -0.95106, -0.94552,
    -0.93969, -0.93358, -0.92718, -0.92050, -0.91355, -0.90631, -0.89879,
    -0.89101, -0.88295, -0.87462, -0.86603, -0.85717, -0.84805, -0.83867,
    -0.82904, -0.81915, -0.80902, -0.79864, -0.78801, -0.77715, -0.76604,
    -0.75471, -0.74314, -0.73135, -0.71934, -0.70711, -0.69466, -0.68200,
    -0.66913, -0.65606, -0.64279, -0.62932, -0.61566, -0.60182, -0.58779,
    -0.57358, -0.55919, -0.54464, -0.52992, -0.51504, -0.50000, -0.48481,
    -0.46947, -0.45399, -0.43837, -0.42262, -0.40674, -0.39073, -0.37461,
    -0.35837, -0.34202, -0.32557, -0.30902, -0.29237, -0.27564, -0.25882,
    -0.24192, -0.22495, -0.20791, -0.19081, -0.17365, -0.15643, -0.13917,
    -0.12187, -0.10453, -0.08716, -0.06976, -0.05234, -0.03490, -0.01745,
    -0.00000, 0.01745, 0.03490, 0.05234, 0.06976, 0.08716, 0.10453, 0.12187,
    0.13917, 0.15643, 0.17365, 0.19081, 0.20791, 0.22495, 0.24192, 0.25882,
    0.27564, 0.29237, 0.30902, 0.32557, 0.34202, 0.35837, 0.37461, 0.39073,
    0.40674, 0.42262, 0.43837, 0.45399, 0.46947, 0.48481, 0.50000, 0.51504,
    0.52992, 0.54464, 0.55919, 0.57358, 0.58779, 0.60182, 0.61566, 0.62932,
    0.64279, 0.65606, 0.66913, 0.68200, 0.69466, 0.70711, 0.71934, 0.73135,
    0.74314, 0.75471, 0.76604, 0.77715, 0.78801, 0.79864, 0.80902, 0.81915,
    0.82904, 0.83867, 0.84805, 0.85717, 0.86603, 0.87462, 0.88295, 0.89101,
    0.89879, 0.90631, 0.91355, 0.92050, 0.92718, 0.93358, 0.93969, 0.94552,
    0.95106, 0.95630, 0.96126, 0.96593, 0.97030, 0.97437, 0.97815, 0.98163,
    0.98481, 0.98769, 0.99027, 0.99255, 0.99452, 0.99619, 0.99756, 0.99863,
    0.99939, 0.99985, 1.00000
])

class Actor:
    def __init__(self, info=None, position=None, health=None):
        self.info = info
        self.position = position
        self.health = health
    def __repr__(self):
        attrs = ", ".join(f"{k}={v}" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({attrs})"

class Player(Actor):
    def __repr__(self):
        attrs = ", ".join(f"{k}={v}" for k, v in self.__dict__.items())
        return f"{self.__class__.__base__.__name__}<{self.__class__.__name__}>({attrs})"

class Component:
    def __repr__(self):
        attrs = ", ".join(f"{k}={v}" for k, v in self.__dict__.items())
        return f"{self.__class__.__base__.__name__}<{self.__class__.__name__}>({attrs})"

class Info(Component):
    def __init__(self, name, char):
        self.name = name
        self.char = char

class Position(Component):
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
    @classmethod
    def origin(cls):
        return Position(0, 0)

class Health(Component):
    def __init__(self, hp=1):
        self.cur_hp = self.max_hp = hp
    @property
    def alive(self):
        return self.cur_hp > 0

def generate_random_positions(width, height, blocked=None):
    positions = generate_positions(width, height)
    random.shuffle(positions)
    for p in positions:
        yield p

def generate_positions(width, height, blocked=None):
    if not blocked:
        blocked = set()
    return [(x, y) for x in range(width) for y in range(height) if (x, y) not in blocked]

def build_actor_positions(positions):
    return [Actor(position=Position(*p)) for p in positions]

def choose_actors(actors, num_actors=10):
    if num_actors > len(actors):
        raise ValueError(f"Number of actors to be chosen larger than actors pool")
    return random.choices(actors, k=num_actors)

def generate_n_actors_with_positions(width, height, num_actors):
    return choose_actors(build_actor_positions(generate_positions(width, height)), num_actors)

def generate_alphabet_actors(generator):
    for i in range(10):
        yield Actor(
            info=Info('ai', chr(97+i)), 
            position=Position(*next(generator)),
            health=Health()
        )

def generate_player_actor(generator):
    return Player(
        info=Info("player", "@"), 
        position=Position(*next(generator)),
        health=Health()
        )

possible_positions = [
    (x, y) for x in range(-1, 2) for y in range(-1, 2) if (x, y) != (0, 0)
]
def generate_random_cardinal_position():
    return random.choice(possible_positions)

sort_by_position = lambda o: (o.position.x, o.position.y)

def help_text():
    return """
q w e   For movement the corresponding movement key
a X d   to move must be entered as followed:
z s c       <movement_key><ENTER>

Win condition:
    Allies are a, d, e, i. All others must be removed"""[1:]

def render(gamemap, objects, logger):
    buffer = [row[:] for row in gamemap.map_array]
    os.system('cls')
    obj_chars = []
    for obj in objects:
        buffer[obj.position.y][obj.position.x] = obj.info.char
        obj_chars.append(obj.info.char)
    obj_chars.sort()
    print("".join(obj_chars))
    print("\n".join("".join(line) for line in buffer))
    print("\n".join(logger.messages))

movement_mapper = {
    'q': (-1, -1),
    'w': (0, -1),
    'e': (1, -1),
    'a': (-1, 0),
    'd': (1, 0),
    'z': (-1, 1),
    's': (0, 1),
    'c': (1, 1)
}

class Rect:
    def __init__(self, x0, y0, x1, y1):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1

class Map:
    def __init__(self, width, height, map_array):
        self.width = width
        self.height = height
        self.map_array = map_array
        self.view_buffer = [row[:] for row in map_array]
    def open_tiles(self):
        return [
            (x, y)
                for x in range(self.width)
                    for y in range(self.height)
                        if self.map_array[y][x] != '#'
        ]
    def generate_random_open_position(self):
        open_tiles = self.open_tiles()
        random.shuffle(open_tiles)
        for position in open_tiles:
            yield position
    def check_blocked_tile(self, x, y):
        return self.map_array[y][x] == '#'
    def view(self, position):
        return "\n".join("".join(line) for line in self.map_array)
    @classmethod
    def from_string(cls, mapstring):
        rows = mapstring.split('\n')
        height = len(rows)
        width = len(rows[0])
        map_array = [[char for char in row] for row in rows]
        return cls(width, height, map_array)

class Logger:
    def __init__(self):
        self._messages = []
    @property
    def messages(self):
        messages = [m for m in self._messages]
        self._messages.clear()
        return messages
    def add(self, message):
        if message:
            self._messages.append(message)

class Engine:
    def __init__(self):
        self.map = Map.from_string(DUNGEON)
        generator = self.map.generate_random_open_position()
        self.actors = list(generate_alphabet_actors(generator))
        self.player = generate_player_actor(generator)
        self.actors.append(self.player)
        random.shuffle(self.actors) 
        self.running = False

    def get_actors(self):
        for actor in self.actors:
            yield actor

    def run(self):
        self.running = True
        player_actor = False
        logger = Logger()
        g = self.get_actors()
        completed_action = True
        while self.running:
            if completed_action:
                try:
                    actor = next(g)
                except StopIteration:
                    g = self.get_actors()
                    actor = next(g)
                completed_action = False
            player_actor = False
            if isinstance(actor, Player):
                player_actor = True
            if player_actor:
                player_input = None
                input_needed = True
                render(self.map, self.actors, logger)
                while input_needed:
                    if keyboard.is_pressed('esc'):
                        self.running = False
                        break
                    for char in 'qweasdzc':
                        if keyboard.is_pressed(char):
                            player_input = char
                            input_needed = False
                            break
                    time.sleep(1/30)
                action = movement_mapper.get(player_input, (0, 0))
            else:
                action = generate_random_cardinal_position()
            completed_action, message = self.update_actor_position(actor, *action)
            if player_actor:
                logger.add(message)
                if not completed_action:
                    continue
                self.actors[:] = [actor for actor in self.actors if actor.health.alive]
                actors = []
                for actor in self.actors:
                    actors.append(actor.info.char)
                actors.sort()
                if ''.join(actors) == '@adei':
                    self.running = False
                    logger.add("You win")
                    render(self.map, self.actors, logger)

    def update_actor_position(self, actor, x, y) -> (bool, str):
        temp_x = min(self.map.width-1, max(actor.position.x + x, 0))
        temp_y = min(self.map.height-1, max(actor.position.y + y, 0))
        if self.map.check_blocked_tile(temp_x, temp_y):
            if actor == self.player:
                return False, f"{actor.info.char} hit a wall!"
            return False, ""
        for other in self.actors:
            if actor != other and (temp_x, temp_y) == (other.position.x, other.position.y):
                if actor == self.player:
                    if other.info.char in "idea":
                        return True, f"'{actor.info.char}' bumped into '{other.info.char}'"
                    else:
                        other.health.cur_hp = 0
                        return True, f"'{actor.info.char}' hit '{other.info.char}'. '{other.info.char}' has died!"
                return True, ""
        actor.position.x = temp_x
        actor.position.y = temp_y
        return True, ""

class ECSTest:
    @staticmethod
    def run_all():
        passed = []
        failed = []
        tests = 0
        for test in ECSTest.__dict__:
            if test.startswith("test_auto"):
                test_func = getattr(ECSTest, test)
                try:
                    test_func()
                except AssertionError as e:
                    print(e)
                    failed.append(test)
                except Exception as e:
                    raise e
                else:
                    passed.append(test)
                finally:
                    tests += 1
        ECSTest.print_results(passed, failed, tests)
        return not failed
    @staticmethod
    def print_results(passed, failed, num_tests):
        for test_type, tests in (('passed', passed), ('failed', failed)):
            if tests:
                format_test_names = "\n    ".join(tests)
                print(f"""{test_type}:
    {format_test_names}""")
        if len(passed) > len(failed):
            print(f"percentage failed: {len(failed)/num_tests:.02f}%")
    @staticmethod
    def test_class_get_info(cls, info):
        actor_info = cls(info).info
        assert actor_info == info, f"Got: {actor_info}. Expected: {info}"
    @staticmethod
    def test_auto_actor_get_info(info="actor"):
        actor_info = Actor(info).info
        assert actor_info == info, f"Got: {actor_info}. Expected: {info}"
    @staticmethod
    def test_auto_player_get_info(name="player", char="char"):
        actor_info = Player(info=Info(name, char), position=None).info
        assert actor_info.name == name, f"Got: {actor_info.name}. Expected: {name}"
        assert actor_info.char == char, f"Got: {actor_info.char}. Expected: {char}"
    @staticmethod
    def test_auto_sort_by_position(width=MAP_WIDTH, height=MAP_HEIGHT):
        positions = generate_positions(width, height)
        actors = build_actor_positions(positions)
        chosen = choose_actors(actors)
        chosen.sort(key=sort_by_position)
        x, y = -1, -1
        for choice in chosen:
            if x != choice.position.x:
                x, y = choice.position.x, -1
            assert x <= choice.position.x, f"x: {x} > {choice.position.x}"
            assert y <= choice.position.y, f"y: {y} > {choice.position.y}"
            x, y = choice.position.x, choice.position.y
    @staticmethod
    def test_sort_by_position(actors=None, width=MAP_WIDTH, height=MAP_HEIGHT):
        if not actors:
            positions = generate_positions(width, height)
            actors = generate_actor_positions(positions)
        chosen = random.choices(actors, k=10)
        chosen.sort(key=sort_by_position)
        r = Renderer(width, height)
        r.render(chosen)

if __name__ == "__main__":
    if ECSTest.run_all():
        input("All tests passed")
        Engine().run()
