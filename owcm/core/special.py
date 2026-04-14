import numpy as np
import scipy.special as sp

# Adapters for common special functions
# This allows us to swap backend later if needed (e.g. to mpmath for high precision)

def erf(x):
    return sp.erf(x)

def gamma(x):
    return sp.gamma(x)

def besselk(nu, z):
    return sp.kv(nu, z)
