import numpy as np
import cvxpy as cp
import typing as Typing

#######
# DATA, do not change this part!
#######
a = [0.5, -0.5, 0.2, -0.7, 0.6, -0.2, 0.7, -0.5, 0.8, -0.4]
l = [40, 20, 40, 40, 20, 40, 30, 40, 30, 60]
Preq = np.arange(a[0], a[0] * (l[0] + 0.5), a[0])
for i in range(1, len(l)):
    Preq = np.r_[Preq, np.arange(Preq[-1] + a[i], Preq[-1] + a[i] * (l[i] + 0.5), a[i])]

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

def _print_objective_state_and_vars(_Peng: cp.Variable,
                                    _Pmg: cp.Variable,
                                    _Pbr: cp.Variable,
                                    _E: cp.Variable,
                                    _prob: cp.Problem):

    slack = []
    slack_values = []
    for t in range(len(Preq)):
        slack += [(_E[t] - _Pmg[t] - eta * cp.abs(_Pmg[t])) - _E[t + 1]]
        print(f"Slack for constraint {t} E: _E[{t}] - _Pmg[{t}]"
              f" - eta * abs(_Pmg[{t}])) - _E[{t + 1}] = {slack[t].value}")
        print(
            f"Peng[{t}] = {_Peng[t].value}, Pmg[{t}] = {_Pmg[t].value},"
            f" Pbr[{t}] = {_Pbr[t].value}, E[{t}] = {_E[t].value} \n")
        slack_values.append(slack[t].value)

    print(f"Objective NO epsilon: {_prob.value}")
    print(f"Max slack for constraint E: {max(slack_values)}")
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
    prob_no_epsilon.solve(solver=cp.ECOS)

    # Solve problem YES epsilon
    prob_yes_epsilon = cp.Problem(cp.Minimize(objective_yes_epsilon), constraints)
    prob_yes_epsilon.solve(solver=cp.ECOS)

    retval = dict()
    retval["Peng"] = [float(peng.value) for peng in Peng]
    retval["Pmg"] = [float(pmg.value) for pmg in Pmg]
    retval["Pbr"] = [float(pbr.value) for pbr in Pbr]
    retval["E"] = [float(e.value) for e in E]

    slack = []
    slack_values = []
    for t in range(len(Preq)):
        slack += [(E[t] - Pmg[t] - eta * cp.abs(Pmg[t])) - E[t + 1]]
        print(f"Slack for constraint {t} E: {slack[t]} = {slack[t].value}")
        print(
            f"Peng[{t}] = {Peng[t].value}, Pmg[{t}] = {Pmg[t].value}, Pbr[{t}] = {Pbr[t].value}, E[{t}] = {E[t].value}")
        slack_values.append(slack[t].value)

    print(f"Objective NO epsilon: {prob_no_epsilon.value}")
    print(f"Objective YES epsilon: {prob_yes_epsilon.value}")
    print(f"Delta: {prob_yes_epsilon.value - prob_no_epsilon.value}")

    print(f"Max slack for constraint E: {max(slack_values)}")

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
    prob_no_epsilon = cp.Problem(cp.Minimize(objective_no_epsilon), constraints)
    prob_no_epsilon.solve(solver=cp.ECOS)

    slack_values = _print_objective_state_and_vars(_Peng = Peng, _Pbr = Pbr,
                                                   _Pmg = Pmg, _E = E,
                                                   _prob = prob_no_epsilon)

    # We begin the post-processing
    # We will only change values indexed 1 to 359
    for t in range(1, len(Preq) - 1):

        E.value[t] = E.value[t] + slack_values[t]
        #E indexing is +1 from t: E[2] is actually E[3]
        if Pmg[t + 1].value < 0:
            Pmg.value[t + 1] = Pmg.value[t + 1] + slack_values[t] / (1 + eta)
            Pbr.value[t + 1] = Pbr.value[t + 1] - slack_values[t] / (1 + eta)
        else:
            Pmg.value[t + 1] = Pmg.value[t + 1] - slack_values[t] / (1 + eta)
            Pbr.value[t + 1] = Pbr.value[t + 1] + slack_values[t] / (1 + eta)

    _print_objective_state_and_vars(_Peng=Peng, _Pbr=Pbr,
                                    _Pmg=Pmg, _E=E,
                                    _prob=prob_no_epsilon)

    return retval


def car_with_battery():
    Ebatt_max = 100.0
    retval = minimize_fuel_consumpt_using_postproc(Ebatt_max)
    return retval


def car_without_battery():
    Ebatt_max = 0
    retval = minimize_fuel_consumpt_using_epsilon(Ebatt_max)
    return retval


car_with_battery()
