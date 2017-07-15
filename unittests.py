import unittest
import bitarray
from utils import load_first_x_bits_from_bitarray
from main import Decoder, Encoder

class UnitTests(unittest.TestCase):

    @unittest.skip("testing skipping")
    def test_bitarray_reader(self):
        bitstring = "010001011101"
        b = bitarray.bitarray(bitstring)
        c = load_first_x_bits_from_bitarray(b, len(bitstring))
        self.assertEqual(int(bitstring, 2), c)

    def test_encode_decode(self):
        bitstring = "01000111111111111111111111111111111111111111111111111000000"
        expected_encoded = "010"
        b = bitarray.bitarray(bitstring)
        encoder = Encoder(b)
        encoder.encode()
        encoded = encoder.get_output()
        print(encoded.tolist())
        self.assertGreater(len(bitarray.bitarray(bitstring)), len(encoded))
        decoder = Decoder(encoded)
        decoder.decode()
        decoded = decoder.get_output()
        self.assertEqual(bitarray.bitarray(bitstring), decoded)
