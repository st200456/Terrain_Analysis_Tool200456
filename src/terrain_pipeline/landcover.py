from __future__ import annotations
from pathlib import Path

from osgeo import gdal

# Standard practice to enable GDAL exceptions globally
gdal.UseExceptions()


class LandCoverFetcher:
    """
    Handles the spatial matching of landcover rasters to a target DEM extent.
    """

    def __init__(
        self,
        output_file: str | Path,
        output_src: str | Path,
        output_landcover_file: str | Path
    ) -> None:
        """
        Initializes the Landcover matcher with source and target paths.

        Args:
            output_file: The target DEM/reference file to match.
            output_src: The raw source landcover raster.
            output_landcover_file: The path for the matched output raster.
        """
        self.output_file = Path(output_file)
        self.output_src = Path(output_src)
        self.output_landcover_file = Path(output_landcover_file)
        self.crs: str | None = None

    def match(self) -> Path:
        """
        Warps the source landcover to the exact CRS, extent, and resolution
         of the target reference file.

        Returns:
            Path: The path to the newly created matched landcover file.
        """
        # Open datasets
        source_dataset = gdal.Open(str(self.output_file), gdal.GA_ReadOnly)
        src_ds = gdal.Open(str(self.output_src), gdal.GA_ReadOnly)

        self.crs = source_dataset.GetProjection()

        # Extract spatial metadata from the reference dataset
        sr_source_dataset = source_dataset.GetProjection()
        src_geo_transform = source_dataset.GetGeoTransform()

        # Get raster dimensions
        x_size = source_dataset.RasterXSize
        y_size = source_dataset.RasterYSize

        # Calculate bounding box coordinates
        min_x = src_geo_transform[0]
        max_y = src_geo_transform[3]
        max_x = min_x + src_geo_transform[1] * x_size
        min_y = max_y + src_geo_transform[5] * y_size

        # Perform the spatial warp (matching resolution and extent)
        out_ds = gdal.Warp(
            destNameOrDestDS=str(self.output_landcover_file),
            srcDSOrSrcDSTab=src_ds,
            dstSRS=sr_source_dataset,
            outputBounds=(min_x, min_y, max_x, max_y),
            width=x_size,
            height=y_size,
            resampleAlg="near",
            format="GTiff",
            creationOptions=["COMPRESS=LZW", "TILED=YES"]
        )

        # Close the datasets by clearing references
        source_dataset = None
        src_ds = None
        out_ds = None

        return self.output_landcover_file

    def __str__(self) -> str:
        return (
            f"LandCover match: {self.output_file.name} -> "
            f"{self.output_landcover_file.name}"
        )