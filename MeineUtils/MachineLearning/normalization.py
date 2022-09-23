from Math.statistics import Mean
from MeineUtils.Math.statistics import StandardDeviation

def MinMaxScaler(x):
    return (x - min(x)) / (max(x) - min(x))

def StandardScaler(x):
    return (x - Mean(x)) / StandardDeviation(x)