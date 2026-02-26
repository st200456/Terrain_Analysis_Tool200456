# Documentation of Functions and Custom Classes
This page gives an overview of all the tool’s functions and custom classes, discussing what they do, input parameters, and output data types.

## 1. Main.py
This script is the main entry point of the terrain-processing workflow. It validates an Area of Interest (AOI), downloads a DEM, aligns landcover data, computes roughness, extracts the thalweg, and generates an elevation profile along the extracted flow path (png and csv). 

The `Main.py` file serves as the entry point of the application. It is worth mentioning that, all inputs are saved in /data directory and all outputs in /results directory.

### Overview
The following section shows all the classes used in the model:

 - AOI
 - DEMFetcher
 - LandCoverFetcher
 - RoughnessCalculator
 - ThalwegExtractor
 - ProfileSampler

Additionally, this section presents all the functions used in the model.

 - gdal_utils
 - standar_steps
   
## AOI Class
A class to check the `Area of Interest (AOI)` bounding box coordinates before getting DEM data
### Methods

#### `__init__(self, west, south, east, north)`

Initializes the `AOI validator` with bounding box coordinates.

##### Input Parameters

- `west` (`float`): Western longitude
- `south` (`float`): Southern latitude
- `east` (`float`): Eastern longitude
- `north` (`float`): Northern latitude
  
#### `validate(self)`

Runs all verification checks (type, range, and logical order).

- Returns: `Boolean value` (`True` if valid)

- Raises: `ValueError` if validation fails

#### `check_types(self)`

Checks that all inputs are numeric (`int` or `float`).

- Raises: `ValueError` if any coordinate is not numeric

#### `check_ranges(self)`

Checks that coordinates fall within valid WGS84 ranges:

- Longitude must be between `-180` and `180`

- Latitude must be between `-90` and `90`

- Raises: `ValueError` if out of range

#### `check_logic(self)`

Checks that min/max coordinate order is correct.

- `west < east`

- `south < north`

- Raises: `ValueError` if bounding box order is invalid

#### `get_bbox(self)`

Returns the bounding box coordinates as a dictionary.

- Returns: dictionary with keys as: `west`, `south`, `east`, `north`

## 2. DEMFetcher Class

A class for downloading `Digital Elevation Model (DEM)` data from the OpenTopography API using the SRTMGL1 dataset.

### Methods

#### `__init__(self, api_key=None)`

Initializes the `DEM fetcher` and requires `api_key`.

- `api_key` (`str`): OpenTopography API key for higher request limits
- `demtype` (`str`): Digital Elevation Model dataset identifier
- `base_url` (`str`): Base endpoint URL of the OpenTopography Global DEM API used to request elevation data

#### `download(self, south, north, west, east, output_file="dem_wgs84.tif")`

Downloads a DEM GeoTIFF file for the specified bounding box.

- `south` (`float`): Southern latitude boundary

- `north` (`float`): Northern latitude boundary

- `west` (`float`): Western longitude boundary

- `east` (`float`): Eastern longitude boundary

- `output_file` (`Path`): Output file path for the DEM

Returns: `Path` to the downloaded DEM file

Raises: Exception if the API request fails

## 3. LandCoverFetcher Class

A class for matching landcover raster data to the DEM resolution, extent, and coordinate system.

### Methods

#### `__init__(self, output_file, output_src, output_landcover_file)`

Initializes the landcover matcher.

- `output_file` (`Path`): Reference raster file (DEM)

- `output_src` (`Path`): Source landcover raster

- `output_landcover_file` (`Path`): Output matched landcover file

#### `match(self)`

Resamples and aligns the landcover raster to match the DEM projection, extent, and resolution.

Returns: `Path` to the matched landcover raster file

#### `__str__(self)`

Returns a string description of the matching process.

Returns: `str` describing the input and output raster files

## 4. RoughnessCalculator Class

A class for computing a Manning’s n roughness raster from landcover data.

### Methods
#### `__init__(self, landcover_file, out_file)`

Initializes the roughness calculation.

- `MANNING_MAP`: Dictionary that maps land cover codes to Manning’s roughness coefficient (n)
  
- `landcover_file` (`Path`): Input landcover raster file

- `out_file` (`Path`): Output roughness raster file

#### `compute(self)`

Generates a roughness raster by mapping landcover classes to Manning’s n coefficients.

Returns: `Path` to the generated roughness raster file

Raises: `RuntimeError` if the landcover raster cannot be opened

#### `__str__(self)`

Returns a string description of the roughness computation.

Returns: `str` describing the input and output raster files

## 5. ThalwegExtractor Class

A class for extracting the main channel (thalweg) from a Digital Elevation Model (DEM).

### Methods
#### `__init__(self, dem_file, output_vector="Thalweg.shp", threshold=1000, outlet_coords=None)`

