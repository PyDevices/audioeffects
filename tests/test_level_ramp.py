# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""A level that jumps walks over 20 ms in the node that carries it.

Fourteen classes carry Mix, or another level, on `audiomixer.Mixer` voices.
Each sets the mixer's `level_ramp` to 20 ms (`_component.ramp_levels`), so
a jump of that control walks there instead of landing at the voice's next
zero crossing. CircuitPython's Mixer has no `level_ramp`; there the levels
step as before, and `ramp_levels` says nothing.

| what it checks | bar |
|---|---|
| every mixer in the fourteen ramps | `level_ramp` is `sample_rate * 20 / 1000` on each `audiomixer.Mixer` a class builds, at 48 and 22.05 kHz |
| a Mix jump does not step | DynamicEQ's Mix moved 127 to 38 in one call on a 200 Hz tone: the largest step within two blocks of the move is under 1.5 times the larger of the tone's own before and after (it was 1.70 times with the level landing at once) |
| a node's Mix jump does not step | Flanger and Reverb, whose Mix is the node's own `mix`, moved 0 to 127 and 127 to 0 in one call on a 200 Hz tone: the largest step within two blocks of the move is under 1.5 times the tone's own before and after (on a 100 Hz triangle whose step is 100 to 140, it was 4400 and 3400 with the mix landing at once) |
| Mix leaving 0 the first time | AirSpace, PitchShifter and ShimmerHall built at Mix 0 and played for 12 blocks, then Mix moved to 127 in one call: the largest step within two blocks of the move is under 1.5 times the tone's own (the graph used to come in at once, cutting from the source to the wet alone: 4900 on a triangle whose step is 100) |
| Mix leaving 0 again | the same three built at Mix 127, moved to 0 and, six blocks later, back to 127: the same bar (the return cut the same way, 4700) |
| the shifted voice arrives faded in | PitchShifter's shifted voice starts from an empty line, so it arrives a window after Mix leaves 0, the first time or again: the largest step over the next 4000 frames is under 1.5 times the tone's own once it has settled (it arrived at full level, 3000 on a triangle whose step is 83) |
| a mixer without the ramp | `ramp_levels` on an object that refuses `level_ramp` hands it back untouched |

    python -m unittest tests.test_level_ramp
"""

import math
import os
import sys
import unittest
from array import array

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "lib"))

import audiocore                                          # noqa: E402
import audiofilters                                       # noqa: E402
import audiomixer                                         # noqa: E402

import audioeffects                                       # noqa: E402
from audioeffects import _component                       # noqa: E402

CLASSES = ("AirSpace", "Bitcrusher", "Compressor", "DeEsser", "Distortion",
           "DynamicEQ", "Exciter", "Fuzz", "MultibandCompressor", "Overdrive",
           "PitchShifter", "Saturation", "ShimmerHall", "Vibrato")
#: Built at Mix 0, these play the source itself and build their graph the
#: first time Mix leaves 0.
LAZY = ("AirSpace", "PitchShifter", "ShimmerHall")
#: Their Mix is a node's own mix, which walks in the node.
NODE_MIX = ("Flanger", "Reverb")
#: Fuzz's germanium circuit, its default, sums on no mixer.
OPTIONS = {"Fuzz": {"character": "cascade"}}
BLOCK = 256
HZ = 200.0
HAS_RAMP = hasattr(audiomixer.Mixer(voice_count=1, sample_rate=48000),
                   "level_ramp")


def tone(rate, channels=2):
    """A looped 200 Hz sine, handed out a block at a time."""
    period = int(rate / HZ) * 20
    values = array("h", bytes(2 * period * channels))
    for i in range(period):
        v = int(round(12000 * math.sin(2 * math.pi * HZ * i / rate)))
        for c in range(channels):
            values[i * channels + c] = v
    raw = audiocore.RawSample(values, sample_rate=rate, channel_count=channels)
    block = audiofilters.Filter(filter=None, mix=1.0,
                                buffer_size=BLOCK * channels * 2,
                                sample_rate=rate, channel_count=channels)
    block.play(raw, loop=True)
    return block


def mixers(effect):
    """Every audiomixer.Mixer reachable from the instance's attributes."""
    found = []
    for value in vars(effect).values():
        items = value if isinstance(value, (list, tuple)) else (value,)
        for item in items:
            if isinstance(item, audiomixer.Mixer) and item not in found:
                found.append(item)
    return found


def pull(effect, frames, channels=2):
    out = array("h")
    while len(out) < frames * channels:
        out.extend(array("h", bytes(audiocore.get_buffer(effect.output)[1])))
    return list(out[0::channels])


