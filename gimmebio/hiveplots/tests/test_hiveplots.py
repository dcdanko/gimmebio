from hiveplots.geometry import *
from hiveplots.hiveplots import *
from matplotlib import pyplot as plt
from matplotlib import cm
from colors.parse_mpa_to_colors import *


def test_hull():
    f = 0 * np.pi / 2
    pts = [RadialPoint(1, 2 + f), RadialPoint(2, 2 + f),
           RadialPoint(2, 1 + f), RadialPoint(4, 1 + f)]
    hull = Hull(*pts)
    hull.draw()
    plt.show()


def test_hive():
    hp = RatioHivePlot()
    hp.addAxis({'a': 0.5, 'b': 0.3, 'c': 0.1})
    hp.addAxis({'a': 0.2, 'b': 0.4, 'c': 0.1})
    hp.addAxis({'a': 0.6, 'b': 0.1, 'c': 0.3})
    cols = {'a': 'r', 'b': 'g', 'c': 'b'}
    hp.draw(colormap=cols)
    plt.show()


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


def coltree_from_mpas(cmap, mpa_files):
    colTreeA = parse_mpa_to_coltree(mpa_files[0])
    for mpa_file in mpa_files[1:]:
        parse_mpa_to_coltree(mpa_file, colTree=colTreeA)
    return colTreeA


def test_hive_with_colors():
    hp = RatioHivePlot()
    add_axis_from_mpa(hp, 'sample_data_a.mpa')
    add_axis_from_mpa(hp, 'sample_data_b.mpa')
    add_axis_from_mpa(hp, 'sample_data_c.mpa')
    cmap = cm.get_cmap('plasma')
    cols = colmap_from_mpas(cmap, ['sample_data_a.mpa',
                                   'sample_data_b.mpa',
                                   'sample_data_c.mpa'])
    hp.draw(colormap=cols)
    plt.show()

def test_hive_with_colors2():
    hp = RatioHivePlot()
    fs = ['/Users/dcdanko/Dropbox/Projects/Nasa/spacesuits/results/SL280259.kraken_taxonomy_profiling.mpa.mpa.tsv',
          '/Users/dcdanko/Dropbox/Projects/Nasa/spacesuits/results/SL280258.kraken_taxonomy_profiling.mpa.mpa.tsv',
          '/Users/dcdanko/Dropbox/Projects/Nasa/spacesuits/results/SL280257.kraken_taxonomy_profiling.mpa.mpa.tsv'
         ]
    add_axis_from_mpa(hp, fs[0])
    add_axis_from_mpa(hp, fs[1])
    add_axis_from_mpa(hp, fs[2])
    cmap = cm.get_cmap('plasma')
    coltree = coltree_from_mpas(cmap, fs)
    cols = coltree.color_map(cmap)
    hp.draw(colormap=cols)
    plt.axis('off')
    plt.show()

if __name__ == '__main__':
    test_hive_with_colors2()
