#!/usr/bin/env python
#
import sys

## hw3.py, to find whether Zn might be a field or a commutative ring

def MI(num, mod):
    '''
    This function uses ordinary integer arithmetic implementation of the
    Extended Euclid's Algorithm to find the MI of the first-arg integer
    vis-a-vis the second-arg integer.
    '''
    NUM = num; MOD = mod
    x, x_old = 0L, 1L
    y, y_old = 1L, 0L
    while mod:
        q = num // mod
        num, mod = mod, num % mod
        x, x_old = x_old - q * x, x
        y, y_old = y_old - q * y, y
    if num != 1:
        return 0
    else:
        MI = (x_old + MOD) % MOD
        return MI


def main():
    Fp = open("output.txt","w")
    n = 0
    while n <= 0:
        n = raw_input("\nPlease enter a number greater than 0: ")
        if n <= 0:
            print "You have entered an invalid digit.\n"
    n = int(n)  ## converting string to int
    for i in range (1,n):
        if MI(i,n) == 0:
            Fp.write("Ring")
            exit (0)
    Fp.write("Field")
    Fp.close()
    exit(0)

if __name__ == "__main__":
    main()



