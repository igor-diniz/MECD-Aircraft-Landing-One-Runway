from file_reader import FileReader
import os
import re

def setup_airlans():
    workdir = os.getcwd()
    datasets_dir = os.path.join(workdir, "datasets")
    airlands_files = os.listdir(datasets_dir)
    airlands_files.sort(key=lambda x: int(re.findall("\d+", x)[0]))

    file_reader = FileReader()
    airlands = { index + 1 : file_reader.read(os.path.join(datasets_dir, path)) 
                for index, path in enumerate(airlands_files)
            }
    return airlands

if __name__ == "__main__":
    airlands = setup_airlans()

    # Just a showcase with the airland 1
    airland1 = airlands[1] 
    planes_al1 = airland1.get_planes()
    for i in planes_al1:
        print(i)
        print()  
