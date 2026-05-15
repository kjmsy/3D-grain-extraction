import numpy as np
from numba import njit
from scipy.spatial.transform import Rotation as R
import time
import matplotlib.pyplot as plt
import math

tic = time.time()

input_file = "ANG_files/output_1x1x1.ang"
misori_threshold = 3 #degree unit, equal or greater
ipf_sel = 'ipf_z' #'ipf_x', 'ipf_y', 'ipf_z'
phase = 0     # 0 / 1 / 2 : cubic / hexagonal / tetragonal
grain_size_threshold = 1

grain_ni = 1 #0 to plot all grains
grain_nf = 1 #-2 to plot all grains

sym_num = 0 #0 to 23


# ============================================================
# 1. 24 proper cubic symmetry matrices
# ============================================================
cubic_symmetries = np.array([
    [[ 1,  0,  0], [ 0,  1,  0], [ 0,  0,  1]],
    [[ 1,  0,  0], [ 0,  0, -1], [ 0,  1,  0]],
    [[ 1,  0,  0], [ 0, -1,  0], [ 0,  0, -1]],
    [[ 1,  0,  0], [ 0,  0,  1], [ 0, -1,  0]],

    [[-1,  0,  0], [ 0, -1,  0], [ 0,  0,  1]],
    [[-1,  0,  0], [ 0,  1,  0], [ 0,  0, -1]],
    [[-1,  0,  0], [ 0,  0, -1], [ 0, -1,  0]],
    [[-1,  0,  0], [ 0,  0,  1], [ 0,  1,  0]],

    [[ 0, -1,  0], [-1,  0,  0], [ 0,  0, -1]],
    [[ 0, -1,  0], [ 1,  0,  0], [ 0,  0,  1]],
    [[ 0,  1,  0], [-1,  0,  0], [ 0,  0,  1]],
    [[ 0,  1,  0], [ 1,  0,  0], [ 0,  0, -1]],

    [[ 0, -1,  0], [ 0,  0, -1], [ 1,  0,  0]],
    [[ 0, -1,  0], [ 0,  0,  1], [-1,  0,  0]],
    [[ 0,  1,  0], [ 0,  0, -1], [-1,  0,  0]],
    [[ 0,  1,  0], [ 0,  0,  1], [ 1,  0,  0]],

    [[ 0,  0, -1], [-1,  0,  0], [ 0,  1,  0]],
    [[ 0,  0, -1], [ 1,  0,  0], [ 0, -1,  0]],
    [[ 0,  0,  1], [-1,  0,  0], [ 0, -1,  0]],
    [[ 0,  0,  1], [ 1,  0,  0], [ 0,  1,  0]],

    [[ 0,  0, -1], [ 0, -1,  0], [-1,  0,  0]],
    [[ 0,  0, -1], [ 0,  1,  0], [ 1,  0,  0]],
    [[ 0,  0,  1], [ 0, -1,  0], [ 1,  0,  0]],
    [[ 0,  0,  1], [ 0,  1,  0], [-1,  0,  0]],
], dtype=np.float64)


# ============================================================
# 1-1. Convert cubic symmetry matrices to quaternions
#
# SciPy returns quaternions in [x, y, z, w] order.
# In the Numba functions below, quaternions are stored as:
#
#     [w, x, y, z]
# ============================================================
sym_q_xyzw = R.from_matrix(cubic_symmetries).as_quat()

cubic_symmetry_quaternions = np.column_stack([
    sym_q_xyzw[:, 3],  # w
    sym_q_xyzw[:, 0],  # x
    sym_q_xyzw[:, 1],  # y
    sym_q_xyzw[:, 2],  # z
]).astype(np.float64)

# Quaternion criterion:
# theta <= threshold  <=>  |cos(theta/2)| >= cos(threshold/2)
cos_half_misorientation_threshold = np.cos(0.5 * np.deg2rad(misori_threshold))


