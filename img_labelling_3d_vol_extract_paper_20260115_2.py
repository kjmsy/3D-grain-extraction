input_file = "example_01.txt"
misori_threshold = 3 #degree unit, equal or greater
ipf_sel = 'ipf_z' #'ipf_x', 'ipf_y', 'ipf_z'
phase = 0     # 0 / 1 / 2 : cubic / hexagonal / tetragonal
grain_size_threshold = 1

#%% 
import numpy as np
import matplotlib.pyplot as plt
import math
import networkx as nx
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401


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


def tri2xyz(xi, eta):
    psi = xi * xi + eta * eta
    z = (4.0 - psi) / (4.0 + psi)
    sin_alpha = math.sin(math.acos(z))
    try:
        beta = math.atan(eta / xi)
    except:
        beta = 0
    sin_beta = math.sin(beta)
    cos_beta = math.cos(beta)
    y = sin_alpha * sin_beta
    x = sin_alpha * cos_beta
    return x, y, z

def tri2misori(xi0, eta0, xi1, eta1):
    x0, y0, z0 = tri2xyz( xi0, eta0 )
    x1, y1, z1 = tri2xyz( xi1, eta1 )
    r = x0 * x1 + y0 * y1 + z0 * z1
    if r > 1:
        r = 1
    misori_rad = math.acos(r)
    misori_deg = misori_rad * 180.0 / math.pi
    return misori_deg

#%%

s = IPF_cal(0, 0, 0, 0, 0, 0, 0, 0, 0, 1, phase)
fid = open(input_file, 'r')
header = fid.readline().split()
x = []
y = []
z = []
u_mat = []
rgb_x = []
rgb_y = []
rgb_z = []
tri_cubic_x0 = []
tri_cubic_y0 = []
tri_cubic_z0 = []
while True:
    line = fid.readline()
    if not line: 
        break
    line_s = line.split()
    x.append(float(line_s[0]))
    y.append(float(line_s[1]))
    z.append(float(line_s[2]))
    u = np.array([[float(line_s[3]), float(line_s[4]), float(line_s[5])],
                  [float(line_s[6]), float(line_s[7]), float(line_s[8])],
                  [float(line_s[9]), float(line_s[10]), float(line_s[11])]])
    u_mat.append(u)
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
    tri_cubic_x0.append([tc_x0[0], tc_x0[1]])
    
    s.direct = 2
    rgb_y.append(s.tri2RGB_sym())
    tc_y0 = s.tri_sym()
    tri_cubic_y0.append([tc_y0[0], tc_y0[1]])
    
    s.direct = 0
    rgb_z.append(s.tri2RGB_sym())
    tc_z0 = s.tri_sym()
    tri_cubic_z0.append([tc_z0[0], tc_z0[1]])

fid.close()


x_a = np.array(x, dtype=np.int32)
y_a = np.array(y, dtype=np.int32)
z_a = np.array(z, dtype=np.int32)

x_a = x_a - np.min(x_a)
y_a = y_a - np.min(y_a)
z_a = z_a - np.min(z_a)

u_mat_a = np.array(u_mat)
rgb_x_a = np.array(rgb_x)
rgb_y_a = np.array(rgb_y)
rgb_z_a = np.array(rgb_z)
x_min = np.array(x_a).min()
y_min = np.array(y_a).min()
z_min = np.array(z_a).min()
x_max = np.array(x_a).max()
y_max = np.array(y_a).max()
z_max = np.array(z_a).max()
img_lv = np.zeros((y_max + 2, x_max + 2, z_max + 2))
img_in = np.zeros((y_max + 2, x_max + 2, z_max + 2))*np.nan
s_img = img_in.shape

for m, n in enumerate(x):
    img_in[y_a[m] + 1, x_a[m] + 1, z_a[m] + 1] = m


#%%

