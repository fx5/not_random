"""
Implementation of the Mersenne Twister that keeps track of every bit-manipulation
"""

from util import *
from itertools import imap
import random

def _shiftr(v, anz):
    vor = [frozenset()] * anz
    return vor + v[:-anz]

def _shiftl(v, anz):
    vor = [frozenset()] * anz
    return v[anz:] + vor

def _xor(a, b):
    return [c.symmetric_difference(d) for c, d in zip(a, b)]

def _andint(v, mask):
    neu = []
    for i in xrange(32):
        if mask & (1 << (31 - i)):
            neu.append(v[i])
        else:
            neu.append(frozenset())
    return neu

class Twister(object):
    def __init__(self, offset=0):
        self.tw = []
        self.offset = offset
        pos = 0
        for i in xrange(N):
            self.tw.append([frozenset((i,)) for i in xrange(pos, pos+32)])
            pos += 32

    def getint32(self):
        mt = self.tw
        if self.offset >= N:
            # for (kk=0;kk<N-M;kk++)
            for kk in xrange(0, N-M):
                #y = (mt[kk]&UPPER_MASK)|(mt[kk+1]&LOWER_MASK);
                #mt[kk] = mt[kk+M] ^ (y >> 1) ^ mag01[y & 0x1UL];
                y = mt[kk][0:1]+mt[kk+1][1:]
                t = _andint([y[-1]] * 32, MATRIX_A)
                mt[kk] = _xor(_xor(mt[kk+M], _shiftr(y, 1)), t)

            #for (;kk<N-1;kk++)
            for kk in xrange(kk+1, N-1):
                #y = (mt[kk]&UPPER_MASK)|(mt[kk+1]&LOWER_MASK);
                #mt[kk] = mt[kk+(M-N)] ^ (y >> 1) ^ mag01[y & 0x1UL];
                y = mt[kk][0:1]+mt[kk+1][1:]
                t = _andint([y[-1]] * 32, MATRIX_A)
                mt[kk] = _xor(_xor(mt[kk+(M-N)], _shiftr(y, 1)), t)

            #y = (mt[N-1]&UPPER_MASK)|(mt[0]&LOWER_MASK);
            #mt[N-1] = mt[M-1] ^ (y >> 1) ^ mag01[y & 0x1UL];
            y = mt[N-1][0:1]+mt[0][1:]
            t = _andint([y[-1]] * 32, MATRIX_A)
            mt[N-1] = _xor(_xor(mt[M-1], _shiftr(y, 1)), t)

            self.offset = 0

        y = self.tw[self.offset]
        y = _xor(y, _shiftr(y, 11))

        t = _shiftl(y, 7)
        t = _andint(t, 0x9d2c5680)
        y = _xor(y, t)

        t = _shiftl(y, 15)
        t = _andint(t, 0xefc60000)
        y = _xor(y, t)

        y = _xor(y, _shiftr(y, 18))

        self.offset += 1        
        return y

if __name__ == "__main__":
    print "Verifying implementation..."
    twister = Twister()
    v = random.getrandbits(32)
    state = random._inst.getstate()[1]
    def getbit(i, state = state):
        return (state[i//32]>>(31 - i % 32))&1
    for byte in xrange(10000):
        print "Byte %d" % (byte)
        now_state = random._inst.getstate()[1]
        if byte % 625 == 0:
            falsch = False
            for p, bits in enumerate(twister.tw):
                for bn, bit in enumerate(bits):
                    #assert sum(imap(getbit, bit)) & 1 == getbit(bn + p * 32, now_state), (p, bn)
                    if sum(imap(getbit, bit)) & 1 != getbit(bn + p * 32, now_state):
                        print (p, bn, bit)
                        falsch = True
                
            if falsch:
                raise "Bad Bit"
        w = twister.getint32()
        for bit, d in enumerate(w):
            assert sum(imap(getbit, d)) & 1 == (v >> (31 - bit)) & 1, byte
        v = random.getrandbits(32)
    print "OK"
