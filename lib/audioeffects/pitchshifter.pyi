# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT
from typing import Any

from . import _component
from ._component import _AudioSource, _Transport
from .digitaldelay import laps_to_zero as laps_to_zero
from .digitaldelay import whole_frames as whole_frames

VENDOR: str
PITCH_I: int
FINE_I: int
MIX_I: int
DELAY_I: int
FEEDBACK_I: int
DELAY_MAX_MS: float
FEEDBACK_MAX: float
WINDOW_MS: float
WINDOW_MIN_MS: float
WINDOW_MAX_MS: float
LINE_MS: float
LOOP_MS: float
BLOCK: int
STEPS: int
DEFAULTS: tuple[float, ...]

def crossfade_frames(sample_rate: int) -> int:
    """The shifter's crossfade: 4/3 ms in whole frames, 64 at 48 kHz."""

def window_frames(window_ms: float, sample_rate: int) -> Any:
    """The shifter's window in whole frames at the running rate."""

def ratio_step(ratio: float) -> int:
    """The node's read rate nearest `ratio`, in 256ths."""

def step_centre_semitones(step) -> float:
    """Semitones that put the node on `step`: the centre of the step, so
    the node's truncation lands on it at any float width."""

def step_semitones(step) -> float:
    """The step itself in semitones, for the loop; exactly 0 at unity."""

class PitchShifter(_component.Component):
    """Play your part again a fixed interval up or down, a little behind
    you, the way the first harmonizer boxes did.

    **The controls.** Pitch is the interval in whole semitones. Fine
    detunes it. The shifter reads in steps of 1/256 of the speed, so Fine
    moves in steps of about 7 cents near unity and 13.5 near the octave
    down, and the interval is within 0.5 % of the one Pitch and Fine name.
    Mix keeps your dry signal at unity up to its centre, 1, with the
    shifted voice coming up to unity beside it; at 2 you hear the shifted
    voice alone, and at 0 the output is your input. Delay holds the shifted
    voice back. Feedback sends the shifted voice round again, and every
    repeat is shifted once more: at a fifth up the repeats climb a fifth,
    then a ninth, then a thirteenth. The Effect controls page lists what
    the knobs span.

    **The splice.** The shifter keeps a short memory of what you play, the
    window, and reads it at the new speed, splicing back to the other end
    when it runs out.
    Off unity, each note comes back anywhere from straight away to one
    window and 1.3 ms late, plus Delay, the delay sweeping and jumping at
    every splice.
    At unity it sits still, 1.3 ms late, from a fresh start, a reset or a
    return from Mix 0; after a Pitch move it sits wherever the splice left
    it, up to one window and 1.3 ms late.
    On CircuitPython's own pitch shifter a reset or a return from Mix 0 does
    not restart the splice, so there it sits wherever the splice was.
    Shifting down drops slices of what you play; shifting up repeats them.
    The window is 30 ms unless you pass `window_ms`, 15 to 60, when you
    build it: a longer window splices less often and arrives later.

    **The dry.** Up to Mix 1 your dry signal passes untouched, sample for
    sample, with the shifted voice added on top, so a hot input can reach
    the rail.
    Feedback stacks level too, far past the input: at Feedback 127, Delay 0
    and Mix 2 a noise burst peaking at -10.3 dBFS reaches the rail at
    unison, and comes within 6 dB of it at an octave or a fourth or fifth
    either way.

    **Mono, latency, tail.** A one-channel source gets a one-channel
    shifter with the same window.
    Latency is zero samples: the dry is never delayed.
    `tail_samples` is an upper bound on how long the output takes to reach
    exact zero once your input stops, at every Feedback.
    `reset()` empties the shifter and both delay lines and returns to
    patch 0.
    The class never reads the host's tempo.
    If your host takes the output before it loads a patch or moves Mix, or
    loads a patch right after a reset, the first 256 frames, 5 ms at
    48 kHz, play at the old level.

    **Limits shared by the family.**
    A control that jumps makes the output step: move it in small steps from
    the host if you need it smooth.
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
    INPUT_CEILING_DBFS: float
    MACRO_LABELS: tuple[str, ...]
    MACRO_MODES: dict[int, str]
    PATCHES: dict[int, tuple[str, tuple[float, ...]]]

    def __init__(
        self,
        source: _AudioSource,
        pitch: float = 7.0,
        fine: float = 0.0,
        mix: float = 1.0,
        delay_ms: float = 0.0,
        feedback: float = 0.0,
        window_ms: float = 30.0,
        patch: int | None = None,
        *,
        sample_rate: int | None = None,
        transport: _Transport | None = None,
    ) -> None: ...
    def macro(self, index: int) -> float:
        """What macro `index` currently stands for, in its own units; for
        Pitch, the whole semitones it plays."""

    @property
    def output(self) -> _AudioSource:
        """The node the host plays. Asking for it is the host's first step
        to pulling, so from here a level that moves is an ordinary move."""

    def reset(self) -> None:
        """Empty the shifter and both lines, return to patch 0, and play
        from there as a new instance does."""

    @property
    def tail_samples(self) -> int | None:
        """Frames until the output is exactly zero once the input stops,
        as an upper bound.

        The shifter hands out what it holds for at most one window and
        crossfade after its input stops, the line adds its delay, and the
        loop then goes round `laps_to_zero(Feedback)` times, each lap at
        most its delay plus the window its splicer reads across, and a frame
        for the read between two. At Feedback 0 the loop is a wire."""
