<h1 style="text-align: center;">Pycxxwrap</h1>

## Getting Started
Pycxxwrap is a tool for generating Python bindings for C++ code and libraries. It is designed to be easy to use and to provide a high level of control over the generated bindings.

### Installation
Pycxxwrap is not yet available on PyPI .So you can install it from source code :

```bash
git clone https://github.com/matrixbot123/pycxxwrap
cd pycxxwrap
pip install .
```

### Hello World !
Let's start with a simple example. Suppose we have a C++ library with the following header file:

```cpp
// hello.hpp
#include <iostream>

int main() {
    std::cout << "Hello World!" << std::endl;
    return 0;
}
```

We can generate same Python bindings for this function as shown below:

```python
from pycxxwrap.pycxx import py11

@py11(headers=["<iostream>"])
def hello()->None:
    """
    std::cout << "Hello world!"<<std::endl;
    """

hello()
```
>Note : The `@py11` decorator is used to indicate that the function should be wrapped. The `headers` argument specifies the headers that should be included in the generated code and namespaces should be specified 

For more reference examples please see [Examples](../Examples) folder