'''
Created on Oct 6, 2017

@author: simulant
'''
import sys
import numpy as np
import time 

DTYPE1 = np.uint32
DTYPE2 = np.float64

#cimport numpy as np
#ctypedef np.uint32_t DTYPE1_t
#ctypedef np.float32_t DTYPE2_t
#cimport cython
"""
import os


def convert_vector(vector,type):
    try:
        if vector.dtype == type:
            pass
            return vector
        if vector.ndim == 1:
            vector1 = np.zeros(vector.shape[0],dtype=type)
            vector1[:] = vector
        else:
            vector1 = np.zeros(vector.shape,dtype=type)
            vector1[:,:] = vector
    except:
        vector1 = type(vector)
    return(vector1)


def reshapeM(INPUT_MATRIX
                , RESOLUTION):
    
    INPUT_MATRIX = convert_vector(INPUT_MATRIX, DTYPE2)

    RESOLUTION_x = convert_vector(abs(RESOLUTION[0]), DTYPE2)
    RESOLUTION_y = convert_vector(abs(RESOLUTION[1]), DTYPE2)
    
    return core_reshapeM(INPUT_MATRIX
                         , RESOLUTION_x
                         , RESOLUTION_y)
    
def max(a, b): return a if a >= b else b
def min(a, b): return a if a <= b else b

#@cython.boundscheck(False) 
#@cython.cdivision(True)   
#@cython.wraparound(False)
def weighted_averageVal(INPUT_MATRIX
            , x, y
            , maxX, maxY):
    
    y_0 = int(max(0,min(maxY,  y)))
    y_m1 = int(max(0,min(maxY, y_0 - 1)))
    y_p1 = int(max(0,min(maxY, y_0 + 1)))
    
    x_0 = int(max(0,min(maxX,  x)))
    x_m1 = int(max(0,min(maxX, x_0 - 1)))
    x_p1 = int(max(0,min(maxX, x_0 + 1)))
    
    share_bottom = y % 1
    share_right = x % 1
    
    val_0= INPUT_MATRIX[y_0, x_0]   # Value of center cell 
    val_b= INPUT_MATRIX[y_p1, x_0]  # Value of cell below
    val_t= INPUT_MATRIX[y_m1, x_0]  # Value of cell above
    val_r= INPUT_MATRIX[y_0, x_p1]  # Value of cell right
    val_l= INPUT_MATRIX[y_0, x_m1]  # Value of cell left
    
    val = (share_bottom * val_b + (1 - share_bottom) * val_t 
           + share_right * val_r + (1 - share_right) * val_l
           + 2 * val_0) / 4

    return (val)
            
#@cython.boundscheck(False) 
#@cython.cdivision(True)   
#@cython.wraparound(False)
def core_reshapeM(INPUT_MATRIX
                  , RESOLUTION_x
                  , RESOLUTION_y):
    
    
    print (RESOLUTION_x)
    """
    cdef DTYPE1_t x_size_new, y_size_new
    cdef DTYPE1_t maxX, maxY
    cdef DTYPE1_t y0, x0
    
    cdef DTYPE2_t b_t, b_cent, b_b
    cdef DTYPE2_t a_l, a_cent, a_r
    cdef DTYPE2_t ratio_a_0, ratio_b_0
        
    
    cdef DTYPE1_t b_cent_0, a_cent_0
    cdef DTYPE1_t b_top_0, b_bot_0, a_left_0, a_right_0

    cdef DTYPE2_t ratx0, raty0
    cdef DTYPE2_t val, val_cent
    cdef DTYPE2_t val_tlc, val_blc, val_trc, val_brc, val_le, val_re, val_weight_corner
    cdef DTYPE2_t average_val_tlc, average_val_trc, average_val_blc, average_val_brc
    cdef DTYPE2_t average_val_le, average_val_re, average_val_weight_corner, average_val_cent
    """
    
    x_size_new = int(np.ceil(INPUT_MATRIX.shape[1] / RESOLUTION_x))
    y_size_new = abs(int(np.ceil(INPUT_MATRIX.shape[0] / RESOLUTION_y)))
    
    RESULTS_MATRIX = np.zeros((y_size_new, x_size_new), dtype="f4")
    
    maxX = INPUT_MATRIX.shape[1] - 1
    maxY = INPUT_MATRIX.shape[0] - 1
    
    print("Start Loop")
    for y0 in range(5571, 28000) : #y_size_new):
        #for y0 in range(y_size_new):
        if y0 % 5000 == 0:
            print("%i out of %i" %(y0,  y_size_new))
        b_t = (y0 * RESOLUTION_y)
        b_cent = ((y0 + 0.5) * RESOLUTION_y)    
        b_b = ((y0 + 1) * RESOLUTION_y)
    
        ratio_b_0 = b_t % 1 # b_t - int(b_t)
        raty0 = (1 - ratio_b_0) / RESOLUTION_y
        ####################
        b_top_0 = int(b_t)
        b_cent_0 = int(min(maxY, b_cent))
        b_bot_0 = int(min(maxY, b_b))
        
        
        for x0 in range(21805, 23000): #x_size_new):
            #for x0 in range(x_size_new):
            
        
            a_l = float(x0 * RESOLUTION_x)
            a_cent = ((x0 + 0.5) * RESOLUTION_x)    
            a_r = (float(x0 + 1) * RESOLUTION_x)
            print (".....")
            print(a_r)
            ratio_a_0 = a_l % 1 # a_l - int(a_l)            
            ratx0 = (1 - ratio_a_0) / RESOLUTION_x
            ####################
            a_left_0 = int(a_l)
            a_cent_0 = int(min(maxX, a_cent))
            a_right_0 = int(min(maxX, a_r))
            print(a_right_0)
        
        
            ####################
            val_cent = INPUT_MATRIX[b_cent_0, a_cent_0] # Value of the center
                        
            val_tlc = INPUT_MATRIX[b_top_0, a_left_0] # Value of the left upper corner
            val_blc = INPUT_MATRIX[b_bot_0, a_left_0] # Value of the left lower corner
            val_trc = INPUT_MATRIX[b_top_0, a_right_0] # Value of the right upper corner
            val_brc = INPUT_MATRIX[b_bot_0, a_right_0] # Value of the right lower corner

            val_le = ((raty0) * val_tlc + (1-raty0) * val_blc) # Value of the left edge
            val_re =   ((raty0) * val_trc + (1-raty0) * val_brc) # Value of the right edge
            val_weight_corner = ((ratx0) * val_le + (1-ratx0) * val_re)
            
            #if val_weight_corner < 0:
            print("#######")
            print(y0)
            print(x0)
            print(raty0)
            print(ratx0)
            print(val_weight_corner)
            print(val_re)
            print(val_le)
            print(val_brc)
            print(val_trc)
            print(val_blc)
            print(val_tlc)
            print(",,,")
            print(b_bot_0)
            print(a_right_0)
            print(INPUT_MATRIX[b_bot_0, a_right_0])
            print("----")
        
            
            ####################
            #if val_tl > 161.18 and val_tl < 161.2:
            #    print(val_tl)
            
            #print("-----")    
            #print(val_weight_corner)
            """
            average_val_tlc = weighted_averageVal(INPUT_MATRIX
                            , a_l, b_t 
                            , maxX, maxY)     # interpolated value of top left corner
            average_val_trc = weighted_averageVal(INPUT_MATRIX
                            , a_r, b_t 
                            , maxX, maxY)     # interpolated value of top right corner            
            average_val_blc = weighted_averageVal(INPUT_MATRIX
                            , a_l, b_t
                            , maxX, maxY)     # interpolated value of bottom left corner
            average_val_brc = weighted_averageVal(INPUT_MATRIX
                            , a_r, b_b
                            , maxX, maxY)     # interpolated value of bottom right corner
            
             
            average_val_le = ((raty0) * average_val_tlc + (1-raty0) * average_val_blc) # Value of the left edge
            average_val_re =   ((raty0) * average_val_trc + (1-raty0) * average_val_brc) # Value of the right edge
            average_val_weight_corner = ((ratx0) * average_val_le + (1-ratx0) * average_val_re)
                       
            average_val_cent = weighted_averageVal(INPUT_MATRIX
                            , a_cent, b_cent
                            , maxX, maxY)     # interpolated value of bottom right corner
            """
            ####################
            val = (  val_weight_corner )
            #+ 0.5*val_cent ) / 1.5
            """
            val = (  1 * average_val_weight_corner
                   + 0.5*val_weight_corner
                   + 0.5*average_val_cent
                   + 0.5*val_cent ) / 2.5
            """  
            RESULTS_MATRIX[y0, x0] = val * RESOLUTION_x * RESOLUTION_y
    
    return (RESULTS_MATRIX)