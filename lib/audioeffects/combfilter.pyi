# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT
from . import _component
from ._component import _AudioSource, _Transport
from .digitaldelay import laps_to_zero as laps_to_zero

VENDOR: str
MAX_DELAY_MS: float
TONE_OFF_HZ: float
FLAT_DB: float
MIX_UNITY_SNAP: float
TRIM_CORNER_HZ: float
TRIM_Q: float
TRIM_TAIL_S: float

class CombFilter(_component.Component):
    """A tuned comb: a delay line short enough to be a pitch, fed back on
    itself, so noise turns into a note and a chord turns metallic.

    **Frequency.** Frequency is the note the comb rings at, tuned between
    samples. From 55 Hz to 3.52 kHz the first repeat lands within 5 cents
    of the note you asked for, and at 880 Hz it does at 48 kHz, 44.1 kHz
    and 22.05 kHz, and in mono. While it rings, it rings on that pitch, and
    then it stops.

    **Feedback.** Feedback sets how tall the resonances stand: at 200 Hz
    the peak is 1/(1-Feedback) and the null 1/(1+Feedback), within 0.2 dB.
    At Feedback 0 it is the feedforward comb, with nulls more than 60 dB
    down and peaks 6 dB up, within 0.1 dB.

    **Mix.** Mix 0 is a wire, 1 is dry plus comb, and 2 is the comb alone.
    Mix 0 is the source sample for sample, whatever Trim is set to.

    **Tone.** Tone is a low-pass inside the loop, darkening the repeats.
    Its top stop is off, and turning it off after it has been in leaves
    nothing behind.

    **Trim.** Trim sits in front of the comb, so turning it down makes room
    for the resonance before the gain rather than after.

    **Glide.** Glide slides the tuning, so turning Frequency bends the note
    rather than clicking.

    **Level.** A comb gains, so a loud input can reach the rail by design. Keep
    the input under -24 dBFS and the defaults and patches stay off the rails.
    Feedback or Trim at its top can still push the output onto the rails.
    `reset()` empties the line.

    **Latency and tail.** It adds no latency at any setting. The tail
    always reaches exact zero, and `tail_samples` says when, for the
    settings as they stand: 3219 frames at the defaults at 48 kHz.

    **Patches.** Each patch tunes the comb to a different note. The Effect
    controls page lists what the knobs span and the patches.

    It needs `audioecho` and `audiobiquad`, so a stock CircuitPython board
    can't run it.
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
    INPUT_CEILING_DBFS: int
    CLIPS_AT_TOP: tuple[int, ...]
    MACRO_LABELS: tuple[str, ...]
    MACRO_MODES: dict[int, str]
    PATCHES: dict[int, tuple[str, tuple[float, ...]]]

    def __init__(
        self,
        source: _AudioSource,
        frequency: float = 440.0,
        feedback: float = 0.7,
        mix: float = 1.0,
        tone_hz: float = 24000.0,
        trim_db: float = 0.0,
        glide: float = 0.05,
        patch: int | None = None,
        *,
        sample_rate: int | None = None,
        transport: _Transport | None = None,
    ) -> None: ...
    def reset(self) -> None: ...
    @property
    def tail_samples(self) -> int | None:
        """Frames until the output is exactly zero once the input stops, as
        an upper bound for the settings as they stand: `laps_to_zero` laps
        of the longest line the read head may be at, each one frame longer
        for the interpolated read and the Tone low-pass's memory longer,
        plus `TRIM_TAIL_S` while the trim is in circuit. Finite at every
        setting."""
