import numpy as np
import geopandas as gpd
from shapely.geometry import LineString
from pathlib import Path
from pysheds.grid import Grid

class ThalwegExtractor:
    """
A tool for extracting the main channel (thalweg) from a Digital Elevation Model.
This class processes a DEM to compute hydrological parameters and traces
the path of maximum flow accumulation from an outlet point upstream.
    """

    def __init__(self, dem_file, output_vector="Thalweg.shp",
                 threshold=5000, outlet_coords=None):
        """
        Initializes the ThalwegExtractor with configuration parameters.

        Args:
        dem_file: Path to the input DEM raster file.
        output_vector: Path where the resulting Shapefile will be saved.
        threshold: Minimum flow accumulation value to continue tracing upstream.
        outlet_coords: Optional (x, y) coordinates in the DEM's CRS for the outlet.
        """
        self.dem_file = Path(dem_file)
        self.output_vector = Path(output_vector)
        self.threshold = threshold
        self.outlet_coords = outlet_coords


    def compute(self):
        """
        Executes the full pipeline: hydrology, outlet detection, tracing,
         and export.
         Returns:
            Path: The path to the saved Shapefile if successful, None otherwise.
        """
        grid, dem, flow_dir, flow_acc = self._compute_hydrology()

        outlet = self._get_outlet(flow_acc, dem)

        line = self._trace_thalweg(flow_dir, flow_acc, dem, outlet)

        if line is None:
            print("Thalweg extraction failed.")
            return None

        return self._export_vector(line, dem)

    def _compute_hydrology(self):
        """
        reprocesses the DEM to compute flow direction and accumulation.
        Returns:
        Tuple containing the Pysheds Grid, Raster object, flow direction array,
        and flow accumulation array."""
        grid = Grid.from_raster(str(self.dem_file))
        dem = grid.read_raster(str(self.dem_file))

        dem_filled = grid.fill_depressions(dem)
        dem_flat = grid.resolve_flats(dem_filled)

        # Standard D8 dirmap
        dirmap = (64, 128, 1, 2, 4, 8, 16, 32)

        flow_dir = grid.flowdir(dem_flat, dirmap=dirmap)
        flow_acc = grid.accumulation(flow_dir, dirmap=dirmap)

        return grid, dem, np.array(flow_dir), np.array(flow_acc)


    def _get_outlet(self, flow_acc, dem):
        """
         Determines the starting cell (row, col) for the upstream trace.

        Args:
        flow_acc: 2D array of flow accumulation values.
        dem: Raster object containing affine transformation data.

        Returns:
        Tuple of (row, col) indices.
                """
        if self.outlet_coords:
            x, y = self.outlet_coords
            col, row = ~dem.affine * (x, y)
            return (int(row), int(col))

        # Auto outlet = cell with max accumulation
        return np.unravel_index(np.argmax(flow_acc), flow_acc.shape)


    def _trace_thalweg(self, flow_dir, flow_acc, dem, outlet):
        """
        Traces the path of maximum accumulation from the outlet to the headwaters.

        Args:
        flow_dir: 2D array of flow direction codes.
        flow_acc: 2D array of flow accumulation values.
        dem: Raster object for coordinate transformation.
        outlet: The (row, col) starting point.

        Returns:
        LineString object representing the thalweg, or None if too short.
        """
        reverse_dirmap = {
            64: (-1, 0), 128: (-1, 1), 1: (0, 1), 2: (1, 1),
            4: (1, 0), 8: (1, -1), 16: (0, -1), 32: (-1, -1)
        }

        rows, cols = flow_acc.shape
        current = outlet
        path_cells = []

        while True:
            path_cells.append(current)
            r, c = current
            upstream = []

            for code, (dr, dc) in reverse_dirmap.items():
                nr, nc = r + dr, c + dc

                if 0 <= nr < rows and 0 <= nc < cols:
                    # Check if neighbours flow points to current cell
                    neighbour_move = reverse_dirmap.get(flow_dir[nr, nc])
                    if neighbour_move:
                        fr, fc = nr + neighbour_move[0], nc + neighbour_move[1]
                        if (fr, fc) == (r, c):
                            upstream.append((nr, nc))

            if not upstream:
                break

            # Move to neighbour with highest accumulation
            current = max(upstream, key=lambda x: flow_acc[x])

            if flow_acc[current] < self.threshold:
                break

        if len(path_cells) < 2:
            return None

        coords = []
        for r, c in path_cells:
            # Shift to cell center (0.5) and transform to CRS coords
            x, y = dem.affine * (c + 0.5, r + 0.5)
            coords.append((x, y))

        return LineString(coords)

    # Vector export (Shapefile)
    def _export_vector(self, line, dem):
        """
        Saves the resulting LineString to an ESRI Shapefile.

        Args:
        line: The geometry to export.
        dem: Raster object containing the CRS.

        Returns:
        Path: The path to the saved .shp file.
        """

        length_m = round(line.length, 2)

        gdf = gpd.GeoDataFrame(
            [{'geometry': line, 'length_m': length_m}],
            crs=dem.crs
        )

        # Using ESRI Shapefile driver
        gdf.to_file(self.output_vector, driver="ESRI Shapefile")

        print(f"Thalweg saved to: {self.output_vector}")
        print(f"Length (m): {length_m}")

        return self.output_vector


