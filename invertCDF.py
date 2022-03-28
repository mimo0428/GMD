import math
import random

def inverseCDF():
    """
    return the x value in PDF
    """
    uniform_random = random.random()
    return inverse_cdf(uniform_random)


def pdf(x):
    return 2 * x

# cdf = x^2, 其逆函数很好求，因此直接用公式法
def inverse_cdf(x):
    return math.sqrt(x)

def getRamdomNumber():
    x = inverseCDF()
    return round(x,2)

