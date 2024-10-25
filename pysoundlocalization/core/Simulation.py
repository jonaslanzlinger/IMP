import config
from .Room import Room


class Simulation:
    def __init__(self):
        self.rooms = []

    @classmethod
    def create(cls):
        return cls()

    def add_room(self, name, vertices, sound_speed=config.DEFAULT_SOUND_SPEED):
        room = Room(name, vertices, sound_speed)
        self.rooms.append(room)
        print(f"Room '{name}' added with vertices {vertices}")
        return room

    def get_rooms(self):
        return self.rooms

    def list_rooms(self):
        if not self.rooms:
            print("No rooms available in the simulation.")
        else:
            print(f"List of Rooms ({len(self.rooms)}):")
            for room in self.rooms:
                print(f"Room: {room.name}, Vertices: {room.vertices}")