# ============================================================
# 2. Misorientation threshold check under cubic symmetry
#
# Quaternion version.
#
# Matrix version:
#
#     delta = g1^T * g2
#     theta = min acos((trace(S * delta) - 1) / 2)
#
# Quaternion version:
#
#     q_delta = inv(q1) * q2
#     q_total = q_sym * q_delta
#
# For a unit quaternion q_total = [w, x, y, z],
#
#     cos(theta / 2) = |w|
#
# Therefore, theta <= threshold is equivalent to:
#
#     |w| >= cos(threshold / 2)
#
# Quaternions are stored as [w, x, y, z].
#
#     inv(q1) = [w1, -x1, -y1, -z1]
# ============================================================
@njit(inline='always', fastmath=True)
def misorientation_threshold_cubic(q1, q2, symmetry_quaternions, cos_half_misorientation_threshold):
    # q1 = [w1, x1, y1, z1]
    # q2 = [w2, x2, y2, z2]

    w1 = q1[0]
    x1 = q1[1]
    y1 = q1[2]
    z1 = q1[3]

    w2 = q2[0]
    x2 = q2[1]
    y2 = q2[2]
    z2 = q2[3]

    dw = w1*w2 + x1*x2 + y1*y2 + z1*z2
    dx = w1*x2 - x1*w2 - y1*z2 + z1*y2
    dy = w1*y2 + x1*z2 - y1*w2 - z1*x2
    dz = w1*z2 - x1*y2 + y1*x2 - z1*w2

    nsym = symmetry_quaternions.shape[0]

    for n in range(nsym):
        s = symmetry_quaternions[n]
        sw = s[0]
        sx = s[1]
        sy = s[2]
        sz = s[3]
        cos_half_angle = sw*dw - sx*dx - sy*dy - sz*dz

        if cos_half_angle < 0.0:
            cos_half_angle = -cos_half_angle

        if cos_half_angle >= cos_half_misorientation_threshold:
            return True

    return False


# ============================================================
# 3. Label-equivalence representation
#
# During the first raster scan, equivalence between conflicting
# provisional labels is recorded using `record_label_equivalence`.
#
# The equivalence relation is stored in `label_parent`.
# Each provisional label points to its representative root label,
# which is obtained by `find_root`.
#
# The array `label_rank` is used to keep the equivalence tree
# balanced when two root labels are merged.
#
# NOTE:
# - The structure operates on provisional labels, not voxel indices
# - `label_1` and `label_2` are provisional labels to be unified
# - `root_label_1` and `root_label_2` are their representative root labels
# - Equivalence is recorded incrementally during the first pass
# - The recorded equivalence is resolved in the second pass
#   by mapping each provisional label to its root label
# ============================================================
@njit(inline='always')
def find_root(label_parent, provisional_label):
    while label_parent[provisional_label] != provisional_label:
        label_parent[provisional_label] = label_parent[label_parent[provisional_label]]
        provisional_label = label_parent[provisional_label]
    return provisional_label


@njit(inline='always')
def record_label_equivalence(label_parent, label_rank, label_1, label_2):
    root_label_1 = find_root(label_parent, label_1)
    root_label_2 = find_root(label_parent, label_2)

    if root_label_1 == root_label_2:
        return

    if label_rank[root_label_1] < label_rank[root_label_2]:
        label_parent[root_label_1] = root_label_2

    elif label_rank[root_label_1] > label_rank[root_label_2]:
        label_parent[root_label_2] = root_label_1

    else:
        label_parent[root_label_2] = root_label_1
        label_rank[root_label_1] += 1


