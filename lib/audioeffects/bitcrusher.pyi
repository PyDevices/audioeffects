# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT
from array import array
from typing import Any

from . import _component
from ._component import _AudioSource, _Transport

VENDOR: str
STAND_RATE_HZ: float
DESIGN_FS: float
MIN_RATE_HZ: float
MAX_BITS: int
CURVE_POINTS: int
CURVE_STEP: int
DITHER_FRAMES_A: int
DITHER_FRAMES_B: int
DITHER_PEAK: int
DITHER_GATE_DB: float
DITHER_GATE_HOLD_MS: float
DITHER_GATE_RELEASE_MS: float
DITHER_GATE_PEAK: float
BAND_SECTIONS: int
BAND_QS: tuple[float, ...]
BAND_FRACTION: float
MIN_Q: float
MAX_Q: float
CURVE_BYTES: bytes
CURVE: array[int]

class Bitcrusher(_component.Component):
    """12-bit linear hold: Bits and Rate, informed by the SP-1200.

    **Bits.** Bits is the word length, and 12 is the SP-1200's own. Every
    depth rounds to the nearest step rather than down, and none is a wire.
    Each step is rounded over a short ramp, so at 12 bits the error is half
    a hard converter's, and it follows that law within 10 %.

    **Rate.** Rate is how fast the hold samples. The hold lands on the
    whole hertz you ask for and never drifts. At the default, at least 99 %
    of its runs are one or two samples long. Its images stand within 3 dB
    of their own level, which is the sound of the knob; above the hold's
    own Nyquist they read between 3 dB and 8 dB down. A single-sample event
    can fall between two held samples and vanish: about 46 % of them do at
    the default at 48 kHz.

    **The running rate.** Asking for the running rate is a pass-through, and
    the latency is then 0. Above it Rate clamps, and `hold_rate_hz` says what
    you got where the macro says what you asked: at 22.05 kHz the default
    clamps, and the top of the knob is the same pass-through. Otherwise the
    latency is the hold's displacement, 1 sample at the default at 48 kHz,
    plus the band limit's when it is on, and the host is told.

    **Band Limit.** Band Limit is a switch, off by default. On, it puts a
    low-pass in front of the hold that takes the images more than 20 dB
    down, without muting what is under it, and the tail becomes 640
    samples.

    **Dither.** Dither is off by default. It is gated on the input, so
    silence in is silence out at every patch, and at its top it fades
    inside the declared tail. At a deep crush with Dither at its top the
    dither holds its own gate open: it plays on silence, and the class
    declares no tail.

    **Mix and Output.** Mix 0 is a wire at the source's own level. Output
    trims the whole blend: -6 dB is 6 dB down within 0.1 dB, at Mix 1 and
    at a blend. Keep the input under -3 dBFS and the defaults and patches
    stay off the rails. The Effect controls page lists what the knobs span
    and the patches.



    It needs `audioshaper`, `audiobiquad`, `audioroute` and `audiodynamics`,
    so a stock CircuitPython board can't run it.
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
    MACRO_LABELS: tuple[str, ...]
    MACRO_MODES: dict[int, str]
    PATCHES: dict[int, tuple[str, tuple[float, ...]]]
    WALKS_TO_BYPASS: bool

    def __init__(
        self,
        source: _AudioSource,
        bits: float = 12.0,
        rate_hz: float = 26040.0,
        dither: float = 0.0,
        band_limit: float = 0.0,
        mix: float = 1.0,
        output_db: float = 0.0,
        patch: int | None = None,
        *,
        sample_rate: int | None = None,
        transport: _Transport | None = None,
    ) -> None: ...
    def reset(self) -> None:
        """Clear every node and restore patch 0, then arm the graph as
        `_build` does, lazily, so a reset is a fresh instance and takes
        nothing from the source."""

    @property
    def hold_rate_hz(self) -> Any:
        """The hold rate this class actually got, in hertz.

        Rate says what you asked for; this says what runs. They differ in
        two places a user can stand: **Rate above the running rate clamps**
        (a hold cannot invent frames), which at 22.05 kHz makes the top
        four of the knob's seventeen MIDI stops -- and patch 0's own hold --
        an identity; and the asked rate is rounded to the whole hertz so the
        ratio can be exact. `audioshaper.SampleHold` reduces the pair, so
        this is `sample_rate * den / num` off the node itself rather than
        the class's arithmetic repeated.
        """

    @property
    def latency_samples(self) -> int:
        """The hold's worst-case displacement, in samples.

        The DSP has no lookahead and no filter in the reported path, and
        `SampleHold.latency` is 0 at every ratio: a refresh latches the
        frame it is looking at and emits it in the same frame. What a click
        probe reads is not 0, because a hold decimates: an event lands on
        the next kept frame and can arrive up to `ceil(num/den) - 1` frames
        late. That bound is read off the node's own reduced pair -- 1 at the
        default at 48 and 44.1 kHz, 0 at 22.05 kHz where Rate clamps, 0 at
        Mix 0. Reporting it is what makes the declaration and the probe the
        same statement.

        **The band limit has its own delay and the bound did not carry
        it.** Its two `Biquad` sections are minimum phase and their group
        delay lands on top of the hold's displacement: shipped patch 3
        measured **2 to 8 samples over 120 offsets at 48 kHz against a
        declared 6**, and 2 to 7 against 5 at 44.1 kHz (audit 3 (p)5, G7).
        `BAND_LATENCY_SAMPLES` is what those sections add, measured the
        same way, and it is in the bound whenever the band limit is in
        circuit.
        """
    BAND_TAIL_SAMPLES: int
    BAND_LATENCY_SAMPLES: int
    DITHER_TAIL_SAMPLES: int

    @property
    def tail_samples(self) -> int | None:
        """0, the band limit's 640, or the dither gate's 9 728, and None
        where the dither is louder than the gate's threshold.

        The gate's threshold is a level, `DITHER_GATE_DB`, and the dither's
        peak is Dither's LSB at the depth in force. Past +-32 counts (12
        bits at maximum Dither, 11 bits at 1 LSB, and every deeper crush
        above that) the dither alone holds the gate open, so it plays on
        silence for good and no bound is true."""
