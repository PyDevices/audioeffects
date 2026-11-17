# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT
from . import _component
from ._component import _AudioSource, _Transport

VENDOR: str

class TransientShaper(_component.Component):
    """A transient shaper after the SPL Transient Designer: turn the hit up
    or down without touching the ring, and the ring without touching the
    hit.

    **No threshold.** There is no threshold and no ratio: the gain follows
    the difference between two envelopes of your own signal, so between -20
    and -40 dBFS a quiet hit is shaped as hard as a loud one, to within
    0.5 dB.

    **Controls.** Attack moves the first few milliseconds of every hit.
    Sustain moves what rings after it, and the two act at once: a snare can
    get more stick and less room from one instance. Output sets the level
    back. Attack Speed sets how fast the attack section runs. Sustain Hold
    is how long the ring section holds at the peak before it lets go; held,
    it digs deeper into the ring than a plain follower does. The Effect
    controls page lists what the knobs span.

    **Where it falls short.** A held note at Attack +12 is still lifted by
    more than 0.5 dB 100 ms after the hit, and back within 0.5 dB by
    150 ms, since the detector reads the note's RMS rather than its peaks.
    On a slow decay Sustain runs out before its end: on a note fading at
    3 dB a second, Sustain -24 reaches about -16 dB.

    **Levels.** At its defaults the class is a wire. Attack and Sustain add
    gain where they are turned up, so a hit that is already loud reaches the
    rails. Keep the input under -12 dBFS and the defaults and patches stay off
    the rails. Attack at its top can still push the output onto the rails. Turn
    Output down, or your input.

    **Timing.** Latency is zero at every setting, and so is the tail:
    silence in is silence out in the same frame.

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
    INPUT_CEILING_DBFS: int
    CLIPS_AT_TOP: tuple[int, ...]
    MACRO_LABELS: tuple[str, ...]
    MACRO_MODES: dict[int, str]
    PATCHES: dict[int, tuple[str, tuple[float, ...]]]

    def __init__(
        self,
        source: _AudioSource,
        attack_db: float = 0.0,
        sustain_db: float = 0.0,
        output_db: float = 0.0,
        attack_speed: float = 1.0,
        sustain_hold_ms: float = 150.0,
        patch: int | None = None,
        *,
        sample_rate: int | None = None,
        transport: _Transport | None = None,
    ) -> None: ...
