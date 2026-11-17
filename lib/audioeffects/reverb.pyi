# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT
from typing import Any

from . import _component
from ._component import _AudioSource, _Transport

VENDOR: str
REF_RATE: float
DATTORRO_LINES: tuple[int, ...]
DATTORRO_TAPS: tuple[tuple[float, ...], ...]
CHARACTERS: tuple[str, ...]
PLATE: int
ROOM: int
CHAMBER: int
HALL: int
RATIOS: tuple[tuple[float, ...], ...]
KAPPA: tuple[float, ...]
LF_CAP: float
MIN_LINE: int
MAX_PREDELAY_MS: float
CHARACTER_MIDI: tuple[int, ...]
DAMPER_LONG_S: float
DAMPER_SHORT_S: float
DECAY_HZ: float
CHARACTER_I: int
DECAY_I: int
SIZE_I: int
PREDELAY_I: int
DIFFUSION_I: int
DAMPING_I: int
BANDWIDTH_I: int
LOW_CUT_I: int
MOD_DEPTH_I: int
MOD_RATE_I: int
WIDTH_I: int
TONE_I: int
MIX_I: int
DEFAULTS: tuple[float, ...]

def line_set(index: int, size, sample_rate: int, ratios=None) -> Any:
    """The twelve line lengths, in frames, of character `index` at `size`
    and `sample_rate`: round(n x fs / 29 761 x size x r) per line."""

def tap_table(index: int, size, sample_rate: int, ratios=None, lines=None) -> Any:
    """The fourteen taps, flattened as the Tank takes them: each offset
    scaled by its own line's factor and held under that line's length."""

def half_periods(lines) -> Any:
    """Frames around each half of the figure-eight: lines 4-7 and 8-11."""

def one_pole_mag(corner_hz: float, frequency, sample_rate: int) -> float:
    """|H| at `frequency` of the node's loop one-pole, whose coefficient is
    1 - exp(-2 pi corner / fs)."""

def damper_hz(decay_s: float, damping_hz: float, sample_rate: int) -> float:
    """The plate's loop corner at a Decay: 0.98 x Nyquist at 8 s and above,
    `damping_hz` at 1 s and below, geometric in log Decay between."""

def decay_law(kappa: float, lines, sample_rate: int, decay_s: float, loop_hz: float) -> Any:
    """The Tank's `decay` for a T60 of `decay_s` at 500 Hz.

    One pass through a half multiplies by `decay` twice, the cross-feed
    read and the in-loop multiply (`audiodsp_tank.c:537-538`, `:552`), and
    the loop one-pole once, so

        decay = min(10^(-3 k P / (2 T fs)) / sqrt|H(500 Hz)|,
                    10^(-3 k P / (2 x 1.5 T fs)))

    with P the mean half period in frames. The first term lifts `decay` by
    the one-pole's loss at 500 Hz; the second caps the bass (where the
    one-pole is 1) at 1.5 x T. Returns (decay, capped, t_lf): `t_lf` is the
    low-frequency T60 the handed decay gives, which bounds the tail."""

def tail_frames(sample_rate: int, predelay_ms: float, t_lf, size) -> int:
    """Tier 3's bound: ceil(fs x (Predelay + 1.6 x max(1.2 x T_lf,
    1.5 x Size)))."""

class Reverb(_component.Component):
    """Dattorro's network as four machines: an EMT plate that is dense at
    once and darkens as Decay shortens, and a room, chamber and hall that
    build. The module docstring is the player's page."""

    NAME: str
    DISPLAY_NAME: str
    CATEGORIES: tuple[str, ...]
    VERSION: str
    TIER: str
    REQUIRES: tuple[str, ...]
    CAPABILITIES: tuple[str, ...]
    LATENCY_SAMPLES: int
    TAIL_SAMPLES: int | None
    INPUT_CEILING_DBFS: int
    MACRO_LABELS: tuple[str, ...]
    MACRO_MODES: dict[int, str]
    PATCHES: dict[int, tuple[str, tuple[float, ...]]]

    def __init__(
        self,
        source: _AudioSource,
        character: float | str = "plate",
        decay: float = 2.4,
        size: float = 1.0,
        predelay_ms: float = 0.0,
        diffusion: float = 0.75,
        damping_hz: float = 1000.0,
        bandwidth_hz: float = 12000.0,
        low_cut_hz: float = 40.0,
        mod_depth_ms: float = 0.27,
        mod_rate_hz: float = 1.0,
        width: float = 1.0,
        tone_db: float = 0.0,
        mix: float = 0.35,
        patch: int | None = None,
        *,
        sample_rate: int | None = None,
        transport: _Transport | None = None,
    ) -> None: ...
    @property
    def tail_samples(self) -> int | None:
        """Frames until the output is exactly zero once the input stops, as
        an upper bound (the dossier's Tier 3): the low-frequency T60 the
        handed `decay` gives, x 1.2 for the law's error, or 1.5 x Size for
        the character's own ringing, whichever is longer, x 1.6, plus the
        predelay."""
