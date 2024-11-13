import pysoundlocalization.config as config
from pysoundlocalization.core.Room import Room


class Simulation:
    def __init__(self):
        """
        Initialize the Simulation with an empty list of rooms.
        """
        self.__rooms: list[Room] = []

    @classmethod
    def create(cls) -> "Simulation":
        """
        Class method to create an instance of Simulation.

        Returns:
            Simulation: A new instance of the Simulation class.
        """
        return cls()

    def add_room(
        self,
        name: str,
        vertices: list[tuple[float, float]],
        sound_speed: float = config.DEFAULT_SOUND_SPEED,
    ) -> Room:
        """
        Add a new room to the simulation.

        Args:
            name (str): The name of the room.
            vertices (list[tuple[float, float]]): List of (x, y) coordinates defining the room's shape in the format ((x1,y1), (xi,yi)).
            sound_speed (float): Optional speed of sound within the room. Defaults to config.DEFAULT_SOUND_SPEED.

        Returns:
            Room: The newly created Room instance.
        """
        room = Room(name, vertices, sound_speed)
        self.__rooms.append(room)
        print(f"Room '{name}' added with vertices {vertices}")
        return room

    def print_all_rooms_to_console(self) -> None:
        """
        Print a list of all rooms in the simulation with their names and vertices.
        """
        if not self.__rooms:
            print("No rooms available in the simulation.")
        else:
            print(f"List of Rooms ({len(self.__rooms)}):")
            for room in self.__rooms:
                print(f"Room: {room.get_name()}, Vertices: {room.vertices}")

    def get_rooms(self) -> list[Room]:
        """
        Get a list of all rooms in the simulation.

        Returns:
            list[Room]: List of Room instances.
        """
        return self.__rooms

    def set_rooms(self, rooms: list[Room]) -> None:
        """
        Set the list of rooms in the simulation.

        Args:
            rooms (list[Room]): List of Room instances.
        """
        self.__rooms = rooms
