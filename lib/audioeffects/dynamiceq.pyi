# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT
from typing import Any

from . import _component
from ._component import _AudioSource, _Transport

VENDOR: str

class DynamicEQ(_component.Component):
    """One EQ band that only moves when there is something in it.

    **What it does.** You dial in a bell the ordinary way, with Frequency
    and Width. It does nothing until the sound in that band crosses
    Threshold, and then it cuts the band as far as Ratio says. Everything
    outside the band is left as it was.

    **Idle, it is a wire.** Below the threshold the band and its complement
    add back to the input within 0.05 dB from 100 Hz to 12 kHz, and an
    impulse comes out at its own height.

    **The controls.** Frequency places the band, Width is its Q, Threshold
    is where the cut starts, Ratio is how far it cuts, and Attack and
    Release are how fast it moves. The Effect controls page lists what the
    knobs span and the patches.

    **The law.** At the default, a 3 kHz tone follows the compressor law
    within 1 dB, and across the bell the cut follows the closed form within
    0.5 dB. Two octaves down nothing moves by as much as 0.2 dB, idle or
    working.

    **Mix is the Range.** Mix also caps the deepest cut: at 0.75 the band
    can move by at most 12 dB, and at 1 there is no limit. Across Mix the
    cut follows that blend within 0.2 dB, and out of band nothing moves.
    Mix 0 is the source byte for byte, at full scale and at 48 kHz, 44.1
    kHz and 22.05 kHz. Bringing Mix back after silence plays nothing.

    **Listen.** Listen solos the band being processed.

    **Expand.** Build it with `expand=True` and it cuts the band when the
    band is quiet instead: over the threshold it is a wire within 0.1 dB,
    and 16 dB under it the band drops by more than 20 dB.

    **Sample rate and mono.** The law holds within 0.35 dB at 48 kHz,
    44.1 kHz and 22.05 kHz, and in mono. A Frequency above 0.4 of the
    running rate is built there, and `frequency_hz` says what you got.

    **Latency and tail.** It adds no latency at any setting. The tail
    reaches exact zero inside `tail_samples`, after a knob move too.

    It needs `audiobiquad`, `audiodynamics` and `audioroute`, so a stock
    CircuitPython board can't run it.
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
    WALKS_TO_BYPASS: bool

    def __init__(
        self,
        source: _AudioSource,
        frequency: float = 3000.0,
        q: float = 2.0,
        threshold_db: float = -30.0,
        ratio: float = 4.0,
        attack_ms: float = 2.0,
        release_ms: float = 80.0,
        mix: float = 1.0,
        listen: bool = False,
        expand: bool = False,
        patch: int | None = None,
        *,
        sample_rate: int | None = None,
        transport: _Transport | None = None,
    ) -> None: ...
    def reset(self) -> None:
        """Clear every node and restore patch 0, then hand the voices their
        sources at patch 0's levels, as `_build` does. The walk used to
        re-play them at the outgoing patch's levels, before patch 0 went
        in, so the levels moved after the gates had opened and landed late,
        a few LSB (up to 70 here) off a fresh instance for the first
        blocks."""

    @property
    def expand(self) -> Any:
        """Whether the band is cut when it goes *under* the threshold
        (`True`) rather than over it. Fixed at construction; see the class
        docstring for why it is not a macro."""

    @property
    def frequency_hz(self) -> Any:
        """The centre actually applied, after the rate clamp. It can sit
        below what `macro(0)` reports - that is the clamp doing its job at a
        lower sample rate."""

    @property
    def range_db(self) -> float:
        """The deepest the band can ever be moved, in dB, at this `Mix`.

        `-20*log10(1 - Mix)`, and `inf` at Mix 1. This is the Range control
        S6 names; it is not a separate macro because in an exactly
        complementary split a dry/wet blend and a band-range limit are the
        same arithmetic (dossier T6).
        """

    @property
    def tail_samples(self) -> int | None:
        """How long the split rings, in samples at this rate.

        The only memory in this class is the two biquads', and they share a
        denominator, so one pole pair sets it: the bound is read off the
        coefficients in force (`_component.biquad_ring`) and holds from any
        state the sections can hold, including what the settings before a
        move left in them. The old figure, 4 periods of `Q / f0` from a
        burst at fixed settings, was short after a large move down
        (audiocomponents#114). The float state is flushed to exact zero
        below 1e-20, so the tail really does arrive.

        The detector holds no audio: `audiodynamics` multiplies its input by
        a gain, so silence in is silence out whatever the release is doing,
        and the release therefore adds nothing here.
        """

    def gain_reduction_db(self) -> Any:
        """What the gain cell did to the last frame of the band, in dB.

        The cell's own number, before the Mix blend, so it is the detector's
        reading and not what reached the output. At blend `m` the output's
        move at the centre is `20*log10((1 - m) + m * 10**(cell/20))`.
        """
