# Audio component runtime API

Every effect, rack and instrument answers the same calls, so a host can drive
any of them without knowing which one it has. This page is what you can call
and what you can rely on. What each component declares about itself (names,
macros, patches) is in [the metadata manifest](metadata.md), the span of every
knob is in [Effect controls](effect-controls.md), and what each knob does is in
the effect's docstring, on its page in the API reference.

## Create one

Ask a package factory for a component by its stable name:

```python
instrument = audioinstruments.create(
    "minimoog", sample_rate=48000, channel_count=2, transport=transport,
)
effect = audioeffects.create(
    "Reverb", instrument.output, sample_rate=48000,
    transport=transport, character="hall",
)
```

| Kind | Factory call |
|---|---|
| Instrument | `create(name, sample_rate, channel_count=2, transport=None, **options)` |
| Effect or rack | `create(name, source, sample_rate, transport=None, **options)` |

`channel_count` is 1 or 2. An effect takes its channel count from `source` and
keeps it. The source must have the requested sample rate: a mismatch is
refused, never resampled, downmixed or upmixed. `options` are construction
choices such as a convolution impulse length; what you change while it plays
is a macro or a patch.

An effect borrows `source`. Its `deinit()` never deinitializes the source, so
you can tear a graph down piece by piece, fan a source out, or share it
between branches. `audioeffects.ALL` and `audioinstruments.ALL` list the names
the factories accept without building anything.

## What every component has

```python
component.output             # the pull source to play
component.sample_rate        # read-only integer
component.channel_count      # read-only integer
component.latency_samples    # read-only, input-to-output latency
component.tail_samples       # read-only integer, or None for unbounded
component.capabilities       # read-only tuple of strings
component.patch_index        # integer, or None after a manual macro move

component.set_macro(index, value, sample_position=0)
component.get_macro(index)
component.program_change(index, sample_position=0)
component.transport_changed()
component.reset()
component.deinit()
```

`output` is the only audio interface. Hand it to `audio_out.play()`, a mixer
voice or the next effect; components never pass arrays to each other.

`tail_samples` counts from the end of the latency: more than
`latency_samples + tail_samples` frames after the input's last non-zero frame,
the output is exact zero. It describes the settings in force, so read it after
a control move. A rack reports its whole graph's latency, and a tail of `None`
as soon as any child's is unbounded.

`capabilities` is advisory: the optional methods are always safe to call. Only
the effects with a Sync control declare one, `"tempo_sync"`. No instrument
declares any, so you can't use it to find, say, a pitch-bend-aware instrument.

### `output` is stable for the life of the component

