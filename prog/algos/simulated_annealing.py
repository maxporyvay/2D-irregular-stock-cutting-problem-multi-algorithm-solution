import numpy as np
from prog.transform import apply_transformations
from prog.nfp import find_nfp, select_best_nfp_pt
from prog.fitness import fitness
import copy

def nest_polygon_to_a_bin(packing, polygon, abin):
    """Will nest the input polygon if the initial quantity for this polygon hasn't been reached yet"""        
    flip = np.random.choice([True, False])
    rotation = np.random.choice([0, 90, 180, 270])
    transformed_polygon = apply_transformations(polygon[1], flip, rotation)
    valid_pts = find_nfp(abin, packing.bin_size, transformed_polygon)
    if len(valid_pts):
        polygon = (polygon[0], transformed_polygon, select_best_nfp_pt(valid_pts))
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
    
    
def make_a_swap_move(packing):
    bins = copy.deepcopy(packing.bins)
    binidx1 = np.random.randint(0, len(bins))
    binidx2 = np.random.randint(0, len(bins))
    polyidx1 = np.random.randint(0, len(bins[binidx1]))
    polyidx2 = np.random.randint(0, len(bins[binidx2]))
    if nest_polygon_to_a_bin(packing, bins[binidx1][polyidx1], bins[binidx2]) and nest_polygon_to_a_bin(packing, bins[binidx2][polyidx2], bins[binidx1]):
        bins[binidx1].pop(polyidx1)
        bins[binidx2].pop(polyidx2)
        return bins
    else:
        return "error"
        

def simulated_annealing(packing, sort, init_temp, temp_decr_rate):
    packing.make_initial_nesting(sort)
    temperature = init_temp
    energy = fitness(packing.bins, packing.bin_size, packing.coeffs)
    while temperature > 0:
        bins = make_a_swap_move(packing)
        if bins != 'error':
            energy_diff = fitness(bins, packing.bin_size, packing.coeffs) - energy
        if bins != 'error' and (energy_diff >= 0 or np.random.random() >= np.exp(energy_diff / temperature)):
            packing.bins = bins
            temperature -= temp_decr_rate
        else:
            temperature -= temp_decr_rate * 0.1
    return packing
