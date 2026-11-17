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
LINE_MS: float
TONE_MIN_HZ: float
TONE_MAX_HZ: float
WOW_HZ: float
WOW_MAX_CENTS: float
REPEATS_MAX: float
SLEW: float
ECHO_TOLERANCE: float
TIME_I: int
LEVEL_I: int
SATURATION_I: int
TONE_I: int
WOW_I: int
REPEATS_I: int
DEFAULTS: tuple[float, ...]

def wow_depth_ms(cents: float) -> Any:
    """The Wow knob's cents -> the node's `wow_depth_ms` at 0.7 Hz.

    A delay swinging D sin(2 pi f t) ms moves pitch by a peak ratio of
    1 + 2 pi f D / 1000, so the rising side reaches `cents` at
    D = (2^(cents/1200) - 1) / (2 pi 0.7) x 1000 (dossier A4): 1.0 cent is
    0.1314 ms, 3.5 cents 0.4601 ms. Clamped to 0..3.5 cents."""

def tone_excess(damping_hz: float, sample_rate: int) -> tuple[int, float]:
    """(frames, relative excess) for a loop low-pass at `damping_hz` (already
    pre-warped): after `frames` frames whatever its state held weighs under
    2^-17 of it, and its single-precision state can rest up to
    2^-24 / a above the line's peak, a being the coefficient. `DigitalDelay`'s
    `_tone_excess`, as a function of the handed value. (0, 0.0) with Tone
    out."""

class SlapbackDelay(_component.Component):
    """One tape repeat after the dry, in the same place: the Sun Studio slap.

    Your dry signal passes untouched, and one copy of it comes back a moment
    later, a little quieter: the two-machine tape echo on Sam Phillips' Sun
    sides.
    By default the repeat comes 134.4 ms after the dry, once.

    **The controls.** Time is the gap between the dry and the repeat. Level
    is the console's return. Saturation is how hard the return drove the
    record amplifier. Tone is the tape path's top end. Wow is the
    transport's slow wobble. Repeats sends the slap round again.
    Time runs from 40 to 250 ms, Level from 0 to 2, Saturation from 0 to 1,
    Tone from 2 kHz to out at its top stop, Wow from 0 to 3.5 cents and
    Repeats from 0 to 0.6.
    Level 0 is a wire.
    Up to Level 1 the dry passes untouched until the repeat arrives, however
    hard Saturation drives the repeat.
    A hot input can reach the rail, since the repeat adds to a dry at unity.
    Keep the input under -6 dBFS and the defaults and patches stay off the
    rails.
    At Repeats 0 there is one repeat and no second.
    Repeats above 0 sends the repeat round for more.
    Wow swings the repeat's pitch by the cents the knob reads, at a slow
    fixed rate.
    The default Wow takes the repeat's very top more than 4 dB down at
    Nyquist, where Wow 0 leaves it within half a dB.
    At 22.05 kHz the last Tone positions below the top stop clamp below
    Nyquist and all do the same thing.

    **Time.** Every Time position lands on the nearest whole frame at
    48 kHz.
    At 44.1 and 22.05 kHz the node lands some positions a fraction of a
    frame off, and a sliver of the repeat falls on the frame beside it.
    A host that writes back `get_macro(0)` keeps the constructor's exact
    Time.
    Turning Time walks the repeat to the new Time, bending its pitch,
    instead of clicking.
    A Wow move glides instead of stepping.

    **Mono, latency, tail.** A source the same in both channels comes out
    the same in both channels, and a one-channel source gets the stereo
    render's left channel.
    A click comes out on the frame it went in: there is no latency.
    `tail_samples` is an upper bound on how many frames the output takes to
    reach exact zero, counted from when your input stops or from when you
    read it if that is later, for the settings as they stand when you read
    it.
    `reset()` empties the line and returns to patch 0.
    The class never reads the host's tempo.
    A constructor value outside a knob's span clamps to the nearer stop, a
    `tone_hz` of 0 or less is Tone out, and NaN takes the option's default.

    **Limits shared by the family.**
    Level walks a jump over 20 ms, but any other control that jumps makes
    the output step: move it in small steps from the host if you need it
    smooth.
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
        time_ms: float | None = None,
        level: float | None = None,
        saturation: float | None = None,
        tone_hz: float | None = None,
        wow_cents: float | None = None,
        repeats: int | None = None,
        patch: int | None = None,
        *,
        sample_rate: int | None = None,
        transport: _Transport | None = None,
    ) -> None: ...
    def reset(self) -> None: ...
    @property
    def tail_samples(self) -> int | None:
        """What this bound promises is in the class docstring; how it is
        built is in the dossier."""
