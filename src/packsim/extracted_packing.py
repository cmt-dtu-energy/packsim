from typing import Any

from .hexagonal_prism import HexagonalPrism


class ExtractedPacking:
    """Class to handle the extraction of packing data from a simulation."""

    def __init__(
        self,
        prisms: list[HexagonalPrism],
        volume: float,
        xmin: float,
        xmax: float,
        ymin: float,
        ymax: float,
        zmin: float,
        zmax: float,
        volumetric_filling_fraction: float,
        average_alignment_x: float,
        average_alignment_y: float,
        average_alignment_z: float,
        standard_deviation_alignment_x: float,
        standard_deviation_alignment_y: float,
        standard_deviation_alignment_z: float,
        volume_weighted_average_alignment_x: float,
        volume_weighted_average_alignment_y: float,
        volume_weighted_average_alignment_z: float,
        volume_weighted_standard_deviation_alignment_x: float,
        volume_weighted_standard_deviation_alignment_y: float,
        volume_weighted_standard_deviation_alignment_z: float,
    ) -> None:
        """Initialize the ExtractdPacking class."""
        self.items = prisms
        self.volume = volume
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.zmin = zmin
        self.zmax = zmax
        self.volumetric_filling_fraction = volumetric_filling_fraction
        self.average_alignment_x = average_alignment_x
        self.average_alignment_y = average_alignment_y
        self.average_alignment_z = average_alignment_z
        self.standard_deviation_alignment_x = standard_deviation_alignment_x
        self.standard_deviation_alignment_y = standard_deviation_alignment_y
        self.standard_deviation_alignment_z = standard_deviation_alignment_z
        self.volume_weighted_average_alignment_x = volume_weighted_average_alignment_x
        self.volume_weighted_average_alignment_y = volume_weighted_average_alignment_y
        self.volume_weighted_average_alignment_z = volume_weighted_average_alignment_z
        self.volume_weighted_standard_deviation_alignment_x = (
            volume_weighted_standard_deviation_alignment_x
        )
        self.volume_weighted_standard_deviation_alignment_y = (
            volume_weighted_standard_deviation_alignment_y
        )
        self.volume_weighted_standard_deviation_alignment_z = (
            volume_weighted_standard_deviation_alignment_z
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ExtractedPacking":
        """Create an ExtractedPacking instance from a dictionary."""
        prisms = [
            HexagonalPrism(
                radius=prism["radius"],
                thickness=prism["thickness"],
                normal=prism["normal"],
                position=prism["position"],
                face_rotation=prism["faceRotation"],
                vertices=prism["vertices"],
            )
            for prism in data["items"]
        ]
        return cls(
            prisms=prisms,
            volume=data["volume"],
            xmin=data["xmin"],
            xmax=data["xmax"],
            ymin=data["ymin"],
            ymax=data["ymax"],
            zmin=data["zmin"],
            zmax=data["zmax"],
            volumetric_filling_fraction=data["volumetricFillingFraction"],
            average_alignment_x=data["averageAlignmentX"],
            average_alignment_y=data["averageAlignmentY"],
            average_alignment_z=data["averageAlignmentZ"],
            standard_deviation_alignment_x=data["standardDeviationAlignmentX"],
            standard_deviation_alignment_y=data["standardDeviationAlignmentY"],
            standard_deviation_alignment_z=data["standardDeviationAlignmentZ"],
            volume_weighted_average_alignment_x=(
                data["volumeWeightedAverageAlignmentX"]
            ),
            volume_weighted_average_alignment_y=(
                data["volumeWeightedAverageAlignmentY"]
            ),
            volume_weighted_average_alignment_z=(
                data["volumeWeightedAverageAlignmentZ"]
            ),
            volume_weighted_standard_deviation_alignment_x=data[
                "volumeWeightedStandardDeviationAlignmentX"
            ],
            volume_weighted_standard_deviation_alignment_y=data[
                "volumeWeightedStandardDeviationAlignmentY"
            ],
            volume_weighted_standard_deviation_alignment_z=data[
                "volumeWeightedStandardDeviationAlignmentZ"
            ],
        )
