import pathlib
import unittest
from types import SimpleNamespace

from support import controls_table
from tools.validate_metadata import MetadataError, validate_component


def component(**fields):
    defaults = {
        "NAME": "example",
        "MACRO_LABELS": (),
        "MACRO_MODES": {},
        "PATCHES": {0: ("Default", ())},
    }
    defaults.update(fields)
    return SimpleNamespace(**defaults)


class MetadataContractTest(unittest.TestCase):
    def test_macroless_component_is_valid_when_empty_fields_are_explicit(self):
        self.assertFalse(validate_component(component(), kind="instrument"))

    def test_missing_required_field_is_invalid_even_when_the_value_is_empty(self):
        owner = component()
        del owner.MACRO_MODES
        with self.assertRaises(MetadataError):
            validate_component(owner, kind="instrument")

    def test_modes_are_complete_and_toggle_patches_are_discrete(self):
        owner = component(
            MACRO_LABELS=("Power", "Drive"),
            MACRO_MODES={0: "TOGGLE", 1: "UNIPOLAR"},
            PATCHES={0: ("Default", (64, 64))},
        )
        with self.assertRaises(MetadataError):
            validate_component(owner, kind="instrument")

    def test_malformed_patch_values_report_metadata_error(self):
        owner = component(PATCHES={0: ("Default", (128,))},
                           MACRO_LABELS=("Level",),
                           MACRO_MODES={0: "UNIPOLAR"})
        with self.assertRaises(MetadataError):
            validate_component(owner, kind="instrument")

    def test_percussion_is_defined_by_a_valid_note_map(self):
        melodic = component()
        self.assertFalse(validate_component(melodic, kind="instrument"))

        percussion = component(NOTE_MAP=((36, "Bass Drum"),))
        self.assertTrue(validate_component(percussion, kind="instrument"))

    def test_a_pad_map_must_cover_36_to_51_with_voices_the_kit_has(self):
        notes = ((36, "Bass Drum"), (38, "Snare"))
        whole = tuple((key, 38 if key != 36 else 36) for key in range(36, 52))
        self.assertTrue(validate_component(
            component(NOTE_MAP=notes, PAD_MAP=whole), kind="instrument"))
        for bad in (whole[:-1],                         # a key missing
                    whole[:-1] + ((51, 40),),           # a voice it lacks
                    ((36, 38),) + whole[1:]):           # its own voice unused
            with self.assertRaises(MetadataError):
                validate_component(component(NOTE_MAP=notes, PAD_MAP=bad),
                                   kind="instrument")

    def test_note_map_is_not_valid_on_an_effect(self):
        with self.assertRaises(MetadataError):
            validate_component(
                component(NOTE_MAP=((36, "Bass Drum"),)), kind="effect")

    def test_public_engineering_ranges_are_rejected(self):
        with self.assertRaises(MetadataError):
            validate_component(component(MACRO_RANGES=()), kind="effect")


if __name__ == "__main__":
    unittest.main()


class EffectControlsPageTest(unittest.TestCase):
    """The controls page has to stay the classes' own answer: a knob's span
    typed by hand is true the day it is written and wrong a month later."""

    PAGE = (pathlib.Path(__file__).resolve().parent.parent
            / "docs" / "reference" / "effect-controls.md")

    def test_the_page_is_what_the_classes_say(self):
        self.assertEqual(self.PAGE.read_text(encoding="utf-8"),
                         controls_table.render())

    def test_the_page_goes_red_on_a_stale_span(self):
        page = self.PAGE.read_text(encoding="utf-8")
        self.assertNotEqual(page.replace("40 Hz to 800 Hz", "40 Hz to 900 Hz"),
                            controls_table.render())

    def test_every_unit_names_a_ranged_knob(self):
        units = ("ms", "s", "Hz", "dB", "dBFS", "semitones", "cents",
                 "degrees", "ips", "um")
        for cls in controls_table.classes():
            for index, unit in getattr(cls, "_MACRO_UNITS", {}).items():
                with self.subTest(cls=cls.NAME, index=index):
                    self.assertIn(index, range(len(cls._MACRO_RANGES)))
                    self.assertNotEqual(cls.MACRO_MODES[index], "TOGGLE")
                    self.assertIn(unit, units)
