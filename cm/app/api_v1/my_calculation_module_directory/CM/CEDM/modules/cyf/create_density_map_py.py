'''
Created on Apr 20, 2017

@author: simulant
'''

import numpy as np
import time 
#cimport numpy as np

DTYPE1 = np.int
#ctypedef np.int_t DTYPE1_t

DTYPE2 = np.float32
#ctypedef np.float32_t DTYPE2_t

DTYPE3 = np.float64
#ctypedef np.float64_t DTYPE3_t

#cimport cython
#from cython.parallel import parallel, prange
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
    del vector
    return(vector1)

def CreateDensistyMap(Indicator_Map
                      , REGION_ID_Map
                      , return_mean=0):
    
    if Indicator_Map.shape != REGION_ID_Map.shape:
        print("Error: Maps need to have same extend")
        return
    Indicator_Map = convert_vector(Indicator_Map, DTYPE2)
    REGION_ID_Map = convert_vector(REGION_ID_Map, DTYPE1)
    (ResultsTable, ResultsCounter) = _core_loopCDM(Indicator_Map
                           , REGION_ID_Map
                           , return_table = 1)
    
    DensityMap = _core_loopRescale(Indicator_Map
                          , REGION_ID_Map
                          , ResultsTable)
    
    
    del Indicator_Map
    del REGION_ID_Map
    return DensityMap

def CreateResultsTableperIndicator(Indicator_Map
                      , REGION_ID_Map, return_mean=0):
    
    if Indicator_Map.shape != REGION_ID_Map.shape:
        print("Error: Maps need to have same extend")
        return
    Indicator_Map = convert_vector(Indicator_Map, DTYPE2)
    REGION_ID_Map = convert_vector(REGION_ID_Map, DTYPE1)
    (ResultsTable, ResultsCounter) = _core_loopCDM(Indicator_Map
                           , REGION_ID_Map
                           , return_table = 1)
    
    if return_mean==1:
        ResultsTable2 = np.zeros((ResultsTable.shape[0], 4), dtype=DTYPE2)
    else:
        ResultsTable2 = np.zeros((ResultsTable.shape[0], 2), dtype=DTYPE2)
    ResultsTable2[:, 0] = np.arange(ResultsTable2.shape[0])
    ResultsTable2[:, 1] = ResultsTable
    
    if return_mean==1:
        ResultsTable2[:, 2] = ResultsCounter
        ResultsTable2[:, 3] = ResultsTable2[:, 1] / (ResultsTable2[:, 2]  + 0.0001)
    idx = ResultsTable2[:, 1] > 10 ** - 8
    return ResultsTable2[idx, :]


def ScaleResultsWithTableperIndicator(Indicator_Map
                                      , REGION_ID_Map
                                      , REGION_DATA
                                      , elasticitiy=1
                                      , maxscale = 1.5):

    
    if Indicator_Map.shape !=REGION_ID_Map.shape:
        print("Error: Maps need to have same extend")
        return
    Indicator_Map = convert_vector(Indicator_Map, DTYPE2)
    REGION_ID_Map = convert_vector(REGION_ID_Map, DTYPE1)
    REGION_DATA = convert_vector(REGION_DATA, DTYPE2)
    elasticitiy = DTYPE2(elasticitiy)
    maxscale = DTYPE2(maxscale)
    
    (ResultsTable) = _core_loopCDM(Indicator_Map
                           , REGION_ID_Map
                           , return_table = 1)
    
    num_entries = np.maximum(ResultsTable.shape[0], REGION_DATA.shape[0])
    min_entries = np.minimum(ResultsTable.shape[0], REGION_DATA.shape[0])
    RescaleVctr = np.zeros(num_entries, dtype=DTYPE2) 
    RescaleVctr[:min_entries] = (0.0001 + ResultsTable[:min_entries]) / (0.0001 + REGION_DATA[:min_entries])
    
    # Set Rescale Value of obiously not-fitting Values to 1
    idx = np.abs(ResultsTable[:min_entries] - REGION_DATA[:min_entries]) > 100
    idxUpperLimit = np.logical_and(idx, RescaleVctr[:min_entries] > 5)
    RescaleVctr[:min_entries][idxUpperLimit] = 1
    idxLowerLimit = np.logical_and(idx, RescaleVctr[:min_entries] < 0.2)
    RescaleVctr[:min_entries][idxLowerLimit] = 1
    
    # Set Rescale Value of missing data to 1
    idx = REGION_DATA[:min_entries] < 1
    RescaleVctr[:min_entries][idx] = 1
    RescaleVctr[min_entries:] = 1
    # Define Boundaries
    RescaleVctr = (np.maximum(0.1, np.minimum(5.0, RescaleVctr)))  ** elasticitiy
    RescaleVctr = (np.maximum(1.0/maxscale, np.minimum(maxscale, RescaleVctr))) 

    DensityMap = _core_loopRescale(Indicator_Map
              , REGION_ID_Map
              , RescaleVctr)

    return DensityMap


