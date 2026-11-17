# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT
from . import _component
from ._component import _AudioSource, _Transport

VENDOR: str

class AutoPan(_component.Component):
    """An auto-panner: an LFO sweeps your signal between the speakers, with
    a new pan position on every sample, under a pan law.

    **The controls.** Rate is the sweep's speed. Depth is how far it
    swings: at Depth 1 it reaches each side, where the far speaker is
    silent, and at Depth 0 the output is the input. Shape runs the sweep
    from a triangle at 0 to a sine at 1. Law is how far the centre dips; at
    3.01 dB the power holds steady across the sweep. Centre moves the
    middle of the sweep towards one side. Phase moves where the sweep
    starts: at 0 it starts on the left. With Sync on, Rate snaps to the
    nearest of one, two, four or eight sweeps a beat of the host's tempo;
    with no host tempo, Rate stays where the knob is. The Effect controls
    page lists what the knobs span.

    **Levels.** The sweep sits 6 dB under your source: hard over, the near
    speaker plays it at half level. A mono source passes untouched, and
    silence in is silence out.

    **Timing.** Latency is zero at every setting, and so is the tail:
    nothing looks ahead and nothing rings on.

    **On a board.** The class needs audiodsp's `audiomath`, and on a board
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
    TAIL_SAMPLES: int
    TABLE_FRAMES: int
    LAW_POWER_DB: float
    LAW_LINEAR_DB: float
    SYNC_BEATS: tuple[float, ...]
    MACRO_LABELS: tuple[str, ...]
    MACRO_MODES: dict[int, str]
    PATCHES: dict[int, tuple[str, tuple[float, ...]]]

    def __init__(
        self,
        source: _AudioSource,
        rate: float = 2.0,
        depth: float = 1.0,
        shape: float = 1.0,
        law_db: float | None = None,
        centre: float = 0.0,
        phase: float = 0.0,
        sync: bool | float | None = 0.0,
        patch: int | None = None,
        *,
        sample_rate: int | None = None,
        transport: _Transport | None = None,
    ) -> None: ...
    def reset(self) -> None:
        """Clear every node, restore patch 0 and start the LFO again: the
        notes on the modulating `synthio.Synthesizer` played on through the
        walk, a block ahead, so patch 0 now builds a fresh one, as a fresh
        instance does."""
