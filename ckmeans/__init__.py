"""
# http://www.fantascienza.net/leonardo/so/kmeans/kmeans.html
kmeans.py, V.2.0, Jun 2 2007, by leonardo maffi.
Related ckmeans.c and ckmeans.so files are optional.
c_version_available is True if available.
The C + ctypes version of the k-means is quite faster than the Psyco version
(tested with n_data = 2000, k = 32, epsilon = 0.001, no perceptual color distance, no verbose.
The Python version chooses the initial centroids distinct):
  Python V.2.5.1:           18.64 s   81   X
  1.5.2 on Python V.2.5.1:   2.1  s    9.1 X
  C + ctypes:                0.23 s    1   X
Possible improvements:
- Add a better choose initial to the C code
"""

import os
import ctypes
import sysconfig, sys
from ctypes import cdll, c_int, c_double, POINTER, cast, addressof
__all__ = ['kmeans']

# ====================================================
# Hook up c module
HERE = os.path.dirname(os.path.realpath(__file__))
'''http://www.python.org/dev/peps/pep-3149/'''
SUFFIX = sysconfig.get_config_var('SO')
if not SUFFIX:  # pragma: no cover
    SOABI = sysconfig.get_config_var('SOABI')
    SUFFIX = ".{}.so".format(SOABI)

SO_PATH = os.path.join(HERE, 'lib' + SUFFIX)
LIB = ctypes.CDLL(SO_PATH)
# ====================================================




def ckmeans(data, k, t=0.0001, maxiter=1000):
    """ckmeans(data, k, t=0.0001, maxiter=5000): C+ctypes version of kmeans().
    See the kmeans() docstring for more info.
    Note: this version doesn't cheek that the initial centroids are all distinct,
      (so it may happen the resulting centroids can be < k)."""
    n = len(data) # number of points
    m = len(data[0]) # number of dimensions of each point

    TyPoint = c_double * m # type of a point, made of m doubles
    TyPoints = TyPoint * n # type of the point array (it's a 2D matrix of doubles)
    TyPunPoint = POINTER(TyPoint) # type of pointer to a point

    # allocation and initialization of the actual array of points,
    #   it's a contigous block of memory.
    # I've had to use the first * because it seems TyPoints() can't take a
    #   generator as input.
    cdata = TyPoints(*(TyPoint(*p) for p in data))

    # type of the array of pointers to points of the cdata array
    TyPuns = TyPunPoint * n

    # allocation and initialization of the actual array of pointers to points of
    #   the cdata array (so the C k_means function can find the start of each point).
    # I have had to use  cast(p, TyPunPoint)  to find the pointer to the point p
    puns = TyPuns( *(cast(p, TyPunPoint) for p in cdata) )

    # type of the output array of the centroids (they are points)
    TyCentroids = TyPoint * k

    # Allocation of the actual array of the centroids (initialized to 0 by ctypes),
    #   this is an output value.
    centroids = TyCentroids()

    # this is like TyPuns, it's the type of the array of pointers to the centroids
    TyPunsCentroids = TyPunPoint * k

    # allocation and initialization of the actual array of pointers to centroids
    puns_centroids = TyPunsCentroids( *(cast(p, TyPunPoint) for p in centroids) )

    LIB.k_means.argtypes = [TyPuns, c_int, c_int, c_int, c_double, c_int, TyPunsCentroids]

    TyLabels = c_int * n

    LIB.k_means.restype = POINTER(TyLabels)

    pr = LIB.k_means(puns, n, m, k, c_double(t), maxiter, puns_centroids)

    labels = list(pr.contents)

    # Conversion (copy) of the centroids array of points to a Python list of list
    pycentroids = map(list, centroids)

    # Linux-Windows compatibility code
    if sys.platform.startswith('win'):
        libc = cdll.msvcrt

    # Call to the free() function of the C lib to free the memory of the array
    #   of labels allocated by the k_means.
        libc.free(addressof(pr.contents))

    # return the labels and centroids
    return labels, pycentroids
