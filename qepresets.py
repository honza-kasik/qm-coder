import logging
logger = logging.getLogger(__name__)

_presets = [#q_e, mps_inc, lps_dec
    [0x59EB, 1, -1],
    [0x5522, 1, 1],
    [0x504F, 1, 1],
    [0x4B85, 1, 1],
    [0x4639, 1, 1],
    [0x415E, 1, 1],
    [0x3C3D, 1, 1],
    [0x375E, 1, 1],
    [0x32B4, 1, 2],
    [0x2E17, 1, 1],
    [0x299A, 1, 2],
    [0x2516, 1, 1],
    [0x1EDF, 1, 1],
    [0x1AA9, 1, 2],
    [0x174E, 1, 1],
    [0x1424, 1, 2],
    [0x119C, 1, 1],
    [0x0F6B, 1, 2],
    [0x0D51, 1, 2],
    [0x0BB6, 1, 1],
    [0x0A40, 1, 2],
    [0x0861, 1, 2],
    [0x0706, 1, 2],
    [0x05CD, 1, 2],
    [0x04DE, 1, 1],
    [0x040F, 1, 2],
    [0x0363, 1, 2],
    [0x02D4, 1, 2],
    [0x025C, 1, 2],
    [0x01F8, 1, 2],
    [0x01A4, 1, 2],
    [0x0160, 1, 2],
    [0x0125, 1, 2],
    [0x00F6, 1, 2],
    [0x00CB, 1, 2],
    [0x00AB, 1, 1],
    [0x008F, 1, 2],
    [0x0068, 1, 2],
    [0x004E, 1, 2],
    [0x003B, 1, 2],
    [0x002C, 1, 2],
    [0x001A, 1, 3],
    [0x000D, 1, 2],
    [0x0006, 1, 2],
    [0x0003, 1, 2],
    [0x0001, 0, 1]
]

class ProbabilityTable:

    def __init__(self):
        self._index = 0

    def next_lps(self):
        self._index -= _presets[self._index][2]
        logger.debug("Moved to next LPS, current index is %i", self._index)

    def next_mps(self):
        self._index += _presets[self._index][1]
        logger.debug("Moved to next MPS, current index is %i", self._index)

    def q_e(self):
        return _presets[self._index][0]

    def is_interval_switch_needed(self):
        return _presets[self._index][2] == -1