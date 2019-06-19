'''
Created on Apr 20, 2017

@author: simulant
'''
import sys
import numpy as np
import time 

DTYPE1 = np.uint32
DTYPE2 = np.float32

#cimport numpy as np
#ctypedef np.uint32_t DTYPE1_t
#ctypedef np.float64_t DTYPE2_t
#cimport cython

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

def CalcShareLowRes(HighResM
                    , LARGE_BUILDINGS_array
                    , ResolutionFactor):
    
    HighResM = convert_vector(HighResM, DTYPE1)
    LARGE_BUILDINGS_array = convert_vector(LARGE_BUILDINGS_array, DTYPE1)
    Building_Vector = np.unique(HighResM)
    if LARGE_BUILDINGS_array[0, 0] != 0 and Building_Vector[0] == 0:
        Building_Vector = Building_Vector[1:]
    if (len(Building_Vector) != LARGE_BUILDINGS_array.shape[0]
        or (Building_Vector != LARGE_BUILDINGS_array[:, 0]).any()):
        print("cy.HighRes_OSM : ((Building_Vector != LARGE_BUILDINGS_array[:, 0])).any()")
        m = 0
        for j in range(LARGE_BUILDINGS_array.shape[0]):
            if LARGE_BUILDINGS_array[j, 0].astype("int") not in Building_Vector:
                m += 1
        print("   Missing Buildings: %i " % m)
        
    ResolutionFactor = convert_vector(ResolutionFactor, DTYPE1)
    
    num_feat = int(np.maximum(len(Building_Vector)
                   , LARGE_BUILDINGS_array.shape[0]))
    #num_feat = LARGE_BUILDINGS_array.shape[0]
    PX_count_Matrix_LowRes, Share_Matrix_LowRes = core_loop_calc_share_lowRes(HighResM
                                                      , LARGE_BUILDINGS_array
                                                      , ResolutionFactor
                                                      , num_feat)
    
    
    
    return PX_count_Matrix_LowRes, Share_Matrix_LowRes

