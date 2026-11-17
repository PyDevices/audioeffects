# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT
import audioeffects.reverb as _reverb

from . import _component
from ._component import _AudioSource, _Transport
from .digitaldelay import laps_to_zero as laps_to_zero
from .digitaldelay import whole_frames as whole_frames
from .tapedelay import tone_excess as tone_excess

VENDOR: str
BLOCK: int
CHARACTER_I: int
SHIMMER_I: int
RISE_I: int
BLOOM_I: int
INTERVAL_I: int
DECAY_I: int
SIZE_I: int
DAMPING_I: int
MIX_I: int
CHARACTERS: tuple[str, ...]
INTERVALS: tuple[int, ...]
INTERVAL_MIDI: tuple[int, ...]
RISE_MAX: float
WINDOW_MS: float
OVERLAP_MS: float
LOOP_WINDOW_MS: float
LINE_MS: float
STEPS: int
DEFAULT_STEPS: tuple[int, ...]
SHIMMER: float
RISE: float
BLOOM_MS: float
DECAY: float
SIZE: float
DAMPING_HZ: float
MIX: float
DEFAULTS: tuple[float, ...]
HALL_PATCH: tuple[int, ...]

def step_centre_semitones(step) -> float:
    """Semitones that put `audiodelays.PitchShift` on `step`: the centre of
    the step, so the node's truncation lands on it at any float width."""

def interval_step(semitones) -> int:
    """The shifter's read rate nearest `semitones`, in 256ths."""

class ShimmerHall(_component.Component):
    """A pitch shifter around a hall. The module docstring is the player's
    page."""

    NAME: str
    DISPLAY_NAME: str
    CATEGORIES: tuple[str, ...]
    VERSION: str
    TIER: str
    REQUIRES: tuple[str, ...]
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
        character: float | str = "rise",
        shimmer: float = ...,
        rise: float = 0.0,
        bloom_ms: float = ...,
        interval: int = 12,
        decay: float = ...,
        size: float = ...,
        damping_hz: float = ...,
        mix: float = ...,
        patch: int | None = None,
        *,
        sample_rate: int | None = None,
        transport: _Transport | None = None,
    ) -> None: ...
    def macro(self, index: int) -> float:
        """What macro `index` currently stands for, in its own units; for
        Interval, the semitones it plays."""

    @property
    def output(self) -> _AudioSource:
        """The node the host plays. Asking for it is the host's first step
        to pulling, so from here a level that moves is an ordinary move."""

    def reset(self) -> None:
        """Empty the hall, the line and the shifter, return to patch 0, and
        play from there as a new instance does."""

    @property
    def tail_samples(self) -> int | None:
        """Frames until the output is exactly zero once the input stops, as
        an upper bound."""

    class _Hall(_reverb.Reverb):
        """The rack's hall: `Reverb` whose only patch is the hall at the
        rack's patch-0 settings, and whose constructor defaults are that
        patch, so its own `reset()` lands there. Nested, so the module holds
        one provider; last, so the rack's `_build` is the first in this
        source."""

        PATCHES: dict[int, tuple[str, tuple[float, ...]]]

        def __init__(
            self,
            source: _AudioSource,
            patch: int | None = None,
            *,
            sample_rate: int | None = None,
            transport: _Transport | None = None,
            **options: float,
        ) -> None: ...
