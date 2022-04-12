import numpy as np
from pydantic import BaseModel
import random
import copy
from shapely.geometry import Polygon

from prog.fitness import fitness
from prog.nfp import find_nfp, select_best_nfp_pt
from prog.transform import apply_transformations

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
        if mode == 'fast greedy':
            self.make_initial_nesting(1, sort)
        elif mode == 'full greedy':
            self.make_initial_nesting(0, sort)
        elif mode == 'simulated annealing':
            self.make_initial_nesting(1, sort)
            initial_temperature = algo_extra[0]
            decrease_rate = algo_extra[1]
            self.simulated_annealing(initial_temperature, decrease_rate)
        # elif mode == 'genetic':
        #     self.make_initial_nesting(1, sort)
    
#     def make_initial_nesting(self, fast=True):
#         """Will nest all polygons not yet nested according to remaining quantities"""
#         for polygon in self.polygons:
#             for _ in range(self.remaining[polygon]):
#                 self.initial_polygon_nest(polygon, fast=fast)
                
    def make_initial_nesting(self, fast, sort):
        """Will nest all polygons not yet nested according to remaining quantities"""
        if sort == 'random':
            while self.remaining:
                polygon = random.choice(self.polygons)
                self.initial_polygon_nest(polygon, sort, fast)
        elif sort == 'decreasing area':
            polygons = dict(sorted(self.remaining.items(), key=lambda pg: Polygon(pg[0]).area, reverse=True))
            for polygon in polygons:
                for _ in range(self.remaining[polygon]):
                    self.initial_polygon_nest(polygon, sort, fast)
                
    def initial_polygon_nest(self, polygon, sort, fast):
        """Will nest the input polygon if the initial quantity for this polygon hasn't been reached yet"""
        if not self.remaining.get(polygon):
            return False
        
        # apply transformation
        if not fast:
            transformed_polygons = [apply_transformations(polygon, flip, rotation) for flip in (False, True) for rotation in (0, 90, 180, 270)]

        if not fast:
            flag = []
            bbins = []
            for abinidx in range(len(self.bins)):
                valid_pts_list = []
                transformed_polygons_ = copy.deepcopy(transformed_polygons)
                for i in range(len(transformed_polygons)):
                    # print('qqq', self.bins[abinidx])
                    # print('www', transformed_polygons)
                    nfp = find_nfp(self.bins[abinidx], self.bin_size, transformed_polygons[i])
                    if len(nfp):
                        valid_pts_list.append(nfp)
                    else:
                        transformed_polygons_[i] = -1
                if len(valid_pts_list):
                    transformed_polygons_ = [x for x in transformed_polygons_ if x != -1]
                    bins = [copy.deepcopy(self.bins) for _ in range(len(valid_pts_list))]
                    fit = []
                    for j in range(len(valid_pts_list)):
                        bins[j][abinidx].append((polygon, transformed_polygons_[j], select_best_nfp_pt(valid_pts_list[j])))
                        fit.append(fitness(bins[j], self.bin_size, self.coeffs))
                    idx = np.argmax(fit)
                    bbins.append(bins[idx])
                else:
                    flag.append(1)
            # print('len(flag) =', len(flag))
            # print('len(self.bins) =', len(self.bins))
            if len(flag) == len(self.bins):  # if else statement is executed, it means that the polygon did not fit in any existing bins, we need to add a new bin
                # TODO: check if polygon fits alone in a new bin
                self.bins.append([(polygon, polygon, np.zeros(2))])
            else:
                maxi = -1
                bestbins = []
                for bins in bbins:
                    fit = fitness(bins, self.bin_size, self.coeffs)
                    if fit > maxi:
                        maxi = fit
                        bestbins = bins
                self.bins = bestbins
        else:
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
        return True
    
    def nest_polygon_to_a_bin(self, polygon, abin):
        """Will nest the input polygon if the initial quantity for this polygon hasn't been reached yet"""        
        # apply transformation
        # print('1', polygon)
        flip = np.random.choice([True, False])
        rotation = np.random.choice([0, 90, 180, 270])
        # print(polygon)
        transformed_polygon = apply_transformations(polygon[1], flip, rotation)
        # print('2', transformed_polygon)
        valid_pts = find_nfp(abin, self.bin_size, transformed_polygon)
        if len(valid_pts):
            polygon = (polygon[0], transformed_polygon, select_best_nfp_pt(valid_pts))
            abin.append(polygon)
            return True
        else:
            return False
    
