# Writing a component: the provider rules

What a class must do to be an audio component. A host reads the shape these
rules produce in [the runtime API](../reference/component-api.md) and
[the metadata manifest](../reference/metadata.md); this page holds the rules
for whoever writes the class. `tools/validate_api.py` and
`tools/validate_metadata.py` enforce them.

## The contract is structural

A provider does not have to inherit from an `audiodsp` helper class, but it
must expose the required attributes and methods. The helper classes in
`audioinstruments._support` and `audioeffects._component` are implementation
conveniences, not a requirement imposed on consumers.

Provider-level class or module factories may remain available for local code,
but consumers use `audioinstruments.create()` and `audioeffects.create()`.

## Construction options

`options` are provider-specific construction options. They may allocate or
select resources needed to build the graph, such as a convolution impulse
length or a fixed topology. Musical behavior that a user should change while
the component is running belongs in macros and patches instead. Options must
be portable values or explicitly documented portable services; a consumer
must not need a CPython-only object to construct a component.

The method names are part of API v1. New optional arguments may be added
compatibly, but existing names and their basic call patterns remain valid.

## No arrays at the boundary

`output` is the only audio-processing interface. Components do not exchange
NumPy arrays, ulab arrays, or runtime-specific buffers at the public boundary.
A provider may use NumPy on CPython or ulab on MicroPython/CircuitPython
internally only when it supplies the portable fallback.

An audio component is portable source code. It may run under CircuitPython,
MicroPython, or CPython on Linux, Windows, WebAssembly, Android (wheels build
and publish; playback is untested on an emulator or a device), or another host
supported by the surrounding audio stack. Component code must therefore use
the common Python/audiodsp surface. When an operation differs by runtime, the
component supplies another route for the other runtimes rather than silently
depending on a CPython-only function or object. The shared builds freeze
`ulab`; CPython may use NumPy behind the same portable route. Components do not
import NumPy-only APIs into their common path. This lets the same component be
used by the offline renderer, a VST3 adapter, a software-only device, or the
audio side of a MIDI controller.

## The output port, for a class author

Underneath, an effect ends in an `audioroute.Port`, a zero-copy pass-through
whose `play()` re-points it, and `Component._output` is a property that builds
one on the first assignment and re-points it on every one after
([`lib/audioeffects/_component.py`](../../lib/audioeffects/_component.py)). A
class author writes `self._output = node` exactly as before. The port moves no
bytes: it hands back its source's own buffer, length and result.

Where the node is wanted instead of the wire (a `reset()` that must not rewind
a borrowed source, or a class appending one more stage to its own graph),
`audioeffects._component.port_target(output)` returns what the wire is
playing.

**A class appends a stage to `port_target(self._output)`, never to
`self._output`.** Wrapping the wire and assigning the wrapper points the wire
at something that reads the wire, and a pull on that never returns. On CPython
it is refused with a `ValueError` naming `port_target`. On a native build the
check has nothing to read and the loop is built, so the rule is the protection
there.

**Instruments have no port**, and neither does a rack. An instrument's graph
is fixed at construction, so `Instrument.output` is the node itself: stable
because nothing re-points it, not because anything guarantees it. A rack's
output is its last child's, which is already a stable one, and an empty rack
is a wire, so its output is the source it was handed.

Where `audioroute` is missing, `_component.PORT` is `None`. `TIER` and
`REQUIRES` do not change for this: a class does not *need* `audioroute`, it
degrades.

## Real-time rules

Construction may allocate the complete graph and bounded resources. Pulling
from `output` must not allocate, block, perform I/O, or depend on garbage
collection. Event methods may update state and perform bounded voice work, but
must not allocate unbounded storage. Any fixed resource or voice limit must be
bounded by construction or explicitly enforced.

`sample_position` is a frame offset, not seconds. Providers must honor
non-zero positions; an adapter may establish the current interval and schedule
the event at that frame.

## Declaring metadata

The provider rule is strict: a published component declares every required
field explicitly. The consumer rule is tolerant: `NAME` is the only field a
consumer must require.

An instrument module is one component. An effect module may contain several,
so each public concrete `Effect` subclass is one component. Metadata is made
only from static, portable Python literals (strings, integers, booleans,
tuples, lists and dictionaries) and is read-only after import.

