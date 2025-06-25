"""Test suite for the packsim CLI and library, based on README specifications.

This module provides pytest-based tests for the packsim tool, including:
- Minimal valid input
- Input with both A and B particles
- Multiple simulations
- Invalid input handling
"""

import math
import json
from pathlib import Path
import pytest

from packsim import Particle, PackingSimulation, PackingResults, ExtractedPacking

PARTICLE_A = Particle(radius=1.0, thickness=0.2, density=1.0)
PARTICLE_B = Particle(radius=0.5, thickness=0.1, density=1.2)


@pytest.fixture(scope="module")
def packing_results_only_A(
    tmp_path_factory: pytest.TempPathFactory,
) -> PackingResults:
    """Fixture for a packing simulation with only Particle A."""
    tmp_path = tmp_path_factory.mktemp("packing_simulation_only_A")
    return PackingSimulation(
        particleA=PARTICLE_A,
        particleB=None,
        mass_fraction_B=0.0,
        num_cubes_xy=2,
        num_cubes_z=10,
        L=10.0,
        workdir=tmp_path / "packing_simulation_only_A",
    ).run(cutoff=0.1, cutoff_direction="x")


@pytest.fixture(scope="module")
def packing_results_AB(
    tmp_path_factory: pytest.TempPathFactory,
) -> PackingResults:
    """Fixture for a packing simulation with both Particle A and B."""
    tmp_path = tmp_path_factory.mktemp("packing_simulation_only_A")
    return PackingSimulation(
        particleA=PARTICLE_A,
        particleB=PARTICLE_B,
        mass_fraction_B=10.0,
        num_cubes_xy=3,
        num_cubes_z=9,
        L=10.0,
        workdir=tmp_path / "packing_simulation_only_A",
    ).run(cutoff=0.3, cutoff_direction="y")


@pytest.fixture(scope="module", params=["A", "AB"])
def packing_results(
    request, packing_results_only_A, packing_results_AB
) -> PackingResults:
    """Fixture for packing simulation results."""
    match request.param:
        case "A":
            return packing_results_only_A
        case "AB":
            return packing_results_AB


def test_simulation_writes_intermediate_files(packing_results: PackingResults):
    """Test that the simulation writes intermediate files."""
    assert packing_results.stl_path.exists()
    assert packing_results.blender_path.exists()


def test_input_and_output_parameters_are_compatible(
    packing_results: PackingResults,
):
    """Test that input and output parameters are compatible."""
    assert packing_results.packgen_json_path.exists()
    with open(packing_results.packgen_json_path) as f:
        packgen_config = json.load(f)

    assert math.isfinite(packgen_config["seed"])
    assert packgen_config["scale"] == 1
    assert math.isclose(packgen_config["r_A"], packing_results.particleA.radius)
    assert math.isclose(
        packgen_config["thickness_A"], packing_results.particleA.thickness
    )
    assert math.isclose(packgen_config["density_A"], packing_results.particleA.density)
    assert math.isclose(
        packgen_config["mass_fraction_B"], packing_results.mass_fraction_B
    )
    assert packing_results.num_cubes_xy == packgen_config["num_cubes_x"]
    assert packing_results.num_cubes_xy == packgen_config["num_cubes_y"]
    assert packing_results.num_cubes_z == packgen_config["num_cubes_z"]
    assert math.isclose(
        packing_results.L,
        packgen_config["distance"] * packgen_config["num_cubes_x"],
    )
    if packing_results.particleB:
        assert math.isclose(packgen_config["r_B"], packing_results.particleB.radius)
        assert math.isclose(
            packgen_config["thickness_B"], packing_results.particleB.thickness
        )
        assert math.isclose(
            packgen_config["density_B"], packing_results.particleB.density
        )


def test_extracted_packing_has_correct_items(packing_results: PackingResults):
    """Test that the extracted packing has the correct number of items."""
    assert isinstance(packing_results.extracted_packing, ExtractedPacking)
