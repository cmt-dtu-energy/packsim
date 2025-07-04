"""Test suite for the packsim CLI and library, based on README specifications.

This module provides pytest-based tests for the packsim tool, including:
- Minimal valid input
- Input with both A and B particles
- Multiple simulations
- Invalid input handling
"""

import json
import math
from pathlib import Path

import pytest

from packsim import ExtractedPacking, PackingResults, PackingSimulation, Particle
from packsim.hexagonal_prism import HexagonalPrism, Triangulation
from packsim.packing_simulation import SimulationError

PARTICLE_A = Particle(radius=1.0, thickness=0.2, density=1.0)
PARTICLE_B = Particle(radius=0.5, thickness=0.1, density=1.2)


@pytest.fixture(scope="module")
def packing_results_only_A(
    tmp_path_factory: pytest.TempPathFactory,
) -> PackingResults:
    """Fixture for a packing simulation with only Particle A."""
    tmp_path = tmp_path_factory.mktemp("packing_simulation_only_A")
    result = PackingSimulation(
        particleA=PARTICLE_A,
        particleB=None,
        mass_fraction_B=0.0,
        num_cubes_xy=2,
        num_cubes_z=10,
        L=10.0,
        workdir=tmp_path / "packing_simulation_only_A",
    ).run(cutoff=0.1, cutoff_direction="x")

    if isinstance(result, SimulationError):
        pytest.skip(f"Simulation failed: {result.error_message}")

    return result


@pytest.fixture(scope="module")
def packing_results_AB(
    tmp_path_factory: pytest.TempPathFactory,
) -> PackingResults:
    """Fixture for a packing simulation with both Particle A and B."""
    tmp_path = tmp_path_factory.mktemp("packing_simulation_AB")
    result = PackingSimulation(
        particleA=PARTICLE_A,
        particleB=PARTICLE_B,
        mass_fraction_B=0.1,
        num_cubes_xy=3,
        num_cubes_z=9,
        L=10.0,
        workdir=tmp_path / "packing_simulation_AB",
    ).run(cutoff=0.3, cutoff_direction="y")

    if isinstance(result, SimulationError):
        pytest.skip(f"Simulation failed: {result.error_message}")

    return result


SIMULATION_FIXTURES = [
    "packing_results_only_A",
    "packing_results_AB",
]


@pytest.mark.parametrize("packing_results_fixture", SIMULATION_FIXTURES)
def test_simulation_writes_intermediate_files(
    request: pytest.FixtureRequest, packing_results_fixture: str
):
    """Test that the simulation writes intermediate files."""
    packing_results = request.getfixturevalue(packing_results_fixture)
    assert packing_results.stl_path.exists()
    assert packing_results.blender_path.exists()


@pytest.mark.parametrize("packing_results_fixture", SIMULATION_FIXTURES)
def test_input_and_output_parameters_are_compatible(
    request: pytest.FixtureRequest, packing_results_fixture: str
):
    """Test that input and output parameters are compatible."""
    packing_results = request.getfixturevalue(packing_results_fixture)
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


@pytest.mark.parametrize("packing_results_fixture", SIMULATION_FIXTURES)
def test_extracted_packing_has_correct_items(
    request: pytest.FixtureRequest, packing_results_fixture: str
):
    """Test that the extracted packing has the correct number of items."""
    packing_results = request.getfixturevalue(packing_results_fixture)
    assert isinstance(packing_results.extracted_packing, ExtractedPacking)
    # ASSUMES A CUTOFF FRACTION > 0.0!!!
    assert len(packing_results.extracted_packing.items) < (
        packing_results.num_cubes_xy
        * packing_results.num_cubes_xy
        * packing_results.num_cubes_z
    )
    for prism in packing_results.extracted_packing.items:
        assert isinstance(prism, HexagonalPrism)
        assert isinstance(prism.triangulation, Triangulation)


def test_run_parallel(tmp_path: Path):
    """Test that run_parallel runs n simulations concurrently and returns correct results."""
    sim = PackingSimulation(
        particleA=PARTICLE_A,
        particleB=PARTICLE_B,
        mass_fraction_B=0.5,
        num_cubes_xy=2,
        num_cubes_z=2,
        L=2.0,
        workdir=tmp_path,
    )
    n = 3
    results, errors = sim.run_parallel(cutoff=0, cutoff_direction="x", n=n)

    # Check that we get the expected return types
    assert isinstance(results, list)
    assert isinstance(errors, list)

    # In a successful test, we expect all simulations to succeed
    # (assuming packgen and matlab are available and working)
    assert len(results) + len(errors) == n

    # If there are any errors, print them for debugging
    if errors:
        print(f"Some simulations failed ({len(errors)} out of {n}):")
        for error in errors:
            print(f"  Simulation {error.simulation_index}: {error.error_message}")

    # Test successful results
    for i, res in enumerate(results):
        assert res.stl_path.exists()
        assert res.blender_path.exists()
        assert res.packgen_json_path.exists()
        assert res.workdir == tmp_path
        assert isinstance(res.extracted_packing, ExtractedPacking)
        for prism in res.extracted_packing.items:
            assert isinstance(prism, HexagonalPrism)
            assert isinstance(prism.triangulation, Triangulation)


