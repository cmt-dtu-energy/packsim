"""Module for simulating packing of particles."""

from pathlib import Path


class Particle:
    """A single particle in the packing."""

    def __init__(self, radius: float, thickness: float, density: float):
        """Initialize a particle with given properties..

        Args:
            radius (float): Radius of the particle in meters.
            thickness (float): Thickness of the particle in meters.
            density (float): Density of the particle in kg/m3.
        """
        self.radius: float = radius
        self.thickness: float = thickness
        self.density: float = density


class PackingResults:
    """Results of a packing simulation."""

    def __init__(self, stl_path: Path, blender_path: Path):
        """Initialize results from a packing simulation."""
        self.stl_path: Path = stl_path
        self.blender_path: Path = blender_path


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
            mass_fraction_B (float): Mass fraction of particle B in the packing.
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

    def run(self, cutoff: float, cutoff_direction: str) -> PackingResults:
        """Run the packing simulation.

        Args:
            cutoff (float): Cutoff distance for the simulation.
            cutoff_direction (str): Direction of the cutoff, e.g., 'x', 'y', or 'z'.
        """
        stl_path = self.workdir / "packing.stl"
        blender_path = self.workdir / "packing.blend"
        return PackingResults(stl_path=stl_path, blender_path=blender_path)


def main() -> None:
    print("Hello from packsim!")
