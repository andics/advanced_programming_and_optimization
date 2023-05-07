import numpy as np
import cvxpy as cp

#######
# DATA, do not change this part!
#######
a=[0.5, -0.5, 0.2, -0.7, 0.6, -0.2, 0.7, -0.5, 0.8, -0.4]
l=[40, 20, 40, 40, 20, 40, 30, 40, 30, 60]
Preq=np.arange(a[0],a[0]*(l[0]+0.5),a[0])
for i in range(1, len(l)):
    Preq=np.r_[ Preq, np.arange(Preq[-1]+a[i],Preq[-1]+a[i]*(l[i]+0.5),a[i]) ]

T = sum(l)

Peng_max = 20.0
Pmg_min = -6.0
Pmg_max = 6.0
eta = 0.1
gamma = 0.1
#####
# End of DATA part
#####

# Implement the following functions
# they should return a dictionary retval such that
# retval['Peng'] is a list of floats of length T such that retval['Peng'][t] = P_eng(t+1) for each t=0,...,T-1
# retval['Pmg'] is a list of floats of length T such that retval['Pmg'][t] = P_mg(t+1) for each t=0,...,T-1
# retval['Pbr'] is a list of floats of length T such that retval['Pbr'][t] = P_br(t+1) for each t=0,...,T-1
# retval['E'] is a list of floats of length T+1 such that retval['E'][t] = E(t+1) for each t=0,...,T

#---EXPLAINATIONS---
'''
NOTE:
1. For more detailed output on all constraints set verbose = True in print statements

The following code offers implementations of both glitch-handling suggestions for the assignment. Before diving into
the intricacies of both presented solutions, let us give a brief explanation as to why the relaxation of the E constraints
gives an equivalent solution to the problem.
1. We firstly state that it clearly holds: if A⊆B then min f(a) >= min f(b) (a in A, b in B);
1.1. Here we denote with A the set of feasible solutions to the original problem and with B the set of feasible
solutions to the relaxed one.
1.2. f is our objective function.
2. Thus, we have that any solution to the relaxation is a lower-bound to the original.
3. Now we only need to prove that the solution x we achieve for the relaxation can be transformed to a solution
x* for the original, without changing the objective.
3.1. If we do that, we strengthen the above-written claim with equality and conclude the proof.
4. Call this transformation of x* into x the function g.
5. We trivially showed two implementations of g, which achieve equality of the relaxed constraints up to the desired precision
6. Thus, we can transform an x* to an x and conclude the proof.
7. It must be noted that 3.1. is trivial to argue by contradiction if one wishes to do so: indeed if an x*
can be transformed into an x, then either f(x*) is the optimum or it is not a lower bound to the original (contradiction)

It must also be stated that the original problem needed to be relaxed in order to satisfy DCP rules:
indeed, adding an absolute-value l.b. results in DCP violation.

Additionally, we add that the solver would generally tend towards solutions that keep the energy waste to a minimum,
since the Energy available determines to what degree the motor can be utilized. Clearly, more is beneficial to the
objective function. As such, higher values of E are generally desirable and if one were choosing in which direction
to violate the law of conservation of energy, the upper one would be the obvious choice.

Now for the technical part:
The main functions are:
1. minimize_fuel_consumpt_using_postproc:
This function implements the first suggestion and post-processes the solution to the original problem s.t.
the errors related to the battery's energy loss are kept to a minimum. The paradigm is as follows:
1.1. The error for constraint i is eliminated by setting E[i] equal to E[i-1] - Pm[i-1] - eta * abs(Pm[i-1])
1.2. In turn, however, this change may cause issues to the battery's energy at the following timestamp (may exceed capacity)
1.3. In order to prevent this from happening, a preventative Auxiliary condition check is put in place:
1.3.1. If the capacity is indeed exceeded, we adjust the Pmg value to decrease it without modifying E, and
correspondingly update the value of Pbr: in order to maintain feasibility of the solution (as not the violate the
non-relaxed constraints)

2. minimize_fuel_consumpt_using_epsilon:
This function implements the second suggestion, using a value for epsilon equal to 0.0002 in order to
penalize errors in the constraints related to E.
A binary grind search was performed to find an optimal value for epsilon.
'''

