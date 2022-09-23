import math

def Mean(x):
    return sum(x) / len(x)

def StandardDeviation(x):
    return math.sqrt(sum((x - Mean(x)) ** 2) / len(x))