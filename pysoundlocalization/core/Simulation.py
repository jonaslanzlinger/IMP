class Simulation:
    sound_speed = 343.2  # Speed of sound in m/s

    def __init__(self, sound_speed):
        self.sound_speed = sound_speed

    # TODO: add properties to simulation
    @classmethod
    def create(cls, sound_speed):
        return cls(sound_speed)

    """
    def addRoom(self)
    -> then add mics to room
    
    def addAudio(audio1) (which requires Audio.add(path, Room.mic1) prior)
    
    def getTdoa(gcc_phat,mic1, mic2) -> to be done for all mic pairs?
    
    def getAllTdoas(gcc_phat, room1)
    
    def getDoa(...)
    
    def localizeSound(algo=..., mics=all_mics_I_want_to_use_for_localization)
     -> uses all microphones and the sounds added to each microphone
     -> multilateration algorithm?
    
    """

    # TODO: add visualization class (not just visualizing room and mics, but also spectogram of audio, etc)

