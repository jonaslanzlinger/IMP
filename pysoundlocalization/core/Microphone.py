from typing import Optional

from core.Audio import Audio


class Microphone:

    def __init__(self, x, y):
        self.x = x
        self.y = y

        # TODO: move towards generic SoundInput?
        self.audio: Optional[Audio] = None

    def get_position(self):
        return self.x, self.y

    def add_audio(self, audio):
        """
        Store the audio in the microphone.

        :param audio: The reference to the audio object
        """
        self.audio = audio

    def get_audio(self) -> Optional[Audio]:
        """
        Returns the audio associated with this microphone.

        Returns:
            Audio:  The Audio object currently referenced by this microphone,
                    containing the audio signal data and any relevant processing
                    applied to the signal.

        Note:
            The returned object is a reference to the original Audio instance.
            Any modifications made to this Audio object will affect the data
            stored in all other references to the same audio.
        """
        return self.audio
