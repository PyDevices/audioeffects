# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT
from . import _component
from ._component import _AudioSource, _Transport

VENDOR: str

class Limiter(_component.Component):
    """Brickwall limiting against a ceiling, with optional lookahead and
    true-peak detection.

    **Ceiling and Gain.** Ceiling sets the level nothing gets past. Gain
    drives the signal into it, and below the ceiling it is exactly the gain
    it says, within 0.1 dB. Below the ceiling nothing else is touched: the
    level holds within 0.05 dB, and at Ceiling 0 dB with no Gain the
    limiter is a wire. The Effect controls page lists what the knobs span
    and the patches.

    **Lookahead.** Lookahead defaults to 0 ms, so out of the box the
    limiter adds no latency. With it on, the latency is the lookahead in
    whole samples, up to 480 samples at 48 kHz and 220 at 22.05 kHz, and
    the host is told the moment you move it. A short burst stays within 0.1
    dB of the ceiling at every Lookahead setting, and a single-sample spike
    is caught at every setting from 0.5 ms up. Lengthening the lookahead
    while audio plays inserts that much silence; it never replays old
    audio.

    **Release is the distortion knob.** The gain follows the signal sample
    by sample, so a fast release distorts low notes. Release is how fast
    the gain recovers, and a 60 Hz sine driven 12 dB into the ceiling
    measures 12.0 % THD at the 5 ms end of the Release macro.
    The default patch sits at 149 ms and 0.71 %, under 1 % at 48 kHz and
    44.1 kHz.

    **True Peak.** Off, the ceiling holds on the samples, and a peak between
    two samples can rise more than 2.5 dB over it. On, with any lookahead at
    all, the waveform between the samples stays within 0.5 dB of the ceiling
    at 48 kHz and 44.1 kHz. On with Lookahead 0 it is a sample ceiling only:
    a full-scale ramp gets more than 2 dB past it, because a peak between
    samples can't be caught with no delay to catch it in. True Peak adds no
    latency of its own.

    **Knee.** At Knee 0 the ceiling is a brickwall. Knee softens the bend,
    and at 12 dB the bend is more than 4 dB wide.

    **Stereo.** The two channels are always limited together, so the image
    doesn't wander when one side is loud. A mono source is limited on its
    own channel.

    **Patches.** Catch The Peaks, Delivery Ceiling and Loud (True Peak)
    turn True Peak on, and an ESP32-S3 can't keep up with them: both stages
    with True Peak on were measured at 6.550 ms of work in a 5.333 ms
    block, and the sound breaks up. Play Delivery Ceiling - lean there
    instead. It keeps Delivery Ceiling's lookahead and release, turns True
    Peak off and sits 3 dB lower, and a worst-phase tone driven 6 dB into
    it stays under -0.94 dB even between the samples.

    Latency is the lookahead, and so is the tail. It needs `audiodynamics`,
    so a stock CircuitPython board can't run it.
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
    BRICKWALL_RATIO: float
    TRUE_PEAK_OVERSAMPLED: int
    TRUE_PEAK_RESERVE_SAMPLES: int

    def __init__(
        self,
        source: _AudioSource,
        ceiling_db: float = -1.0,
        gain_db: float = 0.0,
        lookahead_ms: float = 0.0,
        release_ms: float = 150.0,
        true_peak: bool = False,
        knee_db: float = 0.0,
        patch: int | None = None,
        *,
        sample_rate: int | None = None,
        transport: _Transport | None = None,
    ) -> None: ...
    @property
    def latency_samples(self) -> int:
        """The lookahead, in samples: 0 unless the Lookahead macro has been
        moved off zero."""

    @property
    def tail_samples(self) -> int | None:
        """The same number. The only thing this class holds after its input
        goes silent is whatever is still in the lookahead delay; there is no
        reverberant or feedback state anywhere in it."""
