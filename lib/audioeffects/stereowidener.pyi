# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT
from . import _component
from ._component import _AudioSource, _Transport
from .digitaldelay import whole_frames as whole_frames

VENDOR: str
DELAY_MIN_MS: float
DELAY_MAX_MS: float
LINE_MS: float
SLEW: float
HARD: float
SIGN: int
NEGATE: int
TABLE_FRAMES: int
BLOCK: int
ECHO_TOLERANCE: float
DELAY_STEPS: dict[int, float]
STEP_TOLERANCE: float
WIDTH_I: int
DELAY_I: int
CHARACTER_I: int
CHARACTERS: tuple[str, ...]
DEFAULT_WIDTH: float
DEFAULT_DELAY_MS: float

def haas_voices(width: float) -> tuple[tuple[float, float], tuple[float, float]]:
    """((lead level, lead panning), (copy level, copy panning)) for a Haas
    Width: up to 1 the lead keeps the left at unity and turns its right down
    by the Width while the copy comes up in the right; above 1 the copy
    stays at unity and the lead turns down to 1/Width."""

class StereoWidener(_component.Component):
    """Widen a stereo part: Haas delays the right channel a few milliseconds
    behind the left, and Mid/Side scales the difference between the channels.

    **The controls.** Width sets how wide the part sounds. Delay is how
    late the Haas copy is, and only Haas uses it. Character picks Haas or
    Mid/Side. The Effect controls page lists what the knobs span.

    **Haas.** The ear places a sound by the first arrival and hears the late
    copy as width.
    At Width 1 the left channel passes untouched and the right channel is
    your right channel, exactly Delay late.
    Between Width 0 and 1 the right channel crossfades from itself to its
    late copy, which colours it most at 0.5.
    Width 0 is a wire.
    Above Width 1 the copy stays where it is and the left turns down, 6 dB
    at Width 2, to pull back the image the left's early arrival leans its
    way.
    Turning Delay glides the copy to the new time instead of clicking,
    bending its pitch while it moves.
    Haas folds to mono as a comb filter: at Width 1 with the default 14 ms,
    the mono sum has full-depth notches at 35.7, 107 and 179 Hz and on up.
    Use Mid/Side when the mix may be summed.

    **Mid/Side.** Summed to mono, the output is the same at every Width,
    within one LSB.
    Width 0 is mono, 1 is a wire and 2 doubles the sides.
    Above Width 1, a part panned hard left shows up inverted on the right.
    A part that is the same in both channels comes out unchanged.
    Peaks below half of full scale never clip at any Width.

    **Mono, latency, tail.** A one-channel source comes out exactly as it
    went in, whatever the controls say.
    To widen a mono part, make it stereo first (a stereo chorus, say) and
    put this after it.
    A click in the left comes out on the frame it went in: there is no
    latency.
    `tail_samples` is the copy's reach in Haas, and 0 in Mid/Side or at
    Width 0.
    `reset()` empties the line and returns to patch 0.
    The class never reads the host's tempo.

    **Limits shared by the family.**
    A control that jumps, Width or Character, makes the output step: move it
    in small steps from the host if you need it smooth.
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
    INPUT_CEILING_DBFS: float
    MACRO_LABELS: tuple[str, ...]
    MACRO_MODES: dict[int, str]
    PATCHES: dict[int, tuple[str, tuple[float, ...]]]

    def __init__(
        self,
        source: _AudioSource,
        width: float = 1.0,
        delay_ms: float = 14.0,
        character: float | str = "haas",
        patch: int | None = None,
        *,
        sample_rate: int | None = None,
        transport: _Transport | None = None,
    ) -> None: ...
    def macro(self, index: int) -> float:
        """What macro `index` currently stands for, in its own units; for
        Delay, the milliseconds it plays."""

    @property
    def tail_samples(self) -> int | None:
        """What this bound promises is in the class docstring."""
