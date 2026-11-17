# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT
from typing import Any

from . import _component
from ._component import _AudioSource, _Transport
from .chorus import nominal_damping_hz as nominal_damping_hz
from .digitaldelay import (
    DIVISION_BEATS as DIVISION_BEATS,
)
from .digitaldelay import (
    laps_to_zero as laps_to_zero,
)
from .digitaldelay import (
    whole_frames as whole_frames,
)

VENDOR: str
CHARACTERS: tuple[str, ...]
VARISPEED: str
SLIDING_HEAD: str
TIME_MIN_MS: float
TIME_MAX_MS: float
FULL_RANGE_MS: float
GLIDE_MIN_MS: float
GLIDE_MAX_MS: float
SLEW_PIN: float
GLIDE_FLOOR: float
FEEDBACK_MAX: float
LINE_HEADROOM_MS: float
GAP_M: float
THICK_M: float
SPACING_MIN_UM: float
SPACING_MAX_UM: float
V_FAST: float
V_SLOW: float
T_FAST_MS: float
T_SLOW_MS: float
V_SLIDING: float
WOW_HZ: float
TABLE_POINTS: int
WOW_HARMONIC: int
FLUTTER_HARMONIC: int
WOW_LINE_HZ: float
FLUTTER_LINE_HZ: float
DRIFT_PHASES: tuple[float, ...]
DRIFT_PER_WOW_CENT_MS: float
WOW_MAX_CENTS: float
FLUTTER_MAX_CENTS: float
TIME_I: int
FEEDBACK_I: int
MIX_I: int
GLIDE_I: int
WOW_I: int
FLUTTER_I: int
RECORD_I: int
SPACING_I: int
SPREAD_I: int
SYNC_I: int
DIVISION_I: int
ECHO_TOLERANCE: float
DEFAULTS: tuple[float, ...]

def eq13_gain(k: float, spacing_m) -> float:
    """S3 eq. (13), one pass, as a linear gain at wavenumber `k` (rad/m):
    spacing e^(-k d), thickness (1 - e^(-k delta)) / (k delta) and gap
    |sinc(k g / 2)|, at `GAP_M` and `THICK_M`."""

def k3_of(spacing_m) -> float:
    """The wavenumber at which eq. (13) is at half power (-3.01 dB), by
    bisection in log k: 15 967 rad/m (393.5 um) at 5 um."""

def speed(character, time_ms: float) -> float:
    """Tape speed, m/s, for a character at a Time (dossier section 6)."""

def tone_excess(damping_hz: float, sample_rate: int) -> tuple[int, float]:
    """(frames, relative excess) for the loop low-pass at `damping_hz`
    (already pre-warped): after `frames` frames whatever its state held
    weighs under 2^-17 of it, and its single-precision state can rest up to
    2^-24 / a above the line's peak, a being the coefficient.
    `DigitalDelay`'s `_tone_excess`, as a function of the handed value."""

def slew_of(glide_ms: float) -> float:
    """Sliding-head's `delay_slew` for a Glide: 0 (the jump) at Glide 0,
    otherwise 1 180 ms over `glide_ms`, pinned at 0.99."""

def varispeed_slew(from_ms: float, to_ms: float) -> float:
    """The tape equation for a speed step from a settled transport:
    dT/dt = 1 - T_old / T_new, so the walk runs |dT| / T_new
    delay-seconds per second and lasts exactly T_new (S4 eq. 3)."""

def cents_to_depth_ms(cents: float, line_hz: float) -> Any:
    """A delay D sin(2 pi f t) ms moves pitch by a peak ratio of
    1 + 2 pi f D / 1000, so `cents` peak is
    D = (2^(cents/1200) - 1) / (2 pi f) x 1000: 8 cents of the 0.72 Hz line
    is 1.024 ms, 4 cents of the 5.12 Hz line 0.072 ms."""

def wow_table(
    wow_cents, flutter_cents, out, flutter_harmonic: int = ..., drift: bool = True
) -> Any:
    """Write the wow table for (Wow, Flutter) into `out`, an int16 array of
    `TABLE_POINTS`, and return its peak excursion in ms, which is the
    node's `wow_depth_ms`; 0.0 (and `out` untouched) with nothing to write.

    The wow line's peak is `cents_to_depth_ms(wow, 0.72 Hz)`, the flutter
    line's `cents_to_depth_ms(flutter, 5.12 Hz)` and the drift's 0.25 ms per
    cent of Wow; the table is their sum normalised to its own peak."""

class TapeDelay(_component.Component):
    """A tape echo with the RE-201's motor or the EP-3's sliding head.
    The module docstring is the player's manual."""

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
    MACRO_LABELS: tuple[str, ...]
    MACRO_MODES: dict[int, str]
    PATCHES: dict[int, tuple[str, tuple[float, ...]]]

    def __init__(
        self,
        source: _AudioSource,
        time_ms: float = 350.0,
        feedback: float = 0.45,
        mix: float = 0.35,
        glide_ms: float = 6000.0,
        wow_cents: float = 2.0,
        flutter_cents: float = 1.0,
        record_level: float = 0.2,
        spacing_um: float = 5.0,
        spread: float = 0.0,
        sync: bool | float | None = False,
        division: float | None = 6,
        character: float | str = "varispeed",
        max_time_ms: float = 1200.0,
        patch: int | None = None,
        *,
        sample_rate: int | None = None,
        transport: _Transport | None = None,
    ) -> None: ...
    def reset(self) -> None: ...
    @property
    def tail_samples(self) -> int | None:
        """Frames until the output is exactly zero once the input stops, as
        an upper bound: `laps_to_zero(f, excess)` laps of the longest delay
        the read head may be at, plus the wow table's peak excursion in
        frames rounded up, plus one frame for the interpolated read, plus
        the loop low-pass's memory. Finite at every setting the class
        reaches, stereo and mono, at every Spread."""
