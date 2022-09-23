import os
import re
import time

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

class Sleep():
    def __init__(self):
        self.seconds = 0
        self.minutes = 0
        self.hours = 0
        self.days = 0
        self.time = ''

    def increasement(self):
        self.seconds += 1

        if self.seconds >= 60:
            self.seconds -= 60
            self.minutes += 1
        
        if self.minutes >= 60:
            self.minutes -= 60
            self.hours += 1

        if self.hours >= 60:
            self.hours -= 60
            self.days += 1     

        self.time = ''

        if 0 < self.days < 10: self.time += f"0{self.days}d"  
        if self.days > 10: self.time += f"{self.days}d" 

        if 0 < self.hours < 10: self.time += f"0{self.hours}h"      
        if self.hours > 10: self.time += f"{self.hours}h"

        if 0 < self.minutes < 10: self.time += f"0{self.minutes}m"  
        if self.minutes > 10: f"{self.minutes}m" 

        if 0 < self.seconds < 10: self.time += f"0{self.seconds}s"
        if self.seconds > 10: self.time += f"{self.seconds}s"

        return self 

    def sleep(object):
        try:
            while(True):
                time.sleep(1)
                object.increasement()
                print("", end=f"\rSleeping... {object.time}")
        except KeyboardInterrupt:
            print(f"\n\nKeyboard Interruption")
            return object
            pass