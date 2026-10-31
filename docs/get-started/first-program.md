# Your first program

This program sends one click through a digital delay and prints how loud each
repeat is. It needs no speaker, so it runs the same on a desktop and in a
script on a build machine.

```python
import array
import audiocore
import audioeffects

RATE = 48000
click = array.array("h", [20000] + [0] * (RATE - 1))  # one click, one second
source = audiocore.RawSample(click, sample_rate=RATE, channel_count=1)
echo = audioeffects.create("DigitalDelay", source, RATE,
                           time_ms=250, feedback=0.5, mix=0.5)
heard = array.array("h")
while len(heard) < RATE:
    _, block = audiocore.get_buffer(echo.output)
    heard.extend(array.array("h", bytes(block)))
for ms in range(0, 1000, 250):
    start = ms * RATE // 1000
    print(ms, "ms: loudest sample", max(abs(v) for v in heard[start:start + 12000]))
```

It prints:

```text
0 ms: loudest sample 20000
250 ms: loudest sample 10000
500 ms: loudest sample 5000
750 ms: loudest sample 2500
```

The click comes through at once, and every 250 ms an echo follows at half the
level of the one before, because `feedback=0.5`.

## What each line does

`audiocore.RawSample(click, sample_rate=RATE, channel_count=1)` wraps the
samples as an audio source. Any source works: a `synthio` synthesizer, a
sample, a microphone input or another effect's `output`.

`audioeffects.create("DigitalDelay", source, RATE, ...)` builds an effect
around a source. Keyword arguments after the sample rate are the effect's
construction options; each class's module docstring lists them.
`audioeffects.ALL` lists every name `create()` takes.

`echo.output` is the effect's audio. Effects chain: hand one effect's `output`
to the next as its source.

`audiocore.get_buffer(echo.output)` pulls one block of audio from the end of
the chain. A host does this for you: on a board, hand `echo.output` to
`audio_out.play()` instead of looping yourself. Each block here is 256 frames
of 16-bit mono.

## Next

Put more effects in the chain with [Chain effects](../guides/chain-effects.md).

To hear something right away, run the complete example
[audioeffects_simpletest.py](https://github.com/PyDevices/audioeffects/blob/main/examples/audioeffects_simpletest.py).
It runs plucked notes through a tape echo and a hall and writes a WAV file you
can open in any audio player.
