import sys
import json
from pathlib import Path

from src.terrain_pipeline.dem import DEMFetcher
from src.terrain_pipeline.gdal_utils import reproject_to_utm32n
from src.terrain_pipeline.landcover import LandCoverFetcher
from src.terrain_pipeline.roughness import RoughnessCalculator
from src.terrain_pipeline.thalweg import ThalwegExtractor
from src.terrain_pipeline.profile import ProfileSampler
from src.terrain_pipeline.aoi import AOI


def get_user_input(prompt, default_val):
    """Helper to allow Enter key to accept default value."""
    user_val = input(f"{prompt} [{default_val}]: ").strip().replace(',', '.')
    return float(user_val) if user_val else default_val


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    config_path = root / "last_coords.json"
    api_key = "9b935914b43c18d9cc82f166d036e3ae"

    # Sample coordinates (Remseck am Neckar - Bad Canstatt Region)
    defaults = {
        "west": 9.16362763394136,
        "south": 48.78900873335118,
        "east": 9.28804778738413,
        "north": 48.878862334264085
    }

    # Load previous coordinates if they exist
    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                defaults.update(json.load(f))
        except Exception:
            pass

    print("--- Terrain Pipeline: Coordinate Input for AOI ---")
    print("Press [ENTER] to keep the previous value or type a new coordinate:")

    try:
        west = get_user_input("  West ", defaults["west"])
        south = get_user_input("  South", defaults["south"])
        east = get_user_input("  East ", defaults["east"])
        north = get_user_input("  North", defaults["north"])

        # Save these for next time
        with open(config_path, "w") as f:
            json.dump({"west": west, "south": south, "east": east, "north": north}, f)

        print("\n[1/7] Validating AOI...")
        aoi = AOI(west, south, east, north)
        if not aoi.validate():
            print("Error: Invalid bounding box.")
            sys.exit(1)
        bbox = aoi.get_bbox()

    except ValueError:
        print("Error: Input must be numeric.")
        sys.exit(1)

    # --- Processing Pipeline ---
    try:
        # 1. Download DEM
        print("[2/7] Fetching DEM data...")
        dem_path = root / "results" / "dem_wgs84.tif"
        dem_path.parent.mkdir(parents=True, exist_ok=True)
        dem_fetcher = DEMFetcher(api_key=api_key)
        dem_file = dem_fetcher.download(south, north, west, east, output_file=dem_path)

        # 2. Source Files
        landcover_file = root / "data" / "LandCover_source.tif"

        # 3. CRS & Reprojection
        print("[3/7] Checking CRS and reprojecting to UTM 32N...")
        utm_file_landcover = reproject_to_utm32n(landcover_file)
        utm_file_dem = reproject_to_utm32n(dem_file)

        # 4. Landcover Match
        print("[4/7] Matching Landcover...")
        out_landcover = root / "results" / "LandCover_matched.tif"
        out_landcover.parent.mkdir(parents=True, exist_ok=True)
        landcover_matcher = LandCoverFetcher(output_file=dem_file,
                                              output_src=utm_file_landcover,
                                              output_landcover_file=out_landcover)
        landcover_matcher.match()

        # 5. Roughness
        print("[5/7] Calculating Roughness...")
        rough_file = root / "results" / "roughness.tif"
        roughness_calc = RoughnessCalculator(out_landcover, rough_file)
        roughness_calc.compute()

        # 6. Thalweg
        print("[6/7] Extracting Thalweg...")
        thalweg_output = root / "results" / "Thalweg.shp"
        thalweg_output.parent.mkdir(parents=True, exist_ok=True)
        thalweg = ThalwegExtractor(utm_file_dem, thalweg_output, threshold=5000)
        thalweg_file = thalweg.compute()

        # 7. Profile
        print("[7/7] Sampling Profile...")
        csv_out = root / "results" / "profile.csv"
        fig_out = root / "figures" / "profile.png"
        profile = ProfileSampler(utm_file_dem, thalweg_file, csv_out, fig_out, step=30)
        profile.compute()

        print("\nAll process complete! Saved outputs to /results and figures folder.")

    except Exception as e:
        print(f"Error: {e}")