# ============================================================
# 4. First pass: provisional labeling and equivalence recording
#
# The volume is scanned in x–y–z raster order using zero padding
# to avoid boundary ambiguities. For each voxel, only previously
# visited neighbors in the half-mask (left, up, back) are examined.
#
# If no connected labeled neighbor is found, a new provisional
# label is assigned. If one or more connected neighbors exist,
# one label is assigned and equivalence between conflicting labels
# is recorded using `record_label_equivalence`.
#
# Quaternion version:
# - q_raw stores voxel orientations as quaternions [w, x, y, z]
# - symmetry_quaternions stores cubic symmetry operators as quaternions
#
# Optimized point:
# - No small array allocation inside the voxel loop.
# - Connected neighbor labels are stored using scalar variables.
# ============================================================
@njit
def first_pass_ccl(idx_grid, q_raw, symmetry_quaternions, cos_half_misorientation_threshold):
    nz_pad, ny_pad, nx_pad = idx_grid.shape

    # Provisional label volume
    img_lv = np.zeros((nz_pad, ny_pad, nx_pad), dtype=np.int32)

    # Label-equivalence table
    # Maximum provisional label count cannot exceed the number of occupied voxels
    n_voxels = q_raw.shape[0]
    label_parent = np.arange(n_voxels + 1, dtype=np.int32)
    label_rank = np.zeros(n_voxels + 1, dtype=np.int32)

    next_label = 1

    # z-y-x raster scan
    # x is the fastest-changing coordinate
    for z in range(1, nz_pad - 1):
        for y in range(1, ny_pad - 1):
            for x in range(1, nx_pad - 1):

                current_addr = idx_grid[z, y, x]

                if current_addr < 0:
                    continue

                q_current = q_raw[current_addr]

                # Current mask uses 3 previously visited neighbors:
                # left, up, back
                n_connected = 0
                connected_label_1 = 0
                connected_label_2 = 0
                connected_label_3 = 0

                # ====================================================
                # Check left neighbor: (z, y, x-1)
                # ====================================================
                left_addr = idx_grid[z, y, x - 1]

                if left_addr >= 0:
                    if misorientation_threshold_cubic(q_current, q_raw[left_addr], symmetry_quaternions, cos_half_misorientation_threshold):
                        left_label = img_lv[z, y, x - 1]

                        if left_label > 0:
                            connected_label_1 = left_label
                            n_connected = 1

                # ====================================================
                # Check up neighbor: (z, y-1, x)
                # ====================================================
                up_addr = idx_grid[z, y - 1, x]

                if up_addr >= 0:
                    if misorientation_threshold_cubic(q_current, q_raw[up_addr], symmetry_quaternions, cos_half_misorientation_threshold):
                        up_label = img_lv[z, y - 1, x]

                        if up_label > 0:
                            is_new_label = True

                            if n_connected >= 1:
                                if up_label == connected_label_1:
                                    is_new_label = False

                            if is_new_label:
                                if n_connected == 0:
                                    connected_label_1 = up_label
                                elif n_connected == 1:
                                    connected_label_2 = up_label
                                else:
                                    connected_label_3 = up_label

                                n_connected += 1

                # ====================================================
                # Check back neighbor: (z-1, y, x)
                # ====================================================
                back_addr = idx_grid[z - 1, y, x]

                if back_addr >= 0:
                    if misorientation_threshold_cubic(q_current, q_raw[back_addr], symmetry_quaternions, cos_half_misorientation_threshold):
                        back_label = img_lv[z - 1, y, x]

                        if back_label > 0:
                            is_new_label = True

                            if n_connected >= 1:
                                if back_label == connected_label_1:
                                    is_new_label = False

                            if n_connected >= 2:
                                if back_label == connected_label_2:
                                    is_new_label = False

                            if is_new_label:
                                if n_connected == 0:
                                    connected_label_1 = back_label
                                elif n_connected == 1:
                                    connected_label_2 = back_label
                                else:
                                    connected_label_3 = back_label

                                n_connected += 1

                # ====================================================
                # Assign provisional label
                # ====================================================

                # Case 1:
                # No connected labeled neighbors -> assign a new label
                if n_connected == 0:
                    img_lv[z, y, x] = next_label
                    next_label += 1

                # Case 2:
                # One or more connected labeled neighbors exist
                else:
                    # Choose one representative label
                    assigned_label = connected_label_1

                    if n_connected >= 2:
                        if connected_label_2 < assigned_label:
                            assigned_label = connected_label_2

                    if n_connected >= 3:
                        if connected_label_3 < assigned_label:
                            assigned_label = connected_label_3

                    # Assign the representative label to the current voxel
                    img_lv[z, y, x] = assigned_label

                    # Record equivalence between conflicting labels
                    if connected_label_1 != assigned_label:
                        record_label_equivalence(label_parent, label_rank, assigned_label, connected_label_1)

                    if n_connected >= 2:
                        if connected_label_2 != assigned_label:
                            record_label_equivalence(label_parent, label_rank, assigned_label, connected_label_2)

                    if n_connected >= 3:
                        if connected_label_3 != assigned_label:
                            record_label_equivalence(label_parent, label_rank, assigned_label, connected_label_3)

    return img_lv, label_parent, next_label - 1


