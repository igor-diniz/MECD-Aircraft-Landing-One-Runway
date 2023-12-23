from file_reader import FileReader
import os
import re
from ortools.linear_solver import pywraplp


def setup_airlands():
    workdir = os.getcwd()
    datasets_dir = os.path.join(workdir, "datasets")
    airlands_files = os.listdir(datasets_dir)
    airlands_files.sort(key=lambda x: int(re.findall("\d+", x)[0]))

    file_reader = FileReader()
    airlands = {index + 1: file_reader.read(os.path.join(datasets_dir, path))
                for index, path in enumerate(airlands_files)
                }
    return airlands


def solve_MIP_airland(airland):
    solver = pywraplp.Solver.CreateSolver('SCIP')
    P = airland.get_planes()  # Set of planes

    ############ Variables ###########
    # Actual landing time for each plane
    x = [solver.IntVar(plane.E, plane.L, f'x_{plane.id}') for plane in P]

    # Difference to the target time from the earlier time for each plane
    alpha = [solver.IntVar(0, plane.T - plane.E, f'alpha_{plane.id}') for plane in P]

    # Difference to the target time from the latest time for each plane
    beta = [solver.IntVar(0, plane.L - plane.T, f'beta_{plane.id}') for plane in P]

    # If plane i lands before plane j for each plane
    delta = [[solver.BoolVar(f'delta_{plane_i.id}_{plane_j.id}') if plane_i.id != plane_j.id else 0 for plane_j in P]
             for plane_i in P]

    W = [(plane_i, plane_j) for plane_i in P for plane_j in P
         if plane_i.id != plane_j.id and plane_i.L < plane_j.E and
         plane_i.L + airland.get_sep_time(plane_i.id, plane_j.id) <= plane_j.E]

    V = [(plane_i, plane_j) for plane_i in P for plane_j in P
         if plane_i.id != plane_j.id and
         plane_i.L < plane_j.E < plane_i.L + airland.get_sep_time(plane_i.id, plane_j.id)]

    U = [(plane_i, plane_j) for plane_i in P for plane_j in P
         if plane_i.id != plane_j.id and
         (plane_j.E <= plane_i.E <= plane_j.L or plane_j.E <= plane_i.L <= plane_j.L or
          plane_i.E <= plane_j.E <= plane_i.L or plane_i.E <= plane_j.L <= plane_i.L)]

    for plane_i, plane_j in W + V:
        delta[plane_i.id][plane_j.id] = 1

    for plane_i, plane_j in V:
        solver.Add(x[plane_j.id] >= x[plane_i.id] + airland.get_sep_time(plane_i.id, plane_j.id))

    for plane_i, plane_j in U:
        solver.Add(x[plane_j.id] >= x[plane_i.id] +
                   airland.get_sep_time(plane_i.id, plane_j.id) * delta[plane_i.id][plane_j.id] -
                   (plane_i.L - plane_j.E) * delta[plane_j.id][plane_i.id])

    # Constraints
    for plane in P:
        solver.Add(x[plane.id] == plane.T - alpha[plane.id] + beta[plane.id])
        solver.Add(alpha[plane.id] >= plane.T - x[plane.id])
        solver.Add(0 <= alpha[plane.id] <= plane.T - plane.E)
        solver.Add(beta[plane.id] >= x[plane.id] - plane.T)
        solver.Add(0 <= beta[plane.id] <= plane.L - plane.T)
        solver.Add(x[plane.id] >= plane.A + airland.freeze_time)

    for plane_i in P:
        for plane_j in P:
            if plane_i.id != plane_j.id:
                solver.Add(delta[plane_i.id][plane_j.id] + delta[plane_j.id][plane_i.id] == 1)

    # Objective Function
    objective = solver.Objective()
    for plane in P:
        objective.SetCoefficient(alpha[plane.id], plane.PCb)
        objective.SetCoefficient(beta[plane.id], plane.PCa)
    objective.SetMinimization()

    # Solve the problem
    status = solver.Solve()
    # Display the results
    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
        print('Objective Value =', objective.Value())
        for plane in P:
            print(f'Plane {plane.id}: Landing time = {x[plane.id].solution_value()}')
    else:
        print('The problem does not have an optimal solution.')


if __name__ == "__main__":
    airlands = setup_airlands()

    # Just a showcase with the airland 1
    airland1 = airlands[3]
    solve_MIP_airland(airland1)
