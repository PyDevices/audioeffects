# Audio component metadata manifest

Every component declares what it is as plain data on its class or module, so a
host can build a panel, offer patches or map drum pads without constructing an
audio graph. This page is what those declarations mean. The live calls are in
[the runtime API](component-api.md).

## What a component declares

```python
NAME = "tr808"                         # the stable lookup name
DISPLAY_NAME = "TR-808"                # optional, for menus and panels
MACRO_LABELS = ("Level", "Accent")     # up to 16 knobs
MACRO_MODES = {0: "UNIPOLAR", 1: "UNIPOLAR"}
PATCHES = {
    0: ("Default", (102, 64)),         # name, one value per macro
}
```

`NAME` is what you pass to `create()`. It is an instrument's module name or an
effect's class name, and it doesn't change between releases.

`MACRO_LABELS` names the knobs in index order, the index `set_macro()` takes. A
component with no knobs declares `()`.

`MACRO_MODES` says how each knob rests and moves:

| Mode | Meaning |
|---|---|
| `UNIPOLAR` | rests at 0 and moves upward |
| `BIPOLAR` | rests at 64 and moves either way |
| `TOGGLE` | 0 is off and 127 is on; at run time 0 to 63 is off and 64 to 127 on |

`PATCHES` numbers its patches from 0 with no gaps, up to 128. Each is a name and
one integer from 0 to 127 per macro. Patch 0 is what a new component plays.
Patch values are whole numbers so that a patch saved anywhere plays the same on
a MIDI rig; live macro values can still be fractional.

`CATEGORIES` (a tuple of descriptive strings), `VERSION` and `VENDOR` are
optional. Knob spans in hertz, seconds or decibels are not metadata; they are
listed in [Effect controls](effect-controls.md).

## Drum kits

A percussion instrument also declares `NOTE_MAP`, its voices on General MIDI's
percussion keys, so one MIDI track plays on any kit:

```python
NOTE_MAP = (
    (36, "Bass Drum"),
    (38, "Snare"),
)
```

Having a `NOTE_MAP` is what makes an instrument a drum machine;
`audioinstruments.DRUM_MACHINES` lists those and `MELODIC` the rest.

Every kit also answers keys 36 to 51, the first bank of an 8- or 16-pad
controller. A key the kit has a voice for plays that voice; the rest play the
nearest voice it does have (an electric snare plays the snare, a pedal hat the
closed hat, a ride the cymbal). The kit's `PAD_MAP` lists that choice as
`(key, voice)` pairs:

```python
PAD_MAP = (
    (36, 36),
    (38, 38),
    (39, 38),  # Clap -> Snare
    ...
)
```

Two `create()` options change it. `strict_pads=True` plays only the notes in
`NOTE_MAP`, and the instrument's `strict_pads` property reports it. `pad_map=`
takes `(key, voice)` pairs or a dict in place of `PAD_MAP`. You can't pass both.

Any other note is ignored without a sound, an error or a warning, so a melodic
part sent to a drum track plays nothing. Some patches of a kit with several
machines, such as `drumkits`, leave a few pads silent too. Which kit answers
which hit is a table in the
[audioinstruments](https://github.com/PyDevices/audioinstruments) documentation.

## Reading metadata as a host

Use `NAME` as the identity. Everything else is there when you want it, and a
host must not assume the optional fields exist. A host can still offer a
generic panel for a component with no macros or patches.

## The catalog

Every wheel carries `audioeffects/catalog.json`: each effect's name, display
name, categories, macros (label and mode) and patches (index, name and values).
A DAW or MIDI host can read it to show those names without loading the audio
stack:

```python
import json, os, audioeffects

with open(os.path.join(os.path.dirname(audioeffects.__file__), "catalog.json")) as f:
    catalog = json.load(f)
for effect in catalog["effects"]:
    print(effect["display_name"], [p["name"] for p in effect["patches"]])
```

The file is `{"format": 1, "package": "audioeffects", "effects": [...]}`, in
the order of `audioeffects.ALL`.
