# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT
from typing import Any

from . import _component
from ._component import _AudioSource, _Transport

VENDOR: str
FET: int
OPTICAL: int
VCA: int
VARIMU: int
OPTICAL_ATTACK_MS: float
OPTICAL_RELEASE_MS: float
OPTICAL_RELEASE_SLOW_MS: float
OPTICAL_MEMORY: float
ATTACK_MEASURED_PER_SET: float
RELEASE_MEASURED_PER_SET: float
SLOW_ATTACK_FRACTION: float
SLOW_ATTACK_MIN_MS: float
SLOW_ATTACK_MAX_MS: float
SLOW_THRESHOLD_OFFSET_DB: float
FET_RATIO_REFERENCE: float
FET_RATIO_TILT_DB: float
SLOW_RATIO_SPAN: float

class Compressor(_component.Component):
    """Compressor characters after classic studio units, on a shared panel.

    **Characters.** Character picks the unit. On `fet`, after the Urei
    compressor, the time knobs get faster as you turn them up, and with
    everything up it distorts, which is the sound its buttons-in trick is
    famous for. On `optical`, after the Teletronix and the default, a light
    cell sets the times, so the time knobs and Memory are idle; recovery is
    quick at first and slow after, and slower again after a long or deep
    passage. On `vca`, after the dbx, the detector reads true RMS and the
    release falls in a straight line in decibels. On `varimu`, after the
    Fairchild, the slope climbs with level, gentle on small peaks and hard
    on loud ones, and the Vari-Mu patches are its time-constant positions.

    **Controls.** Threshold, Ratio, Knee and Makeup set the curve. Release
    Slow and Memory run a second, slower stage that remembers how long the
    passage was. Detector switches between peak and RMS, and RMS Window sets
    how long the RMS average is. Emphasis and Emphasis Freq tilt the side
    chain toward a band. Mix at 0 is your dry signal. The Effect controls
    page lists what the knobs span.

    **Timing.** Latency is zero at every setting. The gain multiplies the
    audio, so silence in is silence out on the same sample.

    **Where it is not clean.** On bass with a fast release the gain follows
    the waveform and the output thickens, as it does on the hardware; a
    slower release cleans it up. The RMS detector reads a deep square and
    sine differently at its default window; a wider RMS Window fixes it.

    **Levels.** Keep the input under -6 dBFS and the defaults and patches
    stay off the rails.

    **On a board.** The class needs audiodsp's `audiodynamics` and
    `audioroute`, and on a board without them construction raises
    `ImportError`.
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
        character: float | str = "optical",
        patch: int | None = None,
        *,
        sample_rate: int | None = None,
        transport: _Transport | None = None,
        **overrides: float,
    ) -> None: ...
    def reset(self) -> None:
        """Clear every node and restore patch 0, then arm the graph as
        `_build` does, so a reset is a fresh instance (no block primed
        through the chain before it was cleared plays after it)."""

    @property
    def gain_reduction_db(self) -> Any:
        """What the last processed block was reduced by, both stages summed.
        A meter reading, not part of the contract's surface."""
