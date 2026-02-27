# GDAL notes

Record the exact commands or Python calls you used and why their parameters make 
sense. Include resampling method, nodata handling, and target resolution.

Example:
- Reprojected raster to UTM Zone 32N (WGS84):
gdalwarp -t_srs EPSG:32632 -r bilinear -tap -dstnodata -9999 input.tif output_utm32n.tif
- Opened input raster:
gdal.Open(landcover.tif)
- Created output GeoTIFF (Float32):
gdal.GetDriverByName("GTiff").Create(output.tif, xsize, ysize, 1, GDT_Float32)
- Warped land cover raster to target grid (matching resolution and extent):
gdalwarp -t_srs [target_srs] -te [min_x min_y max_x max_y] -ts [x_size y_size] -r near -of GTiff -co COMPRESS=LZW -co TILED=YES input.tif output.tif