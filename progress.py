import sys
import os

class ProgressBar(object):
    """Just a Progress Bar"""

    def __init__(self, x_res=80, y_res=31):
        self.pbar = self.draw_bar()
        self.x_res = x_res
        self.y_res = y_res
        self.len = (x_res + 1) * y_res
        self.pos = 0

    def draw_bar(self):
        def m(c):
            z = c
            for i in xrange(200):
                z = z ** 2 + c
                if abs(z.real) > 3:
                    return i
            return 0
        c1 = complex(-2.2, -0.9)
        c2 = complex(0.6, 0.9)
        x_res, y_res = self.x_res, self.y_res
        for i in xrange(y_res):
            y = c1.imag + i * (c2.imag - c1.imag) / float(y_res - 1)
            for j in xrange(x_res):
                x = c1.real + j * (c2.real - c1.real) / float(x_res - 1)
                v = m(complex(x, y))
                if v:
                    v = v % 20
                    yield chr(ord("A") + v)
                else:
                    yield "."
            yield os.linesep

    def progress(self, v):
        v = min(v, 1)
        new_pos = int(self.len * v)
        sys.stdout.write("".join(self.pbar.next()
                                 for i in xrange(new_pos - self.pos)))
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
