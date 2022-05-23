import skgeom as sg
import numpy as np
import pyclipper
from numba import njit, jit, literal_unroll
import math
from pydantic import BaseModel
import random
import itertools
from shapely.geometry import Polygon, MultiPolygon, GeometryCollection, LinearRing, MultiLineString, LineString, Point
import copy

SINGLE_NFPS = {}  # do not forget to reset cache before any nesting !


def select_best_nfp_pt(pts):
    """Return one point among all input points `pts`.
    Input points `pts` are the valid positions to  fit a new polygon in an existing container with other polygons
    It selects the point which minimizes the vertical position (so polygon are stacked at the bottom of the container)
    """
    pts = np.array(pts)
    ix = np.argmin(pts[:, 1])
    return pts[ix]


def find_nfp(abin, bin_size, polygon):
    """Given an existing container (defined by `abin` and `bin_size`), returns all the valid positions to fit the new `polygon` into this container"""

    # list of minkowski sums between existing polygon and the new polygon, translated by the respective positions of existing polygon
    paths = [get_minkowski_sum(polygon_, polygon, translation) 
             for _, polygon_, translation in abin]
    
    # make a union of all minkowski sums, cf clipper library http://www.angusj.com/delphi/clipper.php
    pc = pyclipper.Pyclipper()
    pc.AddPaths(paths, pyclipper.PT_SUBJECT, True)
    nfps = pc.Execute(pyclipper.CT_UNION, pyclipper.PFT_POSITIVE, pyclipper.PFT_POSITIVE)
    # nfp means non-fitting polygon, with an 's' because it can be composed of several separated polygons
    # all points belonging to the nfps (so a vertice or on any edge) are valid positions to place the new polygon
    
    valid_pts = []
    for nfp in nfps:
        # so far, container edges were not taken into account to compute the nfp
        # the next step clips the nfp in order to keep only the part which fits inside the container
        bin_pts = get_clipping_limits(bin_size, polygon)
        pc = pyclipper.Pyclipper()
        pc.AddPath(bin_pts, pyclipper.PT_CLIP, True)
        pc.AddPaths([nfp], pyclipper.PT_SUBJECT, True)
        nfp_clip = pc.Execute(pyclipper.CT_INTERSECTION, pyclipper.PFT_NONZERO, pyclipper.PFT_NONZERO)

        # the previous step creates new points, like intersection of nfp edges with container edges
        # some of these points are not valid position, we compare the original nfp and the clipped nfp the remove keep only valid points
        nfp_flat = np.array(nfp)
#         print(nfp_flat)
#         print('/////////////////////')
#         print(nfp_clip)
        if nfp_clip:
            nfp_clip_flat = np.array(nfp_clip[0])
        else:
            continue
#         print('/////////////////////')
#         print(nfp_clip_flat)
#         print('#####################')
        valid_pts.append(get_valid_pts(nfp_flat, nfp_clip_flat))
    returning_valid_pts = np.concatenate(valid_pts) if valid_pts else np.array([])
    return returning_valid_pts  # finally we return all the valid positions to fit the new polygon into the existing container

def get_minkowski_sum(pg1: tuple, pg2: tuple, translation):
    """Minkowski sum is an operation between two polygons. 
    It returns a single polygon (often named nfp for non-fitting polygon) which corresponds to the union of all positions of pg1 and pg2 so that they touch each other without overlapping.
    cf https://camo.githubusercontent.com/6ff0febec651b9e82b37226d6a8f6f75d0e4232cb7fb90cc65c3c85d762b8a49/687474703a2f2f7376676e6573742e636f6d2f6769746875622f6e66702e706e67
    This function also applies a translation to the resulting polygon.
    
    Note: this function is more specifically a minkowski difference as pg2 is reversed in the code, however minkowski sum is a more usual term
    Note: `pg1` and `pg2` should be tuples of points, with first point and last point not equal (ie: no need to close the polygon by repeating first point to last position)
    """
    global SINGLE_NFPS  # used as cache
    
    minkowski_sum = SINGLE_NFPS.get(hash((pg1, pg2)))
    if minkowski_sum is None:
        # if cache not available, compute minkowski sum
        skpg1 = sg.Polygon(pg1)
        if skpg1.orientation() == -1:  # check that polygon has the right orientation
            skpg1.reverse_orientation()

        skpg2 = sg.Polygon(-1 * np.array(pg2))
        if skpg2.orientation() == -1:
            skpg2.reverse_orientation()

        # cf library scikit-geom https://scikit-geometry.github.io/scikit-geometry/polygon.html#Minkowski-Sum-of-2-Polygons
        minkowski_sum = sg.minkowski.minkowski_sum(skpg1, skpg2).outer_boundary().coords
        SINGLE_NFPS[hash((pg1, pg2))] = minkowski_sum
    return vec_sum(minkowski_sum, translation)

