import unittest
import bitarray
from utils import load_first_x_bits_from_bitarray

class UnitTests(unittest.TestCase):

    def test_bitarray_reader(self):
        bitstring = "010001011101"
        b = bitarray.bitarray(bitstring)
        c = load_first_x_bits_from_bitarray(b, len(bitstring))
        self.assertEqual(int(bitstring, 2), c)

if __name__ == '__main__':
    unittest.main()