# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT
"""The construction shape every effect class is built on, which every effect inherits."""

from collections.abc import Callable, Iterable, Sequence
from typing import Protocol, TypeVar

_M = TypeVar("_M")
_R = TypeVar("_R")

class _AudioSource(Protocol):
    """Anything an effect can read: it names its format and hands out audio, as every
    audiodsp node does."""

    @property
    def sample_rate(self) -> int: ...
    @property
    def channel_count(self) -> int: ...

_Transport = Callable[[], tuple[bool, float, float, int, int]]
"""Reads the host's transport as `(playing, position, bpm, numerator, denominator)`."""

STOCK: str
AUDIODSP: str

AUDIODSP_MODULES: tuple[str, ...]
MODES: tuple[str, ...]
MAX_MACROS: int
MAX_PATCHES: int
SPLITTER_TAPS: int
NYQUIST_MARGIN: float
GOOD_BEAT: tuple[float, float]
METER_LIMIT: float
LEVEL_RAMP_MS: int
BYPASS_MARGIN_FRAMES: int
LEVELS_RAMP: bool | None
output_port: property

_Span = tuple[float, float] | tuple[float, float, str]

def port_target(output: object) -> object:
    """What a component's output actually plays: the node behind a port, or the output itself."""

def static_transport() -> tuple[bool, float, float, int, int]:
    """The transport a component sees when it was given none."""

def synced_beat(state: Sequence[object], last: tuple[float, float] = ...) -> tuple[float, float]:
    """(bpm, quarter notes in one bar) read off a host transport tuple, keeping `last` for
    whatever the host gets wrong."""

def biquad_ring(node: object) -> int | None:
    """Frames an `audiobiquad.Biquad` rings for after its input stops, as an upper bound."""

def cascade_ring(nodes: Iterable[object]) -> int | None:
    """`biquad_ring` summed over a cascade, or None if any section has a pole on or outside
    the unit circle."""

def db_to_gain(db: float) -> float: ...
def db_to_amplitude(db: float) -> float:
    """Biquad peaking/shelf A parameter."""

def logmap(value: float, lo: float, hi: float) -> float:
    """0..1 -> lo..hi, logarithmic; the natural mapping for frequencies."""

def macro_value(span: _Span, position: float) -> float:
    """A macro's 0..1 position -> the value it stands for."""

def macro_position(span: _Span, value: float) -> float:
    """The inverse of `macro_value`, unquantized."""

def clamped_midi(value: float) -> float:
    """`value` on the 0-127 MIDI scale as a float, clamped to it."""

def position_of_midi(mode: str, midi: float) -> float:
    """The 0-127 MIDI grid -> a macro's 0..1 position, by the macro's mode."""

def midi_of_position(mode: str, position: float) -> float:
    """The inverse of `position_of_midi`, unquantized."""

def macro_of(span: _Span, value: float, mode: str = "UNIPOLAR") -> int:
    """`value` as the nearest integer on the 0-127 MIDI grid."""

def release(node: object) -> None:
    """Let go of a node no graph points at any more (None is fine)."""

def ramp_levels(mixer: _M, sample_rate: int) -> _M:
    """Make `mixer`'s level and pan moves ramp over `LEVEL_RAMP_MS`; returns `mixer`."""

def level_ramp_frames(sample_rate: int) -> int:
    """`LEVEL_RAMP_MS` in frames at `sample_rate`, rounded to the nearest."""

def unramped_pull(pull: Callable[[object], _R], node: object) -> _R:
    """`pull(node)` with `node`'s `level_ramp` off for that one pull."""

def with_ramps(call: Callable[..., _R], *args: object) -> _R:
    """`call(*args)` with the pulls it makes leaving the level ramps on."""

def open_level_gates(node: object, voices: Iterable[object], silence: object) -> bool:
    """Render one block of silence through `node` so every voice starts at its level."""

def let_go_of_source(
    head: object, source: object, consumers: Iterable[tuple[object, object]] = ()
) -> bool:
    """Drop the source frames `head` has taken and not handed on, without reading or
    resetting `source`. Returns whether it could."""

class MetadataError(ValueError):
    """A malformed macro or patch table."""

class Component:
    """Base for a rebuilt effect: subclasses implement `_build`.

    The live surface below is the contract's, frozen by roadmap §3. A
    subclass supplies `NAME`, `TIER`, the macro and patch tables, `_build`
    and -- if it has macros -- `_apply_macro`."""

    NAME: str | None
    TIER: str
    REQUIRES: tuple[str, ...]
    CAPABILITIES: tuple[str, ...]
    LATENCY_SAMPLES: int
    TAIL_SAMPLES: int | None
    MACRO_LABELS: tuple[str, ...]
    MACRO_MODES: dict[int, str]
    PATCHES: dict[int, tuple[str, tuple[float, ...]]]
    LAZY_BUILD: bool
    WALKS_TO_BYPASS: bool
    def __init__(self, source: _AudioSource, *options: object, **keywords: object) -> None: ...
    @classmethod
    def create(
        cls,
        source: _AudioSource,
        sample_rate: int,
        transport: _Transport | None = None,
        **options: object,
    ) -> Component:
        """The construction boundary: the host names the rate it believes the graph runs at,
        and a mismatch with `source` is an error rather than a silent resample."""
    def macro(self, index: int) -> float:
        """What macro `index` currently stands for, in its own units."""
    @property
    def output(self) -> _AudioSource: ...
    @property
    def sample_rate(self) -> int: ...
    @property
    def channel_count(self) -> int: ...
    @property
    def latency_samples(self) -> int: ...
    @property
    def tail_samples(self) -> int | None: ...
    @property
    def capabilities(self) -> tuple[str, ...]: ...
    @property
    def patch_index(self) -> int | None: ...
    @property
    def transport(self) -> _Transport: ...
    def set_macro(
        self,
        index: int,
        value: float,
        channel: int = 0,
        note_id: int = -1,
        sample_position: int = 0,
    ) -> None:
        """Set macro `index` from the 0-127 MIDI scale. Floats are accepted
        so a host with finer resolution need not quantize."""
    def get_macro(self, index: int) -> float: ...
    def program_change(
        self, index: int, channel: int = 0, note_id: int = -1, sample_position: int = 0
    ) -> None:
        """Apply patch `index`. An index this class does not have is ignored."""
    def pitch_bend(self, value: float, channel: int = 0, sample_position: int = 0) -> None: ...
    def control_change(
        self, controller: int, value: float, channel: int = 0, sample_position: int = 0
    ) -> None: ...
    def channel_pressure(
        self, value: float, channel: int = 0, sample_position: int = 0
    ) -> None: ...
    def poly_pressure(
        self,
        pitch: int,
        value: float,
        channel: int = 0,
        note_id: int = -1,
        sample_position: int = 0,
    ) -> None: ...
    def transport_changed(self) -> None:
        """Tell the component the host's transport may have changed."""
    def reset(self) -> None:
        """Clear every node and restore patch 0."""
    def deinit(self) -> None:
        """Release every node this effect built, and never its source."""
