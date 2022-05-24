# 2D irregular stock cutting problem multi-algorithm solution

## Description

Fast and efficient stock cutting problem solutions are in high demand in many industries. Since these problems belong to the class of NP-hard problems, it is impossible to find an exact solution, which makes it possible to constantly offer better algorithms for finding an approximate solution to such problems. This project offers different approaches to solving nesting problems on the basis of classical heuristic algorithms.

## Dependencies

- Python 3.6

Python packages that can be installed with pip:

- numba
- shapely
- pyclipper
- numpy
- matplotlib
- pydantic

Python packages that can be installed with conda:

- scikit-geometry

## How to run the program

You can run the program as a python package:
```
python3 -m prog
```

Keys are:

1. -i, --input: path to an input file (*required*)
2. -o, --output: path to an output file (*default: stdout, ONLY for one input file usage*)
3. -p, --plot: if you specify this key, visualization of a result will be made using MatPlotLib (*ONLY for one input file usage*)

## One input file usage

You should prepare correct input text file. The lines should go one after the other in the following order:

- **classic input** (*const text*)
- <ins>figures sorting type</ins>: **descending area** OR **random**
- <ins>sheets length</ins> (*x coord*): ***float***
- <ins>sheets width</ins> (*y coord*): ***float***
- <ins>algorithm</ins>: **greedy** OR **simulated annealing**
- IF algorithm is 'simulated annealing', next two lines are <ins>initial temperature</ins>: ***float***, and <ins>temperature decrease rate</ins>: ***float***, respectively
- Next, different figures are specified this way:
  - **(**
  - as many lines as there are vertices (vertices must be listed in the order of traversing the shape along the contour), one line per <ins>vertice</ins>: **(***float***, ***float***)**
  - **)**
  - <ins>number of such figures</ins>: ***int***

Classic input files examples can be found in input/classic directory.

The resulting bins will be written to the specified output file or to standard output. The format of the output is the same as the format of the *bins* field (class *Packing*): list of bins, each bin is a list of its figures, each figure is a tuple with 3 components (constant figure configuration from the input file, transformed figure configuration, translation relative to the origin: numpy.array of two elements (x and y)). Figure configuration is a tuple of tuples-vertices of two elements (coords of each vertice).

Output file example can be found in output directory.

## Using generator

You should prepare correct input text file. The lines should go one after the other in the following order:

- **autogenerator** (*const text*), <ins>directory into input/classic/, where the generated files will be put</ins>: ***str***, divided by a space
- IF you want the program to <ins>make nesting and calculate the quality and the time required for each of the generated classic input files</ins>, **yes** (*const text*) and the <ins>filename for the file with calculations results</ins>: ***str***, divided by space; ELSE **no** (*const text*)
- <ins>figures sorting type</ins>: **descending area** OR **random**
- <ins>sheets length</ins> (*x coord*): ***float***
- <ins>sheets width</ins> (*y coord*): ***float***
- <ins>start number of each of the figures</ins>: ***float***
- <ins>stop number of each of the figures</ins>: ***float***
- <ins>step number of each of the figures</ins>: ***float***
- <ins>algorithm</ins>: **greedy** OR **simulated annealing**
- IF algorithm is 'simulated annealing', next two lines are <ins>initial temperature</ins>: ***float***, and <ins>temperature decrease rate</ins>: ***float***, respectively
- Next, different figures are specified. There can be:
  - **equilateral_triangle** and its <ins>side length</ins>: ***float***, divided by a space
  - **rectangle** and its <ins>width</ins>: ***float***, and <ins>length</ins>: ***float***, divided by spaces
  - **isosceles_trapezium** and its <ins>larger base</ins>: ***float***, and <ins>smaller base (equal to height)</ins>: ***float***, divided by spaces

Autogenerator input files examples can be found in input/autogenerator directory.
