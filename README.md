# notrandom() - reverse the Mersenne Twister

This is a demonstration how to rebuild the internal state of a Mersenne Twister by using only parts of its output. In this example it uses 8 bits per 64 bit MT-output. (This is what you get from
`random.randint(0, 255)`.

The Mersenne Twister implementation is in twister.py. The script `gen_magic_data.py` precalculates the
`magic_data`. (This may take a while, so the precalculated `magic_data` is already included.)

`rebuild_random.py` demonstrates that it works. It reads 3115 bytes from `random.randint(0, 255)` to
infer the internal state of the Mersenne Twister.

Boring output of `rebuild_random.py`:

```
$ python ./rebuild_random.py 
Loading Magic
Done.
Working.... I need 3115 bytes from MT
BBBBBBBBBBBBBBBBBBBBBBBBBBBDDDDCCCCCCCCCCCCCEEEDDDDEEGFHJSREOIHFEEDDEEECCCCCCCBB
BBBBBBBBBBBBBBBBBBBBBBBBBBCDDDDDDCCCCCCCCCDDEEEEFFEEFGRQQF..ONCJFFEEEEDDCCCCCCCC
BBBBBBBBBBBBBBBBBBBBBBBBBCCDDDDDDDDEEDDDDDDDFEEEFFFGGGIRI.....PIGGFEEEFDDDDEDDDD
BBBBBBBBBBBBBBBBBBBBBBBBCCCDDDDDDDDDEEEDDDDEGFGGGHGHHIJO......RJHIGGFFFEFEEDDDDD
CCCBBBBBBBBBBBBBBBBBBCCCCCCDDDDDDDDDEEEEEFFGGNRTKJICBOLBTM..IAQOPMNJIGHHPIEDDDDD
CCCCCCCCCCBBBBBBBCCCCCCCCCDEDDDDDDDDEEEEEFFFGLP..TDK..............HPLMEAPTGEEEEC
CCCCCCCCCCCCDDDDCCCCCCCCCDDEEEDDDDDFFEEEEFGGHKQ.........................NJFFEDDC
CCCCCCCCCCCCCDDDDDDDEDDDDDFEEEFEEEEFFFGGFGIMRN........................JPJGGEEDDC
CCCCCCCCCCCCCDDDDDDDDEEEFFKIGFFGGFGFFFGGGIJO............................TIIGFFDD
CCCCCCCCCCCCCCDDDDDDDEEEEFKKIIHHJBIHGIHHHIF.............................G.QJFEEE
BCCCCCCCCCCCCCDDDDDDDEFFFGHJNNOLMPJLRJIJILI..............................QJGGEDD
BBCCCCCCCCCCCDEEDDDDDEFFFGHIFP.L.....DDMMO...............................HLGGDDD
BBBDDDCCCCCCDDEEEEFFEFHGHIRRA...........PA...............................JJFEEED
BBBCDDDDEEDDDFEEEEFFHGJKKKME.............K...............................LHGEEEE
BBBBCDDDFEEFIFFGFGGHHJKPT.P.............................................QGGFEDDD
BBBBCC................................................................PJHGFEEDDD
BBBBCDDDFEEFIFFGFGGHHJKPT.P.............................................QGGFEDDD
BBBCDDDDEEDDDFEEEEFFHGJKKKME.............K...............................LHGEEEE
BBBDDDCCCCCCDDEEEEFFEFHGHIRRA...........PA...............................JJFEEED
BBCCCCCCCCCCCDEEDDDDDEFFFGHIFP.L.....DDMMO...............................HLGGDDD
BCCCCCCCCCCCCCDDDDDDDEFFFGHJNNOLMPJLRJIJILI..............................QJGGEDD
CCCCCCCCCCCCCCDDDDDDDEEEEFKKIIHHJBIHGIHHHIF.............................G.QJFEEE
CCCCCCCCCCCCCDDDDDDDDEEEFFKIGFFGGFGFFFGGGIJO............................TIIGFFDD
CCCCCCCCCCCCCDDDDDDDEDDDDDFEEEFEEEEFFFGGFGIMRN........................JPJGGEEDDC
CCCCCCCCCCCCDDDDCCCCCCCCCDDEEEDDDDDFFEEEEFGGHKQ.........................NJFFEDDC
CCCCCCCCCCBBBBBBBCCCCCCCCCDEDDDDDDDDEEEEEFFFGLP..TDK..............HPLMEAPTGEEEEC
CCCBBBBBBBBBBBBBBBBBBCCCCCCDDDDDDDDDEEEEEFFGGNRTKJICBOLBTM..IAQOPMNJIGHHPIEDDDDD
BBBBBBBBBBBBBBBBBBBBBBBBCCCDDDDDDDDDEEEDDDDEGFGGGHGHHIJO......RJHIGGFFFEFEEDDDDD
BBBBBBBBBBBBBBBBBBBBBBBBBCCDDDDDDDDEEDDDDDDDFEEEFFFGGGIRI.....PIGGFEEEFDDDDEDDDD
BBBBBBBBBBBBBBBBBBBBBBBBBBCDDDDDDCCCCCCCCCDDEEEEFFEEFGRQQF..ONCJFFEEEEDDCCCCCCCC
BBBBBBBBBBBBBBBBBBBBBBBBBBBDDDDCCCCCCCCCCCCCEEEDDDDEEGFHJSREOIHFEEDDEEECCCCCCCBB
RANDOM POOL SUCCESSFULLY REBUILT!
```

# Introduction

The Mersenne Twister (MT 19937) is a pseudorandom number generator, used by
Python and
[many other languages like Ruby, and PHP](https://en.wikipedia.org/wiki/Mersenne_twister#Applications).
It is known to pass many statistical randomness tests, but it's also known to
be not cryptographically secure. The Python documentation is clear on this
point, describing it as "completely unsuitable for cryptographic purposes."
Here we will show why.

When you are able to predict pseudorandom numbers, you can predict session ids,
randomly generated passwords or encryption keys and know all the cards in online
poker games, or
[play "Asteroids" better than legally possible](http://www.heise.de/video/artikel/Asteroids-Helmut-Buhler-der-Praekognitive-1-Platz-1573672.html)

Many sources already showed that it's easy to rebuild the internal state of the
MT by using 624 consecutive outputs. But this alone isn't a practical attack,
it's unlikely that you have access to the whole output. I'm demonstrating how to
restore its internal state by using only parts of its output. This will allow
us to know all previous and future random number generation.

With every 32bit output the MT directly exposes 32 bit of it's internal state
(only slightly and reversibly modified by the tempering function). After each
round of 624 outputs, the internal state of the Mersenne Twister is "twisted":
All bits are XOR'd with several other bits. In fact the Mersenne Twister is just
a big XOR machine: All its output can be expressed by an sequence of XORs of
the initial state bits.

Python always combines two outputs into a 64bit integer before returning them as
random integers. So each call of `random.randint(0, 255)` gives you only 8 bits
out of two 32 bit Mersenne Twister outputs. Since the tempering function already
mixed the 32 bits outputs, it's not possible anymore to directly recover internal
state bits out of only the 8 bits.

I was curious if it's hard to recover the internal MT state by using only the
output of a function like this:

```
def random_string(length):
    return "".join(chr(random.randint(0, 255)) for i in xrange(length))
```

Since the internal state of the Mersenne Twister consists out of 19968 bits we
will need at least ~2.5KB of output to recover the internal state. In fact I
needed ~3.3kb, probably because of redundant output information.

# How does it work?

First I named the initial state with variables s0..s19967. The initial state
looks like this:

```
Internal state bit | Value
-------------------|-------
0                  | s0
1                  | s1
2                  | s2
...                | ...
19967              | s19967
```

Now the first output of the Mersenne Twister is a combination of the first
32 bits (combined by the tempering function):

```
Output-Bit | Value
-----------|-------
o0         | s0 xor s4 xor s7 xor s15
o1         | s1 xor s5 xor s16
o2         | s2 xor s6 xor s13 xor s17 xor s24
...        | ...
o31        | s2 xor s9 xor s13 xor s17 xor s28 xor s31
```

same for the second output:

```
Output-Bit | Value
-----------|-------------------------
o32        | s32 xor s36 xor s39 xor s47
...        | ...
```

But we can only observe eight of these bits, because random.randint(0,255)
exposes only this portion of the output.

After 624 outputs, the internal state of the Mersenne Twister is "twisted"
around. We update our internal state as an xor-combination of our old indices.

```
Internal state bit | Value
-------------------|-----------------
0                  | s63 xor s12704
1                  | s0 xor s12705
...                | ...
19967              | s61 xor s62 xor s5470 xor s5471 xor s18143
```

The outputs look now more complicated now, because the state bits are an
xor-combination of the initial state:

```
Output-Bit | Value
-----------|--------------
o19968     | s35 xor s38 xor s46 xor s63 xor s12704 xor s12708 xor s12711 xor s12719
...        | ...
```

After 3.3 kb this list contains about 40 variables.

Now we have a big list of output-bits and how they are made out of an
xor-combination of the original state. A big system of equations that we can
solve. This is done as you learned it at school: Here's a simple example for 3
bits.

Given this equations system:

```
o1  =  s0  xor  s1  xor  s2
o2  =           s1  xor  s2
o3  =  s0  xor  s1
```

First we solve s0:

``` 
o1         =  s0  xor  s1  xor  s2
o2         =           s1  xor  s2
=>
o1 xor o2  =  s0
```

With this solution it’s easy to find solution for s1.

```
o3                   =  s0 xor s1
o1 xor o2            =  s0
=>
o1 xor o2 xor o3     =         s1
```

And finally for s2.

```
o2                =  s1 xor s2
o1 xor o2 xor o3  =  s1
=>
o1 xor o3         =         s2
```

Result:

```
o1 xor o2        =  s0
o1 xor o2 xor o3 =      s1
o1 xor o3        =          s2
```

Now we know how to recover the 3-bit state out of our 3 output-bits:

```
s0 = o1 xor o2
s1 = o1 xor o2 xor o3
s2 = o1 xor o3 
```

However, in reality we have about 26,000 equations with 20,000 variables.

# Further notes

Since the Mersenne Twister is highly symmetric, it's probably possible to find
some shortcuts or a fully mathematical solution for this problem. However, I
implemented the straight-forward solution since it's easy and reusable.

Python seeds the Twister with only 128 bits of "real" randomness. So
theoretically it's enough to know a few output bytes to restore the whole state,
but you would need an efficient attack on the seeding algorithm since 128 bit
is too much for a brute-force attack.

Other implementations use much less randomness to seed their random number
generators. PHP seems to use only 32 bits for seeding mt_random, Perl also uses
only 32 bit (but another PRNG). In these cases it's probably easier to use a
brute-force attack on the seed.

Frank Sievertsen
@fx5
