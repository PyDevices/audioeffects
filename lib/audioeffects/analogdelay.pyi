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
SINGLE_LINE: str
DOUBLE_LINE: str
STAGES: dict[str, int]
CORNER_PER_STAGE_SECOND: float
TIME_MIN_MS: float
TIME_MAX_MS: float
SWING_MAX_MS: float
RATE_MIN_HZ: float
RATE_MAX_HZ: float
LINE_HEADROOM_MS: float
FEEDBACK_MAX: float
TABLE_POINTS: int
ECHO_TOLERANCE: float
TIME_I: int
FEEDBACK_I: int
MIX_I: int
MODULATION_I: int
RATE_I: int
SPREAD_I: int
SYNC_I: int
DIVISION_I: int

def triangle_table(points: int = ...) -> Any:
    """Q15 unit triangle, one period: 0 -> +1 -> 0 -> -1 -> 0."""

def corner_hz(stages, time_ms: float) -> Any:
    """The sinc's -3 dB point for `stages` at `time_ms`, before the clamp."""

def clock_slew(from_frames: int, to_frames: int) -> float:
    """The node's `delay_slew` for a clock step from a settled line: the
    walk runs |dT| / T_new delay-seconds per second, so it lasts exactly
    T_new and holds the ratio T_old / T_new (dossier section 6)."""

def walk_floor(frames: int) -> Any:
    """The smallest `delay_slew` that still moves a read head sitting at up
    to `frames`: two single-precision steps of `frames`. The node walks
    `delay_current += slew` in single precision, and a slew under half a
    step of the head's position rounds back to where it was, so the head
    would stay put for good (a move under about T / 2048 frames)."""

def node_frames(value_ms: float, sample_rate: int) -> Any:
    """What the node makes of `delay_ms = value_ms`: the single-precision
    `value * rate / 1000.0f` (`audiodsp_feedback_delay.c:148`)."""

def hand_off_ms(frames: int, sample_rate: int) -> Any:
    """The `delay_ms` the class hands the node for whole frame `frames`:
    `frames * 1000 / fs` in single precision, stepped up one single step
    where the node's own arithmetic would land below `frames`, so the
    read's whole part is `frames` (dossier section 6, the hand-off)."""

def tone_excess(damping_hz: float, sample_rate: int) -> tuple[int, float]:
    """(frames, relative excess) for the loop low-pass, by DigitalDelay's
    `_tone_excess` arithmetic: after `frames` frames whatever the state
    held weighs under 2^-17 LSB, and the single-precision state can rest
    up to 2^-24 / a of the peak above it, a being the coefficient."""

class AnalogDelay(_component.Component):
    """A bucket-brigade delay whose Time knob is the line's clock.

    A bucket brigade has a fixed number of stages, so a longer delay is a
    slower clock and a lower band limit: the repeats get darker as you turn
    Time up, and your dry signal passes untouched.

    **The controls.** Time sets the delay and with it the clock. Feedback
    sends each repeat round again. Mix blends the repeats in. Modulation
    and Mod Rate wobble the delay, a chorus in a blend and a vibrato with
    the repeats alone. Spread feeds each side's repeats into the other.
    Sync locks Time to Division of the host's beat, clamped to Time's span.
    Time runs from 20 to 600 ms, Feedback from 0 to 0.99 and Mix from 0 to 2.
    Up to Mix 1 the dry passes untouched until the first repeat arrives.
    Mix 0 is a wire.
    A click comes out on the frame it went in: there is no latency.
    A one-channel source gets the same effect with Spread held at 0.

    **Two characters.** `"single-line"` (the default) is one 4096-stage
    line, the Boss DM-2; `"double-line"` is two in series, the Deluxe Memory
    Man. Any other `character` raises `ValueError`.
    The repeats' high-frequency corner is 0.2211 N / T for N stages and a
    Time of T seconds, so it halves each time Time doubles.
    Where the law passes 0.98 of Nyquist the corner holds there, so a
    shorter Time no longer brightens the repeats.

    **Time.** Every Time lands on a whole frame at every rate.
    A small Time move still lands.
    Turning Time through several positions a block apart takes seconds to
    settle, where one jump to the same place lands within the new Time.

    **Modulation.** The delay swings on a triangle by a fixed number of
    milliseconds, whatever the Time.
    A Time move leaves the swing as it is.
    A Modulation move glides over 20 ms.

    **Level and tail.** Below Mix 1, an input peaking at or below
    floor(32767 (1 - Mix)) - 1 does not reach the rail.
    Keep the input under -6 dBFS and the defaults and patches stay off the
    rails.
    `tail_samples` is an upper bound on how long the repeats take to reach
    exact zero after your input stops.
    `reset()` empties the line and returns to patch 0.
    With no host tempo, Time stays on the knob.

    **What it leaves out.** There is no sample-and-hold, so the repeats
    have no null at the clock.
    There is no fixed anti-alias pair: the repeats' one corner is the one
    that moves with Time.

    **Limits shared by the family.**
    A control that jumps makes the output step: move it in small steps from
    the host if you need it smooth.
    When your source ends, the tail rings out as it would on silence.
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
        time_ms: float = 300.0,
        feedback: float = 0.4,
        mix: float = 0.4,
        modulation_ms: float = 0.0,
        mod_rate_hz: float = 0.8,
        spread: float = 0.0,
        sync: bool | float | None = False,
        division: float | None = 6,
        character: float | str = "single-line",
        max_time_ms: float = 600.0,
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
        the read head may be at, plus the modulation's peak swing in frames
        rounded up, plus one frame for the interpolated read, plus the loop
        low-pass's memory. Finite at every setting the class reaches."""