# ============================================================
# 5. Resolve label equivalence (second pass)
#
# After the first raster scan, provisional labels may contain
# multiple labels corresponding to the same physical grain.
# In this step, the recorded label equivalence stored in
# `label_parent` is resolved so that all equivalent labels
# are mapped to a single representative root label.
#
# The labels are then compacted into a continuous sequence
# (1, 2, ..., n_grains) to generate the final grain map.
# ============================================================
@njit
def resolve_equivalence(img_lv, label_parent, n_labels):
    nzp, nyp, nxp = img_lv.shape

    # Resolve each provisional label to its representative root label
    for lab in range(1, n_labels + 1):
        label_parent[lab] = find_root(label_parent, lab)

    root_to_new = np.full(n_labels + 1, -1, dtype=np.int32)
    next_new = 1
    out = np.zeros((nzp, nyp, nxp), dtype=np.int32)

    for z in range(1, nzp - 1):
        for y in range(1, nyp - 1):
            for x in range(1, nxp - 1):
                lab = img_lv[z, y, x]

                if lab > 0:
                    root = label_parent[lab]

                    if root_to_new[root] == -1:
                        root_to_new[root] = next_new
                        next_new += 1

                    out[z, y, x] = root_to_new[root]

    return out, next_new - 1


# ============================================================
# 6. Read input data
#    Coordinates are remapped to contiguous grid indices
# ============================================================
def read_ang_file(filename):
    phi1 = []
    Phi  = []
    phi2 = []
    x = []
    y = []
    z = []

    with open(filename, 'r') as f:
        for line in f:
            # header skip
            if line.startswith('#'):
                continue

            vals = line.split()

            if len(vals) < 6:
                continue

            phi1.append(float(vals[0]))
            Phi.append(float(vals[1]))
            phi2.append(float(vals[2]))

            x.append(float(vals[3]))
            y.append(float(vals[4]))
            z.append(float(vals[5]))

    phi1 = np.array(phi1)
    Phi  = np.array(Phi)
    phi2 = np.array(phi2)

    x = np.array(x, dtype=np.float64)
    y = np.array(y, dtype=np.float64)
    z = np.array(z, dtype=np.float64)

    return phi1, Phi, phi2, x, y, z


# ------------------------------------------------------------
# Convert Bunge ZXZ Euler angles to quaternions
# ------------------------------------------------------------
# This function converts an array of Euler angles in the ZXZ convention
# into quaternions using the same output order as scipy:
#
#     R.from_euler('ZXZ', eulers, degrees=False).as_quat()
#
# Input:
#     eulers : ndarray, shape (N, 3)
#         eulers[:, 0] = phi1
#         eulers[:, 1] = Phi
#         eulers[:, 2] = phi2
#
# Output:
#     out : ndarray, shape (N, 4)
#         out[:, 0] = qx
#         out[:, 1] = qy
#         out[:, 2] = qz
#         out[:, 3] = qw
#
# Notes:
#     - The Euler angles must be given in radians.
#     - The quaternion order is (x, y, z, w), not (w, x, y, z).
#     - This avoids scipy Rotation object creation and is faster for
#       large arrays.
# ------------------------------------------------------------
@njit(fastmath=True)
def euler_zxz_to_quat_xyzw_numba(eulers):
    """
    eulers shape: (N, 3)
    output shape: (N, 4)
    """

    N = eulers.shape[0]
    out = np.empty((N, 4), dtype=eulers.dtype)

    for i in range(N):
        phi1 = eulers[i, 0]
        Phi  = eulers[i, 1]
        phi2 = eulers[i, 2]

        half_Phi  = 0.5 * Phi
        half_sum  = 0.5 * (phi1 + phi2)
        half_diff = 0.5 * (phi1 - phi2)

        s = np.sin(half_Phi)
        c = np.cos(half_Phi)

        out[i, 0] = s * np.cos(half_diff)
        out[i, 1] = s * np.sin(half_diff)
        out[i, 2] = c * np.sin(half_sum)
        out[i, 3] = c * np.cos(half_sum)

    return out



