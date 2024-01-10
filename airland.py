import networkx as nx
from pulp import LpProblem, LpVariable, LpMinimize, lpSum

class Airland:
    def __init__(self, id, n_planes, freeze_time):
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

    def solve_linear_programming(self):
        # Create a linear programming problem
        prob = LpProblem("Airland_Problem", LpMinimize)

        # Define decision variables
        x = {(i, j): LpVariable(name=f"x_{i}_{j}", cat='Binary') for i in range(1, self.n_planes + 1) for j in range(1, self.n_planes + 1)}

        # Define landing time variables
        landing_times = {i: LpVariable(name=f"landing_time_{i}", lowBound=0) for i in range(1, self.n_planes + 1)}

        # Objective function
        prob += lpSum(x[i, j] for i in range(1, self.n_planes + 1) for j in range(1, self.n_planes + 1)), "Objective"

        # Constraints
        # Constraints
        for i in range(1, self.n_planes + 1):
            prob += lpSum(x[i, j] for j in range(1, self.n_planes + 1)) == 1, f"Plane_{i}_Outgoing_Once"
            prob += lpSum(x[j, i] for j in range(1, self.n_planes + 1)) == 1, f"Plane_{i}_Incoming_Once"
            prob += landing_times[i] >= self.planes[i-1].E, f"Landing_Time_Lower_Bound_{i}"
            prob += landing_times[i] <= self.planes[i-1].L, f"Landing_Time_Upper_Bound_{i}"


        for i in range(1, self.n_planes + 1):
            for j in range(1, self.n_planes + 1):
                if i != j:
                    prob += x[i, j] * (self.get_sep_time(i, j) + self.planes[j-1].A) >= x[j, i] * (self.planes[i-1].T + self.planes[i-1].L), f"Separation_{i}_{j}"

        # Solve the problem
        prob.solve()

        # Store landing times in Plane instances
        for i in range(1, self.n_planes + 1):
            self.planes[i-1].landing_time = landing_times[i].value()

        # Print the results
        print("Status:", prob.status)
        print("Objective Value:", prob.objective.value())

        for plane in sorted(self.planes, key=lambda p: p.landing_time):
            print(f"Plane {plane.id} lands at time {plane.landing_time} on runway")