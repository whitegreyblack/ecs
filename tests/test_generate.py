# test_generate.py

from source.maps import (add_boundry_to_matrix, cell_auto, flood_fill,
                         generate_poisson_array, matrixfy_string,
                         replace_cell_with_stairs, stringify_matrix,
                         transform_random_array_to_matrix)


def main():
    random_array = generate_poisson_array(58, 17)
    matrix = transform_random_array_to_matrix(random_array, 58, 17, 3)
    print('initial')
    print(stringify_matrix(matrix))
    bounded = add_boundry_to_matrix(matrix)
    print('bounded')
    print(stringify_matrix(bounded))
    no_stairs = bounded
    for i in range(5):
        no_stairs = cell_auto(no_stairs, deadlimit=5+(i-5))
        print(f'cell auto {i+1}')
        print(stringify_matrix(no_stairs))
    dungeon = replace_cell_with_stairs(no_stairs)
    print('with stairs')
    print(stringify_matrix(dungeon))

def flood_fill_test():
    random_array = generate_poisson_array(58, 17)
    matrix = transform_random_array_to_matrix(random_array, 58, 17, 3)
    print('initial')
    print(stringify_matrix(matrix))
    bounded = add_boundry_to_matrix(matrix)
    print('bounded')
    print(stringify_matrix(bounded))
    no_stairs = bounded
    for i in range(3):
        no_stairs = cell_auto(no_stairs, deadlimit=5+(i-5))
        print(f'cell auto {i+1}')
        print(stringify_matrix(no_stairs))
    print('flood_fill')
    # print(stringify_matrix(flood_fill(no_stairs)))
    print('replace tile with stairs')
    dungeon = replace_cell_with_stairs(no_stairs)
    print(stringify_matrix(dungeon))

if __name__ == "__main__":
    # main()
    flood_fill_test()