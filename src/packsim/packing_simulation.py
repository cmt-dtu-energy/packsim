import json
import math
import subprocess
from pathlib import Path

from .extracted_packing import ExtractedPacking
from .packing_results import PackingResults
from .particle import Particle


class SimulationError:
    """Represents an error that occurred during simulation."""

    def __init__(self, simulation_index: int, error_message: str, error_type: str):
        self.simulation_index = simulation_index
        self.error_message = error_message
        self.error_type = error_type

    def __repr__(self):
        return f"SimulationError(index={self.simulation_index}, type={self.error_type}, message='{self.error_message}')"


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

    def run(
        self, cutoff: float, cutoff_direction: str, i: int = 1
    ) -> "PackingResults | SimulationError":
        """Run the packing simulation.

        Args:
            cutoff (float): Cutoff distance for the simulation.
            cutoff_direction (str): Direction of the cutoff, e.g.,
                'x', 'y', or 'z'.
            i (int, optional): Simulation index for parallel runs. Defaults to 1.

        Returns:
            PackingResults or SimulationError: Results of the simulation or error information.
        """
        try:
            stl_path, blender_path, packgen_json_path = self._run_packgen(i=i)
            extracted_packing = self._run_stl_extractor(
                stl_path, cutoff=cutoff, cutoff_direction=cutoff_direction
            )
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
        except subprocess.CalledProcessError as e:
            return SimulationError(
                simulation_index=i,
                error_message=f"Subprocess failed with return code {e.returncode}: {e.cmd}",
                error_type="SubprocessError",
            )
        except FileNotFoundError as e:
            return SimulationError(
                simulation_index=i,
                error_message=f"Required file or executable not found: {e}",
                error_type="FileNotFoundError",
            )
        except json.JSONDecodeError as e:
            return SimulationError(
                simulation_index=i,
                error_message=f"Failed to parse JSON output: {e}",
                error_type="JSONDecodeError",
            )
        except Exception as e:
            return SimulationError(
                simulation_index=i,
                error_message=f"Unexpected error: {e}",
                error_type="UnexpectedError",
            )

    def run_parallel(
        self, cutoff: float, cutoff_direction: str, n: int
    ) -> tuple[list["PackingResults"], list["SimulationError"]]:
        """Run the packing simulation n times in parallel.

        Args:
            cutoff (float): Cutoff distance for the simulation.
            cutoff_direction (str): Direction of the cutoff, e.g., 'x', 'y', or 'z'.
            n (int): Number of parallel simulations to run.

        Returns:
            tuple[list[PackingResults], list[SimulationError]]: Successful results and errors.
        """
        import concurrent.futures

        successful_results = []
        errors = []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self.run, cutoff, cutoff_direction, i) for i in range(n)
            ]
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    if isinstance(result, SimulationError):
                        errors.append(result)
                        print(
                            f"Simulation {result.simulation_index} failed: {result.error_message}"
                        )
                    else:
                        successful_results.append(result)
                except Exception as e:
                    # This catches any additional errors that might occur in the future itself
                    errors.append(
                        SimulationError(
                            simulation_index=-1,  # Unknown index since future failed
                            error_message=f"Future execution failed: {e}",
                            error_type="FutureExecutionError",
                        )
                    )

        # Sort successful results by simulation index (extracted from workdir name)
        successful_results.sort(
            key=lambda r: int(r.workdir.name.split("_")[-1])
            if r.workdir.name.startswith("simulation_")
            else 0
        )
        return successful_results, errors

    def _run_packgen(self, i: int = 1) -> tuple[Path, Path, Path]:
        """Run the packgen tool to generate the packing.

        Args:
            i (int, optional): Simulation index for parallel runs. Defaults to 1.

        Raises:
            subprocess.CalledProcessError: If packgen command fails.
            FileNotFoundError: If packgen executable is not found.
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

        try:
            with open(config_path, "w") as f:
                json.dump(config, f, indent=4)
        except (OSError, IOError) as e:
            raise RuntimeError(f"Failed to write configuration file {config_path}: {e}")

        packgen_args = ["packgen", "--", str(config_path)]
        try:
            subprocess.run(
                packgen_args,
                cwd=subdir,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        except subprocess.CalledProcessError as e:
            error_msg = f"packgen failed with return code {e.returncode}"
            if e.stderr:
                error_msg += f". stderr: {e.stderr.strip()}"
            if e.stdout:
                error_msg += f". stdout: {e.stdout.strip()}"
            raise subprocess.CalledProcessError(e.returncode, e.cmd, error_msg)
        except FileNotFoundError:
            raise FileNotFoundError(
                "packgen executable not found. Please ensure it's installed and in PATH."
            )

        prefix = "packing"
        stl_path = subdir / f"{prefix}_{basename}.stl"

        # Check if expected output files exist
        if not stl_path.exists():
            raise RuntimeError(
                f"Expected STL output file {stl_path} was not created by packgen"
            )

        if (subdir / f"{prefix}_{basename}.blender").exists():
            (subdir / f"{prefix}_{basename}.blender").rename(
                subdir / f"{prefix}_{basename}.blend"
            )
        blender_path = subdir / f"{prefix}_{basename}.blend"
        packgen_json_path = subdir / f"{prefix}_{basename}.json"
        return stl_path, blender_path, packgen_json_path

    def _run_stl_extractor(
        self, stl_path: Path, cutoff: float, cutoff_direction: str
    ) -> ExtractedPacking:
        """Run the STL extractor to process the generated STL file.

        Args:
            stl_path: Path to the STL file to process.
            cutoff: Cutoff distance for the extraction.
            cutoff_direction: Direction of the cutoff.

        Returns:
            ExtractedPacking: The extracted packing data.

        Raises:
            subprocess.CalledProcessError: If matlab command fails.
            FileNotFoundError: If matlab executable is not found.
            json.JSONDecodeError: If the output JSON is invalid.
        """
        stl_json_output = stl_path.parent / f"{stl_path.stem}_extracted.json"
        args = [
            "matlab",
            "-batch",
            f'STLextractToJSON("{stl_path}","{str(stl_json_output)}", "RemoveOutlierRangez",true,"OutlierZThreshold",0,"Cutoff",{cutoff}, "CutoffDirection","{cutoff_direction}","BoundingBoxLength",{self.L})',
        ]

        try:
            subprocess.run(
                args,
                cwd=stl_path.parent,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        except subprocess.CalledProcessError as e:
            error_msg = f"matlab STL extraction failed with return code {e.returncode}"
            if e.stderr:
                error_msg += f". stderr: {e.stderr.strip()}"
            if e.stdout:
                error_msg += f". stdout: {e.stdout.strip()}"
            raise subprocess.CalledProcessError(e.returncode, e.cmd, error_msg)
        except FileNotFoundError:
            raise FileNotFoundError(
                "matlab executable not found. Please ensure MATLAB is installed and in PATH."
            )

        # Check if output file was created
        if not stl_json_output.exists():
            raise RuntimeError(
                f"Expected JSON output file {stl_json_output} was not created by matlab"
            )

        try:
            with open(stl_json_output) as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Failed to parse JSON output from {stl_json_output}: {e}", e.doc, e.pos
            )
        except (OSError, IOError) as e:
            raise RuntimeError(
                f"Failed to read JSON output file {stl_json_output}: {e}"
            )

        self._post_process_data_from_stl_extractor(data)
        return ExtractedPacking.from_dict(data)

    def _post_process_data_from_stl_extractor(self, data: dict) -> None:
        """Post-process the data extracted from the STL file."""

        data["particleA"] = {
            "radius": self.particleA.radius,
            "thickness": self.particleA.thickness,
            "density": self.particleA.density,
        }
        if self.particleB:
            data["particleB"] = {
                "radius": self.particleB.radius,
                "thickness": self.particleB.thickness,
                "density": self.particleB.density,
            }
        else:
            data["particleB"] = None
        for prism in data.get("items", []):
            if math.isclose(
                prism["radius"], self.particleA.radius, rel_tol=1e-3, abs_tol=1e-4
            ) and math.isclose(
                prism["thickness"], self.particleA.thickness, rel_tol=1e-3, abs_tol=1e-4
            ):
                prism["density"] = prism.get("density", self.particleA.density)
            elif (
                self.particleB
                and math.isclose(
                    prism["radius"], self.particleB.radius, rel_tol=1e-3, abs_tol=1e-4
                )
                and math.isclose(
                    prism["thickness"],
                    self.particleB.thickness,
                    rel_tol=1e-3,
                    abs_tol=1e-4,
                )
            ):
                prism["density"] = prism.get("density", self.particleB.density)
            else:
                raise ValueError(
                    "Prism does not match either particle A or B. "
                    f"Prism: {prism}, Particle A: {self.particleA}, Particle B: {self.particleB}"
                )
