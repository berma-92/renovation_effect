from osgeo import gdal
import os

def raster_array(raster, dType=float, return_gt=None):
    if not os.path.exists(raster):
        print("Raster file doesn't exist: %s " % raster)
    assert os.path.exists(raster)
    
    ds = gdal.Open(raster)
    geo_transform = ds.GetGeoTransform()
    band1 = ds.GetRasterBand(1)
    arr = band1.ReadAsArray().astype(dType)
    ds = None
    if return_gt:
        return arr, geo_transform
    else:
        return arr

