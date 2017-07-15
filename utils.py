import bitarray
from loggingconf import logger

def load_first_x_bits_from_bitarray(b: bitarray, bit_count):
    """Get x highest bits to form a bitarray"""
    c = 0
    for i in range(bit_count, 0, -1):
        top_bit = b.pop(0)
        logger.debug("Read %i", top_bit)
        c |= (top_bit << i)
        logger.debug("New value: %s", str(bin(c)))
    return c >> 1

def write_bitarray_to_file(b: bitarray, path):
    with open(path, 'wb') as file:
        b.tofile(file)