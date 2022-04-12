import math
import numpy as np

TRANSFORMATIONS = {}
EPS = 0.000001


def apply_transformations(polygon, flip=False, rotation=0):
    """apply transformations to the input polygon and returns the transformed polygon"""
    global TRANSFORMATIONS  # use as cache
    cached_result = TRANSFORMATIONS.get((polygon, flip, rotation))
    if cached_result is not None:
        # if cache not available, apply transformations
        return cached_result
    
    if flip:  # flip = mirror effect, along y in this case
        polygon = tuple([(x, -y) for x, y in polygon]) 
        
    if rotation:
        radian = rotation * math.pi / 180
        polygon = tuple([(epsilon(x * math.cos(radian) - y * math.sin(radian)), epsilon(y * math.cos(radian) + x * math.sin(radian))) for x, y in polygon]) 
       
    # polygon is shifted to the origin by default (important!)
    shift = np.min(polygon, axis=0)
    polygon = tuple([(epsilon(x - shift[0]), epsilon(y - shift[1])) for x, y in polygon]) 
    
    TRANSFORMATIONS[(polygon, flip, rotation)] = polygon
    return polygon

def roundup(flnum):
    if flnum == int(flnum):
        return int(flnum)
    else:
        return int(flnum) + 1
    
def epsilon(number):
    if roundup(number) > number and roundup(number) - number < EPS:
        return roundup(number)
    elif  number > int(number) and number - int(number) < EPS:
        return int(number)
    else:
        return number
