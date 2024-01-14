from file_reader import FileReader

if __name__ == '__main__':
    reader = FileReader()
    airland_instance = reader.read("datasets/airland1.txt")
    airland_instance.solve_linear_programming(n_runways=1)