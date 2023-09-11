load_func = """
#include <dlfcn.h>
#include <fstream>
#include <sstream>
#include <stdlib.h>
#include <unistd.h>
#include <assert.h>

static inline void *load_func(const char *fun) {
    std::ostringstream fname;
    fname << lib_path << "/" << fun << ".so.txt";
    std::string so_txt = fname.str();

    std::ifstream in;
    in.open(so_txt.c_str());
    assert(in.good());

    std::string ver;
    in >> ver;

    std::ostringstream fun2;
    fun2 << fun << "_v" << ver;

    std::ostringstream lib;
    lib << lib_path << "/" << fun2.str() << ".so";
    in.close();
    in.open(lib.str().c_str());
    assert(in.good());
    in.close();

    void *handle = dlopen(lib.str().c_str(), RTLD_LAZY);
    return dlsym(handle, fun);
}
"""