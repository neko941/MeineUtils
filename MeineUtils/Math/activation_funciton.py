import numpy as np

def ReLU_base(x, alpha1, alpha2):
    return alpha1 * np.minimum(0, x) + alpha2 * np.maximum(0, x)

def ReLU(x):
    """ 
    Rectified Linear Unit
    f(x) = max(0, x)
    """
    return ReLU_base(x, 0, 1)

def PReLU(x):
    """
    Parametric ReLU
    """
    return ReLU_base(x, 0.25, 1)

def LeakyReLU(x):
    return ReLU_base(x, 0.01, 1)