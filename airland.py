import networkx as nx

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
    

