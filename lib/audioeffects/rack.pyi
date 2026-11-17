# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT
from collections.abc import Sequence

from . import _component
from ._component import Component, _AudioSource, _Transport

VENDOR: str

class Rack(_component.Component):
    """A pedalboard cable run: name the effects in order and get a single
    effect back.

    For example:

        rack = Rack.create(source, 48000, chain=(
            ("Fuzz", {}),
            ("DigitalDelay", {"mix": 0.3, "feedback": 0.4}),
            ("ConvolutionReverb", {}),
        ))
        audio_out.play(rack.output)

    `chain` is a tuple of entries, each an effect name, a `(name, options)`
    pair whose options are that effect's constructor keywords, or an effect
    class in place of a name. `("Rack", {"chain": ...})` nests a rack.

    A rack adds no sound of its own: it sounds exactly like the same pedals
    patched by hand, one into the next. Empty, it is a patch cable, and its
    output is your source. A mono source gives a mono rack.

    Order matters as soon as one pedal isn't a plain filter: drive into a
    reverb isn't a reverb into drive.

    `latency_samples` and `tail_samples` are the sums of the pedals' own,
    read live, so they follow a pedal's knobs; the tail is `None` as soon as
    one pedal's is.

    There is no rack Mix, Bypass or Output knob, and patch 0 is its only
    patch. Turn a pedal's own Mix down; `ShimmerHall` and `AirSpace` are
    racks with knobs. The chain is set when the rack is built: to change
    pedals, build a new rack. To turn a pedal's knob, reach it through
    `rack.effects`, a tuple of the pedals in chain order.

    `reset()` clears every pedal and puts each back to the settings the
    rack built it with, undoing knob moves made since. `program_change(0)`
    does the putting back alone, without clearing anything.

    A host's `audiocore.reset_buffer(rack.output)` clears the last pedal
    only, and on an empty rack it rewinds your own source, because the
    output is your source. Call `rack.reset()` instead.

    A tempo-synced pedal follows the song's tempo wherever it sits, nested
    racks included: each pedal gets the rack's transport unless its entry
    names its own, and `transport_changed()` reaches every pedal.
    `capabilities` is the union of the pedals' own, set when the rack is
    built.

    A rack builds nothing of its own, so it costs what its pedals cost.
    Heavy pedals add up quickly on a small board: if the sound breaks up,
    trim the chain. The class itself runs on a stock board; a built rack
    needs whatever modules its pedals need.

    `deinit()` releases every pedal, nested racks included, and never your
    source. If an entry fails to build, or `patch` is refused, the pedals
    already built are released before the error reaches you.
    """

    NAME: str
    DISPLAY_NAME: str
    CATEGORIES: tuple[str, ...]
    VERSION: str
    TIER: str
    MACRO_LABELS: tuple[str, ...]
    MACRO_MODES: dict[int, str]
    PATCHES: dict[int, tuple[str, tuple[float, ...]]]

    def __init__(
        self,
        source: _AudioSource,
        chain: Sequence[object] = ...,
        patch: int | None = None,
        *,
        sample_rate: int | None = None,
        transport: _Transport | None = None,
    ) -> None: ...
    @property
    def effects(self) -> tuple[Component, ...]:
        """The children, in chain order."""

    @property
    def latency_samples(self) -> int: ...
    @property
    def tail_samples(self) -> int | None: ...
    @property
    def capabilities(self) -> tuple[str, ...]: ...
    def transport_changed(self) -> None: ...
    def reset(self) -> None:
        """Each child's own reset, tail first, reloading the settings the
        rack built it with in place of its patch 0, so no child passes
        through a patch the rack never gave it: one built at Mix 0 would
        re-arm there and pull a block of the source. A nested rack's reset
        does the same inside itself. The borrowed source is never named."""

    def deinit(self) -> None:
        """Every child's own deinit, tail first. The port is never released
        here: it is the last child's, or, for an empty rack, the source."""
