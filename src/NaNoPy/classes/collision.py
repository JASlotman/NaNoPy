import random as rnd
import math

class Collision:

    def __init__(self,xsize,ysize):
        self.xsize = xsize
        self.ysize = ysize

    def test(self):
        print("test")

    def get_nrow_ncol(self,gridsize):
        ncol = (self.xsize//gridsize)

        if self.xsize%gridsize != 0:
            ncol += 1

        nrow = (self.ysize//gridsize)

        if self.ysize%gridsize != 0:
            nrow += 1

        return ncol,nrow

    def get_grid_index_xy(self,x,y,gridsize):
        
        shape = self.get_nrow_ncol(gridsize)
        
        xlocation = (x//gridsize)%shape[0]
        ylocation = y//gridsize

        index = xlocation + (ylocation*shape[0])

        return index

    def get_grid_index(self,xloc,yloc,gridsize):
        
        shape = self.get_nrow_ncol(gridsize)
        index = xloc + (yloc*shape[0])

        return index

    def get_grid_location(self,index,gridsize):
        shape = self.get_nrow_ncol(gridsize)
        xloc = index%shape[0]
        yloc = index//shape[0]

        return xloc,yloc

    def get_neighbor_ids(self,index,gridsize):
        shape = self.get_nrow_ncol(gridsize)
        locs = self.get_grid_location(index,gridsize)

        neighborlocs = []

        for i in range(-1,2):
            for j in range(-1,2):
                if locs[0]+i >= 0 and locs[0]+i < shape[0] and locs[1]+j >= 0 and locs[1]+j < shape[1]: 
                    neighborlocs.append(self.get_grid_index(locs[0]+i,locs[j]+j,gridsize))
        
        return neighborlocs

    def create_dictionary(self,xs,ys,gridsize):
        d = dict()
        i=0
        for x,y in zip(xs,ys):
            key = self.get_grid_index_xy(x,y,gridsize)
            value = i
            d.setdefault(key,[])
            d[key].append(value)
            i += 1
            
        return d

    def loop(self,xs,ys,xs2,ys2,gridsize):
        dictionary = self.create_dictionary(xs2,ys2,gridsize)
        def decorator(func):
            for i in range(len(xs)):
                id = self.get_grid_index_xy(xs[i],ys[i],gridsize)
                nb = self.get_neighbor_ids(id,gridsize)
                for key in nb:
                    js = dictionary.get(key,None)
                    if js != None:
                        for j in js:
                            func(i,j)
        return decorator