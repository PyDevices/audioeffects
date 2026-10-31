# Roadmap

audioeffects is heading toward a complete effects library, measured the same
way on every interpreter and board.

## Next

- Control moves that ramp instead of stepping: Mix, levels and depths over
  20 ms in audiodsp's nodes, then filter corners, then crossfaded patch
  changes. The policy is in [docs/how-it-works/control-smoothing.md](docs/how-it-works/control-smoothing.md).

## Later

- Every effect compared with its counterpart in hexefx_audiolib, adopting that
  algorithm where it does measurably better on our tests. Licences are
  respected file by file: GPL-3.0 code informs a design and is never ported.
- CabinetSim with real cabinet impulse responses, if their licence allows
  shipping them. Until then they serve as a reference for the synthetic one.
- An auto-wah (an envelope filter that opens as you play harder) and its
  pedal-swept sibling, Wah. They share one resonant filter that has to move
  fast enough to sound smooth.
- SpringReverb, the dispersive "boing" of a spring tank, which a plate or hall
  reverb cannot give you.
- Ensemble, a multi-voice chorus where the number of voices is the effect, and
  FrequencyShifter, which moves every partial by the same number of hertz
  instead of keeping their ratios (RingMod multiplies; this shifts).
- AmpSim, an amp and DI model after the Tech 21 SansAmp GT2, built from
  measurements of a hardware unit rather than a component trace alone.
- A catalog shipped with each release: every effect's patches and macro names
  as JSON, MIDNAM and Cakewalk `.ins` files, so a DAW or MIDI host can show
  the names without loading the audio stack.

Bugs, and things you need that don't work yet, go to
[issues](https://github.com/PyDevices/audioeffects/issues).
