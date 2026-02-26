from __future__ import annotations
from pathlib import Path

from osgeo import gdal, osr

def get_srs(dataset: str | Path | gdal.Dataset) -> osr.SpatialReference:
    """
    Retrieves the Spatial Reference System (SRS) from a GDAL-compatible dataset.

    Args:
        dataset: Path to the raster file or an already opened GDAL dataset.

    Returns:
        osr.SpatialReference: The identified spatial reference object.
    """
    if isinstance(dataset, (str, Path)):
        dataset = gdal.Open(str(dataset), gdal.GA_ReadOnly)

    sr = osr.SpatialReference()
    sr.ImportFromWkt(dataset.GetProjection())

    # Auto-detect EPSG
    if sr.AutoIdentifyEPSG() != 0:
        # FindMatches returns list of tuples (SpatialReference, similarity)
        matches = sr.FindMatches()
        if matches:
            sr = matches[0][0]
            sr.AutoIdentifyEPSG()

    # Assign input SpatialReference code
    code = sr.GetAuthorityCode(None)
    if code:
        sr.ImportFromEPSG(int(code))


    return sr

def get_elevation(
        x_coord: float,
        y_coord: float,
        raster: any,
        bands: int,
        geo_trans: tuple
) -> list[float]:
    """
    Extracts elevation values from a GDAL raster at a specific coordinate.
    """
    elev_list = []
    x_origin = geo_trans[0]
    y_origin = geo_trans[3]
    pix_width = geo_trans[1]
    pix_height = geo_trans[5]

    x_pt = int((x_coord - x_origin) / pix_width)
    y_pt = int((y_coord - y_origin) / pix_height)

    for band_num in range(bands):
        ras_band = raster.GetRasterBand(band_num + 1)
        ras_data = ras_band.ReadAsArray(x_pt, y_pt, 1, 1)
        elev_list.append(ras_data[0][0])

    return elev_list


def reproject_to_utm32n(
        input_file: str | Path,
        output_file: str | Path | None = None
) -> str:
    """
    Reprojects a raster file to UTM Zone 32N (EPSG:32632).

    Args:
        input_file: Path to the source raster.
        output_file: Path for the reprojected raster. Defaults to suffixing input.

    Returns:
        str: The string path to the output file.
    """
    input_path = Path(input_file)
    if output_file is None:
        output_path = input_path.with_name(f"{input_path.stem}_utm32n.tif")
    else:
        output_path = Path(output_file)

    dst_crs = "EPSG:32632"
    print(f"Reprojecting {input_path.name} -> {output_path.name} ({dst_crs})")

    gdal.Warp(
        str(output_path),
        str(input_path),
        dstSRS=dst_crs,
        resampleAlg=gdal.GRA_Bilinear,
        format="GTiff"
    )
    return str(output_path)