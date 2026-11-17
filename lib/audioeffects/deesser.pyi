# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT
from typing import Any

from . import _component
from ._component import _AudioSource, _Transport

VENDOR: str

class DeEsser(_component.Component):
    """De-essing by comparing the sibilant band with the programme.

    **No threshold.** It listens to how loud the "s" band is against the
    whole track and ducks only when the band comes too close, so one setting
    works on a whisper and a belt. At every shipped patch's Sensitivity the
    reduction agrees within 1 dB from -6 dBFS down to -55 dBFS, and at any
    Sensitivity within 0.5 dB from -6 dBFS to -40 dBFS. On the quietest
    takes, around -55 dBFS, other Sensitivity settings can drift by more
    than 1 dB.

    **Frequency** is where the "s" lives, and it moves the crossover and
    the detector together. **Range** is the most it may take away, and it
    never takes more than 0.05 dB past it. Range 0 is a wire, byte for
    byte. The reduction approaches Range without reaching it: at Range 12
    the deepest any Sensitivity gets is more than 0.5 dB short.
    **Sensitivity** is how close to the full-band level the band may come
    before it counts.

    **Mode.** Broadband ducks the whole signal, for a vocal: the high and
    low bands move within 0.5 dB of each other. HF Only ducks the high band
    alone, for pick noise and cymbal edge, and the low band stays within
    0.25 dB. With nothing to duck, HF Only's split sums back flat within
    0.25 dB.

    **Release** is how fast the reduction lets go. The default 3.5 ms
    recovers at the dbx 902's own 925 dB a second, within 10 %, and the
    rest of the knob moves the rate well away from it. **Attack** gets
    shorter as the "s" gets louder. **Listen** plays the band the detector
    hears. The Effect controls page lists what the knobs span and the
    patches.

    Latency is zero, and no setting adds any. The tail reaches exact zero
    within 256 samples. It needs `audiobiquad`, `audiodynamics` and
    `audioroute`, so a stock CircuitPython board can't run it.
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
    WALKS_TO_BYPASS: bool
    MACRO_LABELS: tuple[str, ...]
    MACRO_MODES: dict[int, str]
    PATCHES: dict[int, tuple[str, tuple[float, ...]]]

    def __init__(
        self,
        source: _AudioSource,
        frequency: float | None = None,
        range_db: float | None = None,
        sensitivity_db: float | None = None,
        hf_only: bool | None = None,
        release_ms: float | None = None,
        attack_ms: float | None = None,
        listen: bool | None = None,
        patch: int | None = None,
        *,
        sample_rate: int | None = None,
        transport: _Transport | None = None,
    ) -> None: ...
    def reset(self) -> None:
        """Come back as a fresh instance at patch 0: the graph is built
        again and the old one released.

        A reset that cleared this graph in place never came back fresh.
        A `Splitter`'s ring cannot be cleared - the type exposes `tap()`
        and nothing else, and `SplitterTap.reset_buffer` is "deliberately
        nothing" - so the old reset pushed eight taps empty with
        `audiocore.get_buffer` (compiled out of CircuitPython's board
        builds, where it raised), and with the rings empty it still
        differed from a fresh instance from the first frame of material
        on. A graph built again is a fresh instance, by construction, on
        every interpreter. The output port is re-pointed at the new tail
        before the old graph is released, so a pump holding the port never
        reads a released node. The borrowed source is not reset or
        rewound; it plays on from where it stands, as a fresh instance
        handed it would.
        """

    def gain_reduction_db(self) -> Any:
        """What the gain cell did to the last frame, in dB.

        This is the cell's own number, before the Range blend, so it is the
        detector's reading rather than what reached the output. The output's
        reduction is `20*log10((1 - alpha) + alpha * 10**(cell/20))`.
        """
