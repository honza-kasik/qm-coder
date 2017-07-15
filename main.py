import bitarray
import math
import argparse
from ctypes import *
from utils import load_first_x_bits_from_bitarray
from utils import write_bitarray_to_file
from loggingconf import logger


presets = [#q_e, mps_inc, lps_dec
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
        self._index -= presets[self._index][2]
        logger.debug("Moved to next LPS, current index is %i", self._index)

    def next_mps(self):
        self._index += presets[self._index][1]
        logger.debug("Moved to next MPS, current index is %i", self._index)

    def q_e(self):
        return presets[self._index][0]

    def is_interval_switch_needed(self):
        return presets[self._index][2] == -1

class Encoder:

    def __init__(self, input):
        self._input = input
        logger.debug("Loaded bitarray with endianity '%s' and lenght '%i'", self._input.endian(), len(self._input))
        self._p_table = ProbabilityTable()
        self._a = c_uint16(0xb55a)
        self._c = c_uint16(0x0000)
        self._out = bitarray.bitarray()

    def encode(self):
        self._lps = 1
        try:
            while(True):
                bit = self._input.pop(0)
                logger.info("Encoding bit!")
                self._encode_bit(bit)
        except IndexError:
            pass #ignored - end of bits to encode
        self._out.append(1)

    def _encode_bit(self, bit):
        if bit == self._lps:
            self._code_lps()
        else:
            self._code_mps()

    def _q_e(self):
        return self._p_table.q_e()

    def _code_mps(self):
        """
        bit is more probable symbol, C is kept as is (bottom of MPS subinterval), interval A is shrunk to size of MPS
        subinterval
        """
        self._a = c_uint16(self._a.value - self._q_e())
        if self._a.value < 0x8000:
            self._switch_intervals_if_needed()
            self._renormalize()
            self._p_table.next_mps()
        logger.debug("Coded MPS")

    def _code_lps(self):
        """
        bit is less probable symbol, bottom of LPS subinterval is added to C and interval A is shrunk to size of LPS
        subinterval
        :return:
        """
        self._c = c_uint16(self._c.value + self._a.value - self._q_e())
        self._a = c_uint16(self._q_e())
        self._switch_intervals_if_needed()
        self._renormalize()
        self._p_table.next_lps()
        logger.debug("Coded LPS")

    def _renormalize(self):
        while self._a.value < 0x8000:
            #C < 0,5 (0xFFFF / 2)
            logger.debug("C value is '%s'", hex(self._c.value))
            logger.debug("A value is '%s'", hex(self._a.value))
            if self._c.value < 0x5555:
                b = 0
                d = 0
            else:
                b = 1
                d = 0x5555
            self._write_bit(b)
            logger.debug("Written '%i' to output", b)
            #C = 2 * (C - D)
            self._c = c_uint16((self._c.value - d) << 1)
            logger.debug("C value is '%s'", hex(self._c.value))
            #A = 2 * A
            self._a = c_uint16(self._a.value << 1)

    def _switch_intervals_if_needed(self):
        """
        Conditional exchange if needed - if LPS subinterval becomes greater than LPS subinterval. This means, that
        "less probable symbol" would be more probable than "more probable symbol", so switch takes place.
        """
        #logger.debug("Should be switched according to values? '%s'", str(self._q_e() > self._a.value - self._q_e()))
        if self._p_table.is_interval_switch_needed():
            #self._a, self._c = self._c, self._a
            self._lps = not(self._lps)
            logger.debug("Switched intervals! LPS is now '%i'!", self._lps)


    def _write_bit(self, bit):
        self._out.append(bit)

    def get_output(self) -> bitarray:
        return self._out

class Decoder:

    def __init__(self, input):
        self._a = c_uint16(0xAAAA)
        self._c = c_uint16(0x0000)
        self._input = input
        self._p_table = ProbabilityTable()
        self._out = bitarray.bitarray()
        self._lps = 1
        self._interval_pointer = c_uint16(self._load_int_from_bitarray(self._input))
        logger.debug("Loaded '%i' as interval pointer, bin: '%s'", self._interval_pointer.value, str(hex(self._interval_pointer.value)))

    def decode(self):
        while self._input.length() > 0:
            dividing_line = self._a.value - self._q_e()
            if self._interval_pointer.value > dividing_line:
                self._decoded_lps()
                logger.debug("Decoded LPS!")
            else:
                self._decoded_mps()
                logger.debug("Decoded MPS!")

    def _decoded_lps(self):
        self._write_bit(self._lps)
        self._c = c_uint16(self._c.value - self._a.value - self._q_e())
        self._a = c_uint16(self._q_e())
        self._renormalize()
        self._p_table.next_lps()

    def _decoded_mps(self):
        self._write_bit(not(self._lps))
        self._a = c_uint16(self._a.value - self._q_e())
        if self._a.value < 0x8000:
            self._renormalize()
            self._p_table.next_mps()

    def _renormalize(self):
        logger.debug("Renormalizing!")

        if self._p_table.is_interval_switch_needed():
            self._lps = not(self._lps)

        logger.debug("C value is '%s'", hex(self._c.value))
        logger.debug("A value is '%s'", hex(self._a.value))

        while self._a.value < 0x8000:
            if self._c.value < 0x5555:
                d = 0
            else:
                d = 0x5555
            #C = 2 * (C - D)
            self._c = c_uint16((self._c.value - d) << 1)
            #A = 2 * A
            self._a = c_uint16(self._a.value << 1)
            self._load_next_bit_to_interval_pointer(self._input, d)

    def _load_next_bit_to_interval_pointer(self, bitarr: bitarray, d: int):
        try:
            b = bitarr.pop(0)
        except IndexError:
            b = 0
        self._interval_pointer = c_uint16(((self._interval_pointer.value - d) << 1) + b)
        logger.debug("Interval pointer is '%i'", self._interval_pointer.value)

    def _load_int_from_bitarray(self, bitarr):
        bit_count = self._rounded_log_base_2(self._q_e())
        return load_first_x_bits_from_bitarray(bitarr, bit_count)

    def _q_e(self):
        return self._p_table.q_e()

    def _write_bit(self, bit):
        self._out.append(bit)

    def _rounded_log_base_2(self, number):
        return int(math.ceil(math.log(number, 2)))

    def get_output(self) -> bitarray:
        return self._out

def _encode(input_path, output_path):
    input = bitarray.bitarray()
    input.fromfile(input_path)
    coder = Encoder(input)
    coder.encode()
    write_bitarray_to_file(coder.get_output(), output_path)

def _decode(input_path, output_path):
    input = bitarray.bitarray()
    input.fromfile(input_path)
    decoder = Decoder(input)
    decoder.decode()
    write_bitarray_to_file(decoder.get_output(), output_path)

def main():
    parser = argparse.ArgumentParser(description='QM encoder/decoder')
    parser.add_argument("mode", type=str, choices=["encode", "decode"],
                        help="set mode, encode for encoding, decode for decoding")
    parser.add_argument("input", type=str,
                        help="path to input file")
    parser.add_argument("output", type=str,
                        help="path to output file")

    args = parser.parse_args()

    if args.mode == 'encode':
         _encode(args.input, args.output)
    else:
        _decode(args.input, args.output)


if __name__ == "__main__":
    main()
