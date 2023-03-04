import numpy as np
import copy
import networkx as nx

# Here you may include additional libraries and define more auxiliary functions:
def remove_empty_lines(arr):
    # Create an empty list to hold the non-empty strings
    non_empty = []

    # Loop through each string in the array
    for string in arr:
        # Check if the string only contains a new line character
        if string.strip() != "":
            # If it's not an empty string, append it to the non_empty list
            non_empty.append(string)

    # Return the list of non-empty strings
    return non_empty


def normalize_given_2D_number_grid(np_2D_number_grid):
    grid_flat = np_2D_number_grid.flatten()
    total_brightness = np.sum(grid_flat)

    # Linearly rescale the array, making all entries integers
    grid_normalized = (80*39*grid_flat / total_brightness)
    grid_normalized_int = np.rint(grid_normalized).astype(int)

    assert np.array_equiv(grid_normalized, grid_normalized_int)

    # Reshape the rescaled array to its original shape
    grid_normalized = np.reshape(grid_normalized_int, np_2D_number_grid.shape)
    return grid_normalized


def read_text_files_into_a_numpy_grid(array_of_filenames):
    # This function essentially stores all the number grid from the files
    # into one 3-dimensional array, which is normalized: all elements must sum to 1

    num_grids = np.zeros((len(array_of_filenames), 10, 80))

    for i, file_name in enumerate(array_of_filenames):
        file_path = file_name
        with open(file_path, 'r') as f:
            # Read the number grid from the file
            lines = f.readlines()
            lines = remove_empty_lines(lines)
            assert len(lines) == 10 and all(len(line.strip()) == 80 for line in lines), \
                f"Invalid number grid in file {file_path}"
            grid = np.array([list(map(int, line.strip())) for line in lines])

            # Add the number grid to the numpy array
            num_grids[i, :, :] = normalize_given_2D_number_grid(grid)

    return num_grids


def find_rightmost_nonzero_entry_x_cord(numpy_2d_grid):
    # As the name suggests
    nrows, ncols = numpy_2d_grid.shape

    current_x_cord_max = -1
    for y in range(nrows):
        for x in range(ncols):
            if numpy_2d_grid[y, x] != 0:
                if x >= current_x_cord_max:
                    current_x_cord_max = x

    assert current_x_cord_max != -1
    return current_x_cord_max


def file2_right_of_file1(file1, file2, distance_dict_sorted):
    # Check if file2 is to the right of file1.
    # This is needed to ensure we avoid the ha-got-you
    # at play in this problem. Additionally, make sure there are
    # no images horizontally in-between!

    normalized_grid = read_text_files_into_a_numpy_grid([file1, file2])
    file1_rightmost_entry_x = find_rightmost_nonzero_entry_x_cord(normalized_grid[0, :, :])
    file2_rightmost_entry_x = find_rightmost_nonzero_entry_x_cord(normalized_grid[1, :, :])

    # Edge case: when we are given file1 P12
    if (np.any(normalized_grid[0, :, 0])) and (np.any(normalized_grid[0, :, -1])):
        print("We were given P12 as file1")
        file1_rightmost_entry_x = 1

    if file1_rightmost_entry_x < file2_rightmost_entry_x:
        # file2 is to the right of file1
        # Ensure nothing in-between
        del distance_dict_sorted[file2]
        for file_name, dist in distance_dict_sorted.items():
            _tmp_grid = read_text_files_into_a_numpy_grid([file_name])
            _rightmost_x_cord = find_rightmost_nonzero_entry_x_cord(_tmp_grid[0, :, :])
            if _rightmost_x_cord > file1_rightmost_entry_x and _rightmost_x_cord < file2_rightmost_entry_x:
                return False

        return True

        return True
    else:
        return False


# This function should return the EMD distances between file1 and file2.
# EMD distance depends on your choice of distance between pixels and
# this will be taken into account during grading.
def comp_dist(file1, file2):
    # Write your code here:
    num_grid_normalized = read_text_files_into_a_numpy_grid([file1, file2])

    nfiles, nrows, ncols = num_grid_normalized.shape

    # Create an empty graph
    G = nx.DiGraph()

    # Add nodes to the graph
    node_counter = 0
    for file_grid, multiplier in enumerate([-1, 1]):
        for y in range(nrows):
            for x in range(ncols):
                if num_grid_normalized[file_grid, y, x] != 0:
                    # Add node with its x, y coordinates and demand as attribute
                    # We want one file grid to have a negative demand (wants to send), and the
                    # other a positive one (wants to recieve)
                    demand = int(multiplier * num_grid_normalized[file_grid, y, x])
                    G.add_node(node_counter, pos=(y, x), demand=demand)
                    node_counter += 1

    # Add edges to the graph
    for u in G.nodes():
        uy, ux = G.nodes[u]['pos']
        for v in G.nodes():
            vy, vx = G.nodes[v]['pos']
            if (G.nodes[u]['demand'] < 0 and G.nodes[v]['demand'] > 0):
                #Check if the nodes are a sender/reciever pair

                # Calculate Euclidean distance between nodes
                dist = int(np.round(np.sqrt((ux - vx) ** 2)))
                capacity = int(min([abs(G.nodes[u]['demand']),
                                abs(G.nodes[v]['demand'])]))
                G.add_edge(u, v, weight = dist, capacity = capacity)


    distance = nx.min_cost_flow_cost(G, demand='demand', capacity = 'capacity', weight='weight')
    # And return the EMD distance, it should be float.
    return float(distance)


# This function should sort the files as described on blackboard.
# P1.txt should be the first one.
def sort_files():
    # If your code cannot handle all files, remove the problematic ones
    # from the following list and sort only those which you can handle.
    # Your code should never fail!
    files = ['P1.txt', 'P2.txt', 'P3.txt', 'P4.txt', 'P5.txt', 'P6.txt', 'P7.txt', 'P8.txt', 'P9.txt', 'P10.txt', 'P11.txt', 'P12.txt', 'P13.txt', 'P14.txt', 'P15.txt']
    # Write your code here:
    current_file = 'P1.txt'
    sorted_files = [current_file]
    files_left_to_choose_from = files
    files_left_to_choose_from.remove('P1.txt')
    try:
        while len(files_left_to_choose_from) > 0:
            distance_dict = dict()
            for file in files_left_to_choose_from:
                print(f"Calculating distance between {current_file} and {file}")
                distance_dict[file] = comp_dist(current_file, file)

            # Sort the dict by EMD
            we_selected_an_img_to_the_right = False
            distance_dict_sorted = {k: v for k, v in sorted(distance_dict.items(), key=lambda item: item[1])}
            for potential_next_file_name, potential_next_file_emd in distance_dict_sorted.items():
                if file2_right_of_file1(current_file,
                                        potential_next_file_name,
                                        copy.deepcopy(distance_dict_sorted)):
                    sorted_files.append(potential_next_file_name)
                    files_left_to_choose_from.remove(potential_next_file_name)
                    current_file = potential_next_file_name
                    we_selected_an_img_to_the_right = True
                    break

            # Fail-proof mechanism
            if not we_selected_an_img_to_the_right:
                # We have a problem. All the remaining images
                # are to the left of our current one.
                # Thus, there must been a screen-edge in front => select furthest image
                potential_next_file_name = list(distance_dict_sorted.items())[-1][0]
                sorted_files.append(potential_next_file_name)
                files_left_to_choose_from.remove(potential_next_file_name)
                current_file = potential_next_file_name
                we_selected_an_img_to_the_right = True
    except Exception as e:
        return ['P1.txt']

    # should return sorted list of file names
    return sorted_files


if __name__=="__main__":
    print(sort_files())