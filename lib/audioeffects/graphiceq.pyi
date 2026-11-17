# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT
from collections.abc import Sequence
from typing import Any

from . import _component
from ._component import _AudioSource, _Transport

VENDOR: str
DEFAULT_CENTRES: tuple[float, ...]

def band_q(gain_db: float, anchor: float) -> float:
    """The Q a band of `gain_db` gets, for a bank anchored at `anchor`.

    `ParametricEQ`'s proportional-Q law, rearranged so the anchor is the
    macro: holding the +/-1 dB skirt at one frequency while the peak grows
    means `Q(G) = anchor * sqrt((A^2 - L^2/A^2) / (A12^2 - L^2/A12^2))` with
    `A = 10^(|G|/40)`. Below +1 dB there is no root -- a 1 dB skirt cannot sit
    on a 1 dB bell -- and Q floors at the kernel's own minimum, which is the
    limit of the law rather than a special case.
    """

class GraphicEQ(_component.Component):
    """A ten-band octave graphic EQ after the MXR M-108: nine bells and a
    top shelf, between a Gain and a Volume slider.

    **Bands.** The bands sit an octave apart from 31.25 Hz to 8 kHz, and
    the top one is a shelf at 16 kHz. At its centre detent a band is out of
    the circuit, so a flat bank is the source byte for byte. A band brought
    back from the detent starts from nothing. `centres=` retunes the bank
    to ten ascending frequencies, and the shelf stays the top band.

    **Band Q and Constant Q.** As on the pedal, a band narrows as its
    slider travels. Band Q is its width at full travel, and it is wider
    than that a few dB in. Constant Q holds every band at Band Q at every
    setting.

    **Gain and Volume.** Gain sits before the bank and Volume after it.
    Each moves every frequency alike, within 0.15 dB. The Effect controls
    page lists what the knobs span and the patches.

    **Level.** Bands overlap and add: three adjacent sliders at +6 dB lift
    the middle one's frequency by more than 7 dB. Every section hands the
    next an int16, so leave headroom, and pull Volume down when you push
    Gain up. A band, Gain or Volume at its top can push a full-scale input
    onto the rails.

    **Patches.** Scooped Mids, Pushed Mids and Full Boost pull Volume down,
    so stepping through them you hear the curve rather than the level. A
    patch change starts the bank clean and doesn't overshoot; a knob move
    rides through.

    **Sample rate.** At 48 kHz and 44.1 kHz every band is where its label
    says. At 22.05 kHz the 16 kHz shelf is past Nyquist, so it is built
    just under it and `clamped` says so.

    **Latency and tail.** It adds no latency at any setting. Silence in is
    exact zero out, and `tail_samples` bounds the ring for the settings in
    force, after a knob move too. A mono source gets the same curve.

    It needs `audiobiquad`, so a stock CircuitPython board can't run it.
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
    CLIPS_AT_TOP: tuple[int, ...]
    MACRO_LABELS: tuple[str, ...]
    MACRO_MODES: dict[int, str]
    PATCHES: dict[int, tuple[str, tuple[float, ...]]]

    def __init__(
        self,
        source: _AudioSource,
        gains_db: Sequence[float] | None = None,
        gain_db: float = 0.0,
        volume_db: float = 0.0,
        band_q: float = 2.0,
        constant_q: bool = False,
        centres: Sequence[float] | None = None,
        patch: int | None = None,
        *,
        sample_rate: int | None = None,
        transport: _Transport | None = None,
    ) -> None: ...
    @property
    def tail_samples(self) -> int | None:
        """The ring time of *this* build: Gain, the ten bands and Volume,
        each section in circuit bounded from its coefficients in force
        (`_component.biquad_ring`) and summed down the chain. The bound
        holds from any state the sections can hold, including what the
        settings before a move left in them: a Gain or Volume move from the
        top to the bottom as the input stopped rang 10 to 20 % past the old
        fixed 0.47 s (audiocomponents#114). A flat section is a wire and
        adds nothing.
        """

    @property
    def centres(self) -> Any:
        """The band centres this instance was asked for, in Hz."""

    @property
    def built_centres(self) -> Any:
        """What is actually in the filters: nine bell centres and, in the
        tenth slot, the **shelf's half-gain corner** -- half an octave below
        its named band, so the band gets 10.91 dB of a 12 dB request rather
        than 6.00.

        At a rate too low to hold the top of the bank the values are clamped
        as well: at 22.05 kHz the shelf's corner sits at 10804.5 Hz rather
        than 11313.7. `clamped` says which, so a caller reads the clamp
        rather than inferring it from a response it did not ask for.
        """

    @property
    def clamped(self) -> Any:
        """The indexes of the bands whose centre was clamped below Nyquist.

        Empty at 48 kHz and 44.1 kHz. The old class dropped those bands
        silently instead; nothing said so, which is absence reading as
        agreement.
        """
