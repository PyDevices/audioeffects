# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT
from typing import Any

from . import _component
from ._component import _AudioSource, _Transport
from .chorus import nominal_damping_hz as nominal_damping_hz
from .digitaldelay import laps_to_zero as laps_to_zero
from .digitaldelay import whole_frames as whole_frames

VENDOR: str
TIME_MIN_MS: float
TIME_MAX_MS: float
HEADS_MIN: int
HEADS_MAX: int
FEEDBACK_MAX: float
TONE_MIN_HZ: float
TONE_MAX_HZ: float
TILT_DB: float
MAX_LAP_MS: float
MIN_LAP_MS: float
BLOCK: int
LAG = BLOCK
MIN_SAMPLE_RATE: int
HEAD_SETS: tuple[tuple[int, ...], ...]
DIVISION_BEATS: tuple[float, ...]
DECAY_MARGIN: float
TIME_I: int
PATTERN_I: int
HEADS_I: int
FEEDBACK_I: int
MIX_I: int
TILT_I: int
TONE_I: int
SYNC_I: int
DIVISION_I: int

def f32(value: float) -> Any:
    """`value` rounded to single precision: exact emulation on a desktop,
    the identity on a board, whose float already is one."""

def lap_node_frames(value_ms: float, sample_rate: int) -> Any:
    """The lap node's own arithmetic for a `delay_ms` it is handed,
    `value * rate / 1000.0f` in single precision
    (`audiodsp_feedback_delay.c:148` at v0.6.3rc1)."""

def lap_node_ms(lap, sample_rate: int) -> Any:
    """The `delay_ms` the lap node is handed for a lap of `lap` frames: the
    least single-precision value whose frames, the node's way, are at or
    over `lap`. From float32(lap 1000 / fs), step up one float32 unit while
    the frames are under; if the start is already over, step down while
    the next value down is still at or over."""

def head_set(mode, heads, table=...) -> Any:
    """Pattern mode 1-12 on a grid of `heads` heads -> the heads that
    sound, rising. Mode 12 is every head 1 ... K."""

def head_levels(selected: float, heads, tilt: float) -> Any:
    """Tilt's law: a straight line in dB across the grid, `TILT_DB` x Tilt
    from head 1 to head K, far heads louder for Tilt > 0, with the loudest
    sounding head at exactly 1.0."""

def landed(time_ms: float, heads, sample_rate: int, max_lap_ms: float) -> Any:
    """(n1, P) in frames: the base on the nearest whole frame, clamped so
    the lap P = K n1 fits `max_lap_ms`."""

def trunc_laps(decay: float) -> Any:
    """Laps of the tap node's own loop to exact zero from full scale. Once
    the input stops it writes `(int32_t)(delayed * decay)`
    (`audiodsp_multitap.c:32` at v0.6.3rc1), which truncates toward zero, so a peak x
    goes to floor(x d) < x and the count is finite at every decay."""

def tone_excess(damping_hz: float, sample_rate: int) -> tuple[int, float]:
    """`DigitalDelay._tone_excess` for a pre-warped `damping_hz`: (memory
    frames, relative excess) of the lap node's loop low-pass, (0, 0.0)
    with it out."""

class MultiTapDelay(_component.Component):
    """A multi-head echo: one recording read by several heads on a grid.

    The heads of a multi-head tape echo, after the Roland Space Echo's
    multi-head modes: your dry signal passes untouched, and a pattern of
    echoes follows it.

    **The controls.**
    Time is the gap to head 1, landed on a whole frame, and head k sounds at
    exactly k times that gap.
    Heads is how many heads the grid has, and the pattern repeats once per
    trip past the farthest of them.
    Pattern picks which heads sound, from the twelve positions of the Roland
    RE-202's mode selector.
    Its last position sounds every head on the grid, not the RE-202's
    unpublished positions.
    The lap is the farthest head on the grid, sounded or not, so heads past
    the ones a position sounds lengthen the lap without sounding.
    Feedback sends the pattern round again, each lap quieter.
    Repeat Tone darkens each lap a little more than the one before, once per
    lap, never once per head.
    Tilt leans the pattern's levels towards the near heads or the far ones.
    Up to Mix 1 the dry passes at unity, and at Mix 2 the echoes play alone.
    At unity the dry is exact to the sample, mono and stereo, right up to
    the rails, on every interpreter.
    Keep the input under -6 dBFS and the defaults and patches stay off the
    rails.
    Mix 0 is a wire.
    Sync locks Time to Division of the host's beat, clamped to Time's span.
    With no host tempo, Time stays on the knob.
    Time runs from 20 to 400 ms, Heads from 3 to 8, Feedback from 0 to 0.95
    and Mix from 0 to 2.
    `max_lap_ms` (1600 by default, 540 at least) caps the lap: where a grid
    would pass it, Time comes down to fit.
    A click comes out on the frame it went in: there is no latency.
    A one-channel source gets the same effect on its one channel.
    The sample rate must be at least 12 825 Hz: below it the constructor
    raises `ValueError`.

    **Reset, Mix at zero and the tail.**
    The lines are not fed while Mix is 0, so a return from Mix 0 starts both
    lines empty.
    `reset()` empties both lines and returns to patch 0.
    Neither a reset nor a trip to Mix 0 drops a frame of your source or
    plays one twice, whatever size of buffer it hands out.
    `tail_samples` is an upper bound on how long the echoes take to reach
    exact zero once your input stops.
    The tail rings on while your source hands back nothing.

    **On a board.**
    Measured at v0.6.3, patch 4 costs 5.567 ms a block on the ESP32-S3,
    where a block lasts 5.333 ms, so it needs a P4-class board: the ESP32-P4
    runs it in 3.865 ms.
    Patch 3 costs 4.163 ms on the ESP32-S3, inside the 4.267 ms budget, and
    may need a P4-class board too, especially when the board is running
    anything else.

    **Limits shared by the family.**
    A control that jumps makes the output step: move it in small steps from
    the host if you need it smooth.
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
    MACRO_LABELS: tuple[str, ...]
    MACRO_MODES: dict[int, str]
    PATCHES: dict[int, tuple[str, tuple[float, ...]]]

    def __init__(
        self,
        source: _AudioSource,
        time_ms: float = 150.0,
        pattern: int = 7,
        heads: int = 3,
        feedback: float = 0.45,
        mix: float = 0.35,
        tilt: float = 0.0,
        tone_hz: float = 4000.0,
        sync: bool | float | None = False,
        division: float | None = 3,
        max_lap_ms: float = 1600.0,
        patch: int | None = None,
        *,
        sample_rate: int | None = None,
        transport: _Transport | None = None,
    ) -> None: ...
    def reset(self) -> None:
        """Empty both lines and restore patch 0, without pulling the
        borrowed source (`_route`)."""

    @property
    def tail_samples(self) -> int | None:
        """Frames until the output is exactly zero once the input stops,
        as an upper bound.

        Repeat Tone in: `laps_to_zero(f', excess) x (P + 1 + memory) + P`,
        `DigitalDelay`'s bound for the lap node at the Feedback it is
        handed, plus one lap for the tap node's line to be read out.
        Repeat Tone out: `(trunc_laps(f) + 1) x P`, the tap node's own
        truncating loop. Finite at every setting.
        """