def euler_bunge_to_g(phi1, Phi, phi2):
    """
    Convert Bunge Euler angles (phi1, Phi, phi2) to orientation matrix U.

    Parameters
    ----------
    phi1, Phi, phi2 : array_like
        Euler angles in radians.
        They can be scalars or NumPy arrays of the same shape.

    Returns
    -------
    U : ndarray
        Orientation matrices with shape (..., 3, 3)
    """

    phi1 = np.asarray(phi1)
    Phi  = np.asarray(Phi)
    phi2 = np.asarray(phi2)

    c1 = np.cos(phi1)
    s1 = np.sin(phi1)
    c  = np.cos(Phi)
    s  = np.sin(Phi)
    c2 = np.cos(phi2)
    s2 = np.sin(phi2)

    g = np.empty(phi1.shape + (3, 3))

    g[..., 0, 0] =  c1 * c2 - s1 * s2 * c
    g[..., 0, 1] =  s1 * c2 + c1 * s2 * c
    g[..., 0, 2] =  s2 * s

    g[..., 1, 0] = -c1 * s2 - s1 * c2 * c
    g[..., 1, 1] = -s1 * s2 + c1 * c2 * c
    g[..., 1, 2] =  c2 * s

    g[..., 2, 0] =  s1 * s
    g[..., 2, 1] = -c1 * s
    g[..., 2, 2] =  c
    
    return g