Take `output` once and keep it. It is the same object from construction until
`deinit()`, whatever the effect does to its graph in between: Mix to 0 and
back, a patch change, a control that rebuilds a whole section. It is a wire,
not a node, so don't assume it is a particular node type or the source you
handed in. [Keep an effect's output wire](../guides/keep-an-output-wire.md)
shows it in use.

On an interpreter with no `audioroute.Port`, a stock CircuitPython board for
one, this doesn't hold: `output` is the last node in the graph and changes when
the effect rebuilds. If your program must run there too, read `output` again
after any control change, or check `audioeffects._component.PORT`, which is
`None` there.

## MIDI and control methods

Every public value is in MIDI units:

| Value | Range |
|---|---|
| note pitch | integer `0..127` |
| velocity | `0..127`; velocity 0 is a note-off |
| channel | integer `0..15` |
| controller and CC value | integer `0..127` |
| macro value | `0..127`; fractions accepted for fine automation |
| channel and poly pressure | `0..127` |
| pitch bend | `0..16383`, centre `8192` |
| program or patch index | non-negative integer |
| detune | floating-point semitones |
| sample position | frame offset within the block about to render |

Instruments take notes:

```python
note_on(pitch, velocity=127, detune=0.0, channel=0, note_id=-1, sample_position=0)
note_off(pitch, channel=0, note_id=-1, sample_position=0)
all_notes_off()
instrument.voices    # 1 if monophonic, its voice limit, or None for a drum machine
```

A note past the voice limit takes a sounding note's voice. A SoundFont
instrument's count is its pool's `voice_count`, which you can lower while it
plays and raise up to the voices its sampler was made with. A note is
identified by `(channel, note_id)` when you pass a `note_id`, otherwise by
`(channel, pitch)`, so note IDs let the same pitch overlap.

Every component also takes `pitch_bend()`, `control_change()`,
`channel_pressure()` and `poly_pressure()`, as no-ops where it has no use for
them. Effects never receive notes. No CC number is mapped to a macro for you:
your host maps them. To drive an instrument from MIDI bytes or a MIDI file,
put `audioinstruments.midi_dispatch.MidiDispatcher` in front of it. It takes
raw bytes (running status included) or `adafruit_midi` messages, sends Control
Change 120 and 123 to `all_notes_off()`, and routes channel 9 (General MIDI's
channel 10) to a drum kit when you give one; `read_midi_file()` turns a
Standard MIDI File into timed events for it. Its module docstring in
[audioinstruments](https://github.com/PyDevices/audioinstruments) has the
routing calls.

### Scheduling a note at a frame

`sample_position` places an event inside the block you are about to render.
To place one further ahead, queue it on an `audiopump.Events`:

```python
inst.schedulable                     # can this instrument take a frame?
with inst.scheduled(queue, frame) as tokens:
    inst.note_on(36, 127)            # heard at `frame`, not now
inst.at(queue, frame).note_on(38, 90)
```

`tokens` gets one token per event; `0` is one a full queue refused. Schedule
in time order and pair every note-on with its note-off, because the
instrument's own bookkeeping moves at schedule time. An instrument whose
`schedulable` is `False` still plays live, and
`audioinstruments.sequencer.Sequencer` refuses it rather than play its part
early.

## Macro and patch state

`get_macro(index)` returns the macro's current value, possibly fractional. A
bad index raises `IndexError`. A value off the 0 to 127 range is clamped, never
refused: below 0, minus infinity and NaN set the bottom stop, above 127 and
plus infinity the top one, and `get_macro()` then reads back 0 or 127.

A new component starts on patch `0`. `program_change(index)` applies a patch
and sets `patch_index`; an unknown index is ignored. Moving a macro by hand
sets `patch_index` to `None`. Macros and patches are global to the component,
not per channel or per note.

`reset()` releases every note, clears the effect's history and restores patch
`0`. `deinit()` frees what the component owns, never a borrowed source. Calling
it twice is safe; any other use after it raises `RuntimeError`.

### After a reset, a rejoin or a control move

A few effects don't come back to exactly where an untouched copy would be. None
of it is a fault, but expect it if you compare one against a twin.

**Free-running phase.** `Chorus`, `Phaser`, `Tremolo` and `Vibrato` restart
their LFO on `reset()` or `reset_buffer()`, and a Rate, Sync or patch change
moves it. `Bitcrusher` does the same with its sample-and-hold count and dither,
on a reset or a move of Rate, Dither, Band Limit or Mix. It sounds the same but
starts at a different point in its cycle.

**Detector and coupling state.** `tail_samples` bounds the output once the
input is silent, not the effect's internal state. After a reset, a rejoin or a
control move, the detectors and coupling filters of these effects take a while
to settle, heard as a re-attack like switching a pedal on:

| Effect | Largest difference from a fresh copy |
|---|---|
| `Compressor` | up to 1,575 LSB for 20 to 50 blocks after a Mix move; 10,000 to 13,000 LSB for up to about 110 blocks after a patch change |
| `DynamicEQ` | about 1,000 LSB for 18 to 27 blocks |
| `MultibandCompressor` | under 16 LSB within three blocks |
| `DeEsser` | up to 20 LSB for one block after a reset |
| `CombFilter` | within 1 LSB of its tail |
| `Exciter` | about 1 LSB of float residue |
| `Overdrive` | a few LSB after a control move; about 43 LSB that persists after a reset |
| `Fuzz` | 200 to 300 LSB that persists |
| `Distortion` | up to about 800 LSB that persists |

The `Compressor`'s patch-change figure is its detector re-attacking: the
characters a patch moves between have releases of up to two seconds. A reset in
the middle of a source buffer behaves the same as one on a block boundary.

**Three controls that are not a bypass.**

- `Fuzz` takes its lean shaper from the selected patch, not the macros: after
  `program_change(8)`, moving the macros back stays lean until another
  `program_change()`. At patch 2 with Bias at -0.85 it puts 6 to 9 LSB out of
  silence, inside its stated 16 LSB wander.
- `DynamicEQ` with Listen on outputs the detector's band, so `Mix` 0 bypasses
  only with Listen off.
- `Exciter` multiplies Output into the result at every Mix, so Mix 0 is an
  exact bypass only at 0 dB Output.

## Tempo and transport

`transport` is an optional callable shared by every component. It returns
`(playing, position_seconds, bpm, numerator, denominator)`, and without one a
component sees `(False, 0.0, 120.0, 4, 4)`.

A component reads the transport when you call `transport_changed()`, never
while its output is pulled; without the call it keeps the tempo it last read
until a control moves. Call it once a block when the tempo may move. It is
cheap, and a component that doesn't sync ignores it:

```python
for block in host_blocks():
    effect.transport_changed()
    audio_out.write(effect.output)
```

The effects with a Sync control follow it: `DigitalDelay`, `TapeDelay`,
`AnalogDelay`, `PingPongDelay`, `MultiTapDelay`, `Flanger`, `Phaser`, `AutoPan`
and `Tremolo`. No instrument syncs to tempo.

## Racks

A rack is one effect built from several. `Rack` is a serial chain described by
literals, for example
`create("Rack", source, rate, chain=(("Reverb", {"character": "hall"}),))`,
and `ShimmerHall` and `AirSpace` are fixed racks with their own macros. Racks
are listed in `audioeffects.ALL`, made by `audioeffects.create()`, and can
contain other racks.

Writing a component of your own follows the provider rules linked from
[CONTRIBUTING.md](https://github.com/PyDevices/audioeffects/blob/main/CONTRIBUTING.md).
