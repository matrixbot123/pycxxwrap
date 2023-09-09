import inspect
type_names = {}


class basic_type:
    def __init__(self,name=None):
        if name is not None:
            self.full_name = name


class template_type:
    def __init__( self, name=None):
        if name is not None:
            self.full_name = name

    def __getitem__( a):
        pass

    def __getslice__( *a):
        pass


def create_type(name, alt=None, is_template=False):
    assert name is not None
    global type_names
    if alt is not None:
        type_names[name] = alt
    else:
        type_names[name] = name

    stack = inspect.stack()
    if 1 < len(stack):
        index = 1
    else:
        index = 0
    
    if is_template:
        stack[index][0].f_globals[name] = template_type(name)
    else:
        stack[index][0].f_globals[name] = basic_type(name)

