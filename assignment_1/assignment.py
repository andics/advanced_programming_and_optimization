# add import of pulp and other things you need here
import pulp
import numpy as np

def ex1():
    retval = {}
    retval["x"] = None
    retval["y"] = None
    retval["obj"] = None
    retval["tight_constraints"] = [None]
    # Insert your code below:

    model = pulp.LpProblem("MinimizationProblem", pulp.LpMinimize)
    x = pulp.LpVariable("x", cat=pulp.const.LpContinuous)
    y = pulp.LpVariable("y", cat=pulp.const.LpContinuous)

    # The objective function we want to minimize
    model += 122 * x + 143 * y

    # Adding the constraints
    model += x >= -10, "C1"
    model += y <= 10, "C2"
    model += 3 * x + 2 * y <= 10, "C3"
    model += 12 * x + 14 * y >= -12.5, "C4"
    model += 2 * x + 3 * y >= 3, "C5"
    model += 5 * x - 6 * y >= -100, "C6"

    # The problem is solved using PuLP's choice of Solver
    model.solve()

    # Each of the variables is printed with it's resolved optimum value
    print("Optimal solution: ", end = "")
    for v in model.variables():
        print(v.name, "=", v.varValue, end = " ")
    print("\n")
    print(f"Objective value: {model.objective.value()}")

    # Print the tight constraints
    tight_constranints = []
    print("Tight constraints:")
    for i, constraint in enumerate(model.constraints.values()):
        if round(constraint.slack, 2) == 0:
            print(f"#{i+1} is tight: ", constraint)
            tight_constranints.append(i+1)

    retval["x"] = x.varValue
    retval["y"] = y.varValue
    retval["obj"] = model.objective.value()
    retval["tight_constraints"] = tight_constranints

    # Return retval dictionary
    return retval


def ex2():
    retval = {}
    retval['x1'] = None
    retval['x2'] = None
    retval['x3'] = None
    retval['x4'] = None
    retval['x5'] = None
    retval['x6'] = None
    retval['obj'] = None
    # Insert your code below:
    # This is a zero-sum ga,e which we can formulate as an LP as follows:
    model = pulp.LpProblem("MinimizationProblem", pulp.LpMaximize)
    y0 = pulp.LpVariable("y0", cat=pulp.const.LpContinuous)
    y1 = pulp.LpVariable("y1", lowBound=0, cat=pulp.const.LpContinuous)
    y2 = pulp.LpVariable("y2", lowBound=0, cat=pulp.const.LpContinuous)
    y3 = pulp.LpVariable("y3", lowBound=0, cat=pulp.const.LpContinuous)
    y4 = pulp.LpVariable("y4", lowBound=0, cat=pulp.const.LpContinuous)
    y5 = pulp.LpVariable("y5", lowBound=0, cat=pulp.const.LpContinuous)
    y6 = pulp.LpVariable("y6", lowBound=0, cat=pulp.const.LpContinuous)

    # The objective function we want to maximize
    model += y0

    # Adding the constraints. This is essentially a manual multiplication with our payoff matrix
    model += 0*y1 + -2*y2 + 1*y3 + 1*y4 + 1*y5 + 1*y6 - y0 >= 0, "C1"
    model += 2*y1 + 0*y2 + -2*y3 + 1*y4 + 1*y5 + 1*y6 - y0 >= 0, "C2"
    model += -1*y1 + 2*y2 + 0*y3 + -2*y4 + 1*y5 + 1*y6 - y0 >= 0, "C3"
    model += -1*y1 + -1*y2 + 2*y3 + 0*y4 + -2*y5 + 1*y6 - y0 >= 0, "C4"
    model += -1*y1 + -1*y2 + -1*y3 + 2*y4 + 0*y5 + -2*y6 - y0 >= 0, "C5"
    model += -1*y1 + -1*y2 + -1*y3 + -1*y4 + 2*y5 + 0*y6 - y0 >= 0, "C6"
    model += y1 + y2 + y3 + y4 + y5 + y6 == 1, "C7"

    model.solve()

    # Each of the variables is printed with it's resolved optimum value
    print("Optimal solution: ", end = "")
    for v in model.variables():
        print(v.name, "=", v.varValue, end = " ")
    print("\n")
    print(f"Objective value: {model.objective.value()}")

    # Print the tight constraints
    tight_constranints = []
    print("Tight constraints:")
    for i, constraint in enumerate(model.constraints.values()):
        if round(constraint.slack, 2) == 0:
            print(f"#{i+1} is tight: ", constraint)
            tight_constranints.append(i+1)

    retval['x1'] = y1.varValue
    retval['x2'] = y2.varValue
    retval['x3'] = y3.varValue
    retval['x4'] = y4.varValue
    retval['x5'] = y5.varValue
    retval['x6'] = y6.varValue
    retval['obj'] = model.objective.value()

    # return retval dictionary
    return retval


def ex3():
    retval = {}
    retval['obj'] = None
    retval['x1'] = None
    # there should be retval['xi'] for each company number i
    # Insert your code below:
    model = pulp.LpProblem("MinimizationProblem", pulp.LpMinimize)
    vars_dict = pulp.LpVariable.dicts(name="", indices = [f'x{i}' for i in range(1, 70)], lowBound=0,
                                      upBound=2, cat=pulp.LpContinuous)

    # Add the variables to the problem
    model += pulp.lpSum([vars_dict[i] for i in vars_dict])
    # Assign 69 values [0, 2]
    # create vercies #num. equations as xu + xv >= 2

    # Read the edges from input and fill the adjacency matrix
    with open('hw1-03.txt', 'r') as f:
        for i, line in enumerate(f):
            node1, node2 = map(int, line.strip().split())
            model += vars_dict['x' + str(node1)] + vars_dict['x' + str(node2)] >= 2, f"Edge{i}"

    model.solve()

    print("Optimal solution: ", end="")
    for (key, var) in vars_dict.items():
        print(key, "=", var.varValue)
        retval[key] = var.varValue
    print("\n")
    print(f"Objective value: {model.objective.value()}")
    retval["obj"] = model.objective.value()

    # return retval dictionary
    return retval


if __name__ == "__main__":
    ex3()
