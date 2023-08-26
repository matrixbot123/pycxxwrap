import os
from subprocess import Popen, PIPE
import re
import sys
import inspect
import ast
from termcolor import colored
from .load_function import load_func
from .utils import get_args, write_src, fcall , prompts, create_dir
from .tools import write_module , python_header_path, pybind11_header_path


python_header = python_header_path()
pybind11_header = pybind11_header_path()
print(pybind11_header)
print(python_header)
flags = "-std=c++17"


if type(sys.stdout).__module__ == 'ipykernel.iostream' and type(sys.stdout).__name__ == 'OutStream':
    is_jupyter = True
else:
    is_jupyter = False


def set_flags(f):
    global flags
    flags = f   


class py11:

    def __init__(self, *kargs, **kwargs):

        self.recompile = kwargs.get("recompile", False)
        self.headers = kwargs.get("headers", [])

        self.module_name = kwargs.get("module_name", False)
        self.lib_path = kwargs.get("lib_path", False)
        self.sub_module_name = kwargs.get("sub_module_name", False)
        
        fun_decls = ""
        fun_calls = ""
        funs_list = []

        if "funs" in kwargs:
            funs_list += kwargs["funs"]

        if "wrap" in kwargs:
            wrapper = kwargs["wrap"]
            assert wrapper is not None
            funs_list.append(wrapper)
            self.wrapper = wrapper
        else:
            self.wrapper = None
        path = create_dir(self.lib_path)
        print(path)
        new_load_func = load_func.replace("lib_path", f'"{path}"')
        print(new_load_func)
        if len(funs_list)>0:
            fun_decls += new_load_func
            for f in funs_list:
                fun_decls += f"typedef {f.rettype}(*{f.fun_name}_type_def)({f.args_decl});\n"
                fun_decls += f"{f.fun_name}_type_def {f.fun_name} = nullptr;\n"
                fun_calls += f'{f.fun_name} = ({f.fun_name}_type_def)load_func("{f.fun_name}");\n'

        print("fun_decls = ", fun_decls)
        print("fun_calls = ", fun_calls)

        self.fun_decls = fun_decls
        self.fun_calls = fun_calls

    def __call__(self, fun):
        # Naming the filename and libname
        # function name module name and its path 
        print(self.lib_path)
        if self.lib_path:
            print(self.lib_path)
            path = create_dir(self.lib_path)
            print(path)
            base = os.path.join(str(path), fun.__name__ )
            print(base)
        else:
            base = os.path.join("~/tmp", fun.__name__)
            print(base)
        if not os.path.exists(self.lib_path):
            path = create_dir(self.lib_path)
            os.makedirs(os.path.dirname(path), exist_ok=True)
        


        # AST (Abstract Syntax Tree) Parsing 
        src = inspect.getsource(fun)
        tree = ast.parse(src)
        args, oargs, cargs, rettype = get_args(tree)
        
        code = ""
        fname = base+'.cpp'
        mname = base+'.so.txt'

        version = self.__get_version(mname)
        suffix = "_v"+str(version)
        libname = base+suffix+'.so'
        

        src = self._call_write_src(fun,rettype,args,oargs,cargs,suffix)

        if os.path.exists(fname):
            code = open(fname).read()
        
        # Recompile case
        if code != src or self.recompile or not os.path.exists(libname):
            old_file = base + suffix + '.so'
            if os.path.exists(old_file):
                os.remove(old_file)
            version += 1
            suffix = "_v"+str(version)
            base += suffix

            src = self._call_write_src(fun,rettype,args,oargs,cargs,suffix)

            with open(mname, "w") as fd:
                print(version, file=fd)

            with open(fname, "w") as fd:
                fd.write(src)
                
            if not self.__execute_compilation(base,fname,fun,suffix):
                if os.path.exists(base+".so"):
                    os.remove(base+".so")
                return None


        return fcall(base, fun.__name__, suffix, args, rettype,self.lib_path)
        
    def _call_write_src(self,fun,rettype,args,oargs,cargs,suffix):
        return write_src(
            name=fun.__name__+suffix,
            raw_name=fun.__name__,
            wrap_name=fun.__name__,
            wrapper=self.wrapper,
            body=fun.__doc__,
            headers='\n'.join(['#include '+h for h in self.headers]),
            rettype=rettype,
            args=args,
            oargs=oargs,
            cargs=cargs,
            fun_decls=self.fun_decls,
            fun_calls=self.fun_calls
        )
    def __get_version(self, mname):
        if os.path.exists(mname):
            with open(mname, "r") as fd:
                return int(fd.read().strip())
        else:
            return 0



    def __execute_compilation(self, base, fname,fun,suffix):
        prompts("started executing compilation ....")
        cmd = "c++ -Wl,--start {flags} -I{python_header} -I{pybind11_header} -rdynamic -fPIC -shared -o {base}.so {fname} -Wl,--end".format(
                    base=base, python_header=python_header, pybind11_header=pybind11_header, flags=flags, fname=fname)

        try:
            split_cmd = re.split(r'\s+', cmd)
            proc = Popen(split_cmd, stdout=PIPE, stderr=PIPE,universal_newlines=True)
            outs, errs = proc.communicate()
            if proc.poll() != 0:
                print("Compilation failed")
                print(outs) # assume stdout should not be colored
                print(colored(errs, "red"))  # assuming `colored` is a function
                return False
            if self.module_name and self.lib_path:
                write_module(fun.__name__+suffix, self.lib_path, self.module_name)
        except Exception as e:
            print(e)
            print("Exception raised during compilation")
            return False
        prompts("finished executing compilation")
        return True
    
  