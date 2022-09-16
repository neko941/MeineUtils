import random

class TXT():
    def __init__(self, file_name):
        self.file_name = file_name
        self.data = list()
    
    def read(self, remove_new_line_char=True, encoding=None):
        for line in open(file=self.file_name, mode='r', encoding=encoding).readlines():
            if remove_new_line_char:
                line = line.replace('\n', '')
            self.data.extend(line)
        return self
    
    def write(self, new_line_char=True, mode='w', encoding=None):
        with open(file=self.file_name, mode=mode, encoding=encoding) as fp:
            for item in self.data:
                if new_line_char: fp.write(f"{item}\n")
                else: fp.write(f"{item}")
        return self
    
    def add_data(self, data):
        self.data.extend(data)
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

# def txt_to_list(file_name, remove_duplicate=False, remove_new_line_char=True, shuffle=False, sort=None):
#     lines = []
#     for line in open(file_name, 'r').readlines():
#         if remove_new_line_char:
#             line = line.replace('\n', '')
#         lines.append(line)
#     if remove_duplicate: lines = list(set(lines))
#     if shuffle: random.shuffle(lines)
#     if sort != None:
#         if sort.lower() in ['ascending', 'asc']: lines.sort()
#         elif sort.lower() in ['descending', 'desc']: lines.sort(reverse=True)
#     return lines

# def list_to_txt(file, data, new_line_char=True, shuffle=False, sort=None):
#     if shuffle: random.shuffle(data) 
#     with open(file, 'w') as fp:
#         for item in data:
#             if new_line_char: fp.write(f"{item}\n")
#             else: fp.write(f"{item}")