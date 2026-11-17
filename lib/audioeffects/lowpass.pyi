# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT
from . import _component
from ._component import _AudioSource, _Transport

VENDOR: str
BUTTERWORTH_LOW: float
BUTTERWORTH_HIGH: float
FLAT_Q: float
MIN_Q: float
MAX_Q: float
TRIM_CORNER_HZ: float
TRIM_Q: float
FLAT_DB: float

class LowPass(_component.Component):
    """A low-pass: above the corner the signal rolls away.

    **Controls.** Frequency slides the whole curve along without changing
    its shape. Resonance is how loud the corner itself stands: at 0.707 it
    is 3 dB down and the roll-off is as gentle as it gets, and turned up it
    stands above the passband and a click at the input rings where you put
    it. Slope is 12 or 24 dB an octave. Trim is a flat gain across the band.
    Mix at 0 is your dry signal. The Effect controls page lists what the
    knobs span.

    **Response.** Above the corner the roll-off is 12 or 24 dB an octave.
    The curve keeps one shape at every corner from 31.5 Hz up. From 40 Hz
    up at 48 kHz the corner stands as loud as Resonance says at either
    slope; at the bottom of the Frequency knob with Resonance high on the
    steep slope it stands a little low.

    **Timing.** Latency is zero at every setting. Silence in is silence out
    once the filter rings down, and the class reports a tail that covers its
    lowest corner and highest Resonance.

    **Levels.** Keep the input under -3 dBFS and the defaults and patches
    stay off the rails. Trim at its top can still push the output onto the
    rails.

    **On a board.** The class needs audiodsp's `audiobiquad`, and on a board
    without it construction raises `ImportError`.
    """

    NAME: str
    DISPLAY_NAME: str
    CATEGORIES: tuple[str, ...]
    VERSION: str
    TIER: str
    REQUIRES: tuple[str, ...]
    CAPABILITIES: tuple[str, ...]
    LATENCY_SAMPLES: int
    TAIL_SAMPLES: int
    INPUT_CEILING_DBFS: int
    CLIPS_AT_TOP: tuple[int, ...]
    MACRO_LABELS: tuple[str, ...]
    MACRO_MODES: dict[int, str]
    PATCHES: dict[int, tuple[str, tuple[float, ...]]]

    def __init__(
        self,
        source: _AudioSource,
        frequency: float = 20000.0,
        q: float = ...,
        slope: int = 12,
        mix: float = 1.0,
        trim_db: float = 0.0,
        patch: int | None = None,
        *,
        sample_rate: int | None = None,
        transport: _Transport | None = None,
    ) -> None: ...
    @property
    def tail_samples(self) -> int | None:
        """The ring time of *this* build: the sections in circuit, each
        bounded from its coefficients in force (`_component.biquad_ring`),
        summed down the cascade. The bound holds from any state the
        sections can hold, including what the settings before a move left
        in them (audiocomponents#114). A section that Mix 0 or the Slope
        switch has taken out passes its input through and adds nothing."""
