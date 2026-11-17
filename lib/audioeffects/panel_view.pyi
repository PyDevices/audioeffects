# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT
from collections.abc import Callable
from typing import Any

from ._component import Component, _AudioSource, _Transport

MACRO_COUNT: int
PATCH_COUNT: int
PADS: int
BANKS: int
BANK_NAMES: str
DISPLAY_COLUMNS: int
SHOW_MS: int

class Panel:
    """The built panel, and the few things that update it.

    *adapter* is what it edits. *screen* is the object to build on (the
    active screen by default) and *group* the input group the encoders join
    (the default group). *theme* is a theme name or dict, *title* replaces
    the adapter's name on the faceplate, *subtitle* the line under it, and
    *on_close*, when given, adds an EXIT button that calls it.

    *two_wheels* is for a setup with a second wheel that moves focus between
    the controls (see ``display_driver.set_wheel_mapping``): the group stays
    in edit mode, so the other wheel always turns the control that has focus.
    """

    adapter: EffectAdapter
    screen: Any  # an LVGL object
    group: Any  # an LVGL input group
    theme: dict[str, Any]
    fine: bool
    encoders: list[Any]
    pads: list[Any]
    banks: list[Any]
    bank: int
    patch: int | None

    def __init__(
        self,
        adapter: EffectAdapter,
        screen: Any = None,
        group: Any = None,
        theme: str | dict[str, Any] | None = None,
        title: str | None = None,
        subtitle: str | None = None,
        on_close: Callable[[], object] | None = None,
        two_wheels: bool = False,
    ) -> None: ...
    def refresh_status(self) -> None:
        """Repaint the engine light and the buttons' LEDs from the adapter."""

    def set_status(self, text: str) -> None:
        """Show *text* on the display's second line in place of READY.

        For a live readout (a meter, a load figure) that fits the display's
        width. An engine error, a restart or BYPASSED still takes its place,
        and so does a value being shown while a control moves. None puts
        READY back.
        """

    def default_value(self, index: int) -> float:
        """The value a reset returns macro *index* to: what the patch set."""

    def edited(self) -> bool:
        """True when an encoder sits away from the value the patch gave it."""

    def choose_patch(self, index: int) -> None:
        """Pick patch *index* as if its pad were pressed."""
    root: Any

    def delete(self) -> None:
        """Take the panel off the screen and stop its timer."""

def create(
    name: str,
    source: _AudioSource,
    sample_rate: int,
    transport: _Transport | None = None,
    **options: object,
) -> EffectAdapter:
    """Create effect ``name`` and wrap it. A reload builds it with the same options."""

def build(
    adapter: EffectAdapter | Component, screen: Any = None, group: Any = None, **options: Any
) -> Panel:
    """Put the control panel for ``adapter`` on ``screen``. Options are ``Panel``'s keywords.

    ``adapter`` is an ``EffectAdapter``, or an effect, which is wrapped first.
    A name is not accepted: a name needs a source and a sample rate, so use
    ``create()`` for that.
    """

class EffectAdapter:
    """What a control panel needs from ``effect``, and nothing else.

    ``rebuild`` returns a new effect; ``request_reload()`` uses it, and
    without one a reload fails and says so. ``create()`` always passes one.
    ``name`` replaces the display name on the faceplate.
    """

    effect: Component
    macro_values: list[int]
    patch_index: int
    bypass: bool
    engine_ready: bool
    engine_error: int
    engine_message: str
    script_name: str

    def __init__(
        self,
        effect: Component,
        rebuild: Callable[[], Component] | None = None,
        name: str | None = None,
    ) -> None: ...
    def set_macro(self, index: int, value: float) -> None: ...
    def set_patch(self, index: int) -> None: ...
    def set_bypass(self, enabled: bool) -> None:
        """Record the bypass flag the panel shows. The effect is not told; see the module note."""

    def request_reload(self) -> bool:
        """Build the effect again and swap it in, keeping the patch and macros.

        Returns True when the new effect is in place. On a failure the old
        one keeps running, ``engine_error`` is 1 and ``engine_message`` says why.
        The old effect is not deinitialised here: it may still be in a graph
        that pulls from it, so a reload listener decides when to let it go.
        """

    def on_external_change(self, callback: Callable[[str, int, float], object]) -> None:
        """Register ``callback(kind, index, value)``: ``("macro", i, v)`` or ``("patch", i, i)``."""

    def on_reload(self, callback: Callable[[Component, Component], object]) -> None:
        """Register ``callback(new, old)``, called after a reload swaps effects."""

    def note_macro(self, index: int, value: float) -> None:
        """A host moved macro ``index`` to ``value`` (0-127): apply it, tell the listeners."""

    def note_program(self, index: int) -> None:
        """A program change from outside: apply it, tell the listeners the patch and every macro it moved."""