r = []
s = 1
for ht in range(1, s_img[2]):
    for row in range(1, s_img[0]):
        for col in range(1, s_img[1]):
            if ~np.isnan(img_in[row, col, ht]):
                
                addr_c = int(img_in[row, col, ht])
                
                if np.isnan(img_in[row-1, col, ht]) & np.isnan(img_in[row, col-1, ht]) & np.isnan(img_in[row, col, ht - 1]):
                    img_lv[row, col, ht] = s
                    s = s + 1
                    r.append((img_lv[row, col, ht], img_lv[row,col, ht]))
                        

                elif ~np.isnan(img_in[row-1, col, ht]) & np.isnan(img_in[row, col-1, ht]) & np.isnan(img_in[row, col, ht - 1]):

                    tc_x0_c = tri_cubic_x0[addr_c]
                    tc_y0_c = tri_cubic_y0[addr_c]
                    tc_z0_c = tri_cubic_z0[addr_c]

                    addr_u = int(img_in[row - 1, col, ht])
                    tc_x0_u = tri_cubic_x0[addr_u]
                    tc_y0_u = tri_cubic_y0[addr_u]
                    tc_z0_u = tri_cubic_z0[addr_u]

                    tri2misori_x_cu = tri2misori(tc_x0_c[0], tc_x0_c[1], tc_x0_u[0], tc_x0_u[1])
                    tri2misori_y_cu = tri2misori(tc_y0_c[0], tc_y0_c[1], tc_y0_u[0], tc_y0_u[1])
                    tri2misori_z_cu = tri2misori(tc_z0_c[0], tc_z0_c[1], tc_z0_u[0], tc_z0_u[1])
                    tri2misori_cu = max(tri2misori_x_cu, tri2misori_y_cu, tri2misori_z_cu)

                    if (tri2misori_cu > misori_threshold):
                        img_lv[row, col, ht] = s
                        s = s + 1
                        r.append((img_lv[row, col, ht], img_lv[row, col, ht]))
                    elif (tri2misori_cu <= misori_threshold):
                        img_lv[row, col, ht] = img_lv[row -1, col, ht]
                

                elif np.isnan(img_in[row-1, col, ht]) & ~np.isnan(img_in[row, col-1, ht]) & np.isnan(img_in[row, col, ht - 1]):

                    tc_x0_c = tri_cubic_x0[addr_c]
                    tc_y0_c = tri_cubic_y0[addr_c]
                    tc_z0_c = tri_cubic_z0[addr_c]

                    addr_l = int(img_in[row, col - 1, ht])
                    tc_x0_l = tri_cubic_x0[addr_l]
                    tc_y0_l = tri_cubic_y0[addr_l]
                    tc_z0_l = tri_cubic_z0[addr_l]

                    tri2misori_x_cl = tri2misori(tc_x0_c[0], tc_x0_c[1], tc_x0_l[0], tc_x0_l[1])
                    tri2misori_y_cl = tri2misori(tc_y0_c[0], tc_y0_c[1], tc_y0_l[0], tc_y0_l[1])
                    tri2misori_z_cl = tri2misori(tc_z0_c[0], tc_z0_c[1], tc_z0_l[0], tc_z0_l[1])
                    tri2misori_cl = max(tri2misori_x_cl, tri2misori_y_cl, tri2misori_z_cl)

                    if (tri2misori_cl > misori_threshold):
                        img_lv[row, col, ht] = s
                        s = s + 1
                        r.append((img_lv[row, col, ht], img_lv[row, col, ht]))
                    elif (tri2misori_cl <= misori_threshold):
                        img_lv[row, col, ht] = img_lv[row, col - 1, ht]


                elif np.isnan(img_in[row-1, col, ht]) & np.isnan(img_in[row, col-1, ht]) & ~np.isnan(img_in[row, col, ht - 1]):

                    tc_x0_c = tri_cubic_x0[addr_c]
                    tc_y0_c = tri_cubic_y0[addr_c]
                    tc_z0_c = tri_cubic_z0[addr_c]

                    addr_h = int(img_in[row, col, ht - 1])
                    tc_x0_h = tri_cubic_x0[addr_h]
                    tc_y0_h = tri_cubic_y0[addr_h]
                    tc_z0_h = tri_cubic_z0[addr_h]
                    
                    tri2misori_x_ch = tri2misori(tc_x0_c[0], tc_x0_c[1], tc_x0_h[0], tc_x0_h[1])
                    tri2misori_y_ch = tri2misori(tc_y0_c[0], tc_y0_c[1], tc_y0_h[0], tc_y0_h[1])
                    tri2misori_z_ch = tri2misori(tc_z0_c[0], tc_z0_c[1], tc_z0_h[0], tc_z0_h[1])
                    tri2misori_ch = max(tri2misori_x_ch, tri2misori_y_ch, tri2misori_z_ch)

                    if (tri2misori_ch > misori_threshold):
                        img_lv[row, col, ht] = s
                        s = s + 1
                        r.append((img_lv[row, col, ht], img_lv[row, col, ht]))
                    elif (tri2misori_ch <= misori_threshold):
                        img_lv[row, col, ht] = img_lv[row, col, ht - 1]



                elif ~np.isnan(img_in[row-1, col, ht]) & ~np.isnan(img_in[row, col-1, ht]) & np.isnan(img_in[row, col, ht - 1]):

                    tc_x0_c = tri_cubic_x0[addr_c]
                    tc_y0_c = tri_cubic_y0[addr_c]
                    tc_z0_c = tri_cubic_z0[addr_c]

                    addr_u = int(img_in[row - 1, col, ht])
                    tc_x0_u = tri_cubic_x0[addr_u]
                    tc_y0_u = tri_cubic_y0[addr_u]
                    tc_z0_u = tri_cubic_z0[addr_u]

                    addr_l = int(img_in[row, col - 1, ht])
                    tc_x0_l = tri_cubic_x0[addr_l]
                    tc_y0_l = tri_cubic_y0[addr_l]
                    tc_z0_l = tri_cubic_z0[addr_l]
                    
                    tri2misori_x_cu = tri2misori(tc_x0_c[0], tc_x0_c[1], tc_x0_u[0], tc_x0_u[1])
                    tri2misori_y_cu = tri2misori(tc_y0_c[0], tc_y0_c[1], tc_y0_u[0], tc_y0_u[1])
                    tri2misori_z_cu = tri2misori(tc_z0_c[0], tc_z0_c[1], tc_z0_u[0], tc_z0_u[1])
                    tri2misori_cu = max(tri2misori_x_cu, tri2misori_y_cu, tri2misori_z_cu)

                    tri2misori_x_cl = tri2misori(tc_x0_c[0], tc_x0_c[1], tc_x0_l[0], tc_x0_l[1])
                    tri2misori_y_cl = tri2misori(tc_y0_c[0], tc_y0_c[1], tc_y0_l[0], tc_y0_l[1])
                    tri2misori_z_cl = tri2misori(tc_z0_c[0], tc_z0_c[1], tc_z0_l[0], tc_z0_l[1])
                    tri2misori_cl = max(tri2misori_x_cl, tri2misori_y_cl, tri2misori_z_cl)

                    if (tri2misori_cu > misori_threshold) & (tri2misori_cl > misori_threshold):
                        img_lv[row, col, ht] = s
                        s = s + 1
                        r.append((img_lv[row, col, ht], img_lv[row, col, ht]))
                    elif (tri2misori_cu <= misori_threshold) & (tri2misori_cl > misori_threshold):
                        img_lv[row, col, ht] = img_lv[row -1, col, ht]
                    elif (tri2misori_cu > misori_threshold) & (tri2misori_cl <= misori_threshold):
                        img_lv[row, col, ht] = img_lv[row, col - 1, ht]
                    elif (tri2misori_cu <= misori_threshold) & (tri2misori_cl <= misori_threshold):
                        img_lv[row, col, ht] = img_lv[row, col - 1, ht]
                        if img_lv[row - 1, col, ht] != img_lv[row, col - 1, ht]:
                                r.append((img_lv[row - 1, col, ht], img_lv[row, col - 1, ht]))
                

                elif ~np.isnan(img_in[row-1, col, ht]) & np.isnan(img_in[row, col-1, ht]) & ~np.isnan(img_in[row, col, ht - 1]):

                    tc_x0_c = tri_cubic_x0[addr_c]
                    tc_y0_c = tri_cubic_y0[addr_c]
                    tc_z0_c = tri_cubic_z0[addr_c]

                    addr_u = int(img_in[row-1, col, ht])
                    tc_x0_u = tri_cubic_x0[addr_u]
                    tc_y0_u = tri_cubic_y0[addr_u]
                    tc_z0_u = tri_cubic_z0[addr_u]

                    addr_h = int(img_in[row, col, ht - 1])
                    tc_x0_h = tri_cubic_x0[addr_h]
                    tc_y0_h = tri_cubic_y0[addr_h]
                    tc_z0_h = tri_cubic_z0[addr_h]
                    
                    tri2misori_x_cu = tri2misori(tc_x0_c[0], tc_x0_c[1], tc_x0_u[0], tc_x0_u[1])
                    tri2misori_y_cu = tri2misori(tc_y0_c[0], tc_y0_c[1], tc_y0_u[0], tc_y0_u[1])
                    tri2misori_z_cu = tri2misori(tc_z0_c[0], tc_z0_c[1], tc_z0_u[0], tc_z0_u[1])
                    tri2misori_cu = max(tri2misori_x_cu, tri2misori_y_cu, tri2misori_z_cu)

                    tri2misori_x_ch = tri2misori(tc_x0_c[0], tc_x0_c[1], tc_x0_h[0], tc_x0_h[1])
                    tri2misori_y_ch = tri2misori(tc_y0_c[0], tc_y0_c[1], tc_y0_h[0], tc_y0_h[1])
                    tri2misori_z_ch = tri2misori(tc_z0_c[0], tc_z0_c[1], tc_z0_h[0], tc_z0_h[1])
                    tri2misori_ch = max(tri2misori_x_ch, tri2misori_y_ch, tri2misori_z_ch)

                    if (tri2misori_cu > misori_threshold) & (tri2misori_ch > misori_threshold):
                        img_lv[row, col, ht] = s
                        s = s + 1
                        r.append((img_lv[row, col, ht], img_lv[row, col, ht]))
                    elif (tri2misori_cu <= misori_threshold) & (tri2misori_ch > misori_threshold):
                        img_lv[row, col, ht] = img_lv[row -1, col, ht]
                    elif (tri2misori_cu > misori_threshold) & (tri2misori_ch <= misori_threshold):
                        img_lv[row, col, ht] = img_lv[row, col, ht - 1]
                    elif (tri2misori_cu <= misori_threshold) & (tri2misori_ch <= misori_threshold):
                        img_lv[row, col, ht] = img_lv[row, col, ht - 1]
                        if img_lv[row - 1, col, ht] != img_lv[row, col, ht - 1]:
                                r.append((img_lv[row - 1, col, ht], img_lv[row, col, ht - 1]))


                elif np.isnan(img_in[row-1, col, ht]) & ~np.isnan(img_in[row, col-1, ht]) & ~np.isnan(img_in[row, col, ht - 1]):

                    tc_x0_c = tri_cubic_x0[addr_c]
                    tc_y0_c = tri_cubic_y0[addr_c]
                    tc_z0_c = tri_cubic_z0[addr_c]

                    addr_l = int(img_in[row, col - 1, ht])
                    tc_x0_l = tri_cubic_x0[addr_l]
                    tc_y0_l = tri_cubic_y0[addr_l]
                    tc_z0_l = tri_cubic_z0[addr_l]

                    addr_h = int(img_in[row, col, ht - 1])
                    tc_x0_h = tri_cubic_x0[addr_h]
                    tc_y0_h = tri_cubic_y0[addr_h]
                    tc_z0_h = tri_cubic_z0[addr_h]
                    
                    tri2misori_x_cl = tri2misori(tc_x0_c[0], tc_x0_c[1], tc_x0_l[0], tc_x0_l[1])
                    tri2misori_y_cl = tri2misori(tc_y0_c[0], tc_y0_c[1], tc_y0_l[0], tc_y0_l[1])
                    tri2misori_z_cl = tri2misori(tc_z0_c[0], tc_z0_c[1], tc_z0_l[0], tc_z0_l[1])
                    tri2misori_cl = max(tri2misori_x_cl, tri2misori_y_cl, tri2misori_z_cl)

                    tri2misori_x_ch = tri2misori(tc_x0_c[0], tc_x0_c[1], tc_x0_h[0], tc_x0_h[1])
                    tri2misori_y_ch = tri2misori(tc_y0_c[0], tc_y0_c[1], tc_y0_h[0], tc_y0_h[1])
                    tri2misori_z_ch = tri2misori(tc_z0_c[0], tc_z0_c[1], tc_z0_h[0], tc_z0_h[1])
                    tri2misori_ch = max(tri2misori_x_ch, tri2misori_y_ch, tri2misori_z_ch)

                    if (tri2misori_cl > misori_threshold) & (tri2misori_ch > misori_threshold):
                        img_lv[row, col, ht] = s
                        s = s + 1
                        r.append((img_lv[row, col, ht], img_lv[row, col, ht]))
                    elif (tri2misori_cl <= misori_threshold) & (tri2misori_ch > misori_threshold):
                        img_lv[row, col, ht] = img_lv[row, col - 1, ht]
                    elif (tri2misori_cl > misori_threshold) & (tri2misori_ch <= misori_threshold):
                        img_lv[row, col, ht] = img_lv[row, col, ht - 1]
                    elif (tri2misori_cl <= misori_threshold) & (tri2misori_ch <= misori_threshold):
                        img_lv[row, col, ht] = img_lv[row, col, ht - 1]
                        if img_lv[row, col - 1, ht] != img_lv[row, col, ht - 1]:
                                r.append((img_lv[row, col - 1, ht], img_lv[row, col, ht - 1]))
                
                elif ~np.isnan(img_in[row-1, col, ht]) & ~np.isnan(img_in[row, col-1, ht]) & ~np.isnan(img_in[row, col, ht - 1]):

                    tc_x0_c = tri_cubic_x0[addr_c]
                    tc_y0_c = tri_cubic_y0[addr_c]
                    tc_z0_c = tri_cubic_z0[addr_c]

                    addr_u = int(img_in[row - 1, col, ht])
                    tc_x0_u = tri_cubic_x0[addr_u]
                    tc_y0_u = tri_cubic_y0[addr_u]
                    tc_z0_u = tri_cubic_z0[addr_u]

                    addr_l = int(img_in[row, col - 1, ht])
                    tc_x0_l = tri_cubic_x0[addr_l]
                    tc_y0_l = tri_cubic_y0[addr_l]
                    tc_z0_l = tri_cubic_z0[addr_l]
                    
                    addr_h = int(img_in[row, col, ht - 1])
                    tc_x0_h = tri_cubic_x0[addr_h]
                    tc_y0_h = tri_cubic_y0[addr_h]
                    tc_z0_h = tri_cubic_z0[addr_h]

                    tri2misori_x_cu = tri2misori(tc_x0_c[0], tc_x0_c[1], tc_x0_u[0], tc_x0_u[1])
                    tri2misori_y_cu = tri2misori(tc_y0_c[0], tc_y0_c[1], tc_y0_u[0], tc_y0_u[1])
                    tri2misori_z_cu = tri2misori(tc_z0_c[0], tc_z0_c[1], tc_z0_u[0], tc_z0_u[1])
                    tri2misori_cu = max(tri2misori_x_cu, tri2misori_y_cu, tri2misori_z_cu)

                    tri2misori_x_cl = tri2misori(tc_x0_c[0], tc_x0_c[1], tc_x0_l[0], tc_x0_l[1])
                    tri2misori_y_cl = tri2misori(tc_y0_c[0], tc_y0_c[1], tc_y0_l[0], tc_y0_l[1])
                    tri2misori_z_cl = tri2misori(tc_z0_c[0], tc_z0_c[1], tc_z0_l[0], tc_z0_l[1])
                    tri2misori_cl = max(tri2misori_x_cl, tri2misori_y_cl, tri2misori_z_cl)

                    tri2misori_x_ch = tri2misori(tc_x0_c[0], tc_x0_c[1], tc_x0_h[0], tc_x0_h[1])
                    tri2misori_y_ch = tri2misori(tc_y0_c[0], tc_y0_c[1], tc_y0_h[0], tc_y0_h[1])
                    tri2misori_z_ch = tri2misori(tc_z0_c[0], tc_z0_c[1], tc_z0_h[0], tc_z0_h[1])
                    tri2misori_ch = max(tri2misori_x_ch, tri2misori_y_ch, tri2misori_z_ch)

                    if (tri2misori_cu > misori_threshold) & (tri2misori_cl > misori_threshold) & (tri2misori_ch > misori_threshold):
                        img_lv[row, col, ht] = s
                        s = s + 1
                        r.append((img_lv[row, col, ht], img_lv[row, col, ht]))

                    elif (tri2misori_cu <= misori_threshold) & (tri2misori_cl > misori_threshold) & (tri2misori_ch > misori_threshold):
                        img_lv[row, col, ht] = img_lv[row -1, col, ht]
                    elif (tri2misori_cu > misori_threshold) & (tri2misori_cl <= misori_threshold) & (tri2misori_ch > misori_threshold):
                        img_lv[row, col, ht] = img_lv[row, col - 1, ht]
                    elif (tri2misori_cu > misori_threshold) & (tri2misori_cl > misori_threshold) & (tri2misori_ch <= misori_threshold):
                        img_lv[row, col, ht] = img_lv[row, col, ht - 1]

                    elif (tri2misori_cu <= misori_threshold) & (tri2misori_cl <= misori_threshold) & (tri2misori_ch > misori_threshold):
                        img_lv[row, col, ht] = img_lv[row, col - 1, ht]
                        if img_lv[row - 1, col, ht] != img_lv[row, col - 1, ht]:
                                r.append((img_lv[row - 1, col, ht], img_lv[row, col - 1, ht]))
                    elif (tri2misori_cu <= misori_threshold) & (tri2misori_cl > misori_threshold) & (tri2misori_ch <= misori_threshold):
                        img_lv[row, col, ht] = img_lv[row, col, ht - 1]
                        if img_lv[row - 1, col, ht] != img_lv[row, col, ht - 1]:
                                r.append((img_lv[row - 1, col, ht], img_lv[row, col, ht - 1]))
                    elif (tri2misori_cu > misori_threshold) & (tri2misori_cl <= misori_threshold) & (tri2misori_ch <= misori_threshold):
                        img_lv[row, col, ht] = img_lv[row, col, ht - 1]
                        if img_lv[row, col - 1, ht] != img_lv[row, col, ht - 1]:
                                r.append((img_lv[row, col - 1, ht], img_lv[row, col, ht - 1]))

                    elif (tri2misori_cu <= misori_threshold) & (tri2misori_cl <= misori_threshold) & (tri2misori_ch <= misori_threshold):
                        img_lv[row, col, ht] = img_lv[row, col, ht - 1]
                        if img_lv[row, col - 1, ht] != img_lv[row, col, ht - 1]:
                                r.append((img_lv[row, col - 1, ht], img_lv[row, col, ht - 1]))
                        elif img_lv[row - 1, col, ht] != img_lv[row, col, ht - 1]:
                                r.append((img_lv[row - 1, col, ht], img_lv[row, col, ht - 1]))
                        elif img_lv[row - 1, col, ht] != img_lv[row, col - 1, ht]:
                                r.append((img_lv[row - 1, col, ht], img_lv[row, col - 1, ht]))



