from __future__ import annotations
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import rasterio
from shapely.geometry import LineString, Point


def area(south: float, north: float, west: float, east: float) -> float:
    """
    Calculates the approximate surface area of a bounding box in km².

    Uses a Haversine-adjacent method by adjusting longitude width based on
    the cosine of the midpoint latitude.
    """
    mid_lat = (south + north) / 2
    # Standardize spacing around operators
    width_km = (east - west) * 111.32 * np.cos(np.radians(mid_lat))
    height_km = (north - south) * 111.32
    return width_km * height_km

def densify_linestring(line: LineString, step: float) -> list[Point]:
    """
    Creates a series of points along a LineString at a fixed distance interval.
    """
    if line.length == 0:
        return [Point(line.coords[0])]

    # Use numpy to generate steps, then interpolate points
    distances = np.arange(0, line.length, step)
    points = [line.interpolate(d) for d in distances]
    points.append(line.interpolate(line.length))

    return points

def profile_from_raster(
        raster_path: str | Path,
        line: LineString,
        npts: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Extracts elevation values along a LineString from a raster.

    Args:
        raster_path: Path to the raster file.
        line: The geometry to sample along.
        npts: Number of points to sample along the line.

    Returns:
        tuple: (distances, xy_coordinates, z_values) as numpy arrays.
    """
    xs = np.linspace(0, 1, npts)
    coords = [line.interpolate(d, normalized=True).coords[0] for d in xs]

    with rasterio.open(str(raster_path)) as src:
        zs = [v[0] for v in src.sample(coords)]

    distances = xs * line.length
    xy_coords = np.asarray(coords)
    z_values = np.asarray(zs)

    return distances, xy_coords, z_values


def write_to_csv(csv_out: str | Path, profile_data: list[tuple]) -> None:
    """
    Writes distance and elevation pairs to a CSV file.

    Args:
        csv_out: Path to the output CSV file.
        profile_data: List of tuples containing (dist, lon, lat, elev).
    """
    csv_path = Path(csv_out)
    if csv_path.exists():
        csv_path.unlink()

    with open(csv_path, 'w', encoding='utf-8') as outfile:
        outfile.write("distance_m,lon,lat,elevation_m\n")
        for dist, lon, lat, elev in profile_data:
            outfile.write(f"{dist:.2f},{lon:.6f},{lat:.6f},{elev:.2f}\n")


def plot_profile(x: list[float], z_bed: list[float], out_png: str | Path) -> None:
    """
    Generates a simple 2D plot of the terrain profile.
    """
    plt.figure(figsize=(10, 6))
    plt.plot(x, z_bed, label="Terrain elevation", color='teal', linewidth=1.5)

    plt.xlabel("Cumulative distance (m)")
    plt.ylabel("Elevation (a.m.s.l)")
    plt.title("Thalweg Longitudinal Profile")
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)
    plt.legend()

    plt.tight_layout()
    plt.savefig(out_png, dpi=200)
    print(f"Profile plot saved: {out_png}")