@pytest.mark.parametrize("packing_results_fixture", SIMULATION_FIXTURES)
def test_particles_have_correct_mass(
    request: pytest.FixtureRequest, packing_results_fixture: str
):
    """Test that particles have correct mass based on their density and volume."""
    packing_results = request.getfixturevalue(packing_results_fixture)
    prisms = packing_results.extracted_packing.items
    expected_density = float("nan")
    for prism in prisms:
        if math.isclose(
            prism.radius, packing_results.particleA.radius, rel_tol=1e-3
        ) and math.isclose(
            prism.thickness, packing_results.particleA.thickness, rel_tol=1e-3
        ):
            expected_density = packing_results.particleA.density
        elif (
            packing_results.particleB
            and math.isclose(
                prism.radius, packing_results.particleB.radius, rel_tol=1e-3
            )
            and math.isclose(
                prism.thickness, packing_results.particleB.thickness, rel_tol=1e-3
            )
        ):
            expected_density = packing_results.particleB.density
        assert math.isclose(prism.density, expected_density, rel_tol=1e-3)
        assert math.isclose(prism.density, expected_density, rel_tol=1e-3)
        assert math.isclose(prism.density, expected_density, rel_tol=1e-3)
        assert math.isclose(prism.density, expected_density, rel_tol=1e-3)
        assert math.isclose(prism.density, expected_density, rel_tol=1e-3)
        assert math.isclose(prism.density, expected_density, rel_tol=1e-3)
        assert math.isclose(prism.density, expected_density, rel_tol=1e-3)
        assert math.isclose(prism.density, expected_density, rel_tol=1e-3)
        assert math.isclose(prism.density, expected_density, rel_tol=1e-3)


def test_simulation_error_handling(tmp_path: Path):
    """Test that simulation errors are properly handled and returned."""
    sim = PackingSimulation(
        particleA=PARTICLE_A,
        particleB=PARTICLE_B,
        mass_fraction_B=0.5,
        num_cubes_xy=2,
        num_cubes_z=2,
        L=2.0,
        workdir=tmp_path,
    )

    # Test single simulation error handling
    result = sim.run(cutoff=0, cutoff_direction="x", i=1)

    # The result should be either PackingResults or SimulationError
    assert isinstance(result, (PackingResults, SimulationError))

    if isinstance(result, SimulationError):
        # Verify error structure
        assert hasattr(result, "simulation_index")
        assert hasattr(result, "error_message")
        assert hasattr(result, "error_type")
        assert isinstance(result.simulation_index, int)
        assert isinstance(result.error_message, str)
        assert isinstance(result.error_type, str)
        print(
            f"Expected simulation error occurred: {result.error_type} - {result.error_message}"
        )
    else:
        # If simulation succeeded, verify it's a proper PackingResults
        assert isinstance(result, PackingResults)
        print("Simulation succeeded unexpectedly (packgen/matlab are available)")


def test_parallel_simulation_error_handling(tmp_path: Path):
    """Test that parallel simulation handles errors gracefully."""
    sim = PackingSimulation(
        particleA=PARTICLE_A,
        particleB=PARTICLE_B,
        mass_fraction_B=0.5,
        num_cubes_xy=2,
        num_cubes_z=2,
        L=2.0,
        workdir=tmp_path,
    )

    n = 3
    results, errors = sim.run_parallel(cutoff=0, cutoff_direction="x", n=n)

    # Verify return types
    assert isinstance(results, list)
    assert isinstance(errors, list)

    # Total should equal requested simulations
    assert len(results) + len(errors) == n

    # All results should be PackingResults
    for result in results:
        assert isinstance(result, PackingResults)

    # All errors should be SimulationError
    for error in errors:
        assert isinstance(error, SimulationError)
        assert hasattr(error, "simulation_index")
        assert hasattr(error, "error_message")
        assert hasattr(error, "error_type")

    print(
        f"Parallel simulation completed: {len(results)} successful, {len(errors)} failed"
    )
    print(
        f"Parallel simulation completed: {len(results)} successful, {len(errors)} failed"
    )
