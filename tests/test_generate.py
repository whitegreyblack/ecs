# test_generate.py

from source.maps import (add_boundry_to_matrix, burrow_passage, cell_auto, flood_fill,
                         generate_poisson_array, matrix,
                         replace_cell_with_stairs, rotate, string,
                         transform_random_array_to_matrix)


def main():
    random_array = generate_poisson_array(58, 17)
    matrix = transform_random_array_to_matrix(random_array, 58, 17, 3)
    print('initial')
    print(string(matrix))
    bounded = add_boundry_to_matrix(matrix)
    print('bounded')
    print(string(bounded))
    no_stairs = bounded
    for i in range(5):
        no_stairs = cell_auto(no_stairs, deadlimit=5+(i-5))
        print(f'cell auto {i+1}')
        print(string(no_stairs))
    dungeon = replace_cell_with_stairs(no_stairs)
    print('with stairs')
    print(string(dungeon))

def flood_fill_test():
    random_array = generate_poisson_array(58, 17)
    matrix = transform_random_array_to_matrix(random_array, 58, 17, 3)
    bounded = add_boundry_to_matrix(matrix)
    no_stairs = bounded
    for i in range(3):
        no_stairs = cell_auto(no_stairs, deadlimit=5+(i-5))
    dungeon = replace_cell_with_stairs(no_stairs)
    print(string(dungeon))

def burrowing_algo_vertical():
    print(string(burrow_passage(75, 17)))

def burrowing_algo_horizontal():
    print(string(rotate(burrow_passage(75, 17))))

if __name__ == "__main__":
    # main()
    # flood_fill_test()
    # burrowing_algo_vertical()
    burrowing_algo_horizontal()
