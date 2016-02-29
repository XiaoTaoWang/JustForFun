# -*- coding: utf-8 -*-
"""
Created on Mon Feb 29 20:58:03 2016

@author: wxt
"""
import numpy as np
# Brute forcing
def sumfactors(num):
    
    result = 1
    maxiter = int(np.sqrt(num))
    if maxiter ** 2 == num:
        result += maxiter
        maxiter -= 1
        
    for i in xrange(2, maxiter+1):
        if num % i == 0:
            result += (i + num / i)
    
    return result

def brutefind(maxnum):
    
    pairs = []
    storage = set()
    for num in xrange(2, maxnum+1):
        if num in storage:
            continue
        sf = sumfactors(num)
        if num < sf <= maxnum:
            check = sumfactors(sf)
            if check == num:
                pairs.append((num, sf))
                storage.add(sf)
    
    return pairs
    

# Prime Fractorization
def findallprimes(maxnum):
    
    ori = np.arange(1, maxnum+1)
    Bool = np.ones(maxnum, dtype = bool)
    Bool[0] = 0
    maxiter = int(np.sqrt(maxnum))
    for i in xrange(2, maxiter+1):
        if Bool[i-1]:
            # Sieve of Eratosthenes
            Bool[np.arange(2*i-1, maxnum, i)] = False
    
    return ori[Bool]

def sumbyprimes(num, primelist):
    
    n = num
    result = 1
    p = primelist[0]
    count = 0
    while (p * p <= n) and (n > 1) and (count < primelist.size):
        p = primelist[count]
        count += 1
        if n % p == 0:
            j = p * p
            n /= p
            while n % p == 0:
                j *= p
                n /= p
            result *= ((j - 1) / (p - 1))
            
    if n > 1:
        result *= (n + 1)
    
    return result - num

def cleverfind(maxnum):
    
    primelist = findallprimes(int(np.sqrt(maxnum)))
    pairs = []
    storage = set()
    for num in xrange(2, maxnum+1):
        if num in storage:
            continue
        sf = sumbyprimes(num, primelist)
        if num < sf <= maxnum:
            check = sumbyprimes(sf, primelist)
            if check == num:
                pairs.append((num, sf))
                storage.add(sf)
    
    return pairs
