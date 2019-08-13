# test_generate.py

from source.maps import (add_blob, add_boundry_to_matrix, array_to_matrix,
                         burrow_passage, cell_auto, distribution, flood_fill,
                         generate_poisson_array, matrix,
                         replace_cell_with_stairs, rotate, string)


def main():
    random_array = generate_poisson_array(58, 17)
    matrix = array_to_matrix(random_array, 58, 17, lambda x: 3 <= x < 5)
    # print('initial')
    # print(string(matrix))
    bounded = add_boundry_to_matrix(matrix, bounds=1)
    # print('bounded')
    # print(string(bounded))
    no_stairs = bounded
    for i in range(4):
        no_stairs = cell_auto(no_stairs, deadlimit=5+(i-5))
        # print(f'cell auto {i+1}')
        # print(string(no_stairs))
    no_stairs = flood_fill(no_stairs)
    dungeon = replace_cell_with_stairs(no_stairs)
    print('with stairs')
    print(string(dungeon))

def flood_fill_test():
    random_array = generate_poisson_array(58, 17)

    matrix = array_to_matrix(random_array, 58, 17, lambda x: x < 3 or x >= 8)
    bounded = add_boundry_to_matrix(matrix, bounds=1)
    no_stairs = bounded
    for i in range(4):
        no_stairs = cell_auto(no_stairs, deadlimit=5+(i-5))
    print('before floodfill')
    print(string(no_stairs))
    no_stairs = flood_fill(no_stairs)
    dungeon = replace_cell_with_stairs(no_stairs)
    print(string(dungeon))

def burrowing_algo_vertical():
    print(string(burrow_passage(58, 17)))

def burrowing_algo_horizontal():
    print(string(rotate(burrow_passage(58, 17))))

def double_map_join():
    w, h = 191, 50
    maps = [generate_poisson_array(w, h), generate_poisson_array(w, h)]
    for n in range(len(maps)):
        d = maps[n]
        d = array_to_matrix(d, w, h, lambda x: x < 4 or x >= 9)
        d = add_boundry_to_matrix(d, bounds=1)
        for i in range(5):
            d = cell_auto(d, deadlimit=5+(i-5))
        print(string(d))
        d = flood_fill(d)
        maps[n] = d
    for m in maps:
        print(string(m))
    m = [['.' if any(m[y][x] == '.' for m in maps) else '#' for x in range(w)] for y in range(h)]
    print(string(m))

if __name__ == "__main__":
    main()
    flood_fill_test()
    # burrowing_algo_vertical()
    # burrowing_algo_horizontal()
    # double_map_join()