#@cython.boundscheck(False) 
#@cython.cdivision(True)   
#@cython.wraparound(False)
def core_loop_calc_share_lowRes(HighResM
                        , LARGE_BUILDINGS_array
                        , ResolutionFactor
                        , num_feat):

    """
    cdef DTYPE1_t max_number_px
    cdef DTYPE1_t estimated_number_of_lines
    cdef DTYPE1_t r
    cdef DTYPE1_t r_
    cdef DTYPE1_t c
    cdef DTYPE1_t c_
    cdef DTYPE1_t new_empty_row
    cdef DTYPE1_t rLow
    cdef DTYPE1_t cLow
    cdef DTYPE1_t feat_id
    
    cdef DTYPE1_t DEBUG 
    cdef DTYPE1_t cont_loop
    """
    
    DEBUG = 0
    
    max_number_px = np.maximum(np.max(LARGE_BUILDINGS_array[:,0]), np.max(HighResM))
    num_feat = LARGE_BUILDINGS_array.shape[0]
    print("Number of feat: %i" % num_feat)
    print("Max_Number_feat_id: %i" % max_number_px)
    estimated_number_of_lines = int(max_number_px 
                                    + (1+num_feat) * 3)
    
    print("Estimated_Number_of lines: %i => +%i lines" % (estimated_number_of_lines
                                                          , int(estimated_number_of_lines - max_number_px)))
    PX_count_Matrix_LowRes = np.zeros((estimated_number_of_lines, 6), dtype=DTYPE1)
    Share_Matrix_LowRes = np.zeros((PX_count_Matrix_LowRes.shape[0]), dtype=DTYPE2)  
    
    r = HighResM.shape[0]
    c = HighResM.shape[1]
    
    new_empty_row = max_number_px + 1
    for r_ in range(num_feat):
        rLow = int(LARGE_BUILDINGS_array[r_, 2] / ResolutionFactor)
        cLow = int(LARGE_BUILDINGS_array[r_, 1] / ResolutionFactor)
        feat_id = int(LARGE_BUILDINGS_array[r_, 0])
        
        if feat_id >= PX_count_Matrix_LowRes.shape[0]:
            print(feat_id)
        try:
            PX_count_Matrix_LowRes[feat_id, 0] = feat_id
        except Exception as e:
            print(str(e))
            
        PX_count_Matrix_LowRes[feat_id, 4] = 1
        PX_count_Matrix_LowRes[feat_id, 3] = 1
        
        PX_count_Matrix_LowRes[feat_id, 1] = rLow
        PX_count_Matrix_LowRes[feat_id, 2] = cLow
        

    for r_ in range(r):
        if (HighResM[r_,:] == 0).all():
            continue
        rLow = int(r_ / ResolutionFactor)
        for c_ in range(c):
            feat_id = HighResM[r_, c_]
            if feat_id == 0:
                continue
            else:
                cLow = int(c_ / ResolutionFactor)
                
                if (PX_count_Matrix_LowRes[feat_id, 2] == cLow 
                      and PX_count_Matrix_LowRes[feat_id, 1] == rLow):
                    
                    # Same Raster Cell
                    PX_count_Matrix_LowRes[feat_id, 4] += 1
                    PX_count_Matrix_LowRes[feat_id, 3] += 1
                elif PX_count_Matrix_LowRes[feat_id, 0] == 0:
                    print("Code should't reach this branch")
                    PX_count_Matrix_LowRes[feat_id, 0] = feat_id
                    PX_count_Matrix_LowRes[feat_id, 4] = 1
                    PX_count_Matrix_LowRes[feat_id, 3] = 1
                    
                    PX_count_Matrix_LowRes[feat_id, 1] = rLow
                    PX_count_Matrix_LowRes[feat_id, 2] = cLow
                else:
                    
                    PX_count_Matrix_LowRes[feat_id, 4] += 1
                    
                    Prev_Row = feat_id
                    Next_Row = PX_count_Matrix_LowRes[feat_id, 5] 
                    cont_loop = 1 
                    while cont_loop > 0:
                        if Next_Row == 0:
                            PX_count_Matrix_LowRes[Prev_Row, 5] = new_empty_row
                            
                            
                            PX_count_Matrix_LowRes[new_empty_row, 0] = feat_id
                            PX_count_Matrix_LowRes[new_empty_row, 3] = 1
                    
                            PX_count_Matrix_LowRes[new_empty_row, 1] = rLow
                            PX_count_Matrix_LowRes[new_empty_row, 2] = cLow
                    
                            new_empty_row += 1
                            cont_loop = 0
                        elif (PX_count_Matrix_LowRes[Next_Row, 2] == cLow 
                              and PX_count_Matrix_LowRes[Next_Row, 1] == rLow):
                            # Same Raster Cell
                            PX_count_Matrix_LowRes[Next_Row, 3] += 1
                            cont_loop = 0
                        else:
                            
                            Prev_Row = Next_Row
                            Next_Row = PX_count_Matrix_LowRes[Next_Row, 5]
    
    print("  Actual_Number_of new lines: +%i lines" % (new_empty_row - 1 - max_number_px))            
    print("   => +%2.2f lines per building" % (float(new_empty_row - 1 - max_number_px) / np.maximum(1.0, num_feat - 1)))

    if DEBUG == 1:
        print(np.sum(PX_count_Matrix_LowRes[:, 4]))
        print(np.sum(HighResM > 0))
        print("-------")
    
    
    
    
    
    orig_feat_row = PX_count_Matrix_LowRes[:, 0]  
        
    Share_Matrix_LowRes[:] = PX_count_Matrix_LowRes[:, 3].astype(DTYPE2) / np.maximum(1, PX_count_Matrix_LowRes[orig_feat_row, 4]).astype(DTYPE2)
    
    if DEBUG == 1:
        print(np.sum(Share_Matrix_LowRes))
        
        for i in range(LARGE_BUILDINGS_array.shape[0]):
            feat_id = LARGE_BUILDINGS_array[i, :]
            print("------")
            print(feat_id)
            print(np.sum(HighResM == feat_id))
            print(PX_count_Matrix_LowRes[feat_id, 4])
            print(PX_count_Matrix_LowRes[feat_id, 0])
    
    
    idx_Not_Empty = PX_count_Matrix_LowRes[:, 0] > 0
    
    Share_Matrix_LowRes = Share_Matrix_LowRes[idx_Not_Empty]
    PX_count_Matrix_LowRes = PX_count_Matrix_LowRes[idx_Not_Empty]
    
    
    
    
    return(PX_count_Matrix_LowRes, Share_Matrix_LowRes)

        