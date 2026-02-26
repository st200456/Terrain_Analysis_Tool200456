from __future__ import annotations
from pathlib import Path

import requests

from src.terrain_pipeline.standar_step import area

class DEMFetcher:
    """
    Handles interaction with the OpenTopography API to retrieve DEM data.

    This class provides methods to download global Digital Elevation Models(DEM)
    specifically using the SRTM GL1 (30m) dataset.
    """
    def __init__(self, api_key=None) -> None:
        """
        Initializes the DemFetcher with an optional API key.

        Args:
        api_key: OpenTopography API key for higher usage limits.
        """
        self.api_key = api_key
        self.demtype = "SRTMGL1"
        self.base_url = "https://portal.opentopography.org/API/globaldem"

    def download(self, south, north, west, east, output_file="dem_wgs84.tif"):
        """
        Downloads a GeoTiff DEM for the specified bounding box.
        
        Args:
            south: Southern latitude boundary.
            north: Northern latitude boundary.
            west: Western longitude boundary.
            east: Eastern longitude boundary.
            output_file: The filename or path where the .tif will be saved.
            
        Returns:
            Path: The location of the downloaded file.

        Raises:
            Exception: If the API request fails or returns a non-200 status code.
        """
        self.output_path = Path(output_file)
        params = {
            "demtype": self.demtype,
            "south": south,
            "north": north,
            "west": west,
            "east": east,
            "outputFormat": "GTiff",}

        if self.api_key:
            params["API_Key"] = self.api_key

        print(f"DEM for bbox: ({west}, {south}) to ({east}, {north})")

        # Calculate approximate area to verify < 100 km²
        area_km2 = area(south, north, west, east)
        print(f"Approximate area: {area_km2:.2f} km²")
        if area_km2 > 100:
            print("Warning: Area exceeds 100 km²")

        # Download the DEM
        response = requests.get(self.base_url, params=params, stream=True)

        if response.status_code == 200:
            with open(self.output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"DEM downloaded successfully: {self.output_path}")
            return self.output_path

        raise Exception(
            f"Download failed: {response.status_code} - {response.text}"
        )
