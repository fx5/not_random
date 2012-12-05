N = 624
M = 397
MATRIX_A = 0x9908b0df

def y(y):
    y ^= (y >> 11)
    y ^= (y << 7) & 0x9d2c5680
    y ^= (y << 15) & 0xefc60000
    y ^= (y >> 18)
    return y

def random_random(a,b):
    a=a>>5
    b=b>>6;
    return (a*67108864.0+b)*(1.0/9007199254740992.0)
