# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT
from typing import Any

from . import _component
from ._component import _AudioSource, _Transport

VENDOR: str
MAX_DELAY_MS: float
SHAPE_LEN: int
DEPTH_OFF: float

def clock_shape(m: float) -> Any:
    """Q15 table for `d = d0/(1 + m·tri)`.

    Fitted as mid + depth × wow with wow in [−1, 1]:
    wow(u) = −(m + u)/(1 + m·u). Depth 0 is a silent table; the node is
    driven with wow_depth_ms = 0 in that case.
    """

def delay_law(mean_ms: float, m: float) -> tuple[float, float]:
    """Node `delay_ms` and `wow_depth_ms` for mean `mean_ms` and swing `m`.

    mid = d0/(1 − m²), depth = d0·m/(1 − m²), so
    d = mid + depth·wow recovers d0/(1 + m·u).
    """

def nominal_damping_hz(corner_hz: float, sample_rate: int) -> Any:
    """`damping_hz` whose one-pole −3 dB is `corner_hz` at `sample_rate`.

    The node takes the analog-style coefficient `1 − exp(−2π f/fs)`
    (`audiodsp_feedback_delay.c:31-38`), so the knob's hertz is not the
    digital −3 dB. Inverse of |H|² = 1/2 for y += a(x − y).
    """

class Chorus(_component.Component):
    """A one-voice analog chorus, the way a bucket-brigade pedal does it:
    one delayed copy of your signal, its pitch swirling because a triangle
    moves the line's clock rather than its delay.

    **Controls.** Rate is the sweep's speed, and Depth is how far the
    clock swings either way. Mix sets the wet voice against your signal,
    which stays at full level: 0 is a wire, the default 0.815 is the
    vintage blend, and 1 puts the two level. Delay is the line's average
    length. Tone is the wet voice's low-pass: at its default 3 kHz the wet
    voice is at least 10 dB down at 10 kHz, the dark sound of the
    originals, and at 12 kHz it is less than 6 dB down there. The Effect
    controls page lists what the knobs span.

    **One voice.** A hit comes back once, with no repeats: there is no
    feedback. The sweep runs free and does not follow a host's tempo.

    **Levels.** The wet voice adds to your signal, so at Mix 1 the output
    can reach twice the input. Keep the input under -6.03 dBFS and no
    setting reaches a rail; with the ceiling taken away, a phrase peaking
    at -3 dBFS rails. Mix 0 is a wire at any level.

    **Timing.** Latency is zero at every setting: the wet voice's delay is
    the effect, and your own signal comes through on time.

    **On a board.** The class needs audiodsp's `audioecho`, and on a board
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
    INPUT_CEILING_DBFS: float
    MACRO_LABELS: tuple[str, ...]
    MACRO_MODES: dict[int, str]
    PATCHES: dict[int, tuple[str, tuple[float, ...]]]

    def __init__(
        self,
        source: _AudioSource,
        rate: float = 0.8,
        depth: float = 0.35,
        mix: float = 0.815,
        delay_ms: float = 8.8,
        tone_hz: float = 3000.0,
        patch: int | None = None,
        *,
        sample_rate: int | None = None,
        transport: _Transport | None = None,
    ) -> None: ...
    def reset(self) -> None:
        """A reset is a fresh instance: patch 0's delay lands at once."""

    @property
    def tail_samples(self) -> int | None: ...
