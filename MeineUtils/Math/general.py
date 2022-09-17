def isfloat(num):
    if int(num) - num == 0:
        return False
    else:
        return True

def isfloatfromstring(num):
    try:
        float(num)
        return True
    except ValueError:
        return False