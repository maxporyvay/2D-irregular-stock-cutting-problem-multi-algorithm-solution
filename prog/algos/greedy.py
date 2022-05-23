import numpy as np
import random
from prog.transform import apply_transformations
from prog.nfp import find_nfp
from prog.fitness import fitness
from shapely.geometry import Polygon
import copy

class Greedy:
    def __init__(self, packing, sort):
        self.packing = packing
        self.sort = sort
        
    def greedy(self):
        """Will nest the input polygon if the initial quantity for this polygon hasn't been reached yet"""
        if self.sort == 'random':
            while self.packing.remaining:
                polygon = random.choice(list(self.packing.remaining.keys()))
                self.greedy_step(polygon)
        elif self.sort == 'descending area':
            polygons = dict(sorted(self.packing.remaining.items(), key=lambda pg: Polygon(pg[0]).area, reverse=True))
            for polygon in polygons:
                for _ in range(self.packing.remaining[polygon]):
                    self.greedy_step(polygon)

    def greedy_step(self, polygon):
        transformed_polygons = [apply_transformations(polygon, flip, rotation) for flip in (False, True) for rotation in (0, 90, 180, 270)]
        flag = []
        bbins = []
        for abinidx in range(len(self.packing.bins)):
            valid_pts_list = []
            transformed_polygons_ = copy.deepcopy(transformed_polygons)
            for i in range(len(transformed_polygons)):
                nfp = find_nfp(self.packing.bins[abinidx], self.packing.bin_size, transformed_polygons[i])
                if len(nfp):
                    valid_pts_list.append(nfp)
                else:
                    transformed_polygons_[i] = -1
            if len(valid_pts_list):
                #valid_pts_list = np.reshape(np.array(valid_pts_list), -1)
                #valid_pts_list = valid_pts_list.reshape(valid_pts_list.shape[0] // 2, 2)
                #valid_pts_list = np.unique(valid_pts_list, axis=0)
                transformed_polygons_ = [x for x in transformed_polygons_ if x != -1]
                bins = [copy.deepcopy(self.packing.bins) for _ in range(len(valid_pts_list))]
                fit = []
                for j in range(len(valid_pts_list)):
                    best_pts = list(valid_pts_list[j])
                    best_pts.sort(key=lambda x: x[0])
                    best_pts.sort(key=lambda x: x[1])
                    best_pt = best_pts[0]
                    bins[j][abinidx].append((polygon, transformed_polygons_[j], best_pt))
                    ff = fitness(bins[j], self.packing.bin_size, self.packing.coeffs)
                    fit.append((ff, best_pt, j))
                fit.sort(key=lambda x: x[1][0])
                fit.sort(key=lambda x: x[1][1])
                fit.sort(key=lambda x: x[0], reverse=True)
                bbins.append(bins[fit[0][2]])
            else:
                flag.append(1)
        if len(flag) == len(self.packing.bins):  # if else statement is executed, it means that the polygon did not fit in any existing bins, we need to add a new bin
            # TODO: check if polygon fits alone in a new bin
            self.packing.bins.append([(polygon, polygon, np.zeros(2))])
        else:
            maxi = -1
            bestbins = []
            for bins in bbins:
                fit = fitness(bins, self.packing.bin_size, self.packing.coeffs)
                if fit > maxi:
                    maxi = fit
                    bestbins = bins
            self.packing.bins = bestbins
        
        self.packing.remaining[polygon] -= 1
        if self.sort == 'random' and (not self.packing.remaining[polygon]):
            self.packing.remaining.pop(polygon)
