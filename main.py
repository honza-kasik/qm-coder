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

class ProbabilityTable:

    def __init__(self):
        self._index = 0

    def next_lps(self):
        self._index -= presets[self._index][2]

    def next_mps(self):
        self._index += presets[self._index][1]

    def q_e(self):
        return presets[self._index][0]

    def is_mps_switch_needed(self):
        return presets[self._index][2] == -1


class Coder:

    def __init__(self, input, output):
        self._input = input
        self._output = output
        self._p_table = ProbabilityTable()
        self._a = 0xB55A
        self._c = 0x0000
        self._excessive_bits = 15


    def encode(self):
        bits = [1,0,0,0,1,0,0,1,0,0,1,0,1,0,1,0,1,0,1,1,1,1,1,1,1,1,1,1,0] #0b1000100100101
        print(len(bits))
        self._lps = 0
        for bit in bits:
            self._encode_bit(bit)
        return (self._c, self._p_table.q_e(), self._lps, self._excessive_bits)

    def _encode_bit(self, bit):
        if bit == self._lps: #lps
            self._c = self._c + (self._a - self._p_table.q_e())
            self._a = self._p_table.q_e()
            self._renormalize()
            self._do_conditional_exchange_if_needed()
            self._p_table.next_lps()
        else: #mps
            self._a = self._a - self._p_table.q_e()
            if self._a < 0x8000:
                if self._is_conditional_exchange_needed():
                    self._c = self._c + self._a
                    self._a = self._p_table.q_e()
                    self._swap_lps_mps()
                self._renormalize()
                self._do_conditional_exchange_if_needed()
                self._p_table.next_mps()

    def _is_conditional_exchange_needed(self):
        return self._p_table.is_mps_switch_needed()
        #return self._a < self._p_table.q_e()

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

        self._interval_pointer = self._c & 0x7fff #0x7fff - first 15 bits 111 1111 1111 1111
        self._c >>= 15
        self._excessive_bits -= 15
        output = bitarray.bitarray()
        while(self._c > 0):
            print("c:", self._c)
            output.append(self._decode_bit())
        return output

    def _decode_bit(self):
        dividing_line = self._a - self._p_table.q_e()
        print("foo", self._interval_pointer, dividing_line, self._a)
        if self._interval_pointer < dividing_line: #points to the lower interval -> decoded lps
            d = self._lps
            self._interval_pointer = self._interval_pointer - (self._a - self._p_table.q_e())
            self._a = self._p_table.q_e()
            self._renormalize_decode()
            self._do_conditional_exchange_if_needed()
            self._p_table.next_lps()
        else: #points to the upper interval -> decoded mps
            d = self._get_mps()
            self._a = self._a - self._p_table.q_e()
            if self._a < 0x8000:
                if self._is_conditional_exchange_needed():
                    self._interval_pointer = self._interval_pointer + self._a
                    self._a = self._p_table.q_e()
                    self._swap_lps_mps()
                self._renormalize_decode()
                self._do_conditional_exchange_if_needed()
                self._p_table.next_mps()
        return d

    def _renormalize_decode(self):
        while self._a < 0x8000:
            self._a <<= 1
            self._interval_pointer = (self._interval_pointer << 1) | (self._c & 1) #copy new bit from sequence to interval pointer
            self._c >>= 1 #remove bit from sequence
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
