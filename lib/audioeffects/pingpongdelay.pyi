# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT
from . import _component
from ._component import _AudioSource, _Transport
from .chorus import nominal_damping_hz as nominal_damping_hz
from .digitaldelay import (
    CUT_LAP_FACTOR as CUT_LAP_FACTOR,
)
from .digitaldelay import (
    DIVISION_BEATS as DIVISION_BEATS,
)
from .digitaldelay import (
    laps_to_zero as laps_to_zero,
)
from .digitaldelay import (
    nominal_cut_hz as nominal_cut_hz,
)
from .digitaldelay import (
    whole_frames as whole_frames,
)
from .slapbackdelay import tone_excess as tone_excess

VENDOR: str
TIME_MIN_MS: float
TIME_MAX_MS: float
LINE_HEADROOM_MS: float
FEEDBACK_MAX: float
TONE_MIN_HZ: float
TONE_MAX_HZ: float
CUT_MIN_HZ: float
CUT_MAX_HZ: float
SLEW: float
ECHO_TOLERANCE: float
TIME_I: int
FEEDBACK_I: int
MIX_I: int
SPREAD_I: int
SIDE_I: int
SYNC_I: int
DIVISION_I: int
TONE_I: int
CUT_I: int
DEFAULT_TIME_MS: float
DEFAULT_FEEDBACK: float
DEFAULT_MIX: float
DEFAULT_SPREAD: float
DEFAULT_DIVISION: float

class PingPongDelay(_component.Component):
    """Two delay lines crossed into each other: the repeats bounce between the
    speakers.

    Your dry signal passes untouched on both sides, and the repeats come
    back one side and then the other, all the way down.

    **The controls.** The first repeat comes back Time later on the side
    First Side names, the next Time after that on the other side, and they
    keep bouncing, each a Feedback's worth quieter than the last. Time runs
    from 20 to 1000 ms and Feedback from 0 to 0.99. Mix is the echo level:
    the dry stays at unity up to Mix 1, Mix 2 is the repeats alone, and at
    Mix 0 the output is the input. Spread moves between two plain delays
    with the same repeats on both sides, at 0, and the full bounce, at 1. At
    Spread 1 each repeat is on one side only, and the other side is exact
    zero. With Sync on, Time is Division of the host's beat, up to 1000 ms;
    with no host tempo, Time stays where the knob is. The class reads the
    host's transport only while Sync is on, and then only when a control
    moves, a patch loads or the host calls `transport_changed()`, never
    while it plays. Repeat Tone is a low-pass
    and Repeat Cut a high-pass inside the loop, so each bounce is a little
    darker or thinner than the last. Repeat Tone's top stop and Repeat Cut's
    bottom stop take them out, and a filter taken out is out. At 22.05 kHz
    the top positions of Repeat Tone sit on one clamp below Nyquist and
    sound the same. Turning Time walks the repeats to the new Time, bending
    their pitch, instead of clicking.

    **Stereo and mono.** At Spread 1 the loop hears the average of the two
    input channels, so what differs between them never repeats. The dry is
    always each channel's own signal, never swapped or summed. A one-channel
    source gets an ordinary feedback delay at the same Time, Feedback and
    Mix, and Spread and First Side do nothing there.

    **Where it stops.** At 48 kHz every Time position lands on the nearest
    whole frame. At 44.1 and 22.05 kHz the node lands some positions a
    fraction of a frame off, and a sliver of each repeat falls on the frame
    beside it. The dry sits at unity and the repeats add to it, so a hot
    input can reach the int16 rail. With Repeat Cut out and Mix below 1, an
    input that peaks at or below floor(32767 (1 - Mix)) - 1 cannot reach the
    rail, at any Time, Feedback or Spread. Repeat Cut's high-pass
    overshoots, so with it in leave more room.
    Keep the input under -6 dBFS and the defaults and patches stay off the
    rails.

    **Limits shared by the family.** Mix walks a jump over 20 ms, but any
    other control that jumps makes the output step: move it in small steps
    from the host if you need it smooth. When your source ends, the tail
    rings out as it would on silence.

    **Latency, tail, portability.** A click comes out on the frame it went
    in: there is no latency. `tail_samples` is an upper bound on how many
    frames the output takes to reach exact zero, counted from when your
    input stops or from when you read it if that is later, for the settings
    as they stand when you read it. With Repeat Cut in circuit the bound
    is twice as many repeats as with it out, a margin measured rather than
    derived. Pass a lower
    `max_time_ms` for a shorter line: Time then stops at that ceiling, and
    `get_macro(0)` shows where it stopped. A constructor value outside a
    knob's span clamps to the nearer stop, a `tone_hz` or `cut_hz` of 0 or
    less is that filter out, and NaN takes the option's default. `reset()`
    empties the line and returns to patch 0. The class needs audiodsp's
    `audioecho`, and on a board without it construction raises
    `ImportError`.
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
        time_ms: float = 280.0,
        feedback: float = 0.45,
        mix: float = 0.3,
        spread: float = 1.0,
        first_side: str = "left",
        sync: bool | float | None = False,
        division: float | None = 6.0,
        tone_hz: float = 16000.0,
        cut_hz: float = 20.0,
        max_time_ms: float = 1000.0,
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

        `laps_to_zero(f, excess)` laps, each at most one frame longer than
        the longest delay the read head may be at (the read interpolates
        towards the next older frame), plus the Tone low-pass's memory.
        While a walk falls, that is the Time it is walking from, until a
        reset lands the head. The cross-feed hands each lane a convex mix
        of the two lanes' loop values (`audiodsp_feedback_delay.c:581-589`),
        so the per-lap argument holds at every Spread. With Repeat Cut in,
        the laps are counted `CUT_LAP_FACTOR` times, as `DigitalDelay`
        counts them: the high-pass can lift a lap's peak above the last
        one's, and that margin is measured, not derived."""