Initializes the thalweg extraction.

- `dem_file` (`Path`): Input DEM raster file

- `output_vector` (`Path`): Output shapefile path

- `threshold` (`int`): Minimum flow accumulation threshold

- `outlet_coords` (`tuple`): Outlet coordinates in DEM CRS

#### `compute(self)`

Runs the full thalweg extraction workflow (hydrology computation, outlet detection, tracing, and export).

Returns: `Path` to the generated shapefile, or None if extraction fails

#### `_compute_hydrology(self)`

Computes flow direction and flow accumulation from the DEM.

Returns: `Grid object`, `DEM raster`, `flow direction array`, and `flow accumulation array`

#### `_get_outlet(self, flow_acc, dem)`

Determines the outlet cell used as the starting point for tracing.

Returns: `Tuple` (`row`, `col`) representing the outlet cell

#### `_trace_thalweg(self, flow_dir, flow_acc, dem, outlet)`

Traces the upstream flow path based on maximum accumulation.

Returns: `LineString` geometry of the thalweg, or `None` if too short

#### `_export_vector(self, line, dem)`

Exports the extracted thalweg as a shapefile.

Returns: `Path` to the saved shapefile

## 6. ProfileSampler Class

A class for generating an elevation profile along a thalweg from a DEM raster.

### Methods

#### `__init__(self, dem_file, thalweg_shp, csv_out, fig_out, step)`

Initializes the profile generator.

- `dem_file` (`Path`): Input DEM raster file

- `thalweg_shp` (`Path`): Input thalweg shapefile

- `csv_out` (`Path`): Output CSV file path

- `fig_out` (`Path`): Output profile figure path

- `step` (`float`): Sampling distance along the line

#### `compute(self)`

Generates an elevation profile along the thalweg by sampling the DEM.

Returns: `Tuple` (`csv_file`, `fig_file`) with paths to the generated CSV and plot (png)

Raises: `ValueError` if the shapefile is empty or invalid

## 7. Gdal_utils function
#### `get_srs(dataset)`

Reads the `CRS (Spatial Reference System)` from a GDAL dataset.

- `dataset` (`gdal.Dataset`): Input raster path or an opened GDAL dataset.

Returns: `osr.SpatialReference` (detected `CRS` / `SRS`)

#### `reproject_to_utm32n(input_file, output_file=None)`

Reprojects a raster to UTM 32N (EPSG:32632) using GDAL Warp.

- `input_file` (`Path`): Input raster file path.

- `output_file` (`Path` or `None`): Output GeoTIFF path. If None, a new file ending in _utm32n.tif is created.

Returns: `str` (path to the reprojected raster)

#### `get_elevation(x_coord, y_coord, raster, bands, geo_trans)`

Samples elevation values from a GDAL raster at a given coordinate.

- `x_coord` (`float`): X coordinate (`lon/easting`)

- `y_coord` (`float`): Y coordinate (`lat/northing`)

- `raster` (`gdal.Dataset`): Opened GDAL dataset

- `bands` (`int`): Number of raster bands

- `geo_trans` (`tuple`: GDAL geotransform (GetGeoTransform())

Returns: `list` (`values` for each band)

## 8. Standar_step function

#### `area(south, north, west, east)`

Calculates the approximate area of a bounding box.

- `south` (`float`): Southern latitude (degrees)

- `north` (`float`): Northern latitude (degrees)

- `west` (`float`): Western longitude (degrees)

- `east` (`float`): Eastern longitude (degrees)

Returns: `float` (area in km²)

#### `densify_linestring(line, step)`

Creates equally spaced points along a `LineString`.

- `line` (`LineString`): Input line geometry

- `step` (`float`): Sampling interval (line units, usually meters)

Returns: `list` (densified points)

#### `write_to_csv(csv_out, profil_data)`

Writes distance/coordinate/elevation data to a CSV.

- `csv_out` (`Path`): Output CSV path

- `profil_data` (`list`): List of (dist, lon, lat, elev)

Returns: `None`

#### `plot_profile(x, zbed, out_png)`

Plots the longitudinal profile and saves it as a PNG.

- `x` (`np.ndarray`): Distances along the profile

- `zbed` (`np.ndarray`): Elevation values

- `out_png` (`Path`): Output PNG path

Returns: `None` (saves the figure)

#### `profile_from_raster(raster_path, line, npts)`

Extracts an elevation/profile along a line from a raster using GDAL Warp.

- `raster_path` (`str`): Path to the raster file.

- `line` (`LineString`): Shapely line geometry used to sample the raster.

- `npts` (`int`): Number of sampling points along the line.

Returns: `tuple` (`s`: distance along the line, `xy`: sampled coordinates, `z`: sampled raster values)
