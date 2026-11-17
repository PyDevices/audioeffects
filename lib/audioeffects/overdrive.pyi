# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT
from array import array
from typing import Any

from . import _component
from ._component import _AudioSource, _Transport

VENDOR: str
R1: float
R6: float
P1: float
C4: float
TONE_LP_HZ: float
UMAX: float
MIN_Q: float
MAX_Q: float
DRIVE_DEFAULT: float
LEVEL_DEFAULT: float
CURVE_VOLTS: float
CURVE_BYTES: bytes
CURVE: array[int]
OVERSAMPLE_FLOOR_HZ: float
ALIAS_DEFAULT_DB: float
ALIAS_PATCH_DB: float
ALIAS_SURFACE_DB: float
ALIAS_OVERSAMPLE_COST_DB: float
INPUT_CEILING_DBFS: float
SURFACE_CEILING_DBFS: float

def shipped_oversample(sample_rate: int) -> Any:
    """The factor this rate ships with: x4 at 48 kHz and up, x8 below it.

    Never below x4, because x2's own node floor at 1010 Hz is -56.4 dB and
    fails T7 before the class is in it; never above x8, because the node
    stops there and because the cost is real - x8 at 48 kHz is +0.799 ms
    on the P4 and +1.408 ms on the S3 per block, which is the whole of why
    the budget's rate keeps x4.

    So the rule is exactly: **x8 at every rate below 48 kHz, x4 at 48 kHz
    and above.** The 192 kHz floor is reached at 48 kHz and above only.
    **Every rate under 24 kHz leaves the internal rate under that floor**
    and takes x8 anyway because x8 is all there is: 22.05 kHz runs
    176.4 kHz internally, and 16 kHz - outside this program's three rates,
    but reachable - runs 128 kHz and reads **-50.451 dB** at Drive max on
    the wet branch, **-41.732 dB** at the worst macro corner. (The -56.9 dB
    the second fix round quoted here was a *mixed* reading, with the dry
    note diluting the floor by about 6 dB.) The ceiling is the node's:
    `AUDIODSP_SHAPER_MAX_OVERSAMPLE` is 8, and audiodsp#104 is the ask.
    The floor is a target, not a guarantee, and the class's bars are
    `ALIAS_DEFAULT_DB` / `ALIAS_PATCH_DB` / `ALIAS_SURFACE_DB` /
    `ALIAS_OVERSAMPLE_COST_DB`.
    """

DC_BLOCK_HZ: float
DC_BLOCK_Q: float
OFFSET_LINE: array[int]
OFFSET_GAIN: float
DC_SETTLE_BLOCKS: int
DC_QUIET_FRAMES: int

class _MixAsLevel:
    """A filter's `mix` under the name a mixer voice gives its level, so
    `Component._rearm_from` can hold it at the dry and let it walk back
    with the voices: `audiobiquad.Biquad` walks a `mix` move over 20 ms."""

    def __init__(self, node) -> None: ...
    @property
    def level(self) -> Any: ...
    @level.setter
    def level(self, value: float) -> None: ...

class Overdrive(_component.Component):
    """A Tube Screamer-shaped overdrive: your note at unity, with a
    high-passed, clipped copy added on top.

    **Controls.** Drive is how hard the copy is clipped, and even at its
    floor the pedal is not clean. Tone is a low-pass after the clip. Body is
    the corner of the high-pass in front of the clip, so it sets how much
    bass reaches it. Ceiling is how tall the clipped copy stands. Symmetry
    biases the clip off centre and brings in even harmonics. Level is the
    output stage. Mix is how much clipped signal is added to your note; it
    does not turn the note down. The Effect controls page lists what the
    knobs span.

    **Switching.** Mix at 0 takes the pedal out of circuit and hands back
    your signal byte for byte. Leaving 0 switches the pedal on fresh,
    rather than replaying what it held when it went off. At Mix 1 with Level
    at 0 the pedal is silent.

    **Sound.** At the defaults, bass comes through cleaner than the mids, as
    the high-pass in front of the clip makes it; at the bottom of Body, or
    on a square, that reverses. With Symmetry centred the
    dirt rises with Drive; off centre it peaks partway up the knob. The clip
    runs oversampled, so aliasing stays at least 40 dB under the note
    anywhere on the panel, up to a full-scale input.

    **Timing.** Latency is zero at every setting. Silence in is silence out
    at every shipped patch.

    **Levels.** Keep the input under -1 dBFS and the shipped patches stay
    off the rails; anywhere on the panel, keep it under -6 dBFS.

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
    ALIAS_DEFAULT_DB: float
    ALIAS_PATCH_DB: float
    ALIAS_SURFACE_DB: float
    ALIAS_OVERSAMPLE_COST_DB: float
    INPUT_CEILING_DBFS: float
    SURFACE_CEILING_DBFS: float
    MACRO_LABELS: tuple[str, ...]
    MACRO_MODES: dict[int, str]
    PATCHES: dict[int, tuple[str, tuple[float, ...]]]

    def __init__(
        self,
        source: _AudioSource,
        drive: float = ...,
        tone: float = ...,
        level: float = ...,
        mix: float = 1.0,
        body: float = 720.0,
        ceiling: float = 1.0,
        symmetry: float = 0.0,
        oversample: bool | int | None = None,
        patch: int | None = None,
        *,
        sample_rate: int | None = None,
        transport: _Transport | None = None,
    ) -> None: ...
    def reset(self) -> None:
        """Clear every node and restore patch 0, then arm the graph as
        `_build` does, so a reset is a fresh instance (no block primed
        through the chain before it was cleared plays after it)."""
    WALKS_TO_BYPASS: bool
