# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT
from typing import Any

from . import _component
from ._component import _AudioSource, _Transport
from .chorus import nominal_damping_hz as nominal_damping_hz

VENDOR: str
TIME_MIN_MS: float
TIME_MAX_MS: float
FULL_RANGE_MS: float
GLIDE_MIN_MS: float
GLIDE_MAX_MS: float
SLEW_PIN: float
GLIDE_FLOOR: float
FEEDBACK_MAX: float
LINE_HEADROOM_MS: float
LINE_PEAK: int
FEEDBACK_MARGIN: float
STALL_CLEARANCE: float
STALL_FUZZ: float
CUT_LAP_FACTOR: int
DIVISION_BEATS: tuple[float, ...]
TIME_I: int
FEEDBACK_I: int
MIX_I: int
GLIDE_I: int
SYNC_I: int
DIVISION_I: int
TONE_I: int
CUT_I: int
DEFAULTS: tuple[float, ...]

def nominal_cut_hz(corner_hz: float, sample_rate: int) -> Any:
    """`cut_hz` whose one-pole high-pass -3 dB is `corner_hz` at
    `sample_rate`. 0 stays 0, which is the filter out of circuit.

    The node's high-pass is `y -= lp(y)` with the low-pass coefficient
    a = 1 - exp(-2 pi hz / fs) (`audiodsp_feedback_delay.c:33-40`,
    `:498-501` at v0.6.2), so with b = 1 - a it is
    H = b (1 - z^-1) / (1 - b z^-1).
    |H|^2 = 1/2 gives b^2 (3 - 4 cos w) + 2 b cos w - 1 = 0; the root in
    (0, 1) is the pole, and `cut_hz = -fs ln b / 2 pi`.
    """

def slew_of(glide_ms: float) -> float:
    """The node's `delay_slew` for a Glide: 0 (the jump) at Glide 0,
    otherwise 787.5 ms over `glide_ms`, pinned at 0.99."""

def whole_frames(time_ms: float, sample_rate: int) -> int:
    """The nearest whole frame at the running rate (dossier section 6)."""

def laps_to_zero(feedback: float, excess: float = 0.0) -> Any:
    """How many laps of the line can still hold a non-zero sample once the
    input stops. Finite at every Feedback since audiodsp v0.6.3rc1.

    Once the input stops, the node writes `to_s16(recirculated(s, f))` for
    each value s it sends round (`audiodsp_feedback_delay.c:529`). Since
    audiodsp v0.6.2 (#154) `recirculated` (`:344`) rounds f s to nearest
    where |s| - |f s| > 0.5 and truncates it toward zero otherwise.

    With Repeat Tone out (`excess` 0) s is a line sample, or a mix of two
    at a fractional read, so |s| <= x, the line's peak, and the node
    guarantees |write| < |s|: a lap maps x to at most
    min(x - 1, floor(f x + 0.5)). Both halves only grow with x, so the peak
    of one lap bounds every sample of the next, and iterating from full
    scale counts the laps to exact zero. That is finite at every Feedback;
    0.99 takes 685 laps.

    With Repeat Tone in, s is the loop low-pass's state, which can sit
    above the line's peak by up to `excess` times it (`DigitalDelay`'s
    `_tone_excess`). Then a lap maps x to the node's write at
    s = x (1 + excess), whichever branch it takes, and the guarantee is
    gone: where that write is still x, the peak is handed back. Up to
    audiodsp v0.6.2 it stayed there for ever (1 LSB at Feedback 0.5, 5 at
    0.9, Tone 800 Hz, on a DC input), and this count was `None` there.
    From v0.6.3rc1 (audiodsp#157) the node sets a damping state that has
    stopped moving onto its input, once a block, at or below 64 LSB, which
    covers every such x (at most 50, at the node's 0.99). So the peak is
    counted one more lap there and then leaves as with the filter out,
    min(x - 1, floor(f x + 0.5)). The extra lap is measured, not derived
    (the landing waits for a block's end, and a host picks the block):
    at every window centre k = 1 ... 50, Repeat Tone grid 0, 64 and 126,
    on a 2 LSB DC and on full scale, in blocks of 64 to 4 096 frames at
    Time 12.5 ms, each tail ends inside the count with the extra lap left
    out, 239 frames or more short of it.
    """

def stall_window(feedback: float, excess: float) -> Any:
    """The Repeat Tone stall window `feedback` sits in, as (low, high), or
    `None` outside every window.

    `laps_to_zero(f, excess)` takes its extra landing lap exactly when
    some whole peak x it reaches is handed back: the rounding branch taken,
    x (1 + excess)(1 - f (1 - m)) > 0.5, and the image not below x,
    f (1 + m) x (1 + excess) + 0.5 >= x, m being `FEEDBACK_MARGIN`. For
    each x that is one window, [(1 - 0.5 / x) / ((1 + m)(1 + excess)),
    (1 - 0.5 / (x (1 + excess))) / (1 - m)), 2-4 x 10^-5 wide around
    1 - 0.5 / x; x = 1 ... 50 are the ones under the node's 0.99. Each is
    returned widened by `STALL_FUZZ` either side. With Repeat Tone out
    (`excess` 0) no lap hands a value back, and there is no window."""

def clear_of_stalls(feedback: float, excess: float) -> Any:
    """`feedback` moved to the nearer edge of the Repeat Tone stall window
    it sits in (`stall_window`), just outside it, or unchanged outside
    every window. The top window's upper edge is above the node's 0.99, so
    there it always moves down. Every move is under 3 x 10^-5 of Feedback
    (2.6 x 10^-5 at the 0.99 stop), far inside one step of the 7-bit knob,
    so `get_macro(1)` still names the setting that plays.

    Not called by this class since audiodsp v0.6.3rc1 (the node lands a
    stalled damping state, audiodsp#157); only planted faults use it."""

class DigitalDelay(_component.Component):
    """A clean digital delay with the DD-2's control law: the dry path is a
    wire, and turning Time pitch-bends the repeats instead of clicking.
    audiodsp tier; zero latency. The module docstring has the rest."""

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
        time_ms: float | None = None,
        feedback: float | None = None,
        mix: float | None = None,
        glide_ms: float | None = None,
        sync: bool | float | None = None,
        division: float | None = None,
        tone_hz: float | None = None,
        cut_hz: float | None = None,
        max_time_ms: float = 800.0,
        patch: int | None = None,
        *,
        sample_rate: int | None = None,
        transport: _Transport | None = None,
    ) -> None: ...
    def reset(self) -> None: ...
    @property
    def tail_samples(self) -> int | None:
        """Frames until the output is exactly zero once the input stops, as
        an upper bound.

        `laps_to_zero(f)` laps, each at most one frame longer than the
        longest delay the read head may be at (the read interpolates
        towards the next older frame). While a Glide walk falls, that is
        the Time it is walking from, not the target, and it stays so until
        a Glide-0 move or a reset lands the head, because the class cannot
        see how far the walk has got.

        Finite at every Feedback. With Repeat Tone in, each lap is
        `memory` frames longer, the time the low-pass takes to forget the
        lap before, and near the Feedback values where the node once held a
        small value for ever the count takes one more lap (`laps_to_zero`).
        With Repeat Cut in, the laps are counted `CUT_LAP_FACTOR` times:
        the high-pass can lift a lap's peak above the last one's, so that
        margin is measured, not derived (`CUT_LAP_FACTOR`).
        """
