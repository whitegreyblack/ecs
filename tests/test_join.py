def test(engine):
    start = time.time()
    g = engine.tiles.join(engine.positions, engine.renders)
    for entity_id, components in g:
        pass
    t1 = time.time() - start

    start = time.time()
    g = engine.positions.join(engine.tiles, engine.renders)
    for entity_id, components in g:
        pass
    t2 = time.time() - start

    start = time.time()
    g = engine.renders.join(engine.tiles, engine.positions)
    for entity_id, components in g:
        pass
    t3 = time.time() - start

    start = time.time()
    g = join(engine.positions, engine.tiles, engine.renders)
    for entity_id, components in g:
        pass
    t4 = time.time() - start

    return t1, t2, t3, t4

def test_loop(engine):
    t1s, t2s, t3s, t4s = [], [], [], []
    for _ in range(1000):
        t1, t2, t3, t4 = test(engine)
        t1s.append(t1)
        t2s.append(t2)
        t3s.append(t3)
        t4s.append(t4)
    print(sum(t1s) / len(t1s))
    print(sum(t2s) / len(t2s))
    print(sum(t3s) / len(t3s))
    print(sum(t4s) / len(t4s))