#%%
img_lv = img_lv[1:, 1:, 1:]
img_lv_2 = img_lv*0
rs = set(tuple(r))

rs_list = list(rs)
rs_list_2 = []
for n in rs_list:
    rs_list_2.append(n)

graph = nx.Graph(rs_list_2) 
graph_connected = [tuple(c) for c in nx.connected_components(graph)]

for m_2, n_2 in enumerate(graph_connected):
    for m_1, n_1 in enumerate(n_2):
        label_where = np.where(img_lv == n_1)
        img_lv_2[label_where] = m_2+1

#%%
u_mat_dummy = np.array([[[0, 0, 0], [0, 0, 0], [0, 0, 0]]])
rgb_x_dummy = np.array([[0, 0, 0]])
rgb_y_dummy = np.array([[0, 0, 0]])
rgb_z_dummy = np.array([[0, 0, 0]])

grain_list = []        
grain_addr = []

ra = np.unique(img_lv_2)

for n in ra:
    try:
        grain_a = np.int64(img_in[1:,1:,1:][np.where(img_lv_2==n)])
        grain_b = [x_a[grain_a], y_a[grain_a], z_a[grain_a], u_mat_a[grain_a], \
                   rgb_x_a[grain_a], rgb_y_a[grain_a], rgb_z_a[grain_a]]
        grain_addr.append(grain_a)
        grain_list.append(grain_b)
    except:
        grain_addr.append(np.array([],dtype=np.int64))
        grain_list.append([[], [], [], u_mat_dummy, \
                           rgb_x_dummy, rgb_y_dummy, rgb_z_dummy])

            