@njit()
def vec_sum(array1, array2):
    """Sum of vectors, accelerated with numba"""
    return array1 + array2

@njit(cache=True)
def get_clipping_limits(bin_size, polygon):
    """Returns a rectangle corresponding to the container but offseted (toward the inside) with polygon delta along x and y 
    Geometrically, this rectangle corresponds to the most extreme positions of the polygon when moving the polygon along the edge of the container without intersecting it
    """
    array = np.array(polygon)
    x = np.max(array[:, 0]) - np.min(array[:, 0])
    y = np.max(array[:, 1]) - np.min(array[:, 1])
    return np.array([
        [0.0, 0.0],
        [float(bin_size[0] - x), 0.0],
        [float(bin_size[0] - x), float(bin_size[1] - y)],
        [0.0, float(bin_size[1] - y)]
    ])

@njit()
def get_valid_pts(pg, pg_to_test):
    """Given two arrays `pg` and `pg_to_test` describing polygons, returns all vertices of `pg_to_test` which are intersecting with `pg`
    The main idea of this function is to use cross and dot products between vectors to understand which points of `pg_to_test` also belong to an edge or a vertice of `pg`
    This function is Numba compatible
    """
    pg_ = np.vstack((pg[-1:], pg[:-1]))
    vectors = pg_ - pg  # defines `pg` as a array of vectors instead of an array of points
    
    # numpy `np.tile` function is not compatible with numba, but this next step is an equivalent, cf non numba version below
    vectors_tiled = vectors
    for _ in range(len(pg_to_test) - 1):  
        vectors_tiled = np.vstack((vectors_tiled, vectors))
    vectors_tiled = vectors_tiled.reshape(len(pg_to_test), len(pg), 2)
    
#     # NON numba version
#     vectors_tiled = np.tile(vectors, (len(pg_to_test), 1, 1))


    # same here, numba doesn't allow `axis` argument in `np.repeat` function
    pg_to_test_repeated = pg_to_test
    for _ in range(len(pg) - 1):
        pg_to_test_repeated = np.hstack((pg_to_test_repeated, pg_to_test))
        
    pg_tiled = pg
    for _ in range(len(pg_to_test) - 1):
        pg_tiled = np.vstack((pg_tiled, pg))
        
    # `vectors_to_test` represents all possible vectors created with a vertice of `pg` and a vertice of `pg_to_test`
    vectors_to_test = (pg_to_test_repeated.reshape(-1, 2) - pg_tiled).reshape(vectors_tiled.shape)
    
#     # non numba version
#     vectors_to_test = (
#         np.repeat(pg_to_test, len(pg), axis=0) - np.tile(pg, (len(pg_to_test), 1))
#     ).reshape(vectors_tiled.shape)
    
    # `vectors_tiled` represented `pg` as vectors, repeated n times, n being the length of `pg_to_test`
    # using cross product and dot product, we can now understand which points from `pg_to_test` also belongs to `pg`
    cross_product = vectors_tiled[:,:,0] * vectors_to_test[:,:,1] - vectors_tiled[:,:,1] * vectors_to_test[:,:,0]
    dot_product = vectors_tiled[:,:,0] * vectors_to_test[:,:,0] + vectors_tiled[:,:,1] * vectors_to_test[:,:,1]
    valid_pts = pg_to_test[np_any_axis1((cross_product == 0) & (dot_product > 0) & (dot_product <= np.sum(vectors ** 2, axis=1)))]
    return valid_pts

@njit()
def np_any_axis1(x):
    """Numba compatible version of np.any(x, axis=1)."""
    out = np.zeros(x.shape[0], dtype=np.bool8)
    for i in range(x.shape[1]):
        out = np.logical_or(out, x[:, i])
    return out
