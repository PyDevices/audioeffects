# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT
from . import _component
from ._component import _AudioSource, _Transport

VENDOR: str
MIN_Q: float
MAX_Q: float
HARMONIC: float
CENTRE_CEILING: float
TRIM_CORNER_HZ: float
TRIM_Q: float
FLAT_DB: float

class Notch(_component.Component):
    """A notch: one band taken out, and the rest of the signal left alone.

    **Controls.** Frequency is where the notch sits. Width is its
    bandwidth: low, the notch is a wide scoop; high, it is a few hertz
    across and you hear a tone leave without hearing the music change.
    Harmonics adds a second notch an octave up, as narrow in hertz as the
    first, for hum that comes as a series. Depth is a blend, and at 0 the
    class is a wire. Trim is a flat gain. The Effect controls page lists
    what the knobs span.

    **Response.** DC and the top of the band pass untouched. At low centres
    the notch is shallower: there it reduces a hum rather than removing it.

    **Timing.** Latency is zero at every setting. Silence in settles to
    exact silence out.

    **Levels.** Keep the input under -6 dBFS and the defaults and patches
    stay off the rails. Trim at its top can still push the output onto the
    rails.

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
        frequency: float = 1000.0,
        q: float = ...,
        harmonics: float = 1,
        depth: float = 1.0,
        trim_db: float = 0.0,
        patch: int | None = None,
        *,
        sample_rate: int | None = None,
        transport: _Transport | None = None,
    ) -> None: ...
    @property
    def tail_samples(self) -> int | None:
        """The ring time of *this* build: the sections in circuit, each
        bounded from its coefficients in force (`_component.biquad_ring`),
        summed down the cascade. The bound holds from any state the
        sections can hold, including what the settings before a move left
        in them (audiocomponents#114). A section a Depth of 0 or the
        Harmonics switch has taken out passes its input through and adds
        nothing."""