#@cython.wraparound(False)
#@cython.boundscheck(False) 
#@cython.cdivision(True)
def _core_loopCDM(Indicator_Map
              , REGION_ID_Map
              , return_table = 0
              , return_mean = 0):
    
    
    
    max_reg_id = np.max(REGION_ID_Map).astype(DTYPE1)
    
    IndicatorSumVct = np.zeros(max_reg_id + 1, DTYPE3)
    IndicatorCounter = np.zeros(max_reg_id + 1, DTYPE3)
    DensityMap = np.zeros_like(Indicator_Map)

    IndicatorSumVct += 10.0 ** -6
    
    r = Indicator_Map.shape[0]
    c = Indicator_Map.shape[1]

    for i in range(r):
        for j in range(c):
            reg_id = REGION_ID_Map[i, j]
            IndicatorSumVct[reg_id] += Indicator_Map[i, j]
            IndicatorCounter[reg_id] += 1
    if return_table == 1:
        if return_mean == 0:
            return IndicatorSumVct
        else:
            return IndicatorSumVct, IndicatorCounter
    else:
        for i in range(r):
            for j in range(c):
                reg_id = REGION_ID_Map[i, j]
                DensityMap[i, j] = (Indicator_Map[i, j] / IndicatorSumVct[reg_id])

    del Indicator_Map, IndicatorSumVct
    return DensityMap

#@cython.wraparound(False)
#@cython.boundscheck(False) 
#@cython.cdivision(True)
def _core_loopRescale(Indicator_Map
              , REGION_ID_Map
              , RescaleVct):
    
    
    DensityMap = np.zeros_like(Indicator_Map)
    
    r = Indicator_Map.shape[0]
    c = Indicator_Map.shape[1]
    
    #with nogil, parallel():
    if 1==1:
        for i in range(r):
            for j in range(c):
                DensityMap[i,j] = Indicator_Map[i,j] / (0.0000001 + RescaleVct[REGION_ID_Map[i,j]])

    return DensityMap

def CreateAverageMap(Indicator_Map
                      , REGION_ID_Map):
    
    if Indicator_Map.shape !=REGION_ID_Map.shape:
        print("Error: Maps need to have same extend")
        return
    Indicator_Map = convert_vector(Indicator_Map, DTYPE2)
    REGION_ID_Map = convert_vector(REGION_ID_Map, DTYPE1)
    AverageMap = core_loopAverageCDM(Indicator_Map
                           , REGION_ID_Map)
    return AverageMap


def core_loopAverageCDM(Indicator_Map
              , REGION_ID_Map):
    
    
    
    max_reg_id = np.max(REGION_ID_Map).astype(DTYPE1)
    
    IndicatorSumVct = np.zeros(max_reg_id + 1, DTYPE3)
    IndicatorCounterVct = np.zeros(max_reg_id + 1, DTYPE3)
    AverageMap = np.zeros_like(Indicator_Map)
    
    IndicatorSumVct += 10.0 ** -6
    IndicatorCounterVct += 10.0 ** -3
    
    r = Indicator_Map.shape[0]
    c = Indicator_Map.shape[1]
    
    
    for i in range(r):
        for j in range(c):
            IndicatorSumVct[REGION_ID_Map[i,j]] += Indicator_Map[i,j]
            IndicatorCounterVct[REGION_ID_Map[i,j]] += 1

    #with nogil, parallel():
    if 1==1:
        for i in range(r):
            for j in range(c):
                AverageMap[i,j] = (IndicatorSumVct[REGION_ID_Map[i,j]] / IndicatorCounterVct[REGION_ID_Map[i,j]])
    


        

    return AverageMap


def CreateFinalMap(Density_Map
                      , REGION_ID_Map
                      , REGION_DATA):
    
    if Density_Map.shape !=REGION_ID_Map.shape:
        print("Error: Maps need to have same extend")
        return
    Density_Map = convert_vector(Density_Map, DTYPE2)
    REGION_ID_Map = convert_vector(REGION_ID_Map, DTYPE1)
    REGION_DATA = convert_vector(REGION_DATA, DTYPE2)
    DensityMap = core_loopCFM(Density_Map
                           , REGION_ID_Map
                           , REGION_DATA)
    return DensityMap

#@cython.wraparound(False)
#@cython.boundscheck(False) 
#@cython.cdivision(True)
def core_loopCFM(Density_Map
              , REGION_ID_Map
              , REGION_DATA):

    r = Density_Map.shape[0]
    c = Density_Map.shape[1]
    
    FinalMap = np.zeros_like(Density_Map)

    #with nogil, parallel():
    if 1==1:
        for i in range(r):
            for j in range(c):
                FinalMap[i, j] = Density_Map[i, j] * REGION_DATA[REGION_ID_Map[i, j]]

    return FinalMap