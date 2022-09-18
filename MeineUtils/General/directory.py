import os
from .decorator import _list
from .general import path_join

@_list
def mkdir(dir_list):
    for dir in dir_list:
        dirs = []
        while True:
            if not os.path.exists(dir) and dir != '':
                arr = os.path.normpath(dir).split(os.sep)
                dirs.insert(0, arr[-1])
                dir = path_join(arr[:-1])
            else:
                for i in range(len(dirs)):
                    os.mkdir(path_join([dir, dirs[:i+1]]))
                break