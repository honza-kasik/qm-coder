import bitarray
import argparse
from utils import write_bitarray_to_file, load_bitarray_from_file
from coder import Encoder, Decoder

import logging
logger = logging.getLogger(__name__)

def _encode(input_path, output_path):
    input = load_bitarray_from_file(input_path)
    coder = Encoder(input)
    coder.encode()
    write_bitarray_to_file(coder.get_output(), output_path)

def _decode(input_path, output_path):
    input = load_bitarray_from_file(input_path)
    decoder = Decoder(input)
    decoder.decode()
    write_bitarray_to_file(decoder.get_output(), output_path)

def main():
    import logging

    logging.basicConfig(level=logging.DEBUG)
    handler = logging.FileHandler("log.txt")
    logger = logging.getLogger(__name__)
    logger.addHandler(handler)

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
