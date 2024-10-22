from core.Audio import Audio


class Microphone:

    def __init__(self, x, y):
        self.x = x
        self.y = y

        # TODO: move towards generic SoundInput and not "recorded audio"
        self.audio = None
        self.recorded_audio = None

    def get_position(self):
        return self.x, self.y

    def add_audio(self, audio: Audio):
        self.audio = audio

    def get_audio(self):
        return self.audio

    def add_recorded_audio(self, audio_signal):
        """
        Store the recorded audio signal in the microphone.
        :param audio_signal: The audio signal from the Audio class.
        """
        self.recorded_audio = audio_signal

    def get_recorded_audio(self):
        """
        Return the stored audio signal.
        Raises an error if no recorded audio has been added yet.
        """
        if self.recorded_audio is None:
            raise ValueError("No recorded audio has been added for this microphone.")
        return self.recorded_audio
