# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT
from typing import Any

from . import _component
from ._component import _AudioSource, _Transport

VENDOR: str
FREQ: int
DEPTH: int
MIX: int
SHAPE: int
BAL: int
PBAL: int
SQUELCH: int
THRESH: int
RELEASE: int
CLOW: int
PHASE: int
CHAR: int
Q15: int
TABLE_FRAMES: int
TARGET_FRAMES = TABLE_FRAMES
MAX_CARRIER_FRAMES = TABLE_FRAMES
MAKEUP_DB: float
DEPTH_WIRE: float
NYQUIST_FRAC: float

def carrier_gain(freq_hz: float, corner_hz: float) -> float:
    """First-order high-pass amplitude at `freq_hz` for corner `corner_hz`."""

def bandlimited_odd(phase: float, freq_hz: float, sample_rate: int, shape: float) -> Any:
    """Sine at `shape` 0; odd-harmonic chopper truncated below 0.45·f_s at 1."""

class RingMod(_component.Component):
    """A ring modulator after Harald Bode's: your signal is multiplied by a
    carrier, so at Depth 1 the pitches you played vanish and only their sum
    and difference with the carrier remain, metallic and out of key.

    **Controls.** Frequency sets the carrier, and stops short of 0.45 times
    the sample rate. Depth blends the carrier with a steady level: at 1
    your signal is gone and the two sidebands come out level with each
    other, at 0.5 it is textbook AM, your signal 6 dB over each sideband,
    and at 0 the class is a wire. Mix sets the result against your signal,
    and Mix 0 is a wire too. The Effect controls page lists what the knobs
    span.

    **Character and Shape.** Character switches the carrier from Bode's
    multiplier to his switching chopper. Shape then moves the chopper from
    a sine, where it sounds just like the multiplier, to a band-limited
    square whose odd harmonics add sidebands of their own: at Shape 1 the
    third harmonic's pair sits about 9.5 dB under the main pair. While
    Character is on the multiplier, Shape does nothing.

    **Letting your signal through.** Balance and Program Bal each add a
    steady offset to the carrier, so your signal comes through under the
    ring: at 0.5 it is level with each sideband, to within 0.5 dB. They do
    the same thing.

    **Stereo and the low end.** Stereo Phase shifts the right channel's
    carrier against the left's, and at 0 the two channels match. Carrier
    Low is a high-pass on the carrier and matters only with Frequency
    turned down near it: at its default 5 Hz, a 2 Hz carrier comes out
    about 8.6 dB under a 200 Hz one.

    **Controls that do nothing.** Squelch, Threshold and Release do not
    change the sound: the output is the same sample for sample wherever
    they sit.

    **Levels.** At Depth 1 the ring comes out about 9 dB under your
    signal, and on every patch the output peaks at least 3 dB under the
    input.

    **Timing.** Latency is zero at every setting, and so is the tail:
    silence in is silence out.

    **On a board.** The class needs audiodsp's `audiomath`, and on a board
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
    MACRO_LABELS: tuple[str, ...]
    MACRO_MODES: dict[int, str]
    PATCHES: dict[int, tuple[str, tuple[float, ...]]]
    FORCE_CHOPPER: bool
    FORCE_SINE: bool
    NO_MAKEUP: bool
    FORCE_MAKEUP: bool
    BYPASS_CARRIER_LOW: bool
    OPEN_GATE: bool
    ZERO_MOD: bool
    HARD_CHOPPER: bool
    SKIP_BALANCE: bool

    def __init__(
        self,
        source: _AudioSource,
        frequency: float = 220.0,
        depth: float = 1.0,
        mix: float = 1.0,
        shape: float = 0.0,
        balance: float = 0.0,
        program_bal: float = 0.0,
        squelch: float = 1.0,
        threshold_db: float = -60.0,
        release_ms: float = 50.0,
        carrier_low_hz: float = 5.0,
        stereo_phase: float = 0.0,
        character: float | str = 0.0,
        patch: int | None = None,
        *,
        sample_rate: int | None = None,
        transport: _Transport | None = None,
    ) -> None: ...
    def reset(self) -> None:
        """Clear every node, restore patch 0 and start the carrier again:
        its notes on the modulating `synthio.Synthesizer` played on through
        the walk, a block ahead, so patch 0 now builds a fresh one, as a
        fresh instance does."""
