from file_reader import FileReader

if __name__ == '__main__':
    reader = FileReader()
    airland_instance = reader.read("datasets/airland3.txt")
    airland_instance.solve_linear_programming()