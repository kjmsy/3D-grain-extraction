import numpy as np
from scipy.spatial.transform import Rotation as R

# ============================================================
# User settings
# ============================================================
input_file = "input_txt/example_01.txt"
output_file = "ANG_files/output_2x2x2.ang"

mx = 2
my = 2
mz = 2

# Expansion factors
# Final size becomes:
# nx_new = nx_original * mx
# ny_new = ny_original * my
# nz_new = nz_original * mz


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
coord_decimals = 10

# ============================================================
# Read input file
#
# Expected columns:
# x y z u11 u12 u13 u21 u22 u23 u31 u32 u33
# ============================================================
x = []
y = []
z = []
u_mat = []

with open(input_file, "r", encoding="utf-8") as fid:
    header = fid.readline().split()

    for line_num, line in enumerate(fid, start=2):
        line_s = line.split()

        if not line_s:
            continue

        if len(line_s) < 12:
            raise ValueError(
                f"Line {line_num} has {len(line_s)} columns, "
                "but at least 12 columns are required."
            )

        x.append(float(line_s[0]))
        y.append(float(line_s[1]))
        z.append(float(line_s[2]))

        u = np.array([
            [float(line_s[3]),  float(line_s[4]),  float(line_s[5])],
            [float(line_s[6]),  float(line_s[7]),  float(line_s[8])],
            [float(line_s[9]),  float(line_s[10]), float(line_s[11])]
        ], dtype=float)

        u_mat.append(u)

x_a = np.asarray(x, dtype=float)
y_a = np.asarray(y, dtype=float)
z_a = np.asarray(z, dtype=float)
u_mat_a = np.asarray(u_mat, dtype=float)

n_points = len(x_a)

print("Input points:", n_points)


# ============================================================
# Convert orientation matrix to Euler angles in cubic FZ
#
# Output Euler angles are in radians.
# FZ condition used here:
#   0 <= phi1 <= 2pi
#   0 <= Phi  <= pi/2
#   0 <= phi2 <= pi/2
# ============================================================
Euler = []

for i, n in enumerate(u_mat_a):
    found = False

    for gs in cubic_symmetries:
        g = n @ gs

        r = R.from_matrix(g)
        e = r.as_euler("ZXZ", degrees=False)

        phi1 = np.mod(e[0], 2.0 * np.pi)
        Phi  = np.mod(e[1], 2.0 * np.pi)
        phi2 = np.mod(e[2], 2.0 * np.pi)

        if Phi > np.pi:
            Phi = 2.0 * np.pi - Phi

        if (
            0.0 <= phi1 <= 2.0 * np.pi
            and 0.0 <= Phi <= 0.5 * np.pi
            and 0.0 <= phi2 <= 0.5 * np.pi
        ):
            Euler.append([phi1, Phi, phi2])
            found = True
            break

    if not found:
        raise ValueError(
            f"No cubic-symmetry-equivalent Euler angle in the requested FZ "
            f"was found for index {i}."
        )

Euler = np.asarray(Euler, dtype=float)

phi1 = Euler[:, 0]
Phi  = Euler[:, 1]
phi2 = Euler[:, 2]


# ============================================================
# Build original ang-like data
#
# columns:
# 0 phi1
# 1 Phi
# 2 phi2
# 3 x
# 4 y
# 5 z
# 6 IQ
# 7 CI
# 8 Phase
# ============================================================
iq_col = np.full(n_points, 1.0, dtype=float)
ci_col = np.full(n_points, 1.0, dtype=float)
phase_col = np.full(n_points, 1.0, dtype=float)

d_out0 = np.column_stack([
    phi1, Phi, phi2,
    x_a, y_a, z_a,
    iq_col, ci_col, phase_col
])


# ============================================================
# Analyze original coordinate grid
# ============================================================
x_key = np.round(x_a, coord_decimals)
y_key = np.round(y_a, coord_decimals)
z_key = np.round(z_a, coord_decimals)

x_unique0 = np.sort(np.unique(x_key))
y_unique0 = np.sort(np.unique(y_key))
z_unique0 = np.sort(np.unique(z_key))

nx0 = len(x_unique0)
ny0 = len(y_unique0)
nz0 = len(z_unique0)

expected_points = nx0 * ny0 * nz0

print("Original grid size:")
print("nx0 =", nx0)
print("ny0 =", ny0)
print("nz0 =", nz0)
print("nx0 * ny0 * nz0 =", expected_points)

if expected_points != n_points:
    raise ValueError(
        "The input data are not a complete rectangular 3D grid.\n"
        f"Number of input points = {n_points}\n"
        f"nx0 * ny0 * nz0 = {expected_points}"
    )


# ============================================================
# Determine coordinate steps
# ============================================================
if nx0 > 1:
    x_step = np.median(np.diff(x_unique0))
else:
    x_step = 1.0

if ny0 > 1:
    y_step = np.median(np.diff(y_unique0))
else:
    y_step = 1.0

if nz0 > 1:
    z_step = np.median(np.diff(z_unique0))
else:
    z_step = 1.0

# Check whether the input grid is regular
if nx0 > 2:
    if not np.allclose(np.diff(x_unique0), x_step):
        raise ValueError("x coordinates are not regularly spaced.")

if ny0 > 2:
    if not np.allclose(np.diff(y_unique0), y_step):
        raise ValueError("y coordinates are not regularly spaced.")

if nz0 > 2:
    if not np.allclose(np.diff(z_unique0), z_step):
        raise ValueError("z coordinates are not regularly spaced.")

