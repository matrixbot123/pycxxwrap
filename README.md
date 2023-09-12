# PyCxxwrap
This package aims to facilitate the integration of CXX library functionality into Python. It was created because some libraries are not directly compatible with pybind11, such as HPX, due to the Global Interpreter Lock (GIL).

The main goal of this project is to provide an easy interface to CXX libraries in Python without introducing any significant overhead. However, there are some drawbacks, one of which is the lack of support for converting CXX classes and structs to Python. This limitation may not be a significant issue since most CXX libraries primarily consist of functions rather than classes or structs.
It Currently only supports Linux and MacOs. Windows support will be added in future.
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
For more details on how the above code works please refer to the [Docs](./Docs).

<!-- to do in future -->
## Future Plans
1. Add proper support for CXX classes and structs
2. Update or rewrite [run_hpx](./run_hpx.cpp) 
