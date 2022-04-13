import numpy as np
from pydantic import BaseModel
import random
import copy
from shapely.geometry import Polygon

from prog.fitness import fitness
from prog.nfp import find_nfp, select_best_nfp_pt
from prog.transform import apply_transformations
from prog.algos.simulated_annealing import simulated_annealing
from prog.algos.greedy import greedy

class Packing:
    """Class representing a packing (aka a nesting), that is a list of containers (aka bins) containing polygons with a certain position (aka translation)"""
    
    def __init__(self, bin_size, polygons, bins=None):
        self.bin_size = bin_size  # bins are all the same size, defined by `bin_size` 
        self.polygons = tuple(polygons.keys())  # polygons we want to fit inside bins (this contains only unique occurences of polygons)
        self.remaining = polygons
        
        # bins are initially empty except if specified in argument `bins`
        # each bin is a list of tuples, each tuple in a bin contains the following: 
        # (initial polygon: tuple(tuple(float, float)), transformed polygon: tuple(tuple(float, float)), translation to locate transformed polygon in the bin: np.array)
        if bins is None:
            self.bins = []
        else:
            self.bins = [[(x, y, np.array(z)) for x, y, z in abin] for abin in bins]
        
        # fitness-fuction weights
        self.coeffs = (1/2, 1/2, 0)
        
    def nest_all(self, mode, sort, algo_extra):
        """Will nest all polygons not yet nested according to remaining quantities"""
        if mode == 'initial':
            self.make_initial_nesting(sort)
        elif mode == 'greedy':
            self = greedy(self, sort)
        elif mode == 'simulated annealing':
            initial_temperature = algo_extra[0]
            decrease_rate = algo_extra[1]
            self = simulated_annealing(self, sort, initial_temperature, decrease_rate)
        # elif mode == 'genetic':
        #     self.make_initial_nesting(sort)
    
    
    # def sort_figures_before_nesting()
    
    
    def make_initial_nesting(self, sort):
        """Will nest all polygons not yet nested according to remaining quantities"""
        if sort == 'random':
            while self.remaining:
                polygon = random.choice(list(self.remaining.keys()))
                self.initial_polygon_nest(polygon, sort)
        elif sort == 'decreasing area':
            polygons = dict(sorted(self.remaining.items(), key=lambda pg: Polygon(pg[0]).area, reverse=True))
            for polygon in polygons:
                for _ in range(self.remaining[polygon]):
                    self.initial_polygon_nest(polygon, sort)
        
        
    def initial_polygon_nest(self, polygon, sort):
        for abin in self.bins[-1:]:    
            valid_pts = find_nfp(abin, self.bin_size, polygon)
            if len(valid_pts):
                abin.append((polygon, polygon, select_best_nfp_pt(valid_pts)))
                break
        else:  # if else statement is executed, it means that the polygon did not fit in any existing bins, we need to add a new bin
            # TODO: check if polygon fits alone in a new bin
            self.bins.append([(polygon, polygon, np.zeros(2))])

        self.remaining[polygon] -= 1
        if sort == 'random' and (not self.remaining[polygon]):
            self.remaining.pop(polygon)

    
def available_polygons(self):
    """returns polygons whose remaining quantities are not 0"""
    return [k for k,v in self.remaining.items() if v > 0]
    
def hashable_bins(self):
    """returns current bins as nested tuples, so they are hashable and can be used in `dict` as keys"""
    return tuple([tuple([(x, y, tuple(z)) for x, y, z in abin]) 
                      for abin in self.bins])
    
def get_n_last(self, n_last):
    """return n last polygons (ignoring bins)"""
    all_polygons = [(x, y, tuple(z)) for abin in self.bins for x, y, z in abin]
    return tuple(all_polygons[-n_last:])
