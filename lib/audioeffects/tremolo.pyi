# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT
from typing import Any

from . import _component
from ._component import _AudioSource, _Transport

VENDOR: str
TABLE_FRAMES: int
BIAS: int
OPTICAL: int
CHAR: int
RATE: int
DEPTH: int
SHAPE: int
LAG: int
BIAS_M: int
LINK: int
PHASE: int
SYNC: int
DEPTH_WIRE: float
R_SRC: float
R_DARK: float
R_LIT: float
R_INT_MAX: float
TAU_ON_S: float
Q15: int

def kinked_sine(phase: float, shape: float) -> Any:
    """Near-sine with a small kink at the bottom (S5). `phase` radians."""

def triangle(phase: float) -> Any:
    """Unit triangle on a 2π period. Planted-fault LFO, not the class."""

def link_scale(rate_hz: float) -> float:
    """Speed-Link amplitude vs Rate. ~3 dB from 3 Hz to 8 Hz."""

def depth_travel(depth: float) -> float:
    """Saturating Depth law (B2): first 20 % of travel adds more than last."""

def bias_gain(s: float, depth: float, idle: float, curve_p: float = 1.8) -> Any:
    """Concave stage gain vs a bipolar LFO sample `s` in [−1, 1]."""

def optical_gains(
    frames: int,
    _rate_hz: float,
    sample_rate: int,
    depth: float,
    shape: float,
    lag_ms: float,
    neon: bool = True,
    equal_tau: bool = False,
    ignore_lag: bool = False,
    gate: bool = False,
    force_taus=None,
) -> Any:
    """One period of optical divider gain, already dark-normalised to 1."""

def tempo_divisions(bpm: float) -> Any:
    """Hz values for whole, half, quarter, eighth, sixteenth, 32nd."""

def snap_rate(rate_hz: float, bpm: float) -> Any: ...

class Tremolo(_component.Component):
    """A tremolo with two amp characters on one LFO: Bias, the near-sine
    wobble of a Fender's bias-vary circuit, and Optical, a neon lamp pulsing
    into a photocell.

    **Controls.** Character picks Bias or Optical. Rate is the sweep's
    speed, and at Depth 0 the output is your signal untouched. Speed Link
    makes the depth fall as Rate falls, the way one pot moves the amp's
    whole RC section. Bias runs from a cold idle to a hot one, and a hot
    idle makes the Bias wobble more than 6 dB shallower. In Optical, Lag is
    how slowly the photocell recovers, so a fast Rate loses depth; Shape
    sets how much of each cycle the signal spends dimmed, less as Shape
    rises. Stereo Phase offsets the right channel's wobble from the left's:
    at 180 one side swells as the other dips. The Effect controls page
    lists what the knobs span.

    **Bias.** At half Depth the wobble is close to a sine, every harmonic of
    it more than 26 dB down. Its dips go further below the average than its
    swells rise above it, its rise and fall run at about the same speed, and
    it never mutes: at full Depth the dip stays within 40 dB of the swell.

    **Optical.** The light dims the signal faster than it recovers, by more
    than two to one, so the wobble is a pulse rather than a sine. It is a
    divider, never a gate: at full Depth the dip sits between 15 and 40 dB
    below the swell.

    **Sync.** With Sync on, Rate snaps to the nearest of one sweep a whole
    note, half, quarter, eighth, sixteenth or 32nd note at the host's tempo.
    With no host the class follows its own 120 bpm, and a host that reports
    no tempo leaves Rate where the knob is.

    **Levels and timing.** Silence in is silence out. The gain moves every
    sample, not every block, so at 48 kHz it leaves no block-rate buzz
    within 80 dB of your signal. Latency and tail are zero at every setting.

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
    BLOCK_HOLD: bool
    FORCE_LINK_SCALE: float | None
    LFO_KIND: str
    CURVE_P: float
    ALLOW_MUTE: bool
    IGNORE_BIAS: bool
    BIAS_USE_OPTICAL_TRACKER: bool
    EQUAL_TAU: bool
    NEON: bool
    GATE_AT_DEPTH1: bool
    IGNORE_LAG: bool
    PLAIN_SINE: bool
    SHALLOW_LINEAR: bool
    RATE_PERIOD_SCALE: float
    TRACKER_TAUS: tuple[float, ...]

    def __init__(
        self,
        source: _AudioSource,
        character: float | str = 0.0,
        rate: float = 5.0,
        depth: float = 0.5,
        shape: float = 0.5,
        lag_ms: float = 35.0,
        bias: float = 0.5,
        speed_link: float = 1.0,
        stereo_phase: float = 0.0,
        sync: bool | float | None = 0.0,
        patch: int | None = None,
        *,
        sample_rate: int | None = None,
        transport: _Transport | None = None,
    ) -> None: ...
    def reset(self) -> None:
        """Clear every node, restore patch 0 and start the LFO again.

        The LFO is a note on a `synthio.Synthesizer`, which the walk does
        not reach: it played on, holding a block it had rendered before the
        reset, and the note it was asked for next started on top of the old
        one's release. A fresh synthesizer, which patch 0 then presses, is
        the LFO a fresh instance starts with."""
