import os
import re
from .decorator import _list

@_list
def flatten_list(alist):
    flattened_list = []
    for element in alist:
        if isinstance(element, list):
            flattened_list.extend(flatten_list(element))
        else:
            flattened_list.append(element)
    return flattened_list

@_list
def path_join(alist):
    if len(alist) != 0:
        temp = flatten_list(alist)
        if temp[0] == '':
            return os.sep + os.path.join(*temp)
        else:
            return os.path.join(*temp)
    else:
        return ''

def split(text, delimiters, maxsplit=0, flags=0, strip=True, keep_delimiter=False, remove_empty=True, join_char=None):
    if keep_delimiter:
        regex_pattern = '|'.join('(?<={})'.format(re.escape(delim)) for delim in delimiters)
    else:
        regex_pattern = '|'.join(map(re.escape, delimiters))

    new = re.split(pattern=regex_pattern,
                   string=text, 
                   maxsplit=maxsplit,
                   flags=flags)

    if strip: new = [element.strip() for element in new]
    if remove_empty: new = [a for a in new if a!='']

    if join_char != None:
        assert keep_delimiter==False, 'Will return the original text'
        new = join_char.join(new)
    
    return new