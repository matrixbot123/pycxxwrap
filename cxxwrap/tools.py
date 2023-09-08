import os,re,sys
import inspect

class create_nametype:
    
    def __init__(self):
        self.type_names = {}

    def __getitem__(self, key):
        return self.type_names[key]
    
    class basic_type:
        def __init__(self, name=None):
            if name is not None:
                self.full_name = name


    class template_type:
        def __init__(self, name=None):
            if name is not None:
                self.full_name = name

        def __getitem__(self, a):
            pass

        def __getslice__(self, *a):
            pass

    
    def create_type(self, name, alt=None, is_template=False):
        assert name is not None
        
        if alt is not None:
            self.type_names[name] = alt
        else:
            self.type_names[name] = name

        stack = inspect.stack()
        if 1 < len(stack):
            index = 1
        else:
            index = 0
        
        if is_template:
            stack[index][0].f_globals[name] = self.template_type(name)
        else:
            stack[index][0].f_globals[name] = self.basic_type(name)



class set_args:
    def __init__(self, *kargs, **kwargs):
        self.flags = kwargs.get("flags", "-std=c++17")
        self.lib_path = kwargs.get("lib_path", False)
        self.module_name = kwargs.get("module_name", False)
        # Here you are embedding the create_nametype class instance into set_args. You can access the methods and attributes using this object.
        self.create_nametype = create_nametype()

    def create_type(self, name, alt=None, is_template=False):
        self.create_nametype.create_type(name, alt, is_template)
    @property
    def is_type_names_empty(self):
        return self.create_nametype.is_empty

        
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
    print(fname)
    pattern = fr'{fun}_v\d+'
    # Check if module file exists
    if os.path.isfile(mfile_path):
        with open(mfile_path, 'r') as f:
            file_content = f.read()
            # Use regex to match function definition
            
            updated_content = re.sub(r'importlib\.import_module\("{}.*?"'.format(pattern),
                                    f'importlib.import_module("{fname}"',
                                    file_content,
                                    flags=re.DOTALL)

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
        f.write(fun_def)


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



    

        

