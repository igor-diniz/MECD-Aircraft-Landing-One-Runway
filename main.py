from file_reader import FileReader
import os
import re
import time
import pandas as pd
from ortools.linear_solver import pywraplp
from ortools.sat.python import cp_model
from copy import deepcopy
import tracemalloc

def setup_airlands():
    """ Reads and setup all airlands and stores them as dictionary """
    workdir = os.getcwd()
    datasets_dir = os.path.join(workdir, "datasets")
    airlands_files = os.listdir(datasets_dir)
    airlands_files.sort(key=lambda x: int(re.findall("\d+", x)[0]))

    file_reader = FileReader()
    airlands = {index + 1: file_reader.read(os.path.join(datasets_dir, path))
                for index, path in enumerate(airlands_files)
                }
    return airlands

def print_solution(solution, objective_value, airland_id, type):
    print(f"AIRLAND {airland_id}, {type} SOLUTION")
    print(f"OBJECTIVE VALUE = {objective_value}")

    plane_data = {
        'Plane Order': [plane.id for plane in solution],
        'Appearence Time': [plane.A for plane in solution],
        'Earliest Time': [plane.E for plane in solution],
        'Target Time': [plane.T for plane in solution],
        'Latest Time': [plane.L for plane in solution],
        'Actual Landing Time': [plane.actual_land_time for plane in solution]
    }

    df_planes = pd.DataFrame(plane_data)
    df_planes.to_csv(f"generated_data/airland{airland_id}.csv", index=False)
    print(df_planes)
    print()


