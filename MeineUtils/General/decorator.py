import platform
import contextlib

def _list(func):
    def wrap(a):
        if isinstance(a, list):
            retval = func(a)
        else:
            retval = func([a])
        return retval
    return wrap

class TryExcept(contextlib.ContextDecorator):
    """
    Example:
    @TryExcept('⚠️ nani the fck: ')
    def calculate(x):
        return x/0
    """
    def __init__(self, msg=''):
        self.msg = msg

    def __enter__(self):
        pass

    def emojis(self, str=''):
        """
        Return platform-dependent emoji-safe version of string
        """
        return str.encode().decode('ascii', 'ignore') if platform.system() == 'Windows' else str

    def __exit__(self, exc_type, value, traceback):
        if value:
            print(self.emojis(f'{self.msg}{value}'))
        return True