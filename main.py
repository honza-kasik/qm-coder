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

presets2 = [#q_e hexa, next MPS, next LPS, SWITCH
    [0x5608, 1, 0, 1],
    [0x5408, 2, 0, 0],
    [0x5008, 3, 1, 0],
    [0x4808, 4, 2, 0],
    [0x3808, 5, 3, 0],
    [0x3408, 6, 4, 0],
    [0x3008, 7, 5, 0],
    [0x2808, 8, 5, 0],
    [0x2408, 9, 6, 0],
    [0x2208, 10, 7, 0],
    [0x1C08, 11, 8, 0],
    [0x1808, 12, 9, 0],
    [0x1608, 13, 10, 0],
    [0x1408, 14, 11, 0],
    [0x1208, 15, 12, 0],
    [0x0C08, 16, 13, 0],
    [0x0908, 17, 14, 0],
    [0x0708, 18, 15, 0],
    [0x0508, 19, 16, 0],
    [0x0388, 20, 17, 0],
    [0x02C8, 21, 18, 0],
    [0x0298, 22, 19, 0],
    [0x0138, 23, 20, 0],
    [0x00b8, 24, 21, 0],
    [0x0098, 25, 21, 0],
    [0x0058, 26, 23, 0],
    [0x0038, 27, 23, 0],
    [0x0028, 28, 25, 0],
    [0x0018, 29, 25, 0],
    [0x0008, 29, 27, 0]
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

    def is_interval_switch_needed(self):
        return presets[self._index][2] == -1


class ProbabilityTable2:

    def __init__(self):
        self._index = 0

    def next_lps(self):
        self._index = presets2[self._index][2]

    def next_mps(self):
        self._index = presets2[self._index][1]

    def q_e(self):
        return presets2[self._index][0]

    def is_interval_switch_needed(self):
        return presets2[self._index][3] == 1


class Coder:

    def __init__(self, input, output):
        self._input = input
        self._output = output
        self._p_table = ProbabilityTable()
        self._a = 0xAAAA
        self._c = 0x0000
        self._excessive_bits = 15


    def encode(self):
        #bits = [1,0,0,0,1,0,0,1,0,0,1,1,1,1,1,1,0,0,0,0,0] #100010010011111100000
        bits = [1, 0, 1, 1, 1]
        self._lps = 0
        for bit in bits:
            print("encoding", bit)
            self._encode_bit(bit)
        return (self._c, self._p_table.q_e(), self._lps, self._excessive_bits)

    def _encode_bit(self, bit):
        if bit == self._lps: #lps
            self._c = self._c + (self._a - self._p_table.q_e())
            self._a = self._p_table.q_e()
            if self._p_table.is_interval_switch_needed():
                self._swap_lps_mps()
                self._p_table.next_mps()
            else:
                self._p_table.next_lps()
            self._renormalize()
        else: #mps
            self._a = self._a - self._p_table.q_e()
            self._p_table.next_mps()
            if self._a < 0x8000:
                self._renormalize()

    def _is_conditional_exchange_needed(self):
        return self._p_table.is_interval_switch_needed()
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
        print("First interval pointer", self._interval_pointer)
        self._c >>= 15
        self._excessive_bits -= 15
        output = bitarray.bitarray()
        while(self._c > 0):
            print("c:", self._c)
            output.append(self._decode_bit())
        return output

    def _decode_bit(self):
        dividing_line = self._a - self._p_table.q_e()
        print("interval_pointer", self._interval_pointer, "dividing_line", dividing_line, "top_limit", self._a)
        if self._interval_pointer > dividing_line: #points to the upper interval -> decoded lps
            d = self._lps
            self._interval_pointer = self._interval_pointer - (self._a - self._p_table.q_e())
            self._a = self._p_table.q_e()
            if self._is_conditional_exchange_needed():
                self._swap_lps_mps()
                self._p_table.next_mps()
            else:
                self._p_table.next_lps()
            self._renormalize_decode()
        else: #points to the lower interval -> decoded mps
            d = self._get_mps()
            self._a = self._a - self._p_table.q_e()
            self._p_table.next_mps()
            if self._a < 0x8000:
                self._renormalize_decode()
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
    decoded = decoder.decode()
    print(len(decoded), "'", decoded, "'")

if __name__ == "__main__":
    main()
