import random

def file_txt_to_list(file_name, duplicate=False, remove_new_line_char=True, shuffle=False, sort=None):
    lines = []
    for line in open(file_name, 'r').readlines():
        if remove_new_line_char:
            line = line.replace('\n', '')
        lines.append(line)
    if duplicate: lines = list(set(lines))
    if shuffle: random.shuffle(lines)
    if sort != None:
        if sort.lower() in ['ascending', 'asc']: lines.sort()
        elif sort.lower() in ['descending', 'desc']: lines.sort(reverse=True)
    return lines