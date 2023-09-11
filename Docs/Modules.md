# Overview
Pycxxwrap being  very simple tool to use , it has only 3 modules :
* pycxx
* tools
* types

## pycxx
* py11 \
The main decorator used to indicate that the function should be wrapped.
> Parameters
> * `headers` : The headers that should be included in the generated code
> * `recompile` : If `True` then the generated code will be recompiled
> * `wrap` : The wrapper function that should be used to wrap the function
> * `args` : The flags that should be passed to the compiler , where the module is being compiled and it's name

### > usage
```python
from pycxxwrap.pycxx import py11

@py11(headers=["<iostream>"],recompile=True,args=["-std=c++17"])
def fun()->None:
    """
    Cxx code here
    """
```
## tools
* set_args \
This function is used to set the arguments that should be passed to the compiler , where the module is being compiled and it's name
> Parameters
> * `flags`: The flags that should be passed to the compiler .
> * `module_name`: The name of the module.
> * `lib_path`: The path where the library is located.(It recommended to use absolute path.)

> Note : This function should be called before any `@py11` decorator
 ### > usage
 This is the basic template for using pycxxwrap with hpx runtime environment this path `-I/home/matrix/GSoc/ipyhpx` points to [`hpx_run.cpp`](../run_hpx.cpp) file and this path `-I/home/matrix/pyhpx/release_hpx/hpx/cmake_install/include` points to the hpx library.
 please change the paths according to your system.
 ```python

from pycxxwrap.pycxx import py11
from pycxxwrap.tools import set_args

# set arguments for compilation and location you want to store the library
f = set_args(flags = """-std=c++17 -I/home/matrix/GSoc/ipyhpx 
          -I/home/matrix/pyhpx/release_hpx/hpx/cmake_install/include 
          -L/home/matrix/pyhpx/release_hpx/hpx/cmake_install/lib -lhpx 
          -Wl,-rpath=/home/matrix/pyhpx/release_hpx/hpx/cmake_install/lib""",
          lib_path="./hello_hpx",
          module_name="hpx_example")

# create wrapper for hpx runtime envirnmnet
@py11(headers=["<run_hpx.cpp>","<iostream>"],args=f)
def hpx_wrapper(f : func)->None:
    """
    const char *num = getenv("HPX_NUM_THREADS");
    int num_threads = num == 0 ? 4 : atoi(num);
    std::cout << "Using " << num_threads << " threads." << std::endl;
    hpx_global::submit_work(num_threads,f);
    """
```
Above the location where all .so files will be store is `./hello_hpx` and the module name is `hpx_example` and the flags are passed to the compiler.

## types
* create_type \
This function is used to create your own types which are not in python  and add to python global namespace. List is maintained in `type_names` dictionary for the `py11` decorator to use.
> Parameters
> * `name`: The name of the type.
> * `alternate`: the original type that should be used to create the new type.
> * `is_template`: If `True` then the type is a template type.(only set true for places where slicing and indexing is required)

> Note : This function should be called before any `@py11` decorator
 ### > usage
 ```python
create_type("func","std::function<void()>")
create_type("svec","std::vector",True)
```