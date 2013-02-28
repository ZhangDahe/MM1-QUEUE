'''
NumberGenerator

Created on Feb 14, 2013
@author: adrielklein
'''
import math
import random
import numpy

def exponentialValue(Lambda):
    y = random.uniform(0,1)
    return -math.log(1-y)/Lambda
'''
Returns a random value according to standard normal distribution.
'''
def Zrand():
    uniformValues = [random.uniform(0,1) for x in range(30)]
    # X is a random variable that follows a standard normal distribution
    X = sum(uniformValues)
    meanX = 15
    varianceX = 30/12
    # Z is a random variable that follows a standard normal distribution. 
    Z = (X - meanX)/math.sqrt(varianceX)
    return Z

'''
Returns a random value according to a normal distribution with mean U and standard deviation S
'''
def Grand(U,S):
    return Zrand()*S + U
    
    
    