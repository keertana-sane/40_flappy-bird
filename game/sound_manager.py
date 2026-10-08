import math
from array import array
import pygame


class SoundManager:
    """Small procedural sound-effect manager for the game."""

    SAMPLE_RATE = 44100

    def __init__(self):
        self.enabled = False
        self.flap_sound = None
        self.point_sound = None
        self.die_sound = None

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()

            self.flap_sound = self._create_tone(
                start_frequency=500,
                end_frequency=800,
                duration=0.08,
                volume=0.35,
            )

            self.point_sound = self._create_tone(
                start_frequency=700,
                end_frequency=1100,
                duration=0.12,
                volume=0.35,
            )

            self.die_sound = self._create_tone(
                start_frequency=300,
                end_frequency=100,
                duration=0.25,
                volume=0.40,
            )

            self.enabled = True

        except (pygame.error, ValueError, TypeError):
            # If audio cannot be initialized, the game still works normally.
            self.enabled = False

    def _create_tone(
        self,
        start_frequency,
        end_frequency,
        duration,
        volume,
    ):
        """Generate a short sine-wave tone."""

        sample_count = int(self.SAMPLE_RATE * duration)
        samples = array("h")

        amplitude = int(32767 * volume)

        for i in range(sample_count):
            progress = i / max(sample_count - 1, 1)

            frequency = (
                start_frequency
                + (end_frequency - start_frequency) * progress
            )

            phase = 2.0 * math.pi * frequency * (i / self.SAMPLE_RATE)

            value = int(amplitude * math.sin(phase))
            samples.append(value)

        return pygame.mixer.Sound(buffer=samples.tobytes())

    def play_flap(self):
        """Play the flap sound."""
        if self.enabled and self.flap_sound is not None:
            self.flap_sound.play()

    def play_point(self):
        """Play the scoring sound."""
        if self.enabled and self.point_sound is not None:
            self.point_sound.play()

    def play_die(self):
        """Play the death sound."""
        if self.enabled and self.die_sound is not None:
            self.die_sound.play()