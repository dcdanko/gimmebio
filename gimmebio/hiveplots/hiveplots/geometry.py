import numpy as np
from matplotlib import pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from math import sqrt, atan


class RadialPoint:

    def __init__(self, r, theta, label=None):
        self.r = r
        self.theta = theta
        self.label = None

    def cartesian(self):
        x = self.r * np.cos(self.theta)
        y = self.r * np.sin(self.theta)
        return CartesianPoint(x, y, label=self.label)

    def translate(self, r, theta):
        return RadialPoint(self.r + r, self.theta + theta, label=self.label)

    def scale(self, alpha):
        return RadialPoint(self.r * alpha, self.theta, label=self.label)

    def translateCartesian(self, x, y):
        rpt = CartesianPoint(x, y).radial()
        return self.translate(rpt.r, rpt.theta)

    def __str__(self):
        s = '{}, {} pi'.format(self.r, self.theta / np.pi)
        return(s)


class CartesianPoint:

    def __init__(self, x, y, label=None):
        self.x = x
        self.y = y
        self.label = None

    def translate(self, x, y):
        return CartesianPoint(self.x + x, self.y + y, label=self.label)

    def scale(self, alpha):
        return self.radial().scale(alpha).cartesian()

    def radial(self):
        r = sqrt(self.x ** 2 + self.y ** 2)
        if self.x == 0:
            if self.y > 0:
                theta = np.pi / 2
            else:
                theta = 3 * np.pi / 2
        elif self.y == 0:
            if self.x > 0:
                theta = 0
            else:
                theta = np.pi
        else:
            theta = atan(self.y / self.x)
            if self.x < 0 and self.y < 0:
                theta += 2 * np.pi
            elif self.x < 0:
                theta += np.pi

        return RadialPoint(r, theta, label=self.label)


class RadialPointSet:

    def __init__(self, *rpts):
        self.pts = rpts

    def xs(self):
        return [pt.cartesian().x for pt in self.pts]

    def ys(self):
        return [pt.cartesian().y for pt in self.pts]

    def xys(self):
        return [(x, y) for x, y in zip(self.xs(), self.ys())]

    def draw(self, color=None):
        plt.plot(self.xs(), self.ys(), color=color)

    def translateCartesian(self, x, y):
        pts = [pt.translateCartesian(x, y) for pt in self.pts]
        return RadialPointSet(*pts)

    def scale(self, alpha):
        pts = [pt.scale(alpha) for pt in self.pts]
        return RadialPointSet(*pts)

    def __len__(self):
        return len(self.pts)


class Colinear(RadialPointSet):

    def __init__(self, rpt0, rpt1):
        super(Colinear, self).__init__(rpt0, rpt1)
        assert rpt0.theta == rpt1.theta
        assert rpt0.r <= rpt1.r


class ArchimedianCurve:

    def __init__(self, rpt0, rpt1):
        self.start = rpt0
        self.end = rpt1
        self.deltaR = self.end.r - self.start.r
        deltaT = self.end.theta - self.start.theta
        if deltaT < 0:
            deltaT += 2 * np.pi
        self.deltaT = deltaT

    def _interpOnce(self, alpha):
        assert alpha >= 0.0
        assert alpha <= 1.0
        return self.start.translate(alpha * self.deltaR,
                                    alpha * self.deltaT)

    def interp(self, N=100):
        alpha = 0
        alphaInc = 1.0 / (N - 1)
        pts = []
        while len(pts) < N:
            pt = self._interpOnce(alpha)
            pts.append(pt)
            alpha += alphaInc
        return RadialPointSet(*pts)

    def draw(self, color=None):
        resolution = 100  # Just a guess
        pts = self.interp(N=resolution)
        plt.plot(pts.xs(), pts.ys(), color=color)


class Hull:

    def __init__(self, rpt0, rpt1, rpt2, rpt3, label=None):
        self.co0 = Colinear(rpt0, rpt1)
        self.co1 = Colinear(rpt2, rpt3)
        self.origin = CartesianPoint(0, 0)
        self.alpha = 1
        self.label = label

    def translateCartesian(self, x, y):
        out = Hull(self.co0.pts[0], self.co0.pts[1],
                   self.co1.pts[0], self.co1.pts[1])
        out.alpha = self.alpha
        out.origin = self.origin.translate(x, y)
        return out

    def scale(self, alpha):
        out = Hull(self.co0.pts[0], self.co0.pts[1],
                   self.co1.pts[0], self.co1.pts[1])
        out.alpha = alpha
        out.origin = self.origin
        return out

    def draw(self, color=None, ax=None):
        if ax is None:
            _, ax = plt.subplots()
        co0 = self.co0.scale(self.alpha)
        #co0 = co0.translateCartesian(self.origin.x, self.origin.y)
        co1 = self.co1.scale(self.alpha)
        #co1 = co1.translateCartesian(self.origin.x, self.origin.y)
        ac0 = ArchimedianCurve(co0.pts[0], co1.pts[0])
        curve0 = ac0.interp().xys()
        ac1 = ArchimedianCurve(co0.pts[1], co1.pts[1])
        curve1 = ac1.interp().xys()
        mat = np.matrix(curve0 + curve1[::-1])
        pc = PatchCollection([Polygon(mat)],
                             facecolor=color,
                             edgecolor=color,
                             alpha=1)
        ax.add_collection(pc)
        #ac0.draw(color=color)
        #ac1.draw(color=color)
