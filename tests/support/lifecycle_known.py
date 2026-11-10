# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""What is red in the lifecycle matrix today, class by class: the rows
`tests/test_lifecycle_matrix.py` holds as KNOWN_RED.

Counted on the quick matrix on CPython, every class the package serves;
recounted for the node level ramps (audiodsp#400). A row is (class NAME, event prefix, property) ->
(red cells in the quick matrix, their digest, the same for the full
matrix or None where it was not counted, reason). Each reason names the
issue that tracks it, or the docstring sentence that states it.
"""

R_JUMP = (
    "a control that jumps hands its node the new value at once, so the"
    " output steps; disclosed in docs/how-it-works/control-smoothing.md."
    " Mix and the levels walk since audiodsp#400; a filter corner, a"
    " switch, a depth, and a patch change's controls other than its levels"
    " still jump, until the later stages there land (audiocomponents#153)")
R_STATE_RAMP = (
    "state that outlives tail_samples, as R_STATE (audiocomponents#155);"
    " and since audiodsp v0.6.6rc9 a filter corner move walks over 20 ms"
    " (#162's fix), so a move and back meets the uninterrupted control up"
    " to 20 ms past the bound, where it used to step")
R_FUZZ_CHARGE = (
    "Fuzz charges its output pole through its shapers when it is built, so"
    " the shapers have played a block before the host's first pull: a Mix,"
    " Level or patch set after the build and before that pull walks over"
    " 20 ms from the built value, where a fresh instance built there starts"
    " at it (the node level ramps, audiodsp#400)")
R_PHASE = (
    "a free-running phase (an LFO, a carrier, a sample-and-hold count)"
    " restarted by a reset or moved by a rate or patch change never meets"
    " the uninterrupted control again; the sound is the same, shifted"
    " (audiocomponents#154)")
R_STATE = (
    "state that outlives tail_samples: a detector re-attacking after a"
    " reset or a rejoin, or a filter's or coupling pole's residue a few"
    " LSB past the declared tail (audiocomponents#155)")
R_FUZZ_LEAN = (
    "the lean shaper follows the patch, so macros moved back after a move"
    " to or from Fuzz - lean stay at that patch's oversampling; with the"
    " coupling residue of #155 elsewhere (audiocomponents#156, #155)")
R_FUZZ_WANDER = (
    "patch 2's Bias -0.85 leaves 6 to 9 LSB out of silence, inside the"
    " 16 LSB wander the class states (audiocomponents#156)")
R_LADDER_OSC = (
    "patch 2, Sustained Sine At Cutoff, self-oscillates on purpose: the"
    " class states it does not hold silence in, silence out there")
R_STATED_P1 = (
    "Listen (DynamicEQ) and Output (Exciter) are stated not to be a"
    " bypass at Mix 0 (audiocomponents#156)")

#: (class NAME, event prefix, property) -> (quick cells, digest, full
#: cells, digest, reason). The full matrix was not counted here (None).
KNOWN_RED = {
    ('AutoPan', 'E1-reset@block', 'P4'): (18, 'a620da1c', None, None, R_PHASE),
    ('AutoPan', 'E1-reset@part', 'P4'): (18, 'a471a429', None, None, R_PHASE),
    ('AutoPan', 'E11-', 'P4'): (2, '56854f54', None, None, R_PHASE),
    ('AutoPan', 'E11-', 'P5'): (2, '087aa9fa', None, None, R_JUMP),
    ('AutoPan', 'E4-', 'P4'): (2, '68d7673d', None, None, R_PHASE),
    ('AutoPan', 'E4-', 'P5'): (12, 'c576f01c', None, None, R_JUMP),
    ('AutoPan', 'E6-', 'P4'): (18, 'ab6136b8', None, None, R_PHASE),
    ('AutoPan', 'E6-', 'P5'): (40, '4a1ecd5f', None, None, R_JUMP),
    ('BandPass', 'E11-', 'P5'): (4, '29718af4', None, None, R_JUMP),
    ('BandPass', 'E2-reset_buffer', 'P4'): (4, '26674fe7', None, None, R_STATE),
    ('BandPass', 'E5-mix0', 'P4'): (4, '3db4de60', None, None, R_STATE),
    ('BandPass', 'E6-', 'P4'): (17, 'c97cd2b1', None, None, R_STATE_RAMP),
    ('BandPass', 'E6-', 'P5'): (12, 'aba60ae5', None, None, R_JUMP),
    ('BandPass', 'E9-', 'P4'): (20, '7c7d321c', None, None, R_STATE),
    ('Bitcrusher', 'E1-reset@block', 'P4'): (16, '0c568ee1', None, None, R_PHASE),
    ('Bitcrusher', 'E1-reset@part', 'P4'): (16, 'efb72d5f', None, None, R_PHASE),
    ('Bitcrusher', 'E11-', 'P4'): (6, 'ddb49c52', None, None, R_PHASE),
    ('Bitcrusher', 'E11-', 'P5'): (8, 'b8cd0394', None, None, R_JUMP),
    ('Bitcrusher', 'E4-', 'P4'): (6, 'bec49683', None, None, R_PHASE),
    ('Bitcrusher', 'E4-', 'P5'): (4, '9c47c5b7', None, None, R_JUMP),
    ('Bitcrusher', 'E5-mix0', 'P4'): (11, '2df8cd4f', None, None, R_PHASE),
    ('Bitcrusher', 'E6-', 'P4'): (48, 'c98676ff', None, None, R_PHASE),
    ('Bitcrusher', 'E6-', 'P5'): (45, '4976f308', None, None, R_JUMP),
    ('Bitcrusher', 'E9-', 'P4'): (75, '73777806', None, None, R_PHASE),
    ('CabinetSim', 'E1-reset@block', 'P4'): (32, 'd4049af3', None, None, R_STATE),
    ('CabinetSim', 'E1-reset@part', 'P4'): (32, '18d29744', None, None, R_STATE),
    ('CabinetSim', 'E11-', 'P4'): (11, '5cfd274d', None, None, R_STATE),
    ('CabinetSim', 'E4-', 'P4'): (19, '8b68cb22', None, None, R_STATE_RAMP),
    ('CabinetSim', 'E5-mix0', 'P4'): (28, 'da1c3f4c', None, None, R_STATE),
    ('CabinetSim', 'E6-', 'P4'): (48, 'b2e9280e', None, None, R_STATE_RAMP),
    ('CabinetSim', 'E6-', 'P5'): (2, 'ce52ab85', None, None, R_JUMP),
    ('CabinetSim', 'E9-', 'P4'): (140, 'a5b3a451', None, None, R_STATE),
    ('Chorus', 'E1-reset@block', 'P4'): (32, '4a87c73b', None, None, R_PHASE),
    ('Chorus', 'E1-reset@part', 'P4'): (32, 'e74bb915', None, None, R_PHASE),
    ('Chorus', 'E11-', 'P4'): (16, 'f8ff4250', None, None, R_PHASE),
    ('Chorus', 'E2-reset_buffer', 'P4'): (32, '44a3e08c', None, None, R_PHASE),
    ('Chorus', 'E4-', 'P4'): (8, '6e4d9f04', None, None, R_PHASE),
    ('Chorus', 'E4-', 'P5'): (6, '7f58228f', None, None, R_JUMP),
    ('Chorus', 'E5-mix0', 'P4'): (13, '55590580', None, None, R_PHASE),
    ('Chorus', 'E6-', 'P4'): (60, '035bcc9f', None, None, R_PHASE),
    ('Chorus', 'E9-', 'P4'): (52, 'a47316fb', None, None, R_PHASE),
    ('CombFilter', 'E11-', 'P5'): (4, 'db431f7a', None, None, R_JUMP),
    ('CombFilter', 'E2-reset_buffer', 'P4'): (2, 'e484c73e', None, None, R_STATE),
    ('CombFilter', 'E4-', 'P4'): (2, '797c2e38', None, None, R_STATE),
    ('CombFilter', 'E4-', 'P5'): (12, '9f58fa94', None, None, R_JUMP),
    ('CombFilter', 'E6-', 'P4'): (17, '3a8a8df8', None, None, R_STATE),
    ('CombFilter', 'E6-', 'P5'): (44, '3b44b8cc', None, None, R_JUMP),
    ('Compressor', 'E1-reset@block', 'P4'): (64, '425ab558', None, None, R_STATE),
    ('Compressor', 'E1-reset@part', 'P4'): (64, '56933d4c', None, None, R_STATE),
    ('Compressor', 'E11-', 'P4'): (8, 'e6342cf4', None, None, R_STATE),
    ('Compressor', 'E11-', 'P5'): (8, 'e77977a7', None, None, R_JUMP),
    ('Compressor', 'E4-', 'P4'): (8, '265bf6d2', None, None, R_STATE),
    ('Compressor', 'E4-', 'P5'): (19, '7fa91f6d', None, None, R_JUMP),
    ('Compressor', 'E5-mix0', 'P4'): (28, 'e7fff304', None, None, R_STATE),
    ('Compressor', 'E6-', 'P4'): (150, 'fa3d35a7', None, None, R_STATE),
    ('Compressor', 'E6-', 'P5'): (162, '8c2759f9', None, None, R_JUMP),
    ('Compressor', 'E9-', 'P4'): (156, '02b3f3c5', None, None, R_STATE),
    ('DeEsser', 'E4-', 'P5'): (10, 'c323d9b3', None, None, R_JUMP),
    ('DeEsser', 'E5-mix0', 'P4'): (2, '8051e9a5', None, None, R_STATE),
    ('DeEsser', 'E9-', 'P4'): (8, '2156c340', None, None, R_STATE),
    ('DeEsser', 'E9-src256', 'P4'): (2, 'a589814f', None, None, R_STATE),
    ('Distortion', 'E1-reset@block', 'P4'): (48, 'd84a1067', None, None, R_STATE),
    ('Distortion', 'E1-reset@part', 'P4'): (48, 'ce661657', None, None, R_STATE),
    ('Distortion', 'E11-', 'P5'): (12, '5be4892b', None, None, R_JUMP),
    ('Distortion', 'E4-', 'P4'): (4, '0f2adcdf', None, None, R_STATE),
    ('Distortion', 'E4-', 'P5'): (4, '909c890f', None, None, R_JUMP),
    ('Distortion', 'E5-mix0', 'P4'): (44, '14ea31c6', None, None, R_STATE),
    ('Distortion', 'E6-', 'P4'): (46, '365ceaaa', None, None, R_STATE),
    ('Distortion', 'E6-', 'P5'): (76, '88dad621', None, None, R_JUMP),
    ('Distortion', 'E9-', 'P4'): (236, 'f3a8ddc3', None, None, R_STATE),
    ('DynamicEQ', 'E1-reset@block', 'P4'): (28, '0b10ffa7', None, None, R_STATE),
    ('DynamicEQ', 'E1-reset@part', 'P4'): (28, '4e33bc13', None, None, R_STATE),
    ('DynamicEQ', 'E11-', 'P4'): (16, 'a0afa5a4', None, None, R_STATE),
    ('DynamicEQ', 'E4-', 'P1'): (4, '65f0c3d8', None, None, R_STATED_P1),
    ('DynamicEQ', 'E4-', 'P4'): (32, 'd84c1f5d', None, None, R_STATE),
    ('DynamicEQ', 'E4-', 'P5'): (4, '50bc4b3a', None, None, R_JUMP),
    ('DynamicEQ', 'E5-mix0', 'P4'): (26, 'e755b82b', None, None, R_STATE),
    ('DynamicEQ', 'E6-', 'P4'): (60, 'e878f970', None, None, R_STATE_RAMP),
    ('DynamicEQ', 'E6-', 'P5'): (12, 'fb7800c3', None, None, R_JUMP),
    ('DynamicEQ', 'E9-', 'P4'): (104, 'eeee87de', None, None, R_STATE),
    ('Exciter', 'E1-reset@block', 'P4'): (32, '2ea00aec', None, None, R_STATE),
    ('Exciter', 'E1-reset@part', 'P4'): (32, '862fb9d8', None, None, R_STATE),
    ('Exciter', 'E11-', 'P4'): (14, '43436585', None, None, R_STATE),
    ('Exciter', 'E4-', 'P1'): (4, '99c82410', None, None, R_STATED_P1),
    ('Exciter', 'E4-', 'P4'): (17, '298025b3', None, None, R_STATE),
    ('Exciter', 'E5-mix0', 'P4'): (32, '93dc7e80', None, None, R_STATE),
    ('Exciter', 'E6-', 'P4'): (68, 'ae6fb523', None, None, R_STATE),
    ('Exciter', 'E6-', 'P5'): (8, '8dcf21c6', None, None, R_JUMP),
    ('Exciter', 'E9-', 'P4'): (160, '4359c45d', None, None, R_STATE),
    ('Expander', 'E1-reset@block', 'P4'): (16, '374c116a', None, None, R_STATE),
    ('Expander', 'E1-reset@part', 'P4'): (16, '5e4aff57', None, None, R_STATE),
    ('Expander', 'E11-', 'P5'): (4, '83adb352', None, None, R_JUMP),
    ('Expander', 'E2-reset_buffer', 'P4'): (16, 'ed5b5919', None, None, R_STATE),
    ('Expander', 'E4-', 'P5'): (8, '0de52e7a', None, None, R_JUMP),
    ('Expander', 'E6-', 'P4'): (6, '2c2c6b3a', None, None, R_STATE),
    ('Fuzz', 'E10-', 'P4'): (16, 'c7e49d06', None, None, R_FUZZ_CHARGE),
    ('Fuzz', 'E10-macros', 'P4'): (4, '92e3f2ae', None, None, R_STATE),
    ('Fuzz', 'E10-mix0', 'P3'): (4, '1c2a8dc6', None, None, R_FUZZ_WANDER),
    ('Fuzz', 'E10-patch', 'P3'): (4, '617e432c', None, None, R_FUZZ_WANDER),
    ('Fuzz', 'E10-patch', 'P4'): (20, '9cadc2f0', None, None, R_FUZZ_LEAN),
    ('Fuzz', 'E10-reset', 'P4'): (4, '0785c28c', None, None, R_STATE),
    ('Fuzz', 'E11-', 'P4'): (16, '67c5faea', None, None, R_FUZZ_LEAN),
    ('Fuzz', 'E12-', 'P4'): (20, '05d517b6', None, None, R_FUZZ_CHARGE),
    ('Fuzz', 'E12-', 'PF'): (20, '86e47d09', None, None, R_FUZZ_CHARGE),
    ('Fuzz', 'E4-', 'P4'): (32, 'd667b376', None, None, R_STATE),
    ('Fuzz', 'E4-', 'P5'): (4, 'eb979d08', None, None, R_JUMP),
    ('Fuzz', 'E5-mix0', 'P3'): (4, '785ac763', None, None, R_FUZZ_WANDER),
    ('Fuzz', 'E5-mix0', 'P4'): (36, '70f1f6b6', None, None, R_STATE),
    ('Fuzz', 'E5-mix0', 'P5'): (10, '0df66d65', None, None, R_JUMP),
    ('Fuzz', 'E6-', 'P3'): (8, 'f027b35d', None, None, R_FUZZ_WANDER),
    ('Fuzz', 'E6-', 'P4'): (89, '6d78d82a', None, None, R_FUZZ_LEAN),
    ('Fuzz', 'E6-', 'P5'): (24, 'abac2451', None, None, R_JUMP),
    ('Fuzz', 'E9-', 'P3'): (16, 'a4652cfe', None, None, R_FUZZ_WANDER),
    ('Fuzz', 'E9-', 'P4'): (192, '1cf6be45', None, None, R_STATE),
    ('Fuzz', 'E9-', 'P5'): (26, '95969050', None, None, R_JUMP),
    ('GraphicEQ', 'E11-', 'P5'): (4, '1805e152', None, None, R_JUMP),
    ('GraphicEQ', 'E2-reset_buffer', 'P4'): (12, '17431038', None, None, R_STATE),
    ('GraphicEQ', 'E4-', 'P5'): (54, 'f206751b', None, None, R_JUMP),
    ('GraphicEQ', 'E6-', 'P4'): (28, 'df3917fc', None, None, R_STATE),
    ('GraphicEQ', 'E6-', 'P5'): (60, 'fc0f3765', None, None, R_JUMP),
    ('HighPass', 'E1-reset@block', 'P4'): (21, 'd9891c63', None, None, R_STATE),
    ('HighPass', 'E1-reset@part', 'P4'): (21, 'af7690b3', None, None, R_STATE),
    ('HighPass', 'E11-', 'P4'): (15, '1113f5a1', None, None, R_STATE),
    ('HighPass', 'E11-', 'P5'): (12, '4a25493b', None, None, R_JUMP),
    ('HighPass', 'E2-reset_buffer', 'P4'): (8, 'd1d172ed', None, None, R_STATE),
    ('HighPass', 'E4-', 'P4'): (16, 'd39c8c68', None, None, R_STATE),
    ('HighPass', 'E4-', 'P5'): (4, '8fe22ac6', None, None, R_JUMP),
    ('HighPass', 'E5-mix0', 'P4'): (11, '227acce3', None, None, R_STATE),
    ('HighPass', 'E6-', 'P4'): (53, 'e040235e', None, None, R_STATE_RAMP),
    ('HighPass', 'E6-', 'P5'): (24, '65a9c1f9', None, None, R_JUMP),
    ('HighPass', 'E9-', 'P4'): (55, '95a58d3e', None, None, R_STATE),
    ('LadderFilter', 'E10-mix0', 'P3'): (4, 'b6574e03', None, None, R_LADDER_OSC),
    ('LadderFilter', 'E2-reset_buffer', 'P4'): (2, 'f71d78d2', None, None, R_STATE),
    ('LadderFilter', 'E4-', 'P5'): (22, '62ce6690', None, None, R_JUMP),
    ('LadderFilter', 'E5-mix0', 'P3'): (4, '5df6ec0e', None, None, R_LADDER_OSC),
    ('LadderFilter', 'E5-mix0', 'P5'): (30, '87c00d0a', None, None, R_JUMP),
    ('LadderFilter', 'E6-', 'P4'): (4, 'b99eecc4', None, None, R_STATE),
    ('LadderFilter', 'E6-', 'P5'): (58, 'f6d58cc2', None, None, R_JUMP),
    ('LadderFilter', 'E9-', 'P3'): (16, '4978cfa6', None, None, R_LADDER_OSC),
    ('LadderFilter', 'E9-', 'P5'): (150, '638865df', None, None, R_JUMP),
    ('Limiter', 'E11-', 'P5'): (4, '3b25af0f', None, None, R_JUMP),
    ('Limiter', 'E4-', 'P5'): (12, 'c136df4f', None, None, R_JUMP),
    ('Limiter', 'E6-', 'P4'): (6, '6dd682df', None, None, R_STATE),
    ('Limiter', 'E6-', 'P5'): (64, '851616ce', None, None, R_JUMP),
    ('LowPass', 'E11-', 'P5'): (4, '001c564d', None, None, R_JUMP),
    ('LowPass', 'E2-reset_buffer', 'P4'): (8, '960b8f7c', None, None, R_STATE),
    ('LowPass', 'E5-mix0', 'P4'): (12, 'deb21c7a', None, None, R_STATE),
    ('LowPass', 'E5-mix0', 'P5'): (2, '98a49ec8', None, None, R_JUMP),
    ('LowPass', 'E6-', 'P4'): (20, '48ecf86c', None, None, R_STATE_RAMP),
    ('LowPass', 'E6-', 'P5'): (16, 'aa06899d', None, None, R_JUMP),
    ('LowPass', 'E9-', 'P4'): (60, '7c0a5b65', None, None, R_STATE),
    ('LowPass', 'E9-', 'P5'): (10, '2d3f6552', None, None, R_JUMP),
    ('MultibandCompressor', 'E1-reset@block', 'P4'): (18, '2ff6f235', None, None, R_STATE),
    ('MultibandCompressor', 'E1-reset@part', 'P4'): (18, '79006c73', None, None, R_STATE),
    ('MultibandCompressor', 'E11-', 'P4'): (12, 'cdb143fb', None, None, R_STATE_RAMP),
    ('MultibandCompressor', 'E11-', 'P5'): (8, 'b97c4673', None, None, R_JUMP),
    ('MultibandCompressor', 'E4-', 'P4'): (11, '0fa1b121', None, None, R_STATE_RAMP),
    ('MultibandCompressor', 'E4-', 'P5'): (19, 'f45b7444', None, None, R_JUMP),
    ('MultibandCompressor', 'E5-mix0', 'P4'): (10, '5536d0f1', None, None, R_STATE),
    ('MultibandCompressor', 'E6-', 'P4'): (40, '77eac701', None, None, R_STATE_RAMP),
    ('MultibandCompressor', 'E6-', 'P5'): (46, '46adef16', None, None, R_JUMP),
    ('MultibandCompressor', 'E9-', 'P4'): (40, '9221d3e1', None, None, R_STATE),
    ('NoiseGate', 'E1-reset@block', 'P4'): (14, '8e201f94', None, None, R_STATE),
    ('NoiseGate', 'E1-reset@part', 'P4'): (14, 'b8240548', None, None, R_STATE),
    ('NoiseGate', 'E2-reset_buffer', 'P4'): (10, '5e5004a0', None, None, R_STATE),
    ('NoiseGate', 'E4-', 'P5'): (4, '00a5daae', None, None, R_JUMP),
    ('Notch', 'E11-', 'P5'): (4, '795303da', None, None, R_JUMP),
    ('Notch', 'E4-', 'P5'): (4, '19e73042', None, None, R_JUMP),
    ('Notch', 'E5-mix0', 'P4'): (8, '0822c04f', None, None, R_STATE),
    ('Notch', 'E6-', 'P4'): (24, '6d9aa0d4', None, None, R_STATE_RAMP),
    ('Notch', 'E6-', 'P5'): (44, 'ec221fd4', None, None, R_JUMP),
    ('Notch', 'E9-', 'P4'): (40, '1b5d55d5', None, None, R_STATE),
    ('Overdrive', 'E1-reset@block', 'P4'): (34, 'aaf11cd2', None, None, R_STATE),
    ('Overdrive', 'E1-reset@part', 'P4'): (34, '75164359', None, None, R_STATE),
    ('Overdrive', 'E10-macros', 'P4'): (2, '0af84d6b', None, None, R_STATE),
    ('Overdrive', 'E10-patch', 'P4'): (2, '9ee38023', None, None, R_STATE),
    ('Overdrive', 'E10-reset', 'P4'): (4, '34caff5e', None, None, R_STATE),
    ('Overdrive', 'E11-', 'P4'): (8, '294ebbde', None, None, R_STATE),
    ('Overdrive', 'E11-', 'P5'): (2, 'ec676210', None, None, R_JUMP),
    ('Overdrive', 'E4-', 'P4'): (16, 'b10db851', None, None, R_STATE),
    ('Overdrive', 'E5-mix0', 'P4'): (18, '60d901f0', None, None, R_STATE),
    ('Overdrive', 'E6-', 'P4'): (44, 'f84cecd5', None, None, R_STATE),
    ('Overdrive', 'E6-', 'P5'): (9, '59322590', None, None, R_JUMP),
    ('Overdrive', 'E9-', 'P4'): (90, 'e2899302', None, None, R_STATE),
    ('ParametricEQ', 'E11-', 'P5'): (2, '1a3d01df', None, None, R_JUMP),
    ('ParametricEQ', 'E6-', 'P4'): (15, '05c0db34', None, None, R_STATE_RAMP),
    ('ParametricEQ', 'E6-', 'P5'): (10, '19891537', None, None, R_JUMP),
    ('Phaser', 'E1-reset@block', 'P4'): (40, 'eca258f1', None, None, R_PHASE),
    ('Phaser', 'E1-reset@part', 'P4'): (40, '54e5b3be', None, None, R_PHASE),
    ('Phaser', 'E11-', 'P4'): (16, '3eec4c9a', None, None, R_PHASE),
    ('Phaser', 'E11-', 'P5'): (8, '2408ab3c', None, None, R_JUMP),
    ('Phaser', 'E4-', 'P4'): (24, '7eca4736', None, None, R_PHASE),
    ('Phaser', 'E4-', 'P5'): (14, '3c192f73', None, None, R_JUMP),
    ('Phaser', 'E6-', 'P4'): (76, '520373a6', None, None, R_PHASE),
    ('Phaser', 'E6-', 'P5'): (84, 'e9989249', None, None, R_JUMP),
    ('RingMod', 'E1-reset@block', 'P4'): (40, '5f037604', None, None, R_PHASE),
    ('RingMod', 'E1-reset@part', 'P4'): (40, '4cdc6f50', None, None, R_PHASE),
    ('RingMod', 'E11-', 'P4'): (16, 'fb67e9fc', None, None, R_PHASE),
    ('RingMod', 'E11-', 'P5'): (8, '739846f9', None, None, R_JUMP),
    ('RingMod', 'E4-', 'P4'): (8, '97e3e000', None, None, R_PHASE),
    ('RingMod', 'E4-', 'P5'): (30, '289d459f', None, None, R_JUMP),
    ('RingMod', 'E5-mix0', 'P5'): (28, 'c504653d', None, None, R_JUMP),
    ('RingMod', 'E6-', 'P4'): (96, '862d0a32', None, None, R_PHASE),
    ('RingMod', 'E6-', 'P5'): (44, 'aefba1ae', None, None, R_JUMP),
    ('RingMod', 'E9-', 'P5'): (140, 'f09d9cee', None, None, R_JUMP),
    ('Saturation', 'E11-', 'P5'): (8, 'd037b49c', None, None, R_JUMP),
    ('Saturation', 'E4-', 'P5'): (28, 'b87df81b', None, None, R_JUMP),
    ('Saturation', 'E6-', 'P5'): (94, 'c9c25f1c', None, None, R_JUMP),
    ('TransientShaper', 'E11-', 'P5'): (8, '24eee129', None, None, R_JUMP),
    ('TransientShaper', 'E2-reset_buffer', 'P4'): (22, 'bee31922', None, None, R_STATE),
    ('TransientShaper', 'E4-', 'P5'): (8, '60441386', None, None, R_JUMP),
    ('TransientShaper', 'E6-', 'P4'): (22, 'a20cab27', None, None, R_STATE),
    ('TransientShaper', 'E6-', 'P5'): (50, '554a84b9', None, None, R_JUMP),
    ('Tremolo', 'E11-', 'P4'): (12, 'eedd0ced', None, None, R_PHASE),
    ('Tremolo', 'E11-', 'P5'): (4, 'dc306763', None, None, R_JUMP),
    ('Tremolo', 'E4-', 'P4'): (12, '058ac2bd', None, None, R_PHASE),
    ('Tremolo', 'E4-', 'P5'): (4, '034d4667', None, None, R_JUMP),
    ('Tremolo', 'E6-', 'P4'): (96, 'cf3d5954', None, None, R_PHASE),
    ('Tremolo', 'E6-', 'P5'): (33, 'dc1bc985', None, None, R_JUMP),
    ('Vibrato', 'E11-', 'P4'): (12, '4204b137', None, None, R_PHASE),
    ('Vibrato', 'E2-reset_buffer', 'P4'): (32, 'a6de06f2', None, None, R_PHASE),
    ('Vibrato', 'E4-', 'P4'): (8, 'f6a551f6', None, None, R_PHASE),
    ('Vibrato', 'E4-', 'P5'): (2, 'e006a60f', None, None, R_JUMP),
    ('Vibrato', 'E6-', 'P4'): (52, 'b9c53ae9', None, None, R_PHASE),
}

#: CircuitPython's own nodes answer the host's `reset_buffer` differently
#: from audiodsp's port, so E2 renders other bytes there with the same
#: verdicts (audiocomponents#158). class -> (quick cells, digest, full
#: cells, digest, reason).
_CP_RESET_BUFFER = (
    "CircuitPython's own nodes answer the host's reset_buffer differently"
    " from audiodsp's port: other bytes, the same verdicts"
    " (audiocomponents#158)")
KNOWN_P6 = {
    "Compressor": (4, "70d574f2", None, None, _CP_RESET_BUFFER),
    "Distortion": (48, "950b4395", None, None, _CP_RESET_BUFFER),
    "Exciter": (32, "4f3d4cfb", None, None, _CP_RESET_BUFFER),
    "MultibandCompressor": (5, "83a48f4f", None, None, _CP_RESET_BUFFER),
    "Overdrive": (18, "ae64809f", None, None, _CP_RESET_BUFFER),
}
