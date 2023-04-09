# Import packages. You can import additional packages, if you want
# You can change the way they are imported, e.g import pulp as pl or whatever
# But take care to adapt the solver configuration accordingly.
from pulp import *
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
import matplotlib

# Use the following solver
solver = COIN_CMD(path="/usr/bin/cbc",threads=8)
# at home, you can try it with different solvers, e.g. GLPK, or with a different
# number of threads.
# WARNING: your code when run in vocareum should finish within 10 minutes!!!

def generate_visualization(data, filename_to_save):
    #nested_array: an array containing 5 sub-arrays (id, dough_ready, start_bake, end_bake, pickup)
    # Define the x-axis and y-axis labels
    # Set up the plot
    data_sorted = sorted(data, key=lambda x: x[2])
    filename_to_save = "./visualization.png"
    n = len(data_sorted)

    fig, axs = plt.subplots(nrows=3, ncols=1, figsize=(13, 20),
                            gridspec_kw={'height_ratios': [2, 1, 1]})

    # Increase the vertical gap between sub-plots
    plt.subplots_adjust(hspace=1)

    # Plot 0: original plot
    axs[0].set_title("Baking Schedule Gantt Chart")
    axs[0].set_xlabel('Time')
    axs[0].set_ylabel('Pastry')
    x_ticks = [i * 1800 for i in range(n)]
    axs[0].set_xticks(x_ticks)
    axs[0].set_xticklabels(['{:02d}:{:02d}'.format(x // 3600, (x % 3600) // 60) for x in x_ticks])
    y_ticks = [i for i in range(n)]
    y_tick_labels = ['#{:02d}'.format(i[0]) for i in data_sorted]
    axs[0].set_yticks(y_ticks)
    axs[0].set_yticklabels(y_tick_labels)
    axs[0].tick_params(axis='y', which='major', pad=12)
    for i, pastry in enumerate(data_sorted):
        x_bake_start = pastry[2]
        x_bake_end = pastry[3]
        y = i
        rect = Rectangle((x_bake_start, y - 0.4), x_bake_end - x_bake_start, 0.8, linewidth=1, edgecolor='gray',
                         facecolor='gray')
        axs[0].add_patch(rect)
        axs[0].plot([pastry[2]], [y], marker=4, markersize=4, markerfacecolor="None",
         markeredgecolor='gray', markeredgewidth=4)
        axs[0].plot([pastry[3]], [y], marker=5, markersize=4, markerfacecolor="None",
         markeredgecolor='gray', markeredgewidth=4)
        axs[0].plot([pastry[1]], [y], marker='|', markersize=14, color='blue')
        axs[0].plot([pastry[4]], [y], marker='|', markersize=14, color='red')
    legend_handles = [
        plt.Line2D([], [], marker='|', markersize=12, color='blue', label='Dough ready to bake', linestyle='None'),
        plt.Line2D([], [], marker='|', markersize=12, color='red', label='Pickup deadline', linestyle='None'),
        plt.Line2D([], [], marker=4, markersize=6, color='gray', label='Pastry goes in', linestyle='None'),
        plt.Line2D([], [], marker=5, markersize=6, color='gray', label='Pastry goes out', linestyle='None')
    ]
    axs[0].legend(handles=legend_handles, loc='lower center')

    # Plot 1: height-coded bars
    heights = [(pastry[2] - pastry[1]) for pastry in data_sorted]
    sorted_indices = sorted(range(len(heights)), key=lambda k: heights[k])
    sorted_heights = [heights[i] for i in sorted_indices]

    axs[1].set_title("Dough-ready to pastry-enters-oven time buffer")
    axs[1].bar(['#{:02d}'.format(data_sorted[i][0]) for i in sorted_indices], sorted_heights)
    axs[1].set_xlabel('Pastry')
    axs[1].set_ylabel('Time buffer (in hours)')
    axs[1].tick_params(axis='y', which='major', pad=1)
    axs[1].set_yticks([i*3600 for i in range(int(max(heights)/3600)+2)])
    axs[1].set_yticklabels([f'{i}:00' for i in range(int(max(heights)/3600)+2)])

    # Plot 2: color-coded bars
    gaps = [(pastry[4] - pastry[3]) for pastry in data_sorted]
    sorted_indices = sorted(range(len(gaps)), key=lambda k: gaps[k])
    sorted_gaps = [gaps[i] for i in sorted_indices]
    norm = matplotlib.colors.Normalize(vmin=sorted_gaps[0], vmax=sorted_gaps[-1])
    sorted_colors = [matplotlib.cm.RdBu(norm(gap)) for gap in sorted_gaps]
    axs[2].set_title("Critical to Less-critical pastries color chart")
    axs[2].bar(['#{:02d}'.format(data_sorted[i][0]) for i in sorted_indices], [1]*n, color=sorted_colors)
    axs[2].set_xlabel('Pastry')
    axs[2].set_ylabel('Color-coded gap')
    axs[2].tick_params(axis='both', which='both',length=0)
    axs[2].tick_params(axis='y', labelsize=0)
    axs[2].set_xlim(-0.5, n-0.5)
    bbox_props = dict(boxstyle="square, pad=0.3", fc="yellow", ec="black", lw=0.5)
    axs[2].text(0.062, -0.4, '1. The baker should store the bluer pastries in increasingly more heat-preserving packaging'
                          ' (larger gap with customer arrival). \n'
                           '2. The redder a pastry, the more critical it is that its baking is delivered on time'
                           ' (smaller gap with customer arrival).',
                fontsize=10, transform=axs[2].transAxes, ma='left', ha='left', va='center', bbox=bbox_props)

    # Show the plot
    plt.savefig(filename_to_save, dpi=300)


def bakery():
    # Input file is called ./bakery.txt
    input_filename = './bakery.txt'

    # Use solver defined above as a parameter of .solve() method.
    # e.g., if your LpProblem is called prob, then run
    # prob.solve(solver) to solve it

    #Big-M penalty
    M = 10 ** 10

    # Constraints
    pastry_ids = []
    dough_ready_array = []
    baking_time_array = []
    deadline_array = []
    #Read the file
    with open(input_filename, 'r') as f:
        for line in f:
            line_clean = line.strip()
            pastry_id, pastry_ready_to_bake_time, pastry_ready_deadline, pastry_baking_time = line_clean.split()[:4]

            pastry_ids.append(int(pastry_id))
            dough_ready_array.append(int(pastry_ready_to_bake_time))
            baking_time_array.append(int(pastry_baking_time))
            deadline_array.append(int(pastry_ready_deadline))

    n = len(pastry_ids)

    problem = LpProblem("Minimize sum of starting times", LpMinimize)
    s = LpVariable.dicts("s", range(0, n), lowBound=0)
    # define the objective function
    problem += lpSum([s[i] for i in range(0, n)])

    # define the constraints
    for i in range(0, n):
        problem += s[i] + baking_time_array[i] <= deadline_array[i]
        problem += s[i] >= dough_ready_array[i]
        for j in range(0, n):
            #Constraint activator Auxiliary variable
            z_i_j = LpVariable(f"z_{i}_{j}", lowBound=0, upBound=1, cat=LpInteger)
            problem += s[i] <= s[j] - baking_time_array[i] + M*z_i_j
            problem += s[j] <= s[i] - baking_time_array[j] + M - M*z_i_j

    # solve the problem
    problem.solve()

    # print the solution
    retval = dict()
    visualization_data = []
    for i in range(0, n):
        retval[f"s_{i}"] = s[i].varValue
        _visual_tuple = (i, dough_ready_array[i], s[i].varValue, s[i].varValue + baking_time_array[i], deadline_array[i])
        visualization_data.append(_visual_tuple)

    print("Objective value:", value(problem.objective))
    print(retval)

    # Write visualization to the correct file:
    visualization_filename = './visualization.png'
    generate_visualization(visualization_data, visualization_filename)

    # retval should be a dictionary such that retval['s_i'] is the starting
    # time of pastry i
    return retval

if __name__ == "__main__":
    bakery()