import math
from typing import Any

from .hexagonal_prism import HexagonalPrism
from .particle import Particle


class ExtractedPacking:
    """Class to handle the extraction of packing data from a simulation."""

    def __init__(
        self,
        prisms: list[HexagonalPrism],
        particleA: Particle,
        particleB: Particle | None,
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
        Lx: float,
        Ly: float,
        Lz: float,
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
        self.particleA: Particle = particleA
        self.particleB: Particle | None = particleB
        self.actual_mass_fraction_B = self._calculate_mass_fraction_B()
        self.Lx = Lx
        self.Ly = Ly
        self.Lz = Lz

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
                density=prism["density"],
            )
            for prism in data["items"]
        ]
        return cls(
            prisms=prisms,
            volume=data["volume"],
            particleA=Particle.from_dict(data["particleA"]),
            particleB=Particle.from_dict(data["particleB"])
            if data.get("particleB") is not None
            else None,
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
            Lx=data["Lx"],
            Ly=data["Ly"],
            Lz=data["Lz"],
        )

    def _calculate_mass_fraction_B(self) -> float:
        """Calculate the mass fraction of particle B in the packing."""
        if self.particleB is None:
            return 0.0
        total_mass = sum(prism.mass for prism in self.items)
        if total_mass == 0:
            return 0.0
        mass_B = sum(
            prism.mass
            for prism in self.items
            if math.isclose(prism.density, self.particleB.density, rel_tol=1e-3)
        )
        return mass_B / total_mass if total_mass > 0 else 0.0
