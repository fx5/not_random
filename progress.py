import sys
import os

class ProgressBar(object):
    """Just a Progress Bar"""
    def __init__(self):
        def m(c):
            z = c
            for i in xrange(200):
                z = z ** 2 + c
                if abs(z.real) > 3:
                    return i
            return 0
        c1 = complex(-2.2,-0.9)
        c2 = complex(0.6, 0.9)
        out = []
        x_res, y_res = 80, 30
        for i in xrange(y_res + 1):
            y = c1.imag + i * (c2.imag - c1.imag) / float(y_res)
            for j in xrange(x_res + 1):
                x = c1.real + j * (c2.real - c1.real) / float(x_res)
                v = m(complex(x,y))
                if v:
                    v = v % 20
                    out.append(chr(ord("A")+v))
                else:
                    out.append(".")
            out.append(os.linesep)
        self.bar = "".join(out)
        self.pos = 0

    def progress(self, v):
        v = min(v, 1)
        new_pos = int(len(self.bar) * v)
        sys.stdout.write(self.bar[self.pos:new_pos])
        sys.stdout.flush()
        self.pos = new_pos

if __name__ == "__main__":
    import random
    import time
    t = 0.0
    p = ProgressBar()
    while t < 1:
        t += random.random() / 10
        p.progress(t)
        time.sleep(0.2)
