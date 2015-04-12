"""Rebuild internal state of Mersenne Twister from truncated output"""

from contextlib import closing
import gzip
import random
from itertools import izip
from progress import ProgressBar
import cPickle as pickle
from util import N


def rebuild_random(magic, data):
    """Create a random.Random() object from the data and the magic vectors

    :param list[str] magic: magic vector data
    :param str data: observed output from Mersenne Twister
    :rtype: random.Random
    """
    progress = ProgressBar()
    data_vals = [ord(d) for d in data]
    state = [0L for _ in xrange(N)]

    for bit_pos, bit_magic in enumerate(magic):
        progress.progress((bit_pos + 1.) / len(magic))
        magic_vals = (ord(d) for d in bit_magic)
        xor_data = (a & b for a, b in izip(magic_vals, data_vals))
        xor_data = reduce(lambda a, b: a ^ b, xor_data, 0)
        xor_data = reduce(lambda a, b: a ^ b,
                          (xor_data >> i for i in xrange(8)))
        xor_data &= 1
        state[bit_pos // 32] |= xor_data << (31 - bit_pos % 32)

    state.append(N)
    ran = random.Random()
    ran.setstate((3, tuple(state), None))
    cmp_data = random_string(len(data), ran)
    assert cmp_data == data
    return ran


def random_string(length, random_obj=random):
    """Generate "random" output string from Mersenne Twister
    :param int length: number of bytes
    :param random.Random random_obj: random object (default: random module)
    :return: str
    """
    return "".join(chr(random_obj.randint(0, 255)) for _ in xrange(length))


def main():
    """Main function"""

    print "Loading Magic"
    with closing(gzip.GzipFile("magic_data")) as f:
        magic = pickle.load(f)
    print "Done."

    need_bytes = max(len(d) for d in magic)

    print "Working.... I need %d bytes from the MT" % (need_bytes,)

    # Shuffle the random-state a little bit
    random_string(random.randint(0, 10000))

    # First we receive 3115 bytes from our random-function
    first_random_string = random_string(need_bytes)

    # and put it into our magic function. It returns a Random-object
    # that is in the same state as the other random-object, reconstructed
    # out of the random-strings

    my_random = rebuild_random(magic, first_random_string)

    # Now we expect this string
    expected_string = random_string(10000, my_random)

    # Let's see...
    second_random_string = random_string(10000)

    # if it matches.
    if expected_string == second_random_string:
        print "RANDOM POOL SUCCESSFULLY REBUILT!"
    else:
        print "Should not happen"


if __name__ == '__main__':
    main()