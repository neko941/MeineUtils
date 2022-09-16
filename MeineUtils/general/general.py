def flatten_list(alist):
    flattened_list = []
    if isinstance(alist, list):
        for element in alist:
            if isinstance(element, list):
                flattened_list.extend(flatten_list(element))
            else:
                flattened_list.append(element)
    else:
        flattened_list.append(alist)
    return flattened_list