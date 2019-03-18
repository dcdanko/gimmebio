
from unittest import TestCase

from os.path import join, dirname

from gimmebio.hiveplots.geometry import *
from gimmebio.hiveplots.hiveplots import *
from matplotlib import pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import cm
from gimmebio.hiveplots.colors.parse_mpa_to_colors import *


def indir(fname):
    return join(dirname(__file__), fname)


def add_axis_from_mpa(hp, mpa_file):
    colTreeA = parse_mpa_to_coltree(mpa_file)
    leafsA = {leaf.label: leaf.value
              for leaf in colTreeA.get_leafs()
              if 's__' in leaf.label}
    totA = sum(leafsA.values())
    leafsA = {leaf.label: leaf.value / totA
              for leaf in colTreeA.get_leafs()
              if 's__' in leaf.label}
    leafsA = {k: v for k, v in leafsA.items() if v >= 0.01}
    hp.addAxis(leafsA)


def coltree_from_mpas(mpa_files):
    colTreeA = parse_mpa_to_coltree(mpa_files[0])
    for mpa_file in mpa_files[1:]:
        parse_mpa_to_coltree(mpa_file, colTree=colTreeA)
    return colTreeA


class TestHiveplots(TestCase):
    """Test suite for hive plots."""

    def test_hull(self):
        f = 0 * np.pi / 2
        pts = [RadialPoint(1, 2 + f), RadialPoint(2, 2 + f),
               RadialPoint(2, 1 + f), RadialPoint(4, 1 + f)]
        hull = Hull(*pts)
        hull.draw()
        plt.show()

    def test_hive(self):
        hp = RatioHivePlot()
        hp.addAxis({'a': 0.5, 'b': 0.3, 'c': 0.1})
        hp.addAxis({'a': 0.2, 'b': 0.4, 'c': 0.1})
        hp.addAxis({'a': 0.6, 'b': 0.1, 'c': 0.3})
        cols = {'a': 'r', 'b': 'g', 'c': 'b'}
        hp.draw(colormap=cols)
        plt.show()

    def test_hive_with_label(self):
        hp = RatioHivePlot()
        hp.addAxis({'a': 0.5, 'b': 0.3, 'c': 0.1})
        hp.addAxis({'a': 0.2, 'b': 0.4, 'c': 0.1})
        hp.addAxis({'a': 0.6, 'b': 0.1, 'c': 0.3})
        cols = {'a': 'r', 'b': 'g', 'c': 'b'}
        hp.draw(colormap=cols, label='foo')
        plt.show()

    def test_straight_hive(self):
        hp = RatioHivePlot(straight_sided=True)
        hp.addAxis({'a': 0.5, 'b': 0.3, 'c': 0.1})
        hp.addAxis({'a': 0.2, 'b': 0.4, 'c': 0.1})
        hp.addAxis({'a': 0.6, 'b': 0.1, 'c': 0.3})
        cols = {'a': 'r', 'b': 'g', 'c': 'b'}
        hp.draw(colormap=cols)
        plt.show()

    def test_straight_hive_with_gap(self):
        hp = RatioHivePlot(straight_sided=True)
        hp.addAxis({'a': 0.5, 'b': 0.3})
        hp.addAxis({'a': 0.2, 'b': 0.4, 'c': 0.1})
        hp.addAxis({'a': 0.6, 'b': 0.1})
        cols = {'a': 'r', 'b': 'g', 'c': 'b'}
        hp.draw(colormap=cols, thickaxes=True)
        plt.show()

    def test_hive_with_colors(self):
        hp = RatioHivePlot()
        sample_data = [
            indir(el) for el in ['sample_data_a.mpa', 'sample_data_b.mpa', 'sample_data_c.mpa']
        ]
        for f in sample_data:
            add_axis_from_mpa(hp, f)
        cmap = cm.get_cmap('plasma')
        cols = coltree_from_mpas(sample_data).color_map(cmap)
        hp.draw(colormap=cols)
        plt.show()

    def test_straight_hive_with_colors(self):
        hp = RatioHivePlot(straight_sided=True)
        sample_data = [
            indir(el) for el in ['sample_data_a.mpa', 'sample_data_b.mpa', 'sample_data_c.mpa']
        ]
        for f in sample_data:
            add_axis_from_mpa(hp, f)
        cmap = cm.get_cmap('plasma')
        cols = coltree_from_mpas(sample_data).color_map(cmap)
        hp.draw(colormap=cols)
        plt.show()

    def test_legend(self):
        hp = RatioHivePlot()
        sample_data = [
            indir(el) for el in ['sample_data_a.mpa', 'sample_data_b.mpa', 'sample_data_c.mpa']
        ]
        for f in sample_data:
            add_axis_from_mpa(hp, f)
        cmap = cm.get_cmap('plasma')
        cols = coltree_from_mpas(sample_data).color_map(cmap)
        hp.draw(colormap=cols)

        patches = [mpatches.Patch(color=col, label=label) for label, col in cols.items()]
        plt.legend(handles=patches)

        plt.show()
