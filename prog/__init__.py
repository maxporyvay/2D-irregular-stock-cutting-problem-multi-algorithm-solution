import sys
import matplotlib.pyplot as plt
import time
import argparse

from prog.packing import Packing
from prog.visualize import plot_packing
from prog.fitness import fitness


def input_data(filename):
    lines = filename.readlines()
    sort, xbin, ybin, algo, *other = lines
    bin_size = (float(xbin), float(ybin))
    algo_extra = []
    if algo.strip() == 'simulated annealing':
        algo_extra.extend([float(other[0]), float(other[1])])
        figures = other[2:]
    else:
        figures = other
    polygons = {}
    for line in figures:
        if line.strip() == '(':
            poly = []
        elif line.strip() == ')':
            poly = tuple(poly)
        elif line.strip()[0] == '(' and line.strip()[-1] == ')':
            poly.append(tuple(map(float, line.strip()[1:-1].split(','))))
        else:
            polygons[poly] = int(line.strip())
    return polygons, bin_size, algo.strip(), algo_extra, sort.strip()


def main():
    # main speed bottlenecks are visible in this profiling, function `get_minkowski_sum`, `pc.AddPaths` and `get_clipping_limits`
    # IMPORTANT first run is slow as numba compiles functions, always run TWICE
    
    parser = argparse.ArgumentParser()
    parser.add_argument ('-i', '--input', required=True, type=argparse.FileType())
    parser.add_argument ('-o', '--output', default='stdout')
    namespace = parser.parse_args(sys.argv[1:])
    polygons, bin_size, algo, algo_extra, figures_sorting_type = input_data(namespace.input)
    #print('polygons', polygons, 'size', bin_size, 'algo', algo, 'extra', algo_extra, 'sort', figures_sorting_type, sep='\n')

    packing = Packing(bin_size, polygons)
    time1 = time.time()
    packing.nest_all(algo, figures_sorting_type, algo_extra)
    print('Time:', time.time() - time1)
    fit = fitness(packing.bins, packing.bin_size, packing.coeffs)
    print('Fitness-function value:', fit)
    if namespace.output == 'stdout':
        print('Bins:', packing.bins, sep='\n')
    else:
        with open(namespace.output, 'w') as f:
            f.write(str(packing.bins))
    plot_packing(packing, 10)

if __name__ == '__main__':
    sys.exit(main())
