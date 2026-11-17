# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT
import audioeffects.reverb as _reverb

from . import _component
from ._component import _AudioSource, _Transport
from .digitaldelay import (
    CUT_LAP_FACTOR as CUT_LAP_FACTOR,
)
from .digitaldelay import (
    laps_to_zero as laps_to_zero,
)
from .digitaldelay import (
    whole_frames as whole_frames,
)
from .tapedelay import tone_excess as tone_excess

VENDOR: str
BLOCK: int
TIME_MIN_MS: float
TIME_MAX_MS: float
LINE_MS: float
FULL_RANGE_MS: float
FEEDBACK_MAX: float
LOOP_BASS_LAP_FACTOR = CUT_LAP_FACTOR
TIME_I: int
FEEDBACK_I: int
GLIDE_I: int
DRIVE_I: int
LOOP_TOP_I: int
LOOP_BASS_I: int
TOP_CUT_I: int
LOW_CUT_I: int
DECAY_I: int
DAMPING_I: int
MIX_I: int
DEFAULTS: tuple[float, ...]
DEFAULT_STEPS: tuple[int, ...]
STEP_TOLERANCE: float
REVERB_DECAY_I: int
REVERB_DAMPING_I: int
REVERB_LOW_CUT_I: int
CHAMBER_PATCH: tuple[int, ...]

def slew_of(glide_ms: float) -> float:
    """`delay_slew` for a Glide: the whole Time range over Glide."""

class AirSpace(_component.Component):
    """A tape echo sent into a chamber. The module docstring is the
    player's page."""

    NAME: str
    DISPLAY_NAME: str
    CATEGORIES: tuple[str, ...]
    VERSION: str
    TIER: str
    REQUIRES: tuple[str, ...]

    class _Chamber(_reverb.Reverb):
        """The rack's chamber: `Reverb` whose only patch is the chamber at
        the rack's settings, so its own `reset()` lands there without a
        re-cut. Nested, so the module holds one provider."""

        PATCHES: dict[int, tuple[str, tuple[float, ...]]]

    CAPABILITIES: tuple[str, ...]
    LATENCY_SAMPLES: int
    INPUT_CEILING_DBFS: float
    TAIL_SAMPLES: int | None
    MACRO_LABELS: tuple[str, ...]
    MACRO_MODES: dict[int, str]
    PATCHES: dict[int, tuple[str, tuple[float, ...]]]

    def __init__(
        self,
        source: _AudioSource,
        time_ms: float = 111.0,
        feedback: float = 0.375,
        glide_ms: float = 4000.0,
        drive: float = 0.2,
        loop_top_hz: float = 6000.0,
        loop_bass_hz: float = 100.0,
        top_cut_hz: float = 5000.0,
        low_cut_hz: float = 100.0,
        decay: float = 1.8,
        damping_hz: float = 4000.0,
        mix: float = 0.35,
        patch: int | None = None,
        *,
        sample_rate: int | None = None,
        transport: _Transport | None = None,
    ) -> None: ...
    def macro(self, index: int) -> float:
        """What macro `index` currently stands for, in its own units: what
        plays, the default itself on the default's step."""

    def set_macro(
        self,
        index: int,
        value: float,
        channel: int = 0,
        note_id: int = -1,
        sample_position: int = 0,
    ) -> None:
        """Set macro `index` from the 0-127 scale. A whole step is a step
        and plays the default on the default's step; a fraction is a value
        of its own. A call that leaves the position where it is (a host
        echoing `get_macro`) changes neither."""

    def reset(self) -> None:
        """Empty the tape and the chamber, restore patch 0, and play from
        there as a new instance does: the graph is wired again the way the
        constructor wires it, so its levels land at once rather than walking
        from the ones the knobs had left."""

    @property
    def output(self) -> _AudioSource:
        """The node the host plays. Asking for it is the host's first step
        to pulling, so from here Mix's first move off 0 walks in."""

    @property
    def tail_samples(self) -> int | None:
        """Frames until the output is exactly zero once the input stops, as
        an upper bound: the tape's repeats, the Top Cut's ring and the
        chamber's own tail, end to end. The repeats are counted twice over
        (`LOOP_BASS_LAP_FACTOR`), a margin measured rather than derived."""
