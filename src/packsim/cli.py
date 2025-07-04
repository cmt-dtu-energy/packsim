import json
import sys
from pathlib import Path
from typing import Annotated, Optional

import typer

from .packing_simulation import PackingSimulation, SimulationError
from .particle import Particle

app = typer.Typer(help="packsim: Simulate the process of packing particles in a box.")


def parse_particle(data: dict) -> Particle:
    return Particle(
        radius=data["radius"],
        thickness=data.get("thickness", 1.0),
        density=data["density"],
    )


class PackSimJSONEncoder(json.JSONEncoder):
    def default(self, o):
        # Handle Particle and other custom classes
        if hasattr(o, "to_dict"):
            return o.to_dict()
        if isinstance(o, SimulationError):
            return {
                "simulation_index": o.simulation_index,
                "error_message": o.error_message,
                "error_type": o.error_type,
            }
        if hasattr(o, "__dict__"):
            return o.__dict__
        if isinstance(o, Path):
            return str(o)
        return super().default(o)


@app.command()
def main(
    input_file: Annotated[
        Optional[Path],
        typer.Argument(
            help="Input JSON file. If omitted, reads from stdin.",
            exists=False,
            file_okay=True,
            dir_okay=False,
            readable=True,
        ),
    ] = None,
    o: Annotated[
        Optional[Path],
        typer.Option(
            "-o",
            "--output",
            help="Output file. If omitted, writes to stdout.",
            exists=False,
            file_okay=True,
            dir_okay=False,
            writable=True,
        ),
    ] = None,
):
    """
    Run a packing simulation from a JSON input file or stdin.
    """
    # Print help if no input and stdin is empty
    if input_file is None and sys.stdin.isatty():
        typer.echo("No input file provided and no data in stdin. Use --help for usage.")
        raise typer.Exit(code=1)

    # Read input JSON
    if input_file is not None:
        with open(input_file) as f:
            config = json.load(f)
    else:
        try:
            config = json.load(sys.stdin)
        except json.JSONDecodeError:
            typer.echo("No input provided. Use --help for usage.")
            raise typer.Exit(code=1)

    # Parse particles
    particleA = parse_particle(config["particle_A"])
    particleB = None
    if "particle_B" in config and config["particle_B"] is not None:
        particleB = parse_particle(config["particle_B"])

    # Required arguments for PackingSimulation
    mass_fraction_B = config.get("mass_fraction_B", 0.0)
    num_cubes_xy = config["num_cubes_xy"]
    num_cubes_z = config["num_cubes_z"]
    L = config["L"]

    # resolve workdir relative to the path of the input file
    basedir = input_file.parent if input_file else Path.cwd()
    workdir = (basedir / Path(config["work_dir"])).resolve()

    # Arguments for run/run_parallel
    cutoff = config.get("cutoff", 0.1)
    cutoff_direction = config.get("cutoff_direction", "x")
    n = config.get("n", 1)

    sim = PackingSimulation(
        particleA=particleA,
        particleB=particleB,
        mass_fraction_B=mass_fraction_B,
        num_cubes_xy=num_cubes_xy,
        num_cubes_z=num_cubes_z,
        L=L,
        workdir=workdir,
    )

    if n == 1:
        result = sim.run(cutoff, cutoff_direction)
        if isinstance(result, SimulationError):
            typer.echo(f"Simulation failed: {result.error_message}", err=True)
            raise typer.Exit(code=1)
        results = [result]
        errors: list[SimulationError] = []
    else:
        results, errors = sim.run_parallel(cutoff, cutoff_direction, n)

        # Report any errors to stderr
        if errors:
            typer.echo(
                f"Warning: {len(errors)} out of {n} simulations failed:", err=True
            )
            for error in errors:
                typer.echo(
                    f"  Simulation {error.simulation_index}: {error.error_message}",
                    err=True,
                )

        if not results:
            typer.echo("Error: All simulations failed.", err=True)
            raise typer.Exit(code=1)

    # Prepare output with both results and error summary
    output_data = {
        "successful_results": results,
        "total_requested": n,
        "successful_count": len(results),
        "failed_count": len(errors),
    }

    if errors:
        output_data["errors"] = errors

    output_json = json.dumps(output_data, indent=2, cls=PackSimJSONEncoder)

    if o is not None:
        with open(o, "w") as f:
            f.write(output_json)
    else:
        typer.echo(output_json)


if __name__ == "__main__":
    app()
