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

from ._component import Component, _AudioSource, _Transport
from .airspace import AirSpace as AirSpace
from .analogdelay import AnalogDelay as AnalogDelay
from .autopan import AutoPan as AutoPan
from .bandpass import BandPass as BandPass
from .bitcrusher import Bitcrusher as Bitcrusher
from .cabinetsim import CabinetSim as CabinetSim
from .chorus import Chorus as Chorus
from .combfilter import CombFilter as CombFilter
from .compressor import Compressor as Compressor
from .convolutionreverb import ConvolutionReverb as ConvolutionReverb
from .deesser import DeEsser as DeEsser
from .digitaldelay import DigitalDelay as DigitalDelay
from .distortion import Distortion as Distortion
from .dynamiceq import DynamicEQ as DynamicEQ
from .exciter import Exciter as Exciter
from .expander import Expander as Expander
from .flanger import Flanger as Flanger
from .fuzz import Fuzz as Fuzz
from .graphiceq import GraphicEQ as GraphicEQ
from .harmonizer import Harmonizer as Harmonizer
from .highpass import HighPass as HighPass
from .ladderfilter import LadderFilter as LadderFilter
from .limiter import Limiter as Limiter
from .lowpass import LowPass as LowPass
from .multibandcompressor import MultibandCompressor as MultibandCompressor
from .multitapdelay import MultiTapDelay as MultiTapDelay
from .noisegate import NoiseGate as NoiseGate
from .notch import Notch as Notch
from .octaver import Octaver as Octaver
from .overdrive import Overdrive as Overdrive
from .parametriceq import ParametricEQ as ParametricEQ
from .phaser import Phaser as Phaser
from .pingpongdelay import PingPongDelay as PingPongDelay
from .pitchshifter import PitchShifter as PitchShifter
from .rack import Rack as Rack
from .reverb import Reverb as Reverb
from .ringmod import RingMod as RingMod
from .saturation import Saturation as Saturation
from .shimmerhall import ShimmerHall as ShimmerHall
from .slapbackdelay import SlapbackDelay as SlapbackDelay
from .stereowidener import StereoWidener as StereoWidener
from .tapedelay import TapeDelay as TapeDelay
from .transientshaper import TransientShaper as TransientShaper
from .tremolo import Tremolo as Tremolo
from .vibrato import Vibrato as Vibrato

__all__ = [
    "configure",
    "sample_rate",
    "channel_count",
    "create",
    "ALL",
    "Compressor",
    "Limiter",
    "Expander",
    "NoiseGate",
    "DeEsser",
    "TransientShaper",
    "MultibandCompressor",
    "ParametricEQ",
    "GraphicEQ",
    "LowPass",
    "HighPass",
    "BandPass",
    "Notch",
    "LadderFilter",
    "CombFilter",
    "DynamicEQ",
    "Reverb",
    "ConvolutionReverb",
    "DigitalDelay",
    "SlapbackDelay",
    "TapeDelay",
    "AnalogDelay",
    "PingPongDelay",
    "MultiTapDelay",
    "Chorus",
    "Flanger",
    "Phaser",
    "Tremolo",
    "AutoPan",
    "Vibrato",
    "RingMod",
    "Overdrive",
    "Distortion",
    "Fuzz",
    "Saturation",
    "Bitcrusher",
    "Exciter",
    "CabinetSim",
    "PitchShifter",
    "Harmonizer",
    "Octaver",
    "StereoWidener",
    "Rack",
    "ShimmerHall",
    "AirSpace",
]

ALL: tuple[str, ...]
"""The name of every effect class, sorted."""

def configure(rate: int, channel_count: int = 2) -> None:
    """Record a default format. Kept for code that calls it; an effect's
    format always comes from its source, so this changes no effect."""

def sample_rate() -> int:
    """The rate `configure()` last recorded (48000 until it is called)."""

def channel_count() -> int:
    """The channel count `configure()` last recorded (2 until it is called)."""

def create(
    name: str,
    source: _AudioSource,
    sample_rate: int,
    transport: _Transport | None = None,
    **options: object,
) -> Component:
    """Construct the public effect named ``name``.

    The selected class's ``create`` method owns the actual construction, so a
    consumer does not need to know which module contains it.
    """
