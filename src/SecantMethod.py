from random import uniform

from sympy.parsing.sympy_parser import parse_expr


class SecantMethod:
    STOPPING_VALUE = 10 ** (-7)
    MAX_ITERATION = 1000
    xa = 0
    xb = 0
    fx = parse_expr("0")
    root = 0
    point_list = []

    def __init__(self, fx):
        self.fx = fx
        self.point_list = []
        self.xa = uniform(-5, 5)
        self.xb = uniform(-5, 5)

    def start(self):
        xa = self.xa
        xb = self.xb
        fx = self.fx
        i = 1

        while True:  # do-while emulation in python
            ya = fx.subs({'x': xa})
            yb = fx.subs({'x': xb})
            self.point_list.append([round(xa,4), round(ya,4)])

            tmp = xb
            xb = self.get_next_x(xa, xb, ya, yb)
            xa = tmp

            i += 1

            fn = fx.subs({'x': xb})

            if abs(fn) < self.STOPPING_VALUE or abs(xa - xb) < self.STOPPING_VALUE ** 4 or i >= self.MAX_ITERATION:
                self.point_list.append([round(xb,4), round(yb,4)])
                self.root = xb
                return

    @classmethod
    def get_next_x(cls, xa, xb, ya, yb):
        return xa - (ya * (xb - xa) / (yb - ya))  # simplification for the secant's intersection with X axis formula

    def get_root(self):
        return self.root

    def get_point_list(self):
        return self.point_list
