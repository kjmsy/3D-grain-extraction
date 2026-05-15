# -*- coding: utf-8 -*-
"""
Created on Wed May 13 13:24:10 2026

@author: kjmsy
"""

import glob
import numpy as np

def get_time(time_string):
    h, m, sec = time_string.split(":")
    return int(h) * 3600 + int(m) * 60 + float(sec)

file_list = sorted(glob.glob('D3D_pipeline_log/*.txt'))


t_out = []
for n in range(8):
    t_tmp = []
    for fn in file_list[3*n:3*n + 3]:
        print(fn)
        fid = open(fn, 'r', encoding='utf-16')
        t = []
        while True:
            line = fid.readline()
            if not line: 
                break
            s = line.find(' : [10/11] Segment Features (Misorientation)')
            if s >= 0:
                t.append(line[11:s])
            s = line.find('Segment Features (Misorientation): Randomizing Feature Ids')
            if s >= 0:
                t.append(line[11:s])        
        fid.close()
    
        t_measured = get_time(t[1]) - get_time(t[0])
        t_tmp.append(t_measured)
    t_out.append(t_tmp)
    

t_array = np.array(t_out)

t_mean = np.round(np.mean(t_array, 1), 4)
t_std = np.round(np.std(t_array, 1), 4)





