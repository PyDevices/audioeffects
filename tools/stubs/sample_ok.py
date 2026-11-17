# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT
"""What a user writes against the stubs: mypy must accept it."""

import audiocore
import audioeffects

source = audiocore.RawSample(bytearray(960), channel_count=1, sample_rate=48000)
comp = audioeffects.Compressor(source, threshold_db=-20, ratio=3)
comp.set_macro(0, 96)
tail: int | None = audioeffects.Reverb(comp.output, decay=2.4).tail_samples
