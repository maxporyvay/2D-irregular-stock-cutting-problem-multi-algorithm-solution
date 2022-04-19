import sys
import os
import matplotlib.pyplot as plt
import time
import argparse
import math

from prog.packing import Packing
from prog.visualize import plot_packing
from prog.fitness import fitness

def input_data(lines):
    mode, *other = lines
    if mode.strip().split()[0] == 'classic_input':
        return classic_input(other)
    elif mode.strip().split()[0] == 'autogenerator':
        return autogenerator_input(mode.strip().split()[1], other)


def classic_input(lines):
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
    return 'classic_input', polygons, bin_size, algo.strip(), algo_extra, sort.strip()


def autogenerator_input(dirname, lines):
    calculate, sort, xbin, ybin, start, stop, step, algo, *other = lines
    bin_size = (float(xbin), float(ybin))
    algo_extra = []
    if algo.strip() == 'simulated annealing':
        algo_extra.extend([float(other[0]), float(other[1])])
        figures = other[2:]
    else:
        figures = other
    polylist = []
    for line in figures:
        figure, *params = line.strip().split()
        params = list(map(float, params))
        if figure == 'equilateral_triangle':
            polylist.append(((0.0, 0.0), (params[0], 0.0), (params[0] / 2, params[0] / 2 * math.tan(math.pi / 3))))
        elif figure == 'isosceles_trapezium':
            maxside = max(params[0], params[1])
            minside = min(params[0], params[1])
            polylist.append(((0.0, 0.0), (maxside, 0.0), ((maxside + minside) / 2, float(minside)), ((maxside - minside) / 2, float(minside))))
        elif figure == 'rectangle':
            polylist.append(((0, 0), (0, float(params[1])), (float(params[0]), float(params[1])), (float(params[0]), 0)))
    return 'autogenerator', polylist, int(start), int(stop), int(step), sort.strip(), bin_size, algo.strip(), algo_extra, dirname, calculate.strip()
    
    
def autogenerate_files(data):
    polylist, start, stop, step, sort, bin_size, algo, algo_extra, dirname, calculate = data
    path = 'input/classic/' + dirname
    os.mkdir(path, mode=0o777, dir_fd=None)
    filenames = []
    for count in range(start, stop, step):
        filename = path + '/' + str(count) + '.txt'
        filenames.append(filename)
        with open(filename, 'w') as f:
            print('classic_input', file=f)
            print(sort, file=f)
            print(bin_size[0], file=f)
            print(bin_size[1], file=f)
            print(algo, file=f)
            for i in algo_extra:
                print(i, file=f)
            for polygon in polylist:
                print('(', file=f)
                for point in polygon:
                    print('    ' + str(point), file=f)
                print(')', file=f)
                print(count, file=f)
    return filenames, calculate, path


def make_calculations(filenames, infofilename, path):
    timelist = []
    fitlist = []
    countlist = []
    for filename in filenames:
        with open(filename) as f:
            lines = f.readlines()
            _, *data = input_data(lines)
            polygons, bin_size, algo, algo_extra, figures_sorting_type = data
            countlist.append(sum(list(polygons.values())))
            packing = Packing(bin_size, polygons)
            time1 = time.time()
            packing.nest_all(algo, figures_sorting_type, algo_extra)
            timelist.append(time.time() - time1)
            fit = fitness(packing.bins, packing.bin_size, packing.coeffs)
            fitlist.append(fit)
    with open(path + '/' + infofilename + '.txt', 'w') as infofile:
        print(countlist, file=infofile)
        print(timelist, file=infofile)
        print(fitlist, file=infofile)

def main():
    # main speed bottlenecks are visible in this profiling, function `get_minkowski_sum`, `pc.AddPaths` and `get_clipping_limits`
    # IMPORTANT first run is slow as numba compiles functions, always run TWICE
    
    parser = argparse.ArgumentParser()
    parser.add_argument ('-i', '--input', required=True, type=argparse.FileType())
    parser.add_argument ('-o', '--output', default='stdout')
    parser.add_argument ('-p', '--plot', action='store_const', const=True)
    namespace = parser.parse_args(sys.argv[1:])
    lines = namespace.input.readlines()
    mode, *data = input_data(lines)
    if mode == 'classic_input':
        polygons, bin_size, algo, algo_extra, figures_sorting_type = data
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
        if namespace.plot:
            plot_packing(packing, 10)
    elif mode == 'autogenerator':
        time1 = time.time()
        filenames, calculate, path = autogenerate_files(data)
        print('Generation time:', time.time() - time1)
        if calculate.split()[0] == 'yes':
            infofilename = calculate.split()[1]
            time1 = time.time()
            make_calculations(filenames, infofilename, path)
            print('Calculation time:', time.time() - time1)
        # delete_autogenerated_files()

if __name__ == '__main__':
    sys.exit(main())
