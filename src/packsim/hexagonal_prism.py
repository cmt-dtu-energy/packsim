from numpy.typing import ArrayLike


class Triangulation:
    """Triangulation data for a 3D object.

    This is a port of the MATLAB triangulation object.
    It contains the vertices and faces of the triangulated object.
    """

    def __init__(self, points: ArrayLike, connectivity_list: ArrayLike):
        """Initialize the triangulation with points and connectivity list.

        Args:
            points (ArrayLike): Vertices of the triangulated object, shape (N, 3),
                where N is the number of vertices. Each row represents a vertex
                in 3D space (x, y, z).
            connectivity_list (ArrayLike): Matrix of indices that define the
                connectivity of the vertices. Each row contains indices of the vertices that form a triangle, extracted from `points`.
                E.g. [[0, 1, 2], [2, 3, 0]] means the first triangle is formed by
                    vertices defined by rows 0, 1, and 2 of `points`, and the second triangle is formed by
                    vertices defined by rows 2, 3, and 0 of `points`.
        """
        self.points: ArrayLike = points
        self.connectivity_list: ArrayLike = connectivity_list

    @classmethod
    def from_dict(cls, data: dict[str, ArrayLike]) -> "Triangulation":
        """Create a Triangulation instance from a dictionary.

        Args:
            data (dict[str, ArrayLike]): Dictionary containing 'Points' and 'ConnectivityList'.

        Returns:
            Triangulation: An instance of the Triangulation class.
        """
        return cls(
            points=data["Points"],
            connectivity_list=data["ConnectivityList"],
        )


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
        density: float,
        triangulation: Triangulation,
    ):
        """Initialize a hexagonal prism particle with given properties.
        Args:
            radius (float): Radius of the hexagonal prism in meters.
            thickness (float): Thickness of the hexagonal prism in meters.
            normal (ArrayLike): Normal vector of the hexagonal prism.
            position (ArrayLike): Position of the hexagonal prism in space.
            face_rotation (ArrayLike): Rotation of the faces of the prism.
            vertices (ArrayLike): Vertices of the hexagonal prism.
            density (float): Density of the hexagonal prism in kg/m^3.
            triangulation (Triangulation): Triangulation of the hexagonal prism.
        """
        self.radius: float = radius
        self.thickness: float = thickness
        self.normal: ArrayLike = normal
        self.position: ArrayLike = position
        self.face_rotation: ArrayLike = face_rotation
        self.vertices: ArrayLike = vertices
        self.volume: float = 3 / 2 * (3**0.5) * self.radius**2 * self.thickness
        self.density: float = density
        self.mass: float = self.volume * self.density
        self.triangulation: Triangulation = triangulation
