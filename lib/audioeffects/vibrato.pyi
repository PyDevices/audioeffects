# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT
from typing import Any

from . import _component
from ._component import _AudioSource, _Transport

VENDOR: str
MAX_DELAY_MS: float
SHAPE_LEN: int
BLOCK_FRAMES: int
DEPTH_OFF: float
M_MAX: float
RISE_10_90: float
DEPTH_GLIDE_MS: float

def one_pole_ring(hz, sample_rate: int) -> int:
    """Frames a `FeedbackDelay` loop filter at `hz` takes to fall from full
    scale to under half an LSB: the node's state falls by exp(-2 pi f / fs)
    a frame (`one_pole_coefficient`), plus one frame for the single
    precision it computes that in. 0 for a filter out of circuit."""

def clock_shape(m: float) -> Any:
    """Q15 table for `d = d0/(1 + m·sin)`.

    Fitted as mid + depth × wow with wow in [−1, 1]:
    wow(u) = −(m + u)/(1 + m·u). Depth 0 is a silent table.
    """

def delay_law(mean_ms: float, m: float) -> tuple[float, float]:
    """Node `delay_ms` and `wow_depth_ms` for mean `mean_ms` and swing `m`.

    mid = d0/(1 − m²), depth = d0·m/(1 − m²), so
    d = mid + depth·wow recovers d0/(1 + m·u).
    """

def peak_cents(mean_ms: float, rate_hz: float, m: float, steps: int = 256) -> float:
    """Exact peak |Δf/f| of `d0/(1 + m·sin ωt)`, in cents."""

def m_for_cents(mean_ms: float, rate_hz: float, cents: float) -> float:
    """Clock index m whose exact peak cents match `cents`, clamped to M_MAX."""

def nominal_damping_hz(corner_hz: float, sample_rate: int) -> Any:
    """`damping_hz` whose one-pole −3 dB is `corner_hz` at `sample_rate`."""

class Vibrato(_component.Component):
    """A vibrato after the Boss VB-2: your signal comes out only through a
    short bucket-brigade line whose clock a sine sweeps, so the pitch
    wobbles and none of the dry is left to comb against it.

    **Controls.** Rate is the sweep's speed. Depth is the peak pitch swing,
    and stays that size wherever Rate and Delay sit. Engage turns the
    vibrato on and off without switching the audio: Rise is how long the
    depth takes to go from 10 % to 90 % of the way, in a straight line. Any
    other knob that moves the depth glides there over 20 ms rather than
    stepping. Delay is the line's average length. Tone is the wet voice's
    low-pass, and Body its high-pass; at the defaults the band is 3 dB down
    at 40 Hz and at 17 kHz. Level cuts the output by up to 12 dB; at the
    top of its travel the output is at the input's level. The Effect
    controls page lists what the knobs span.

    **The sound.** With no dry path there is no comb: from 200 Hz to 2 kHz
    the level stays within 1 dB at any Depth up to 60 cents. At the
    default patch the sweep is a smooth sine, its third harmonic more than
    25 dB down. The sweep runs free and does not follow a host's tempo;
    `reset()` starts it afresh.

    **Timing.** Latency is the Delay, snapped to a whole sample: 4 ms by
    default, which is 192 samples at 48 kHz and 176 at 44.1 kHz. Nothing
    looks ahead.

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
    MACRO_LABELS: tuple[str, ...]
    MACRO_MODES: dict[int, str]
    PATCHES: dict[int, tuple[str, tuple[float, ...]]]

    def __init__(
        self,
        source: _AudioSource,
        rate: float = 5.0,
        depth: float = 30.0,
        rise: float = 1.0,
        engage: bool = True,
        delay_ms: float = 4.0,
        tone_hz: float = 17000.0,
        body_hz: float = 40.0,
        level_db: float = 0.0,
        patch: int | None = None,
        *,
        sample_rate: int | None = None,
        transport: _Transport | None = None,
    ) -> None: ...
    @property
    def latency_samples(self) -> int: ...
    @property
    def tail_samples(self) -> int | None: ...
