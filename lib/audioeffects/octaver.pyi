# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT
from typing import Any

from . import _component
from ._component import _AudioSource, _Transport

VENDOR: str
DIRECT_I: int
OCTAVE1_I: int
OCTAVE2_I: int
TRACKING_I: int
TONE1_I: int
TONE2_I: int
SENS_I: int
DEFAULTS: tuple[float, ...]
CURVE_POINTS: int
DEAD_HALF: int
TICK_HALF: int
TICK: int
EDGE: float
CLOCK_Q: float
TONE_Q: float
MEAN_HZ: float
MEAN_POLES: int
CLOCK_THRESHOLD: float
CLOCK_HOLD_MS: float
GATE_HALF: int
BLOCK: int

def comparator_curve() -> Any:
    """The comparator's table, built once and shared by every instance."""

def gate_curve() -> Any:
    """The table after each divider, built once and shared."""

def pre_gain(sensitivity_db: float) -> float:
    """The comparator's input gain for a Sensitivity in dBFS."""

class Octaver(_component.Component):
    """An octave down that is your own note: like the Boss OC-2, it turns
    every other cycle of what you play upside down, so the octave keeps
    your attack, your decay and your tone.

    **The controls.** Direct is your own note's level, and the Octave knobs
    set the octaves'. Tracking moves the range of notes the divider
    follows. Tone 1 and Tone 2 are two-pole low-passes at the hertz they
    show, on the first and second octave. Sensitivity is the level your
    note must keep after Tracking's low-pass for the octaves to play, not
    the level you play at. The higher the note, the more that low-pass
    takes, so a quiet high note stops before a quiet low one: at patch 0 a
    sine at -60 dBFS still has its octave on E2 and none on E4. Constructor
    values land on the nearest of each knob's 128 steps. The Effect
    controls page lists what the knobs span.

    **What you hear.** The octave is exactly half your note and sounds
    within 2 ms of it.
    Octave 2 is Octave 1 divided again: two octaves down, not a fourth
    below the note, until Octave 1 itself stops.
    On an A2 the octave follows your note's decay within 1 dB: it has no
    envelope of its own.
    Below Sensitivity the octaves are silent, with no ghost and no hum,
    and as a note fades into it the octave never turns into the note
    itself.
    With the Tones open the octave carries a fifth above it 4.4 dB
    quieter, as the pedal's multiplication does, wherever Tracking is set.
    Turning Tone 1 down thins that fifth more on high notes than on low
    ones.

    **Its range.** Played at -8.7 dBFS peak, every note at patch 0 from
    low E (E2) to A4 divides cleanly, even with a strong second harmonic.
    Played at -8.7 dBFS peak, the Bass patch covers E1 to G3, and High on
    the neck covers D3 to E5; played quieter, each range ends lower.
    Below the range a low note's second harmonic clocks the divider and it
    skips; above it the clock is low-passed under Sensitivity and the
    octave goes silent.
    Between -90 and -84.5 dBFS Sensitivity changes nothing: that whole
    stretch is one step of the clock.
    A direct offset in the input, as a plucked string rings round, does not
    take the top of the range from you: the divider turns over on the
    clock's own centre, not on zero.

    **Limits.** It plays one note at a time: on a power chord (A2 and E3)
    about two fifths of the octave is intermodulation.
    A stereo source is clocked on its mid: with the right channel 45
    degrees ahead of the left, the fifth sits 3.2 dB under the octave
    instead of 4.4, on both channels.
    The output can peak at about 5 times the input (a low square, all
    three levels at full with the Tones open), so keep the input under
    -15 dBFS.
    A control that jumps makes the output step: move it in small steps
    from the host if you need it smooth.

    **On an ESP32-S3, Both octaves can't keep up and the sound breaks up;
    play Both octaves - lean instead.** It has the same balance of your
    note and the two octaves, 2 dB louder: turn the level after it down
    2 dB and you hear Both octaves.

    **Wire, latency, tail.** With both octaves at 0 and Direct at 1 the
    output is the input, byte for byte, however the host's buffers are
    cut.
    There is no latency.
    `tail_samples` covers the all-pass and the two Tone filters ringing
    down.
    `reset()` clears the filters and the dividers and returns to patch 0.
    The class never reads the host's tempo.
    """

    NAME: str
    DISPLAY_NAME: str
    CATEGORIES: tuple[str, ...]
    VERSION: str
    TIER: str
    REQUIRES: tuple[str, ...]
    CAPABILITIES: tuple[str, ...]
    LATENCY_SAMPLES: int
    TAIL_SAMPLES: int | None
    INPUT_CEILING_DBFS: float
    MACRO_LABELS: tuple[str, ...]
    MACRO_MODES: dict[int, str]
    PATCHES: dict[int, tuple[str, tuple[float, ...]]]

    def __init__(
        self,
        source: _AudioSource,
        direct: float = 1.0,
        octave1: float = 0.7,
        octave2: float = 0.0,
        tracking_hz: float = 90.0,
        tone1_hz: float = 324.0,
        tone2_hz: float = 70.3,
        sensitivity_db: float = -80.0,
        patch: int | None = None,
        *,
        sample_rate: int | None = None,
        transport: _Transport | None = None,
    ) -> None: ...
    @property
    def tail_samples(self) -> int | None:
        """The all-pass and both Tone filters ringing down, end to end."""
