import bitarray

import logging
logger = logging.getLogger(__name__)

def load_first_x_bits_from_bitarray(b: bitarray, bit_count):
    """Get x highest bits to form a bitarray"""
    c = 0
    for i in range(bit_count, 0, -1):
        top_bit = b.pop(0)
        logger.debug("Read %i", top_bit)
        c |= (top_bit << i)
        logger.debug("New value: %s", str(bin(c)))
    return c >> 1

def write_bitarray_to_file(b: bitarray, path: str):
    with open(path, 'wb') as file:
        b.tofile(file)

def load_bitarray_from_file(path: str) -> bitarray:
    input = bitarray.bitarray()
    with open(path, 'rb') as file:
        input.fromfile(file)
    return input
