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
