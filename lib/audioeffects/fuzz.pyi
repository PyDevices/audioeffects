# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT
from typing import Any

from . import _component
from ._component import _AudioSource, _Transport

VENDOR: str
GERMANIUM_SCALE: float
GERMANIUM_CURVE: bytes
CASCADE_CURVE: bytes
HP_HZ: tuple[float, ...]
HP_PARK_HZ: float
CHARGE_BLOCKS: int
CHARGE_FRAMES: int
CASCADE_OUT_HP_HZ: float
HP_A_HZ: float
HP_A_Q: float
HP_B_HZ: float
HP_B_Q: float
TILT_HZ: float
TONE_LP_HZ: float
TONE_HP_HZ: float
BUTTER_Q: float
CHARACTERS: tuple[str, ...]
OVERSAMPLES: tuple[int, ...]
LEAN_PATCH: int
LEAN_OVERSAMPLE: int
GERMANIUM_OVERSAMPLE: int
CASCADE_OVERSAMPLE: int
MIXER_BUFFER_BYTES: int

def shipped_oversample(character) -> int:
    """The factor this character ships at: ×8 on `germanium`, ×2 on
    `cascade`. Chosen on cascade's own alias floor — see
    `CASCADE_OVERSAMPLE`, which has the numbers — and not on the maximum
    the node offers."""

class _MixAsLevel:
    """A node's `mix` under the name a mixer voice gives its level, so the
    walk to the dry and back can hold it the way it holds a voice. A Biquad
    and a Waveshaper walk a `mix` move over 20 ms. The Waveshaper takes its
    `mix` through `set()` and doesn't hand it back, so the last value set is
    kept here. Which one a node is gets asked once: a plain attribute
    assignment would land on a Python-level node without reaching it."""

    def __init__(self, node, level: float = 1.0) -> None: ...
    @property
    def level(self) -> Any: ...
    @level.setter
    def level(self, value: float) -> None: ...

class Fuzz(_component.Component):
    """Fuzz Face germanium, or a Ram's Head 1973 Big Muff as `cascade`.

    **Character.** `character` picks the pedal when you build it:
    `germanium` (the default) or `cascade`. On `germanium` the transistor
    sits off centre, so the fuzz leans even: at the default the second
    harmonic of a -20 dBFS 1 kHz tone is no more than 30 dB under it, and
    the even harmonics together no more than 26 dB. Turned up to 48 dB of
    Fuzz and past, both halves go square and the lean is gone. There is no
    tone stack on `germanium`: the band stays flat within 1 dB, and 40 Hz
    within 3 dB of 1 kHz.

    **Cascade.** `cascade` is two silicon pairs with a mid scoop between
    them. With Tone and Bias centred the scoop is more than 3 dB deep. From
    Fuzz 18 dB to 32 dB, Tone moves the scoop's centre over more than half
    an octave; from 34 dB up the clipper fills the scoop in.

    **Fuzz and Bias.** Fuzz is how hard the transistor is driven, and Bias
    moves it off centre. The Effect controls page lists what the knobs span
    and the patches. On `cascade` any Bias off centre is a gate on the
    level: it rails both pairs and the output falls away, while the scoop
    stays more than 3 dB deep. With Bias off centre the output settles near
    zero rather than on it, so the class declares no tail there.

    **Level, Load and Mix.** Level, Load and Mix set the volume, the load
    and the blend. Level 0 is digital silence at every Mix above 0, and
    halving Level takes 6.02 dB off at every Mix. Load 1 takes 6.02 dB off
    at every Mix. At Mix 0 the output is the source itself, at its own
    level, and the latency is 0.

    **Output Tilt.** Output Tilt tilts the balance of lows and highs.
    Nothing on the surface reaches the rail from 100 Hz to 3700 Hz, even at
    0 dBFS in.

    **Aliasing.** At 48 kHz and 44.1 kHz, at the default, the aliasing is at
    least 50 dB under a 1010 Hz tone and 35 dB under a 3700 Hz one. Nowhere
    else on the surface, Fuzz - lean aside, does it come closer than 35 dB
    and 28 dB. At 22.05 kHz that does not hold, because the fuzz's own
    harmonics fold back at the output rate.

    **Latency and tail.** `germanium` shapes at x8 and reports 4 samples of
    latency; `cascade` shapes at x2 and reports 2, and so does Fuzz - lean.
    With Bias centred the tail is 24576 samples.

    **Patches.** Alone on an ESP32-S3 the germanium default was measured at
    77 % of a block and the costliest patch at 78 %. Fuzz - lean shapes at
    x2 and was measured at 33 %, so play it when you stack effects.

    It needs `audioshaper`, `audiobiquad` and `audioroute`, so a stock
    CircuitPython board can't run it.
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
    WALKS_TO_BYPASS: bool

    def __init__(
        self,
        source: _AudioSource,
        fuzz_db: float = 36.0,
        level: float = 1.0,
        tone: float = 0.5,
        bias: float = 0.0,
        load: float = 0.0,
        mix: float = 1.0,
        tilt_db: float = 0.0,
        character: float | str = "germanium",
        oversample: bool | int | None = None,
        patch: int | None = None,
        *,
        sample_rate: int | None = None,
        transport: _Transport | None = None,
    ) -> None: ...
    @property
    def latency_samples(self) -> int: ...
    @property
    def tail_samples(self) -> int | None:
        """`TAIL_SAMPLES` with Bias centred or Mix at 0, and None anywhere
        else.

        Off centre the shaper answers silence with a constant, the coupling
        poles behind it settle into a wander of a few LSB rather than onto
        zero, and nothing bounds when (or whether) it stops: on `germanium`
        it was still there 6 s after the input at every Bias stop but the
        three either side of centre, and on `cascade` it settled at some
        stops and not at others. A bound there would be a guess, and the
        contract's None is the honest answer. Mix 0 is the dry alone, and
        the wander is not in it."""