#########################
class IPF_cal:
    # direc = 0 :  z-axis
    # direc = 1 :  x-axis
    # direc = 2 :  y-axis
    # phase = 0 :  cubic
    # phase = 1 :  hexagonal
    # phase = 2 :  tetragonal

    def __init__(self, u11, u12, u13, u21, u22, u23, u31, u32, u33, direct, phase):
        self.u11 = u11
        self.u12 = u12
        self.u13 = u13
        self.u21 = u21
        self.u22 = u22
        self.u23 = u23
        self.u31 = u31
        self.u32 = u32
        self.u33 = u33
        self.direct = direct
        self.phase = phase
        self.n_div = 500
    
    def set_axis(self):
        u2z = [self.u31, self.u32, self.u33]
        u2x = [self.u11, self.u12, self.u13]
        u2y = [self.u21, self.u22, self.u23]

        if self.direct == 1:
            axis = u2x 
        elif self.direct == 2 :
            axis = u2y
        else:
            axis = u2z
        return axis

    def tri_sym(self):
        x, y, z = self.set_axis()
        x0 = math.fabs(x)
        y0 = math.fabs(y)
        z0 = math.fabs(z)
        if self.phase == 0:
            if x0 < y0:
                x1 = y0
                y1 = x0
            else :
                x1 = x0
                y1 = y0
            z1 = z0
            if x1 > z1:
                if y1 > z1 :
                    x2 = y1
                    y2 = z1
                    z2 = x1
                else:
                    x2 = z1
                    y2 = y1
                    z2 = x1
            else:
                x2 = x1
                y2 = y1
                z2 = z1
            xi = 2 * x2 / (1 + z2)
            eta = 2 * y2 / (1 + z2)
            r = xi, eta
            
        elif self.phase == 1:
            if z >= 0:
                xi0= x / (1 + z)
                eta0= y / (1 + z)
            else :
                xi0 = -x / (1 - z)
                eta0 = -y / (1 - z)
            xi1 = math.fabs(xi0)
            eta1 = math.fabs(eta0)
            tan3 = math.tan(math.pi / 3)
            tan6 = math.tan(math.pi / 6)
            sin_p = math.sin(math.pi / 3)
            sin_m = math.sin(-math.pi / 3)
            cos_p = math.cos(math.pi / 3)
            cos_m = math.cos(-math.pi / 3)
            if eta1 > xi1 * tan3:
                xi2 = cos_m * xi1 - sin_m * eta1
                eta2 = sin_m * xi1 + cos_m * eta1
            elif eta1 > xi1 * tan6:
                xi2 = cos_p * xi1 + sin_p * eta1
                eta2 = sin_p * xi1 - cos_p * eta1
            else:
                xi2 = xi1
                eta2 = eta1
            r = xi2, eta2
        elif self.phase == 2:
            if x0 < y0 :
                x1 = y0
                y1 = x0
            else :
                x1 = x0
                y1 = y0
            z1 = z0
            xi = x1 / (1.0 + z1)
            eta = y1 / (1.0 + z1)
            r = xi, eta
        return r
    
    def tri2RGB_sym(self):
        x, y = self.tri_sym()
        if self.phase == 0:
            x1 = 0.0
            y1 = 0.0
            x2 = 0.82843
            y2 = 0.0
            x3 = 0.73059
            y3 = 0.73059
            
        elif self.phase == 1:
            x1 = 0.0
            y1 = 0.0
            x2 = 1.0
            y2 = 0.0
            x3 = 0.866
            y3 = 0.50

        elif self.phase == 2:
            x1 = 0.0
            y1 = 0.0
            x2 = 1.0
            y2 = 0.0
            x3 = 0.7071068
            y3 = x3

        R12 = x2
        R31 = math.sqrt(x3 * x3 + y3 * y3)
        r1 = math.sqrt((x - x1) * (x - x1) + (y - y1) * (y - y1))
        r2 = math.sqrt((x - x2) * (x - x2) + (y - y2) * (y - y2))
        r3 = math.sqrt((x - x3) * (x - x3) + (y - y3) * (y - y3))
        R = 1.0 - r1 / R31
        G = 1.0 - r2 / R12
        B = 1.0 - r3 / R31
        return math.fabs(R), math.fabs(G), math.fabs(B)
        

    def tri2RGB_sym_2(self, x, y):
        if self.phase == 0:
            x1 = 0.0
            y1 = 0.0
            x2 = 0.82843
            y2 = 0.0
            x3 = 0.73059
            y3 = 0.73059
            
        elif self.phase == 1:
            x1 = 0.0
            y1 = 0.0
            x2 = 1.0
            y2 = 0.0
            x3 = 0.866
            y3 = 0.50

        elif self.phase == 2:
            x1 = 0.0
            y1 = 0.0
            x2 = 1.0
            y2 = 0.0
            x3 = 0.7071068
            y3 = x3

        R12 = x2
        R31 = math.sqrt(x3 * x3 + y3 * y3)
        r1 = math.sqrt((x - x1) * (x - x1) + (y - y1) * (y - y1))
        r2 = math.sqrt((x - x2) * (x - x2) + (y - y2) * (y - y2))
        r3 = math.sqrt((x - x3) * (x - x3) + (y - y3) * (y - y3))
        R = 1.0 - r1 / R31
        G = 1.0 - r2 / R12
        B = 1.0 - r3 / R31
        
        return math.fabs(R), math.fabs(G), math.fabs(B)

    def show_RGB(self):
        n_div = 3
        rgb = 1.0,1.0,1.0
        c = [[rgb for j in range (n_div)] for i in range (n_div)]
        RGB = self.tri2RGB_sym()
        R = RGB[0]
        G = RGB[1]
        B = RGB[2]
        c[1][1] = R, G, B
        print(R, G, B)
        im = plt.imshow(c, origin='lower',interpolation='nearest')
        plt.show()
        return im
    
    def show_RGB_basic_tri_sym(self):
        n_div = self.n_div
        n_shift=int(n_div*0.1)        
        rgb = 1.0,1.0,1.0
        if self.phase == 0:
            x3=0.73059     
            z = [[rgb for j in range (n_div)] for i in range (n_div)]
            for ix in range(n_div):
                for iy in range(n_div):
                    x=float(ix) / float(n_div)
                    y=float(iy) / float(n_div)
                    if x <= x3:
                        if y <= x:
                            z[iy+n_shift][ix+n_shift]= self.tri2RGB_sym_2(x, y)
                    else :
                        if y * y <= 8 - (x + 2) * (x + 2):
                            z[iy+n_shift][ix+n_shift]= self.tri2RGB_sym_2(x, y)
        elif self.phase == 1:
            x3 = 0.866
            z = [[rgb for j in range (n_div + n_shift * 2)] for i in range (n_div + n_shift * 2)]

            for ix in range(n_div):
                for iy in range(n_div):
                    x=float(ix) / float(n_div)
                    y=float(iy) / float(n_div)
                    if x <= x3:
                        if y <= x * math.tan(math.pi / 6):
                            z[iy + n_shift][ix + n_shift] = self.tri2RGB_sym_2(x, y)
                    else :
                        if y * y <= 1 - x * x :
                            z[iy + n_shift][ix + n_shift]= self.tri2RGB_sym_2(x, y)
            
        elif self.phase == 2:
            x3 = 0.7071068
            z = [[rgb for j in range (n_div + n_shift * 2)] for i in range (n_div + n_shift * 2)]
            for ix in range(n_div):
                for iy in range(n_div):
                    x=float(ix)/float(n_div)
                    y=float(iy)/float(n_div)
                    if x <= x3:
                        if y <= x:
                            z[iy + n_shift][ix + n_shift]= self.tri2RGB_sym_2(x, y)
                    else :
                        if y * y <= 1 - x * x :
                            z[iy + n_shift][ix + n_shift]= self.tri2RGB_sym_2(x, y)
        im = plt.imshow(z,origin='lower', interpolation='nearest')
        plt.show()
        return im

