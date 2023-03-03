import numpy as np
import os
import networkx as nx

# Here you may include additional libraries and define more auxiliary functions:
def normalize_given_2D_number_grid(np_2D_number_grid):
    grid_flat = np_2D_number_grid.flatten()
    total_brightness = np.sum(grid_flat)

    # Linearly rescale the array
    grid_normalized = grid_flat / total_brightness

    # Reshape the rescaled array to its original shape
    grid_normalized = np.reshape(grid_normalized, np_2D_number_grid.shape)
    return grid_normalized


def read_text_files_into_a_numpy_grid(array_of_filenames):
    # This function essentially stores all the number grid fronm the files
    # into one 3-dimensional array, which is normalized: all elements must sum to 1

    num_grids = np.zeros((len(array_of_filenames), 10, 80))

    for i, file_name in enumerate(array_of_filenames):
        file_path = file_name
        with open(file_path, 'r') as f:
            # Read the number grid from the file
            lines = f.readlines()
            assert len(lines) == 10 and all(len(line.strip().split()) == 80 for line in lines), \
                f"Invalid number grid in file {file_path}"
            grid = np.array([list(map(int, line.strip().split())) for line in lines])

            # Add the number grid to the numpy array
            num_grids[i, :, :] = normalize_given_2D_number_grid(grid)

    # Print the final numpy array
    print(num_grids)


# This function should return the EMD distances between file1 and file2.
# EMD distance depends on your choice of distance between pixels and
# this will be taken into account during grading.
def comp_dist(file1, file2):
    # Write your code here:
    num_grid_normalized = read_text_files_into_a_numpy_grid([file1, file2])

    nrows, ncols = num_grid_normalized.shape

    # Create an empty graph
    G = nx.Graph()

    #TO FINISH
    # Add nodes to the graph
    for i in range(nrows):
        for j in range(ncols):
            # Add node with its x, y coordinates and capacity as attributes
            G.add_node((i, j), x=i, y=j, capacity=grid[i, j])

    # Add edges to the graph
    for u in G.nodes():
        ux, uy = G.nodes[u]['x'], G.nodes[u]['y']
        for v in G.nodes():
            vx, vy = G.nodes[v]['x'], G.nodes[v]['y']
            # Calculate Euclidean distance between nodes
            dist = np.sqrt((ux - vx) ** 2 + (uy - vy) ** 2)
            # If distance is 1, add an edge between nodes
            if dist == 1:
                G.add_edge(u, v)

    # Print graph information
    print(nx.info(G))

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
    all_files_grid_unsorted = read_text_files_into_a_numpy_grid(files)


    # should return sorted list of file names
    return sorted_files
