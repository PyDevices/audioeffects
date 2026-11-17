# Install

audioeffects is one package. It needs
[audiodsp](https://github.com/PyDevices/audiodsp), the part of OmniPython
that supplies the audio nodes and the CircuitPython-compatible `synthio` and
`audiocore` layer underneath.

## On a desktop

```bash
pip install --pre omnipython-audioeffects
```

pip pulls in `omnipython-audiodsp` for you. The distribution is
`omnipython-audioeffects`; the import name is `audioeffects`. Python 3.11 or
newer.

Check it:

```bash
python -c "import audioeffects; print(len(audioeffects.ALL), 'effects')"
```

```text
45 effects
```

## On a MicroPython-compatible board

```python
import omip
omip.install("audioeffects")
```

`omip` comes with OmniPython firmware. On other MicroPython firmware, run
`mip.install("github:PyDevices/omnipython/lib/omip.py")` once to put it on the board.

The firmware has to carry audiodsp's native modules, because the effects
build their graphs from them. `mip` copies only the Python.

## On a CircuitPython-compatible board

Most effects need audiodsp's extra nodes (`audiodynamics`, `audiobiquad`,
`audioecho`, `audioverb` and others), which a stock CircuitPython build does not
have. Each effect class names the ones it needs in `REQUIRES`, for example
`Reverb.REQUIRES == ("audioverb",)`.

## A specific release

The sound of an effect can change between releases
([Sound stability](https://github.com/PyDevices/audiodsp/blob/main/docs/how-it-works/sound-stability.md)). To keep a composition
the way it sounds today, pin the version:

```bash
pip install --pre omnipython-audioeffects==<version>
```
