# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT
from . import _component
from ._component import _AudioSource, _Transport

VENDOR: str
SELF_OSCILLATION: float
RING_CONSTANT: float
RING_RATE: float
RING_FLOOR: float
RING_SLOWEST: float

def ring_frames(
    sample_rate: int,
    cutoff_hz: float,
    resonance,
    drive: float,
    poles: int = 4,
    oversample: int = 2,
    output_gain: float = 1.0,
    mix: float = 1.0,
) -> int | None:
    """Frames from the input's end until the ladder's output is exactly
    zero, as an upper bound, or `None` from Resonance 4 up and in the
    narrow band just below it where the slowest decay per step is under
    `RING_SLOWEST`. At Mix 0 the output is the input, so the count is 0 at
    any Resonance.

    Each stage is a bilinear one-pole, so the zero-delay loop's poles are
    the analog ladder's, mapped by z = (1 + t p) / (1 - t p), t being the
    prewarped tan(pi fc / rate). For a pole p, 1 - |z|^2 is
    -4 t Re(p) / |1 - t p|^2, and half of that is a per-step decay rate no
    faster than the true one. The slow pair's -Re(p) = 1 - k^(1/4)/sqrt(2)
    is worked out as (4 - k) / 4 over (1 + q/sqrt(2))(1 + q^2/2), q being
    k^(1/4), so it keeps its digits near 4 in single precision too.

    No integrator holds more than `drive` plus 2/3 of the Resonance (the
    saturator's ceiling) times max(1, t) times max(1, 2g)^3, and the output
    rounds to exact zero under 0.5 / (32768 gain mix). The envelope
    (`RING_CONSTANT`) then gives the count. This is the linear ladder's
    decay; the saturator only lowers the loop's gain, and that it does not
    slow the ring is measured, not derived."""

class LadderFilter(_component.Component):
    """A Moog transistor ladder: four filter stages round one feedback loop,
    with a saturator inside the loop.

    **Controls.** Cutoff is the filter's corner, held just under half the
    sample rate. Resonance is the loop's feedback. As it rises the cutoff
    sharpens and the whole passband sinks, about 14 dB by a Resonance of 4:
    that droop is the circuit's sound, not a fault. From 4 up, the filter
    sings a sine of its own at the cutoff, and once it has heard anything
    it keeps singing after your signal stops. Drive is how hard the
    saturator is hit, so the growl follows your input level the way it does
    in the hardware. Passband Comp puts the sunk passband back: at 1 the
    passband holds its level at any Resonance. Poles picks the output from
    one to four poles. Oversample runs the loop at twice the rate; it is on
    by default, and the Ladder - lean patch is Wide Open with it off, for
    slower boards. Mix at 0 is your dry signal. A jump of Cutoff,
    Resonance, Drive, Passband Comp or Mix walks there over 20 ms rather
    than stepping the output. The Effect controls page lists what the knobs
    span.

    **Response.** At 48 kHz the four-pole output is 12 dB down at the cutoff
    and about 50 dB down two octaves above it, and each pole fewer takes
    about 12 dB off that.

    **Timing.** Latency is zero at every setting, Oversample included. Below
    a Resonance of 4, silence in is silence out once the filter rings down:
    Wide Open's tail is under a millisecond and Growl With Drive's about
    285 ms. `tail_samples` is an upper bound on that ring for the settings
    as they stand; at the slowest settings it is about twice the ring
    measured. From 4 up the tone does not stop by itself, so the class
    reports no tail bound, and none either in the hair below 4 where the
    ring outlasts what single precision can count (from Resonance 3.988 at
    a 20 Hz cutoff, nearer 4 above it). `reset()` stops it at any setting.

    **Levels.** The resonance peak and the drive both add gain, so no input
    level is clean on every setting. Keep the input under -15 dBFS and the
    defaults and patches stay off the rails. Drive at its top can still push
    the output onto the rails. Turn Drive, Resonance or your input down.

    **On a board.** The class needs audiodsp's `audioladder`, and on a board
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
    TAIL_SAMPLES: int | None
    INPUT_CEILING_DBFS: int
    CLIPS_AT_TOP: tuple[int, ...]
    MACRO_LABELS: tuple[str, ...]
    MACRO_MODES: dict[int, str]
    PATCHES: dict[int, tuple[str, tuple[float, ...]]]

    def __init__(
        self,
        source: _AudioSource,
        cutoff_hz: float = 12000.0,
        resonance: float = 0.6,
        drive_db: float = 0.0,
        passband_comp: float = 0.0,
        poles: int = 4,
        oversample: bool | int | None = True,
        mix: float = 1.0,
        patch: int | None = None,
        *,
        sample_rate: int | None = None,
        transport: _Transport | None = None,
    ) -> None: ...
    @property
    def tail_samples(self) -> int | None:
        """Frames until the output is exactly zero once the input stops, as
        an upper bound for the settings as they stand, or `None` from a
        Resonance of 4 up, where the filter sustains, and just below it
        where single precision cannot show the decay (`ring_frames`)."""
