# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT
from typing import Any

from . import _component
from ._component import _AudioSource, _Transport

VENDOR: str
MIN_Q: float
MAX_Q: float
HP_Q: float
HZ_GRID_LOW: float
HZ_GRID: float
DB_GRID: float
MIX_GRID: float
STACK_BODY_HZ: float
STACK_BODY_Q: float
STACK_BODY_BIAS: float
COMBO_BODY_HZ: float
COMBO_BODY_Q: float
COMBO_BODY_BIAS: float
NOTCH_HZ: float
NOTCH_Q: float
NOTCH_DB: float
PEAK_A_RATIO: float
PEAK_B_RATIO: float
PEAK_A_Q: float
PEAK_B_Q: float
SHELF1_RATIO: float
SHELF1_Q: float
SHELF2_RATIO: float
SHELF2_Q: float
SHELF2_GAIN_FRAC: float
FLAT_DB: float
T3_BAND_LO: float
T3_BAND_HI: float
CHAR_STACK: float
LOW_CUT_DEFAULT: float
BODY_DEFAULT: float
BREAK_DEFAULT: float
BITE_DEFAULT: float
TOP_DEFAULT: float
AIR_DEFAULT: float
MIX_DEFAULT: float

class CabinetSim(_component.Component):
    """A designed 4x12 stack or 1x12 combo cabinet, built from filters
    rather than a recorded impulse.

    **Character.** `4x12 stack` is a sealed, close-miked box. `1x12 combo`
    is an open back: at the same settings it has at least 3 dB more at
    100 Hz than the stack, and a notch between 100 Hz and 300 Hz that
    stays at every Low Cut.

    **Low Cut and Body.** Low Cut and Body shape the bottom. 40 Hz sits at
    least 12 dB under 1 kHz at every patch, and 20 Hz at least 20 dB under
    at the default. 60 Hz stays at least 20 dB under over the whole Body
    travel, at 48 kHz, 44.1 kHz and 22.05 kHz.

    **Break-up and Bite.** Break-up moves the speaker's two break-up peaks;
    over its whole travel each stands at least 3 dB over 1 kHz with a dip
    of at least 2 dB between them. Bite sets how tall they are. At Bite 0
    they are switched off, so there is no break-up at all.

    **Top and Air.** Top and Air shape the top end. Between 5 kHz and 8 kHz
    the response falls by at least 15 dB at every patch. Between 8 kHz and
    16 kHz it falls by no more than 12 dB at the default, and by more once
    Top is at its 7 kHz stop.

    **Mix.** Mix blends every section at once, and Mix 0 is a wire. The
    top-end fall holds down to Mix MIDI 120 and is gone by 96; the low cut
    holds down to Mix MIDI 96 and is gone by 32.

    **Level.** The response is a boost and there is no output trim, so
    leave headroom. At the hottest setting, combo with Low Cut 55 Hz and
    Body +6 dB, nothing reaches the rail below -14 dBFS; at the default,
    nothing does below -6 dBFS. Over the whole surface 1 kHz stays within
    1 dB of the input. Below the ceiling the cabinet is linear. Well above
    it, it clips, and 1 kHz is where you won't hear it.

    **Sample rate.** At 48 kHz and 44.1 kHz it is the same cabinet within
    0.5 dB. At 22.05 kHz the top changes: against 1 kHz, 5 kHz sits more
    than 3.5 dB higher and 7 kHz more than 3.5 dB lower than at 48 kHz,
    and the worst patch moves by between 4 dB and 6 dB.

    **Latency and tail.** It adds no latency. The tail is 6144 samples at
    every shipped patch. The longest ring is the combo's body bell, not
    the lowest Low Cut.

    **Your own impulse.** Pass `impulse=` some int16 frames and it convolves
    that instead, which needs `audioconvolve`. The tail then grows by the
    impulse's length.

    **Macros.** Each macro takes the 128 MIDI positions, and a fractional
    position snaps to the nearest, so a board and a desktop build the same
    filters.

    **Patches.** Alone on an ESP32-S3 the default was measured at 28 % of a
    block. The Effect controls page lists what the knobs span and the
    patches.

    It needs `audiobiquad`, so a stock CircuitPython board can't run it.
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
    SURFACE_CEILING_DBFS: float
    DEFAULT_CEILING_DBFS: float
    MACRO_LABELS: tuple[str, ...]
    MACRO_MODES: dict[int, str]
    PATCHES: dict[int, tuple[str, tuple[float, ...]]]

    def __init__(
        self,
        source: _AudioSource,
        character: float | str = 0.0,
        low_cut: float = 90.0,
        body: float = 0.0,
        break_up: float = 2600.0,
        bite: float = 5.0,
        top: float = 5200.0,
        air: float = -22.0,
        mix: float = 1.0,
        impulse: bytes | bytearray | memoryview | None = None,
        patch: int | None = None,
        *,
        sample_rate: int | None = None,
        transport: _Transport | None = None,
    ) -> None: ...
    def set_macro(
        self,
        index: int,
        value: float,
        channel: int = 0,
        note_id: int = -1,
        sample_position: int = 0,
    ) -> Any:
        """Set macro `index` from the 0-127 MIDI scale.

        **This surface is the 128 integer positions**, and a float snaps to
        the nearest before anything else happens. The base class accepts
        floats "so a host with finer resolution need not quantize"; on this
        class a finer position is not safe to honour, because only those
        128 per macro are proved to hand a board's single precision and a
        desktop's double the same filter (audiocomponents#75). The snap is
        done here, on the MIDI number the host passed, where `+ 0.5` is
        exact in both precisions - snapping later, from the stored 0..1
        position, would put the tie back at every half-step.
        `get_macro` reads back the snapped number, not the one sent. The one
        exception is the number `get_macro` itself returns: sent straight
        back it is kept, so a constructor option off the grid survives a
        host's echo.
        """

    @property
    def latency_samples(self) -> int: ...
    @property
    def tail_samples(self) -> int | None:
        """The synthetic sections' ring, **or the user impulse's length**.

        `TAIL_SAMPLES` is the eight-section number and the class returned
        it whatever `impulse=` held: an 8 192-tap impulse measures **8 447**
        samples of tail and a 48 000-tap room measures **48 255**, and a
        host that trusts 6 144 truncates the tail it was handed (audit 3
        (p)1, G2). The convolver's own ring is the impulse plus what the
        sections behind it add, so the declaration is the impulse's length
        plus the synthetic figure - which is what those two measurements
        say, to 255 and 255 samples.
        """
