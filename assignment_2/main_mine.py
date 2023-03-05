import numpy as np
import networkx as nx

def normalize_given_2D_number_grid(np_2D_number_grid):
    grid_flat = np_2D_number_grid.flatten()
    total_brightness = np.sum(grid_flat)

    # Linearly rescale the array, making all entries integers
    grid_normalized = (80*39*grid_flat / total_brightness)
    grid_normalized_int = np.rint(grid_normalized).astype(int)

    # Reshape the rescaled array to its original shape
    grid_normalized = np.reshape(grid_normalized_int, np_2D_number_grid.shape)
    return grid_normalized


def read_text_files_into_a_numpy_grid(array_of_filenames):
    # This function essentially stores all the number grid from the files
    # into one 3-dimensional array, which is normalized: all elements remain integers and have the same sum

    num_grids = np.zeros((len(array_of_filenames), 10, 80))

    for i, file_name in enumerate(array_of_filenames):
        file_path = file_name
        with open(file_path, 'r') as f:
            # Read the number grid from the file
            lines = f.readlines()
            grid = np.array([list(map(int, line.strip())) for line in lines[0:10]])
            # Add the number grid to the numpy array
            num_grids[i, :, :] = normalize_given_2D_number_grid(grid)

    return num_grids

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
                    # Sender has negative, receiver positive
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

                # Calculate distance between nodes (only horizontal matters)
                dist = vx - ux + 80 if ux > vx else vx - ux
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
    files_to_choose_from = files
    try:
        distance_dict = dict()
        for file in files_to_choose_from:
            distance_dict[file] = comp_dist(current_file, file)

        # Sort the dict by EMD
        distance_dict_sorted = {k: v for k, v in sorted(distance_dict.items(), key=lambda item: item[1])}
        sorted_files = list(distance_dict_sorted.keys())
    except Exception as e:
        return files_to_choose_from

    # should return sorted list of file names
    return sorted_files

if __name__ == "__main__":
    print(sort_files())