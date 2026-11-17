# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT
from . import _component
from ._component import _AudioSource, _Transport

VENDOR: str
MINIMUM_HOLD_MS: float
INVERTING_LEVEL: int
SILENT_DB: float

class NoiseGate(_component.Component):
    """A noise gate after the Drawmer DS201: below the Threshold your signal
    is held down, and above it the gate opens and lets it through.

    **Controls.** Threshold is the level where the gate opens. Range is how
    far the closed gate holds the signal down, with 0 dB where the output
    is the input; it is a fixed depth, however far under the Threshold the
    signal falls. A crossing opens the gate over the Attack, holds it open
    for the Hold, and only then lets it fall over the Release. A long Hold
    with a short Release chops a reverb's tail off square: that is the
    gated-reverb snare. Once a crossing opens the gate, the gate runs
    through its Attack, Hold and Release even if the signal drops away at
    once. The Effect controls page lists what the knobs span.

    **The key never touches the sound.** The gate listens through its own
    band, with Key Low and Key High setting its edges, the top held just
    under half the sample rate, so a gate on a tom can ignore the hi-hat
    above it and the kick below it. Key Listen puts that band on the output
    in place of the audio, so you can hear what you are tuning.

    **Options.** Give the class `key=` another stream and that stream opens
    and closes the gate, which is how one sound gates another.
    `lookahead_ms` lets the gate read ahead of the audio, up to 50 ms, so it
    is already open when a transient arrives; each millisecond of look-ahead
    is a millisecond of latency. `duck=True` turns the gate inside out, for
    voice-overs: below the Threshold your signal passes untouched, and above
    it Range pushes it down. A duck's depth is honest to about -40 dB, and
    past that it falls short: Range -80 measures about -77 dB.

    **Levels.** With the gate open, the output is your signal at its own
    level. Silence in is silence out, and a mono source gets the same gate
    as stereo. The first opening after construction or `reset()` fades in
    from silence over the Attack, even at Range 0 dB.

    **Timing.** Latency is zero unless you set `lookahead_ms`. The tail is
    zero, except while Key Listen is on, when it covers the key band's ring;
    with `key=` the key decides, and the tail is `None`.

    **The detector reads peaks.** A sine opens the gate at a Threshold
    about 3 dB higher than a square of the same loudness, because its peaks
    are higher. A square of the same peak as a sine opens it about 0.63 dB
    higher than the sine, because the key band rings on the square's edges.

    **On a board.** The class needs audiodsp's `audiodynamics`,
    `audioroute` and `audiomath`, and on a board without any of them
    construction raises `ImportError`.
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
    THRESHOLD: int
    ATTACK: int
    HOLD: int
    RELEASE: int
    RANGE: int
    KEY_LOW: int
    KEY_HIGH: int
    KEY_LISTEN: int
    MAX_LOOKAHEAD_MS: float

    def __init__(
        self,
        source: _AudioSource,
        threshold_db: float = -40.0,
        attack_ms: float = 1.0,
        hold_ms: float = 50.0,
        release_ms: float = 200.0,
        range_db: float = -80.0,
        key_low_hz: float = 25.0,
        key_high_hz: float = 20000.0,
        key_listen: bool = False,
        duck: bool = False,
        lookahead_ms: float = 0.0,
        key_poles: int = 1,
        key: _AudioSource | None = None,
        patch: int | None = None,
        *,
        sample_rate: int | None = None,
        transport: _Transport | None = None,
    ) -> None: ...
    @property
    def latency_samples(self) -> int:
        """The look-ahead, in frames, and nothing else.

        Overridden because `_component` keeps `LATENCY_SAMPLES` on the
        class, and `lookahead_ms` is a per-instance choice: two gates in one
        graph may legitimately report different figures.
        """

    @property
    def tail_samples(self) -> int | None:
        """The same number, with Key Listen off: what is left to come out
        after the input goes quiet is exactly the audio held in the
        look-ahead buffer. Nothing here has a feedback path or a delay line.

        With Key Listen on, the output is the key band, and its one-pole
        filters ring after the input stops (audiocomponents#114: 2 048
        frames at the default Key Low). Each pole adds the frames its state
        takes to fall from four times full scale - the most a high-pass
        hands the next stage - to under half an LSB. With an external `key=`
        the band follows the key, not the input, so there is no bound:
        `None`.
        """
