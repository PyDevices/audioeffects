# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT
from typing import Any

from . import _component
from ._component import _AudioSource, _Transport

VENDOR: str
PITCH_I: int
VOICE_I: tuple[int, ...]
LEVEL_I: tuple[int, ...]
DETUNE_I: int
SPREAD_I: int
MIX_I: int
BLOCK: int
LEVEL_TOP_DB: float
LEVEL_FLOOR_DB: float
LEVEL_OFF_DB: float
DETUNE_MAX_CENTS: float
WINDOW_MIN_MS: float
WINDOW_MAX_MS: float
WINDOW_DEFAULT_MS: float
DEFAULTS: tuple[float, ...]
STEPS: int

def ratio_step(semitones) -> int:
    """The shifter's nearest read-rate step, in 256ths, to an interval."""

def step_semitones(step) -> float:
    """The interval at the centre of read-rate step `step`: the node's
    floor lands on `step` from it, with half a step to spare either way,
    in single precision as in double."""

def whole(value: float) -> int:
    """A Pitch or Voice value as the whole semitone it plays."""

def mix_gains(mix: float) -> tuple[float, float]:
    """(dry, voice) gain at Mix `mix`: the dry at unity up to 1, then
    2 - Mix; each voice at Mix, capped at 1."""

def level_gain(db: float) -> float:
    """A Level in dB as a gain; 0 for the bottom step, which is off."""

class Harmonizer(_component.Component):
    """Three pitch shifters, each a fixed interval from your note, blended
    under the dry: the rig of three Eventide H910s played from one
    keyboard, so one singer is three-part harmony.

    **The controls.** Voice 1 to Voice 3 set each voice's interval in whole
    semitones, and Pitch moves all three together. Level 1 to Level 3 set
    each voice's level, and the bottom step turns the voice off. Detune
    pulls voice 1 down and voice 2 up. Spread pans voice 1 left and voice 2
    right; the dry and voice 3 stay in the centre. Mix holds the dry at
    unity up to 1 while the voices rise to their Levels; from 1 to 2 the
    dry fades, and at 2 the voices play alone. Constructor values land on
    the nearest of each knob's 128 steps; `window_ms`, 5 to 60 ms (21.33 by
    default), is fixed for good. The Effect controls page lists what the
    knobs span.

    **What you hear.** Each voice is its own machine: turning one on or
    off never changes the dry or the other voices.
    Each voice sits on the closest pitch its shifter can make: within 3.4
    cents of its interval from unison up, 6.8 cents down to an octave
    below and 13.7 cents below that.
    So Detune moves in steps of about 7 cents near unison, and voices 1
    and 2 sit evenly apart only to within a step.
    Detune is a steady offset, not a chorus: a voice holds its pitch.
    Each voice glitches as it splices, more often the further it is
    shifted and the shorter the window: at the default window a fifth up
    splices every 43 ms, at any sample rate, where the first channel is
    silent.
    Where it is not, each splice moves by up to a fiftieth of a second to
    land in phase, so the splices come sooner.
    A voice at exact unison never splices: it is a fixed short delay, and
    it combs with the dry.
    A voice you turn back on starts from silence, not with a scrap of what
    it played before.

    **Limits.** It moves notes by fixed intervals and does not listen for
    the key.
    Each voice rounds off peaks above about -1.4 dBFS.
    The voices add to the dry: at patch 0 an input that peaks at or below
    13 900 (-7.4 dBFS) cannot reach full scale.
    Patch 6 is patch 0 without the octave below, for a board that cannot
    run three voices in time.
    The shifter reads its line without interpolation, which you may hear
    as grit on a shifted voice.
    On a mono source Spread does nothing.
    An interval move leaves each voice's splice where it was.
    A control that jumps makes the output step: move it in small steps
    from the host if you need it smooth.

    **Wire, latency, tail.** At Mix 0 the output is the input, byte for
    byte.
    There is no latency: the dry is a wire, and each shifted voice trails
    it by between the crossfade, a sixteenth of the window, and the whole
    window.
    `tail_samples` covers the window, the crossfade and one block, and is
    0 at Mix 0 or with every voice off.
    `reset()` empties the three lines, starts their splices where a new
    instance's start, and returns to patch 0.
    On CircuitPython's own pitch shifter a reset does not restart the
    splices.
    The class never reads the host's tempo.
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
        pitch: float = 0.0,
        voice1: float = 4.0,
        voice2: float = 7.0,
        voice3: float = -12.0,
        level1_db: float = -6.0,
        level2_db: float = -6.0,
        level3_db: float = -9.0,
        detune_cents: float = 0.0,
        spread: float = 0.0,
        mix: float = 1.0,
        window_ms: float = ...,
        patch: int | None = None,
        *,
        sample_rate: int | None = None,
        transport: _Transport | None = None,
    ) -> None: ...
    def reset(self) -> None:
        """Empty the three lines, return their splices to a new node's
        start, and restore patch 0 (or, under a rack, what the rack built
        this with)."""

    @property
    def tail_samples(self) -> int | None:
        """The shifters' lines, every one overwritten, and a block."""

    @property
    def window_ms(self) -> Any:
        """The window the instance was built with, in milliseconds."""