#%%
# ------------------------------------------------------------
# Input data preparation
# ------------------------------------------------------------
phi1, Phi, phi2, x_raw, y_raw, z_raw = read_ang_file(input_file)
if x_raw.size == 0:
    raise ValueError("No data points were read from the .ang file.")

# ------------------------------------------------------------
# Euler angles -> orientation quaternions
# ------------------------------------------------------------
# IMPORTANT:
# This convention must match the one used to generate the .ang file.
# Here ZXZ with radians is assumed.
#
# SciPy returns quaternions as [x, y, z, w].
# The Numba functions use [w, x, y, z].
# ------------------------------------------------------------
eulers = np.column_stack((phi1, Phi, phi2))
q_xyzw = euler_zxz_to_quat_xyzw_numba(eulers)

# If your .ang angles are in degrees, use this instead:
# q_xyzw = R.from_euler('ZXZ', eulers, degrees=True).as_quat()

q_raw = np.column_stack([
    q_xyzw[:, 3],  # w
    q_xyzw[:, 0],  # x
    q_xyzw[:, 1],  # y
    q_xyzw[:, 2],  # z
]).astype(np.float64)

# ------------------------------------------------------------
# Remap coordinates to contiguous integer grid indices
# ------------------------------------------------------------
x_unique, x_idx = np.unique(x_raw, return_inverse=True)
y_unique, y_idx = np.unique(y_raw, return_inverse=True)
z_unique, z_idx = np.unique(z_raw, return_inverse=True)

nx = x_unique.size
ny = y_unique.size
nz = z_unique.size

idx_grid = np.full((nz + 2, ny + 2, nx + 2), -1, dtype=np.int32)

N = q_raw.shape[0]

zz = z_idx.astype(np.int64, copy=False) + 1
yy = y_idx.astype(np.int64, copy=False) + 1
xx = x_idx.astype(np.int64, copy=False) + 1

lin_idx = zz * ((ny + 2) * (nx + 2)) + yy * (nx + 2) + xx

counts = np.bincount(lin_idx, minlength=idx_grid.size)
dup_lin = np.flatnonzero(counts > 1)

if dup_lin.size > 0:
    dup_pos = np.flatnonzero(lin_idx == dup_lin[0])
    i = dup_pos[0]

    raise ValueError(
        f"Duplicate voxel detected at raw coordinate "
        f"(x={x_raw[i]}, y={y_raw[i]}, z={z_raw[i]})"
    )

idx_grid.ravel()[lin_idx] = np.arange(N, dtype=np.int32)

#%%
# ============================================================
# 7. First pass + second pass
# ============================================================

img_lv_pad, label_parent, n_labels = first_pass_ccl(idx_grid, q_raw, cubic_symmetry_quaternions, cos_half_misorientation_threshold)
feature_ids_pad, n_grains = resolve_equivalence(img_lv_pad, label_parent, n_labels)

# remove zero padding
feature_ids = feature_ids_pad[1:-1, 1:-1, 1:-1]
g_mat = euler_bunge_to_g(phi1, Phi, phi2)

#%%

s = IPF_cal(0, 0, 0, 0, 0, 0, 0, 0, 0, 1, phase)
rgb_x = []
rgb_y = []
rgb_z = []

