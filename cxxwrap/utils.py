# utils.py
import os 
import re
import sys
import inspect
import ast
import numpy as np
import importlib
from termcolor import colored
from .load_function import load_func
from colorama import Fore, Style, init
from IPython.display import Markdown, display
from .tools import default_dir
from .types import type_names


if type(sys.stdout).__module__ == 'ipykernel.iostream' and type(sys.stdout).__name__ == 'OutStream':
    is_jupyter = True
else:
    is_jupyter = False 

init()
def prompts(a):
    if is_jupyter:
        display(Markdown(f'<span style="color:red">{a}</span>'))
    else :
        print(a)


def ttran(n):
    s = ''
    for match in re.finditer(r'[\w\.]+|.', n):
        s += {
            "np.float32": "std::float32_t",
            "np.float64": "std::float64_t",
            "np.int64": "std::int64_t",
            "str": "std::string",
            "None": "void",
            "List": "std::vector",
            "Dict": "std::map",
            "[": "<",
            "]": ">"
        }.get(match.group(0), match.group(0))
    print("type translation" ,s)
    return s

def gettype(ty):
    if ty is None:
        return "None"
    t = type(ty)
    if t == ast.Name:
        if ty.id in type_names.keys():
            return type_names[ty.id]
        return ty.id
    elif t in [np.float64]:
        return str(t)
    elif t in [ast.Index, ast.NameConstant]:
        return gettype(ty.value)
    elif t in [ast.Attribute]:
        return gettype(ty.value) + "." + gettype(ty.attr)
    elif t == ast.Subscript:
        return gettype(ty.value) + '[' + gettype(ty.slice) + ']'
    elif t == ast.Tuple:
        s = ''
        sep = ''
        for e in ty.elts:
            s += sep + gettype(e)
            sep = ','
        return s
    elif t == ast.Call:
        if ty.func.id == "Ref":
            return "%s&" % gettype(ty.args[0])
        elif ty.func.id == "Const":
            return "%s const" % gettype(ty.args[0])
        elif ty.func.id == "Move":
            return "%s&&" % gettype(ty.args[0])
        elif ty.func.id == "Ptr":
            return "%s*" % gettype(ty.args[0])
        else:
            s = ty.func.id + "<"
            for i in len(ty.args):
                if i > 0:
                    s += ","
                arg = ty.args[i]
                s += gettype(arg)
            s += ">"
            return s
        
    elif type(ty) == str:
        print("type is str",ty)
        raise Exception("?")
    
    elif type(ty) == ast.Constant:
        if ty.value is None:
            return "void"
        else:
            raise Exception()
        
    else:
        print(ty.func.id)
        print(ty.args, "//", dir(ty.args[0]))
        print(ty.args[0].s, ty.args[1].id)
        print("<<", ty.__class__.__name__, ">>", dir(ty))
        raise Exception("?")

def get_args(function):
    src = inspect.getsource(function)
    tree = ast.parse(src)

    def g_args(tree):
        nm = tree.__class__.__name__
        if nm in ["Module"]:
            for k in tree.body:
                args = g_args(k)
                if args is not None:
                    return args

        elif nm in ["FunctionDef"]:
            args = []
            cargs = []
            oargs = ""
            for a in tree.args.args:
                type = ttran(gettype(a.annotation))
                args += [type+" "+a.arg]
                oargs += ',py::arg("%s")' % a.arg
                cargs += [a.arg]
                #oargs += ','+type
            return [",".join(args), oargs, cargs, ttran(gettype(tree.returns)) ]

        raise Exception("In get_args() : Could not find args")
    return g_args(tree)
    

class fcall:
    def __init__(self,base,fun_name,suffix,args,rettype,lib_path):
        self.base = base
        self.fun_name = fun_name
        assert not re.match(r'.*_v\d+$',fun_name), fun_name
        self.suffix = suffix
        self.args_decl = args
        self.rettype = rettype
        self.lib_path = lib_path
 
        if self.lib_path:
            if lib_path not in sys.path:
                sys.path += [lib_path]
            self.path = self.lib_path
            fpath = os.path.join(lib_path,fun_name+suffix+".so")
            self.m = importlib.import_module(fun_name+suffix,fpath)
        else :
            if default_dir() not in sys.path:
                sys.path += [default_dir()]
            self.path = default_dir()
            fpath = os.path.join(default_dir(),fun_name+suffix+".so")
            self.m = importlib.import_module(fun_name+suffix,fpath)
        print("The path where .so goes",self.path)


    def __call__(self,*args):
        self.m.load()
        if is_jupyter:
            try:
                outfile = os.path.join(self.path,"out.txt")
                fd1 = open(outfile, "w")
                save_out = os.dup(1)
                os.close(1)
                os.dup(fd1.fileno())

                errfile = os.path.join(self.path,"err.txt")
                fd2 = open(errfile, "w")
                save_err = os.dup(2)
                os.close(2)
                os.dup(fd2.fileno())

                return self.m.call(*args)
            finally:
                fd1.close()
                os.close(1)
                os.dup(save_out)
                os.close(save_out)
                print(open(outfile,"r").read(),end='')

                fd2.close()
                os.close(2)
                os.dup(save_err)
                os.close(save_err)
                print(colored(open(errfile,"r").read(),"red"),end='')
        else:
            return self.m.call(*args)

# Create the basic source code
def write_src(**kwargs):

        wrapper = kwargs['wrapper']
        raw_name = kwargs["raw_name"]
        args = kwargs["args"]
        oargs = kwargs["oargs"]
        rettype = kwargs["rettype"]

        if wrapper is not None:
            cargs = kwargs["cargs"]
            call_args = "(" + ",".join(cargs) + ")"
            kwargs['wrap'] = wrap_src(
                f=raw_name,
                args=args,
                rettype=rettype,
                oargs=oargs,
                call_args=call_args,
                wrapper=wrapper.fun_name
            )
            kwargs['wrap_name'] = raw_name + "_wrapped"
        else:
            kwargs['wrap_name'] = raw_name
            kwargs['wrap'] = ''

        return """
                #include <pybind11/pybind11.h>
                #include <pybind11/stl.h>
                {headers}

                {fun_decls}

                namespace py = pybind11;

                extern "C" {rettype} {raw_name}({args}){{
                {body}
                }};

                {wrap}

                extern "C" void load_functions() {{
                    {fun_calls}
                }}

                PYBIND11_MODULE({name}, m) {{
                    m.def("load",load_functions,"function"),
                    m.def("call",{wrap_name},"function"{oargs});
                }}""".format(**kwargs)

def wrap_src(**kwargs):
    if kwargs["rettype"] == "void":
        src = """
                void {f}_wrapped({args}) {{
                    std::function<void()> f = [&](){{
                        {f}{call_args};
                    }};
                    {wrapper}(f);
                }}""".format(**kwargs)
        
    else:
        src = """
                {rettype} {f}_wrapped({args}) {{
                    {rettype} r;
                    std::function<void()> f = [&](){{
                        r = {f}{call_args};
                    }};
                    {wrapper}(f);
                    return r;
                }}""".format(**kwargs)
        
    return src