def solve_MIP_airland(airland):
    solver = pywraplp.Solver.CreateSolver('SAT')
    P = airland.get_planes()  # Set of planes

    ############ Variables ###########
    # Actual landing time for each plane
    x = [solver.IntVar(plane.E, plane.L, f'x_{plane.id}') for plane in P]

    # Difference to the target time from the earlier time for each plane
    alpha = [solver.IntVar(0, plane.T - plane.E, f'alpha_{plane.id}') for plane in P]

    # Difference to the target time from the latest time for each plane
    beta = [solver.IntVar(0, plane.L - plane.T, f'beta_{plane.id}') for plane in P]

    # If plane i lands before plane j for each plane
    lands_before = [[solver.BoolVar(f'delta_{plane_i.id}_{plane_j.id}') if plane_i.id != plane_j.id else 0 for plane_j in P]
             for plane_i in P]


    ############ Preprocessing ###########
    # Cases where obviously planes_i lands before planes_j without waiting sep time
    W = [(plane_i, plane_j) for plane_i in P for plane_j in P
         if plane_i.id != plane_j.id and plane_i.L < plane_j.E and
         plane_i.L + airland.get_sep_time(plane_i.id, plane_j.id) <= plane_j.E]
    
    # Cases where obviously planes_i lands before planes_j but waiting sep time
    V = [(plane_i, plane_j) for plane_i in P for plane_j in P
         if plane_i.id != plane_j.id and
         plane_i.L < plane_j.E < plane_i.L + airland.get_sep_time(plane_i.id, plane_j.id)]
    
    # Set boolean variables to true in W and V cases
    for plane_i, plane_j in W + V:
        solver.Add(lands_before[plane_i.id][plane_j.id] == 1)
        solver.Add(lands_before[plane_j.id][plane_i.id] == 0)

    # Add restriction to wait sep time for the V cases
    for plane_i, plane_j in V:
        solver.Add(x[plane_j.id] >= x[plane_i.id] + airland.get_sep_time(plane_i.id, plane_j.id))


    ####### To solver deal ########
    # Cases where landing time window are overlaped
    U = [(plane_i, plane_j) for plane_i in P for plane_j in P
         if plane_i.id != plane_j.id and
         (plane_j.E <= plane_i.E <= plane_j.L or plane_j.E <= plane_i.L <= plane_j.L or
          plane_i.E <= plane_j.E <= plane_i.L or plane_i.E <= plane_j.L <= plane_i.L)]

    # Add mutual exclusive restrictions for the U cases
    for plane_i, plane_j in U:
        solver.Add(x[plane_j.id] >= x[plane_i.id] + airland.get_sep_time(plane_i.id, plane_j.id) * lands_before[plane_i.id][plane_j.id] - 
                   (plane_i.L - plane_j.E) * lands_before[plane_j.id][plane_i.id])

    # Complementary Constraints
    for plane in P:
        solver.Add(x[plane.id] == plane.T - alpha[plane.id] + beta[plane.id])
        solver.Add(alpha[plane.id] >= plane.T - x[plane.id])
        solver.Add(beta[plane.id] >= x[plane.id] - plane.T)

        # This constraint is referrenced in the problem, but makes airland 5 and 6 unfeasible if active
        # solver.Add(x[plane.id] >= plane.A + airland.freeze_time)

    for plane_i, plane_j in U:
            if plane_i.id != plane_j.id:
                solver.Add(lands_before[plane_i.id][plane_j.id] + lands_before[plane_j.id][plane_i.id] == 1)

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
        for plane in P:
            plane.actual_land_time = x[plane.id].solution_value()
        
        solution = P.copy()
        solution.sort(key = lambda x: x.actual_land_time)
        print_solution(solution, objective.Value() // 100, airland.id, type="MIP")
        # Objective value is divided by 100, since costs were multiplied by 100 to
        # convert float to integer

    else:
        print('The problem does not have neither optimal nor feasible solution.')

    return solver, objective


def solve_CP_airland(airland):
    model = cp_model.CpModel()
    P = airland.get_planes()  # Set of planes

    ############ Variables ###########
    # Actual landing time for each plane
    t = [model.NewIntVar(plane.E, plane.L, f't_{plane.id}') for plane in P]

    # Cost of each landing time for each arrived plane
    cost = [model.NewIntVar(0, cp_model.INT32_MAX, f'cost_{plane.id}') for plane in P]

    # If plane i lands before plane j for each plane
    lands_before = [[model.NewBoolVar(f'lb_{plane_i.id}_{plane_j.id}') if plane_i.id != plane_j.id else 0 for plane_j in P]
             for plane_i in P]


    ############ Preprocessing ###########
    # Cases where obviously planes_i lands before planes_j without waiting sep time
    W = [(plane_i, plane_j) for plane_i in P for plane_j in P
         if plane_i.id != plane_j.id and plane_i.L < plane_j.E and
         plane_i.L + airland.get_sep_time(plane_i.id, plane_j.id) <= plane_j.E]
    
    # Cases where obviously planes_i lands before planes_j but waiting sep time
    V = [(plane_i, plane_j) for plane_i in P for plane_j in P
         if plane_i.id != plane_j.id and
         plane_i.L < plane_j.E < plane_i.L + airland.get_sep_time(plane_i.id, plane_j.id)]
    
    # Set boolean variables to true in W and V cases
    for plane_i, plane_j in W + V:
        model.Add(lands_before[plane_i.id][plane_j.id] == 1)
        model.Add(lands_before[plane_j.id][plane_i.id] == 0)

    # Set boolean variables to true in W and V cases
    for plane_i, plane_j in W + V:
        model.Add(lands_before[plane_i.id][plane_j.id] == 1)
        model.Add(lands_before[plane_j.id][plane_i.id] == 0)

    # Add restriction to wait sep time for the V cases
    for plane_i, plane_j in V:
        model.Add(t[plane_j.id] >= t[plane_i.id] + airland.get_sep_time(plane_i.id, plane_j.id))


    ####### To solver deal ########
    # Cases where landing time window are overlaped
    U = [(plane_i, plane_j) for plane_i in P for plane_j in P
         if plane_i.id != plane_j.id and
         (plane_j.E <= plane_i.E <= plane_j.L or plane_j.E <= plane_i.L <= plane_j.L or
          plane_i.E <= plane_j.E <= plane_i.L or plane_i.E <= plane_j.L <= plane_i.L)]
    
    # Add mutual exclusive constraint for landing before
    # plane_i lands before plane j XOR the other way around 
    for plane_i, plane_j in U:
        if plane_i.id != plane_j.id:
            model.AddBoolXOr(lands_before[plane_i.id][plane_j.id], lands_before[plane_j.id][plane_i.id])
    
    # Assert separation time constraint
    for plane_i, plane_j in U:
        if plane_i.id != plane_j.id:
            model.Add(t[plane_i.id] + airland.get_sep_time(plane_i.id, plane_j.id) <= t[plane_j.id]).\
                OnlyEnforceIf(lands_before[plane_i.id][plane_j.id])
            model.Add(t[plane_j.id] + airland.get_sep_time(plane_j.id, plane_i.id) <= t[plane_i.id]).\
                OnlyEnforceIf(lands_before[plane_j.id][plane_i.id])


    # Calculate costs based on landing time for each plane
    for plane in P:
        diff1 = model.NewIntVar(-cp_model.INT32_MAX, cp_model.INT32_MAX, 'diff1')
        model.AddMaxEquality(diff1, [0, plane.T - t[plane.id]])

        diff2 = model.NewIntVar(-cp_model.INT32_MAX, cp_model.INT32_MAX, 'diff2')
        model.AddMaxEquality(diff2, [0, t[plane.id] - plane.T])

        model.Add(cost[plane.id] == plane.PCb * diff1 + plane.PCa * diff2)        

    # Objective Function
    model.Minimize(sum(cost))

    # Solve the problem
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # Display the results
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        for plane in P:
            plane.actual_land_time = solver.Value(t[plane.id])
        
        solution = P.copy()
        solution.sort(key = lambda x: x.actual_land_time)
        print_solution(solution, solver.ObjectiveValue() // 100, airland.id,  type="CP")
        # Objective value is divided by 100, since costs were multiplied by 100 to
        # convert float to integer

    else:
        print('The problem does not have neither optimal nor feasible solution.')

    return solver

if __name__ == "__main__":
    airlands = setup_airlands()

    results = []

    tracemalloc.start()

    for index, airland in airlands.items():
        # Measuring the time and memory usage for the solve_MIP_airland function
        airland_mip = deepcopy(airland)
        mip_solver, mip_objective = solve_MIP_airland(airland_mip)
        _, memory_usage_mip = tracemalloc.get_traced_memory()

        tracemalloc.clear_traces()

        # Measuring the time and memory usage for the solve_CP_airland function
        airland_cp = deepcopy(airland)
        cp_solver = solve_CP_airland(airland_cp)
        _, memory_usage_cp = tracemalloc.get_traced_memory()

        tracemalloc.clear_traces()

        results.append({
            'Airland': index,
            'N_planes': len(airland.get_planes()), 
            'MIP_obj_value': mip_objective.Value() // 100,
            'MIP_execution_time': mip_solver.wall_time(),       # milliseconds
            'MIP_memory_usage': memory_usage_mip,
            'CP_obj_value': cp_solver.ObjectiveValue() // 100,
            'CP_execution_time': round(cp_solver.WallTime() * 1000, 2),   # convert to millisecons
            'CP_memory_usage': memory_usage_cp,
            'CP_status': cp_solver.StatusName(),
            'CP_propagations': cp_solver.NumBranches(),
            'CP_conflicts': cp_solver.NumConflicts(),
        })

        if index == 8:
            break

    tracemalloc.stop()

    # Summary of Statistical Results
    print('\t##################### Summary of KPIs for MIP and CP models ####################')
    df_stats = pd.DataFrame(results)
    print(df_stats)
    df_stats.to_csv('generated_data/stats_results.csv', index=False)