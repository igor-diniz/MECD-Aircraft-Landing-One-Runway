import networkx as nx
from pulp import LpProblem, LpVariable, LpMinimize, lpSum

class Airland:
    def __init__(self, id, n_planes, freeze_time):
        self.s = 10  # Minimum separation time between two planes landing on the same runway
        self.id = id
        self.n_planes = n_planes
        self.freeze_time = freeze_time
        self.planes = []
        self.Gst = nx.Graph()       # Gst - graph of separated times between landings
        self.Gst.add_nodes_from(range(1, n_planes))

    def register_plane(self, plane):
        self.planes.append(plane)

    def register_sep_time(self, plane_id1, plane_id2, sep_time):
        self.Gst.add_edge(plane_id1, plane_id2, sep_time=sep_time)

    def get_sep_time(self, plane_id1, plane_id2):
        return self.Gst[plane_id1][plane_id2]["sep_time"]

    def get_all_sep_times(self):
        return self.Gst.edges.data()

    def get_planes(self):
        return self.planes

    def solve_linear_programming(self, n_runways=1):
        # Create a linear programming problem
        prob = LpProblem("Airland_Problem", LpMinimize)
        
        # Update the range for runways
        runways_range = range(1, n_runways + 1)

        # Create decision variables
        x = {(i, t, r): LpVariable(name=f"x_{i}_{t}_{r}", cat='Binary') 
             for i in range(1, self.n_planes + 1) 
             for t in range(int(self.planes[i-1].E), int(self.planes[i-1].L) + 1) 
             for r in runways_range}

        # Objective function
        prob += lpSum(self.planes[i-1].PCb * x[i, t, r] if t < self.planes[i-1].T else self.planes[i-1].PCa * x[i, t, r]
                      for i in range(1, self.n_planes + 1) 
                      for t in range(int(self.planes[i-1].E), int(self.planes[i-1].L) + 1) 
                      for r in runways_range), "Objective"


        # Constraints
        # Constraint 1: Each plane must land exactly once within its time window
        for i in range(1, self.n_planes + 1):
            prob += lpSum(x[i, t, r] for t in range(int(self.planes[i-1].E), int(self.planes[i-1].L) + 1) for r in runways_range) == 1

        # Constraint 2: Avoid conflicts between different planes on the same runway and overlapping time.
        for i in range(1, self.n_planes + 1):
            for j in range(i + 1, self.n_planes + 1):
                for t in range(int(self.planes[i-1].E), int(self.planes[i-1].L) + 1):
                    for r in runways_range:
                        for s in runways_range:
                            if (t <= self.planes[j-1].L and t <= self.planes[j-1].E + self.s) and (r == s) and (j != s):
                                try:
                                    prob += x[i, t, r] + x[j, t, s] <= 1
                                except KeyError:
                                    pass

        # Constraint 3: Avoid conflicts between different planes on different runways and overlapping time.
        for i in range(1, self.n_planes + 1):
            for j in range(i + 1, self.n_planes + 1):
                for t in range(int(self.planes[i-1].E), int(self.planes[i-1].L) + 1):
                    for r in runways_range:
                        for u in runways_range:
                            if (t <= self.planes[j-1].L and t <= self.planes[j-1].E + self.s) and (r != u):
                                try:
                                   prob += x[i, t, r] + x[j, t, u] <= 1
                                except KeyError:
                                    pass

        # Solve the problem
        prob.solve()

        # Print the results
        print("Status:", prob.status)
        print("Objective Value:", prob.objective.value())

        for i in range(1, self.n_planes + 1):
            for t in range(int(self.planes[i-1].E), int(self.planes[i-1].L + 1)):
                for r in runways_range:
                    if x[i, t, r].value() == 1:
                        self.planes[i-1].landing_time = t
                        print(f"Plane {i} lands at time {t} on runway {r}")