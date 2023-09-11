# PyCxxwrap
This Package aims to help bring any CXX library functionality to python . This is created becasue some libraries are not directly compatible with pybind11 (like HPX ) due to GIL . 

So , the main goal of this project is an easy interface to CXX libraries in python without any overhead. But ease come some drawbacks , one of those is not having support for class and struct from CXX to python .This is not a big problem as most of the CXX libraries are just a bunch of functions and not classes or structs .

## Installation
Currently the package is not in pypi you just need to clone the repo , and install it using pip then it is ready to use
```bash
git clone https://github.com/matrixbot123/pycxxwrap
pip install .
```

## Usage

1.  Simple Hello World example

```python
from pycxxwrap.pycxx import py11

@py11(headers=["<iostream>"])
def hello()->None:
    """
    std::cout << "Hello world!"<<std::endl;
    """
hello()
```
2. A more complex example
```python
from pycxxwrap.pycxx import py11
from pycxxwrap.types import type_names, create_type
from pycxxwrap.tools import set_args

# set arguments for compilation and location you want to store the library
f = set_args(flags = """-std=c++17 -I/home/matrix/GSoc/ipyhpx 
          -I/home/matrix/pyhpx/release_hpx/hpx/cmake_install/include 
          -L/home/matrix/pyhpx/release_hpx/hpx/cmake_install/lib -lhpx 
          -Wl,-rpath=/home/matrix/pyhpx/release_hpx/hpx/cmake_install/lib""",
          lib_path="./hello_hpx",
          module_name="hpx_example")

# Create your own types
create_type("func","std::function<void()>")

# create wrapper for hpx runtime envirnmnet
@py11(headers=["<run_hpx.cpp>","<iostream>"],args=f)
def hpx_wrapper(f : func)->None:
    """
    const char *num = getenv("HPX_NUM_THREADS");
    int num_threads = num == 0 ? 4 : atoi(num);
    std::cout << "Using " << num_threads << " threads." << std::endl;
    hpx_global::submit_work(num_threads,f);
    """
@py11(headers=["<hpx/hpx.hpp>"],wrap=hpx_wrapper,args=f)
def do_future()->None:
    """
    std::cout << "Hello, World!" << std::endl;
    auto f = hpx::async([](){ return 5; });
    std::cout << "f=" << f.get() << std::endl;
    """
do_future()


```
We are setting up the flags and library path for the hpx library and then we are creating a wrapper for the hpx runtime environment. Then passing the do_future function to the wrapper.
The above do_future function is equivalent to the following c++ code. Here main() starts the hpx runtime environment by default.
```c++
#include <hpx/hpx.hpp>
#include <iostream>
int main()
{
    std::cout << "Hello, World!" << std::endl;
    auto f = hpx::async([](){ return 5; });
    std::cout << "f=" << f.get() << std::endl;
}
``` 
For more details on how the above code works please refer to the Docs.

<!-- to do in future -->
## 