# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""Forty-five effect classes built out of audiodsp's audio nodes.

Every class wires itself from an audio source - a synthesizer, an
instrument's `output`, a host input, or a previous effect's `output` - and
exposes its chain tail as `output`. See README.md for the catalogue.

    import audioeffects
    comp = audioeffects.create("Compressor", source, 48000,
                               threshold_db=-20, ratio=3)
    audio_out.play(comp.output)

The package factory receives the source and sample rate explicitly. Direct
class construction is supported for local code too, and reads the format
off the source it is handed.

Some classes also carry patches - named settings on the 0-127 MIDI grid, the
way an instrument does. See README.md, "A note on patches".
"""

from . import _component


#: What `configure()` last set. No class reads it: every effect takes its
#: format from the source it is built around. It stays so the
#: `configure(48000)` idiom in existing code keeps working.
_FORMAT = [48000, 2]


def configure(rate, channel_count=2):
    """Record a default format. Kept for code that calls it; an effect's
    format always comes from its source, so this changes no effect."""
    _FORMAT[0] = int(rate)
    _FORMAT[1] = int(channel_count)


def sample_rate():
    """The rate `configure()` last recorded (48000 until it is called)."""
    return _FORMAT[0]


def channel_count():
    """The channel count `configure()` last recorded (2 until it is called)."""
    return _FORMAT[1]


# Each effect's class and the module that holds it. A class is imported the
# first time it is used, so a firmware can freeze only the effects it plays
# and a program pays only for the ones it touches; `from audioeffects import
# Reverb` and `audioeffects.Reverb` work as before.
_MODULES = {
    "Compressor": "compressor",
    "Limiter": "limiter",
    "Expander": "expander",
    "NoiseGate": "noisegate",
    "DeEsser": "deesser",
    "TransientShaper": "transientshaper",
    "MultibandCompressor": "multibandcompressor",
    "ParametricEQ": "parametriceq",
    "GraphicEQ": "graphiceq",
    "LowPass": "lowpass",
    "HighPass": "highpass",
    "BandPass": "bandpass",
    "Notch": "notch",
    "LadderFilter": "ladderfilter",
    "CombFilter": "combfilter",
    "DynamicEQ": "dynamiceq",
    "Reverb": "reverb",
    "ConvolutionReverb": "convolutionreverb",
    "DigitalDelay": "digitaldelay",
    "SlapbackDelay": "slapbackdelay",
    "TapeDelay": "tapedelay",
    "AnalogDelay": "analogdelay",
    "PingPongDelay": "pingpongdelay",
    "MultiTapDelay": "multitapdelay",
    "Chorus": "chorus",
    "Phaser": "phaser",
    "Tremolo": "tremolo",
    "AutoPan": "autopan",
    "Vibrato": "vibrato",
    "RingMod": "ringmod",
    "Flanger": "flanger",
    "Overdrive": "overdrive",
    "Distortion": "distortion",
    "Bitcrusher": "bitcrusher",
    "CabinetSim": "cabinetsim",
    "Fuzz": "fuzz",
    "Saturation": "saturation",
    "Exciter": "exciter",
    "PitchShifter": "pitchshifter",
    "Harmonizer": "harmonizer",
    "Octaver": "octaver",
    "StereoWidener": "stereowidener",
    "Rack": "rack",
    "ShimmerHall": "shimmerhall",
    "AirSpace": "airspace",
}


def __getattr__(name):
    module = _MODULES.get(name)
    if module is None:
        raise AttributeError(name)
    cls = getattr(__import__("audioeffects." + module, None, None, [name]), name)
    globals()[name] = cls
    return cls


__all__ = [
    "configure", "sample_rate", "channel_count", "create", "ALL",
    # dynamics
    "Compressor", "Limiter", "Expander", "NoiseGate", "DeEsser",
    "TransientShaper", "MultibandCompressor",
    # eq and filters
    "ParametricEQ", "GraphicEQ", "LowPass", "HighPass", "BandPass",
    "Notch", "LadderFilter", "CombFilter", "DynamicEQ",
    # reverb
    "Reverb", "ConvolutionReverb",
    # delay
    "DigitalDelay", "SlapbackDelay", "TapeDelay", "AnalogDelay",
    "PingPongDelay", "MultiTapDelay",
    # modulation
    "Chorus", "Flanger", "Phaser", "Tremolo", "AutoPan", "Vibrato",
    "RingMod",
    # drive
    "Overdrive", "Distortion", "Fuzz", "Saturation", "Bitcrusher", "Exciter",
    "CabinetSim",
    # pitch and stereo
    "PitchShifter", "Harmonizer", "Octaver", "StereoWidener",
    # racks
    "Rack", "ShimmerHall", "AirSpace",
]


def _is_provider(candidate):
    """Whether `candidate` is one of this package's public effect classes.

    Every class the package ships is a `_component.Component` subclass that
    carries a `NAME`; the base itself is not a provider.
    """
    return (isinstance(candidate, type)
            and candidate is not _component.Component
            and issubclass(candidate, _component.Component)
            and getattr(candidate, "NAME", None) is not None)


def create(name, source, sample_rate, transport=None, **options):
    """Construct the public effect named ``name``.

    This is the effect-side counterpart to ``audioinstruments.create``. The
    selected class's ``create`` method owns the actual construction, so a
    consumer does not need to know which module contains it.
    """
    if name not in _MODULES:
        raise ImportError("audioeffects has no %s" % name)
    cls = __getattr__(name)
    return cls.create(source, sample_rate, transport=transport, **options)


# Stable provider names, not implementation module names. Each class's NAME
# is its class name, so this needs no effect imported.
ALL = tuple(sorted(_MODULES))
