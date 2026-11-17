# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT
from array import array
from typing import Any

from . import _component
from ._component import _AudioSource, _Transport

VENDOR: str
V_SCALE: float
LEVEL_LINE: array[int]
LEVEL_GAIN: float
GBW_HZ: float
R_GAIN: float
R_BODY_STOCK: float
R_BODY_RUETZ: float
R_LEG_BASS: float
FILTER_R0: float
FILTER_POT: float
FILTER_C: float
FILTER_R0_SCOOP: float
BOOSTER_HZ: float
TONE_LP_HZ: float
TONE_HP_HZ: float
CLIP_LP_HZ: float
OPAMP_HP_HZ: float
OUT_HP_HZ: float
PARK_HZ: float
PARK_LO_HZ: float
CLICK_DELAY_SAMPLES: dict[int, int]
OVERSAMPLE_FLOOR_HZ: float

def shipped_oversample(sample_rate: int) -> Any:
    """The factor this rate ships with: x4 at 48 and 44.1 kHz, x8 at 22.05.

    Never below x4 - x2 misses A1 at every rate - and never above x8,
    because the node stops there and because above `OVERSAMPLE_FLOOR_HZ`
    the floor is no longer the fold. At 48 kHz x8 moves maximum-Distortion
    1010 Hz from -58.51 to -58.93 dB and 3700 Hz from -48.11 to -48.12 for
    +0.784 / +1.408 ms, which is why it is not taken there.
    """

DIST: int
FILT: int
TONE: int
VOL: int
MIX: int
CHAR: int
CEIL: int
BOOST: int
ASYM: int
BODY: int

class Distortion(_component.Component):
    """A hard-clipping distortion with a pair of pedals inside it: the ProCo
    Rat (`filter`, the default) and Boss's orange distortion (`scoop`).

    **Controls.** Distortion is the gain in front of the clip. Filter is the
    tone control after it, and on the Rat it runs backwards: clockwise is
    darker. Tone is the Boss's scooped bass-to-treble balance. Volume is the
    output level and Mix how much of the clipped signal replaces your note.
    Character picks the pedal. Ceiling is how tall the clipped signal
    stands. Boost is a booster in front of the clip, and `scoop` starts
    with it at 35 dB because the Boss has one in its circuit. Asymmetry
    clips the Boss's sides unevenly, which brings in even harmonics.
    Body moves the Rat's treble leg between the stock pedal and a common
    modification. The Effect controls page lists what the knobs span.

    **Switching.** Mix at 0 hands back your signal untouched. Leaving 0
    switches the pedal on fresh, rather than replaying what it held when it
    went off.

    **Sound.** At Distortion 0 the Rat is nearly clean and the Boss never
    is. Turned up, the Rat's brightness folds into a mid hump. On `scoop`
    every Filter position is its own, and Filter at 0 is the stock Boss.
    At the defaults, aliasing on a 1010 Hz tone between -22 and -16 dBFS
    stays 60 dB under the note; louder than that it does not.

    **Timing.** Latency is 2 samples at Mix 1 and zero at any Mix below it.
    Silence in is silence out at every shipped patch, and the tail settles
    inside what the class reports.

    **Levels.** A full-scale input plays without wrapping at every shipped
    patch. The clip keeps its output inside its own headroom at any Ceiling,
    so Ceiling stops raising the level before the top of its travel, and
    with Ceiling high, Volume and Mix stop moving the output above a knee
    that `wet_ceiling()` reports. No shipped patch sits on a DC offset, and
    the first note does not arrive on one.

    **On a board.** The class needs audiodsp's `audioshaper`, `audiobiquad`
    and `audioroute`, and on a board without them construction raises
    `ImportError`.
    """

    LAZY_BUILD: bool
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
    OVERSAMPLE: int
    ASYM_BLEND_STEPS: int
    CLIPPER_CEILING: float

    def __init__(
        self,
        source: _AudioSource,
        distortion: float = 0.5,
        filt: float = 0.5,
        tone: float = 0.0,
        volume: float = ...,
        mix: float = 1.0,
        character: float | str = 0.0,
        ceiling: float | None = None,
        boost: float | None = None,
        asymmetry: float = 0.0,
        body: float = 0.0,
        patch: int | None = None,
        oversample: bool | int | None = None,
        *,
        sample_rate: int | None = None,
        transport: _Transport | None = None,
    ) -> None: ...
    @property
    def latency_samples(self) -> int: ...
    WALKS_TO_BYPASS: bool

    def reset(self) -> None:
        """Clear every node and restore patch 0, then arm the graph as
        `_build` does, so a reset is a fresh instance (no block primed
        through the chain before it was cleared plays after it)."""

    def wet_ceiling(self) -> Any:
        """The largest wet level this class can deliver at the Ceiling and
        Asymmetry in force, 0-1 - and therefore where `Volume` and `Mix`
        stop moving the output.

        `Ceiling` scales the diode drop and the clipper's own output is
        held at or below `CLIPPER_CEILING` of full scale, so above this
        point the split in `_headroom` has nowhere left to put the level:
        `post_gain` is already at the ceiling and a mixer voice cannot go
        past 1.0. **Volume and Mix are live below it and inoperative above
        it** - `Volume` MIDI 84 to 127 is one number at shipped patch 3,
        which is 43 positions and 3.6 dB of label travel delivering 0.00 dB
        (audit 3 (p)2, ruling (o)).

        At the shipped Ceiling (MIDI 42) and Asymmetry 0 this is **1.0** -
        the whole travel works - and it falls as either knob rises: the
        knee is what `test_volume_is_monotone_below_the_knee` walks.
        """
