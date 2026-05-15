import os
import numpy as np
from numba import njit
from scipy.spatial.transform import Rotation as R
import time

tic = time.time()

input_file = "ANG_files/output_1x1x1.ang"

misori_threshold = 3
compare_with_dream3d = True
warming_up = True


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

# ------------------------------------------------------------
# Numba warm-up
# This avoids including JIT compilation time in the processing time.
# ------------------------------------------------------------
if warming_up:
    idx_grid_dummy = np.full((3, 3, 3), -1, dtype=np.int32)
    idx_grid_dummy[1, 1, 1] = 0
    q_raw_dummy = np.array([[1.0, 0.0, 0.0, 0.0]], dtype=np.float64)
    img_lv_dummy, label_parent_dummy, n_labels_dummy = first_pass_ccl(idx_grid_dummy, q_raw_dummy, cubic_symmetry_quaternions, cos_half_misorientation_threshold)
    feature_ids_dummy, n_grains_dummy = resolve_equivalence(img_lv_dummy, label_parent_dummy, n_labels_dummy)

tic_proc = time.time()
img_lv_pad, label_parent, n_labels = first_pass_ccl(idx_grid, q_raw, cubic_symmetry_quaternions, cos_half_misorientation_threshold)
feature_ids_pad, n_grains = resolve_equivalence(img_lv_pad, label_parent, n_labels)

t_out = []
# remove zero padding
for n in range(3):
    toc_proc = time.time()
    feature_ids = feature_ids_pad[1:-1, 1:-1, 1:-1]
    t_out.append(toc_proc - tic_proc)

t_out_mean = np.mean(t_out)
print("Processing time:", t_out_mean)
print("Number of provisional labels:", n_labels)
print("Number of grains:", n_grains)
toc = time.time()
print("Total time:", toc - tic)

#%%
mt = input_file[input_file.rfind('_')+1:input_file.rfind('.ang')]
if compare_with_dream3d:

    t0 = time.time()

    # ------------------------------------------------------------
    # Load Dream3D Feature IDs
    # ------------------------------------------------------------
    # Here we assume that the voxel order in Dream3D Featureids.txt
    # is identical to the order of feature_ids.ravel().
    #
    # In other words:
    #
    #     CCL_id[i] and d3d_id[i]
    #
    # must correspond to the same voxel position.
    #
    # Therefore, x.txt, y.txt, and z.txt are not loaded here.
    # The coordinate order should be checked separately, only once,
    # before repeated benchmarking.
    # ------------------------------------------------------------
    file_Featureids = os.path.join("D3D_out", mt, "Featureids.txt")

    d3d_id = np.fromfile(file_Featureids, sep=" ", dtype=np.int32)

    # ------------------------------------------------------------
    # Flatten CCL result
    # ------------------------------------------------------------
    # feature_ids is assumed to have the same voxel order as the
    # Dream3D Featureids output.
    #
    # The actual label numbers do not need to be identical between
    # CCL and Dream3D. Only the voxel grouping must be compared.
    # ------------------------------------------------------------
    CCL_id = feature_ids.ravel().astype(np.int32, copy=False)

    # ------------------------------------------------------------
    # Basic size check
    # ------------------------------------------------------------
    # If the number of voxels is different, the two results cannot
    # be compared directly.
    # ------------------------------------------------------------
    if CCL_id.size != d3d_id.size:
        raise ValueError(
            f"Size mismatch: CCL_id.size={CCL_id.size}, "
            f"d3d_id.size={d3d_id.size}"
        )

    print("load time:", time.time() - t0)

    t1 = time.time()

    # ------------------------------------------------------------
    # Compress label values
    # ------------------------------------------------------------
    # Dream3D and the present CCL code may assign different numerical
    # labels to the same grain.
    #
    # Example:
    #
    #     CCL label      : 1, 1, 1, 2, 2, 2
    #     Dream3D label : 5, 5, 5, 8, 8, 8
    #
    # These are different label numbers, but the segmentation is the
    # same if the voxel grouping is identical.
    #
    # np.unique(..., return_inverse=True) converts arbitrary label
    # values into continuous indices:
    #
    #     ccl_inv : 0, 0, 0, 1, 1, 1, ...
    #     d3d_inv : 0, 0, 0, 1, 1, 1, ...
    #
    # This makes the following pair-based comparison independent of
    # the actual label numbers.
    # ------------------------------------------------------------
    ccl_labels, ccl_inv = np.unique(CCL_id, return_inverse=True)
    d3d_labels, d3d_inv = np.unique(d3d_id, return_inverse=True)

    n_ccl = len(ccl_labels)
    n_d3d = len(d3d_labels)

    # ------------------------------------------------------------
    # Build CCL-Dream3D label pairs for all voxels
    # ------------------------------------------------------------
    # For each voxel, we record the pair:
    #
    #     (CCL label index, Dream3D label index)
    #
    # Instead of storing a 2-column array, the pair is converted into
    # a single integer index:
    #
    #     pair_idx = ccl_inv * n_d3d + d3d_inv
    #
    # Therefore, each unique value in pair_idx represents one unique
    # overlap relation between a CCL grain and a Dream3D grain.
    # ------------------------------------------------------------
    pair_idx = ccl_inv.astype(np.int64) * n_d3d + d3d_inv.astype(np.int64)

    unique_pairs = np.unique(pair_idx)

    # ------------------------------------------------------------
    # Exact segmentation equivalence check
    # ------------------------------------------------------------
    # If the two segmentations are exactly the same up to relabeling,
    # each CCL grain should correspond to exactly one Dream3D grain,
    # and each Dream3D grain should correspond to exactly one CCL grain.
    #
    # Therefore, the number of unique CCL-Dream3D pairs must be equal
    # to both:
    #
    #     number of CCL labels
    #     number of Dream3D labels
    #
    # Interpretation:
    #
    #     unique_pairs.size == n_ccl == n_d3d
    #         -> same segmentation up to label renumbering
    #
    #     unique_pairs.size > n_ccl
    #         -> at least one CCL grain overlaps multiple Dream3D grains
    #            CCL may have merged grains compared with Dream3D
    #
    #     unique_pairs.size > n_d3d
    #         -> at least one Dream3D grain overlaps multiple CCL grains
    #            CCL may have split grains compared with Dream3D
    # ------------------------------------------------------------
    exact_same_segmentation = (
        unique_pairs.size == n_ccl and
        unique_pairs.size == n_d3d
    )

    print("comparison time:", time.time() - t1)

    # ------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------
    # This comparison checks whether the voxel grouping is identical,
    # not whether the numerical label IDs are identical.
    # ------------------------------------------------------------
    print("Number of CCL grains:", n_ccl)
    print("Number of Dream3D grains:", n_d3d)
    print("Number of unique CCL-Dream3D pairs:", unique_pairs.size)
    print("Exactly same segmentation:", exact_same_segmentation)
    print("total comparison time:", time.time() - t0)
    

