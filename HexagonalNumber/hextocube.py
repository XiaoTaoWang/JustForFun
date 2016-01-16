# -*- coding: utf-8 -*-
"""
Created on Sat Jan 16 09:29:06 2016

@author: wxt
"""

from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.patches as mpatches

def circles(ax, x, y, r, c = 'b', **kwargs):
    
    from matplotlib.patches import Circle
    from matplotlib.collections import PatchCollection  

    if isinstance(c, basestring):
        color = c
    else:
        color = None
    kwargs.update(color = color)

    if np.isscalar(x):
        patches = [Circle((x, y), r),]
    elif np.isscalar(r):
        patches = [Circle((x_, y_), r) for x_, y_ in zip(x, y)]
    else:
        patches = [Circle((x_, y_), s_) for x_, y_, s_ in zip(x, y, r)]
    collection = PatchCollection(patches, **kwargs)

    if color is None:
        collection.set_array(np.asarray(c))

    ax.add_collection(collection)
    
    return collection

def hexagonplot(ax, n = 5, c = '#A5ACAF'):
    
    axis = [(0, i) for i in range(2*n-1)]
    r_side = [(np.sqrt(3)/2*i, i/2+j) for i in range(1, n) for j in range(2*n-i-1)]
    l_side = [(-i, j) for i, j in r_side]
    
    Pool = np.r_[axis, r_side, l_side]
    circles(ax, Pool[:,0], Pool[:,1], r = 0.5, c = c, alpha = 0.5)
    
    ax.set_xlim(Pool[:,0].min() - 1, Pool[:,0].max() + 1)
    ax.set_ylim(Pool[:,1].min() - 1, Pool[:,1].max() + 1)
    ax.set_aspect("equal")
    ax.axis('off')

def cubicmatrix(ax, n = 5, length = 2, front_color = '#A5ACAF'):
    
    from itertools import combinations, product
    # The minimum unit
    h = [i * length for i in [-0.5, 0.5]]
    coords = np.array(list(product(h, h, h)))
    
    part_1 = [np.r_['1,2,0', coords[:,0], coords[:,1]+i*length, coords[:,2]+j*length] for i in range(n) for j in range(n)]
    part_2 = [np.r_['1,2,0', coords[:,0]+i*length, coords[:,1]+(n-1)*length, coords[:,2]+j*length] for i in range(1, n) for j in range(n)]
    part_3 = [np.r_['1,2,0', coords[:,0]+i*length, coords[:,1]+j*length, coords[:,2]] for i in range(1, n) for j in range(n-1)]
    # Frame
    Parts = [part_1, part_2, part_3]
    Pool = [np.concatenate(tuple(part_1)), np.concatenate(tuple(part_2)), np.concatenate(tuple(part_3))]
    
    for i in range(3):
        for unit in Parts[i]:
            for s, e in combinations(unit, 2):
                if np.sum(np.abs(s - e)) == h[1] - h[0]:
                    if ((s[1] == Pool[i][:,1].min()) and (e[1] == Pool[i][:,1].min())) or\
                       (s[0] == Pool[i][:,0].max() or (s[2] == Pool[i][:,2].max())):
                        if i == 0:
                            if (s[0] == Pool[i][:,0].max()) and ((e[1] == Pool[i][:,1].max()) or (s[2] == Pool[i][:,2].min())):
                                pass
                            else:
                                ax.plot3D(*zip(s, e), color = front_color)
                        elif i == 1:
                            if (s[1] == Pool[i][:,1].min()) and (s[2] == Pool[i][:,2].min()) and (s[0] != Pool[i][:,0].max()):
                                pass
                            else:
                                ax.plot3D(*zip(s, e), color = front_color)
                        else:
                            ax.plot3D(*zip(s, e), color = front_color)
    ax.set_xlim3d(Pool[0][:,0].min(), Pool[1][:,0].max())
    ax.set_ylim3d(Pool[0][:,1].min(), Pool[0][:,1].max())
    ax.set_zlim3d(Pool[0][:,2].min(), Pool[0][:,2].max())
    ax.set_aspect("equal")
    ax.axis('off')
    
if __name__ == '__main__':
    
    fig = plt.figure(figsize = (10, 5))
    ax = fig.add_subplot(1, 2, 1)
    hexagonplot(ax, n = 10)
    xmin = ax.get_position().xmax
    ax = fig.add_subplot(1, 2, 2, projection='3d')
    cubicmatrix(ax, n = 10)
    xmax = ax.get_position().xmin
    # Arrow
    ax = fig.add_axes([xmin, 0.45, xmax - xmin, 0.1])
    ax.annotate('', xy = (1, 0), xytext = (0.2, 0), bbox = dict(boxstyle='round', fc='none', ec='none'),
                arrowprops = dict(arrowstyle = 'fancy', connectionstyle = 'arc3,rad=0.1', fc='0.5', ec='none'))
    ax.axis('off')
    # Annotate
    fig.text(0.5, 0.06, r'$h_n = n^3 - (n-1)^3$', fontsize = 20, ha = 'center')
    plt.savefig('tens.png', dpi = 500)
    plt.close()
    
    