#%%            

grain_list_refined = []
grain_vol = []
for n in grain_list:
    if len(n[0])>=grain_size_threshold:
        grain_list_refined.append(n)
        grain_vol.append(len(n[0]))

#%%

x_n = np.arange(x_a.min(), x_a.max() + 2, 1)    
y_n = np.arange(y_a.min(), y_a.max() + 2, 1)    
z_n = np.arange(z_a.min(), z_a.max() + 2, 1)    
x_m, y_m, z_m = np.meshgrid(y_n, x_n, z_n)

if ipf_sel == 'ipf_x':
    sel = 4

elif ipf_sel == 'ipf_y':
    sel = 5

elif ipf_sel == 'ipf_z':
    sel = 6

else:
    print('Wrong direction')


#%%
gs_sort = []
for n in grain_list_refined:
    gs_sort.append(len(n[0]))

gs_argsort = np.argsort(gs_sort)[::-1]
grains_sorted = []
for n in gs_argsort:
    grains_sorted.append(grain_list_refined[n])

#%%
nn = 1 #1 5 6
grains = grains_sorted[nn:nn+1]
#grains = grains_sorted[:]

r = img_lv_2*np.nan
g = r.copy()
b = r.copy()

for m_1, grain_sel in enumerate(grains):
    for m, n in enumerate(zip(grain_sel[0], grain_sel[1], grain_sel[2])):
        xa, ya, za = n
        r[xa, ya, za] = grain_sel[sel][m][0]
        g[xa, ya, za] = grain_sel[sel][m][1]
        b[xa, ya, za] = grain_sel[sel][m][2]

