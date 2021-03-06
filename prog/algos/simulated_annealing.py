import numpy as np
from prog.transform import apply_transformations
from prog.nfp import find_nfp
from prog.fitness import fitness
import copy

class SA:
    def __init__(self, packing, sort, init_temp, temp_decr_rate):
        self.packing = packing
        self.sort = sort
        self.init_temp = init_temp
        self.temp_decr_rate = temp_decr_rate
        
    def nest_polygon_to_a_bin(self, polygon, abin):
        """Will nest the input polygon if the initial quantity for this polygon hasn't been reached yet"""        
        flip = np.random.choice([True, False])
        rotation = np.random.choice([0, 90, 180, 270])
        transformed_polygon = apply_transformations(polygon[1], flip, rotation)
        valid_pts = find_nfp(abin, self.packing.bin_size, transformed_polygon)
        if len(valid_pts):
            best_pts = list(valid_pts)
            best_pts.sort(key=lambda x: x[0])
            best_pts.sort(key=lambda x: x[1])
            best_pt = best_pts[0]
            polygon = (polygon[0], transformed_polygon, best_pt)
            abin.append(polygon)
            return True
        else:
            return False

    #     def make_a_move(packing):
    #         polygon = packing.bins[-1][-1]
    #         for idx in range(len(packing.bins[:-1])):
    #             # print('idx', idx)
    #             if packing.nest_polygon_to_a_bin(polygon, packing.bins[idx]):
    #                 return idx
    #         else:
    #             return -1
        
    def make_a_swap_move(self):
        bins = copy.deepcopy(self.packing.bins)
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
            
    def simulated_annealing(self):
        self.packing.make_initial_nesting(self.sort)
        temperature = self.init_temp
        init_fitness = fitness(self.packing.bins, self.packing.bin_size, self.packing.coeffs)
        energy = 100000 * (1 - fitness(self.packing.bins, self.packing.bin_size, self.packing.coeffs))
        sum_changes = 0
        poss_changes = 0
        while temperature > 0:
            bins = self.make_a_swap_move()
            if bins != 'error':
                possible_new_energy = 100000 * (1 - fitness(bins, self.packing.bin_size, self.packing.coeffs))
                energy_diff = possible_new_energy - energy
                if energy_diff < 0 or np.random.random() < np.exp(-energy_diff / temperature):
                    sum_changes += 1
                    if energy_diff >= 0:
                        poss_changes += 1
                    self.packing.bins = bins
                    energy = possible_new_energy
                    temperature -= self.temp_decr_rate
                else:
                    temperature -= self.temp_decr_rate * 0.1
            else:
                temperature -= self.temp_decr_rate * 0.1
        return sum_changes, poss_changes, init_fitness
