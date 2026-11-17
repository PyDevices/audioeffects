# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT
from typing import Any

from . import _component
from ._component import _AudioSource, _Transport

VENDOR: str
KEY_RING_CYCLES: float

class Expander(_component.Component):
    """A downward expander in the Drawmer DS201's shape: below the
    threshold, quiet passages get quieter, by a ratio you set and down to a
    floor you set, without the slam of a gate. Above the threshold it is a
    wire.

    **Controls.** Threshold is where the expansion starts. Ratio is
    how many dB the output falls for every dB the input falls below the
    threshold; with the RMS detector the slope stays within 5 % of it even
    at 8. Depth is the floor: a quiet passage falls no further than that,
    to within 0.5 dB. Ratio 1 and Depth 0 are each a wire, byte for byte.
    Attack and Release set how fast the detector follows the level. The
    Effect controls page lists what the knobs span.

    **The key.** Key Low and Key High, the top just under Nyquist, narrow
    the band the detector hears, at 12 dB/octave at each end, so a loud
    tone outside the band can still open it. Key Listen puts that band on
    the output so you can hear what the detector hears. Pass `key=` another
    stream and the detector reads that instead of your signal, the DS201's
    external key.

    **Detector.** RMS, the default, gives a sine and a square of equal RMS
    the same gain, to within 0.1 dB at Ratio 2 with the band wide open.
    Peak rides each cycle of the waveform, so the slope falls short of the
    ratio and the expander turns into a soft, slightly gritty gate; the
    Hard Downward patch is built on it.

    **No hold.** There is no Hold and no one-shot envelope: the expander
    follows the level continuously. For a gate with a trigger, use
    `NoiseGate`.

    **Timing.** Latency is zero at every setting. So is the tail, except
    with Key Listen on, when the key filters ring on after your signal
    stops: `tail_samples` bounds that ring, under 6000 frames at 48 kHz.

    **On a board.** The class needs audiodsp's `audiodynamics`, and on a
    board without it construction raises `ImportError`.
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
        threshold_db: float = -36.0,
        ratio: float = 1.5,
        depth_db: float = -20.0,
        attack_ms: float = 5.0,
        release_ms: float = 200.0,
        key_low_hz: float = 25.0,
        key_high_hz: float = 35000.0,
        key_listen: bool = False,
        detector_rms: bool = True,
        key: _AudioSource | None = None,
        patch: int | None = None,
        *,
        sample_rate: int | None = None,
        transport: _Transport | None = None,
    ) -> None: ...
    @property
    def tail_samples(self) -> int | None:
        """0, or with Key Listen on a bound on the key filters' ring.

        Each key filter is a two-pole section. From a state near full scale
        it is under half an LSB after about `KEY_RING_CYCLES` / fc seconds,
        and the two add, so the bound is the sum at Key Low and Key High as
        they stand.
        """

    def gain_reduction_db(self) -> Any:
        """What the gain computer applied on the last frame rendered, in dB.

        The node's own readout, forwarded. Not part of the component
        contract - a meter, and the measurement kit's GAINTRACE source.
        """
