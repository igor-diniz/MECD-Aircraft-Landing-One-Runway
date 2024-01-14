import numpy as np

class Airland:
    def __init__(self, id, n_planes, freeze_time):
        self.id = id
        self.n_planes = n_planes
        self.freeze_time = freeze_time
        self.planes = []
        self.sep_times = np.zeros((n_planes, n_planes), dtype=int)
    

    def register_plane(self, plane):
        self.planes.append(plane)


    def register_sep_time(self, plane_id1, plane_id2, sep_time):
        self.sep_times[plane_id1, plane_id2] = sep_time


    def get_sep_time(self, plane_id1, plane_id2):
        return self.sep_times[plane_id1, plane_id2]


    def get_all_sep_times(self):
        return self.sep_times

    
    def get_planes(self):
        return self.planes
    