print("Original coordinate steps:")
print("x_step =", x_step)
print("y_step =", y_step)
print("z_step =", z_step)


# ============================================================
# Convert original data to a 3D grid
#
# grid0 shape:
#   [z, y, x, 9]
#
# This is important.
# DREAM3D usually expects the output data order as:
#   z fixed
#     y fixed
#       x increasing
# ============================================================
x_index = {v: i for i, v in enumerate(x_unique0)}
y_index = {v: i for i, v in enumerate(y_unique0)}
z_index = {v: i for i, v in enumerate(z_unique0)}

grid0 = np.full((nz0, ny0, nx0, 9), np.nan, dtype=float)

for row in d_out0:
    xval = np.round(row[3], coord_decimals)
    yval = np.round(row[4], coord_decimals)
    zval = np.round(row[5], coord_decimals)

    ix = x_index[xval]
    iy = y_index[yval]
    iz = z_index[zval]

    if not np.isnan(grid0[iz, iy, ix, 0]):
        raise ValueError(
            f"Duplicate coordinate found at x={row[3]}, y={row[4]}, z={row[5]}"
        )

    grid0[iz, iy, ix, :] = row

if np.isnan(grid0).any():
    raise ValueError("Some grid points were not filled. Check input coordinates.")


# ============================================================
# Expand the 3D grid
#
# np.tile order:
#   mz in z direction
#   my in y direction
#   mx in x direction
# ============================================================
grid_big = np.tile(grid0, (mz, my, mx, 1))

nx_big = nx0 * mx
ny_big = ny0 * my
nz_big = nz0 * mz

print("Expanded grid size:")
print("nx_big =", nx_big)
print("ny_big =", ny_big)
print("nz_big =", nz_big)
print("Total voxels =", nx_big * ny_big * nz_big)


# ============================================================
# Regenerate coordinates for the expanded grid
#
# Do not simply shift copied coordinates using x_max - x_min.
# That can produce duplicate boundary coordinates.
# Instead, regenerate all coordinates regularly.
# ============================================================
x_start = x_unique0[0]
y_start = y_unique0[0]
z_start = z_unique0[0]

x_big = x_start + np.arange(nx_big) * x_step
y_big = y_start + np.arange(ny_big) * y_step
z_big = z_start + np.arange(nz_big) * z_step

for iz in range(nz_big):
    grid_big[iz, :, :, 5] = z_big[iz]

for iy in range(ny_big):
    grid_big[:, iy, :, 4] = y_big[iy]

for ix in range(nx_big):
    grid_big[:, :, ix, 3] = x_big[ix]


# ============================================================
# Flatten to table
#
# C-order reshape from [z, y, x, column] gives:
#   x fastest
#   y second
#   z slowest
#
# However, we still do final explicit sorting below
# for DREAM3D compatibility.
# ============================================================
d_out = grid_big.reshape(-1, 9)


# ============================================================
# Final sorting for DREAM3D-compatible ang ordering
#
# np.lexsort((x, y, z)) means:
#   primary key   = z
#   secondary key = y
#   tertiary key  = x
#
# Therefore the final order is:
#   z increasing
#     y increasing
#       x increasing
# ============================================================
x_sort = np.round(d_out[:, 3], coord_decimals)
y_sort = np.round(d_out[:, 4], coord_decimals)
z_sort = np.round(d_out[:, 5], coord_decimals)

sort_idx = np.lexsort((x_sort, y_sort, z_sort))
d_out = d_out[sort_idx]


# ============================================================
# Final checks
# ============================================================
x_unique = np.sort(np.unique(np.round(d_out[:, 3], coord_decimals)))
y_unique = np.sort(np.unique(np.round(d_out[:, 4], coord_decimals)))
z_unique = np.sort(np.unique(np.round(d_out[:, 5], coord_decimals)))

if len(x_unique) != nx_big:
    raise ValueError("Final x grid size is inconsistent.")

if len(y_unique) != ny_big:
    raise ValueError("Final y grid size is inconsistent.")

if len(z_unique) != nz_big:
    raise ValueError("Final z grid size is inconsistent.")

if d_out.shape[0] != nx_big * ny_big * nz_big:
    raise ValueError("Final voxel number is inconsistent.")

print("Final data shape:", d_out.shape)


# ============================================================
# Write expanded ang file
# ============================================================
header_lines = [
    "# TEM_PIXperUM          1.000000",
    "# x-star                0.000000",
    "# y-star                0.000000",
    "# z-star                1.000000",
    "# WorkingDistance       0.000000",
    f"# XSTEP                 {x_step:.6f}",
    f"# YSTEP                 {y_step:.6f}",
    f"# NCOLS_ODD             {nx_big}",
    f"# NCOLS_EVEN            {nx_big}",
    f"# NROWS                 {ny_big}",
    f"# NZ                    {nz_big}",
    "# OPERATOR              ",
    "# SAMPLEID              ",
    "# SCANID                ",
]

with open(output_file, "w", encoding="utf-8") as f:
    for line in header_lines:
        f.write(line + "\n")

    for row in d_out:
        f.write(
            f"{row[0]:.6f} {row[1]:.6f} {row[2]:.6f} "
            f"{row[3]:.6f} {row[4]:.6f} {row[5]:.6f} "
            f"{row[6]:.1f} {row[7]:.1f} {int(row[8])}\n"
        )

print("Expanded .ang file written to:", output_file)