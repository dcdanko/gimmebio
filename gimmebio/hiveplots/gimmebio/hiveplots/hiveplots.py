import numpy as np
from .geometry import (
    RadialPoint,
    CartesianPoint,
    RadialPointSet,
    Hull,
)
from matplotlib import pyplot as plt


class Axis:
    '''Represent one axis in a ratio hiveplot.

    Assume sum(vals) <= 1

    Args:
        vals `{`str`: `float`}`
        fitlength   do not force the axis to unit length

    '''

    def __init__(self, vals, fitlength=False):
        self.rawVals = vals
        self.fitlength = fitlength

    def _processVals(self, names):
        out = []
        start = 0
        for name in names:
            try:
                val = self.rawVals[name]
            except KeyError:
                val = 0
            end = start + val
            out.append((name, start, end))
            start = end
        return out

    def getCoords(self, names, theta):
        out = {}
        for name, r0, r1 in self._processVals(names):
            pt0 = RadialPoint(r0, theta, label=name)
            pt1 = RadialPoint(r1, theta, label=name)
            out[name] = (pt0, pt1)
        return out

    def getTip(self, theta, names):
        '''Return a radial point representing the tip of the axis.'''
        if not self.fitlength:
            return RadialPoint(1, theta)
        vals = self._processVals(names)
        tip = RadialPoint(vals[-1][2], theta)
        return tip

    def names(self):
        return self.rawVals.keys()


class RatioHivePlot:

    def __init__(self):
        self.axes = []

    def addAxis(self, vals):
        self.axes.append(Axis(vals))

    def _getAngles(self):
        angleIncr = 2 * np.pi / len(self.axes)
        startAngle = np.pi / 2
        angles = []
        for i in range(len(self.axes)):
            angles.append(startAngle + i * angleIncr)
        return angles

    def getHulls(self, names):
        out = []
        angles = self._getAngles()

        for i in range(len(self.axes)):
            j = (i + 1) % len(self.axes)
            coords0 = self.axes[i].getCoords(names, angles[i])
            coords1 = self.axes[j].getCoords(names, angles[j])
            out += [Hull(coords0[name][0], coords0[name][1],
                         coords1[name][0], coords1[name][1],
                         label=name)
                    for name in names]
        return out

    def _getNameOrder(self):
        nameSet = {}
        for axis in self.axes:
            for name, val in axis.rawVals.items():
                try:
                    nameSet[name] += val
                except KeyError:
                    nameSet[name] = val
        revValNames = sorted(nameSet.items(), key=lambda x: -x[1])
        names = [name for name, val in revValNames]
        return names

    def draw(self, names=None, colormap=None, box=1, pt=CartesianPoint(0, 0)):
        '''

        Args:
            l `int`, width and height of the bounding square
            pt, `geometry.CartesianPoint`, coords of the top
                left corner of the bounding box
        '''
        if names is None:
            names = self._getNameOrder()
        hulls = self.getHulls(names)
        fig, ax = plt.subplots()
        for i, hull in enumerate(hulls):
            try:
                col = colormap[hull.label]
            except KeyError:
                col = None
            hull.draw(color=col, ax=ax)
        self.drawAxes(names)

    def drawAxes(self, names):
        for axis, angle in zip(self.axes, self._getAngles()):
            pts = RadialPointSet(RadialPoint(0, 0), axis.getTip(angle, names))
            pts.draw(color='black')

    @classmethod
    def from_df(cls, df):
        hive_plot = cls()
        for _, row in df.iterrows():
            hive_plot.addAxis(row)
        return hive_plot
