from .Room import Room


class Simulation:
    sound_speed = 343.2  # Default speed of sound in m/s

    def __init__(self, sound_speed):
        self.sound_speed = sound_speed
        self.rooms = []

    @classmethod
    def create(cls, sound_speed=343.2):
        return cls(sound_speed)

    def add_room(self, name, vertices):
        room = Room(name, vertices)
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

    def get_sound_speed(self):
        return self.sound_speed

    def set_sound_speed(self, speed):
        self.sound_speed = speed

    """
    def addAudio(audio1) (which requires Audio.add(path, Room.mic1) prior)
    
    def getTdoa(gcc_phat,mic1, mic2) -> to be done for all mic pairs?
    
    def getAllTdoas(gcc_phat, room1)
    
    def getDoa(...)
    
    def localizeSound(algo=..., mics=all_mics_I_want_to_use_for_localization)
     -> uses all microphones and the sounds added to each microphone
     -> multilateration algorithm?
    
    """

    # TODO: add visualization class (not just visualizing room and mics, but also spectogram of audio, etc)
