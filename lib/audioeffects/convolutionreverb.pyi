# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT
from typing import Any

from . import _component
from ._component import _AudioSource, _Transport

VENDOR: str
PARTITION: int
MAX_PARTITIONS: int
CEILING_TAPS: int
FLOOR_SECONDS: float
NODE_DECAY_FLOOR: float
PREDELAY_MAX_MS: float
DIFFUSION_MAX_MS: float
DAMPING_LOW_HZ: float
DAMPING_HIGH_HZ: float
DAMPING_CLAMP: float
IR_GAIN_MIN_DB: float
IR_GAIN_MAX_DB: float
START_MAX_MS: float
ROOMS: int
TRIM_PEAK_DB: float
TRIM_KNEE_DB: float
OUT_LIFT_DB: float

def room_trim(peak_gain: float) -> float:
    """The wet gain for a room whose `room_peak_gain` is `peak_gain`: 1.0
    up to the knee, then down by the excess over `TRIM_PEAK_DB`, through a
    quadratic soft knee `TRIM_KNEE_DB` either side of it. Never above 1.0.
    Rounded to 1/4096, so it is the same number in single and double
    precision."""

DECAY_I: int
DAMPING_I: int
PREDELAY_I: int
DIFFUSION_I: int
ROOM_I: int
MIX_I: int
SYNTHESIS_MACROS: tuple[int, ...]

def read_wav(path, sample_rate: int) -> Any:
    """`(data, channels)` from a 16-bit PCM WAV at `sample_rate`.

    The file is read once; `data` is the `data` chunk's bytes. A WAV at
    another rate raises naming both rates: an effect does not resample.
    """

class ConvolutionReverb(_component.Component):
    """A room behind your dry signal, made by convolution: synthesized from
    five knobs, or the room your own impulse was recorded in.

    With nothing loaded the class synthesizes a short room from noise.
    By default the room is 0.08 s long.

    **The controls.** Decay is how long the room rings, Damping darkens its
    tail, Predelay puts silence between the dry and the room, and Diffusion
    fades the room in instead of starting it as a burst.
    Room picks one of 64 rooms of the same size.
    Damping runs from 500 Hz at its bottom stop to out at its top stop.
    At 22.05 kHz its brightest positions below the top stop clamp and all
    make the same room.
    Mix runs from 0 to 2: the dry at unity up to 1, the room alone at 2.
    With Damping out, each of the 64 Rooms falls 60 dB within 3 % of the
    Decay time.
    With Damping in, the 64 Rooms fall 60 dB within 2 % of the Decay time on
    average.
    A single Room with Damping in can take more than 15 % longer.
    A synthesized room plays through a level trim read off the room itself:
    none where the room brings a low square back 1 dB or more under 12 dB
    louder, and otherwise just enough to hold it to 12 dB, so the defaults
    play about 1 dB down at 48 kHz.
    One step of Decay or Damping moves the room's level by 0.5 dB at most.
    Anywhere on the knobs, a synthesized room alone is clean up to
    -13.5 dBFS in, and with the dry mixed in up to -15.5 dBFS, its input
    ceiling: the trim holds a low square's steady state at -12 dBFS, its
    onset rises about 1.3 dB past that, and the dry is not trimmed.
    Each side of a stereo room is normalised on its own, so the room sits in
    the middle.

    **Your own impulse.** Hand it `impulse=`, int16 frames or the path to a
    16-bit PCM WAV at the graph's rate, and the room is that recording.
    The room is then your source convolved with the impulse at unit
    energy, within 1 LSB.
    `ir_gain_db` trims it from -24 to +12 dB, and `start_ms` cuts up to
    200 ms from its start.
    Only Mix is live then: the other five knobs raise `IndexError`.
    A WAV at another rate raises `ValueError`, and so does an impulse with
    no energy or a `start_ms` that trims away every frame.
    An empty impulse, `impulse=b""`, is an undelayed wire whose Mix does
    nothing and whose `reset()` silences nothing.

    **The allocation.** `seconds` is the longest room the instance can hold,
    carved once when you build it: from 0.06 s up to 131 072 frames, and
    outside that the constructor raises `ValueError`.

    **Latency and tail.** `latency_samples` reads 256 while an impulse is
    loaded and 0 on the empty impulse.
    Held at Mix 0, the output is your source, byte for byte,
    `latency_samples` late, while the source keeps feeding it and nothing
    resets it.
    `tail_samples` is `latency_samples` plus the loaded room rounded up to
    a whole block of 256 frames.
    More than `tail_samples` frames after your input's last non-zero frame,
    the output is exact zero.

    **Moving the knobs.** No frame of your dry signal drops or repeats when
    you move a room knob, at any Mix, however many moves you make.
    From the end of the block in flight, the output is that of an instance
    that always had the new settings.
    A Mix move acts from the end of the block in flight, so Mix 0 reaches
    the plain source up to 256 frames late.
    `reset()` empties the room and returns to patch 0.
    With an impulse loaded, `reset()` in the middle of a stream silences the
    block in flight, 256 frames, dry included, and with Mix set back to 0
    your source carries on on time after it.
    A host that calls `audiocore.reset_buffer` on the output does the same.

    **Limits shared by the family.**
    A control that jumps makes the output step: move it in small steps from
    the host if you need it smooth.
    When your source ends, the tail rings out as it would on silence.
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
        decay: float = 1.0,
        damping_hz: float = 6000.0,
        predelay: float = 0.0,
        diffusion: float = 0.5,
        room: int = 1,
        mix: float = 0.6,
        seconds: float = 0.08,
        impulse: bytes | bytearray | memoryview | None = None,
        impulse_channels: int = 1,
        ir_gain_db: float = 0.0,
        start_ms: float = 0.0,
        patch: int | None = None,
        *,
        sample_rate: int | None = None,
        transport: _Transport | None = None,
    ) -> None: ...
    @property
    def node(self) -> Any:
        """The one `audioconvolve.Convolver` this class built."""

    @property
    def measured(self) -> Any:
        """True when an impulse was given: the room is that impulse."""

    @property
    def live_macros(self) -> Any:
        """The macro indexes this instance has: all six synthesized, only
        Mix (5) in measured mode."""

    @property
    def seconds(self) -> Any:
        """The allocation asked for; in measured mode, the trimmed
        impulse's own length."""

    @property
    def allocated_seconds(self) -> Any:
        """The allocation actually held: partitions x 256 / fs."""

    @property
    def decay_seconds(self) -> Any:
        """The room's T60 by the Decay law, or None in measured mode."""

    @property
    def latency_samples(self) -> int:
        """256 whenever the node holds an impulse, 0 when it holds none,
        read from the node."""

    @property
    def tail_samples(self) -> int | None:
        """`latency_samples` plus the loaded impulse rounded up to a
        partition; 0 when nothing is loaded."""
