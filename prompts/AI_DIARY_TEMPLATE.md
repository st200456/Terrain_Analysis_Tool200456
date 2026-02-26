# AI Collaboration Diary

## 2025-12-17
Prompt 1 : " I need to write a code that downloads a DEM from OpenTopography 
for a user-supplied WGS84 bounding box no larger than 10 km by 10 km.
what are the steps?."
Assistant suggestion: "Set up API Request, computes approximate area and 
download DEM as GeoTiff "
Decision: Accepted structure,rewrote code and reprojected DEM from WGS84 to UTM.
Verification: Opened DEM in QGIS to check output file format

## 2026-02-12
Prompt 2: " I want to use pysheds and D8 routing to extract the thalweg as 
a shapefile. what are the steps?
Assistant suggestion: "Load and preprocess the DEM,Compute flow direction,
Compute flow accumulation,Extract streams,Identify the thalweg,
Convert the thalweg to a shapefile"
Decision: Accepted structure, the stream accumulation in cells as threshold, 
applied a binary mask to cells < threshold. and plotted the streams  
Verification: Opened DEM in QGIS to check output file format

## 2026-02-22
Prompt 3: " I need to extract only the main thalweg from my stream network.
How can I modify my code?"
Assistant suggestion: "Automatically select the outlet as the cell with maximum
flow accumulation (unless user-defined). Trace upstream by:
Identifying all neighboring cells that flow into the current cell
Selecting the upstream cell with the highest flow accumulation
Continuing until no upstream cells exist or accumulation drops below a threshold
Converting traced raster cells to CRS coordinates
Exporting a single LineString as a Shapefile
Decision: Accepted the code provided. 
Verification: Opened DEM in QGIS to check if a single polyline was created and
that it follows the drainage path  

## 2026-02-20
Prompt 4: "How can I simplify file paths in Python using Path without writing
long path expressions?"
Assitant suggestion: You can store the base directory in a variable called root
and build paths like Export_file = root / "Results" / "Export.tif".
Decision: We use a root variable because it makes the code shorter, cleaner,
and easier to maintain.
Verification: check if the program correctly accesses files using
the root path variable.

## 2026-02-15
Prompt 5: How can I extract a band from a land cover raster using GDAL and
convert it into a roughness raster?
Assitant suggestion: You can use GDAL to read the raster band with GetRasterBand(), 
convert land cover classes to roughness values using a lookup table, and save the
result as a new raster.
Decision: We use GDAL because it is widely used for geospatial raster processing
and preserves georeferencing information.
Verification: Verify if the output raster contains the correct
roughness values and keeps the original spatial reference and resolution.

## 2026-02-15
Prompt 6: Is it necessary to use -9999 as the NoData value when working with 
raster data?
Assitant suggestion: You can use -9999 as a NoData value because it is commonly
recognized by GIS software, but other values or NaN can also be used.
Decision: We choose -9999 because it ensures compatibility with most geospatial 
tools and workflows.
Verification: The solution is verified if GIS software correctly recognizes -9999
pixels as NoData in the output raster.

## 2026-02-15
Prompt 7: How can I map land cover class values to Manning’s n roughness values
in Python?
Assitant suggestion: Create an output array filled with the NoData value and then
assign Manning’s n values by replacing pixels where the land cover equals each 
class code from a lookup dictionary.
Decision: We use a dictionary-based mapping loop because it is simple, readable,
and easy to update when landcover classes or Manning’s n values change.
Verification: The mapping is correct if pixels with each land cover class code
receive the expected Manning’s n value and all unmapped pixels remain as NoData.

## 2026-02-15
Prompt 8: Are the gdal.Warp() parameters (like dstSRS, outputBounds, width/height,
resampleAlg, format, and creationOptions) necessary when creating an output
landcover raster?
Assitant suggestion: These parameters are only necessary if you need to reproject,
crop to a specific extent, force an exact output size, control resampling, or set
output GeoTIFF options like compression and tiling.
Decision: We keep these parameters because I want a landcover output that matches 
a specific CRS, extent, and grid, and because near preserves class values while 
COMPRESS=LZW and TILED=YES improve file performance.
Verification: The parameters are validated if the output raster has the intended
CRS, bounds, resolution, and correct landcover classes (no category mixing), and
the file is efficiently stored as a compressed, tiled GeoTIFF.

## 2026-02-20
Prompt 9: When should empty data checks be used in Python before processing 
spatial or structured data?
Assitant suggestion: Empty checks should be used before performing operations
that assume the presence of valid data, such as indexing, calculations, or 
spatial analysis, to prevent runtime errors.
Decision: We include empty data validation to make the script more robust and to
fail early with clear error messages instead of unexpected crashes.
Verification: The approach is correct if the program stops gracefully when given
empty input and runs successfully when valid data is provided.

## 2026-02-23
Prompt 10: Why is it important to densify a LineString before spatial analysis,
and how can this be done in Python?
Assitant suggestion: Densifying a LineString improves spatial accuracy by creating
regularly spaced points along the geometry, which can be done by interpolating
points along the line and ensuring the final endpoint is included.
Decision: We densify the LineString to obtain consistent sampling along the 
geometry and avoid missing important spatial variations
Verification: The method is validated if the generated points follow the line at
regular intervals and the full geometry, including the endpoint, is represented 
correctly.

## 2026-02-26
Prompt 11 : "I want to modify the code such that the coordinates input runs in
a user-friendly manner such that when I run the code it ask for the user to 
input each coordinate east,north,west south" 
Assitant suggestion:provided a user input code for coordinates. 
Decision: accepted the code and added it to main script. 
Verification: Run the code to see if it works 

## 2026-02-26
Prompt 12: "it works perfect but can it save the previous coordinate and the user
need to modify it instead input all the time ?" 
Assitant suggestion:we'll implement a simple JSON-based "memory" file. 
The script will look for a config.json file. If it exists, it will display the
old coordinates and let the user press Enter to keep them or type a new value 
to change them
Decision: accepted the code and added it to main script. 
Verification: Run the code to see if it works 

