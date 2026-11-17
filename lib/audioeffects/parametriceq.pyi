# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT
from . import _component
from ._component import _AudioSource, _Transport

VENDOR: str
FLAT_DB: float
SKIRT_DB: float
ANCHOR_DB: float
ANCHOR_Q: float
CONSTANT_Q: float
MIN_Q: float
MAX_Q: float
SHELF_Q: float
CUT_RATIO: float
OUTPUT_CORNER_HZ: float
ATTEN_STEPS: tuple[float, ...]
LOW_BOOST_MAX_DB: float
LOW_ATTEN_MAX_DB: float
HIGH_BOOST_MAX_DB: float
HIGH_ATTEN_MAX_DB: float
BW_Q_BROAD: float
BW_Q_SHARP: float

def proportional_q(gain_db: float) -> float:
    """The bell Q the proportional law gives for `gain_db`.

    Reads the **magnitude** of the gain, never its sign. A law that read the
    signed gain would give a cut a different width from the matching boost
    and break T5's reciprocal at the skirts while the peak still looked
    right - the dossier names that as T5's way of failing.
    """

class ParametricEQ(_component.Component):
    """A Pultec at the ends and an API in the middle: the EQP-1A's two low
    networks and its resonant top, with three proportional-Q bells between.

    **Controls.** Low Freq is the corner for both low networks. Low Boost
    and Low Atten work at once: turn both up and you get the record trick,
    a lift at the bottom with a scoop just above it. Each bell has a Freq
    and a Gain; turn one up and its skirt stays where it is while the curve
    narrows, and its cut is the exact mirror of its boost. High Boost is a
    resonant bell at High Freq, and Bandwidth sets how sharp it is. High
    Atten is a separate shelf at Atten Freq. Q Law switches the bells from
    proportional to constant Q. Output is a gain after everything. The
    Effect controls page lists what the knobs span.

    **Response.** With every gain at 0 the class is a wire. A boost is
    delivered whole only while the signal has room for it; a cut always is.

    **Timing.** Latency is zero at every setting. Silence in settles to
    exact silence out.

    **Levels.** Keep the input under -12 dBFS and the defaults and patches
    stay off the rails. A boost or Output at its top can still push the
    output onto the rails.

    **On a board.** The class needs audiodsp's `audiobiquad`, and on a board
    without it construction raises `ImportError`.
    """

    NAME: str
    DISPLAY_NAME: str
    CATEGORIES: tuple[str, ...]
    VERSION: str
    TIER: str
    REQUIRES: tuple[str, ...]
    CAPABILITIES: tuple[str, ...]
    LATENCY_SAMPLES: int
    TAIL_SAMPLES: int
    INPUT_CEILING_DBFS: int
    CLIPS_AT_TOP: tuple[int, ...]
    MACRO_LABELS: tuple[str, ...]
    MACRO_MODES: dict[int, str]
    PATCHES: dict[int, tuple[str, tuple[float, ...]]]

    def __init__(
        self,
        source: _AudioSource,
        low_hz: float = 60.0,
        low_boost: float = 0.0,
        low_atten: float = 0.0,
        bell1_hz: float = 250.0,
        bell1_db: float = 0.0,
        bell2_hz: float = 1000.0,
        bell2_db: float = 0.0,
        bell3_hz: float = 4000.0,
        bell3_db: float = 0.0,
        bandwidth: float = 5.0,
        high_hz: float = 10000.0,
        high_boost: float = 0.0,
        atten_hz: float = 10000.0,
        high_atten: float = 0.0,
        q_law: float = 0.0,
        output_db: float = 0.0,
        patch: int | None = None,
        *,
        sample_rate: int | None = None,
        transport: _Transport | None = None,
    ) -> None: ...
    def reset(self) -> None:
        """Clear every section and restore patch 0, from the settings a
        fresh instance's sections hold: built, then the constructor's
        values, then patch 0. A section patch 0 leaves flat is only taken
        out (`mix` 0), so it kept the outgoing patch's corner, Q and gain,
        and a later move that brought it in moved from those instead of
        from a fresh section's."""
