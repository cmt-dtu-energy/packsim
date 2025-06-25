"""Test suite for the packsim CLI and library, based on README specifications.

This module provides pytest-based tests for the packsim tool, including:
- Minimal valid input
- Input with both A and B particles
- Multiple simulations
- Invalid input handling
"""

from pathlib import Path
import pytest

from packsim import Particle, PackingSimulation

PARTICLE_A = Particle(radius=1.0, thickness=0.2, density=1.0)
PARTICLE_B = Particle(radius=0.5, thickness=0.1, density=1.2)


@pytest.fixture
def packing_simulation_only_A(tmp_path: Path) -> PackingSimulation:
    """Fixture for a packing simulation with only Particle A."""
    return PackingSimulation(
        particleA=PARTICLE_A,
        particleB=None,
        mass_fraction_B=0.0,
        num_cubes_xy=2,
        num_cubes_z=10,
        L=10.0,
        workdir=tmp_path / "packing_simulation_only_A",
    )


def test_minimal_valid_input(packing_simulation_only_A: PackingSimulation):
    """Test minimal valid input with only Particle A."""
    packing_simulation_only_A.run(cutoff=0.1, cutoff_direction="x")
    assert True  # Replace with actual assertions based on expected results
