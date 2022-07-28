from contextlib import closing
import gzip
import json
import random
import cPickle as pickle
from twister import Twister
from bitarray import bitarray
from util import N
import sys


def iter_bits_8_bit(twister):
    """Generate bits of 8 bit output as produced by random module

    :param Twister twister: Our twister implementation
    :rtype collections.Iterable[set[int]]
    """
    while True:
        int32 = twister.getint32()
        _ = twister.getint32()
        for bit in int32[:output_bits_length]:
            yield bit


def find_bit(data, field, bit):
    """Generate indexes where data[field][bit] is True

    :param list[(bitarray, bitarray)] data: Our rulebase
    :param int field: 0 or 1
    :param int bit: bit number in field
    :return: collections.Iterable[int]
    """
    return (x
            for x, bitfields in enumerate(data)
            if bitfields[field][bit])


def get_verifier(state, verify_data):
    """Returns a verifier function

    :param list[long] state: the initial state of MT
    :param list[int] verify_data: observed output of MT
    :rtype: ((bitarray, bitarray)) -> None
    """
    count = [0]

    def _verify(rule, force=False):
        count[0] += 1
        if not force and count[0] < 1000:
            return
        count[0] = 0
        bitfield1, bitfield2 = rule
        b1 = 1 & sum((verify_data[x // output_bits_length] >> (output_bits_length - 1 - x % output_bits_length)) & 1
                     for x in bitfield1.itersearch(bitarray([1])))
        b2 = 1 & sum((state[x // 32] >> (31 - x % 32)) & 1
                     for x in bitfield2.itersearch(bitarray([1])))
        assert b1 == b2, (b1, b2)
    return _verify


def generate_output(bits1, bits2, verify):
    """Fill our rule-base with outputs from MT

    :param bits1: number of bits from MT output
    :param bits2: number of bits in MT
    :param ((bitarray, bitarray)) -> None verify: verify function
    :rtype: list[(bitarray, bitarray)]
    """
    twister = Twister(N)
    iterator = iter_bits_8_bit(twister)
    data = []
    for i in xrange(bits1):
        print "Generating output bit %d/%d" % (i, bits1)
        bitfield1 = [0] * bits1
        bitfield2 = [0] * bits2
        val = next(iterator)
        bitfield1[i] = 1
        for j in val:
            bitfield2[j] = 1
        bitfield1 = bitarray(bitfield1)
        bitfield2 = bitarray(bitfield2)
        data.append((bitfield1, bitfield2))
        verify(data[len(data) - 1])
    return data


def triangle_data(bits1, bits2, data, verify):
    """Make a triangle out of our rule-base
    xxxx         1xxx
    xxxx         01xx
    xxxx    =>   001x
    xxxx         0001

    :param int bits1: number of bits from mt output
    :param int bits2: number of bits in mt state
    :param list[(bitarray, bitarray)] data: our rulebase
    :param ((bitarray, bitarray)) -> None verify: verify function
    """
    skipped = 0
    for bit in xrange(bits2):
        found_bits = [b for b in find_bit(data, 1, bit) if b >= bit]
        print "Working on bit %d/%d (skipped: %d, found: %d)" % (
            bit, bits2, skipped, len(found_bits)
        )
        if len(found_bits) < 1:
            print "skipping"
            skipped += 1
            bitfield1 = [0] * bits1
            bitfield2 = [0] * bits2
            data.insert(bit, (bitarray(bitfield1), bitarray(bitfield2)))
        else:
            main_bitfield1, main_bitfield2 = data[found_bits[0]]
            for pos in found_bits[1:]:
                bitfield1, bitfield2 = data[pos]
                bitfield1 ^= main_bitfield1
                bitfield2 ^= main_bitfield2
                verify((bitfield1, bitfield2))
                if not any(bitfield1):
                    assert not any(bitfield2)
            data[bit], data[found_bits[0]] = data[found_bits[0]], data[bit]
            verify(data[bit])


def solve_data(bits2, data, verify):
    """Solve our rulebase
    1xxx          1000
    01xx    =>    0100
    001x          0010
    0001          0001

    :param int bits2: number of bits in mt state
    :param list[(bitarray, bitarray)] data: our rulebase
    :param ((bitarray, bitarray)) -> None verify: verify function
    """
    for bit in xrange(bits2):
        bit = bits2 - 1 - bit
        found_bits = [b for b in find_bit(data, 1, bit) if b != bit]
        print "Finishing bit %d/%d (found: %d)" % (bit, bits2, len(found_bits))
        main_bitfield1, main_bitfield2 = data[bit]
        for pos in found_bits:
            bitfield1, bitfield2 = data[pos]
            bitfield1 ^= main_bitfield1
            bitfield2 ^= main_bitfield2
            verify((bitfield1, bitfield2))
            assert any(bitfield1) and any(bitfield2)
        assert [] == [b for b in find_bit(data, 1, bit) if b != bit]


def verify_solved_data(data, verify):
    """Verify that our solution is really a solution

    :param list[(bitarray, bitarray)] data: our rulebase
    :param ((bitarray, bitarray)) -> None verify: verify function
    """
    for x, rules in enumerate(data):
        print "Verifying... (%d/%d)" % (x, len(data))
        verify(rules, True)
        assert sum(rules[1]) <= 1


def save_data(data):
    """Save data to file 'magic_data'

    :param list[(bitarray, bitarray)] data: our rulebase
    """
    print "Masking bits to bytes...."
    data_masked = []
    mask = "".zfill(8 - output_bits_length)
    for line_bitarray, _ in data:
        line_string = line_bitarray.to01()
        line_string = line_string.rstrip("0")
        line_string_masked = [mask + line_string[i:i+output_bits_length] for i in range(0, len(line_string), output_bits_length)]
        line_bitarray_masked = bitarray("".join(line_string_masked))
        data_masked.append(line_bitarray_masked)
    print "done"

    print "Saving data...."
    with closing(gzip.GzipFile("magic_data_"+str(output_bits_length), "w")) as f:
        pickle.dump([b.tobytes().rstrip("\0") for b in data_masked], f)
    print "Done."


def main():
    """Main function"""
    global output_bits_length

    # 1 optional argument : output bits length
    if len(sys.argv) > 1:
        output_bits_length = int(sys.argv[1])
        if output_bits_length < 1 or output_bits_length > 8:
            print "Argument %d bits output invalid, currently supported : integer between 1 and 8 inclusive" % output_bits_length
            return
        print "Using argument %d bits output" % output_bits_length
    else:
        output_bits_length = 8
        print "Using default 8 bits output"

    # bits1 = 26880, a little bit over 19668 and divisible by all output bits possible, originally 3500*8 for 8 bits
    bits1 = 2 * 3 * 4 * 4 * 5 * 7 * 8
    bits2 = N * 32
    rnd = random.Random()
    rng_state = rnd.getstate()[1][:624]
    rng_data = [rnd.randint(0, (2 **output_bits_length) - 1) for _ in xrange(bits1/output_bits_length)]
    verify = get_verifier(rng_state, rng_data)

    data = generate_output(bits1, bits2, verify)
    triangle_data(bits1, bits2, data, verify)

    data[bits2:] = []

    solve_data(bits2, data, verify)
    verify_solved_data(data, verify)
    save_data(data)

if __name__ == '__main__':
    main()
