class Microphone:

    def __init__(self, x, y, z=None):
        self.x = x
        self.y = y
        self.z = z # TODO: z coordinate not supported

        # TODO: how to ensure mic coordinate is inside room? likely only when adding mic to room, so inside room function, right?