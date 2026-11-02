# SPDX-FileCopyrightText: 2026 Brad Barnett
# SPDX-License-Identifier: MIT
"""An effect as a control panel sees it, and the one call that puts it on screen.

``EffectAdapter(effect)`` wraps an effect from ``audioeffects.create()`` in
the adapter that ``controlpanel`` edits through: up to sixteen macros on the
MIDI scale, the patch names, bypass, reload, and a callback for changes that
come from somewhere else. It is the effects half of
``audioinstruments.panel.PanelAdapter``, with the same names.

    import audioeffects.panel_view as panel_view

    adapter = panel_view.create("RingMod", source, 48000)
    adapter.set_macro(0, 96)     # the effect's macro 0, on the 0-127 scale
    adapter.set_patch(2)         # what a pad press does

``build(adapter, screen=...)`` puts the panel on a screen. It imports
``controlpanel`` only when called, so this module loads without LVGL.

Bypass: an effect has no bypass of its own. Some effects have a Mix macro,
and most do not, so ``set_bypass`` only records the flag the panel shows.
It does not change the sound. A bypass that routes around the effect is a
host's job, and it is not in this file.
"""

MACRO_COUNT = 16
PATCH_COUNT = 128


def create(name, source, sample_rate, transport=None, **options):
    """Create effect ``name`` and wrap it. A reload builds it with the same options."""
    import audioeffects

    def rebuild():
        return audioeffects.create(name, source, sample_rate, transport=transport, **options)

    return EffectAdapter(rebuild(), rebuild=rebuild)


def build(adapter, screen=None, **options):
    """Put the control panel for ``adapter`` on ``screen``. Options go to ``controlpanel.build``.

    ``adapter`` is an ``EffectAdapter``, or an effect, which is wrapped first.
    A name is not accepted: a name needs a source and a sample rate, so use
    ``create()`` for that.
    """
    import controlpanel

    if isinstance(adapter, str):
        raise TypeError("build() takes an adapter or an effect; use create(name, source, rate) for a name")
    if not isinstance(adapter, EffectAdapter):
        adapter = EffectAdapter(adapter)
    return controlpanel.build(adapter, screen=screen, **options)


class EffectAdapter:
    """What a control panel needs from ``effect``, and nothing else.

    ``rebuild`` returns a new effect; ``request_reload()`` uses it, and
    without one a reload fails and says so. ``create()`` always passes one.
    ``name`` replaces the display name on the faceplate.
    """

    def __init__(self, effect, rebuild=None, name=None):
        self.effect = effect
        self._rebuild = rebuild
        self._listeners = []
        self._reload_listeners = []
        self.macro_values = [64] * MACRO_COUNT
        self.patch_index = 0
        self.bypass = False
        self.engine_ready = True
        self.engine_error = 0
        self.engine_message = ""
        cls = type(effect)
        self.script_name = name or getattr(cls, "DISPLAY_NAME", None) or cls.NAME
        self._read_declarations()
        self._refresh()

    # ---- what the effect declares --------------------------------------

    def _read_declarations(self):
        cls = type(self.effect)
        labels = [str(text) for text in cls.MACRO_LABELS[:MACRO_COUNT]]
        self.macro_labels = labels
        self.macro_count = len(labels)
        declared = cls.PATCHES
        names = []
        if declared:
            count = min(max(declared) + 1, PATCH_COUNT)
            for index in range(count):
                entry = declared.get(index)
                names.append(str(entry[0]) if entry else "Patch %03d" % (index + 1))
        self.patches = names

    def _refresh(self):
        """Read every macro back from the effect, in place."""
        values = self.macro_values
        get = self.effect.get_macro
        for index in range(self.macro_count):
            values[index] = _midi(get(index))

    # ---- what the panel tells the effect -------------------------------

    def set_macro(self, index, value):
        if not 0 <= index < self.macro_count:
            return
        value = _midi(value)
        self.macro_values[index] = value
        self.effect.set_macro(index, value)

    def set_patch(self, index):
        self.patch_index = index
        self.effect.program_change(index)
        self._refresh()

    def set_bypass(self, enabled):
        """Record the bypass flag the panel shows. The effect is not told; see the module note."""
        self.bypass = bool(enabled)

    def request_reload(self):
        """Build the effect again and swap it in, keeping the patch and macros.

        Returns True when the new effect is in place. On a failure the old
        one keeps running, ``engine_error`` is 1 and ``engine_message`` says why.
        The old effect is not deinitialised here: it may still be in a graph
        that pulls from it, so a reload listener decides when to let it go.
        """
        self.engine_ready = False
        old = self.effect
        new = None
        try:
            if self._rebuild is None:
                raise ValueError("no rebuild given: build the adapter with create(), which knows the source")
            new = self._rebuild()
            self._restore(new)
        except Exception as error:  # noqa: BLE001 - any failure is reported, not raised
            self.engine_error = 1
            self.engine_message = "%s: %s" % (type(error).__name__, error)
            self.engine_ready = True
            if new is not None:
                try:
                    new.deinit()
                except Exception:  # noqa: BLE001,S110 - it never ran
                    pass
            return False
        self.effect = new
        self._read_declarations()
        self._refresh()
        self.engine_error = 0
        self.engine_message = ""
        self.engine_ready = True
        for callback in self._reload_listeners:
            callback(new, old)
        return True

    def _restore(self, new):
        """Give a rebuilt effect the patch and macros the old one had."""
        if self.patch_index in (getattr(type(new), "PATCHES", None) or {}):
            new.program_change(self.patch_index)
        count = min(self.macro_count, len(type(new).MACRO_LABELS))
        for index in range(count):
            value = self.macro_values[index]
            if _midi(new.get_macro(index)) != value:
                new.set_macro(index, value)

    # ---- what the panel listens to -------------------------------------

    def on_external_change(self, callback):
        """Register ``callback(kind, index, value)``: ``("macro", i, v)`` or ``("patch", i, i)``."""
        self._listeners.append(callback)

    def on_reload(self, callback):
        """Register ``callback(new, old)``, called after a reload swaps effects."""
        self._reload_listeners.append(callback)

    def _notify(self, kind, index, value):
        for callback in self._listeners:
            callback(kind, index, value)

    # ---- the host side -------------------------------------------------

    def note_macro(self, index, value):
        """A host moved macro ``index`` to ``value`` (0-127): apply it, tell the listeners."""
        if not 0 <= index < self.macro_count:
            return
        value = _midi(value)
        self.effect.set_macro(index, value)
        if self.macro_values[index] != value:
            self.macro_values[index] = value
            self._notify("macro", index, value)

    def note_program(self, index):
        """A program change from outside: apply it, tell the listeners the patch and every macro it moved."""
        if not 0 <= index < PATCH_COUNT:
            return
        self.effect.program_change(index)
        if self.patch_index != index:
            self.patch_index = index
            self._notify("patch", index, index)
        values = self.macro_values
        get = self.effect.get_macro
        for macro in range(self.macro_count):
            value = _midi(get(macro))
            if values[macro] != value:
                values[macro] = value
                self._notify("macro", macro, value)


def _midi(value):
    value = int(value + 0.5)
    return 0 if value < 0 else (127 if value > 127 else value)

