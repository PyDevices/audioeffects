# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT
from array import array

from . import _component
from ._component import _AudioSource, _Transport

VENDOR: str
FB_FLOOR_HZ: float
TAN_22_5: float
HALF_SWING_HZ: float
STAGES_CHOICES: tuple[int, ...]
DIVISION_BARS: tuple[float, ...]
WAVEFORM_POINTS: int
CURVE_POINTS: int
CURVE_SCALE: float
CURVE_BYTES: bytes
CUBIC_CURVE: array[int]

class Phaser(_component.Component):
    """A phaser after the Phase 90: notches swept up and down your signal on
    a triangle.

    **Controls.** Rate is the sweep's speed, and at 0 the notches hold
    still. Depth is how far they swing, and Centre puts the lower notch,
    mid-sweep. Stages sets how many all-pass stages there are, and each
    pair makes a notch: four stages make two, the second about two and a
    half octaves above the first. Mix at 0 is your dry signal, and at 0.5,
    the default, the notches go deeper than 40 dB. Feedback lifts a hump
    between the notches. Shape leans the triangle. Drive softens the signal
    on its way into the stages, so it grows harmonics as your level rises.
    The Effect controls page lists what the knobs span.

    **Drive and Feedback.** Drive is 0.3 when you construct the class, and
    there the Feedback hump stays under 5 dB. Turn Drive to 0 and Feedback
    lifts it more than 5 dB. The Phaser - lean patch is the default with Drive
    at 0. Keep the input under -9 dBFS and the defaults and patches stay off
    the rails. Feedback at its top can still push the output onto the rails.

    **Sync.** With Sync on, the sweep locks to the host: Division picks the
    length of a sweep in bars, a bar is read from the host's time
    signature, and a change of tempo or meter is followed.

    **Timing.** Latency is zero at every setting. Silence in is silence out
    once the notches ring down, which at musical settings is quick; the
    class reports the worst case, 552960 samples, for stages at their
    sharpest.

    **On a board.** The class needs audiodsp's `audiobiquad` and
    `audioshaper`, and on a board without them construction raises
    `ImportError`.
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
    INPUT_CEILING_DBFS: int
    CLIPS_AT_TOP: tuple[int, ...]
    MACRO_LABELS: tuple[str, ...]
    MACRO_MODES: dict[int, str]
    PATCHES: dict[int, tuple[str, tuple[float, ...]]]

    def __init__(
        self,
        source: _AudioSource,
        rate: float = 0.4,
        depth: float = 0.7,
        centre: float = 400.0,
        feedback: float = 0.0,
        mix: float = 0.5,
        stages: int = 4,
        shape: float = 0.5,
        drive: float = 0.3,
        sync: bool | float | None = False,
        division: float | None = 1.0,
        patch: int | None = None,
        *,
        sample_rate: int | None = None,
        transport: _Transport | None = None,
    ) -> None: ...
    def reset(self) -> None:
        """Clear every node, restore patch 0 and start the sweep again.

        The sweep is a `synthio.LFO` the walk does not reach, so it ran on
        through a reset from wherever it was; patch 0 now builds a fresh
        one, which starts where a fresh instance's does, as Vibrato's does
        on its clear."""

    def transport_changed(self) -> None:
        """With Sync on, follow the host's tempo and its time signature: a
        move of either sets the sweep's rate again. The base follows the
        tempo alone, so a 4/4 to 3/4 change at one tempo would keep the old
        rate. A NaN read twice is no change, as the base has it for a
        tempo."""