@unittest.skipUnless(HAS_RAMP, "this audiodsp's Mixer has no level_ramp")
class LevelRamp(unittest.TestCase):

    def test_every_mixer_ramps(self):
        for rate in (48000, 22050):
            for name in CLASSES:
                with self.subTest(name=name, rate=rate):
                    effect = audioeffects.create(name, tone(rate), rate,
                                                 **OPTIONS.get(name, {}))
                    found = mixers(effect)
                    self.assertTrue(found, "no mixer found")
                    for node in found:
                        self.assertEqual(node.level_ramp,
                                         (rate * 20 + 500) // 1000)
                    effect.deinit()

    def test_mix_jump_does_not_step(self):
        rate = 48000
        effect = audioeffects.create("DynamicEQ", tone(rate), rate)
        index = list(type(effect).MACRO_LABELS).index("Mix")
        effect.set_macro(index, 127)
        head = pull(effect, 24000)
        effect.set_macro(index, 38)
        tail = pull(effect, 24000)
        effect.deinit()
        trace = head + tail
        at = len(head)
        steps = [abs(trace[i] - trace[i - 1]) for i in range(1, len(trace))]
        near = max(steps[at - BLOCK:at + 2 * BLOCK])
        own = max(max(steps[at // 2:at - 2 * BLOCK]),
                  max(steps[at + 4800:at + 14400]))
        self.assertLess(near / own, 1.5)

    def test_a_node_mix_jump_does_not_step(self):
        rate = 48000
        for name in NODE_MIX:
            for start, end in ((0, 127), (127, 0)):
                with self.subTest(name=name, start=start, end=end):
                    effect = audioeffects.create(name, tone(rate), rate)
                    index = list(type(effect).MACRO_LABELS).index("Mix")
                    effect.set_macro(index, start)
                    head = pull(effect, 40 * BLOCK)
                    effect.set_macro(index, end)
                    tail = pull(effect, 12 * BLOCK)
                    effect.deinit()
                    trace = head + tail
                    at = len(head)
                    steps = [abs(trace[i] - trace[i - 1])
                             for i in range(1, len(trace))]
                    near = max(steps[at - 1:at + 2 * BLOCK])
                    own = max(max(steps[at - 8 * BLOCK:at - 1]),
                              max(steps[at + 6 * BLOCK:]))
                    self.assertLess(near / own, 1.5)

    def test_mix_leaving_0_the_first_time_walks_in(self):
        rate = 48000
        for name in LAZY:
            with self.subTest(name=name):
                effect = audioeffects.create(name, tone(rate), rate, mix=0.0)
                index = list(type(effect).MACRO_LABELS).index("Mix")
                head = pull(effect, 12 * BLOCK)
                effect.set_macro(index, 127)
                tail = pull(effect, 4 * BLOCK)
                effect.deinit()
                trace = head + tail
                at = len(head)
                steps = [abs(trace[i] - trace[i - 1])
                         for i in range(1, len(trace))]
                near = max(steps[at - 1:at + 2 * BLOCK])
                own = max(steps[BLOCK:at - 1])
                self.assertLess(near / own, 1.5)

    def test_mix_leaving_0_again_walks_in(self):
        rate = 48000
        for name in LAZY:
            with self.subTest(name=name):
                effect = audioeffects.create(name, tone(rate), rate)
                index = list(type(effect).MACRO_LABELS).index("Mix")
                effect.set_macro(index, 127)
                head = pull(effect, 12 * BLOCK)
                effect.set_macro(index, 0)
                head += pull(effect, 6 * BLOCK)
                effect.set_macro(index, 127)
                tail = pull(effect, 4 * BLOCK)
                effect.deinit()
                trace = head + tail
                at = len(head)
                steps = [abs(trace[i] - trace[i - 1])
                         for i in range(1, len(trace))]
                near = max(steps[at - 1:at + 2 * BLOCK])
                # At Mix 0 the output is the tone itself.
                own = max(steps[at - 4 * BLOCK:at - 1])
                self.assertLess(near / own, 1.5)

    def test_the_shifted_voice_arrives_faded_in(self):
        rate = 48000
        for again in (False, True):
            with self.subTest(again=again):
                effect = audioeffects.create(
                    "PitchShifter", tone(rate), rate,
                    mix=1.0 if again else 0.0)
                index = list(type(effect).MACRO_LABELS).index("Mix")
                if again:
                    effect.set_macro(index, 127)
                    head = pull(effect, 12 * BLOCK)
                    effect.set_macro(index, 0)
                    head += pull(effect, 6 * BLOCK)
                else:
                    head = pull(effect, 12 * BLOCK)
                effect.set_macro(index, 127)
                tail = pull(effect, 16 * BLOCK)
                effect.deinit()
                trace = head + tail
                at = len(head)
                steps = [abs(trace[i] - trace[i - 1])
                         for i in range(1, len(trace))]
                # The shifted voice arrives a window, about 1000 frames,
                # after the move.
                near = max(steps[at - 1:at + 4000])
                own = max(steps[at + 8 * BLOCK:])
                self.assertLess(near / own, 1.5)


class NoRamp(unittest.TestCase):

    def test_a_mixer_without_it(self):
        class Refuses:
            __slots__ = ()
        node = Refuses()
        self.assertIs(_component.ramp_levels(node, 48000), node)


if __name__ == "__main__":
    unittest.main()