def _print_objective_state_and_vars(_Peng: cp.Variable,
                                    _Pmg: cp.Variable,
                                    _Pbr: cp.Variable,
                                    _E: cp.Variable,
                                    _prob: cp.Problem,
                                    verbose: bool):

    slack = []
    slack_values = []
    for t in range(len(Preq)):
        slack += [(_E[t] - _Pmg[t] - eta * cp.abs(_Pmg[t])) - _E[t + 1]]
        if verbose:
            print(f"Slack for constraint {t} E: _E[{t}] - _Pmg[{t}]"
                  f" - eta * abs(_Pmg[{t}])) - _E[{t + 1}] = {slack[t].value}")
            print(
                f"Peng[{t}] = {_Peng[t].value}, Pmg[{t}] = {_Pmg[t].value},"
                f" Pbr[{t}] = {_Pbr[t].value}, E[{t}] = {_E[t].value} \n")
        slack_values.append((_E.value[t] - _Pmg.value[t] - eta * abs(_Pmg.value[t])) - _E.value[t + 1])

    if verbose:
        for t in range(len(Preq)):
            print(f"Error for Peng[{t}] + Pmg[{t}] - Pbr[{t}] - Preq[{t}] ="
                  f"{(_Peng.value[t] + _Pmg.value[t] - _Pbr.value[t] - Preq[t])}")

    print(f"E[1] = {_E.value[0]}, E[{len(Preq) + 1}] = {_E.value[len(Preq)]}")
    print(f"Objective: {_prob.objective.value}")
    print(f"Max error for constraints E: {max(slack_values)}")
    return slack_values



def minimize_fuel_consumpt_using_epsilon(ebatt_max):
    E_max = ebatt_max
    E_min = 0.0
    Pbr_min = 0.0
    epsilon = 0.0002

    # Define decision variables
    Peng = cp.Variable(len(Preq))
    Pmg = cp.Variable(len(Preq))
    Pbr = cp.Variable(len(Preq))
    E = cp.Variable(len(Preq) + 1)

    # Define objective function
    objective_no_epsilon = cp.sum(Peng + gamma * cp.square(Peng))
    objective_yes_epsilon = cp.sum(Peng + gamma * cp.square(Peng) + epsilon * cp.maximum(0, -Pmg))

    # Define constraints
    constraints = []
    for t in range(len(Preq)):
        constraints += [
            Peng[t] >= 0,
            Peng[t] <= Peng_max,
            Pmg[t] >= Pmg_min,
            Pmg[t] <= Pmg_max,
            Pbr[t] >= Pbr_min,
            Peng[t] + Pmg[t] - Pbr[t] == Preq[t],
            E[t + 1] <= E[t] - Pmg[t] - eta * cp.abs(Pmg[t])
        ]

    constraints += [E[0] == E[len(Preq)], E >= E_min, E <= E_max]

    # Solve problem
    prob_no_epsilon = cp.Problem(cp.Minimize(objective_no_epsilon), constraints)
    prob_no_epsilon.solve(solver="ECOS")
    no_epsilon_objective = prob_no_epsilon.objective.value
    print("Original solution, no epsilon penalty (epsilon = 0):")
    _print_objective_state_and_vars(_Peng=Peng, _Pbr=Pbr,
                                    _Pmg=Pmg, _E=E,
                                    _prob=prob_no_epsilon, verbose = False)
    print("\n=======\n")

    # Solve problem YES epsilon
    prob_yes_epsilon = cp.Problem(cp.Minimize(objective_yes_epsilon), constraints)
    prob_yes_epsilon.solve(solver="ECOS")
    print(f"Solution with Epsilon penalty (epsilon = {epsilon}):")
    _print_objective_state_and_vars(_Peng=Peng, _Pbr=Pbr,
                                    _Pmg=Pmg, _E=E,
                                    _prob=prob_yes_epsilon, verbose = False)

    print(f"--- Difference in objective values (original/epsilon-penalized): "
          f"{abs(no_epsilon_objective - prob_yes_epsilon.objective.value)}---")

    retval = dict()
    retval["Peng"] = [float(peng.value) for peng in Peng]
    retval["Pmg"] = [float(pmg.value) for pmg in Pmg]
    retval["Pbr"] = [float(pbr.value) for pbr in Pbr]
    retval["E"] = [float(e.value) for e in E]

    return retval


