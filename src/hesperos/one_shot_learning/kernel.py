# ============ Import python packages ============
import numpy as np


# ============ 2D Kernel definition used to compute features of the raw image ============
gaussian_kernel_3x3 = np.array((
        [ [1,2,1], [2,4,2], [1,2,1]]), dtype="int")
gaussian_kernel_5x5 = np.array((
        [ [1,2,4,2,1], [2,4,8,4,2], [4,8,16,8,4], [2,4,8,4,2], [1,2,4,2,1]]), dtype="int")

prewitt_kernel_3x3 = np.array((
        [ [1,0,-1], [1,0,-1], [1,0,-1]]), dtype="int")
prewitt_kernel_5x5 = np.array((
        [ [2,1,0,-1,-2], [2,1,0,-1,-2], [2,1,0,-1,-2], [2,1,0,-1,-2], [2,1,0,-1,-2]]), dtype="int")

laplacian_kernel_3x3 = np.array((
        [ [0,-1,0], [-1,4,-1], [0,-1,0]]), dtype="int")
laplacian_kernel_5x5 = np.array((
        [ [0,0,-1,0,0], [0,-1,-2,-1,0], [-1,-2,32,-2,-1], [0,-1,-2,-1,0], [0,0,-1,0,0]]), dtype="int")