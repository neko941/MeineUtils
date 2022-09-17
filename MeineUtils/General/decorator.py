def _list(func):
    def wrap(a):
        if isinstance(a, list):
            retval = func(a)
        else:
            retval = func([a])
        return retval
    return wrap
