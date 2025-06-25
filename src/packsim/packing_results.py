from pathlib import Path

from .extracted_packing import ExtractedPacking
from .particle import Particle


class PackingResults:
    """Results of a packing simulation."""

    def __init__(
        self,
        particleA: Particle,
        particleB: Particle | None,
        mass_fraction_B: float,
        num_cubes_xy: int,
        num_cubes_z: int,
        L: float,
        workdir: Path,
        cutoff: float,
        cutoff_direction: str,
        stl_path: Path,
        blender_path: Path,
        packgen_json_path: Path,
        extracted_packing: ExtractedPacking,
    ) -> None:
        """Initialize results from a packing simulation."""
        self.particleA: Particle = particleA
        self.particleB: Particle | None = particleB
        self.mass_fraction_B: float = mass_fraction_B
        self.num_cubes_xy: int = num_cubes_xy
        self.num_cubes_z: int = num_cubes_z
        self.L: float = L
        self.workdir: Path = workdir
        self.cutoff: float = cutoff
        self.cutoff_direction: str = cutoff_direction
        self.stl_path: Path = stl_path
        self.blender_path: Path = blender_path
        self.packgen_json_path: Path = packgen_json_path
        self.extracted_packing: ExtractedPacking = extracted_packing
