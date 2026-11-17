# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT
"""One deliberate type error, which mypy must report: a check that only passes proves nothing."""

import audiocore
import audioeffects

source = audiocore.RawSample(bytearray(960), channel_count=1, sample_rate=48000)
audioeffects.Compressor(source, threshold_db="loud")
