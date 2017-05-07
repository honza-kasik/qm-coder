import bitarray

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

class Coder:

    def __init__(self, input, output):
        self._input = input
        self._output = output
        self._qe_index = 0
        self._a = 0xB55A
        self._c = 0x0000
        self._q_e = presets[self._qe_index][0]
        self._excessive_bits = 15


    def encode(self):
        bits = bitarray.bitarray()
        with open(self._input, 'rb') as file:
            bits.fromfile(file)

        if bits.count(0) > bits.count(1):
            self._lps = 1
        else:
            self._lps = 0

        try:
            while(True):
                self._encode_bit(bits.pop())
        except IndexError:
            print("End of bits! All should be compressed with ", self._excessive_bits, " excessive bits!")
            return (self._c, self._q_e, self._lps, self._excessive_bits)

    def _encode_bit(self, bit):
        if bit == self._lps:
            self._c = self._c + self._a - self._q_e
            print(self._c, self._a)
            self._a = self._q_e
            self._renormalize()
            self._adjust_q_e(True)
        else:
            self._a = self._a - self._q_e
            if self._a < 0x8000:
                self._renormalize()
                self._adjust_q_e(False)

    def _adjust_q_e(self, is_lps):
        if is_lps:
            self._qe_index -= presets[self._qe_index][2]
            self._q_e = presets[self._qe_index][0]
            # conditional exchange
            self._do_conditional_exchange_if_needed()
        else:
            self._qe_index += presets[self._qe_index][1]
            self._q_e = presets[self._qe_index][0]

    def _is_conditional_exchange_needed(self):
        return presets[self._qe_index][2] == -1

    def _do_conditional_exchange_if_needed(self):
        if self._is_conditional_exchange_needed():
            self._swap_lps_mps()

    def _renormalize(self):
        while self._a < 0x8000:
            self._a <<= 1
            self._c <<= 1
            self._excessive_bits += 1

    def _swap_lps_mps(self):
        self._lps = self._get_mps()

    def _get_mps(self):
        if self._lps == 1:
            return 0
        else:
            return 1

    def decode(self):
        self._c = self._input[0]
        print("c:", self._c)

        self._lps = self._input[2]
        self._excessive_bits = self._input[3]

        self._decoded_value = self._c & 0x7fff #0x7fff - first 15 bits
        self._c >>= 15
        self._excessive_bits -= 15
        output = bitarray.bitarray()
        while(self._c > 0):
            #print("c:", self._c)
            output.append(self._decode_bit())
        return output

    def _decode_bit(self):
        dividing_line = self._a - self._q_e
        if self._decoded_value < dividing_line:
            d = self._get_mps()
            self._a -= self._q_e
            self._qe_index += presets[self._qe_index][1]
            self._q_e = presets[self._qe_index][0]
            if self._a < 0x8000:
                self._renormalize_decode()
        else:
            print("BAR")
            d = self._lps
            self._decoded_value -= dividing_line
            self._a = self._q_e
            if self._is_conditional_exchange_needed():
                self._swap_lps_mps()
                self._qe_index += presets[self._qe_index][1]
            else:
                self._qe_index -= presets[self._qe_index][2]
            self._q_e = presets[self._qe_index][0]
            self._renormalize_decode()
        return d

    def _renormalize_decode(self):
        while self._a < 0x8000:
            self._a <<= 1
            self._decoded_value = (self._decoded_value << 1) | (self._c & 1)
            self._c >>= 1
            self._excessive_bits -= 1

def main():
    coder = Coder("test.txt", "foo")
    coded = coder.encode()
    print(coded)
    decoder = Coder(coded, "foo")
    print("decoding: ", coded)
    print("'", decoder.decode(), "'")

if __name__ == "__main__":
    main()