def minimize_fuel_consumpt_using_postproc(ebatt_max):
    E_max = ebatt_max
    E_min = 0.0
    Pbr_min = 0.0
    epsilon = 0.0002

    # Define decision variables
    Peng = cp.Variable(len(Preq))
    Pmg = cp.Variable(len(Preq))
    Pbr = cp.Variable(len(Preq))
    E = cp.Variable(len(Preq) + 1)

    # Define objective function
    objective_no_epsilon = cp.sum(Peng + gamma * cp.square(Peng))

    # Define constraints
    constraints = []
    for t in range(len(Preq)):
        constraints += [
            Peng[t] >= 0,
            Peng[t] <= Peng_max,
            Pmg[t] >= Pmg_min,
            Pmg[t] <= Pmg_max,
            Pbr[t] >= Pbr_min,
            Peng[t] + Pmg[t] - Pbr[t] == Preq[t],
            E[t + 1] <= E[t] - Pmg[t] - eta * cp.abs(Pmg[t])
        ]

    constraints += [E[0] == E[len(Preq)], E >= E_min, E <= E_max]

    # Solve problem
    prob = cp.Problem(cp.Minimize(objective_no_epsilon), constraints)
    prob.solve(solver="ECOS")
    pre_post_objective = prob.objective.value

    print("Original solution (no post-processing):")
    slack_values = _print_objective_state_and_vars(_Peng = Peng, _Pbr = Pbr,
                                                   _Pmg = Pmg, _E = E,
                                                   _prob = prob, verbose = False)
    print("\n=======\n")

    # We begin the post-processing
    # We will only change values indexed 1 to 360
    for t in range(1, len(Preq) + 1):
        real_E_value = E.value[t-1] - Pmg.value[t-1] - eta * abs(Pmg.value[t-1])

        if real_E_value > ebatt_max:
            E.value[t] = ebatt_max
            old_Pmg = Pmg.value[t - 1]
            err_E = real_E_value - ebatt_max

            if Pmg.value[t-1] < 0:
                Pmg.value[t - 1] = Pmg.value[t - 1] + (err_E/(1 - eta))
            else:
                Pmg.value[t - 1] = Pmg.value[t - 1] + (err_E/(1 + eta))
            Pbr.value[t - 1] = Pbr.value[t - 1] + (Pmg.value[t - 1] - old_Pmg)

        else:
            E.value[t] = real_E_value
            continue

    print("Solution after post-processing:")
    _print_objective_state_and_vars(_Peng=Peng, _Pbr=Pbr,
                                    _Pmg=Pmg, _E=E,
                                    _prob=prob, verbose = False)
    print(f"--- Difference in objective values (pre/post): {abs(pre_post_objective - prob.objective.value)} ---")

    retval = dict()
    retval["Peng"] = [float(peng.value) for peng in Peng]
    retval["Pmg"] = [float(pmg.value) for pmg in Pmg]
    retval["Pbr"] = [float(pbr.value) for pbr in Pbr]
    retval["E"] = [float(e.value) for e in E]

    return retval


def car_with_battery():
    print("\n\nCAR-WITH-BATTERY")
    Ebatt_max = 100.0
    print("Solving problem with post-processing ...\n")
    retval = minimize_fuel_consumpt_using_postproc(Ebatt_max)
    print("\n=====================\n")
    print("Solving problem using Epsilon method ...\n")
    retval_epsilon = minimize_fuel_consumpt_using_epsilon(Ebatt_max)
    return retval

def car_without_battery():
    print("\n\nCAR-WITHOUT-BATTERY")
    Ebatt_max = 0
    print("Solving problem with post-processing ...\n")
    retval = minimize_fuel_consumpt_using_postproc(Ebatt_max)
    print("\n=====================\n")
    print("Solving problem using Epsilon method ...\n")
    retval_epsilon = minimize_fuel_consumpt_using_epsilon(Ebatt_max)
    return retval

car_with_battery()
car_without_battery()