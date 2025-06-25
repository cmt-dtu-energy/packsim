from numpy.typing import ArrayLike


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
        self.volume: float = 3 / 2 * (3**0.5) * self.radius**2 * self.thickness
