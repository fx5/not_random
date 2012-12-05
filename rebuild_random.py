import gzip
import random
from itertools import imap


print "Loading Magic"
f = gzip.GzipFile("magic_data","r")
magic = eval(f.read())
f.close()
print "Done."

def rebuild_random(data):
    assert len(data) >= 3360
    vals = list(imap(ord, data))

    def getbit(bit):
        assert bit >= 0
        return (vals[bit // 8] >> (7 - bit % 8)) & 1

    state = []
    for i in xrange(0, 624):
        print "REBUILDING RANDOM-POOL ["+ ("#" * (i // 10)).ljust(62) +"]"
        val = 0
        data = magic[i % 2]
        for bit in data:
            val <<= 1
            for b in bit:
                val ^= getbit(b+(i//2)*8 - 8)
        state.append(val)

    state.append(0)
    ran = random.Random()
    ran.setstate((3, tuple(state),None))
    for i in xrange(len(vals) - 3201 + 394):
        _ = ran.randint(0,255)
    return ran
    
def random_string(length, random_module = random):
    return "".join(chr(random_module.randint(0, 255)) for i in xrange(length))


## OK... here's how it works

# Shuffle the random-state a little bit
random_string(random.randint(0,10000))

# First we receive 3500 bytes from our random-function
first_random_string = random_string(3360)

# and put it into our magic function. It returns a Random-object
# that is in the same state as the other random-object, reconstructed
# out of the random-strings

my_random = rebuild_random(first_random_string)

# Now we expect this string
expected_string = random_string(10000, my_random)

# Let's see...
second_random_string = random_string(10000)

# if it matches.
if expected_string == second_random_string:
    print "RANDOM POOL SUCCESSFULLY REBUILT!"
else:
    print "Should not happen"


