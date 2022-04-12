from shapely.geometry import Polygon, MultiPolygon, GeometryCollection, LinearRing, MultiLineString, LineString, Point

def fitness(bins, binsize, coeffs):
        """Packing fitness"""
        fitness_A = (sum(bin_fitness_A(abin, binsize) for abin in bins[:-1]) + last_bin_fitness_A(bins[-1]))  / len(bins)
        # fitness_A = len(bins)
        fitness_B = sum(bin_fitness_B(abin) for abin in bins) / len(bins)
        #fitness_C = ((bin_size[0] * bin_size[1]) - max(self.bin_fitness_C(abin, binsize) for abin in self.bins)) / (bin_size[0] * bin_size[1]) 
        fitness_C = 0
        A, B, C = coeffs
        return 1 - (A * fitness_A + B * fitness_B + C * fitness_C)
    
def bin_fitness_A(abin, bin_size):
    """Packing fitness part a, lower is better"""
    polygons = [Polygon(pg + translation) for _, pg, translation in abin]
    union = GeometryCollection(polygons)
    return 1 - sum(pg.area for pg in polygons) / (bin_size[0] * bin_size[1])

def last_bin_fitness_A(abin):
    """Packing fitness part a, lower is better"""
    polygons = [Polygon(pg + translation) for _, pg, translation in abin]
    union = GeometryCollection(polygons)
    return 1 - sum(pg.area for pg in polygons) / union.envelope.area

def bin_fitness_B(abin):
    """Packing fitness part b, lower is better
    It computes an "emptyness" ratio between the sum of each polygons area and the total area of the convex hull of all polygons
    So if packing is good, polygons fill most of the convex hull and the fitness is low. 
    This fitness is calculated by bins and then averaged.
    """
    polygons = [Polygon(pg + translation) for _, pg, translation in abin]
    union = GeometryCollection(polygons)
    return 1 - sum(pg.area for pg in polygons) / union.convex_hull.area
    # ПУНКТ Б ПОСТАНОВКИ ЗАДАЧИ (МАКСИМАЛЬНО ПЛОТНОЕ РАЗМЕЩЕНИЕ): НУЖНО ОПРЕДЕЛИТЬСЯ,
    # convex_hull, envelope ИЛИ minimum_rotated_rectangle

def bin_fitness_C(abin, bin_size):
    """Packing fitness part c, higher is better"""
    polygons = [Polygon(pg + translation) for _, pg, translation in abin]
    union = GeometryCollection(polygons)
    _, _, maxx, maxy = union.envelope.bounds
    vertical = bin_size[1] - maxy
#         horizontal = self.bin_size[0] - maxx
#         v_to_h_ratio = vertical / self.bin_size[0]
#         binmax, binmin = max(self.bin_size), min(self.bin_size)
#         if v_to_h_ratio < 1:
#             remmax, remmin = self.bin_size[0], vertical
#         else:
#             remmin, remmax = self.bin_size[0], vertical
#         maxratio = binmax / remmax
#         minratio = binmin / remmin
    return vertical * bin_size[0]
