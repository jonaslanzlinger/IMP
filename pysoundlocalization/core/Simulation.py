import pysoundlocalization.config as config
from pysoundlocalization.core.Environment import Environment


class Simulation:
    def __init__(self):
        """
        Initialize the Simulation with an empty list of environments.
        """
        print("Simulation created.")
        self.__environments: list[Environment] = []

    @classmethod
    def create(cls) -> "Simulation":
        """
        Class method to create an instance of Simulation.

        Returns:
            Simulation: A new instance of the Simulation class.
        """
        return cls()

    def add_environment(
        self,
        name: str,
        vertices: list[tuple[float, float]],
        sound_speed: float = config.DEFAULT_SOUND_SPEED,
    ) -> Environment:
        """
        Add a new environment to the simulation.

        Args:
            name (str): The name of the environment.
            vertices (list[tuple[float, float]]): List of (x, y) coordinates defining the environment's shape in the format ((x1,y1), (xi,yi)).
            sound_speed (float): Optional speed of sound within the environment. Defaults to config.DEFAULT_SOUND_SPEED.

        Returns:
            Environment: The newly created Environment instance.
        """
        environment = Environment(name=name, vertices=vertices, sound_speed=sound_speed)
        self.__environments.append(environment)
        print(f"Environment '{name}' added with vertices {vertices}")
        return environment

    def print_all_environments_to_console(self) -> None:
        """
        Print a list of all environments in the simulation with their names and vertices.
        """
        if not self.__environments:
            print("No environments available in the simulation.")
        else:
            print(f"List of Environments ({len(self.__environments)}):")
            for environment in self.__environments:
                print(
                    f"Environment: {environment.get_name()}, Vertices: {environment.__vertices}"
                )

    def get_environments(self) -> list[Environment]:
        """
        Get a list of all environments in the simulation.

        Returns:
            list[Environment]: List of Environment instances.
        """
        return self.__environments

    def set_environments(self, environments: list[Environment]) -> None:
        """
        Set the list of environments in the simulation.

        Args:
            environments (list[Environment]): List of Environment instances.
        """
        self.__environments = environments
