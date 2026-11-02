"""The effect panel's adapter, on CPython with no LVGL and no audiodsp.

A fake effect stands in for a rebuilt class: the same declarations
(``MACRO_LABELS``, ``PATCHES``) and the same macro calls. ``build()`` is
checked against a fake ``controlpanel`` module, so nothing here draws.

    python -m unittest tests.test_panel_view
"""

import importlib.util
import os
import sys
import types
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Load the file by path: the package's __init__ imports audiocore, which
# this test does not need and a plain CPython run does not have.
_spec = importlib.util.spec_from_file_location(
    "panel_view", os.path.join(ROOT, "lib", "audioeffects", "panel_view.py"))
panel_view = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(panel_view)


class FakeEffect:
    NAME = "Fake"
    DISPLAY_NAME = "Fake Effect"
    MACRO_LABELS = ("Frequency", "Depth", "Mix")
    PATCHES = {0: ("Clean", (10, 20, 30)), 2: ("Wide", (100, 90, 80))}

    def __init__(self, macros=(0, 0, 0)):
        self.macros = [float(v) for v in macros]
        self.patch = None
        self.deinited = False

    def get_macro(self, index):
        return self.macros[index]

    def set_macro(self, index, value):
        self.macros[index] = float(value)

    def program_change(self, index):
        self.patch = index
        for macro, value in enumerate(self.PATCHES[index][1]):
            self.macros[macro] = float(value)

    def deinit(self):
        self.deinited = True


class Adapter(unittest.TestCase):
    def test_declarations_come_from_the_class(self):
        adapter = panel_view.EffectAdapter(FakeEffect())
        self.assertEqual(adapter.script_name, "Fake Effect")
        self.assertEqual(adapter.macro_labels, ["Frequency", "Depth", "Mix"])
        self.assertEqual(adapter.macro_count, 3)
        # Patch 1 is missing from PATCHES, so it gets the placeholder name.
        self.assertEqual(adapter.patches, ["Clean", "Patch 002", "Wide"])

    def test_values_are_read_back_on_the_midi_scale(self):
        adapter = panel_view.EffectAdapter(FakeEffect(macros=(12.4, 127.6, -3.0)))
        self.assertEqual(adapter.macro_values[:3], [12, 127, 0])

    def test_set_macro_reaches_the_effect_and_is_clamped(self):
        effect = FakeEffect()
        adapter = panel_view.EffectAdapter(effect)
        adapter.set_macro(1, 200)
        self.assertEqual(adapter.macro_values[1], 127)
        self.assertEqual(effect.macros[1], 127.0)
        adapter.set_macro(5, 9)  # no such macro: ignored
        self.assertEqual(adapter.macro_values[5], 64)

    def test_set_patch_applies_it_and_rereads_the_macros(self):
        effect = FakeEffect()
        adapter = panel_view.EffectAdapter(effect)
        adapter.set_patch(2)
        self.assertEqual(effect.patch, 2)
        self.assertEqual(adapter.patch_index, 2)
        self.assertEqual(adapter.macro_values[:3], [100, 90, 80])

    def test_bypass_is_a_flag_the_effect_never_sees(self):
        effect = FakeEffect()
        adapter = panel_view.EffectAdapter(effect)
        adapter.set_bypass(True)
        self.assertTrue(adapter.bypass)
        self.assertEqual(effect.macros, [0.0, 0.0, 0.0])

    def test_external_macro_and_patch_changes_are_announced_once(self):
        adapter = panel_view.EffectAdapter(FakeEffect())
        heard = []
        adapter.on_external_change(lambda *event: heard.append(event))
        adapter.note_macro(0, 40)
        adapter.note_macro(0, 40)  # same value again: nothing new to say
        adapter.note_program(2)
        self.assertEqual(heard, [("macro", 0, 40), ("patch", 2, 2),
                                 ("macro", 0, 100), ("macro", 1, 90), ("macro", 2, 80)])

    def test_reload_keeps_patch_and_macros_and_tells_listeners(self):
        old = FakeEffect()
        adapter = panel_view.EffectAdapter(old, rebuild=lambda: FakeEffect())
        adapter.set_patch(2)
        adapter.set_macro(0, 7)
        swapped = []
        adapter.on_reload(lambda new, previous: swapped.append((new, previous)))
        self.assertTrue(adapter.request_reload())
        new = adapter.effect
        self.assertIsNot(new, old)
        self.assertEqual(new.patch, 2)
        self.assertEqual(new.macros[0], 7.0)
        self.assertEqual(swapped, [(new, old)])
        self.assertFalse(old.deinited)  # the old one is left for a listener to let go

    def test_failed_reload_keeps_the_old_effect_and_says_why(self):
        def broken():
            raise ValueError("no source")

        old = FakeEffect()
        adapter = panel_view.EffectAdapter(old, rebuild=broken)
        self.assertFalse(adapter.request_reload())
        self.assertIs(adapter.effect, old)
        self.assertEqual(adapter.engine_error, 1)
        self.assertEqual(adapter.engine_message, "ValueError: no source")
        self.assertTrue(adapter.engine_ready)

    def test_reload_without_a_rebuild_fails_with_a_reason(self):
        adapter = panel_view.EffectAdapter(FakeEffect())
        self.assertFalse(adapter.request_reload())
        self.assertIn("create()", adapter.engine_message)


class Build(unittest.TestCase):
    def setUp(self):
        self.calls = []
        fake = types.ModuleType("controlpanel")

        def build(adapter, screen=None, **options):
            self.calls.append((adapter, screen, options))
            return "panel"

        fake.build = build
        self._saved = sys.modules.get("controlpanel")
        sys.modules["controlpanel"] = fake

    def tearDown(self):
        if self._saved is None:
            del sys.modules["controlpanel"]
        else:
            sys.modules["controlpanel"] = self._saved

    def test_an_effect_is_wrapped_and_handed_over_with_its_options(self):
        result = panel_view.build(FakeEffect(), screen="scr", title="Fake")
        self.assertEqual(result, "panel")
        adapter, screen, options = self.calls[0]
        self.assertIsInstance(adapter, panel_view.EffectAdapter)
        self.assertEqual(screen, "scr")
        self.assertEqual(options, {"title": "Fake"})

    def test_an_adapter_is_used_as_it_is(self):
        adapter = panel_view.EffectAdapter(FakeEffect())
        panel_view.build(adapter)
        self.assertIs(self.calls[0][0], adapter)

    def test_a_name_is_refused_with_a_pointer_to_create(self):
        with self.assertRaises(TypeError):
            panel_view.build("Fake")
        self.assertEqual(self.calls, [])


if __name__ == "__main__":
    unittest.main()
