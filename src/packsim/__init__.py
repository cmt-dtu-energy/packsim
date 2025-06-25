"""Module for simulating packing of particles."""

import json
import subprocess
from pathlib import Path
from typing import Any

from numpy.typing import ArrayLike


class Particle:
    """A single particle in the packing."""

    def __init__(self, radius: float, thickness: float, density: float):
        """Initialize a particle with given properties.

        Args:
            radius (float): Radius of the particle in meters.
            thickness (float): Thickness of the particle in meters.
            density (float): Density of the particle in kg/m3.
        """
        self.radius: float = radius
        self.thickness: float = thickness
        self.density: float = density


class HexagonalPrism:
    """A hexagonal prism particle in the packing."""

    def __init__(
        self,
        radius: float,
        thickness: float,
        normal: ArrayLike,
        position: ArrayLike,
        face_rotation: ArrayLike,
        vertices: ArrayLike,
    ):
        """Initialize a hexagonal prism particle with given properties.
        Args:
            radius (float): Radius of the hexagonal prism in meters.
            thickness (float): Thickness of the hexagonal prism in meters.
            normal (ArrayLike): Normal vector of the hexagonal prism.
            position (ArrayLike): Position of the hexagonal prism in space.
            face_rotation (ArrayLike): Rotation of the faces of the prism.
            vertices (ArrayLike): Vertices of the hexagonal prism.
        """

        self.radius: float = radius
        self.thickness: float = thickness
        self.normal: ArrayLike = normal
        self.position: ArrayLike = position
        self.face_rotation: ArrayLike = face_rotation
        self.vertices: ArrayLike = vertices

        # Expression for the volume of a hexagonal prism
        # from given circumscribed circle radius and thickness.
        self.volume: float = 3 / 2 * (3**0.5) * self.radius**2 * self.thickness


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
        self.volume_weighted_average_alignment_x = (
            volume_weighted_average_alignment_x
        )
        self.volume_weighted_average_alignment_y = (
            volume_weighted_average_alignment_y
        )
        self.volume_weighted_average_alignment_z = (
            volume_weighted_average_alignment_z
        )
        self.volume_weighted_standard_deviation_alignment_x = (
            (volume_weighted_standard_deviation_alignment_x),
        )
        self.volume_weighted_standard_deviation_alignment_y = (
            (volume_weighted_standard_deviation_alignment_y),
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


class PackingSimulation:
    """Simulation for the process of packing particles."""

    def __init__(
        self,
        particleA: Particle,
        particleB: Particle | None,
        mass_fraction_B: float,
        num_cubes_xy: int,
        num_cubes_z: int,
        L: float,
        workdir: Path,
    ):
        """Initialize the packing simulation with particles and parameters.

        Args:
            particleA (Particle): The first particle type.
            particleB (Particle | None): The second particle type, if any.
            mass_fraction_B (float): Mass fraction of particle B.
            num_cubes_xy (int): Number of cubes in the XY plane.
            num_cubes_z (int): Number of cubes in the Z direction.
            L (float): Length of the simulation box in meters.
            workdir (Path): Directory for storing simulation results.
        """
        self.particleA: Particle = particleA
        self.particleB: Particle | None = particleB
        self.mass_fraction_B: float = mass_fraction_B
        self.num_cubes_xy: int = num_cubes_xy
        self.num_cubes_z: int = num_cubes_z
        self.L: float = L
        self.workdir: Path = workdir
        self.workdir.mkdir(parents=True, exist_ok=True)

    def run(self, cutoff: float, cutoff_direction: str) -> PackingResults:
        """Run the packing simulation.

        Args:
            cutoff (float): Cutoff distance for the simulation.
            cutoff_direction (str): Direction of the cutoff, e.g.,
                'x', 'y', or 'z'.
        """
        stl_path, blender_path, packgen_json_path = self._run_packgen()
        extracted_packing = self._run_stl_extractor(stl_path)
        return PackingResults(
            particleA=self.particleA,
            particleB=self.particleB,
            mass_fraction_B=self.mass_fraction_B,
            num_cubes_xy=self.num_cubes_xy,
            num_cubes_z=self.num_cubes_z,
            L=self.L,
            workdir=self.workdir,
            cutoff=cutoff,
            cutoff_direction=cutoff_direction,
            stl_path=stl_path,
            blender_path=blender_path,
            packgen_json_path=packgen_json_path,
            extracted_packing=extracted_packing,
        )

    def _run_packgen(self) -> tuple[Path, Path, Path]:
        """Run the packgen tool to generate the packing."""
        # Create configuration for packgen based on the simulation parameters.
        config = {
            "seed": None,
            "scale": 1,
            # packgen does not accept zero values for the properties,
            # even if the particle is not present.
            "r_B": self.particleB.radius if self.particleB else 1,
            "r_A": self.particleA.radius,
            "thickness_B": self.particleB.thickness if self.particleB else 1,
            "thickness_A": self.particleA.thickness,
            "density_B": self.particleB.density if self.particleB else 1,
            "density_A": self.particleA.density,
            "mass_fraction_B": self.mass_fraction_B,
            "num_cubes_x": self.num_cubes_xy,
            "num_cubes_y": self.num_cubes_xy,
            "num_cubes_z": self.num_cubes_z,
            "num_sides": 6,
            "distance": self.L / self.num_cubes_xy,
            "quit_on_finish": True,
        }

        # create unique subdir inside workdir for this simulation
        # subdirectories end with a number to ensure uniqueness
        # workdir is a Path object
        subdir = (
            self.workdir /
            f"simulation_{len(list(self.workdir.glob('simulation_*')))}"
        )
        subdir.mkdir(parents=True, exist_ok=True)
        # Save the configuration to a json file in the workdir.
        basename = "parameters"
        config_path = subdir / f"{basename}.json"
        with open(config_path, "w") as f:
            import json

            json.dump(config, f, indent=4)

        # Run the packgen command with the configuration file, from workdir.
        packgen_args = ["packgen", "--", str(config_path)]
        _ = subprocess.run(
            packgen_args,
            cwd=subdir,
            check=True,
        )
        prefix = "packing"
        stl_path = subdir / f"{prefix}_{basename}.stl"

        # there's a bug in packgen that saves the blender file as "*.blender"
        # instead of "*.blend, so we rename it here
        if (subdir / f"{prefix}_{basename}.blender").exists():
            (subdir / f"{prefix}_{basename}.blender").rename(
                subdir / f"{prefix}_{basename}.blend"
            )
        blender_path = subdir / f"{prefix}_{basename}.blend"
        packgen_json_path = subdir / f"{prefix}_{basename}.json"
        return stl_path, blender_path, packgen_json_path

    def _run_stl_extractor(self, stl_path: Path) -> ExtractedPacking:
        stl_json_output = stl_path.parent / f"{stl_path.stem}_extracted.json"
        args = [
            "matlab",
            "-batch",
            f'STLextractToJSON("{stl_path}","{str(stl_json_output)}")',
        ]
        _ = subprocess.run(
            args,
            cwd=stl_path.parent,
            check=True,
        )
        # Load the extracted packing data from the JSON file.
        with open(stl_json_output) as f:
            data = json.load(f)

        return ExtractedPacking.from_dict(data)


# This is a placeholder for the actual packgen command.
def main() -> None:
    print("Hello from packsim!")
