from setuptools import setup, find_packages

setup(
    name="cxxwrap",
    version="0.0.1",
    description="Tool used to warpping CXX code in python",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    author="Shubham Kumar",
    author_email="shyubhamr@gmail.com",
    license="Boost Software License 1.0 (BSL-1.0)",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Operating System :: POSIX :: Linux",
        "License :: OSI Approved :: Boost Software License 1.0 (BSL-1.0)",
        "Programming Language :: Python :: 3",
    ],
    keywords=[
        "CXX Code warpping",
        "Custom CXXtypes in python",
    ],
    packages=find_packages(),
    install_requires=["pybind11", "numpy", "IPython", "colorama", "termcolor"],
    python_requires=">=3.10",
)
