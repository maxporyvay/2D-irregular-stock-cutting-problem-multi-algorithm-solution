import sys
import skgeom as sg
import numpy as np
import pyclipper
from numba import njit, jit, literal_unroll
import math
from pydantic import BaseModel
import random
import itertools
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, MultiPolygon, GeometryCollection, LinearRing, MultiLineString, LineString, Point
import time
import copy

from prog.packing import Packing
from prog.visualize import plot_packing
from prog.fitness import fitness

# example polygons
# polygons are defined as tuple(tuple(float, float)) because we use them as `dict` keys

pg0 = (
    (0, 0),
    (8, 0),
    (8, 9),
    (9, 9),
    (9, 3),
    (1, 3),
    (1, 9),
    (0, 9),
)

pg1 = (  # this is a square with a notch on the top
    (0, 0),
    (10, 0),
    (10, 10),
    (7, 10),
    (7, 5),
    (3, 5),
    (3, 10),
    (0, 10)
)

pg2 = (  # this is a triangle with
    (0, 0),
    (10, 0),
    (5, math.tan(math.pi / 3) * 5)
)

pg3 = (  # this is a parallelogram leaning on the right
    (0, 0),
    (5, 0),
    (10, 10),
    (5, 10)
)

pg4 = (  # звездочка
    (0, 3),
    (2, 4),
    (3, 6),
    (4, 4),
    (6, 3),
    (4, 2),
    (3, 0),
    (2, 2)
)

# pg4 = ( 
#     (0, 2),
#     (1.5, 2.5),
#     (2, 4),
#     (2.5, 2.5),
#     (4, 2),
#     (2.5, 1.5),
#     (2, 0),
#     (1.5, 1.5)
# )

pg5 = (  # this is a square
    (0, 0),
    (10, 0),
    (10, 10),
    (0, 10)
)

pg6 = (  # this is a trapeze
    (0, 0),
    (9, 0),
    (6, 5),
    (3, 5)
)

pg7 = (  # восьмиугольник
    (0, 4),
    (0, 8),
    (4, 12),
    (8, 12),
    (12, 8),
    (12, 4),
    (8, 0),
    (4, 0)
)

pg8 = (  # треугольник прямоугольный
    (0, 0),
    (10, 0),
    (0, 10)
)

# pg5 = (
#     (0, 0),
#     (9, 0),
#     (5, 40)
# )

#bin_size = (55, 100)  # size of the container
bin_size = (70, 100)


def main():
    # main speed bottlenecks are visible in this profiling, function `get_minkowski_sum`, `pc.AddPaths` and `get_clipping_limits`
    # IMPORTANT first run is slow as numba compiles functions, always run TWICE

    # polygons = (pg1, pg2, pg3)
    polygons = {pg1: 100, pg2: 100, pg3: 100, pg4: 150, pg5: 70, pg6: 30}
    # polygons = {pg0:100, pg1: 100, pg2: 100, pg3: 100, pg4: 150, pg5: 70, pg6: 30}
    # polygons = {pg1: 100, pg2: 100, pg3: 100, pg4: 150}
    polygons = dict(sorted(polygons.items(), key=lambda pg: Polygon(pg[0]).area, reverse=True))
    # print(polygons)
    # quantities = (1000, 1000, 1000, 1500)
    # quantities = (100, 100, 100)
    packing = Packing(bin_size, polygons)
    # %lprun -f find_nfp packing.nest_all(100)
    time1 = time.time()
    # packing.nest_all('simulated annealing', False, 500, 1)
    # packing.nest_all('full greedy', False, 0, 0)
    packing.nest_all('fast greedy', False, 0, 0)
    print('Time:', time.time() - time1)
    fit = fitness(packing.bins, packing.bin_size, packing.coeffs)
    print('Fitness-function value:', fit)
    plot_packing(packing, 10)

if __name__ == '__main__':
    sys.exit(main())