#     def make_a_move(self):
#         polygon = self.bins[-1][-1]
#         for idx in range(len(self.bins[:-1])):
#             # print('idx', idx)
#             if self.nest_polygon_to_a_bin(polygon, self.bins[idx]):
#                 return idx
#         else:
#             return -1
        
    def make_a_swap_move(self):
        bins = copy.deepcopy(self.bins)
        binidx1 = np.random.randint(0, len(bins))
        binidx2 = np.random.randint(0, len(bins))
        polyidx1 = np.random.randint(0, len(bins[binidx1]))
        polyidx2 = np.random.randint(0, len(bins[binidx2]))
        if self.nest_polygon_to_a_bin(bins[binidx1][polyidx1], bins[binidx2]) and self.nest_polygon_to_a_bin(bins[binidx2][polyidx2], bins[binidx1]):
            bins[binidx1].pop(polyidx1)
            bins[binidx2].pop(polyidx2)
            return bins
        else:
            return "error"
            
    
    def simulated_annealing(self, init_temp, temp_decr_rate):
        temperature = init_temp
        energy = fitness(self.bins, self.bin_size, self.coeffs)
        while temperature > 0:
            bins = self.make_a_swap_move()
            # print('returned idx', idx)
            if bins != 'error':
                energy_diff = fitness(bins, self.bin_size, self.coeffs) - energy
            if bins != 'error' and (energy_diff >= 0 or np.random.random() >= np.exp(energy_diff / temperature)):
                self.bins = bins
                temperature -= temp_decr_rate
            else:
                temperature -= temp_decr_rate * 0.1
    
#     def fitness(self):
#         """Packing fitness"""
#         fitness_A = (sum(self.bin_fitness_A(abin) for abin in self.bins[:-1]) + self.last_bin_fitness_A(self.bins[-1]))  / len(self.bins)
#         fitness_B = sum(self.bin_fitness_B(abin) for abin in self.bins) / len(self.bins)
#         #fitness_C = ((self.bin_size[0] * self.bin_size[1]) - max(self.bin_fitness_C(abin) for abin in self.bins)) / (self.bin_size[0] * self.bin_size[1]) 
#         fitness_C = 0
#         return 1 - self.A * fitness_A + self.B * fitness_B + self.C * fitness_C
    
#     def bin_fitness_A(self, abin):
#         """Packing fitness part a, lower is better"""
#         polygons = [Polygon(pg + translation) for _, pg, translation in abin]
#         union = GeometryCollection(polygons)
#         return 1 - sum(pg.area for pg in polygons) / (self.bin_size[0] * self.bin_size[1])
    
#     def last_bin_fitness_A(self, abin):
#         """Packing fitness part a, lower is better"""
#         polygons = [Polygon(pg + translation) for _, pg, translation in abin]
#         union = GeometryCollection(polygons)
#         return 1 - sum(pg.area for pg in polygons) / union.envelope.area
    
#     def bin_fitness_B(self, abin):
#         """Packing fitness part b, lower is better
#         It computes an "emptyness" ratio between the sum of each polygons area and the total area of the convex hull of all polygons
#         So if packing is good, polygons fill most of the convex hull and the fitness is low. 
#         This fitness is calculated by bins and then averaged.
#         """
#         polygons = [Polygon(pg + translation) for _, pg, translation in abin]
#         union = GeometryCollection(polygons)
#         return 1 - sum(pg.area for pg in polygons) / union.convex_hull.area
#         # ПУНКТ Б ПОСТАНОВКИ ЗАДАЧИ (МАКСИМАЛЬНО ПЛОТНОЕ РАЗМЕЩЕНИЕ): НУЖНО ОПРЕДЕЛИТЬСЯ,
#         # convex_hull, envelope ИЛИ minimum_rotated_rectangle
        
#     def bin_fitness_C(self, abin):
#         """Packing fitness part c, higher is better"""
#         polygons = [Polygon(pg + translation) for _, pg, translation in abin]
#         union = GeometryCollection(polygons)
#         _, _, maxx, maxy = union.envelope.bounds
#         vertical = self.bin_size[1] - maxy
# #         horizontal = self.bin_size[0] - maxx
# #         v_to_h_ratio = vertical / self.bin_size[0]
# #         binmax, binmin = max(self.bin_size), min(self.bin_size)
# #         if v_to_h_ratio < 1:
# #             remmax, remmin = self.bin_size[0], vertical
# #         else:
# #             remmin, remmax = self.bin_size[0], vertical
# #         maxratio = binmax / remmax
# #         minratio = binmin / remmin
#         return vertical * bin_size[0]
    
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
