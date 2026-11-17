# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT
from . import _component
from ._component import _AudioSource, _Transport

VENDOR: str
TUBE_CURVE: bytes
TAPE_CURVE: bytes
IRON_CURVE: bytes
CHARACTERS: tuple[str, ...]
OVERSAMPLES: tuple[int, ...]
LEAN_PATCH: int
OVERSAMPLE_RATE_HZ: float
NODE_CEILING: float
MAKEUP_SHELF_HZ: float
MIXER_BUFFER_BYTES: int
CHARGE_FRAMES: int
BIAS_STEPS: int
TUBE_BIAS_REACH: float
HELD_BY_THE_PLAY_OPERATOR: tuple[int, ...]
TILT_HZ: float
PLATE_HZ: float
FLUX_HZ: float
LOSS_HZ_AT_15: float
SPEED_REF: float
BUTTER_Q: float
TUBE_PRE0: float
TUBE_MAKEUP: float
TAPE_PRE0: float
TAPE_MAKEUP: float
IRON_PRE0: float
IRON_MAKEUP: float
DRIVE_CEILING_DB: float
CONSOLE_EXTRA_SAMPLES: float
CLICK_ONSET_SAMPLES: dict[tuple[int | str, ...], int]

def shipped_oversample(sample_rate: int) -> int:
    """The factor this rate ships with: x4 at 48 and 44.1 kHz, x2 at 22.05.

    Taken from the alias floor at each factor rather than from a rule of
    thumb — the numbers are at `OVERSAMPLE_RATE_HZ`. Above x4 the floor at
    every supported rate is harmonic fold-back, which is the base rate's
    Nyquist and not the oversampler's business, so the factors above it are
    S3 block for nothing.
    """

class Saturation(_component.Component):
    """A 12AX7 stage, a tape machine, or transformer iron.

    **Character.** `character` picks the stage when you build it: `tube`
    (the default), `tape` or `console`. On `tube` the second harmonic leads
    the third by more than 15 dB from -26 dBFS to -6 dBFS, and by more than
    20 dB at -6 dBFS. On `tape` the curve is odd: at the default the second
    harmonic of a -12 dBFS tone stays 40 dB under it. `console` is
    transformer iron, and it saturates from the bottom up.

    **Drive and Headroom.** Headroom is Drive spent the other way round,
    and the two share one ceiling: Drive less Headroom stops at +15 dB
    however you reach it.

    **Aliasing.** At 48 kHz on `tube` the aliasing stays more than 60 dB
    under a 1010 Hz or a 3700 Hz tone, at the default and at full Drive, and
    at every Headroom down to -12 dB. That is a ratio, so wherever the output
    is quiet it reads worse, one dB for one, and `console` at Drive 0 dB
    does not reach it.

    **Output and Mix.** Output's +3, +6, +9 and +12 dB come out within 0.25
    dB of what they say. At the default the stage takes level away: a -12
    dBFS 1 kHz tone comes out about 8 dB down on `tube`, 13 dB on `tape`
    and 33 dB on `console`, and Output is what puts it back. With every
    macro at its top a full-scale input can clip. Mix runs from the dry
    signal at 0 to the stage at 1, and it is a blend: the level never rises
    on the way and there is no notch. At Mix 0 the output is the source
    itself and the latency is 0.

    **Bias.** Bias moves the stage's operating point. Every position
    sounds: none takes more than 12 dB off the level at Bias 0, and none
    wanders more than 1 dB once it has settled. Silence in is silence out
    at every Bias and every patch.

    **Speed, Tilt and Hysteresis.** Speed is the tape's, in inches a
    second, and slides its playback loss; on `tube` it changes nothing.
    Tilt tilts the balance about 1 kHz. Hysteresis is off by default. The
    Effect controls page lists what the knobs span and the patches.

    **Latency and tail.** The rate picks the oversampling: x4 at 48 kHz and
    44.1 kHz, x2 at 22.05 kHz. At x4 the latency is 1 sample on `tube`, 2 on
    `tape` and 4 on `console`, and the host is told. After a burst every
    patch is back to silence within the declared tail of 65536 samples.

    **Patches.** Alone on an ESP32-S3 the class was measured at 55 % of a
    block at its default patch and 56 % at its costliest. Saturation - lean
    runs one oversampling factor lower and was measured at 40 %, so play it
    when you stack effects.

    It needs `audioshaper`, `audiobiquad`, `audioroute` and `audioecho`, so
    a stock CircuitPython board can't run it.
    """

    LAZY_BUILD: bool
    WALKS_TO_BYPASS: bool
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
        drive_db: float = 0.0,
        output_db: float = 0.0,
        mix: float = 1.0,
        headroom_db: float = 0.0,
        bias: float = 0.0,
        speed_ips: float = 15.0,
        tilt_db: float = 0.0,
        hysteresis: float = 0.0,
        character: float | str = "tube",
        oversample: bool | int | None = None,
        patch: int | None = None,
        *,
        sample_rate: int | None = None,
        transport: _Transport | None = None,
    ) -> None: ...
    def reset(self) -> None:
        """Clear every node and come back as `_build` leaves a fresh
        instance at patch 0.

        The walk clears the mixer first (it is registered last), and its
        voices used to be re-played there: a play primes a voice with a
        block of its source, so the wet voice took one from a chain the
        walk had not cleared yet and the first block after the reset was
        the old audio, 1504 LSB at the defaults. Here the voices are
        stopped, the patch goes in with the graph unarmed, and the graph is
        armed the way `_build` arms it: the shapers re-pointed, the level
        gates opened, then the voices played.
        """

    @property
    def latency_samples(self) -> int: ...
