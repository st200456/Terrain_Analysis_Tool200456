class AOI:
    """
    Validates Area of Interest (AOI) bounding box coordinates
    for DEM data acquisition.
    """

    def __init__(self, west: float, south: float, east: float, north: float):
        """
        Initializes the validator with bounding box coordinates.

        Args:
            west: Minimum longitude.
            south: Minimum latitude.
            east: Maximum longitude.
            north: Maximum latitude.
        """
        self.west = west
        self.south = south
        self.east = east
        self.north = north

    def validate(self) -> bool:
        """
        Runs all verification checks.

        Returns:
            bool: True if valid.

        Raises:
            ValueError: If any validation check fails.
        """
        self.check_types()
        self.check_ranges()
        self.check_logic()

        print(
            f"AOI Validated: "
            f"[{self.west}, {self.south}, {self.east}, {self.north}]"
        )
        return True

    def check_types(self) -> None:
        """Ensure all inputs are numeric."""
        coords = [
            ("west", self.west),
            ("south", self.south),
            ("east", self.east),
            ("north", self.north)
        ]

        for name, val in coords:
            if not isinstance(val, (int, float)):
                raise ValueError(
                    f"Invalid type for {name}: {type(val)}. "
                    f"Expected int or float."
                )

    def check_ranges(self) -> None:
        """Ensure coordinates fall within global WGS84 limits."""
        if not (-180 <= self.west <= 180) or not (-180 <= self.east <= 180):
            raise ValueError("Longitude must be between -180 and 180.")

        if not (-90 <= self.south <= 90) or not (-90 <= self.north <= 90):
            raise ValueError("Latitude must be between -90 and 90.")

    def check_logic(self) -> None:
        """Ensure min values are actually smaller than max values."""
        if self.west >= self.east:
            raise ValueError(
                "Invalid Longitude: West (min_x) must be less than East (max_x)."
            )

        if self.south >= self.north:
            raise ValueError(
                "Invalid Latitude: South (min_y) must be less than North (max_y)."
            )

    def get_bbox(self) -> dict[str, float]:
        """Returns the coordinates in a format used by OpenTopography."""
        return {
            "west": self.west,
            "south": self.south,
            "east": self.east,
            "north": self.north
        }