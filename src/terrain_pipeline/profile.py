from __future__ import annotations
from pathlib import Path

import geopandas as gpd
import numpy as np
import rasterio

from src.terrain_pipeline.standar_step import (
    write_to_csv,
    plot_profile,
    densify_linestring
)


class ProfileSampler:
    """
    Samples elevation data from a DEM along a Thalweg line and exports results.
    """

    def __init__(
        self,
        dem_file: str | Path,
        thalweg_shp: str | Path,
        csv_out: str | Path,
        fig_out: str | Path,
        step: float
    ) -> None:
        """
        Initializes the profile sampler with necessary file paths and step size.

        Args:
            dem_file: Path to the input DEM raster.
            thalweg_shp: Path to the input Thalweg shapefile.
            csv_out: Path where the output CSV will be saved.
            fig_out: Path where the output plot will be saved.
            step: Distance interval for sampling along the line.
        """
        self.dem_file = Path(dem_file)
        self.thalweg_shp = Path(thalweg_shp)
        self.csv_out = Path(csv_out)
        self.fig_out = Path(fig_out)
        self.step = step

    def compute(self) -> tuple[Path, Path]:
        """
        Executes the sampling process, generates a CSV, and creates a plot.

        Returns:
            tuple[Path, Path]: The paths to the generated CSV and plot files.

        Raises:
            ValueError: If the shapefile is empty or geometry is invalid.
        """
        # 1. Read the Thalweg shapefile
        gdf = gpd.read_file(self.thalweg_shp)
        if gdf.empty:
            raise ValueError(f"Shapefile empty: {self.thalweg_shp}")

        line = gdf.geometry.iloc[0]
        if line is None or line.is_empty:
            raise ValueError("Empty geometry found in shapefile.")

        # 2. Sample the DEM along the line
        # Generate equidistant points based on the step size
        points = densify_linestring(line, step=self.step)
        coords = [(p.x, p.y) for p in points]

        with rasterio.open(self.dem_file) as src:
            nodata = src.nodata
            # Sample raster at point coordinates
            samples = list(src.sample(coords))
            elevation = np.array(
                [s[0] if len(s) else np.nan for s in samples],
                dtype=float
            )

        # Replace nodata values with NaN for cleaner processing
        if nodata is not None:
            elevation = np.where(elevation == nodata, np.nan, elevation)

        # 3. Organize data (distance_m, lon, lat, elevation_m)
        profile_data = []
        for i, p in enumerate(points):
            dist_m = line.project(p)  # Cumulative distance from outlet
            lon, lat = p.x, p.y
            elev_m = elevation[i]

            if not np.isnan(elev_m):
                profile_data.append((dist_m, lon, lat, elev_m))

        # 4. Export to CSV
        write_to_csv(self.csv_out, profile_data)

        # 5. Generate and save plot
        distances = [d[0] for d in profile_data]
        elevations = [d[3] for d in profile_data]
        plot_profile(distances, elevations, self.fig_out)

        print(f"Generated: {self.csv_out.name}, {self.fig_out.name}")

        return self.csv_out, self.fig_out