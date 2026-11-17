# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT
from typing import Any

from . import _component
from ._component import _AudioSource, _Transport

VENDOR: str
MIN_CROSSOVER_RATIO: float

class MultibandCompressor(_component.Component):
    """Split-band compression: the mix split into two or three bands, each
    with its own compressor, then summed back flat. Use it when one
    compressor on the whole mix lets the bass pump everything else.

    **Bands.** Build it with `bands=2` or `bands=3`; nothing else is
    accepted. The splits are Crossover Low and Crossover High. Crossover
    High is held at least eight times Crossover Low: ask for less and it
    moves up rather than refusing, and `crossover_high_hz` reports where it
    landed. At two bands the split is at Crossover Low, the upper band uses
    the High macros, and Crossover High and the three Mid macros do
    nothing, which `macro_is_live()` reports.

    **Flat at rest.** With every Ratio at 1 the bands sum to within 0.25 dB
    of the input from 30 Hz to 16 kHz, at two bands and at three. Each
    band alone is 6 dB down at its corner, within 0.5 dB.

    **Each band.** The bands have a Threshold, a Ratio and a Gain apiece,
    and Attack and Release are shared across the bands. Driving one band to
    12 dB of reduction moves the middle of that band by 12 dB, within 0.5
    dB, and the other bands by under 0.5 dB. Towards its own corners a band
    compresses less than you dialled, so dial the number you want for the
    middle of the band. The Effect controls page lists what the knobs span
    and the patches.

    **Mix.** Mix crossfades the input with the summed bands, so between its
    stops it is parallel compression. Mix 0 is the source byte for byte, at
    22.05 kHz, 44.1 kHz and 48 kHz, mono and stereo, and moving off it does not
    click. Brought back up from 0, it starts as it was built rather than
    playing what the bands held. Keep the input under -9 dBFS and the defaults
    and patches stay off the rails. A band's Gain at its top can still push the
    output onto the rails.

    **Latency and tail.** It adds no latency at any setting. The tail
    reaches exact zero, and `tail_samples` says when.

    **Patches.** Master Glue is the constructor's defaults.

    **Boards.** At three bands its costliest patch was measured at 54 % of a
    block on an ESP32-P4 and 107 % on an ESP32-S3, so the S3 can't keep up.
    Built with `bands=2` it was 34 % and 71 %, so on an S3 build it that
    way. It needs `audiobiquad`, `audiodynamics` and `audioroute`, so a
    stock CircuitPython board can't run it.
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
    INPUT_CEILING_DBFS: int
    CLIPS_AT_TOP: tuple[int, ...]
    MACRO_LABELS: tuple[str, ...]
    MACRO_MODES: dict[int, str]
    PATCHES: dict[int, tuple[str, tuple[float, ...]]]
    WALKS_TO_BYPASS: bool

    def __init__(
        self,
        source: _AudioSource,
        bands: int = 3,
        crossover_low_hz: float = 200.0,
        crossover_high_hz: float = 2000.0,
        low_threshold_db: float = -18.0,
        mid_threshold_db: float = -18.0,
        high_threshold_db: float = -18.0,
        low_ratio: float = 3.0,
        mid_ratio: float = 3.0,
        high_ratio: float = 3.0,
        low_gain_db: float = 0.0,
        mid_gain_db: float = 0.0,
        high_gain_db: float = 0.0,
        attack_ms: float = 10.0,
        release_ms: float = 150.0,
        mix: float = 1.0,
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
    def bands(self) -> Any:
        """2 or 3, as the constructor was asked for. It is not a macro: see
        the class docstring."""

    @property
    def crossover_low_hz(self) -> Any:
        """The lower corner actually applied, after the Nyquist clamp."""

    @property
    def crossover_high_hz(self) -> Any:
        """The upper corner actually applied, after the eight-to-one clamp
        and the Nyquist clamp; `None` at two bands, where there is no upper
        crossover. It can sit above the Crossover High macro's own value -
        that is the clamp doing its job, and `macro(1)` still reports what
        was asked for."""

    @property
    def tail_samples(self) -> int | None:
        """How long the crossover rings, in samples at this rate.

        The only memory in this class is the biquads': the detectors hold an
        envelope and no audio, and neither the Mixer nor the Splitter holds a
        line. The lowest corner is the slowest, and a float recursion flushed
        to zero below 1e-20 really does arrive - measured, one LR4 half at
        40 Hz rings for 2.90 periods of its corner and one at 100 Hz for
        2.88, from a full-scale DC burst.
        """

    def macro_is_live(self, index: int) -> Any:
        """Whether macro `index` does anything at this band count. Every
        macro is live at three bands; at two, Crossover High and the three
        Mid macros are not."""

def audiomixer_mixer(rate: float, channels, voices) -> Any:
    """The summing node, imported at call time.

    `audiomixer` is a ported CircuitPython module and is on every build this
    library runs on, so it is not in `REQUIRES`; it is imported here rather
    than at module level only to keep the guarded audiodsp imports together
    at the top.
    """
