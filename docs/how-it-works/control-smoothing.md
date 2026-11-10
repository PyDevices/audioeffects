# Smoothing control moves

When you jump a level or a Mix, these effects walk the output to the new
setting over 20 ms instead of stepping there, so the jump doesn't click. That
covers a patch change's levels, a MIDI value that leaps, and a host setting
Mix from 0.3 to 1.0 in one call: Bitcrusher, Chorus, CombFilter, Compressor,
DeEsser, Distortion, DynamicEQ, Exciter, Fuzz, MultibandCompressor, Overdrive,
Phaser, Saturation, Tremolo and Vibrato, with the exceptions below. The Mix
of DigitalDelay and PingPongDelay and SlapbackDelay's Level walk too, since
their delay node does.

A few moves still step. A filter corner moves at once, and so do a switch, a
patch change that rebuilds part of a graph, and an effect built at Mix 0 the
first time its Mix leaves 0. Until those walk too, send such a jump as small steps, one a
block: the delays' own tests show Mix moved in 127 steps, one a block, steps
the output by less than one and a half times the steepest step of the tone
going through it. The rest is on the
[roadmap](https://github.com/PyDevices/audioeffects/blob/main/ROADMAP.md).

## Which controls ramp, and for how long

Every control that scales a signal ramps: Mix, Level, Volume, Output and
Makeup, a band's gain, a wet or dry gain, and a modulation depth. A move
walks in a straight line over 20 ms, the time `audioecho.FeedbackDelay`
already takes for its wow depth. That is short enough to sound like the knob
you turned, and the lifecycle matrix's step property (below) holds it to not
clicking.

Mix 0 is still your signal, byte for byte. An effect that hands you the
source itself there walks its graph to the dry first and switches once the
walk has landed, and walks back in from the dry when Mix leaves 0. DeEsser's
Range 0 works the same way, and Tremolo's Depth 0 walks there and back too.

A delay's Time is not ramped here: it already glides, at the rate its Glide
control sets. A filter corner that jumps steps the output too, more quietly
than a level does; it comes after the levels, with the node moving its
coefficients across the same 20 ms.

A switch, or a patch change that rebuilds part of a graph, will crossfade from
the old graph to the new over the same 20 ms instead of cutting.

## Where the ramp lives

In the nodes, in audiodsp. A ramp has to move once a sample to be smooth, and
an effect class runs Python only when a control is called, never while its
output is pulled. A ramp stepped from Python moves once a block at best, and
only if the host calls something every block. Built into the node, the ramp
costs a multiply a sample, runs on every interpreter and every board, and
reaches anyone using the bare nodes too, CircuitPython users included.

The nodes that walk are `audiomixer.Mixer`'s voice levels (its `level_ramp`),
the Waveshaper's `mix` and `post_gain`, the Biquad's and the AllPass's `mix`,
the Dynamics node's makeup, the FeedbackDelay's `mix` and
`audiomath.Multiply`'s `mix`. An
`audioroute.Port` told `play(source, after=frames)` keeps playing what it
plays until a walk has landed, which is how Mix 0 switches to the source
without a cut.

## When it is done

The plan is done when the lifecycle matrix's step property (P5 in
[`tests/support/LIFECYCLE.md`](https://github.com/PyDevices/audioeffects/blob/main/tests/support/LIFECYCLE.md)) holds for every
class with no exception declared for a control that jumps, and each class's
docstring drops the sentence that says a jump steps the output.
