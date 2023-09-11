import os,re,sys

class set_args:
    def __init__(self, *kargs, **kwargs):
        self.flags = kwargs.get("flags", "-std=c++17")
        self.lib_path = kwargs.get("lib_path", False)
        self.module_name = kwargs.get("module_name", False)

        
def default_dir():
    home = os.environ["HOME"]
    path = os.path.join(home,"tmp")
    return path

def create_dir(directory_path):
    print("input is", directory_path)
    if "~" in directory_path :
        full_path = os.path.expanduser(directory_path)
        print("tilde")
    elif "./" in directory_path or "../" in directory_path:
        print("absolute path ")
        full_path = os.path.abspath(directory_path)

    else:
        print("anything else")
        home = os.environ["HOME"]
        full_path = os.path.join(home,directory_path)

    if not os.path.exists(full_path):
        print("Creating directory:", full_path)
        os.makedirs(full_path)
    else:
        print("Directory already exists:", full_path)
    return full_path

def write_module(fname, fpath, mname):
    fpath = os.path.expanduser(fpath)
    if not os.path.exists(fpath):
        print("Module path does not exist")
        return

    fun = fname.split('_v')[0]
    mfile_path = os.path.join(fpath, mname + ".py")
    fun_def = f'''
def {fun}(*args):
    fun = importlib.import_module("{fname}","{fpath}")
    fun.load()
    return fun.call(*args)
    '''

    print("function  is :", fun_def)
    pattern = fr'{fun}_v\d+'
    # Check if module file exists
    if os.path.isfile(mfile_path):
        with open(mfile_path, 'r') as f:
            file_content = f.read()
            # Use regex to match function definition
            if re.search(fr'def {fun}\(.*?\):', file_content):
                print("function already exists")
                return
            elif re.search(fr'def {fun}_v\d+\(.*?\):', file_content):
                # If function with same name but different version exists, update the import statement
                updated_content = re.sub(r'importlib\.import_module\("{}.*?"'.format(pattern),
                                        f'importlib.import_module("{fname}"',
                                        file_content,
                                        flags=re.DOTALL)
                print("function was updated")
            else:
                # If function with same name does not exist, append the function definition
                updated_content = file_content + fun_def

            with open(mfile_path, 'w') as file:
                file.write(updated_content)
                print("function was updated")
            
            return

    # If module file does not exist, it's created with the import statement at the top
    # If it exists, the function is appended
    exists = os.path.exists(mfile_path)
    with open(mfile_path, 'a' if os.path.exists(mfile_path) else 'w') as f:
        if not exists:
            f.write("import importlib\n")
            f.write("import sys\n")
            f.write(f"module_directory = \"{fpath}\"\n")
            f.write("sys.path.append(module_directory)\n\n")
        f.write(fun_def)

#TODO: make this function
def make_installable(fpath, mname):pass 

def python_header_path():
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    possible_locations = [
        f"/usr/include/python{python_version}",
        f"/usr/local/include/python{python_version}"
    ]

    for location in possible_locations:
        if os.path.exists(location):
            return location
        
def pybind11_header_path():
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    possible_locations = [
        "/usr/include/pybind11",
        "/usr/local/include/pybind11",
        f"/home/{os.getlogin()}/.local/lib/python{python_version}/site-packages/pybind11"
        # Add more possible locations if needed
    ]

    for location in possible_locations:
        if os.path.exists(location):
            loc = str(location)+"/include"
            return loc
    # if not able to find pybind11, throw error
    raise Exception("pybind11 not found")



    

        