`NAME` is a non-empty ASCII Python identifier, stable within its package and
kind, and matches an instrument module name or an effect class name. Renaming
it is a breaking change.

`MACRO_LABELS` is a tuple of zero to sixteen unique, non-empty strings; a
component with no macros declares `()`. `MACRO_MODES` has exactly one entry
per label, `{}` when there are none. The mode is explicit and is not inferred
from a MIDI CC assignment; `audioinstruments.midi_cc` may convert normalized
host values, but it does not replace the declaration.

`PATCHES` is a non-empty dictionary with contiguous integer indexes from `0`
through `N-1`, up to 128 patches. Each name is unique and non-empty; each
values tuple has exactly one integer per macro, each in `0..127`. With one
patch, `Default` is the convention but not a requirement; with several, patch
`0` has a descriptive name like the rest. A macro-less component uses an empty
values tuple.

`CATEGORIES`, `VERSION`, `VENDOR` and `DISPLAY_NAME` are optional; when
supplied they must have the documented shape. `CATEGORIES` is a tuple of
descriptive strings, `VERSION` and `VENDOR` non-empty strings. In an effect
source file, `VENDOR` is module-level and applies to every public component in
that file; instruments also use module-level `VENDOR`.

### Why patch values are integers

The live surface and the patch surface do different jobs. Live macro values
are performance: continuous, at whatever resolution the host offers, so
`get_macro()` can return a fraction. Patch values are storage: discrete,
portable, and meant to reproduce. Floats would suit a DAW and then need
special cases for MIDI, which is integer-native for program change and patch
transfer, and a patch saved from a DAW's continuous control could not be
reproduced on a MIDI rig. The 7-bit integer is what makes a patch portable.

The resolution this costs is bought back by choosing the curve rather than
widening the type. A macro whose useful values crowd one end of its range maps
logarithmically, putting fine grain where the ear needs it. Engineering ranges
(hertz, seconds, decibels) stay private in `_MACRO_RANGES`, so a provider may
re-range freely; `MACRO_RANGES` is not public metadata, and only the public
`0..127` scale is fixed.

Since construction applies patch `0` and a patch supplies every macro, a
source-level default for a macro-controlled parameter is never observable.
What ships is patch `0`. Where the two disagree, the source is documentation
that contradicts the artifact.

### Kits

A percussion instrument declares a non-empty `NOTE_MAP` of unique MIDI note
numbers and unique, non-empty labels, on General MIDI's percussion keys. It
also writes `PAD_MAP`, one `(key, voice)` pair for each key from 36 through
51, as literals a tool can read without importing the module. Every voice is a
note in `NOTE_MAP`, and a key the kit has a voice for always plays that voice.
`drumkits` has no table of its own; it hands each key to the kit that is
playing.

Six of these drum machines predate MIDI and speak trigger pulses, so they had
no numbers of their own to keep. The four that shipped with MIDI put their
voices on GM's slots anyway, bar one: the DrumTraks cabasa, which its chart
puts on 58, where GM has a vibraslap; it is on 69 here. Those charts also gave
several voices a second key number, the accented hit on hardware with no
velocity. Velocity carries that, so the second numbers are not answered.

The presence of a valid `NOTE_MAP` is the sole percussion discriminator.
`CATEGORIES` may contain `"percussion"`, but that value is descriptive. Effects
do not declare `NOTE_MAP`.

### Racks

A rack declares the same required metadata as a single effect class. When the
rack is a public class inside an effects package (the shipped form) the
declarations sit at class scope; a standalone rack script makes the same
declarations at module scope, because that rack is one source file. It may
implement its control surface with a module-level event handler or with an
object equivalent to an effect class.

## Discovery

`audioinstruments.ALL` identifies instrument modules. Public concrete effect
classes are the effect providers; private helpers and base classes are
excluded. `audioinstruments.DRUM_MACHINES` is derived from the modules that
declare a non-empty `NOTE_MAP`, and `MELODIC` is the rest of `ALL`, so there
is no second hand-kept list.

`tools/make_catalog.py` writes `catalog.json` from the classes, and its
`--check` fails a pull request that changes a class without it.
