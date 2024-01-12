from plane import Plane
from airland import Airland

class FileReader:
    def __init__(self):
        pass
    
    
    def __read_plane_profile(self, file, plane_id, airland):
        plane_profile = map(float, file.readline().split())
        plane = Plane(plane_id, airland.id, *plane_profile)
        airland.register_plane(plane)


    def __read_sep_times(self, file, n_planes, plane_id, airland):
        n = 0
        while n < n_planes:
            line_times = file.readline().split()

            for plane_j, val in enumerate(line_times):
                airland.register_sep_time(plane_id, n + plane_j, sep_time=float(val))
            
            n += len(line_times)


    def read(self, file_path):
        airland_id = int(file_path.split('.')[0][-1])

        with open(file_path) as f:
            n_planes, freeze_time = map(int, f.readline().split())
            airland = Airland(airland_id, n_planes, freeze_time)
            
            for plane_id in range(n_planes):
                self.__read_plane_profile(f, plane_id, airland)
                self.__read_sep_times(f, n_planes, plane_id, airland)
        
        return airland

                
                
