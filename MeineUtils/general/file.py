import random
from general import flatten_list

class TXT():
    def __init__(self, file_name):
        self.file_name = file_name
        self.data = []
    
    def read(self, remove_new_line_char=True, encoding=None):
        for line in open(file=self.file_name, mode='r', encoding=encoding).readlines():
            if remove_new_line_char:
                line = line.replace('\n', '')
            self.data.extend(flatten_list(line))
        return self
    
    def write(self, new_line_char=True, mode='w', encoding=None):
        with open(file=self.file_name, mode=mode, encoding=encoding) as fp:
            for item in self.data:
                if new_line_char: fp.write(f"{item}\n")
                else: fp.write(f"{item}")
        return self
    
    def add_data(self, data):
        self.data.extend(flatten_list(data))
        return self
    
    def drop_duplicate(self):
        assert len(self.data)==0, 'No data'
        self.data = list(set(self.data))
        return self

    def shuffle(self):
        self.data = random.shuffle(self.data)
        return self

    def sort(self, order=None):
        if order != None:
            if order.lower() in ['ascending', 'asc']: self.data.sort()
            elif order.lower() in ['descending', 'desc']: self.data.sort(reverse=True)
        return self