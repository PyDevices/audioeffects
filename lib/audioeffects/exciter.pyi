# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT
from array import array

from . import _component
from ._component import _AudioSource, _Transport

VENDOR: str
DC_BLOCK_HZ: float
INPUT_CEILING_DBFS: float
ALIAS_OVERSAMPLE_COST_DB: float
OVERSAMPLE_CLAUSE_TUNE_HZ: float
TUNE_DEFAULT: float
HARMONICS_DEFAULT: float
MIX_DEFAULT: float
OUTPUT_DEFAULT: float
HARMONICS_SPAN_DB: float
TRANSIENT_ATTACK_DB: float
TRANSIENT_SUSTAIN_DB: float
TRANSIENT_FAST_RELEASE_MS: float
MIXER_BUFFER_BYTES: int
CURVE_BYTES: bytes
CURVE: array[int]

class Exciter(_component.Component):
    """A harmonic exciter: your note at unity, with a high-passed copy,
    clipped on a single side, added for air and edge.

    **Controls.** Tune is the corner of the high-pass that feeds the clip,
    so it picks which part of the note gets brighter. Harmonics drives the
    copy into the clip, from 0 to +14 dB. Mix is how much of the copy is
    added; it does not turn the note down. Character picks `classic`, a
    fixed clip, or `transient`, which drives the copy 6 dB harder for the
    first 8 ms of each onset. Output trims the whole effect, the note and
    the copy together, so the balance between them does not move with it,
    and it only turns down. The Effect controls page lists what the knobs
    span.

    **Switching.** Mix at 0, with Output at 0 dB, hands back your signal
    untouched. Bringing Mix back up switches the copy on fresh, rather than
    replaying what it held when it went off.

    **Sound.** The copy's high-pass is second order at every rate, because
    Tune is held under a seventh of the sample rate: at 22.05 kHz it tops
    out at 3150 Hz. The clip is one-sided, so the copy carries more second
    harmonic than third, and its second harmonic rises with level. At full
    Mix the copy stays under the note. The clip runs oversampled, so at
    48 kHz aliasing stays 60 dB under the copy at the defaults and with
    Harmonics at the top, up to the input ceiling.

    **Timing.** Latency is zero at every setting. Silence in is silence out
    at every shipped patch, and the tail falls to zero within 4096 frames.

    **Levels.** Keep the input under -3 dBFS and nothing rails, on any
    shipped patch or with Harmonics and Mix at the top; at -2 dBFS it can.
    No shipped patch leaves a DC offset on its output while it plays.

    **On a board.** The class needs audiodsp's `audioshaper`, `audiobiquad`,
    `audioroute` and `audiodynamics`, and on a board without them
    construction raises `ImportError`.
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
    INPUT_CEILING_DBFS: float
    ALIAS_OVERSAMPLE_COST_DB: float
    OVERSAMPLE_CLAUSE_TUNE_HZ: float
    MACRO_LABELS: tuple[str, ...]
    MACRO_MODES: dict[int, str]
    PATCHES: dict[int, tuple[str, tuple[float, ...]]]
    TUNE_RATE_FRACTION: float
    WALKS_TO_BYPASS: bool

    def __init__(
        self,
        source: _AudioSource,
        tune: float = 4000.0,
        harmonics: float = 0.25,
        mix: float = 0.3,
        character: float | str = 0.0,
        output_db: float = 0.0,
        oversample: bool | int | None = 4,
        patch: int | None = None,
        *,
        sample_rate: int | None = None,
        transport: _Transport | None = None,
    ) -> None: ...
    def reset(self) -> None:
        """Clear every node and restore patch 0, then arm the graph as
        `_build` does, so a reset is a fresh instance (no block primed
        through the chain before it was cleared plays after it)."""
