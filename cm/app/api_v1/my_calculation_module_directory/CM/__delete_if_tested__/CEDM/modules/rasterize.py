import gdal, ogr, osr, os, time
import numpy as np
import CM_intern.common_modules.array2raster as a2r #array2raster

def rasterize(inRasterPath, inVectorPath, fieldName, dataType
              , outRasterPath=None, noDataValue=0, saveAsRaster=False
              , pixelWidth=100, pixelHeight=-100):
    
    inRastDatasource = gdal.Open(inRasterPath)
    geotransform_obj = inRastDatasource.GetGeoTransform()
    minx = geotransform_obj[0]
    maxy = geotransform_obj[3]
    #maxx = minx + transform[1] * inRastDatasource.RasterXSize
    #miny = maxy + transform[5] * inRastDatasource.RasterYSize
    rasterOrigin = (minx, maxy)
    b = inRastDatasource.GetRasterBand(1)
    arr = b.ReadAsArray()
    y_ext = arr.shape[0]     # 4472
    x_ext = arr.shape[1]     # 5559   
    #inRastDatasource = None
    
    
    
    
    inShapefile = inVectorPath
    inDriver = ogr.GetDriverByName("ESRI Shapefile")
    inDataSource = inDriver.Open(inShapefile, 0)
    inLayer = inDataSource.GetLayer()


    
        
    x_vec_origin = rasterOrigin[0] + 500
    y_vec_origin = rasterOrigin[1] - 500

    arr_out = np.zeros((int(np.ceil(y_ext * 1000 / abs(pixelWidth)))
                      , int(np.ceil(x_ext * 1000 / abs(pixelHeight))))
                   ,dtype = dataType)
    for i in range(0, inLayer.GetFeatureCount()):
        inFeature = inLayer.GetFeature(i)
        #if x_index<x_size*10 and y_index<y_size*10:
        if not(inFeature.GetField(fieldName) is None):
            geom = inFeature.GetGeometryRef().Centroid()
        
            x = geom.GetX()
            y = geom.GetY()
            #         if x>x_vec_origin and y>y_vec_origin :
            x_index = round((x - x_vec_origin)/1000)
            y_index = round((y_vec_origin - y)/1000)
            temp = inFeature.GetField(fieldName)
            
            arr_out[10*y_index:10*y_index+10, 10*x_index:10*x_index+10] = temp
    inFeature = None  
    
        
    inLayer = None 
    # rev_array = arr_out[::-1] # reverse array so the tif looks like the array
    if saveAsRaster == True:
        a2r.array2raster(outRasterPath, geotransform_obj
                         , dataType
                         , arr_out, noDataValue) # convert array to raster
        
    
    #ds = gdal.Open(outRasterPath)
    
    
    
    return (outRasterPath, geotransform_obj
                    , dataType
                    , arr_out, noDataValue)
    
    
def rasterize_no_centroid(inVectorPath, fieldName, dataType
              , geotransf_obj
              , array_size
              , noDataValue=0
              , OutPutProjection=3035):

    y_size = array_size[0]  
    x_size = array_size[1]     

    inShapefile = inVectorPath
    print(os.path.exists(inShapefile))
    inDriver = ogr.GetDriverByName("ESRI Shapefile")
    inDataSource = inDriver.Open(inShapefile, 0)
    inLayer = inDataSource.GetLayer()

    #x_min,x_max,y_min,y_max = inLayer.GetExtent()
    #x_size = int(np.ceil((x_max-x_min)/ abs(pixelWidth)/10)*10)
    #y_size = int(np.ceil((y_max-y_min)/ abs(pixelHeight)/10)*10)
    #x_size = x_ext * 10
    #y_size = y_ext * 10
    print("Create Layer")
    target_ds = gdal.GetDriverByName('MEM').Create("", x_size, y_size
                                                   , 1, gdal.GDT_Float32)
    #target_ds.SetGeoTransform((x_min-10000, pixelWidth,0,y_max-10000,0, pixelHeight))
    

    outRasterSRS = osr.SpatialReference()
    outRasterSRS.ImportFromEPSG(OutPutProjection)
    target_ds.SetProjection(outRasterSRS.ExportToWkt())
    
    target_ds.SetGeoTransform(geotransf_obj)
    
    band = target_ds.GetRasterBand(1)
    band.SetNoDataValue(noDataValue)
    #gdal.RasterizeLayer(target_ds,[1], inLayer, burn_values=[123324.153])
    print("  Raster")
    gdal.RasterizeLayer(target_ds,[1], inLayer, options=["ATTRIBUTE=%s" % fieldName]) #options=["ATTRIBUTE=%s" % "IDNUMBER",'ALL_TOUCHED=TRUE'])#, ['ALL_TOUCHED=TRUE'], burn_values=[1]
    arr_out = band.ReadAsArray().astype(dataType)
    #somehow process results in a shift of 2000 m
    #arr_out[0:-20,:] = arr_out[20:,:]
    geotransform_obj = target_ds.GetGeoTransform()
    #print (target_ds.GetGeoTransform())
    target_ds = None #flush to disk
    #rasterOrigin = [x_min, y_max]
        
    inLayer = None 
    # rev_array = arr_out[::-1] # reverse array so the tif looks like the array
    
    
    return (arr_out, geotransform_obj)