for g in g_mat:
    u = g.T
    s.u11 = u[0][0]
    s.u12 = u[0][1]
    s.u13 = u[0][2]
    s.u21 = u[1][0]
    s.u22 = u[1][1]
    s.u23 = u[1][2]
    s.u31 = u[2][0]
    s.u32 = u[2][1]
    s.u33 = u[2][2]
    s.direct = 1
    tc_x0 = s.tri_sym()
    rgb_x.append(s.tri2RGB_sym())
    
    s.direct = 2
    rgb_y.append(s.tri2RGB_sym())
    tc_y0 = s.tri_sym()
    
    s.direct = 0
    rgb_z.append(s.tri2RGB_sym())
    tc_z0 = s.tri_sym()

rgb_x = np.array(rgb_x)
rgb_y = np.array(rgb_y)
rgb_z = np.array(rgb_z)

g_mat_dummy = np.array([[[0, 0, 0], [0, 0, 0], [0, 0, 0]]])
rgb_x_dummy = np.array([[0, 0, 0]])
rgb_y_dummy = np.array([[0, 0, 0]])
rgb_z_dummy = np.array([[0, 0, 0]])

idx_map = idx_grid[1:-1, 1:-1, 1:-1]

grain_list = []
grain_vol = []

for lab in range(1, n_grains + 1):

    g_addr = np.where(feature_ids == lab)

    if len(g_addr[0]) == 0:
        continue

    z_grid = g_addr[0]
    y_grid = g_addr[1]
    x_grid = g_addr[2]
    raw_addr = idx_map[g_addr]

    # safety check
    valid = raw_addr >= 0
    if not np.all(valid):
        z_grid = z_grid[valid]
        y_grid = y_grid[valid]
        x_grid = x_grid[valid]
        raw_addr = raw_addr[valid]

    grain_ext = [
        x_grid.astype(np.int64),    # voxel x index
        y_grid.astype(np.int64),    # voxel y index
        z_grid.astype(np.int64),    # voxel z index
        g_mat[raw_addr],            # orientation matrix
        rgb_x[raw_addr],            # IPF-x color
        rgb_y[raw_addr],            # IPF-y color
        rgb_z[raw_addr],            # IPF-z color
        lab                         # original grain label
    ]

    grain_list.append(grain_ext)
    grain_vol.append(len(raw_addr))

#%%
grain_list_refined = []
grain_vol_refined = []

for grain in grain_list:
    if len(grain[0]) >= grain_size_threshold:
        grain_list_refined.append(grain)
        grain_vol_refined.append(len(grain[0]))

sel_dict = {
    "ipf_x": 4,
    "ipf_y": 5,
    "ipf_z": 6,
}

if ipf_sel not in sel_dict:
    raise ValueError("ipf_sel must be 'ipf_x', 'ipf_y', or 'ipf_z'.")

sel = sel_dict[ipf_sel]

grains_sorted = sorted(
    grain_list_refined,
    key=lambda g: len(g[0]),
    reverse=True
)

grains = grains_sorted[grain_ni:grain_nf+1]

r = np.full((nx, ny, nz), np.nan, dtype=np.float64)
g = np.full((nx, ny, nz), np.nan, dtype=np.float64)
b = np.full((nx, ny, nz), np.nan, dtype=np.float64)

for grain_sel in grains:
    xs = grain_sel[0]
    ys = grain_sel[1]
    zs = grain_sel[2]

    colors = grain_sel[sel]

    r[xs, ys, zs] = colors[:, 0]
    g[xs, ys, zs] = colors[:, 1]
    b[xs, ys, zs] = colors[:, 2]

filled = ~np.isnan(r)

alpha = np.zeros_like(r)
alpha[filled] = 1.0

rgb = np.stack(
    [
        np.nan_to_num(r, nan=0.0),
        np.nan_to_num(g, nan=0.0),
        np.nan_to_num(b, nan=0.0),
        alpha,
    ],
    axis=-1
)

rgb = np.clip(rgb, 0.0, 1.0)

#%%

fig = plt.figure(figsize=(6, 6))
ax = fig.add_subplot(111, projection="3d")

ax.voxels(filled, facecolors=rgb, edgecolor=None)

ax.set_xlabel("X", fontsize=12)
ax.set_ylabel("Y", fontsize=12)
ax.set_zlabel("Z", fontsize=12)

ax.set_xlim([-1, nx + 1])
ax.set_ylim([-1, ny + 1])
ax.set_zlim([-1, nz + 1])

ax.set_box_aspect((nx, ny, nz))

fig.tight_layout()
plt.show()
