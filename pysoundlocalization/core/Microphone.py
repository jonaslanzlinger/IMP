class Microphone:

    def __init__(self, x, y):
        self.x = x
        self.y = y

        # TODO: move towards generic SoundInput and not "recorded audio"
        # TODO: do we want to add an Audio reference instead of just a recorded_audio_signal??
        self.recorded_audio_signal = None

    def get_position(self):
        return self.x, self.y

    def add_recorded_audio(self, audio_signal):
        """
        Store the recorded audio signal in the microphone.
        :param audio_signal: The audio signal from the Audio class.
        """
        self.recorded_audio_signal = audio_signal

    def get_recorded_audio(self):
        """
        Return the stored audio signal.
        """
        return self.recorded_audio_signal
