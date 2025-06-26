import json
import subprocess
from pathlib import Path

from .extracted_packing import ExtractedPacking
from .packing_results import PackingResults
from .particle import Particle


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

    def run(self, cutoff: float, cutoff_direction: str, i: int = 1) -> PackingResults:
        """Run the packing simulation.

        Args:
            cutoff (float): Cutoff distance for the simulation.
            cutoff_direction (str): Direction of the cutoff, e.g.,
                'x', 'y', or 'z'.
            i (int, optional): Simulation index for parallel runs. Defaults to 1.
        """
        stl_path, blender_path, packgen_json_path = self._run_packgen(i=i)
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

    def run_parallel(
        self, cutoff: float, cutoff_direction: str, n: int
    ) -> list["PackingResults"]:
        """Run the packing simulation n times in parallel.

        Args:
            cutoff (float): Cutoff distance for the simulation.
            cutoff_direction (str): Direction of the cutoff, e.g., 'x', 'y', or 'z'.
            n (int): Number of parallel simulations to run.

        Returns:
            list[PackingResults]: List of PackingResults for each simulation.
        """
        import concurrent.futures

        results = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self.run, cutoff, cutoff_direction, i) for i in range(n)
            ]
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())
        # Sort results by simulation index to preserve order
        results.sort(key=lambda r: r.workdir)
        return results

    def _run_packgen(self, i: int = 1) -> tuple[Path, Path, Path]:
        """Run the packgen tool to generate the packing.

        Args:
            i (int, optional): Simulation index for parallel runs. Defaults to 1.
        """
        config = {
            "seed": None,
            "scale": 1,
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
        subdir = self.workdir / f"simulation_{i}"
        subdir.mkdir(parents=True, exist_ok=True)
        basename = "parameters"
        config_path = subdir / f"{basename}.json"
        with open(config_path, "w") as f:
            json.dump(config, f, indent=4)
        packgen_args = ["packgen", "--", str(config_path)]
        _ = subprocess.run(
            packgen_args,
            cwd=subdir,
            check=True,
        )
        prefix = "packing"
        stl_path = subdir / f"{prefix}_{basename}.stl"
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
        with open(stl_json_output) as f:
            data = json.load(f)
        return ExtractedPacking.from_dict(data)
