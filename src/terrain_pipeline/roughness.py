from __future__ import annotations
from pathlib import Path

import numpy as np
from osgeo import gdal


class RoughnessCalculator:
    """
    Computes a Manning's n roughness raster based on land cover classification.

    This class maps specific land cover classes (ESA WorldCover) to
    standard hydraulic roughness coefficients used in hydrodynamic modeling.
    """

    # Manning roughness coefficients according to ESA WorldCover classes
    MANNINGS_MAP = {
        10: 0.120,  # Dense forest
        20: 0.070,  # Shrub vegetation
        30: 0.040,  # Grassland
        40: 0.050,  # Cropland
        50: 0.070,  # Urban
        60: 0.030,  # Sparse vegetation / bare
        70: 0.015,  # Snow / ice
        80: 0.025,  # Water bodies / channels
        90: 0.080,  # Wetlands
        95: 0.120,  # Mangroves
        100: 0.035,  # Moss / lichen
    }

    def __init__(self, landcover_file: str | Path, out_file: str | Path) -> None:
        """
        Initializes the Roughness generator with input and output paths.

        Args:
            landcover_file: Path to the input land cover classification raster.
            out_file: Path where the Manning's n raster will be saved.
        """
        self.landcover_file = Path(landcover_file)
        self.out_file = Path(out_file)

    def compute(self) -> Path:
        """
        Executes the raster reclassification to produce a Manning's n map.

        Returns:
            Path: The path to the generated roughness raster.

        Raises:
            RuntimeError: If the land cover file cannot be opened.
        """
        ds = gdal.Open(str(self.landcover_file))
        if ds is None:
            raise RuntimeError(f"Cannot open {self.landcover_file}")

        band = ds.GetRasterBand(1)
        data = band.ReadAsArray()
        nodata = band.GetNoDataValue()

        if nodata is None:
            nodata = -9999.0

        # Create output raster
        driver = gdal.GetDriverByName("GTiff")
        out_ds = driver.Create(
            str(self.out_file),
            ds.RasterXSize,
            ds.RasterYSize,
            1,
            gdal.GDT_Float32
        )

        out_ds.SetProjection(ds.GetProjection())
        out_ds.SetGeoTransform(ds.GetGeoTransform())

        # Mapping Manning n coefficients
        roughness = np.full(data.shape, nodata, dtype=np.float32)

        for cls, val in self.MANNINGS_MAP.items():
            roughness[data == cls] = val

        out_band = out_ds.GetRasterBand(1)
        out_band.WriteArray(roughness)
        out_band.SetNoDataValue(nodata)

        return self.out_file

    def __str__(self) -> str:
        return (
            f"Compute Manning Roughness: "
            f"{self.landcover_file.name} -> {self.out_file.name}"
        )