import os,re


def add_func_a(fname, fpath, mname):
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


    

        

