# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT
from typing import Any

from . import _component
from ._component import _AudioSource, _Transport

VENDOR: str

class BandPass(_component.Component):
    """A resonant band-pass: the band around the centre comes through and
    the rest falls away.

    **Controls.** Frequency is the centre. Width is how wide the band is,
    and narrowing it changes what gets through, never how loud the centre
    is. Slope on puts a second section behind the first, for steeper skirts
    at the same width. Mix at 0 is your dry signal. The Effect controls page
    lists what the knobs span.

    **Response.** The centre stands at 0 dB at every width, except a tenth
    of a decibel low at 31.5 Hz with the band at its narrowest. DC and the
    top of the band are cut to exact zero.

    **Timing.** Latency is zero at every setting. Silence in settles to
    exact silence out. A hard jump in Frequency or Width rings out as a
    click; move the knob in steps and it sweeps.

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
    MACRO_LABELS: tuple[str, ...]
    MACRO_MODES: dict[int, str]
    PATCHES: dict[int, tuple[str, tuple[float, ...]]]

    def __init__(
        self,
        source: _AudioSource,
        frequency: float = 1000.0,
        q: float = 0.707,
        sections: int = 1,
        mix: float = 1.0,
        patch: int | None = None,
        *,
        sample_rate: int | None = None,
        transport: _Transport | None = None,
    ) -> None: ...
    @property
    def centre_hz(self) -> Any:
        """The centre frequency in force, after the rate's own clamp."""

    @property
    def bandwidth_hz(self) -> Any:
        """`Width` as the -3 dB bandwidth it stands for, `f0 / Q`. The knob
        stores Q, because Q is what the node takes and what the dossier's T2
        is stated in; this is the number a panel shows."""

    @property
    def sections(self) -> int:
        """1 or 2 - how many band-pass sections are in the path."""

    @property
    def tail_samples(self) -> int | None:
        """The ring time of *this* build, not a class constant.

        A band-pass is a resonator, so its tail is set by its poles: the
        sections' working Q at the centre in force, one section or the two
        of the steep slope (`_component.biquad_ring`). The bound holds
        from any state the sections can hold, including what the settings
        before a move left in them. A host told the surface's worst case at
        every setting would allocate 13 s for a filter nobody asked for.
        """
