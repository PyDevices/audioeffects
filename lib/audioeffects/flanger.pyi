# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT
from . import _component
from ._component import _AudioSource, _Transport

VENDOR: str
RATE_I: int
RANGE_I: int
MANUAL_I: int
COLOR_I: int
MIX_I: int
POLARITY_I: int
SYNC_I: int
DIVISION_I: int
MAX_DELAY_MS: int
BLOCK: int
DIVISION_BARS: tuple[float, ...]
POLARITIES: tuple[str, ...]
SILENCE_DB: float
ECHO_TOLERANCE: float
PATCH_0: tuple[int, ...]
DEFAULTS: tuple[float, ...]
RATE: float
RANGE: float
MANUAL_MS: float
COLOR: float
MIX: float

def tail_frames(color, top_ms: float, rate: float) -> int:
    """Frames until the ring is exact silence, for Color `color` and a
    sweep whose top is `top_ms`, at `rate` (the card's section 5).

    Interpolation never exceeds its two samples and the feedback truncates
    toward zero, so the line's peak falls by at least g each D + 1 frames,
    and is zero once it would fall under one LSB."""

class Flanger(_component.Component):
    """A flanger: your signal plus a copy of itself a few milliseconds
    late, the delay swept up and down by a triangle, so the comb of notches
    the sum makes moves through the spectrum.

    **The controls.** Rate is the sweep's speed. Manual is the sweep's
    floor, and Range is how far it climbs from there towards 10 ms: at
    Range 0 the comb holds still at Manual. Color feeds the copy back into
    the line and raises the comb's peaks into a ring. Mix is the copy's
    level against a dry that never moves: 1 is equal weight and the deepest
    notches, 0 is a wire. Polarity minus turns the comb over and puts a
    notch at DC. With Sync on, one sweep lasts Division bars at the host's
    tempo and meter, and Rate is ignored. Constructor values play exactly
    until their knob first moves or a patch loads. The Effect controls page
    lists what the knobs span.

    **What you hear.** The copy is your signal exactly Manual late, added
    at Mix.
    At Color 0 and Mix 1 a tone on a notch comes out at least 40 dB down.
    Color raises the peaks by up to 26.4 dB over the input and fills the
    notches to 6 dB under it.
    The sweep is a triangle in milliseconds that starts at Manual and
    reaches its top once a sweep.
    The ring lasts about 0.4 s to -60 dB at 3 ms and full Color, and
    about 0.7 s at 5 ms; it grows as Range sweeps the delay longer, and it
    never oscillates on its own.

    **Limits.** It is linear only to about -28 dBFS on a resonant frequency
    at full Color, and -7.5 dBFS at Color 0: above that the output is
    squashed and gritty, not louder.
    Turning Mix up makes the output louder, by 6 dB on a comb peak at Mix 1:
    there is no wet-only setting.
    There is no tone control, no through-zero and no stereo spread: both
    channels sweep together.
    Sync sets the sweep's period, not its phase: the sweep starts at Manual
    when the class is built or reset, not on a bar line, and a synced sweep
    faster than 20 Hz runs at 20 Hz.
    A jump of Mix walks to its new setting over 20 ms rather than stepping
    the output. A jump of another control steps it: move that in small
    steps from the host if you need it smooth.
    At 22.05 kHz the sweep's top is 9.977 ms, half a frame under 10 ms.
    Mix's first step above 0 is still a wire; the copy comes in at the
    second step, about 36 dB down.
    Keep the input under -6 dBFS.

    **Wire, latency, tail.** At Mix 0 the output is the input, byte for
    byte.
    There is no latency.
    `tail_samples` is the longest the ring can last at the controls in
    force, while the source keeps playing, silence included.
    If the source ends, the output stops dead; `reset()` clears what the
    line held and returns to patch 0.
    On a CircuitPython board, stop the flanger from the host if your source
    can run dry: CircuitPython's own flanger waits on a source that comes
    back empty. Firmware built with omnipython-builds' build_mp.py
    carries the fix and returns.
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
    INPUT_CEILING_DBFS: float
    MACRO_LABELS: tuple[str, ...]
    MACRO_MODES: dict[int, str]
    PATCHES: dict[int, tuple[str, tuple[float, ...]]]

    def __init__(
        self,
        source: _AudioSource,
        rate: float = ...,
        depth: float = ...,
        manual_ms: float = ...,
        color: float = ...,
        mix: float = 1.0,
        polarity: str = "positive",
        sync: bool | float | None = False,
        division: float | None = 1.0,
        patch: int | None = None,
        *,
        sample_rate: int | None = None,
        transport: _Transport | None = None,
    ) -> None: ...
    def transport_changed(self) -> None:
        """With Sync on, follow the host's tempo and its meter: a move of
        either sets the sweep's rate again. The base follows the tempo
        alone, so a 4/4 to 3/4 change at one tempo would keep the old
        rate."""

    def macro(self, index: int) -> float:
        """What macro `index` currently stands for, in its own units; for
        the first five, the value that plays."""

    @property
    def tail_samples(self) -> int | None:
        """The bound at the controls in force; see the class docstring."""