r_e = np.expand_dims(r, 3)
g_e = np.expand_dims(g, 3)
b_e = np.expand_dims(b, 3)
alpha = r_e*0 + 1

rgb = np.concatenate((r_e,g_e,b_e,alpha),3)
filled = ~np.isnan(r)


fig = plt.figure(figsize=(7, 6))
ax = fig.add_subplot(111, projection="3d")

ax.voxels(filled, facecolors=rgb, edgecolor=None)

ax.set_xlabel("X", fontsize=12)
ax.set_ylabel("Y", fontsize=12)
ax.set_zlabel("Z", fontsize=12)
ax.set_xlim([-1, 52])
ax.set_ylim([-1, 52])
ax.set_zlim([-1, 52])

fig.tight_layout()

#%%
bs=np.arange(0, 40, 4)

gs = np.array(gs_sort)
v_voxel = 1

v_dist = 2*(3/4/np.pi * gs * v_voxel)**(1/3)

v_dist[np.isnan(v_dist)]=0

colors = plt.colormaps.get_cmap('viridis').resampled(20).colors

plt.rcParams.update({'font.size': 15})
#plt.rcParams["font.family"] = "Times New Roman"
#plt.rcParams["font.family"] = "Default"
fig = plt.figure(figsize=(6, 5))
ax_a = plt.subplot(1,1,1)

ax_a.hist(v_dist, bins=bs, density=False, alpha=1, edgecolor='black', linewidth=0.5)
#ax_a.hist(ht[1], bins=bs, density=True, alpha=1, edgecolor='black', linewidth=0.5, color=colors[9])
#ax_a.hist(ht[2], bins=bs, density=True, alpha=1, edgecolor='black', linewidth=0.5, color=colors[16])
#ax_a.legend(['\u03B5 = 0%','\u03B5 = 4.0%','\u03B5 = 6.4%'])

ax_a.set_ylim([0.1, 80])
ax_a.set_xlabel('Equivalent sphere diameter (Voxel)', fontsize=20)
ax_a.set_ylabel('Counts', fontsize=20)
#ax_a.set_yscale('log')
plt.show()
fig.tight_layout()



